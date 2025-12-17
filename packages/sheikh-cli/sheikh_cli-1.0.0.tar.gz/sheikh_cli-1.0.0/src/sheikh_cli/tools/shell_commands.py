"""
Shell Commands Tool Plugin
Handles safe shell command execution with sandboxing and security checks.
"""

import subprocess
import shlex
import signal
import time
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

class ShellCommands:
    """Safe shell command execution with security controls"""
    
    def __init__(self, max_execution_time: int = 30):
        self.max_execution_time = max_execution_time
        
        # Security whitelist of allowed commands
        self.allowed_commands = {
            'ls', 'cat', 'grep', 'find', 'tree', 'head', 'tail', 'wc', 'sort', 'uniq',
            'git', 'python', 'python3', 'node', 'npm', 'pip', 'pip3', 'pipx',
            'curl', 'wget', 'tree', 'file', 'stat', 'du', 'df', 'free', 'ps',
            'pwd', 'cd', 'mkdir', 'touch', 'echo', 'date', 'whoami', 'id'
        }
        
        # Blocked commands for security
        self.blocked_commands = {
            'rm', 'sudo', 'su', 'passwd', 'chmod', 'chown', 'mkfs', 'dd',
            'fdisk', 'parted', 'mount', 'umount', 'systemctl', 'service'
        }
        
        # Commands that should be executed in sandbox
        self.sandbox_commands = {'git', 'python', 'python3', 'node', 'npm', 'pip', 'pip3'}
    
    def _validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command for security"""
        # Check if command starts with blocked commands
        parts = shlex.split(command)
        if not parts:
            return False, "Empty command"
        
        base_command = parts[0]
        
        # Check blocked commands
        if base_command in self.blocked_commands:
            return False, f"Blocked command: {base_command}"
        
        # Check if command is whitelisted (for safety, be restrictive)
        if base_command not in self.allowed_commands:
            # Allow some common development commands
            common_dev_commands = {'cargo', 'rustc', 'go', 'gcc', 'g++', 'make', 'cmake'}
            if base_command not in common_dev_commands:
                return False, f"Command not whitelisted: {base_command}"
        
        return True, "Command is safe"
    
    def run_command(self, command: str, working_dir: str = None, timeout: int = None) -> str:
        """Execute shell command safely"""
        if timeout is None:
            timeout = self.max_execution_time
        
        # Validate command
        is_valid, validation_msg = self._validate_command(command)
        if not is_valid:
            return f"❌ Security violation: {validation_msg}"
        
        try:
            # Prepare command execution
            if working_dir:
                working_dir = Path(working_dir)
                if not working_dir.exists():
                    return f"❌ Working directory not found: {working_dir}"
            
            # Execute command with timeout
            start_time = time.time()
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                preexec_fn=lambda: signal.alarm(timeout) if hasattr(signal, 'alarm') else None
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            # Format output
            result_parts = []
            
            if stdout.strip():
                result_parts.append(f"📤 STDOUT:\n```\n{stdout.strip()}\n```")
            
            if stderr.strip():
                result_parts.append(f"⚠️  STDERR:\n```\n{stderr.strip()}\n```")
            
            if not result_parts:
                result_parts.append("✅ Command executed successfully (no output)")
            
            result_parts.append(f"⏱️  Execution time: {execution_time:.2f}s")
            result_parts.append(f"🔄 Exit code: {process.returncode}")
            
            return "\n\n".join(result_parts)
            
        except subprocess.TimeoutExpired:
            return f"⏰ Command timed out after {timeout} seconds"
        except subprocess.CalledProcessError as e:
            return f"❌ Command failed with exit code {e.returncode}\n\n📤 Output:\n```\n{e.stdout}\n```\n⚠️ Error:\n```\n{e.stderr}\n```"
        except Exception as e:
            return f"❌ Error executing command: {str(e)}"
    
    def run_python_script(self, script_content: str, script_args: List[str] = None) -> str:
        """Execute Python script safely"""
        if script_args is None:
            script_args = []
        
        # Create temporary script file
        script_file = Path.home() / "coding-agent" / "temp_script.py"
        try:
            script_file.parent.mkdir(parents=True, exist_ok=True)
            script_file.write_text(script_content)
            
            # Build command
            command_parts = ["python", str(script_file)] + script_args
            command = " ".join(shlex.quote(part) for part in command_parts)
            
            result = self.run_command(command)
            
            # Clean up
            if script_file.exists():
                script_file.unlink()
            
            return result
            
        except Exception as e:
            return f"❌ Error running Python script: {str(e)}"
    
    def run_nodejs_script(self, script_content: str, script_args: List[str] = None) -> str:
        """Execute Node.js script safely"""
        if script_args is None:
            script_args = []
        
        # Create temporary script file
        script_file = Path.home() / "coding-agent" / "temp_script.js"
        try:
            script_file.parent.mkdir(parents=True, exist_ok=True)
            script_file.write_text(script_content)
            
            # Build command
            command_parts = ["node", str(script_file)] + script_args
            command = " ".join(shlex.quote(part) for part in command_parts)
            
            result = self.run_command(command)
            
            # Clean up
            if script_file.exists():
                script_file.unlink()
            
            return result
            
        except Exception as e:
            return f"❌ Error running Node.js script: {str(e)}"
    
    def check_command_available(self, command: str) -> str:
        """Check if a command is available in the system"""
        try:
            result = self.run_command(f"which {command}")
            if result.startswith("❌") or "not found" in result:
                return f"❌ Command '{command}' is not available"
            else:
                return f"✅ Command '{command}' is available at: {result.strip()}"
        except Exception as e:
            return f"❌ Error checking command availability: {str(e)}"
    
    def get_system_info(self) -> str:
        """Get basic system information"""
        commands = [
            ("uname -a", "System Information"),
            ("python --version", "Python Version"),
            ("node --version", "Node.js Version"),
            ("git --version", "Git Version"),
            ("free -h", "Memory Usage"),
            ("df -h", "Disk Usage")
        ]
        
        results = []
        for cmd, description in commands:
            result = self.run_command(cmd)
            if not result.startswith("❌"):
                results.append(f"📊 {description}:\n```\n{result.split('📤')[0].split('⏱️')[0].strip()}\n```")
        
        return "\n\n".join(results)
