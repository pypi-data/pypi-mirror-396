"""
Git Operations Tool Plugin
Handles Git repository operations safely.
"""

import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import shlex

class GitOperations:
    """Git repository operations with safety checks"""
    
    def __init__(self):
        self.allowed_commands = {
            'status', 'diff', 'log', 'show', 'branch', 'checkout', 'add', 'commit',
            'pull', 'push', 'clone', 'init', 'remote', 'fetch', 'merge', 'rebase'
        }
    
    def _run_git_command(self, command: List[str], working_dir: str = None) -> Tuple[bool, str, str]:
        """Run a git command safely"""
        try:
            # Validate git command
            if not command or command[0] != 'git':
                return False, "", "Invalid git command"
            
            git_subcommand = command[1] if len(command) > 1 else ""
            if git_subcommand not in self.allowed_commands:
                return False, "", f"Git command '{git_subcommand}' not allowed"
            
            # Add safety flags
            safe_command = ['git']
            if git_subcommand in ['push', 'force-push']:
                safe_command.append('--dry-run')  # Safety first
            
            # Add the rest of the command
            safe_command.extend(command[1:])
            
            result = subprocess.run(
                safe_command,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=working_dir
            )
            
            return True, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Git command timed out"
        except Exception as e:
            return False, "", f"Error running git command: {str(e)}"
    
    def status(self, working_dir: str = None) -> str:
        """Get git repository status"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        try:
            success, stdout, stderr = self._run_git_command(['git', 'status', '--porcelain'], working_dir)
            
            if not success:
                if "not a git repository" in stderr.lower():
                    return f"❌ Not a git repository: {working_dir}"
                else:
                    return f"❌ Git status failed: {stderr}"
            
            if not stdout.strip():
                return f"✅ Working directory is clean in {working_dir}"
            
            lines = stdout.strip().split('\n')
            modified = []
            added = []
            deleted = []
            untracked = []
            
            for line in lines:
                if line.startswith(' M'):
                    modified.append(line[3:])
                elif line.startswith('A '):
                    added.append(line[2:])
                elif line.startswith('D '):
                    deleted.append(line[2:])
                elif line.startswith('??'):
                    untracked.append(line[2:])
            
            result = f"📊 Git Status for {working_dir}:\n\n"
            
            if modified:
                result += f"📝 Modified files ({len(modified)}):\n"
                for file in modified:
                    result += f"  • {file}\n"
                result += "\n"
            
            if added:
                result += f"➕ Added files ({len(added)}):\n"
                for file in added:
                    result += f"  • {file}\n"
                result += "\n"
            
            if deleted:
                result += f"➖ Deleted files ({len(deleted)}):\n"
                for file in deleted:
                    result += f"  • {file}\n"
                result += "\n"
            
            if untracked:
                result += f"❓ Untracked files ({len(untracked)}):\n"
                for file in untracked:
                    result += f"  • {file}\n"
                result += "\n"
            
            total_changes = len(modified) + len(added) + len(deleted) + len(untracked)
            result += f"📊 Total changes: {total_changes} files"
            
            return result
            
        except Exception as e:
            return f"❌ Error getting git status: {str(e)}"
    
    def diff(self, file_path: str = None, working_dir: str = None) -> str:
        """Show git diff"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        try:
            if file_path:
                success, stdout, stderr = self._run_git_command(['git', 'diff', file_path], working_dir)
            else:
                success, stdout, stderr = self._run_git_command(['git', 'diff'], working_dir)
            
            if not success:
                if "not a git repository" in stderr.lower():
                    return f"❌ Not a git repository: {working_dir}"
                else:
                    return f"❌ Git diff failed: {stderr}"
            
            if not stdout.strip():
                return f"📄 No changes to show in {working_dir}"
            
            return f"📄 Git Diff:\n\n```diff\n{stdout}\n```"
            
        except Exception as e:
            return f"❌ Error getting git diff: {str(e)}"
    
    def log(self, count: int = 10, working_dir: str = None) -> str:
        """Show git commit log"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        try:
            success, stdout, stderr = self._run_git_command(['git', 'log', f'--oneline', f'-{count}'], working_dir)
            
            if not success:
                if "not a git repository" in stderr.lower():
                    return f"❌ Not a git repository: {working_dir}"
                else:
                    return f"❌ Git log failed: {stderr}"
            
            if not stdout.strip():
                return f"📜 No commit history found in {working_dir}"
            
            lines = stdout.strip().split('\n')
            return f"📜 Recent {len(lines)} commits:\n\n" + '\n'.join(lines)
            
        except Exception as e:
            return f"❌ Error getting git log: {str(e)}"
    
    def branch_list(self, working_dir: str = None) -> str:
        """List git branches"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        try:
            success, stdout, stderr = self._run_git_command(['git', 'branch', '-a'], working_dir)
            
            if not success:
                if "not a git repository" in stderr.lower():
                    return f"❌ Not a git repository: {working_dir}"
                else:
                    return f"❌ Git branch list failed: {stderr}"
            
            if not stdout.strip():
                return f"🌿 No branches found in {working_dir}"
            
            lines = stdout.strip().split('\n')
            current_branch = None
            other_branches = []
            
            for line in lines:
                if line.startswith('*'):
                    current_branch = line[2:]  # Remove '* ' prefix
                else:
                    other_branches.append(line[2:] if line.startswith('  ') else line)
            
            result = f"🌿 Git Branches for {working_dir}:\n\n"
            
            if current_branch:
                result += f"🔸 Current branch: {current_branch}\n\n"
            
            if other_branches:
                result += f"📋 All branches:\n"
                for branch in other_branches:
                    result += f"  • {branch}\n"
            else:
                result += "📋 Only current branch exists"
            
            return result
            
        except Exception as e:
            return f"❌ Error listing git branches: {str(e)}"
    
    def add_files(self, files: List[str], working_dir: str = None) -> str:
        """Add files to git staging area"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        if not files:
            return "❌ No files specified to add"
        
        try:
            # Use git add . for safety when no specific files
            if files == ['.']:
                success, stdout, stderr = self._run_git_command(['git', 'add', '.'], working_dir)
            else:
                success, stdout, stderr = self._run_git_command(['git', 'add'] + files, working_dir)
            
            if not success:
                if "not a git repository" in stderr.lower():
                    return f"❌ Not a git repository: {working_dir}"
                else:
                    return f"❌ Git add failed: {stderr}"
            
            return f"✅ Successfully added {len(files)} file(s) to staging area"
            
        except Exception as e:
            return f"❌ Error adding files to git: {str(e)}"
    
    def commit(self, message: str, working_dir: str = None) -> str:
        """Create a git commit"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        if not message:
            return "❌ No commit message provided"
        
        try:
            success, stdout, stderr = self._run_git_command(['git', 'commit', '-m', message], working_dir)
            
            if not success:
                if "not a git repository" in stderr.lower():
                    return f"❌ Not a git repository: {working_dir}"
                elif "nothing to commit" in stderr.lower():
                    return f"ℹ️ Nothing to commit in {working_dir}"
                else:
                    return f"❌ Git commit failed: {stderr}"
            
            return f"✅ Commit created successfully:\n{stdout}"
            
        except Exception as e:
            return f"❌ Error creating git commit: {str(e)}"
    
    def clone(self, repository_url: str, target_dir: str = None, working_dir: str = None) -> str:
        """Clone a git repository"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        if not repository_url:
            return "❌ No repository URL provided"
        
        try:
            if target_dir:
                success, stdout, stderr = self._run_git_command(['git', 'clone', repository_url, target_dir], working_dir)
            else:
                success, stdout, stderr = self._run_git_command(['git', 'clone', repository_url], working_dir)
            
            if not success:
                return f"❌ Git clone failed: {stderr}"
            
            return f"✅ Successfully cloned repository:\n{stdout}"
            
        except Exception as e:
            return f"❌ Error cloning repository: {str(e)}"
    
    def init_repo(self, working_dir: str = None) -> str:
        """Initialize a new git repository"""
        if working_dir is None:
            working_dir = str(Path.home() / "coding-agent")
        
        try:
            success, stdout, stderr = self._run_git_command(['git', 'init'], working_dir)
            
            if not success:
                return f"❌ Git init failed: {stderr}"
            
            return f"✅ Git repository initialized in {working_dir}"
            
        except Exception as e:
            return f"❌ Error initializing git repository: {str(e)}"
