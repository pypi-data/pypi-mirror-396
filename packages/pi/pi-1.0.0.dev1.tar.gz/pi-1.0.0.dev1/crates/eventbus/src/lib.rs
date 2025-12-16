mod events;

pub use events::{DISPATCHER, EventListeners, EventSource, ListenerHandle};

pub enum EventData {
    Copy(usize),
    Boxed(Box<dyn std::any::Any + Send + 'static>),
}

pub trait Eventable
where
    Self: Send + Sync + 'static,
{
    type Recv<'a>;

    fn cast(data: &EventData) -> Self::Recv<'_>;
    fn cast_send(self) -> EventData;
}

impl Eventable for () {
    type Recv<'a> = ();

    fn cast(_: &EventData) -> Self::Recv<'_> {}

    fn cast_send(self) -> EventData {
        EventData::Copy(0)
    }
}

impl Eventable for String {
    type Recv<'a> = &'a str;

    fn cast(data: &EventData) -> Self::Recv<'_> {
        match data {
            EventData::Boxed(boxed) => boxed.downcast_ref::<String>().unwrap(),
            _ => unreachable!(),
        }
    }

    fn cast_send(self) -> EventData {
        EventData::Boxed(Box::new(self))
    }
}

impl Eventable for &'static str {
    type Recv<'a> = &'static str;

    fn cast(data: &EventData) -> Self::Recv<'_> {
        match data {
            EventData::Boxed(boxed) => boxed.downcast_ref::<&'static str>().unwrap(),
            _ => unreachable!(),
        }
    }

    fn cast_send(self) -> EventData {
        EventData::Boxed(Box::new(self))
    }
}

impl Eventable for usize {
    type Recv<'a> = usize;

    fn cast(data: &EventData) -> Self::Recv<'_> {
        match data {
            EventData::Copy(n) => *n,
            _ => unreachable!(),
        }
    }

    fn cast_send(self) -> EventData {
        EventData::Copy(self)
    }
}

impl Eventable for bool {
    type Recv<'a> = bool;

    fn cast(data: &EventData) -> Self::Recv<'_> {
        match data {
            EventData::Copy(n) => *n != 0,
            _ => unreachable!(),
        }
    }

    fn cast_send(self) -> EventData {
        EventData::Copy(if self { 1 } else { 0 })
    }
}
