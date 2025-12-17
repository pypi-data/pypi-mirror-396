#!/usr/bin/env python3
"""
Termux Local Coding Agent - Main Entry Point
A privacy-focused, local AI coding assistant that runs entirely on Android devices.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add tools directory to Python path
sys.path.append(str(Path(__file__).parent / "tools"))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

import typer
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

from .tools.file_operations import FileOperations
from .tools.shell_commands import ShellCommands
from .tools.code_search import CodeSearch
from .tools.git_operations import GitOperations

app = typer.Typer(
    help="🧠 sheikh-cli - Privacy-first AI coding assistant for Termux",
    rich_markup_mode="rich"
)

console = Console()

@dataclass
class AgentConfig:
    """Configuration for the coding agent"""
    model_type: str = "local_first"  # local_first, local_only, remote_fallback
    llama_cpp_path: str = ""
    model_path: str = ""
    max_tokens: int = 512
    temperature: float = 0.7
    sandbox_enabled: bool = True
    max_execution_time: int = 30
    allowed_directories: List[str] = None
    
    def __post_init__(self):
        if self.allowed_directories is None:
            self.allowed_directories = [
                str(Path.home() / "coding-agent"),
                str(Path.home() / "storage" / "shared"),
            ]

class CodingAgent:
    """Main coding agent orchestrator"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.console = Console()
        self.logger = self._setup_logging()
        
        # Initialize tools
        self.file_ops = FileOperations(config.allowed_directories)
        self.shell_cmds = ShellCommands(config.max_execution_time)
        self.code_search = CodeSearch()
        self.git_ops = GitOperations()
        
        # Tool registry for no-code interface
        self.tools = {
            "read_file": self.file_ops.read_file,
            "write_file": self.file_ops.write_file,
            "search_code": self.code_search.search_code,
            "run_shell": self.shell_cmds.run_command,
            "git_status": self.git_ops.status,
            "git_diff": self.git_ops.diff,
            "list_files": self.file_ops.list_files,
            "find_files": self.file_ops.find_files,
        }
        
        self.console.print("[bold blue]🧠 Sheikh-CLI Initialized[/bold blue]")
        self.logger.info("Agent initialized with config: %s", config)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_dir = Path.home() / "coding-agent" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "agent.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    async def process_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Process a natural language prompt and execute appropriate tools"""
        try:
            self.logger.info(f"Processing prompt: {prompt}")
            
            # For now, implement simple intent detection
            # In a full implementation, this would call a local LLM
            intent = self._detect_intent(prompt)
            result = await self._execute_intent(intent, prompt, context)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing prompt: {e}")
            return f"❌ Error: {str(e)}"
    
    def _detect_intent(self, prompt: str) -> Dict[str, Any]:
        """Simple intent detection - in production, use local LLM"""
        prompt_lower = prompt.lower()
        
        if "read" in prompt_lower and any(ext in prompt_lower for ext in [".py", ".js", ".md", ".txt"]):
            return {"action": "read_file", "params": {"file_path": self._extract_file_path(prompt)}}
        elif "write" in prompt_lower or "create" in prompt_lower:
            return {"action": "write_file", "params": {"content": self._extract_content(prompt)}}
        elif "search" in prompt_lower or "find" in prompt_lower:
            return {"action": "search_code", "params": {"pattern": self._extract_search_pattern(prompt)}}
        elif "git" in prompt_lower:
            if "status" in prompt_lower:
                return {"action": "git_status", "params": {}}
            elif "diff" in prompt_lower:
                return {"action": "git_diff", "params": {}}
        elif "list" in prompt_lower or "show" in prompt_lower:
            return {"action": "list_files", "params": {"directory": self._extract_directory(prompt)}}
        else:
            return {"action": "run_shell", "params": {"command": prompt}}
    
    async def _execute_intent(self, intent: Dict[str, Any], original_prompt: str, context: Dict[str, Any] = None) -> str:
        """Execute the detected intent"""
        action = intent["action"]
        params = intent["params"]
        
        if action not in self.tools:
            return f"❌ Unknown action: {action}"
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Executing {action}...", total=None)
                
                result = self.tools[action](**params)
                
                progress.update(task, description="✅ Complete")
                
            return result
            
        except Exception as e:
            return f"❌ Error executing {action}: {str(e)}"
    
    def _extract_file_path(self, prompt: str) -> str:
        """Extract file path from prompt"""
        # Simple extraction - in production, use more sophisticated parsing
        words = prompt.split()
        for word in words:
            if "." in word and len(word) > 2:
                return word
        return str(Path.home() / "coding-agent")  # Default path
    
    def _extract_content(self, prompt: str) -> str:
        """Extract content to write from prompt"""
        # Simple extraction - in production, use more sophisticated parsing
        if "create" in prompt.lower():
            return f"# Generated content for: {prompt}\n\n"
        return f"# Content for: {prompt}\n\n"
    
    def _extract_search_pattern(self, prompt: str) -> str:
        """Extract search pattern from prompt"""
        # Remove common words and extract search terms
        words = prompt.lower().replace("search", "").replace("find", "").replace("for", "").strip().split()
        return " ".join(words[:3])  # Take first 3 words as pattern
    
    def _extract_directory(self, prompt: str) -> str:
        """Extract directory from prompt"""
        return str(Path.home() / "coding-agent")
    
    def run_interactive_mode(self):
        """Run agent in interactive mode"""
        self.console.print(Panel.fit(
            "[bold cyan]🧠 Sheikh-CLI Interactive Mode[/bold cyan]\n"
            "Type 'help' for commands, 'quit' to exit, or describe what you want to do.",
            border_style="cyan"
        ))
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold yellow]You[/bold yellow]").strip()
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    self.console.print("[bold red]Goodbye! 👋[/bold red]")
                    break
                elif user_input.lower() == "help":
                    self._show_help()
                elif user_input:
                    # Process the prompt asynchronously
                    result = asyncio.run(self.process_prompt(user_input))
                    self.console.print(f"\n[bold green]Agent:[/bold green] {result}")
                    
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Interrupted. Use 'quit' to exit.[/bold red]")
                continue
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/bold red]")
    
    def _show_help(self):
        """Show help information"""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="magenta")
        help_table.add_column("Example", style="green")
        
        help_table.add_row("read_file", "Read contents of a file", "read example.py")
        help_table.add_row("write_file", "Create or write to a file", "write new file content")
        help_table.add_row("search_code", "Search for patterns in code", "search for 'function'")
        help_table.add_row("run_shell", "Execute shell commands", "ls -la")
        help_table.add_row("git_status", "Show git repository status", "git status")
        help_table.add_row("git_diff", "Show git diff", "git diff")
        help_table.add_row("list_files", "List files in directory", "list files")
        
        self.console.print(help_table)

