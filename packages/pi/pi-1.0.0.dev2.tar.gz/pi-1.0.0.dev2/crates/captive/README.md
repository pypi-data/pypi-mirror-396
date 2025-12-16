# pi-captive

A process capture and management tool that allows you to start, manage, and interact with processes in a controlled environment. `pi-captive` runs processes in a virtual terminal and provides an interface to manage their lifecycle, send input, and view output.

## Overview

`pi-captive` is designed to run interactive processes in a controlled way, allowing you to:
- Start processes and capture their output
- Send text input or key sequences to running processes  
- View process logs and screen output
- Manage multiple processes with tags
- Kill and clean up processes

## Installation

Build the project from the workspace root:

```bash
cargo build --bin pi-captive
```

The binary will be available at `target/debug/pi-captive` (or `target/release/pi-captive` for release builds).

## Quick Start

1. **Start a process**: Run a shell and capture it
   ```bash
   pi-captive run /bin/sh
   ```

2. **List running processes**:
   ```bash
   pi-captive ls
   ```

3. **Send input to the process**:
   ```bash
   pi-captive resume --tag sh --text "echo hello\n"
   ```

4. **View process logs**:
   ```bash
   pi-captive log --tag sh
   ```

5. **Clean up**:
   ```bash
   pi-captive reset --force
   ```

## Commands

### `run` - Start a new process

Start a new process and run until it requires input.

```bash
pi-captive run [OPTIONS] <COMMAND> [ARGS...]
```

**Options:**
- `--kill`: Kill existing process with the same tag before starting
- `--tag <TAG>`: Assign a custom tag to the process (defaults to command name)
- `--timeout <TIMEOUT>`: Set timeout in seconds (default: 60)

**Examples:**
```bash
# Start a shell
pi-captive run /bin/sh

# Start with a custom tag
pi-captive run --tag my-shell /bin/bash

# Kill existing process with same tag and start new one
pi-captive run --kill /bin/sh

# Start with custom timeout
pi-captive run --timeout 120 /bin/sh
```

### `ls` - List running processes

List all running processes in the current namespace.

```bash
pi-captive ls
```

Shows processes with their PID, tag, and status (active/inactive).

### `resume` - Send input to a process

Resume a process by sending text input or key sequences.

```bash
pi-captive resume [OPTIONS]
```

**Options:**
- `--tag <TAG>`: Target process by tag
- `--pid <PID>`: Target process by PID  
- `--text <TEXT>`: Send text input (supports escape sequences like `\n`)
- `--key <KEY>`: Send key sequences (can be used multiple times)

**Examples:**
```bash
# Send a command to a shell
pi-captive resume --tag sh --text "ls -la\n"

# Send just text without newline
pi-captive resume --tag sh --text "echo hello"

# Send specific keys
pi-captive resume --tag sh --key "Enter"
pi-captive resume --tag sh --key "Ctrl+C"
```

### `log` - View process logs

View the output logs of a process.

```bash
pi-captive log [OPTIONS]
```

**Options:**
- `--tag <TAG>`: Target process by tag
- `--pid <PID>`: Target process by PID
- `--head`: Show first 25 lines
- `--tail`: Show last 25 lines (default)
- `--all`: Show entire log

**Examples:**
```bash
# View recent output (last 25 lines)
pi-captive log --tag sh

# View all output
pi-captive log --tag sh --all

# View first 25 lines
pi-captive log --tag sh --head
```

### `kill` - Kill processes

Kill one or more processes.

```bash
pi-captive kill [OPTIONS]
```

**Options:**
- `--tag <TAG>`: Kill process by tag
- `--pid <PID>`: Kill process by PID
- `--all`: Kill all processes

**Examples:**
```bash
# Kill specific process
pi-captive kill --tag sh

# Kill by PID
pi-captive kill --pid 1234

# Kill all processes
pi-captive kill --all
```

### `remove` - Clean up defunct processes

Remove logs and tags for processes that are no longer running.

```bash
pi-captive remove [OPTIONS]
```

**Options:**
- `--tag <TAG>`: Remove by tag
- `--pid <PID>`: Remove by PID
- `--all`: Remove all defunct processes

**Examples:**
```bash
# Remove defunct process files
pi-captive remove --tag sh

# Remove all defunct processes
pi-captive remove --all
```

### `dump-screen` - Capture screen content

Capture the current screen content of a process.

```bash
pi-captive dump-screen [OPTIONS]
```

**Options:**
- `--tag <TAG>`: Target process by tag
- `--pid <PID>`: Target process by PID

### `timeout` - Set process timeout

Set or modify the timeout for a process.

```bash
pi-captive timeout [OPTIONS] <TIMEOUT>
```

**Options:**
- `--tag <TAG>`: Target process by tag
- `--pid <PID>`: Target process by PID

### `reset` - Reset environment

Kill all processes and clean up the entire captive environment.

```bash
pi-captive reset [OPTIONS]
```

**Options:**
- `--force`: Skip confirmation prompt

## Process Management

### Tags

Processes can be assigned tags for easy identification and management. If no tag is specified, `pi-captive` derives one from the command name.

- Tags are automatically made unique (e.g., `sh`, `sh-1`, `sh-2`)
- Use `--kill` option to replace an existing tagged process
- Tags create symlinks for quick PID lookup

### Namespaces

`pi-captive` uses namespaces to organize processes and their data. Each namespace has its own:
- Process list
- Log files
- Socket files  
- Tag symlinks

### Process States

- **Active**: Process is running and has an active socket
- **Defunct**: Process has terminated but logs/tags remain

## Examples Walkthrough

Here's a complete example workflow:

```bash
# 1. Start a shell
pi-captive run /bin/sh
# Output: Started captive process with --pid 1234 and --tag sh

# 2. Check what's running
pi-captive ls
# Output: [pi] --pid 1234 --tag sh (active)

# 3. Send a command
pi-captive resume --tag sh --text "echo 'Hello World'\n"

# 4. View the output
pi-captive log --tag sh
# Shows the command execution and output

# 5. Start another shell (will get tag 'sh-1')
pi-captive run /bin/sh
# Output: Started captive process with --pid 5678 and --tag sh-1

# 6. List all processes
pi-captive ls
# Shows both shells

# 7. Kill one process
pi-captive kill --tag sh-1

# 8. Clean up everything
pi-captive reset --force
```

## Error Handling

Common error scenarios:

- **"Tag is already in use"**: Use `--kill` option or choose a different tag
- **"No process found with tag"**: Check running processes with `pi-captive ls`
- **"Socket not found for PID"**: Process may have terminated, use `remove` to clean up
- **"Timeout waiting for response"**: Process may be unresponsive, try killing it

## Files and Directories

`pi-captive` creates several directories to manage process data:

- **Run directory**: Contains socket files for active processes
- **Cache directory**: Contains log files and process metadata
- **Tag symlinks**: Quick references from tag names to PIDs

These are automatically managed and cleaned up by the `reset` command.

## Integration

`pi-captive` is designed to be used programmatically and can be integrated into larger automation systems. The consistent command structure and predictable output make it suitable for scripting and testing scenarios.

