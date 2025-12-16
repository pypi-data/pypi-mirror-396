use super::vt::{self, *};

use tracing::{debug, info};
use vt_push_parser::event::VTEvent;
use vt_push_parser::{VTEscapeSignature, VTPushParser};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CursorShape {
    Default,
    BlinkingBlock,
    SteadyBlock,
    BlinkingUnderline,
    SteadyUnderline,
    BlinkingBar,
    SteadyBar,
}

pub fn terminal_info() -> Result<TerminalInfo, std::io::Error> {
    let mut writer = std::io::stdout();
    let mut reader = std::io::stdin();

    let terminal_info = request_terminal_info(&mut writer, &mut reader)?;

    Ok(terminal_info)
}

#[allow(unused)]
fn debug<T: std::fmt::Debug>(value: Option<T>) -> String {
    if let Some(v) = value {
        format!("{:?}", v)
    } else {
        "(unset)".to_string()
    }
}

#[derive(Clone, Default, derive_more::Debug)]
pub struct TerminalInfo {
    #[debug("{}", debug(self.terminal_size))]
    pub terminal_size: Option<(u16, u16)>,
    #[debug("{}", debug(self.cursor_position))]
    pub cursor_position: Option<(u16, u16)>,
    #[debug("{}", debug(self.foreground_color.as_ref()))]
    pub foreground_color: Option<String>,
    #[debug("{}", debug(self.background_color.as_ref()))]
    pub background_color: Option<String>,
    #[debug("device_attributes={:?}", self.device_attributes)]
    pub device_attributes: Vec<vt::DA1>,
    #[debug("{}", debug(self.alt_screen_active))]
    pub alt_screen_active: Option<bool>,
    #[debug("{}", debug(self.bracketed_paste_mode))]
    pub bracketed_paste_mode: Option<bool>,
    #[debug("{}", debug(self.mouse_x10_mode))]
    pub mouse_x10_mode: Option<bool>,
    #[debug("{}", debug(self.mouse_normal_mode))]
    pub mouse_normal_mode: Option<bool>,
    #[debug("{}", debug(self.mouse_rxvt_mode))]
    pub mouse_rxvt_mode: Option<bool>,
    #[debug("{}", debug(self.mouse_vt200_drag_mode))]
    pub mouse_vt200_drag_mode: Option<bool>,
    #[debug("{}", debug(self.mouse_any_event_mode))]
    pub mouse_any_event_mode: Option<bool>,
    #[debug("{}", debug(self.mouse_sgr_mode))]
    pub mouse_sgr_mode: Option<bool>,
    #[debug("{}", debug(self.focus_reporting_mode))]
    pub focus_reporting_mode: Option<bool>,
    #[debug("{}", debug(self.application_cursor_keys_mode))]
    pub application_cursor_keys_mode: Option<bool>,
    #[debug("{}", debug(self.auto_wrap_mode))]
    pub auto_wrap_mode: Option<bool>,
    #[debug("{}", debug(self.insert_mode))]
    pub insert_mode: Option<bool>,
    #[debug("{}", debug(self.linefeed_newline_mode))]
    pub linefeed_newline_mode: Option<bool>,
    #[debug("{}", debug(self.cursor_shape))]
    pub cursor_shape: Option<CursorShape>,
    #[debug("{}", debug(self.cursor_visible))]
    pub cursor_visible: Option<bool>,
    #[debug("{}", debug(self.cursor_blinking))]
    pub cursor_blinking: Option<bool>,
}

const CURSOR_POSITION_REPORT: VTEscapeSignature = VTEscapeSignature::csi(b'R').with_params_exact(2);
const TERMINAL_SIZE_REPORT: VTEscapeSignature = VTEscapeSignature::csi(b't').with_params_exact(3);
const FEATURE_REPORT: VTEscapeSignature = VTEscapeSignature::csi(b'y')
    .with_private(b'?')
    .with_params_exact(2)
    .with_intermediate(b'$');
const PRIVATE_FEATURE_REPORT: VTEscapeSignature = VTEscapeSignature::csi(b'y')
    .with_params_exact(2)
    .with_intermediate(b'$');
// Cursor shape query signature
const REQUEST_SETTING_REPORT: VTEscapeSignature = VTEscapeSignature::dcs(b'r')
    .with_params_exact(1)
    .with_intermediate(b'$');