def load_config(config_path: str = None) -> AgentConfig:
    """Load agent configuration"""
    if config_path is None:
        # Look for config in package data
        package_config = Path(__file__).parent / "config" / "agent_config.json"
        if package_config.exists():
            config_path = str(package_config)
        else:
            config_path = str(Path.home() / "coding-agent" / "config" / "agent_config.json")
    
    config_file = Path(config_path)
    if not config_file.exists():
        console.print(f"[yellow]Configuration file not found: {config_path}[/yellow]")
        return AgentConfig()
    
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        return AgentConfig(**config_data)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return AgentConfig()

@app.command()
def interactive(
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Start the coding agent in interactive mode"""
    agent_config = load_config(config)
    agent = CodingAgent(agent_config)
    agent.run_interactive_mode()

@app.command()
def prompt(
    prompt_text: str = typer.Argument(..., help="Natural language prompt to process"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Process a single prompt"""
    agent_config = load_config(config)
    agent = CodingAgent(agent_config)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing prompt...", total=None)
        result = asyncio.run(agent.process_prompt(prompt_text))
        progress.update(task, description="✅ Complete")
    
    console.print(f"\n[bold green]Result:[/bold green] {result}")
    
    if output:
        with open(output, 'w') as f:
            f.write(result)
        console.print(f"[bold blue]Result saved to: {output}[/bold blue]")

@app.command()
def tools():
    """List available tools"""
    agent_config = load_config()
    agent = CodingAgent(agent_config)
    
    tools_table = Table(title="Available Tools")
    tools_table.add_column("Tool", style="cyan", no_wrap=True)
    tools_table.add_column("Description", style="magenta")
    
    tool_descriptions = {
        "read_file": "Read file contents",
        "write_file": "Create or write to files",
        "search_code": "Search code patterns",
        "run_shell": "Execute shell commands",
        "git_status": "Git repository status",
        "git_diff": "Show git changes",
        "list_files": "List directory contents",
        "find_files": "Find files by pattern"
    }
    
    for tool, description in tool_descriptions.items():
        tools_table.add_row(tool, description)
    
    console.print(tools_table)

@app.command()
def setup(
    target_dir: Optional[str] = typer.Option(None, "--target", help="Target directory for setup")
):
    """Setup Termux development environment"""
    if target_dir is None:
        target_dir = str(Path.home() / "coding-agent")
    
    console.print(f"[bold blue]Setting up Termux environment in {target_dir}[/bold blue]")
    
    # Create directory structure
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (target_path / "logs").mkdir(exist_ok=True)
    (target_path / "models").mkdir(exist_ok=True)
    (target_path / "config").mkdir(exist_ok=True)
    
    # Copy configuration if not exists
    config_path = target_path / "config" / "agent_config.json"
    if not config_path.exists():
        import shutil
        shutil.copy(Path(__file__).parent / "config" / "agent_config.json", config_path)
    
    console.print(f"[bold green]✅ Setup complete! Environment created at {target_path}[/bold green]")
    console.print(f"[bold blue]Next steps:[/bold blue]")
    console.print(f"  - Interactive mode: sheikh-cli interactive")
    console.print(f"  - Single prompt: sheikh-cli prompt 'your command'")
    console.print(f"  - List tools: sheikh-cli tools")

if __name__ == "__main__":
    app()
