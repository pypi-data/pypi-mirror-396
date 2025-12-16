use std::sync::{
    Arc,
    atomic::{AtomicUsize, Ordering},
};

use tracing::info;
use vt_push_parser::{VTEscapeSignature, event::VTEvent};

use crate::pty_pipes::input_mode::consts::{MODE_MOUSE_MOTION, MODE_MOUSE_X11};

pub(crate) mod consts {
    #![allow(unused)]

    // Key mode constants

    /// Application cursor keys mode (DECCKM)
    pub const MODE_KEY_APPLICATION_CURSOR_KEYS: usize = 1;
    /// Application keypad mode (DECNKM)
    pub const MODE_KEY_APPLICATION_KEYPAD: usize = 66;
    /// Application escape mode (https://github.com/mintty/mintty/wiki/CtrlSeqs).
    pub const MODE_KEY_APPLICATION_ESCAPE: usize = 7727;
    /// Delete sends DEL mode ("Send DEL from the editing-keypad Delete key" from
    /// <https://wiki.tau.garden/dec-modes/>),
    /// <https://github.com/mintty/mintty/issues/406>
    pub const MODE_KEY_DELETE_SENDS_DEL: usize = 1037;
    /// Send ESC when ALT modifies the keycode
    pub const MODE_KEY_SEND_ESC_WHEN_ALT_MODIFIES: usize = 1039;
    /// F1 key sends terminfo style sequence ESC[11~
    pub const MODE_KEY_F1_TERMINFO: usize = 1050;
    /// F1 key sends Sun style sequence ESC[224z
    pub const MODE_KEY_F1_SUN: usize = 1051;
    /// F1 key sends HP style sequence ESC&vF1k or similar
    pub const MODE_KEY_F1_HP: usize = 1052;
    /// F1 key sends SCO style sequence ESC[M
    pub const MODE_KEY_F1_SCO: usize = 1053;
    /// Enable X11R6 legacy keyboard mode — old X11R6-style function keys
    pub const MODE_KEY_F1_X11R6: usize = 1060;
    /// F1 key sends VT220 style sequence ESCOP (VT PF1)
    pub const MODE_KEY_F1_VT220: usize = 1061;

    // Mouse mode constants
    /// X10 mouse mode: send X&Y mouse on button press.
    pub const MODE_MOUSE_X10: usize = 9;
    /// X11/VT200 mouse mode: send X&Y mouse on button press/release.
    pub const MODE_MOUSE_X11: usize = 1000;
    /// "Mouse highlight tracking notifies a program of a button press, receives a range of lines from the program, highlights
    /// the region covered by the mouse within that range until button release, and then sends the program the release coor-
    /// dinates" <https://invisible-island.net/xterm/ctlseqs/ctlseqs.pdf>
    pub const MODE_MOUSE_HILITE: usize = 1001;
    // Also report button+motion events.
    pub const MODE_MOUSE_DRAG: usize = 1002;
    /// Also report motion without button press.
    pub const MODE_MOUSE_MOTION: usize = 1003;
    /// Enable UTF-8 encoding for mouse events.
    pub const MODE_MOUSE_UTF8: usize = 1005;
    /// SGR mouse mode: (CSI <)
    pub const MODE_MOUSE_SGR: usize = 1006;
    /// Same encoding as X10, but decimal (ambiguous with "delete lines" escapes)
    pub const MODE_MOUSE_URXVT: usize = 1015;
    /// SGR mouse mode, pixel coordinates: (CSI <)
    pub const MODE_MOUSE_SGR_PIXEL: usize = 1016;

    // Focus modes
    pub const MODE_FOCUS_REPORTING: usize = 1004;

    /// Bracketed paste mode: (`ESC [ 2 0 0 ~` pasted text `ESC [ 2 0 1 ~`)
    pub const MODE_BRACKETED_PASTE: usize = 2004;
}