impl TerminalInfo {
    fn process_vt_event<'a>(&mut self, buffer: &mut Vec<u8>, event: VTEvent<'a>) {
        match &event {
            VTEvent::Csi { params, .. } => {
                if CURSOR_POSITION_REPORT.matches(&event) {
                    if let (Some(row), Some(col)) =
                        (params.try_parse::<u16>(0), params.try_parse::<u16>(1))
                    {
                        self.cursor_position = Some((row, col));
                    }
                } else if TERMINAL_SIZE_REPORT.matches(&event) {
                    if let (Some(rows), Some(cols)) =
                        (params.try_parse::<u16>(0), params.try_parse::<u16>(1))
                    {
                        self.terminal_size = Some((rows, cols));
                    }
                } else if matches!(
                    event,
                    VTEvent::Csi {
                        private: Some(b'?'),
                        final_byte: b'c',
                        ..
                    }
                ) {
                    // DA1 (Device Attributes Primary)
                    for param in params {
                        if let Ok(param_str) = std::str::from_utf8(param) {
                            if let Ok(attr) = param_str.parse::<u8>() {
                                if let Ok(da1) = vt::DA1::try_from(attr) {
                                    self.device_attributes.push(da1);
                                }
                            }
                        }
                    }
                } else if matches!(
                    event,
                    VTEvent::Csi {
                        private: Some(b'>'),
                        final_byte: b'c',
                        ..
                    }
                ) {
                    // TODO
                } else if FEATURE_REPORT.matches(&event) || PRIVATE_FEATURE_REPORT.matches(&event) {
                    if let Some(feature) = params.try_parse::<u16>(0) {
                        if let Ok(feature) = FeatureReport::try_from(feature) {
                            // terminal didn't recognize
                            if params.try_parse::<u16>(1) == Some(0) {
                                return;
                            }
                            // set or permanently set
                            let v = params.try_parse::<u16>(1) == Some(1)
                                || params.try_parse::<u16>(1) == Some(3);
                            match feature {
                                FeatureReport::AltScreenActive => self.alt_screen_active = Some(v),
                                FeatureReport::BracketedPasteMode => {
                                    self.bracketed_paste_mode = Some(v)
                                }
                                FeatureReport::MouseX10Mode => self.mouse_x10_mode = Some(v),
                                FeatureReport::MouseNormalMode => self.mouse_normal_mode = Some(v),
                                FeatureReport::MouseRXVTMode => self.mouse_rxvt_mode = Some(v),
                                FeatureReport::MouseVT200DragMode => {
                                    self.mouse_vt200_drag_mode = Some(v)
                                }
                                FeatureReport::MouseAnyEventMode => {
                                    self.mouse_any_event_mode = Some(v)
                                }
                                FeatureReport::MouseSGRMode => self.mouse_sgr_mode = Some(v),
                                FeatureReport::FocusReportingMode => {
                                    self.focus_reporting_mode = Some(v)
                                }
                                FeatureReport::ApplicationCursorKeysMode => {
                                    self.application_cursor_keys_mode = Some(v)
                                }
                                FeatureReport::AutoWrapMode => self.auto_wrap_mode = Some(v),
                                FeatureReport::AnsiInsertMode => self.insert_mode = Some(v),
                                FeatureReport::LinefeedNewlineMode => {
                                    self.linefeed_newline_mode = Some(v)
                                }
                                FeatureReport::CursorBlinking => self.cursor_blinking = Some(v),
                                FeatureReport::CursorVisible => self.cursor_visible = Some(v),
                            }
                        } else {
                            info!("Unknown feature: {:?}", feature);
                        }
                    } else {
                        info!("Unknown feature: {:?}", params.get(0));
                    }
                } else {
                    info!("Unknown CSI sequence: {:?}", event);
                }
            }
            VTEvent::OscData(data) | VTEvent::OscEnd { data, .. } => {
                buffer.extend_from_slice(data);

                if matches!(event, VTEvent::OscEnd { .. }) {
                    let data = std::mem::take(buffer);
                    if data.starts_with(b"10;") {
                        // Foreground color
                        let foreground_color = String::from_utf8_lossy(&data[3..]).to_string();
                        info!("Foreground color: {:?}", foreground_color);
                        self.foreground_color = Some(foreground_color);
                    } else if data.starts_with(b"11;") {
                        // Background color
                        let background_color = String::from_utf8_lossy(&data[3..]).to_string();
                        info!("Background color: {:?}", background_color);
                        self.background_color = Some(background_color);
                    } else {
                        let data = String::from_utf8_lossy(&data);
                        info!("Unknown OSC sequence: {:?}", &data[..data.len().min(10)]);
                    }
                }
            }
            VTEvent::DcsStart { params, .. } => {
                if REQUEST_SETTING_REPORT.matches(&event) {
                    if params.try_parse::<u8>(0) == Some(1) {
                        // valid request, data in DcsData/DcsEnd
                    }
                }
            }
            VTEvent::DcsData(data) => {
                buffer.extend_from_slice(data);
            }
            VTEvent::DcsEnd(data) => {
                buffer.extend_from_slice(data);
                let buffer = std::mem::take(buffer);
                match buffer.as_slice() {
                    b"1 q" => self.cursor_shape = Some(CursorShape::BlinkingBlock),
                    b"2 q" => self.cursor_shape = Some(CursorShape::SteadyBlock),
                    b"3 q" => self.cursor_shape = Some(CursorShape::BlinkingUnderline),
                    b"4 q" => self.cursor_shape = Some(CursorShape::SteadyUnderline),
                    b"5 q" => self.cursor_shape = Some(CursorShape::BlinkingBar),
                    b"6 q" => self.cursor_shape = Some(CursorShape::SteadyBar),
                    _ => info!("Unknown DEQRSS response: {:?}", buffer.as_slice()),
                }
            }
            _ => {}
        }
    }
}

