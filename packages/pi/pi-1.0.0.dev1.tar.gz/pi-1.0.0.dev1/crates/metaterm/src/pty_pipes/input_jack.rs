use std::{
    borrow::Cow,
    os::fd::RawFd,
    sync::{
        Arc, Mutex,
        atomic::{AtomicI16, AtomicPtr, Ordering},
    },
};

use pishell_eventbus::{DISPATCHER, EventListeners, EventSource};
use tracing::debug;
use vtinput::Encode;

use crate::{TerminalSize, trigger::AtomicTrigger};
use crate::{pty_pipes::input_mode::InputMode, safe_libc};

#[derive(Debug)]
pub enum Input<'a> {
    Raw(&'a [u8]),
    TerminalEvent(vtinput::TerminalInputEvent<'a>),
    Size(TerminalSize),
    BracketedPaste(BracketedPaste<'a>),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum InputOwned {
    Raw(Vec<u8>),
    TerminalEvent(vtinput::TerminalInputEventOwned),
    Size(TerminalSize),
    BracketedPaste(BracketedPaste<'static>),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BracketedPaste<'a> {
    /// The start of the bracketed paste.
    Start,
    /// The end of the bracketed paste.
    End,
    /// The content of the bracketed paste.
    /// Multiple chunks of data can be sent.
    Content(Cow<'a, [u8]>),
}

impl Into<InputOwned> for Input<'_> {
    fn into(self) -> InputOwned {
        match self {
            Input::Raw(data) => InputOwned::Raw(data.to_vec()),
            Input::TerminalEvent(event) => InputOwned::TerminalEvent(event.to_owned()),
            Input::Size(size) => InputOwned::Size(size),
            Input::BracketedPaste(BracketedPaste::Content(paste)) => {
                InputOwned::BracketedPaste(BracketedPaste::Content(paste.into_owned().into()))
            }
            Input::BracketedPaste(BracketedPaste::Start) => {
                InputOwned::BracketedPaste(BracketedPaste::Start)
            }
            Input::BracketedPaste(BracketedPaste::End) => {
                InputOwned::BracketedPaste(BracketedPaste::End)
            }
        }
    }
}

pub trait AcceptsInput: 'static {
    fn accept_input(&self, input: Input<'_>) -> bool;
}

impl<F> AcceptsInput for F
where
    F: for<'a> Fn(Input<'a>) -> bool + 'static,
{
    fn accept_input(&self, input: Input<'_>) -> bool {
        self(input)
    }
}

impl<T> AcceptsInput for Mutex<T>
where
    T: Extend<InputOwned> + 'static,
{
    fn accept_input(&self, input: Input<'_>) -> bool {
        let owned = input.into();
        self.lock().unwrap().extend([owned]);
        true
    }
}

#[derive(derive_more::Debug)]
pub struct FdAcceptsInput {
    #[debug("{fd}")]
    fd: RawFd,
    mutex: Mutex<[u8; 1024]>,
    input_mode: InputMode,
}

impl FdAcceptsInput {
    pub fn new(fd: RawFd) -> Self {
        Self {
            fd,
            mutex: Mutex::new([0_u8; 1024]),
            input_mode: InputMode::new(),
        }
    }

    pub fn input_mode(&self) -> &InputMode {
        &self.input_mode
    }
}

impl AcceptsInput for FdAcceptsInput {
    fn accept_input(&self, input: Input<'_>) -> bool {
        // Acquire the buffer for all paths to prevent contention
        let mut buffer = self.mutex.lock().unwrap();

        match input {
            Input::BracketedPaste(BracketedPaste::Content(paste)) => {
                if safe_libc::write_all(self.fd, paste.as_ref()).is_err() {
                    return false;
                }
            }
            Input::BracketedPaste(BracketedPaste::Start) => {
                if safe_libc::write_all(self.fd, b"\x1b[200~").is_err() {
                    return false;
                }
            }
            Input::BracketedPaste(BracketedPaste::End) => {
                if safe_libc::write_all(self.fd, b"\x1b[201~").is_err() {
                    return false;
                }
            }
            Input::Raw(data) => {
                if safe_libc::write_all(self.fd, data).is_err() {
                    return false;
                }
            }
            Input::TerminalEvent(event) => {
                let input_mode = self.input_mode.get();
                match event {
                    vtinput::TerminalInputEvent::Key(mut key) => {
                        let size = key.encode(&mut *buffer).unwrap();
                        if safe_libc::write_all(self.fd, &buffer[..size]).is_err() {
                            return false;
                        }
                    }
                    vtinput::TerminalInputEvent::Mouse(mut mouse) => {
                        // If the mouse format is not set, don't send the mouse event
                        if input_mode.mouse_mode().matches(&mouse) {
                            let size = mouse.encode(&mut *buffer).unwrap();
                            if safe_libc::write_all(self.fd, &buffer[..size]).is_err() {
                                return false;
                            }
                        }
                    }
                    vtinput::TerminalInputEvent::Focus(gained) => {
                        let focus_bytes = if gained { b"\x1b[I" } else { b"\x1b[O" };
                        if safe_libc::write_all(self.fd, focus_bytes).is_err() {
                            return false;
                        }
                    }
                    vtinput::TerminalInputEvent::Paste(paste) => {
                        if safe_libc::write_all(self.fd, paste).is_err() {
                            return false;
                        }
                    }
                    vtinput::TerminalInputEvent::Resize(_cols, _rows) => {
                        // Resize events are not sent as input to the terminal
                    }
                    #[cfg(unix)]
                    vtinput::TerminalInputEvent::CursorPosition(_col, _row) => {
                        // Cursor position is a response from the terminal, not input
                    }
                    #[cfg(unix)]
                    vtinput::TerminalInputEvent::KeyboardEnhancementFlags(_flags) => {
                        // Enhancement flags are responses, not input
                    }
                    #[cfg(unix)]
                    vtinput::TerminalInputEvent::KeyboardEnhancementFlagsPush(_flags) => {
                        // Enhancement flags push are responses, not input
                    }
                    #[cfg(unix)]
                    vtinput::TerminalInputEvent::KeyboardEnhancementFlagsPop(_flags) => {
                        // Enhancement flags pop are responses, not input
                    }
                    #[cfg(unix)]
                    vtinput::TerminalInputEvent::KeyboardEnhancementFlagsQuery => {
                        // Enhancement flags query are responses, not input
                    }
                    #[cfg(unix)]
                    vtinput::TerminalInputEvent::PrimaryDeviceAttributes => {
                        // Device attributes are responses, not input
                    }
                    vtinput::TerminalInputEvent::LowLevel(_vt_event) => {
                        // Low-level events are already processed
                    }
                }
            }
            Input::Size(_size) => {}
        }

        true
    }
}

impl AcceptsInput for () {
    fn accept_input(&self, _: Input<'_>) -> bool {
        false
    }
}

pub trait ProvidesInput {
    fn attach(&self, accepts_input: Arc<dyn AcceptsInput>);
    fn detact(&self);
}

/// An input jack interposer that offsets the mouse coordinates.
pub struct OffsetMouseInputJack {
    input_jack: AtomicAcceptHandle,
    x: AtomicI16,
    y: AtomicI16,
}

impl OffsetMouseInputJack {
    pub fn new(x: i16, y: i16) -> Self {
        Self {
            input_jack: AtomicAcceptHandle::new(),
            x: AtomicI16::new(x),
            y: AtomicI16::new(y),
        }
    }

    pub fn set_offset(&self, x: i16, y: i16) {
        self.x.store(x, Ordering::Relaxed);
        self.y.store(y, Ordering::Relaxed);
    }

    pub fn attach(&self, accepts_input: Arc<dyn AcceptsInput>) {
        self.input_jack.attach(accepts_input);
    }

    pub fn detach(&self) {
        self.input_jack.detach();
    }
}

impl AcceptsInput for OffsetMouseInputJack {
    fn accept_input(&self, input: Input<'_>) -> bool {
        if let Input::TerminalEvent(vtinput::TerminalInputEvent::Mouse(mouse)) = input {
            let mut event = mouse;
            event.column = event
                .column
                .saturating_add_signed(self.x.load(Ordering::Relaxed));
            event.row = event
                .row
                .saturating_add_signed(self.y.load(Ordering::Relaxed));
            return self.input_jack.accept_input(Input::TerminalEvent(
                vtinput::TerminalInputEvent::Mouse(event),
            ));
        }
        self.input_jack.accept_input(input)
    }
}

/// A input jack interposer that triggers an event when a control character is
/// received.
pub struct TriggeredInputJack {
    input_jack: AtomicAcceptHandle,
    trigger: AtomicTrigger,
    trigger_event: EventListeners<usize>,
    trigger_event_source: EventSource<usize>,
}

impl TriggeredInputJack {
    pub fn new() -> Self {
        let (trigger_event_source, trigger_event) = DISPATCHER.tear_off();

        Self {
            input_jack: AtomicAcceptHandle::new(),
            trigger: AtomicTrigger::new(),
            trigger_event,
            trigger_event_source,
        }
    }

    pub fn ctrl(&self, letter: char) {
        self.trigger.ctrl(letter);
    }

    pub fn esc(&self) {
        self.trigger.esc();
    }

    pub fn trigger_event(&self) -> &EventListeners<usize> {
        &self.trigger_event
    }

    pub fn attach(&self, accepts_input: Arc<dyn AcceptsInput>) {
        self.input_jack.attach(accepts_input);
    }

    pub fn detach(&self) {
        self.input_jack.detach();
    }
}

impl AcceptsInput for TriggeredInputJack {
    fn accept_input(&self, input: Input<'_>) -> bool {
        if let Input::TerminalEvent(vtinput::TerminalInputEvent::Key(ref key)) = input {
            if let Some(char) = self.trigger.matches(key) {
                debug!("TriggeredInputJack: matched: {:?}", key);
                self.trigger_event_source.send(char);
                return true;
            }
        }
        self.input_jack.accept_input(input)
    }
}

/// A atomic handle to an AcceptsInput that can be attached to a ProvidesInput.
pub struct AtomicAcceptHandle {
    provides_input: AtomicPtr<AcceptsInputWrapper>,
}

struct AcceptsInputWrapper {
    accepts_input: Arc<dyn AcceptsInput>,
}

impl AtomicAcceptHandle {
    pub fn new() -> Self {
        Self {
            provides_input: AtomicPtr::new(std::ptr::null_mut()),
        }
    }

    pub fn from(provides_input: Arc<dyn AcceptsInput>) -> Self {
        Self {
            provides_input: AtomicPtr::new(Box::into_raw(Box::new(AcceptsInputWrapper {
                accepts_input: provides_input,
            }))),
        }
    }

    pub fn accept_input(&self, input: Input<'_>) -> bool {
        let wrapper = self.provides_input.load(Ordering::Relaxed);
        let Some(wrapper) = (unsafe { wrapper.as_mut() }) else {
            return false;
        };
        wrapper.accepts_input.accept_input(input)
    }

    pub fn attach(&self, provides_input: Arc<dyn AcceptsInput>) {
        let raw = Box::into_raw(Box::new(AcceptsInputWrapper {
            accepts_input: provides_input,
        }));
        let old = self.provides_input.swap(raw, Ordering::Relaxed);
        if !old.is_null() {
            drop(unsafe { Box::from_raw(old) });
        }
    }

    pub fn detach(&self) {
        let old = self
            .provides_input
            .swap(std::ptr::null_mut(), Ordering::Relaxed);
        if !old.is_null() {
            drop(unsafe { Box::from_raw(old) });
        }
    }
}
