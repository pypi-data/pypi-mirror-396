#!/usr/bin/env fish

if status --is-interactive;
    if begin; not functions -q -- __pi_osc133_prompt_start; and test -n "$_PI_SETUP_SEMANTIC_PROMPT"; end
        function __pi_debug_log
            test "$_PI_SHELL_DEBUG" = "1"; and echo "$argv[1]"
        end

        set __pi_osc133_enablement (string split , "$_PI_SETUP_SEMANTIC_PROMPT")

        function __pi_osc133_prompt_start
            printf "\033]133;A\007"
        end

        function __pi_osc133_prompt_end
            printf "\033]133;B\007"
        end

        function __pi_osc133_command_start
            printf "\033]133;C\007"
        end

        function __pi_osc133_command_end
            printf "\033]133;D;%s\007" "$argv[1]"
        end

        if contains "CommandStart" $__pi_osc133_enablement;
            __pi_debug_log "Setting up fish OSC133 COMMAND START hook"

            function __pi_preexec_handler --on-event fish_preexec
                __pi_osc133_command_start
            end
        end

        if contains "CommandEnd" $__pi_osc133_enablement;
            __pi_debug_log "Setting up fish OSC133 COMMAND END hook"

            function __pi_postexec_handler --on-event fish_postexec
                __pi_osc133_command_end $status
            end
        end

        if contains "PromptStart" $__pi_osc133_enablement;
            __pi_debug_log "Setting up fish OSC133 PROMPT START hook"

            function __pi_prompt_start --on-event fish_prompt
                __pi_osc133_prompt_start
            end
        end

        if contains "PromptEnd" $__pi_osc133_enablement;
            __pi_debug_log "Setting up fish OSC133 PROMPT END hook"

            functions -c fish_prompt __pi_orig_fish_prompt

            function fish_prompt
                __pi_orig_fish_prompt
                __pi_osc133_prompt_end
            end
        end
    end

    # Set up aliases
    alias python="$PI_EXE python"
    alias python3="$PI_EXE python3"
    alias py="$PI_EXE python"
end

set __pi_this_script (status current-filename)
if string match -q "*/.pitmprc.*" "$__pi_this_script"
    rm -f "$__pi_this_script" 2>/dev/null; or true
end