const CSI_SET_MODE: VTEscapeSignature = VTEscapeSignature::csi(b'h').with_params_exact(1);
const CSI_UNSET_MODE: VTEscapeSignature = VTEscapeSignature::csi(b'l').with_params_exact(1);
const CSI_PRIVATE_SET_MODE: VTEscapeSignature = CSI_SET_MODE.with_private(b'?');
const CSI_PRIVATE_UNSET_MODE: VTEscapeSignature = CSI_UNSET_MODE.with_private(b'?');
const CSI_KITTY_KEY_PUSH: VTEscapeSignature = VTEscapeSignature::csi(b'u')
    .with_private(b'>')
    .with_params_exact(1);
const CSI_KITTY_KEY_POP: VTEscapeSignature = VTEscapeSignature::csi(b'u').with_private(b'<');
const MOUSE_FORMAT_SHIFT: usize = 32;
const MOUSE_FORMAT_MASK: usize = 0xffff << MOUSE_FORMAT_SHIFT;
const MOUSE_MODE_SHIFT: usize = 16;
const MOUSE_MODE_MASK: usize = 0xffff << MOUSE_MODE_SHIFT;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum MouseFormat {
    None,
    Xterm,
    XtermUtf8,
    Urxvt,
    Sgr,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum MouseMode {
    None,
    Press,
    PressRelease,
    ButtonMotion,
    AllMotion,
}

impl MouseMode {
    pub fn matches(&self, event: &vtinput::event::MouseEvent) -> bool {
        use vtinput::event::*;
        match (self, event.kind) {
            (MouseMode::None, _) => true,
            (_, MouseEventKind::Down(_)) => true,
            (MouseMode::Press, _) => false,
            (_, MouseEventKind::Up(_)) => true,
            (MouseMode::PressRelease, _) => false,
            (_, MouseEventKind::Drag(_)) => true,
            (MouseMode::ButtonMotion, _) => false,
            (MouseMode::AllMotion, _) => true,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct InputModeSnapshot {
    flags: u16,
    mouse_mode: u8,
    mouse_format: u8,
}

impl InputModeSnapshot {
    fn unpack(mode: usize) -> Self {
        Self {
            flags: (mode & 0xFFFF) as u16,
            mouse_mode: ((mode >> MOUSE_MODE_SHIFT) & 0xFF) as u8,
            mouse_format: ((mode >> MOUSE_FORMAT_SHIFT) & 0xFF) as u8,
        }
    }

    fn pack(self) -> usize {
        self.flags as usize
            | ((self.mouse_mode as usize) << MOUSE_MODE_SHIFT)
            | ((self.mouse_format as usize) << MOUSE_FORMAT_SHIFT)
    }

    #[inline(always)]
    pub fn mouse_mode(&self) -> MouseMode {
        match self.mouse_mode {
            1 => MouseMode::Press,
            2 => MouseMode::PressRelease,
            3 => MouseMode::ButtonMotion,
            4 => MouseMode::AllMotion,
            _ => MouseMode::None,
        }
    }

    #[inline(always)]
    pub fn mouse_format(&self) -> MouseFormat {
        match self.mouse_format {
            1 => MouseFormat::XtermUtf8,
            2 => MouseFormat::Urxvt,
            3 => MouseFormat::Sgr,
            _ => {
                if self.mouse_mode != 0 {
                    MouseFormat::Xterm
                } else {
                    MouseFormat::None
                }
            }
        }
    }

    #[inline(always)]
    pub fn application_cursor_keys_mode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_KEY_APPLICATION_CURSOR_KEYS)) != 0
    }

    #[inline(always)]
    pub fn application_keypad_mode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_KEY_APPLICATION_KEYPAD)) != 0
    }

    #[inline(always)]
    pub fn application_escape_mode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_KEY_APPLICATION_ESCAPE)) != 0
    }

    #[inline(always)]
    pub fn delete_sends_del_mode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_KEY_DELETE_SENDS_DEL)) != 0
    }

    #[inline(always)]
    pub fn send_esc_when_alt_modifies_keycode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_KEY_SEND_ESC_WHEN_ALT_MODIFIES)) != 0
    }

    #[inline(always)]
    pub fn focus_reporting_mode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_FOCUS_REPORTING)) != 0
    }

    #[inline(always)]
    pub fn bracketed_paste_mode(&self) -> bool {
        self.flags & (1 << mode_to_bit(consts::MODE_BRACKETED_PASTE)) != 0
    }
}

