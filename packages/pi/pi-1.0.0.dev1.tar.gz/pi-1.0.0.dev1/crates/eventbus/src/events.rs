use crate::{EventData, Eventable};
use crossbeam_channel::{self, RecvTimeoutError, Sender};
use slab::Slab;
use std::{
    collections::HashMap,
    sync::{
        Arc, LazyLock, Mutex, Weak,
        atomic::{AtomicBool, AtomicUsize, Ordering::*},
    },
    thread::{self, JoinHandle},
    time::Duration,
};

// =================== Public surface (using EventData enum) ===================

pub static DISPATCHER: LazyLock<Dispatcher> = LazyLock::new(Dispatcher::new);

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct ChannelId(u64);

pub struct Dispatcher {
    inner: Arc<Inner>,
}

/// Strong ref keeps the dispatcher (and thus loop) alive while any source clone exists.
#[derive(Clone)]
#[must_use]
pub struct EventSource<T: Eventable> {
    inner: Arc<Inner>,        // strong keeps Inner alive
    id: ChannelId,            // channel this source belongs to
    lease: Arc<ChannelLease>, // used to run per-channel teardown on last drop
    _phantom: std::marker::PhantomData<T>,
}

/// Clonable view that can register listeners bound to a single channel.
#[derive(Clone)]
#[must_use]
pub struct EventListeners<T> {
    inner: Arc<Inner>, // strong is fine; doesn't keep loop running
    id: ChannelId,
    _phantom: std::marker::PhantomData<T>,
}

/// Dropping this automatically unsubscribes. Weak — doesn't keep the loop alive.
#[must_use]
pub struct ListenerHandle {
    inner: Weak<Inner>,
    id: ChannelId,
    key: usize,
    unsubbed: bool,
}

type Callback = Box<dyn FnMut(&EventData) + Send + 'static>;

// =================== Private control plane ===================

enum WorkItem {
    AllocChannel {
        ack: Sender<ChannelId>,
    },
    SendEvent {
        id: ChannelId,
        event: EventData,
    },
    Barrier {
        _id: ChannelId,
        ack: Sender<()>,
    },
    DropChannel(ChannelId),
    Subscribe {
        id: ChannelId,
        callback: Callback,
        ack: Sender<usize>,
    },
    Unsubscribe {
        id: ChannelId,
        key: usize,
    },
    Wake,
}

struct Inner {
    // Worker thread's work submission queue using crossbeam-channel
    work_tx: Mutex<Option<Sender<WorkItem>>>,

    // Worker thread state
    running: AtomicBool,
    join_handle: Mutex<Option<JoinHandle<()>>>,

    // Channel lifecycle tracking
    channel_count: AtomicUsize,
}

/// A per-channel guard whose last strong drop triggers channel teardown.
/// We don't need fields here; the Arc's strong_count tells us when last clone drops.
struct ChannelLease;

// =================== Worker Thread State ===================

struct WorkerState {
    // Channel ID allocation
    next_channel_id: u64,

    // Event listeners organized by channel
    listeners: HashMap<ChannelId, Slab<Callback>>,
}

impl WorkerState {
    fn new() -> Self {
        Self {
            next_channel_id: 1,
            listeners: HashMap::new(),
        }
    }

    fn allocate_channel(&mut self) -> ChannelId {
        let id = ChannelId(self.next_channel_id);
        self.next_channel_id = self.next_channel_id.wrapping_add(1);
        self.listeners.entry(id).or_insert_with(Slab::new);
        id
    }

    fn drop_channel(&mut self, id: ChannelId) {
        self.listeners.remove(&id);
    }

    fn subscribe(&mut self, id: ChannelId, callback: Callback) -> usize {
        let slab = self.listeners.entry(id).or_insert_with(Slab::new);
        slab.insert(callback)
    }

    fn unsubscribe(&mut self, id: ChannelId, key: usize) {
        if let Some(slab) = self.listeners.get_mut(&id) {
            if slab.contains(key) {
                _ = slab.remove(key);
            }
        }
    }

