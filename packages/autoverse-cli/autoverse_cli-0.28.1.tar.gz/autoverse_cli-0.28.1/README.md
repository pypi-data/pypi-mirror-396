# Autoverse CLI

The new implementation of the Autoverse CLI

## Installation

```bash
pip install autoverse-cli
```

## Shell Completion

To enable tab completion for the `avrs` command, run:

```bash
avrs --install-completion
```

Then reload your shell:

```bash
source ~/.bashrc  # or ~/.zshrc, ~/.config/fish/config.fish, etc.
```

For full details, see [SHELL_COMPLETION.md](SHELL_COMPLETION.md).

### Supported Shells

- Bash
- Zsh
- Fish
- Tcsh

### Quick Usage Examples

```bash
# List all available commands
avrs <TAB>

# Complete subcommand arguments
avrs launcher <TAB>
avrs restart <TAB>
```