#[derive(Default, Debug, Clone)]
pub struct InputMode {
    mode: Arc<AtomicUsize>,
}

const fn mode_to_bit(mode: usize) -> usize {
    match mode {
        consts::MODE_KEY_APPLICATION_CURSOR_KEYS => 0,
        consts::MODE_KEY_APPLICATION_KEYPAD => 1,
        consts::MODE_KEY_APPLICATION_ESCAPE => 2,
        consts::MODE_KEY_DELETE_SENDS_DEL => 3,
        consts::MODE_KEY_SEND_ESC_WHEN_ALT_MODIFIES => 4,
        consts::MODE_FOCUS_REPORTING => 5,
        consts::MODE_BRACKETED_PASTE => 6,
        _ => unreachable!(),
    }
}

impl InputMode {
    pub fn new() -> Self {
        Self {
            mode: Arc::new(AtomicUsize::new(0)),
        }
    }

    #[inline(always)]
    pub fn is_mode_event(&self, event: &VTEvent) -> bool {
        for mode in [
            CSI_SET_MODE,
            CSI_UNSET_MODE,
            CSI_PRIVATE_SET_MODE,
            CSI_PRIVATE_UNSET_MODE,
        ] {
            if mode.matches(&event) {
                if self.is_mode_supported(
                    event
                        .csi()
                        .unwrap()
                        .params
                        .try_parse::<usize>(0)
                        .unwrap_or(0),
                ) {
                    return true;
                }
            }
        }
        false
    }

    #[inline(always)]
    pub fn is_mode_supported(&self, mode: usize) -> bool {
        match mode {
            consts::MODE_KEY_APPLICATION_CURSOR_KEYS
            | consts::MODE_KEY_APPLICATION_KEYPAD
            | consts::MODE_KEY_APPLICATION_ESCAPE
            | consts::MODE_KEY_DELETE_SENDS_DEL
            | consts::MODE_KEY_SEND_ESC_WHEN_ALT_MODIFIES
            | consts::MODE_FOCUS_REPORTING
            | consts::MODE_BRACKETED_PASTE
            | consts::MODE_MOUSE_X10
            | consts::MODE_MOUSE_X11
            | consts::MODE_MOUSE_DRAG
            | consts::MODE_MOUSE_MOTION
            | consts::MODE_MOUSE_UTF8
            | consts::MODE_MOUSE_SGR
            | consts::MODE_MOUSE_URXVT => true,
            _ => false,
        }
    }

    #[inline(always)]
    pub fn reset(&self) {
        self.mode.store(0, Ordering::Relaxed);
    }

    #[inline(always)]
    pub fn set_mode(&self, mode: usize) -> bool {
        self.update_mode(mode, true)
    }

    #[inline(always)]
    pub fn unset_mode(&self, mode: usize) -> bool {
        self.update_mode(mode, false)
    }

