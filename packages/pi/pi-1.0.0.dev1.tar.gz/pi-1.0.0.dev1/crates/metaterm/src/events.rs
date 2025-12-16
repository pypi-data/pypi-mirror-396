use pishell_eventbus::{EventData, Eventable};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum OutputEvent {
    FirstByte,
    Bell,
    Line,
    BracketedPaste,
    Prompt(crate::osc133::Osc133Sequence),
}

impl Eventable for OutputEvent {
    type Recv<'a> = &'a OutputEvent;

    fn cast(data: &EventData) -> Self::Recv<'_> {
        match data {
            EventData::Boxed(boxed) => boxed.downcast_ref::<OutputEvent>().unwrap(),
            _ => unreachable!(),
        }
    }

    fn cast_send(self) -> EventData {
        EventData::Boxed(Box::new(self))
    }
}
