use serde::{Deserialize, Serialize};

/// Various escape sequence types.
///
/// Reference: ECMA-48 - https://www.ecma-international.org/publications-and-standards/standards/ecma-48/
#[derive(Debug, Clone, Copy, derive_more::TryFrom)]
#[repr(u8)]
#[try_from(repr)]
pub enum EscapeSequenceType {
    /// Control Sequence Introducer (CSI)
    ///
    /// The Control Sequence Introducer (CSI) is used to introduce control sequences,
    /// which are commands or functions that modify the behavior of the terminal.
    /// CSI sequences typically start with an escape character (\x1B) followed by a
    /// left square bracket ([) and are used for tasks such as cursor movement, text
    /// formatting, color changes, and more.
    CSI = b'[',

    /// Operating System Command (OSC)
    ///
    /// The Operating System Command (OSC) is used to send commands directly to the
    /// terminal emulator or operating system. OSC sequences typically start with an
    /// escape character (\x1B) followed by a right square bracket (]), and they are
    /// often used for tasks like setting the terminal window title, changing the
    /// terminal's icon, or sending notifications to the user.
    OSC = b']',

    /// Single Shift 2 (SS2)
    ///
    /// The Single Shift 2 (SS2) sequence is used to switch between different
    /// character sets in the terminal. SS2 sequences typically start with an
    /// escape character (\x1B) followed by the letter 'N'. They are used in
    /// internationalization scenarios where different character sets are needed.
    SS2 = b'N',

    /// Single Shift 3 (SS3)
    ///
    /// The Single Shift 3 (SS3) sequence is used to switch between different
    /// character sets in the terminal. SS3 sequences typically start with an
    /// escape character (\x1B) followed by the letter 'O'. They are used in
    /// internationalization scenarios where different character sets are needed.
    SS3 = b'O',

    /// Device Control String (DCS)
    ///
    /// The Device Control String (DCS) is similar to the OSC sequence but is used
    /// for more advanced device control. DCS sequences typically start with an
    /// escape character (\x1B) followed by the letter 'P', and they allow for more
    /// complex interactions with the terminal hardware or emulator.
    DCS = b'P',

    /// Privacy Message (PM)
    ///
    /// The Privacy Message (PM) sequence is similar to the OSC and DCS sequences
    /// but serves different purposes. PM sequences typically start with an escape
    /// character (\x1B) followed by the caret (^), and they are used for various
    /// communication and control tasks, including passing data between applications
    /// and the terminal emulator.
    PM = b'^',

    /// Application Program Command (APC)
    ///
    /// The Application Program Command (APC) sequence is similar to the OSC and DCS
    /// sequences but serves different purposes. APC sequences typically start with
    /// an escape character (\x1B) followed by the underscore (_), and they are used
    /// for various communication and control tasks, including passing data between
    /// applications and the terminal emulator.
    APC = b'_',

    /// String Terminator (ST)
    ///
    /// The String Terminator (ST) is used to indicate the end of an escape sequence.
    /// ST sequences typically start with an escape character (\x1B) followed by a
    /// backslash (\), and they signal the end of the escape sequence.
    ST = b'\\',

    /// DECKPAM (DEC Keypad Application Mode) Escape Sequence.
    ///
    /// This escape sequence is used to enable the application keypad mode in a DEC VT220 terminal.
    /// When application keypad mode is enabled, certain keys on the keypad (such as function keys)
    /// send special escape sequences instead of their regular ASCII characters. For example, the
    /// Page Up key may send the sequence for Page Up instead of its regular ASCII character.
    ///
    /// https://vt100.net/docs/vt220-rm/chapter4.html
    DECKPAM = b'=',

    /// DECKPNM (DEC Keypad Numeric Mode) Escape Sequence.
    ///
    /// This escape sequence is used to disable the application keypad mode in a DEC VT220 terminal
    /// and switch back to the normal keypad mode where keys send their regular ASCII characters.
    ///
    /// https://vt100.net/docs/vt220-rm/chapter4.html
    DECKPNM = b'>',

    DECSC = b'7',
    DECRC = b'8',
}

impl EscapeSequenceType {
    pub fn as_str(&self) -> &'static str {
        match self {
            EscapeSequenceType::CSI => "\x1B[",
            EscapeSequenceType::OSC => "\x1B]",
            EscapeSequenceType::SS2 => "\x1BN",
            EscapeSequenceType::SS3 => "\x1BO",
            EscapeSequenceType::DCS => "\x1BP",
            EscapeSequenceType::PM => "\x1B^",
            EscapeSequenceType::APC => "\x1B_",
            EscapeSequenceType::ST => "\x1B\\",
            EscapeSequenceType::DECKPAM => "\x1B=",
            EscapeSequenceType::DECKPNM => "\x1B>",
            EscapeSequenceType::DECSC => "\x1B7",
            EscapeSequenceType::DECRC => "\x1B8",
        }
    }
}

