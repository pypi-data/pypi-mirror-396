pub mod error;
pub mod events;
pub mod osc133;
mod process;
mod process_handle;
mod pty;
mod pty_pipes;
mod real_terminal;
pub mod safe_libc;
mod terminal;
mod terminal_size;
mod trigger;
mod virtual_pty;

pub use events::OutputEvent;
pub use osc133::Osc133Type;
pub use process::{Process, ProcessSetup, ProcessSetupBuilder};
pub use process_handle::ProcessHandle;
pub use pty::spawn_in_pty;
pub use pty_pipes::{
    IdleType, PipeMode,
    input_jack::{Input, InputOwned, OffsetMouseInputJack, TriggeredInputJack},
    real_input_pipe::InputPipe,
};
pub use real_terminal::raw_terminal::TerminalGuard;
pub use real_terminal::{CursorShape, RealTerminal, TerminalInfo, terminal_info};
pub use terminal::Terminal;
pub use terminal_size::TerminalSize;
pub use virtual_pty::VirtualPty;

/// This is a xterm escape sequence that normalizes the xterm-like terminal to a
/// known state (works for xterm and wezterm, at least).
///
/// First, we set the terminal to UTF-8 mode.
///
/// `ESC % G` -> UTF-8 mode
///
/// We want to disable xterm keyboard handling modes, and enable ALT-sends-ESC
/// and Meta-sends-ESC.
///
/// `CSI [ ? <mode> l` (disable):
///  * 1050: Set terminfo/termcap function-key mode
///  * 1051: Set Sun function-key mode
///  * 1052: Set HP function-key mode
///  * 1053: Set SCO function-key mode
///  * 1060: Set legacy function-key mode
///  * 1061: Set VT220 function-key mode
///
/// `CSI [ ? 1036 h` (enable):
///  * 1036: Send ESC when Meta modifies a key
///  * 1039: Send ESC when ALT modifies the keycode
///
/// Finally, we set `modify{Cursor,Function,Keypad,Other,Modifier,Special}Keys`
/// to 1 or 2 which will try to use the `CSI [ 27 ; mod ; key ~` sequence.
///
/// `CSI [ > Pp ; 1 m`:
///
///  * `Pp` = 1: `modifyCursorKeys` (2)
///  * `Pp` = 2: `modifyFunctionKey` (2)
///  * `Pp` = 3: `modifyKeypadKeys` (2)
///  * `Pp` = 4: `modifyOtherKeys` (1)
///  * `Pp` = 6: `modifyModifierKey` (2)
///  * `Pp` = 7: `modifySpecialKey` (2)
pub const XTERM_NORMALIZE: &[u8] = &XTERM_NORMALIZE_RAW;

const XTERM_NORMALIZE_RAW: [u8; XTERM_NORMALIZE_STRINGS_LEN] = {
    let mut output = [0; XTERM_NORMALIZE_STRINGS_LEN];

    let mut i = 0;
    let mut l = 0;
    while i < XTERM_NORMALIZE_STRINGS.len() {
        let mut j = 0;
        while j < XTERM_NORMALIZE_STRINGS[i].len() {
            output[l] = XTERM_NORMALIZE_STRINGS[i][j];
            j += 1;
            l += 1;
        }
        i += 1;
    }
    if l != output.len() {
        panic!("XTERM_NORMALIZE is not the correct length");
    }
    output
};

const XTERM_NORMALIZE_STRINGS_LEN: usize = {
    let mut len = 0;
    let mut i = 0;
    while i < XTERM_NORMALIZE_STRINGS.len() {
        len += XTERM_NORMALIZE_STRINGS[i].len();
        i += 1;
    }
    len
};

const XTERM_NORMALIZE_STRINGS: &[&[u8]] = &[
    b"\x1b%G".as_slice(),
    b"\x1b[?1050l".as_slice(),
    b"\x1b[?1051l".as_slice(),
    b"\x1b[?1052l".as_slice(),
    b"\x1b[?1053l".as_slice(),
    b"\x1b[?1060l".as_slice(),
    b"\x1b[?1061l".as_slice(),
    b"\x1b[?1036h".as_slice(),
    b"\x1b[?1039h".as_slice(),
    b"\x1b[>1;2m".as_slice(),
    b"\x1b[>2;2m".as_slice(),
    b"\x1b[>3;2m".as_slice(),
    b"\x1b[>4;1m".as_slice(),
    b"\x1b[>6;2m".as_slice(),
    b"\x1b[>7;2m".as_slice(),
];