    fn deliver_event(&mut self, id: ChannelId, event: &EventData) {
        if let Some(slab) = self.listeners.get_mut(&id) {
            for (_, callback) in slab.iter_mut() {
                (callback)(event);
            }
        }
    }
}

// =================== Dispatcher ===================

impl Dispatcher {
    fn new() -> Self {
        Self {
            inner: Arc::new(Inner {
                work_tx: Mutex::new(None),
                running: AtomicBool::new(false),
                join_handle: Mutex::new(None),
                channel_count: AtomicUsize::new(0),
            }),
        }
    }

    /// Create a private channel: (EventSource, EventListeners)
    pub fn tear_off<T: Eventable>(&self) -> (EventSource<T>, EventListeners<T>) {
        let prev = self.inner.channel_count.fetch_add(1, SeqCst);
        if prev == 0 {
            self.start_worker();
        }

        // Ask the worker to allocate a fresh ChannelId
        let work_tx = self
            .inner
            .work_tx
            .lock()
            .unwrap()
            .clone()
            .expect("worker must be running");
        let (ack_tx, ack_rx) = crossbeam_channel::bounded(1);
        work_tx
            .send(WorkItem::AllocChannel { ack: ack_tx })
            .expect("send alloc");
        let id = ack_rx.recv().expect("recv alloc");

        let lease = Arc::new(ChannelLease);
        (
            EventSource {
                inner: self.inner.clone(),
                id,
                lease: lease.clone(),
                _phantom: std::marker::PhantomData,
            },
            EventListeners {
                inner: self.inner.clone(),
                id,
                _phantom: std::marker::PhantomData,
            },
        )
    }

    /// Wait until all messages currently enqueued for this channel are processed.
    /// Returns false if the loop isn't running.
    pub fn flush_channel(&self, id: ChannelId, timeout: Duration) -> bool {
        let Some(work_tx) = self.inner.work_tx.lock().unwrap().clone() else {
            return false;
        };
        let (ack_tx, ack_rx) = crossbeam_channel::bounded(1);
        if work_tx
            .send(WorkItem::Barrier {
                _id: id,
                ack: ack_tx,
            })
            .is_err()
        {
            return false;
        }
        ack_rx.recv_timeout(timeout).is_ok()
    }