fn write_escape(writer: &mut impl std::io::Write, escape: &[u8]) -> std::io::Result<()> {
    debug!(
        "writing escape: {s:?} ({hex})",
        s = String::from_utf8_lossy(escape),
        hex = hex::encode(escape)
    );
    writer.write_all(&[13])?; // CR
    writer.write_all(escape)?;
    writer.write_all(&[13])?; // CR
    writer.flush()?;
    Ok(())
}

fn write_escapes(writer: &mut impl std::io::Write) -> std::io::Result<()> {
    write_escape(writer, &report_cursor_position())?;
    write_escape(writer, &report_terminal_iterm2_version())?;
    write_escape(writer, &report_terminal_xt_get_cap(TerminalCapability::TN))?;
    write_escape(writer, &report_default_foreground())?;
    write_escape(writer, &report_default_background())?;
    write_escape(writer, &report_terminal_device_attributes())?;
    write_escape(writer, &report_terminal_device_attributes2())?;
    write_escape(writer, &report_terminal_device_attributes3())?;
    write_escape(writer, &report_terminal_extended_device_attributes())?;

    write_escape(writer, &report_text_attributes())?;
    write_escape(writer, &report_scrolling_top_bottom())?;
    write_escape(writer, &report_scrolling_left_right())?;

    write_escape(writer, &report_feature(FeatureReport::AltScreenActive))?;
    write_escape(writer, &report_feature(FeatureReport::BracketedPasteMode))?;
    write_escape(writer, &report_feature(FeatureReport::MouseX10Mode))?;
    write_escape(writer, &report_feature(FeatureReport::MouseNormalMode))?;
    write_escape(writer, &report_feature(FeatureReport::MouseRXVTMode))?;
    write_escape(writer, &report_feature(FeatureReport::MouseVT200DragMode))?;
    write_escape(writer, &report_feature(FeatureReport::MouseAnyEventMode))?;
    write_escape(writer, &report_feature(FeatureReport::MouseSGRMode))?;
    write_escape(writer, &report_feature(FeatureReport::FocusReportingMode))?;
    write_escape(
        writer,
        &report_feature(FeatureReport::ApplicationCursorKeysMode),
    )?;
    write_escape(writer, &report_feature(FeatureReport::AutoWrapMode))?;
    write_escape(writer, &report_feature(FeatureReport::AnsiInsertMode))?;
    write_escape(writer, &report_feature(FeatureReport::LinefeedNewlineMode))?;

    // Query cursor state features
    write_escape(writer, &report_feature(FeatureReport::CursorBlinking))?;
    write_escape(writer, &report_feature(FeatureReport::CursorVisible))?;
    write_escape(writer, &report_cursor_shape())?;

    write_escape(writer, &report_terminal_size())?;
    write_escape(writer, &report_cursor_position())?;

    write_escape(writer, &clear_line())?;
    Ok(())
}

pub fn request_terminal_info(
    writer: &mut impl std::io::Write,
    reader: &mut impl std::io::Read,
) -> std::io::Result<TerminalInfo> {
    // Request terminal information
    write_escapes(writer)?;
    let mut terminal_info = TerminalInfo::default();

    // Read and process responses
    let mut vt100 = VTPushParser::new();
    let mut buffer = [0; 1024];
    let mut got_cursor = 0;
    let mut osc_buffer = Vec::new();
    loop {
        if got_cursor == 2 {
            break;
        }
        match reader.read(&mut buffer) {
            Ok(0) => break, // EOF
            Ok(n) => {
                let data = &buffer[..n];
                debug!("data: {}\r\n", hex::encode(data));
                vt100.feed_with(data, &mut |event| {
                    if got_cursor == 2 {
                        info!("Ignoring event: {:?}", event);
                        return;
                    }
                    debug!("event: {:?}", event);

                    // Count cursor position reports
                    if CURSOR_POSITION_REPORT.matches(&event) {
                        got_cursor += 1;
                    }

                    terminal_info.process_vt_event(&mut osc_buffer, event);
                });
            }
            Err(e) => return Err(e),
        }
    }

    info!("terminal_info: {:?}", terminal_info);
    Ok(terminal_info)
}