    fn update_mode(&self, mode: usize, is_set: bool) -> bool {
        match mode {
            consts::MODE_KEY_APPLICATION_CURSOR_KEYS
            | consts::MODE_KEY_APPLICATION_KEYPAD
            | consts::MODE_KEY_APPLICATION_ESCAPE
            | consts::MODE_KEY_DELETE_SENDS_DEL
            | consts::MODE_KEY_SEND_ESC_WHEN_ALT_MODIFIES => {
                let bit = match mode {
                    consts::MODE_KEY_APPLICATION_CURSOR_KEYS => 0,
                    consts::MODE_KEY_APPLICATION_KEYPAD => 1,
                    consts::MODE_KEY_APPLICATION_ESCAPE => 2,
                    consts::MODE_KEY_DELETE_SENDS_DEL => 3,
                    consts::MODE_KEY_SEND_ESC_WHEN_ALT_MODIFIES => 4,
                    consts::MODE_FOCUS_REPORTING => 5,
                    consts::MODE_BRACKETED_PASTE => 6,
                    _ => unreachable!(),
                };
                if is_set {
                    let previous = self.mode.fetch_or(1 << bit, Ordering::Relaxed);
                    if previous & (1 << bit) == 0 {
                        info!("Input mode set: {}", mode);
                        true
                    } else {
                        false
                    }
                } else {
                    let previous = self.mode.fetch_and(!(1 << bit), Ordering::Relaxed);
                    if previous & (1 << bit) != 0 {
                        info!("Input mode unset: {}", mode);
                        true
                    } else {
                        false
                    }
                }
            }
            consts::MODE_MOUSE_X10
            | consts::MODE_MOUSE_X11
            | consts::MODE_MOUSE_DRAG
            | consts::MODE_MOUSE_MOTION => {
                let mouse_mode = match mode {
                    consts::MODE_MOUSE_X10 => 1,
                    consts::MODE_MOUSE_X11 => 2,
                    consts::MODE_MOUSE_DRAG => 3,
                    consts::MODE_MOUSE_MOTION => 4,
                    _ => unreachable!(),
                } << MOUSE_MODE_SHIFT;
                if is_set {
                    let previous = self
                        .mode
                        .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |value| {
                            Some((value & !MOUSE_MODE_MASK) | mouse_mode)
                        })
                        .unwrap();
                    if previous & MOUSE_MODE_MASK != mouse_mode {
                        info!("Input mouse mode set: {}", mode);
                        true
                    } else {
                        false
                    }
                } else {
                    let previous = self
                        .mode
                        .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |value| {
                            if value & MOUSE_MODE_MASK == mouse_mode {
                                Some(value & !MOUSE_MODE_MASK)
                            } else {
                                Some(value)
                            }
                        })
                        .unwrap();
                    if previous & MOUSE_MODE_MASK == mouse_mode {
                        info!("Input mouse mode unset: {}", mode);
                        true
                    } else {
                        false
                    }
                }
            }
            consts::MODE_MOUSE_UTF8 | consts::MODE_MOUSE_SGR | consts::MODE_MOUSE_URXVT => {
                let mouse_format = match mode {
                    consts::MODE_MOUSE_UTF8 => 1,
                    consts::MODE_MOUSE_URXVT => 2,
                    consts::MODE_MOUSE_SGR => 3,
                    _ => unreachable!(),
                } << MOUSE_FORMAT_SHIFT;
                if is_set {
                    let previous = self
                        .mode
                        .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |value| {
                            Some((value & !MOUSE_FORMAT_MASK) | mouse_format)
                        })
                        .unwrap();
                    if previous & MOUSE_FORMAT_MASK != mouse_format {
                        info!("Input mouse format set: {}", mode);
                        true
                    } else {
                        false
                    }
                } else {
                    let previous = self
                        .mode
                        .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |value| {
                            if value & MOUSE_FORMAT_MASK == mouse_format {
                                Some(value & !MOUSE_FORMAT_MASK)
                            } else {
                                Some(value)
                            }
                        })
                        .unwrap();
                    if previous & MOUSE_FORMAT_MASK == mouse_format {
                        info!("Input mouse format unset: {}", mode);
                        true
                    } else {
                        false
                    }
                }
            }
            _ => false,
        }
    }

    pub fn process_vt_event(&self, event: &VTEvent) {
        let csi = event.csi().unwrap();
        let mode = csi.params.try_parse::<usize>(0).unwrap_or(0);
        let is_private = csi.private.is_some();
        let is_set = csi.final_byte == b'h';

        if is_private {
            self.update_mode(mode, is_set);
        } else {
            // Nothing
        }
    }

    pub fn get(&self) -> InputModeSnapshot {
        InputModeSnapshot::unpack(self.mode.load(Ordering::Relaxed))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_mode_supported() {
        let input_mode = InputMode::new();
        assert!(input_mode.is_mode_supported(consts::MODE_KEY_APPLICATION_CURSOR_KEYS));
    }

    #[test]
    fn test_pack_unpack() {
        let input_mode = InputModeSnapshot {
            flags: 0,
            mouse_mode: 1,
            mouse_format: 0,
        };
        assert_eq!(InputModeSnapshot::unpack(input_mode.pack()), input_mode);
        let input_mode = InputModeSnapshot {
            flags: 2,
            mouse_mode: 1,
            mouse_format: 0,
        };
        assert_eq!(InputModeSnapshot::unpack(input_mode.pack()), input_mode);
        let input_mode = InputModeSnapshot {
            flags: 2,
            mouse_mode: 5,
            mouse_format: 4,
        };
        assert_eq!(InputModeSnapshot::unpack(input_mode.pack()), input_mode);
    }

    #[test]
    fn test_set_unset_mouse() {
        let input_mode = InputMode::new();

        assert!(input_mode.set_mode(consts::MODE_MOUSE_X10));
        assert!(!input_mode.set_mode(consts::MODE_MOUSE_X10));
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::Press);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Xterm);
        assert!(input_mode.unset_mode(consts::MODE_MOUSE_X10));
        assert!(!input_mode.unset_mode(consts::MODE_MOUSE_X10));
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::None);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::None);

        assert!(input_mode.set_mode(consts::MODE_MOUSE_DRAG));
        assert!(input_mode.set_mode(consts::MODE_MOUSE_SGR));
        assert!(input_mode.unset_mode(consts::MODE_MOUSE_DRAG));
        assert!(input_mode.unset_mode(consts::MODE_MOUSE_SGR));
    }

    #[test]
    fn test_set_mouse_mode() {
        let input_mode = InputMode::new();
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::None);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::None);

        input_mode.set_mode(consts::MODE_MOUSE_X10);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::Press);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Xterm);

        input_mode.reset();

        input_mode.set_mode(consts::MODE_MOUSE_X11);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::PressRelease);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Xterm);

        input_mode.reset();

        input_mode.set_mode(consts::MODE_MOUSE_MOTION);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::AllMotion);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Xterm);

        input_mode.reset();

        input_mode.set_mode(consts::MODE_MOUSE_SGR);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::None);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Sgr);
        input_mode.set_mode(consts::MODE_MOUSE_X10);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::Press);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Sgr);

        input_mode.reset();

        input_mode.set_mode(consts::MODE_MOUSE_SGR);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::None);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Sgr);
        input_mode.set_mode(consts::MODE_MOUSE_X11);
        assert_eq!(input_mode.get().mouse_mode(), MouseMode::PressRelease);
        assert_eq!(input_mode.get().mouse_format(), MouseFormat::Sgr);

        input_mode.reset();

        input_mode.set_mode(consts::MODE_MOUSE_DRAG);
        assert_eq!(
            input_mode.get().mouse_mode(),
            MouseMode::ButtonMotion,
            "{:?}",
            input_mode.get()
        );
        assert_eq!(
            input_mode.get().mouse_format(),
            MouseFormat::Xterm,
            "{:?}",
            input_mode.get()
        );

        input_mode.set_mode(consts::MODE_MOUSE_MOTION);
        assert_eq!(
            input_mode.get().mouse_mode(),
            MouseMode::AllMotion,
            "{:?}",
            input_mode.get()
        );
        assert_eq!(
            input_mode.get().mouse_format(),
            MouseFormat::Xterm,
            "{:?}",
            input_mode.get()
        );

        input_mode.set_mode(consts::MODE_MOUSE_UTF8);
        assert_eq!(
            input_mode.get().mouse_mode(),
            MouseMode::AllMotion,
            "{:?}",
            input_mode.get()
        );
        assert_eq!(
            input_mode.get().mouse_format(),
            MouseFormat::XtermUtf8,
            "{:?}",
            input_mode.get()
        );
    }
}
