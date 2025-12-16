#!/bin/bash
# SPDX-License-Identifier: MIT
#
# bash-preexec-mod.sh -- Modification for bash-preexec to ensure precmd
# callbacks are called LAST in the PROMPT_COMMAND chain.
#
# This script should be sourced AFTER bash-preexec.sh to reorder the
# PROMPT_COMMAND so that precmd functions run after all other prompt
# commands instead of before them.
#

# Tell shellcheck what kind of file this is.
# shellcheck shell=bash

# Only proceed if bash-preexec is already loaded
if [[ -z "${bash_preexec_imported:-}" ]]; then
    echo "bash-preexec-mod: bash-preexec.sh must be loaded first" >&2
    return 1
fi

# Avoid duplicate modification
if [[ -n "${bash_preexec_mod_applied:-}" ]]; then
    return 0
fi
bash_preexec_mod_applied="defined"

# Function to reorder PROMPT_COMMAND to put precmd callbacks last
__bp_mod_reorder_prompt_command() {
    local existing_commands=()
    local bp_precmd_cmd=""
    local bp_interactive_cmd=""

    # Handle different bash versions
    if (( BASH_VERSINFO[0] > 5 || (BASH_VERSINFO[0] == 5 && BASH_VERSINFO[1] >= 1) )); then
        # Bash 5.1+: PROMPT_COMMAND is an array
        local i
        for i in "${!PROMPT_COMMAND[@]}"; do
            local cmd="${PROMPT_COMMAND[i]}"
            if [[ "$cmd" == "__bp_precmd_invoke_cmd" ]]; then
                bp_precmd_cmd="$cmd"
            elif [[ "$cmd" == "__bp_interactive_mode" ]]; then
                bp_interactive_cmd="$cmd"
            else
                existing_commands+=("$cmd")
            fi
        done

        # Rebuild PROMPT_COMMAND array with proper order
        PROMPT_COMMAND=()
        # Add existing commands first
        for cmd in "${existing_commands[@]}"; do
            if [[ -n "$cmd" ]]; then
                PROMPT_COMMAND+=("$cmd")
            fi
        done
        # Add precmd invoke
        if [[ -n "$bp_precmd_cmd" ]]; then
            PROMPT_COMMAND+=("$bp_precmd_cmd")
        fi
        # Add interactive mode last
        if [[ -n "$bp_interactive_cmd" ]]; then
            PROMPT_COMMAND+=("$bp_interactive_cmd")
        fi
    else
        # Bash 5.0 and earlier: PROMPT_COMMAND is a string
        local IFS=$'\n'
        local prompt_commands
        read -rd '' -a prompt_commands <<< "${PROMPT_COMMAND//$'\n'/$'\n'}"

        local cmd
        for cmd in "${prompt_commands[@]}"; do
            # Trim whitespace
            cmd="${cmd#"${cmd%%[![:space:]]*}"}"
            cmd="${cmd%"${cmd##*[![:space:]]}"}"

            if [[ "$cmd" == "__bp_precmd_invoke_cmd" ]]; then
                bp_precmd_cmd="$cmd"
            elif [[ "$cmd" == "__bp_interactive_mode" ]]; then
                bp_interactive_cmd="$cmd"
            elif [[ -n "$cmd" ]]; then
                existing_commands+=("$cmd")
            fi
        done

        # Rebuild PROMPT_COMMAND string with proper order
        PROMPT_COMMAND=""
        # Add existing commands first
        for cmd in "${existing_commands[@]}"; do
            if [[ -n "$cmd" ]]; then
                if [[ -n "$PROMPT_COMMAND" ]]; then
                    PROMPT_COMMAND+=$'\n'
                fi
                PROMPT_COMMAND+="$cmd"
            fi
        done
        # Add precmd invoke
        if [[ -n "$bp_precmd_cmd" ]]; then
            if [[ -n "$PROMPT_COMMAND" ]]; then
                PROMPT_COMMAND+=$'\n'
            fi
            PROMPT_COMMAND+="$bp_precmd_cmd"
        fi
        # Add interactive mode last
        if [[ -n "$bp_interactive_cmd" ]]; then
            if [[ -n "$PROMPT_COMMAND" ]]; then
                PROMPT_COMMAND+=$'\n'
            fi
            PROMPT_COMMAND+="$bp_interactive_cmd"
        fi
    fi
}

# Apply the reordering
__bp_mod_reorder_prompt_command

# Inhibit the HISTCONTROL hack.  OSC 133 machinery does not rely
# on command data passed to prexec and this way we avoid messing
# with user settings.
__bp_adjust_histcontrol() {
    :
}
