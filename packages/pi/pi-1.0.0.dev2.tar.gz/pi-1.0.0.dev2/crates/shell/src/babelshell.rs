use std::path::{Path, PathBuf};

macro_rules! shell {
    ($($variant:ident => $name:literal),* $(,)?) => {
        /// Known shells
        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        pub enum Shell {
            $($variant,)*
        }

        impl Shell {
            pub fn shell_name(&self) -> &str {
                match self {
                    $(Shell::$variant => $name,)*
                }
            }

            pub fn iter() -> impl Iterator<Item = Shell> {
                [$(Shell::$variant,)*].into_iter()
            }
        }

        impl TryFrom<&Path> for Shell {
            type Error = ();

            fn try_from(value: &Path) -> Result<Self, Self::Error> {
                let shell_name = value.file_name().expect(&format!("{value:?} is not a file path")).to_string_lossy();
                // Remove leading '-' (login shells) and trailing ".exe" (Windows executables)
                let no_prefix = shell_name.strip_prefix('-').unwrap_or(&shell_name);
                let clean_name = no_prefix.strip_suffix(".exe").unwrap_or(no_prefix);

                match clean_name {
                    $($name => Ok(Shell::$variant),)*
                    _ => Err(()),
                }
            }
        }

        impl TryFrom<PathBuf> for Shell {
            type Error = ();

            fn try_from(value: PathBuf) -> Result<Self, Self::Error> {
                Shell::try_from(value.as_path())
            }
        }

        impl TryFrom<&PathBuf> for Shell {
            type Error = ();

            fn try_from(value: &PathBuf) -> Result<Self, Self::Error> {
                Shell::try_from(value.as_path())
            }
        }

        impl TryFrom<&str> for Shell {
            type Error = ();

            fn try_from(value: &str) -> Result<Self, Self::Error> {
                Shell::try_from(PathBuf::from(value))
            }
        }

        impl TryFrom<String> for Shell {
            type Error = ();

            fn try_from(value: String) -> Result<Self, Self::Error> {
                Shell::try_from(PathBuf::from(value))
            }
        }
    };
}

shell!(
    Bash => "bash",
    Zsh => "zsh",
    Fish => "fish",
    Ksh => "ksh",
    Mksh => "mksh",
    Oksh => "oksh",
    Pdksh => "pdksh",
    Dash => "dash",
    Ash => "ash",
    Tcsh => "tcsh",
    Csh => "csh",
    Xonsh => "xonsh",
    Elvish => "elvish",
    Nushell => "nushell.nu",
    Ion => "ion",
    Ysh => "ysh",
    Osh => "osh",
    Yash => "yash",
    Rc => "rc",
    Es => "es",
    Sh => "sh",
);

static BASHRC: &str = concat!(
    "if [ -e ~/.bashrc ]; then source ~/.bashrc; fi\n",
    include_str!("scripts/bash-preexec.sh"),
    "\n",
    include_str!("scripts/bash-preexec-mod.sh"),
    "\n",
    include_str!("scripts/bashrc.bash"),
);

static FISHRC: &str = include_str!("scripts/fishrc.fish");
static ZSHRC: &str = include_str!("scripts/zshrc.zsh");

impl Shell {
    /// Get shell-specific env and/or arguments for no-history mode
    pub fn scratch_mode(
        &self,
    ) -> (
        &'static [&'static str],
        &'static [(&'static str, &'static str)],
    ) {
        match self {
            Shell::Bash => (&[], &[("HISTFILE", "/dev/null")]),
            Shell::Zsh => (&[], &[("HISTFILE", "/dev/null"), ("SAVEHIST", "0")]),
            Shell::Fish => (&["--private"], &[]),
            Shell::Ksh | Shell::Mksh | Shell::Oksh | Shell::Pdksh => {
                (&[], &[("HISTFILE", "/dev/null")])
            }
            Shell::Dash | Shell::Ash | Shell::Sh => (&[], &[]),
            Shell::Tcsh => (&[], &[("history", "0")]),
            Shell::Csh => (&[], &[("history", "0")]),
            Shell::Xonsh => (&[], &[("XONSH_HISTORY_SIZE", "0")]),
            Shell::Elvish => (&[], &[]),
            Shell::Nushell => (&[], &[]),
            Shell::Ion => (&[], &[("HISTFILE", "/dev/null")]),
            Shell::Ysh | Shell::Osh => (&[], &[("HISTFILE", "/dev/null")]),
            Shell::Yash => (&[], &[("HISTFILE", "/dev/null")]),
            Shell::Rc | Shell::Es => (&[], &[]),
        }
    }

    pub fn interactive_mode(
        &self,
    ) -> (
        &'static [&'static str],
        &'static [(&'static str, &'static str)],
    ) {
        // All supported shells use the same flag for interactive
        // mode.  In case this stops being true, add a match here.
        (&["-i"], &[])
    }

    pub fn rc_script(&self) -> Option<&'static str> {
        match self {
            Shell::Bash => Some(BASHRC),
            Shell::Zsh => Some(ZSHRC),
            Shell::Fish => Some(FISHRC),
            _ => None,
        }
    }

    pub fn insert_rc_args(&self, args: &[&str], rcfile: &Path) -> Vec<String> {
        let script_str = rcfile.to_string_lossy();
        let args_vec = || args.iter().map(|a| a.to_string()).collect();
        let prepend_args = |rc_args: &[&str]| {
            rc_args
                .iter()
                .map(|s| s.to_string())
                .chain(args.iter().map(|a| a.to_string()))
                .collect()
        };
        let append_args =
            |rc_args: Vec<String>| args.iter().map(|a| a.to_string()).chain(rc_args).collect();

        match self {
            // GNU Bash really wants long options to be _first_
            Shell::Bash => prepend_args(&["--rcfile", &script_str]),

            // zsh: no --rcfile equivalent
            // we do an exec that does some ZDOTDIR magic
            // note: -c 'script' must be last to take into account preceding options
            Shell::Zsh => append_args(vec!["-c".to_string(), format!("source {}", script_str)]),

            // fish: --init-command needs a *command string*, so we source the file.
            // Use fish's own string escaper to avoid path/space issues:
            //   fish --init-command "source (string escape --style=script -- /path/to/file)"
            Shell::Fish => prepend_args(&[
                "--init-command",
                &format!("source (string escape --style=script -- {})", script_str),
            ]),

            // xonsh: supports explicit rc file
            Shell::Xonsh => prepend_args(&["--rc", &script_str]),

            // elvish: alternate rc file
            Shell::Elvish => prepend_args(&["-rc", &script_str]),

            // nushell: prefer one-off `source` via --commands instead of replacing the whole config with --config
            // Single-quote and escape single quotes for safety.
            Shell::Nushell => {
                let quoted = script_str.replace('\'', "''");
                prepend_args(&["--commands", &format!("source '{}'", quoted)])
            }

            // Oil/Ysh/Osh: rcfile supported
            Shell::Ysh | Shell::Osh => prepend_args(&["--rcfile", &script_str]),

            // Yash: rcfile supported
            Shell::Yash => prepend_args(&["--rcfile", &script_str]),

            // Shells that don't support rc file injection or rely on ENV
            Shell::Ksh
            | Shell::Mksh
            | Shell::Oksh
            | Shell::Pdksh
            | Shell::Dash
            | Shell::Ash
            | Shell::Tcsh
            | Shell::Csh
            | Shell::Ion
            | Shell::Rc
            | Shell::Es
            | Shell::Sh => args_vec(),
        }
    }
}
