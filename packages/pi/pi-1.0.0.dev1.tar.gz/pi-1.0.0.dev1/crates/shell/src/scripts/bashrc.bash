#!/usr/bin/env bash
# shellcheck shell=bash

if [[ "$-" == *i* ]]; then
    # Source user's bashrc
    # shellcheck disable=SC1090
    [ -e ~/.bashrc ] && source ~/.bashrc

    if [ -z "${__pi_shell_integration-}" ] && [ -n "${_PI_SETUP_SEMANTIC_PROMPT-}" ]; then
        [ "${_PI_SHELL_DEBUG:-0}" = "1" ] && echo "Initializing bash with OSC 133 integration"

        __pi_shell_integration="installed"
        IFS=',' read -ra __pi_osc133_enablement <<< "$_PI_SETUP_SEMANTIC_PROMPT"

        __pi_contains() {
            local element match="$1"
            shift
            for element; do
                if [[ "$element" == "$match" ]]; then
                    return 0
                fi
            done
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

        if __pi_contains "CommandStart" "${__pi_osc133_enablement[@]}"; then
            __pi_emit_osc133_command_start() {
                __pi_osc133_command_start
            }
        else
            __pi_emit_osc133_command_start() { :; }
        fi

        if __pi_contains "CommandEnd" "${__pi_osc133_enablement[@]}"; then
            __pi_emit_osc133_command_end() {
                __pi_osc133_command_end "$1"
            }
        else
            __pi_emit_osc133_command_end() { :; }
        fi

        __pi_orig_ps1="$PS1"
        __pi_preexec_called=""

        if __pi_contains "PromptStart" "${__pi_osc133_enablement[@]}" && __pi_contains "PromptEnd" "${__pi_osc133_enablement[@]}"; then
            __pi_bash_prompt() {
                local prompt_start
                prompt_start="$(__pi_osc133_prompt_start)"

                # Inject OSC 133 markers into PS1
                if [[ $PS1 != *"${prompt_start}"* ]]; then
                    PS1="\[${prompt_start}\]${PS1}\[$(__pi_osc133_prompt_end)\]"
                fi
            }
        elif __pi_contains "PromptStart" "${__pi_osc133_enablement[@]}"; then
            __pi_bash_prompt() {
                local prompt_start
                prompt_start="$(__pi_osc133_prompt_start)"

                # Inject OSC 133 markers into PS1
                if [[ $PS1 != *"${prompt_start}"* ]]; then
                    PS1="\[${prompt_start}\]${PS1}"
                fi
            }
        elif __pi_contains "PromptEnd" "${__pi_osc133_enablement[@]}"; then
            __pi_bash_prompt() {
                local prompt_end
                prompt_end="$(__pi_osc133_prompt_end)"

                # Inject OSC 133 markers into PS1
                if [[ $PS1 != *"${prompt_end}"* ]]; then
                    PS1="${PS1}\[${prompt_end}\]"
                fi
            }
        else
            __pi_bash_prompt() { :; }
        fi

        __pi_precmd_hook() {
            local last_exit_code=$?
            if [ -n "${__pi_preexec_called-}" ]; then
                __pi_preexec_called=""
                __pi_emit_osc133_command_end "$last_exit_code"
            fi
            __pi_bash_prompt
            # shellcheck disable=SC2154
            __bp_set_ret_value "$last_exit_code" "$__bp_last_argument_prev_command"
        }

        __pi_preexec_hook() {
            # Restore the undecorated PS1 in case the command needs to
            # operate on it.
            PS1="$__pi_orig_ps1"
            __pi_preexec_called="1"
            __pi_emit_osc133_command_start
        }

        # Add our functions to the bash-preexec arrays
        preexec_functions+=(__pi_preexec_hook)
        precmd_functions+=(__pi_precmd_hook)
    fi

    # Set up aliases
    alias python="$PI_EXE python"
    alias python3="$PI_EXE python3"
    alias py="$PI_EXE python"
fi

if [[ "${BASH_SOURCE[0]}" == */.pitmprc.* ]]; then
    rm -f "${BASH_SOURCE[0]}" 2>/dev/null || true
fi
