#!/usr/bin/env zsh

[ "${_PI_SHELL_DEBUG:-0}" = "1" ] && echo "Initializing zsh: $-"

# ZSH requires a ZDOTDIR to be set to use the rc file
if [[ -o interactive ]] && [ -z "${_PI_ZSH_REEXEC-}" ]; then
    # Save original HISTFILE before changing ZDOTDIR
    if [ -n "$HISTFILE" ]; then
        export _PI_ORIG_HISTFILE="$HISTFILE"
    else
        # If HISTFILE wasn't set, save the default zsh would use
        export _PI_ORIG_HISTFILE="${ZDOTDIR:-$HOME}/.zsh_history"
    fi

    # Create temporary directory with error handling
    if ! export _PI_ZDOTDIR=$(mktemp -d); then
        echo "Failed to create temporary directory" >&2
        exit 1
    fi

    export ZDOTDIR="$_PI_ZDOTDIR"
    export _PI_ZSH_REEXEC=1

    __pi_this="${(%):-%x}"

    # Copy script with error handling
    if ! cp "$__pi_this" "$ZDOTDIR/.zshrc"; then
        echo "Failed to copy script to temporary directory" >&2
        rm -rf "$ZDOTDIR" 2>/dev/null
        if [[ "$__pi_this" == */.pitmprc.* ]]; then
            rm -f "$__pi_this" 2>/dev/null
        fi
        exit 1
    fi

    if [[ "$__pi_this" == */.pitmprc.* ]]; then
        rm -f "$__pi_this" 2>/dev/null
    fi

    # Re-exec interactive
    exec "${_PI_SHELL_EXECUTABLE:-zsh}" -i

elif [[ -o interactive ]]; then
    export HISTFILE="$_PI_ORIG_HISTFILE"
    [ -e ~/.zshrc ] && source ~/.zshrc

    if [ "${_PI_SETUP_SEMANTIC_PROMPT-}" != "" ] && [ "${_PI_SEMANTIC_PROMPT_INTEGRATION_INSTALLED-}" = "" ]; then
        _PI_SEMANTIC_PROMPT_INTEGRATION_INSTALLED=Yes

        __pi_osc133_enablement=(${(s:,:)_PI_SETUP_SEMANTIC_PROMPT})

        __pi_contains() {
            local needle=$1;
            local arrname=$2;
            local arr=${(P)arrname};
            local idx;
            idx=${arr[(ie)$needle]}

            (( idx <= ${#arr} )) && return 0
            return 1
        }

        __pi_osc133_prompt_start() {
            printf "\033]133;A\007"
        }

        __pi_osc133_prompt_end() {
            printf "\033]133;B\007"
        }

        __pi_osc133_command_start() {
            printf "\033]133;C\007"
        }

        __pi_osc133_command_end() {
            printf "\033]133;D;%s\007" "$1"
        }

        if __pi_contains "CommandStart" __pi_osc133_enablement; then
            __pi_emit_osc133_command_start() {
                __pi_osc133_command_start
            }
        else
            __pi_emit_osc133_command_start() { }
        fi

        if __pi_contains "CommandEnd" __pi_osc133_enablement; then
            __pi_emit_osc133_command_end() {
                __pi_osc133_command_end "$1"
            }
        else
            __pi_emit_osc133_command_end() { }
        fi

        __pi_orig_ps1="$PS1"
        __pi_preexec_called=""

        if __pi_contains "PromptStart" __pi_osc133_enablement && __pi_contains "PromptEnd" __pi_osc133_enablement; then
            __pi_zsh_prompt() {
                local prompt_start="$(__pi_osc133_prompt_start)"

                if [[ $PS1 != *"${prompt_start}"* ]]; then
                    __pi_orig_ps1="$PS1"
                    PS1="%{${prompt_start}%}$PS1%{$(__pi_osc133_prompt_end)%}"
                fi
            }
        elif __pi_contains "PromptStart" __pi_osc133_enablement; then
            __pi_zsh_prompt() {
                local prompt_start="$(__pi_osc133_prompt_start)"

                if [[ $PS1 != *"${prompt_start}"* ]]; then
                    __pi_orig_ps1="$PS1"
                    PS1="%{${prompt_start}%}$PS1"
                fi
            }
        elif __pi_contains "PromptEnd" __pi_osc133_enablement; then
            __pi_zsh_prompt() {
                local prompt_end="$(__pi_osc133_prompt_end)"

                if [[ $PS1 != *"${prompt_end}"* ]]; then
                    __pi_orig_ps1="$PS1"
                    PS1="$PS1%{${prompt_end}%}"
                fi
            }
        else
            __pi_zsh_prompt() { }
        fi


        __pi_precmd() {
            local laststatus="$?"
            if [ -n "${__pi_preexec_called-}" ]; then
                __pi_preexec_called=""
                __pi_emit_osc133_command_end "$laststatus"
            fi
            __pi_zsh_prompt
        }

        __pi_preexec() {
            # Restore the undecorated PS1 in case the command needs to
            # operate on it.
            PS1="$__pi_orig_ps1"
            __pi_preexec_called="1"
            __pi_emit_osc133_command_start
        }

        [[ -z ${precmd_functions-} ]] && precmd_functions=()
        precmd_functions=($precmd_functions __pi_precmd)

        [[ -z ${preexec_functions-} ]] && preexec_functions=()
        preexec_functions=($preexec_functions __pi_preexec)
    fi

    # Set up aliases
    alias python="$PI_EXE python"
    alias python3="$PI_EXE python3"
    alias py="$PI_EXE python"

    # Cleanup
    if [ -d "$_PI_ZDOTDIR" ]; then
        rm -rf "$_PI_ZDOTDIR" 2>/dev/null || true
    fi
fi
