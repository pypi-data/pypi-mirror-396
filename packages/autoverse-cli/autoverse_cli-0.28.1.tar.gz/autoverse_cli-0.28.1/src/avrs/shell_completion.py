import os
import sys
import subprocess
from pathlib import Path

def get_shell_name():
    """Detect the current shell from SHELL environment variable or parent process."""
    shell = os.environ.get('SHELL', '')
    if shell:
        return os.path.basename(shell)
    
    # Fallback: try to get parent shell
    try:
        parent_pid = os.getppid()
        with open(f'/proc/{parent_pid}/comm', 'r') as f:
            return f.read().strip()
    except:
        return 'bash'

def get_shell_config_file():
    """Get the config file path for the detected shell."""
    shell = get_shell_name()
    home = str(Path.home())
    
    if 'zsh' in shell:
        return os.path.join(home, '.zshrc')
    elif 'fish' in shell:
        return os.path.join(home, '.config/fish/config.fish')
    elif 'tcsh' in shell:
        return os.path.join(home, '.tcshrc')
    else:  # bash and others
        return os.path.join(home, '.bashrc')

def get_completion_command():
    """Get the shell-specific completion registration command."""
    shell = get_shell_name()
    
    # Try to use register-python-argcomplete if available, fall back to register-python-argcomplete3
    # This makes it compatible with both pip-installed and system-package versions
    register_cmd = "register-python-argcomplete"
    
    if 'zsh' in shell:
        return f'eval "$({register_cmd} --shell zsh avrs 2>/dev/null || {register_cmd}3 --shell zsh avrs)"'
    elif 'fish' in shell:
        return f'{register_cmd} --shell fish avrs 2>/dev/null | source || {register_cmd}3 --shell fish avrs | source'
    elif 'tcsh' in shell:
        return f'eval "$({register_cmd} --shell tcsh avrs 2>/dev/null || {register_cmd}3 --shell tcsh avrs)"'
    else:  # bash
        return f'eval "$({register_cmd} avrs 2>/dev/null || {register_cmd}3 avrs)"'

def install_completion():
    """Install shell completion for the avrs CLI."""
    shell = get_shell_name()
    config_file = get_shell_config_file()
    completion_command = get_completion_command()
    
    print(f"Installing shell completion for {shell}...")
    
    # Check if completion already installed
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            if 'register-python-argcomplete' in content and 'avrs' in content:
                print(f"✓ Completion already installed in {config_file}")
                return True
    
    # Ensure config file exists
    Path(config_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Append completion command
    try:
        with open(config_file, 'a') as f:
            f.write('\n\n# avrs CLI completion\n')
            f.write(completion_command + '\n')
        print(f"✓ Completion installed successfully!")
        print(f"✓ Added to {config_file}")
        print(f"\nTo activate completion in current shell, run:")
        print(f"  source {config_file}")
        return True
    except Exception as e:
        print(f"✗ Error installing completion: {e}")
        print(f"\nManually add this line to {config_file}:")
        print(f"  {completion_command}")
        return False

def uninstall_completion():
    """Remove shell completion for the avrs CLI."""
    shell = get_shell_name()
    config_file = get_shell_config_file()
    
    print(f"Uninstalling shell completion from {config_file}...")
    
    if not os.path.exists(config_file):
        print("Config file not found.")
        return False
    
    try:
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        # Filter out avrs completion lines
        new_lines = [
            line for line in lines 
            if 'register-python-argcomplete' not in line or 'avrs' not in line
        ]
        
        # Also remove the comment line if it's there
        filtered_lines = []
        for i, line in enumerate(new_lines):
            if line.strip() == '# avrs CLI completion':
                continue
            filtered_lines.append(line)
        
        with open(config_file, 'w') as f:
            f.writelines(filtered_lines)
        
        print(f"✓ Completion uninstalled successfully!")
        return True
    except Exception as e:
        print(f"✗ Error uninstalling completion: {e}")
        return False