#[derive(
    Debug,
    Clone,
    Copy,
    PartialEq,
    Eq,
    PartialOrd,
    Ord,
    Hash,
    Serialize,
    Deserialize,
    derive_more::TryFrom,
)]
#[repr(u8)]
#[try_from(repr)]
pub enum DA1 {
    Columns132 = 1,
    PrinterPort = 2,
    Sixel = 4,
    SelectiveErase = 6,
    SoftCharacterSet = 7,
    UserDefinedKeys = 8,
    NationalReplacementCharacterSets = 9,
    InternationalTerminalOnly = 10,
    Yugoslavian = 12,
    TechnicalCharacterSet = 15,
    WindowingCapability = 18,
    HorizontalScrolling = 21,
    Greek = 23,
    Turkish = 24,
    ISOLatin2CharacterSet = 42,
    PCTerm = 44,
    SoftKeyMap = 45,
    ASCIIEmulation = 46,
}

pub fn escape(escape_type: EscapeSequenceType, params: Option<&str>) -> Vec<u8> {
    let sequence = match params {
        Some(p) => format!("{}{}", escape_type.as_str(), p),
        None => escape_type.as_str().to_string(),
    };
    sequence.into_bytes()
}

// Function to report terminal size (DECSLPP)
pub fn report_terminal_size() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some("18t"))
}

// Function to report terminal device attributes
pub fn report_terminal_device_attributes() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some("c"))
}

// Function to report terminal device attributes
pub fn report_terminal_device_attributes2() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some(">c"))
}

// Function to report terminal device attributes
pub fn report_terminal_device_attributes3() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some("=c"))
}

#[derive(
    Debug,
    Clone,
    Copy,
    PartialEq,
    Eq,
    PartialOrd,
    Ord,
    Hash,
    Serialize,
    Deserialize,
    derive_more::TryFrom,
)]
#[repr(u16)]
#[try_from(repr)]
pub enum FeatureReport {
    AltScreenActive = 1049,
    BracketedPasteMode = 2004,
    MouseX10Mode = 9,
    MouseNormalMode = 1000,
    MouseVT200DragMode = 1002,
    MouseAnyEventMode = 1003,
    MouseSGRMode = 1006,
    MouseRXVTMode = 1015,
    FocusReportingMode = 1004,
    ApplicationCursorKeysMode = 1,
    AutoWrapMode = 7,
    CursorBlinking = 12,
    CursorVisible = 25,
    LinefeedNewlineMode = 20,

    AnsiInsertMode = 4,
}

impl FeatureReport {
    fn is_ansi(&self) -> bool {
        match self {
            FeatureReport::AnsiInsertMode | FeatureReport::LinefeedNewlineMode => true,
            _ => false,
        }
    }
}

pub fn report_feature(feature: FeatureReport) -> Vec<u8> {
    if feature.is_ansi() {
        // "standard" or ANSI mode
        escape(
            EscapeSequenceType::CSI,
            Some(&format!("{}$p", feature as u16)),
        )
    } else {
        // DEC extended mode
        escape(
            EscapeSequenceType::CSI,
            Some(&format!("?{}$p", feature as u16)),
        )
    }
}

#[derive(Debug, Clone, Copy)]
pub enum TerminalCapability {
    TN,
}

// Function to report terminal XTerm version
pub fn report_terminal_xt_get_cap(cap: TerminalCapability) -> Vec<u8> {
    match cap {
        TerminalCapability::TN => escape(
            EscapeSequenceType::DCS,
            Some(&format!("544e;{}", EscapeSequenceType::ST.as_str())),
        ),
    }
}

pub fn report_default_foreground() -> Vec<u8> {
    escape(
        EscapeSequenceType::OSC,
        Some(&format!("10;?{}", EscapeSequenceType::ST.as_str())),
    )
}

pub fn report_default_background() -> Vec<u8> {
    escape(
        EscapeSequenceType::OSC,
        Some(&format!("11;?{}", EscapeSequenceType::ST.as_str())),
    )
}

// Function to report terminal iTerm2 version
pub fn report_terminal_iterm2_version() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some("1337n"))
}

// Function to report terminal extended device attributes
pub fn report_terminal_extended_device_attributes() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some(">q"))
}

pub fn report_text_attributes() -> Vec<u8> {
    escape(
        EscapeSequenceType::DCS,
        Some(&format!("$qm{}", EscapeSequenceType::ST.as_str())),
    )
}

pub fn report_scrolling_top_bottom() -> Vec<u8> {
    escape(
        EscapeSequenceType::DCS,
        Some(&format!("$qr{}", EscapeSequenceType::ST.as_str())),
    )
}

pub fn report_scrolling_left_right() -> Vec<u8> {
    escape(
        EscapeSequenceType::DCS,
        Some(&format!("$qs{}", EscapeSequenceType::ST.as_str())),
    )
}

pub fn clear_line() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some("2K"))
}

// Function to report cursor position
pub fn report_cursor_position() -> Vec<u8> {
    escape(EscapeSequenceType::CSI, Some("6n"))
}

// Query cursor shape (DECSCUSR) - not standard but some terminals support
pub fn report_cursor_shape() -> Vec<u8> {
    // DECSCUSR w DECSCUSR
    escape(EscapeSequenceType::DCS, Some("$q q\x1b\\"))
}