    fn start_worker(&self) {
        if self.inner.running.swap(true, SeqCst) {
            return;
        }

        let (work_tx, work_rx) = crossbeam_channel::unbounded::<WorkItem>();
        *self.inner.work_tx.lock().unwrap() = Some(work_tx.clone());

        let inner = self.inner.clone();
        let handle = thread::spawn(move || {
            let mut state = WorkerState::new();

            loop {
                // Check if we should exit (no channels alive)
                if inner.channel_count.load(SeqCst) == 0 {
                    // Drain any remaining work items
                    while let Ok(item) = work_rx.try_recv() {
                        match item {
                            WorkItem::AllocChannel { ack } => {
                                let id = state.allocate_channel();
                                let _ = ack.send(id);
                            }
                            WorkItem::SendEvent { id, event } => {
                                state.deliver_event(id, &event);
                            }
                            WorkItem::Barrier { _id: _, ack } => {
                                let _ = ack.send(());
                            }
                            WorkItem::DropChannel(id) => state.drop_channel(id),
                            WorkItem::Subscribe { id, callback, ack } => {
                                let key = state.subscribe(id, callback);
                                let _ = ack.send(key);
                            }
                            WorkItem::Unsubscribe { id, key } => {
                                state.unsubscribe(id, key);
                            }
                            WorkItem::Wake => {}
                        }
                    }

                    // Double-check we should still exit
                    if inner.channel_count.load(SeqCst) == 0 {
                        inner.running.store(false, SeqCst);
                        *inner.work_tx.lock().unwrap() = None;
                        break;
                    }
                }

                // Process work items with timeout
                match work_rx.recv_timeout(Duration::from_millis(200)) {
                    Ok(WorkItem::AllocChannel { ack }) => {
                        let id = state.allocate_channel();
                        let _ = ack.send(id);
                    }
                    Ok(WorkItem::SendEvent { id, event }) => {
                        state.deliver_event(id, &event);

                        // Burst-drain for amortization
                        for _ in 0..256 {
                            match work_rx.try_recv() {
                                Ok(WorkItem::AllocChannel { ack }) => {
                                    let id = state.allocate_channel();
                                    let _ = ack.send(id);
                                }
                                Ok(WorkItem::SendEvent { id, event }) => {
                                    state.deliver_event(id, &event);
                                }
                                Ok(WorkItem::Barrier { _id: _, ack }) => {
                                    let _ = ack.send(());
                                }
                                Ok(WorkItem::DropChannel(id)) => state.drop_channel(id),
                                Ok(WorkItem::Subscribe { id, callback, ack }) => {
                                    let key = state.subscribe(id, callback);
                                    let _ = ack.send(key);
                                }
                                Ok(WorkItem::Unsubscribe { id, key }) => {
                                    state.unsubscribe(id, key);
                                }
                                Ok(WorkItem::Wake) => {}
                                Err(_) => break,
                            }
                        }
                    }
                    Ok(WorkItem::Barrier { _id: _, ack }) => {
                        let _ = ack.send(());
                    }
                    Ok(WorkItem::DropChannel(id)) => state.drop_channel(id),
                    Ok(WorkItem::Subscribe { id, callback, ack }) => {
                        let key = state.subscribe(id, callback);
                        let _ = ack.send(key);
                    }
                    Ok(WorkItem::Unsubscribe { id, key }) => {
                        state.unsubscribe(id, key);
                    }
                    Ok(WorkItem::Wake) => {}
                    Err(RecvTimeoutError::Timeout) => {}
                    Err(RecvTimeoutError::Disconnected) => {
                        inner.running.store(false, SeqCst);
                        *inner.work_tx.lock().unwrap() = None;
                        break;
                    }
                }
            }
        });

        *self.inner.join_handle.lock().unwrap() = Some(handle);
        let _ = work_tx.send(WorkItem::Wake);
    }
}

// =================== EventSource / EventListeners ===================

impl<T: Eventable> EventSource<T> {
    pub fn id(&self) -> ChannelId {
        self.id
    }

    pub fn send(&self, event: T) {
        if let Some(work_tx) = self.inner.work_tx.lock().unwrap().as_ref() {
            let _ = work_tx.send(WorkItem::SendEvent {
                id: self.id,
                event: event.cast_send(),
            });
        }
    }
}

impl<T: Eventable> Drop for EventSource<T> {
    fn drop(&mut self) {
        // When the *last clone* of this EventSource drops, tear down channel state.
        if Arc::strong_count(&self.lease) == 1 {
            // One channel fewer is alive
            let prev = self.inner.channel_count.fetch_sub(1, SeqCst);
            debug_assert!(prev > 0);

            // Ask worker to delete listeners for this channel
            if let Some(work_tx) = self.inner.work_tx.lock().unwrap().as_ref() {
                let _ = work_tx.send(WorkItem::DropChannel(self.id));
                let _ = work_tx.send(WorkItem::Wake);
            }

            // If that was the last channel overall, join the worker thread now
            if prev == 1 {
                if let Some(h) = self.inner.join_handle.lock().unwrap().take() {
                    let _ = h.join();
                }
            }
        }
    }
}

impl<T: Eventable> EventListeners<T> {
    pub fn id(&self) -> ChannelId {
        self.id
    }

