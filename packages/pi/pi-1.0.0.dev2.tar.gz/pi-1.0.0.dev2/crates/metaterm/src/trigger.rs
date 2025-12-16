use std::sync::{
    Arc,
    atomic::{AtomicUsize, Ordering},
};

const ESC_CHAR: char = '[';
const ESC_CODE: usize = 27;

#[derive(Clone)]
pub struct AtomicTrigger {
    trigger_event: Arc<AtomicUsize>,
}

fn map_ctrl_key_char(key: char) -> usize {
    match key {
        'a'..='z' => key.to_ascii_uppercase() as usize - b'A' as usize + 1,
        'A'..='Z' => key as usize - b'A' as usize + 1,
        ESC_CHAR => ESC_CODE,
        _ => usize::MAX,
    }
}

impl AtomicTrigger {
    pub fn new() -> Self {
        Self {
            trigger_event: Arc::new(AtomicUsize::new(usize::MAX)),
        }
    }

    pub fn ctrl(&self, letter: char) {
        let expected = map_ctrl_key_char(letter);
        self.trigger_event
            .store(expected as usize, Ordering::Relaxed);
    }

    pub fn esc(&self) {
        self.trigger_event
            .store(ESC_CODE as usize, Ordering::Relaxed);
    }

    pub fn clear(&self) {
        self.trigger_event.store(usize::MAX, Ordering::Relaxed);
    }

    #[inline]
    pub fn matches_ctrl(&self, key: char) -> Option<usize> {
        let expected = map_ctrl_key_char(key);
        if self.trigger_event.load(Ordering::Relaxed) == expected {
            Some(expected)
        } else {
            None
        }
    }

    #[inline]
    pub fn matches(&self, key_event: &vtinput::KeyEvent) -> Option<usize> {
        if key_event.modifiers == vtinput::KeyModifiers::CONTROL {
            let char = match key_event.code {
                vtinput::KeyCode::Char(c) => c,
                _ => '\0',
            };
            return self.matches_ctrl(char);
        } else if key_event.code == vtinput::KeyCode::Esc {
            if self.trigger_event.load(Ordering::Relaxed) == ESC_CODE {
                return Some(ESC_CODE);
            } else {
                return None;
            }
        }
        None
    }
}