    /// Subscribe to this channel only.
    pub fn subscribe<F>(&self, mut f: F) -> ListenerHandle
    where
        F: for<'a> FnMut(T::Recv<'a>) + Send + 'static,
    {
        let work_tx = self
            .inner
            .work_tx
            .lock()
            .unwrap()
            .clone()
            .expect("worker must be running");
        let (ack_tx, ack_rx) = crossbeam_channel::bounded(1);

        // Wrap the callback to handle the conversion
        let wrapped_callback = Box::new(move |event: &EventData| {
            let converted = T::cast(event);
            f(converted);
        });

        work_tx
            .send(WorkItem::Subscribe {
                id: self.id,
                callback: wrapped_callback,
                ack: ack_tx,
            })
            .expect("send subscribe");

        let key = ack_rx.recv().expect("recv subscribe key");

        // Nudge worker for tests that call flush right away
        let _ = work_tx.send(WorkItem::Wake);

        ListenerHandle {
            inner: Arc::downgrade(&self.inner),
            id: self.id,
            key,
            unsubbed: false,
        }
    }
}

// =================== ListenerHandle ===================

impl ListenerHandle {
    pub fn unsubscribe(&mut self) {
        if self.unsubbed {
            return;
        }
        if let Some(inner) = self.inner.upgrade() {
            if let Some(work_tx) = inner.work_tx.lock().unwrap().as_ref() {
                let _ = work_tx.send(WorkItem::Unsubscribe {
                    id: self.id,
                    key: self.key,
                });
                let _ = work_tx.send(WorkItem::Wake);
            }
        }
        self.unsubbed = true;
    }

    pub fn forget(mut self) {
        // Drop without unsubscribing
        self.unsubbed = true;
    }
}

impl Drop for ListenerHandle {
    fn drop(&mut self) {
        self.unsubscribe();
    }
}

// =================== Tests ===================

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::mpsc;
    use std::time::{Duration, Instant};

    // --------- helpers ---------

    fn wait_until(timeout: Duration, mut cond: impl FnMut() -> bool) -> bool {
        let start = Instant::now();
        while start.elapsed() < timeout {
            if cond() {
                return true;
            }
            std::thread::sleep(Duration::from_millis(5));
        }
        false
    }

    fn fresh_dispatcher() -> Dispatcher {
        Dispatcher::new() // tests are in the same module and can call private `new`
    }

    // When asserting "no more events", both Timeout and Disconnected mean success.
    fn assert_no_event<T>(rx: &mpsc::Receiver<T>, timeout_ms: u64) {
        match rx.recv_timeout(Duration::from_millis(timeout_ms)) {
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => {}
            Ok(_) => panic!("unexpected event received"),
        }
    }

    // Helper function to extract String from EventData
    fn extract_string(event: &EventData) -> Option<String> {
        if let EventData::Boxed(boxed) = event {
            (&**boxed).downcast_ref::<String>().map(|s| s.to_string())
        } else {
            None
        }
    }

    // --------- tests ---------

    #[test]
    fn per_channel_isolation() {
        let d = fresh_dispatcher();

        let (src_a, lst_a) = d.tear_off::<&'static str>();
        let (src_b, _lst_b) = d.tear_off::<&'static str>();

        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));

        let (tx_a, rx_a) = mpsc::channel::<String>();
        let _ha = lst_a.subscribe(move |s| {
            let _ = tx_a.send(s.to_string());
        });

        src_b.send("from_b");
        src_a.send("from_a");

        // Flush both channels to create deterministic ordering
        assert!(d.flush_channel(src_a.id(), Duration::from_millis(500)));
        assert!(d.flush_channel(src_b.id(), Duration::from_millis(500)));

        // Only messages from A should be received by A's listener
        let got = rx_a
            .recv_timeout(Duration::from_millis(300))
            .expect("expected event on A");
        assert_eq!(got, "from_a");

        drop(src_a);
        drop(src_b);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn multiple_listeners_get_the_same_message() {
        let d = fresh_dispatcher();

        let (src, lst) = d.tear_off::<String>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));

        let (tx1, rx1) = mpsc::channel::<String>();
        let (tx2, rx2) = mpsc::channel::<String>();
        let _h1 = lst.subscribe(move |s| {
            let _ = tx1.send(s.to_string());
        });
        let _h2 = lst.subscribe(move |s| {
            let _ = tx2.send(s.to_string());
        });

        src.send("hello".to_string());
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));

        assert_eq!(
            rx1.recv_timeout(Duration::from_millis(300)).unwrap(),
            "hello"
        );
        assert_eq!(
            rx2.recv_timeout(Duration::from_millis(300)).unwrap(),
            "hello"
        );

        drop(src);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn unsubscribe_stops_delivery_for_that_listener_only() {
        let d = fresh_dispatcher();
        let (src, lst) = d.tear_off::<String>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));

        let (tx1, rx1) = mpsc::channel::<String>();
        let (tx2, rx2) = mpsc::channel::<String>();
        let mut h1 = lst.subscribe(move |event| {
            let _ = tx1.send(event.to_string());
        });
        let _h2 = lst.subscribe(move |event| {
            let _ = tx2.send(event.to_string());
        });

        // Prove both receive
        src.send("one".to_string());
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));
        assert_eq!(rx1.recv_timeout(Duration::from_millis(300)).unwrap(), "one");
        assert_eq!(rx2.recv_timeout(Duration::from_millis(300)).unwrap(), "one");

        // Unsubscribe first; second should still receive
        h1.unsubscribe();
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));

        src.send("two".to_string());
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));
        assert_no_event(&rx1, 150);
        assert_eq!(rx2.recv_timeout(Duration::from_millis(300)).unwrap(), "two");

        drop(src);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn send_before_subscribe_is_not_buffered() {
        let d = fresh_dispatcher();
        let (src, lst) = d.tear_off();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));

        // Send first, then subscribe – should not receive the early one
        src.send("early".to_string());
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));

        let (tx, rx) = mpsc::channel::<String>();
        let _h = lst.subscribe(move |event| {
            let _ = tx.send(event.to_string());
        });

        // Now send a second message which should be delivered
        src.send("late".to_string());
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));

        assert_eq!(rx.recv_timeout(Duration::from_millis(300)).unwrap(), "late");

        drop(src);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn source_clone_keeps_channel_alive_until_last_drop() {
        let d = fresh_dispatcher();
        let (src, lst) = d.tear_off::<String>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));
        let src2 = src.clone();

        let (tx, rx) = mpsc::channel::<String>();
        let _h = lst.subscribe(move |s| {
            let _ = tx.send(s.to_string());
        });

        // Drop the first source; channel should still work via clone
        drop(src);
        src2.send("via_clone".to_string());
        assert!(d.flush_channel(src2.id(), Duration::from_millis(500)));
        assert_eq!(
            rx.recv_timeout(Duration::from_millis(300)).unwrap(),
            "via_clone"
        );

        drop(src2);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn flush_channel_returns_false_when_not_running() {
        let d = fresh_dispatcher();

        // no channels yet, loop should not be running
        assert!(!d.inner.running.load(SeqCst));
        // pick a dummy id that will never exist
        assert_eq!(
            d.flush_channel(ChannelId(42), Duration::from_millis(100)),
            false
        );

        // Start and stop once, then check again
        {
            let (src, _lst) = d.tear_off::<String>();
            assert!(wait_until(Duration::from_millis(300), || d
                .inner
                .running
                .load(SeqCst)));
            drop(src);
            assert!(wait_until(Duration::from_millis(600), || !d
                .inner
                .running
                .load(SeqCst)));
        }

        assert_eq!(
            d.flush_channel(ChannelId(1), Duration::from_millis(100)),
            false
        );
    }

    #[test]
    fn restart_after_all_channels_closed() {
        let d = fresh_dispatcher();

        // First run
        {
            let (src, lst) = d.tear_off::<String>();
            assert!(wait_until(Duration::from_millis(300), || d
                .inner
                .running
                .load(SeqCst)));
            let (tx, rx) = mpsc::channel::<String>();
            let _h = lst.subscribe(move |event| {
                let _ = tx.send(event.to_string());
            });
            src.send("first".to_string());
            assert!(d.flush_channel(src.id(), Duration::from_millis(500)));
            assert_eq!(
                rx.recv_timeout(Duration::from_millis(300)).unwrap(),
                "first"
            );
            drop(src);
            assert!(wait_until(Duration::from_millis(600), || !d
                .inner
                .running
                .load(SeqCst)));
        }

        // Second run
        let (src2, lst2) = d.tear_off::<String>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));
        let (tx2, rx2) = mpsc::channel::<String>();
        let _h2 = lst2.subscribe(move |event| {
            let _ = tx2.send(event.to_string());
        });
        src2.send("second".to_string());
        assert!(d.flush_channel(src2.id(), Duration::from_millis(500)));
        assert_eq!(
            rx2.recv_timeout(Duration::from_millis(300)).unwrap(),
            "second"
        );
        drop(src2);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn dropping_source_removes_its_listeners() {
        let d = fresh_dispatcher();

        let (src, lst) = d.tear_off::<String>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));
        let (tx, rx) = mpsc::channel::<String>();
        let _h = lst.subscribe(move |event| {
            let _ = tx.send(event.to_string());
        });

        src.send("alive".to_string());
        assert!(d.flush_channel(src.id(), Duration::from_millis(500)));
        assert_eq!(
            rx.recv_timeout(Duration::from_millis(300)).unwrap(),
            "alive"
        );

        // Drop last source for this channel -> channel is removed from map
        drop(src);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));

        // Recreate a new channel and ensure no stray deliveries from the old id appear
        let (src2, lst2) = d.tear_off::<String>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));
        let (tx2, rx2) = mpsc::channel::<String>();
        let _h2 = lst2.subscribe(move |event| {
            let _ = tx2.send(event.to_string());
        });

        src2.send("fresh".to_string());
        assert!(d.flush_channel(src2.id(), Duration::from_millis(500)));
        assert_eq!(
            rx2.recv_timeout(Duration::from_millis(300)).unwrap(),
            "fresh"
        );
        // The old rx should see nothing further
        assert_no_event(&rx, 150);

        drop(src2);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }

    #[test]
    fn per_channel_flush_does_not_block_other_channels() {
        let d = fresh_dispatcher();
        let (src_a, lst_a) = d.tear_off::<String>();
        let (src_b, lst_b) = d.tear_off::<usize>();
        assert!(wait_until(Duration::from_millis(300), || d
            .inner
            .running
            .load(SeqCst)));

        let (tx_a, rx_a) = mpsc::channel::<String>();
        let (tx_b, rx_b) = mpsc::channel::<usize>();
        let _ha = lst_a.subscribe(move |event| {
            let _ = tx_a.send(event.to_string());
        });
        let _hb = lst_b.subscribe(move |event| {
            let _ = tx_b.send(event);
        });

        // Interleave messages
        src_a.send("a1".to_string());
        src_b.send(1usize);
        src_a.send("a2".to_string());

        // Flushing A should not require B to be drained to deliver A's messages
        assert!(d.flush_channel(src_a.id(), Duration::from_millis(500)));

        // Drain A; should get both a1 and a2 (order not guaranteed here, but both present)
        let mut got = vec![];
        while let Ok(s) = rx_a.try_recv() {
            got.push(s);
        }
        assert!(got.contains(&"a1".to_string()));
        assert!(got.contains(&"a2".to_string()));

        // B's message still there
        assert_eq!(rx_b.recv_timeout(Duration::from_millis(300)).unwrap(), 1);

        drop(src_a);
        drop(src_b);
        assert!(wait_until(Duration::from_millis(600), || !d
            .inner
            .running
            .load(SeqCst)));
    }
}
