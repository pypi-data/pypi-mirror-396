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
from .openrouter_ai import OpenRouterAI
from .interactive_dev_env import InteractiveDevelopmentEnvironment
from .repository_integration import RepositoryIntegration
from .session_manager import session_manager, SessionManager
from .workflow_orchestrator import workflow_orchestrator, WorkflowOrchestrator
from .advanced_config import config_manager, ConfigManager, ModelCapability, ProviderType

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
    openrouter_api_key: str = ""
    approval_mode: str = "consultative"  # auto, consultative, read_only
    auto_approve: bool = False
    read_only: bool = False
    
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
        
        # Initialize AI capabilities
        self.ai = OpenRouterAI(config.openrouter_api_key if hasattr(config, 'openrouter_api_key') else None)
        
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
        """Enhanced intent detection using OpenRouter AI if available"""
        # Try OpenRouter AI first if available
        if self.ai.is_available():
            try:
                ai_intent = self.ai.detect_intent(prompt)
                if ai_intent.get("confidence", 0) > 0.6:
                    # Convert AI response to our format
                    action = ai_intent.get("action", "run_shell")
                    params = ai_intent.get("parameters", {})
                    self.console.print(f"[dim]🤖 AI detected intent: {action} (confidence: {ai_intent.get('confidence', 0):.2f})[/dim]")
                    return {"action": action, "params": params, "explanation": ai_intent.get("explanation", "")}
            except Exception as e:
                self.logger.warning(f"AI intent detection failed: {e}")
        
        # Fallback to simple pattern matching
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
def ai_generate(
    description: str = typer.Argument(..., help="Description of the code to generate"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Generate code using AI"""
    config = load_config()
    agent = CodingAgent(config)
    
    if not agent.ai.is_available():
        console.print("[yellow]OpenRouter AI not available. Set OPENROUTER_API_KEY environment variable.[/yellow]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating code with AI...", total=None)
        code = agent.ai.generate_code(description, language)
        progress.update(task, description="✅ Code generated")
    
    console.print(f"\n[bold green]Generated {language} code:[/bold green]")
    console.print(Panel(code, title="AI Generated Code", border_style="green"))
    
    if output:
        with open(output, 'w') as f:
            f.write(code)
        console.print(f"[bold blue]Code saved to: {output}[/bold blue]")

@app.command()
def ai_explain(
    code_file: str = typer.Argument(..., help="Path to code file to explain"),
    language: str = typer.Option(None, "--language", "-l", help="Programming language (auto-detected if not provided)")
):
    """Explain code using AI"""
    config = load_config()
    agent = CodingAgent(config)
    
    if not agent.ai.is_available():
        console.print("[yellow]OpenRouter AI not available. Set OPENROUTER_API_KEY environment variable.[/yellow]")
        return
    
    # Read the code file
    if not Path(code_file).exists():
        console.print(f"[red]File not found: {code_file}[/red]")
        return
    
    with open(code_file, 'r') as f:
        code_content = f.read()
    
    # Auto-detect language if not provided
    if not language:
        if code_file.endswith('.py'):
            language = 'python'
        elif code_file.endswith(('.js', '.ts', '.jsx', '.tsx')):
            language = 'javascript'
        elif code_file.endswith(('.java', '.kt')):
            language = 'java'
        elif code_file.endswith(('.cpp', '.c', '.h')):
            language = 'cpp'
        else:
            language = 'python'  # default
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Explaining code with AI...", total=None)
        explanation = agent.ai.explain_code(code_content, language)
        progress.update(task, description="✅ Code explained")
    
    console.print(f"\n[bold green]AI Explanation of {code_file}:[/bold green]")
    console.print(Panel(explanation, title=f"AI Explanation ({language})", border_style="green"))

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

@app.command()
def ide(
    directory: Optional[str] = typer.Option(None, "--directory", "-d", help="Working directory for the IDE"),
    model: str = typer.Option("openai/gpt-3.5-turbo", "--model", "-m", help="AI model to use"),
    auto_approve: bool = typer.Option(False, "--auto-approve", help="Enable auto-approval mode"),
    read_only: bool = typer.Option(False, "--read-only", help="Enable read-only mode"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to configuration file")
):
    """Launch advanced interactive development environment"""
    config_obj = load_config(config)
    
    # Set working directory
    if directory:
        if not Path(directory).exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            return
        os.chdir(directory)
    
    # Set approval mode
    if read_only:
        config_obj.approval_mode = "read_only"
    elif auto_approve:
        config_obj.approval_mode = "auto"
    else:
        config_obj.approval_mode = "consultative"
    
    # Initialize IDE
    ide = InteractiveDevelopmentEnvironment(config_obj)
    ide.ai_model = model
    
    console.print(Panel.fit(
        f"[bold cyan]🚀 Sheikh-CLI Advanced IDE[/bold cyan]\n"
        f"Working Directory: [yellow]{Path.cwd()}[/yellow]\n"
        f"AI Model: [green]{model}[/green]\n"
        f"Approval Mode: [blue]{config_obj.approval_mode}[/blue]\n"
        f"GitHub: [link]https://github.com/osamabinlikhon/sheikh-cli[/link]",
        border_style="cyan"
    ))
    
    try:
        asyncio.run(ide.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]IDE session interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]IDE error: {e}[/red]")

@app.command()
def repository(
    action: str = typer.Argument(..., help="Action: clone, status, diff, commit, analyze, review, workflow"),
    url: Optional[str] = typer.Option(None, help="Repository URL for clone action"),
    directory: Optional[str] = typer.Option(None, help="Target directory"),
    message: Optional[str] = typer.Option(None, help="Commit message"),
    branch: Optional[str] = typer.Option(None, help="Branch name"),
    files: Optional[str] = typer.Option(None, help="Comma-separated list of files for review"),
    config: Optional[str] = typer.Option(None, help="Path to configuration file")
):
    """Advanced repository management with AI assistance"""
    config_obj = load_config(config)
    agent = CodingAgent(config_obj)
    repo_integration = RepositoryIntegration(agent.ai)
    
    # Set working directory
    if directory:
        if not Path(directory).exists():
            console.print(f"[red]Directory not found: {directory}[/red]")
            return
        os.chdir(directory)
    
    if action == "clone":
        if not url:
            console.print("[red]Repository URL required for clone action[/red]")
            return
        
        target_dir = directory or url.split('/')[-1].replace('.git', '')
        console.print(f"[blue]Cloning repository to {target_dir}...[/blue]")
        
        result = agent.git_ops.clone(url, target_dir)
        console.print(result)
        
    elif action == "status":
        console.print("[blue]Repository status:[/blue]")
        result = agent.git_ops.status(directory)
        console.print(result)
        
    elif action == "diff":
        console.print("[blue]Repository diff:[/blue]")
        result = agent.git_ops.diff(working_dir=directory)
        console.print(result)
        
    elif action == "commit":
        if not message:
            console.print("[red]Commit message required[/red]")
            return
        
        console.print("[blue]Committing changes...[/blue]")
        result = agent.git_ops.commit(message, working_dir=directory)
        console.print(result)
        
    elif action == "analyze":
        console.print("[blue]🔍 AI Repository Analysis:[/blue]")
        summary = repo_integration.generate_ai_repository_summary(directory)
        console.print(Panel(summary, title="Repository Analysis", border_style="blue"))
        
    elif action == "review":
        file_list = []
        if files:
            file_list = [f.strip() for f in files.split(',')]
        
        console.print("[blue]🤖 AI Code Review:[/blue]")
        review = repo_integration.ai_code_review(file_list, directory)
        console.print(Panel(review, title="AI Code Review", border_style="green"))
        
    elif action == "workflow":
        console.print("[blue]🔄 Git Workflow Suggestions:[/blue]")
        workflow = repo_integration.suggest_git_workflow(directory)
        console.print(Panel(workflow, title="Git Workflow Recommendations", border_style="cyan"))
        
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: clone, status, diff, commit, analyze, review, workflow")

@app.command()
def workflow(
    name: str = typer.Argument(..., help="Workflow name"),
    auto: bool = typer.Option(False, "--auto", help="Run in auto mode"),
    config: Optional[str] = typer.Option(None, help="Path to configuration file")
):
    """Execute pre-defined development workflows"""
    config_obj = load_config(config)
    agent = CodingAgent(config_obj)
    
    workflows = {
        "code-review": {
            "description": "Automated code review workflow",
            "steps": ["git status", "git diff", "search_code issues", "ai-explain problems"]
        },
        "new-feature": {
            "description": "New feature development workflow", 
            "steps": ["git checkout -b", "create feature files", "write tests", "git commit"]
        },
        "debug-session": {
            "description": "Debug workflow for identifying and fixing issues",
            "steps": ["search_code error", "ai-explain issue", "generate fix", "test solution"]
        },
        "refactor": {
            "description": "Code refactoring workflow",
            "steps": ["analyze code", "identify improvements", "generate refactored code", "validate changes"]
        }
    }
    
    if name not in workflows:
        console.print(f"[red]Unknown workflow: {name}[/red]")
        console.print(f"Available workflows: {', '.join(workflows.keys())}")
        return
    
    workflow = workflows[name]
    console.print(f"[bold blue]🚀 Running workflow: {name}[/bold blue]")
    console.print(f"[dim]{workflow['description']}[/dim]")
    
    for i, step in enumerate(workflow['steps'], 1):
        console.print(f"\n[yellow]Step {i}/{len(workflow['steps'])}: {step}[/yellow]")
        
        if auto:
            result = asyncio.run(agent.process_prompt(step))
            console.print(result[:200] + "..." if len(result) > 200 else result)
        else:
            if not Confirm.ask(f"Execute step: {step}"):
                console.print("[yellow]Workflow cancelled by user[/yellow]")
                break
    
    console.print(f"[green]✅ Workflow '{name}' completed![/green]")

@app.command()
def config_show():
    """Display current configuration"""
    config = load_config()
    
    config_table = Table(title="🔧 Sheikh-CLI Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="magenta")
    
    config_table.add_row("Model Type", config.model_type)
    config_table.add_row("AI Available", "Yes" if hasattr(config, 'openrouter_api_key') and config.openrouter_api_key else "No")
    config_table.add_row("Max Tokens", str(config.max_tokens))
    config_table.add_row("Temperature", str(config.temperature))
    config_table.add_row("Sandbox Enabled", str(config.sandbox_enabled))
    config_table.add_row("Max Execution Time", f"{config.max_execution_time}s")
    
    console.print(config_table)

@app.command()
def config_set(
    key: str,
    value: str
):
    """Set configuration value"""
    config_path = Path.home() / ".config" / "sheikh-cli" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    else:
        config_data = {}
    
    config_data[key] = value
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    console.print(f"[green]✅ Configuration updated: {key} = {value}[/green]")

# Session Management Commands
@app.command()
def session_create(
    name: str = typer.Option(None, "--name", "-n", help="Session name"),
    working_dir: str = typer.Option(None, "--working-dir", "-d", help="Working directory")
):
    """Create a new coding session"""
    session_id = session_manager.create_session(name, working_dir)
    console.print(f"[green]✅ Session created: {session_id}[/green]")

@app.command()
def session_load(session_id: str):
    """Load an existing session"""
    success = session_manager.load_session(session_id)
    if success:
        session_manager.show_session_info()

@app.command()
def session_list():
    """List all available sessions"""
    sessions = session_manager.list_sessions()
    if sessions:
        sessions_table = Table(title="💾 Available Sessions")
        sessions_table.add_column("Session ID", style="cyan")
        
        for session_id in sessions:
            sessions_table.add_row(session_id)
        
        console.print(sessions_table)
    else:
        console.print("[yellow]No sessions found[/yellow]")

@app.command()
def session_delete(session_id: str):
    """Delete a session"""
    if Confirm.ask(f"Delete session '{session_id}'?"):
        session_manager.delete_session(session_id)

@app.command()
def session_info():
    """Show current session information"""
    session_manager.show_session_info()

@app.command()
def session_cleanup(days: int = typer.Option(30, "--days", help="Keep sessions newer than N days")):
    """Clean up old sessions"""
    session_manager.cleanup_old_sessions(days)

# Model Management Commands
@app.command()
def model_list():
    """List all available models"""
    config_manager.list_models()

@app.command()
def model_switch(model_id: str):
    """Switch to a different model"""
    config_manager.switch_model(model_id)

@app.command()
def model_test(model_id: str):
    """Test model connectivity"""
    config_manager.test_model(model_id)

@app.command()
def model_add(
    model_id: str,
    name: str = typer.Option(..., "--name", help="Model display name"),
    provider: str = typer.Option(..., "--provider", help="Provider type (openai, anthropic, openrouter, huggingface, ollama, local)"),
    description: str = typer.Option(..., "--description", help="Model description"),
    max_tokens: int = typer.Option(4096, "--max-tokens", help="Maximum tokens"),
    context_length: int = typer.Option(16384, "--context-length", help="Context length"),
    local_model: bool = typer.Option(False, "--local", help="Is this a local model"),
    api_endpoint: str = typer.Option(None, "--endpoint", help="API endpoint"),
    api_key_env: str = typer.Option(None, "--api-key-env", help="Environment variable for API key")
):
    """Add a new model configuration"""
    capabilities = ["code_generation", "code_explanation"]  # Default capabilities
    
    config_manager.add_model(
        model_id=model_id,
        name=name,
        provider=provider,
        description=description,
        capabilities=capabilities,
        max_tokens=max_tokens,
        context_length=context_length,
        local_model=local_model,
        api_endpoint=api_endpoint,
        api_key_env=api_key_env
    )

@app.command()
def model_remove(model_id: str):
    """Remove a model configuration"""
    config_manager.remove_model(model_id)

@app.command()
def model_export(output_path: str):
    """Export model configuration"""
    config_manager.export_configuration(Path(output_path))

@app.command()
def model_import(input_path: str):
    """Import model configuration"""
    config_manager.import_configuration(Path(input_path))

# Workflow Management Commands
@app.command()
def workflow_list(category: str = typer.Option(None, "--category", help="Filter by category")):
    """List available workflows"""
    workflow_orchestrator.list_workflows(category)

@app.command()
def workflow_show(workflow_id: str):
    """Show workflow details"""
    workflow_orchestrator.show_workflow_details(workflow_id)

@app.command()
def workflow_run(
    workflow_id: str,
    auto_approve: bool = typer.Option(False, "--auto-approve", help="Auto-approve all steps"),
    params: str = typer.Option(None, "--params", help="Workflow parameters as JSON")
):
    """Execute a workflow"""
    import json
    workflow_params = {}
    
    if params:
        try:
            workflow_params = json.loads(params)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON parameters[/red]")
            return
    
    asyncio.run(workflow_orchestrator.execute_workflow(workflow_id, workflow_params, auto_approve))

@app.command()
def workflow_executions(limit: int = typer.Option(10, "--limit", help="Number of executions to show")):
    """Show recent workflow executions"""
    workflow_orchestrator.list_executions(limit)

# Advanced Configuration Commands
@app.command()
def config_advanced():
    """Show advanced configuration"""
    config_manager.show_configuration()

@app.command()
def config_reset():
    """Reset configuration to defaults"""
    if Confirm.ask("Reset configuration to defaults?"):
        config_manager.reset_to_defaults()

# Interactive Development Commands
@app.command()
def ide():
    """Launch interactive development environment"""
    config_obj = load_config()
    ide = InteractiveDevelopmentEnvironment(config_obj)
    ide.run()

@app.command()
def repo_action(
    action: str = typer.Argument(..., help="Action to perform (clone, status, diff, commit)"),
    target: str = typer.Argument(None, help="Target repository or file")
):
    """Repository integration actions"""
    repo = RepositoryIntegration()
    
    if action == "clone":
        if not target:
            console.print("[red]Repository URL required for clone action[/red]")
            return
        repo.clone_repository(target)
    
    elif action == "status":
        repo.show_repository_status()
    
    elif action == "diff":
        repo.show_differences()
    
    elif action == "commit":
        message = Prompt.ask("Commit message")
        repo.commit_changes(message)
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("Available actions: clone, status, diff, commit")

# AI Commands with Enhanced Features
@app.command()
def ai_chat(
    message: str = typer.Argument(..., help="Message to send to AI"),
    model: str = typer.Option(None, "--model", help="Specific model to use"),
    stream: bool = typer.Option(False, "--stream", help="Stream response"),
    max_tokens: int = typer.Option(None, "--max-tokens", help="Maximum tokens")
):
    """Chat with AI using configured models"""
    config_obj = load_config()
    agent = CodingAgent(config_obj)
    
    # Use specific model if provided
    if model:
        config_manager.switch_model(model)
    
    # Add to session conversation history
    if session_manager.active_session:
        response = asyncio.run(agent.process_prompt(message))
        session_manager.add_conversation_entry(message, response)
    else:
        response = asyncio.run(agent.process_prompt(message))
    
    if stream:
        console.print("[blue]Streaming response...[/blue]")
        # Implement streaming logic here
    
    console.print(response)

@app.command()
def ai_explain(
    target: str = typer.Argument(..., help="File or code to explain"),
    model: str = typer.Option(None, "--model", help="Specific model to use")
):
    """Explain code using AI"""
    config_obj = load_config()
    agent = CodingAgent(config_obj)
    
    if model:
        config_manager.switch_model(model)
    
    # Get file content if it's a file path
    if os.path.exists(target):
        with open(target, 'r') as f:
            code_content = f.read()
        prompt = f"Explain the following code:\n\n```\n{code_content}\n```"
    else:
        prompt = f"Explain the following code:\n\n```\n{target}\n```"
    
    response = asyncio.run(agent.process_prompt(prompt))
    console.print(response)

@app.command()
def ai_debug(
    code: str = typer.Argument(..., help="Code to debug"),
    model: str = typer.Option(None, "--model", help="Specific model to use")
):
    """Debug code using AI"""
    config_obj = load_config()
    agent = CodingAgent(config_obj)
    
    if model:
        config_manager.switch_model(model)
    
    prompt = f"Debug the following code and identify issues:\n\n```\n{code}\n```"
    response = asyncio.run(agent.process_prompt(prompt))
    console.print(response)

# Utility Commands
@app.command()
def doctor():
    """Run system diagnostics"""
    console.print("[bold blue]🔍 Sheikh-CLI System Diagnostics[/bold blue]\n")
    
    # Check configuration
    config_manager.show_configuration()
    console.print()
    
    # Check session manager
    if session_manager.active_session:
        console.print("[green]✅ Active session found[/green]")
    else:
        console.print("[yellow]⚠️ No active session[/yellow]")
    
    console.print()
    
    # Check available models
    active_model = config_manager.get_active_model_info()
    if active_model:
        console.print(f"[green]✅ Active model: {active_model.name}[/green]")
    else:
        console.print("[red]❌ No active model configured[/red]")
    
    console.print()
    
    # Test model connectivity
    if active_model:
        console.print("[blue]Testing model connectivity...[/blue]")
        config_manager.test_model(active_model.id)
    
    console.print()
    
    # Check workflows
    workflow_count = len(workflow_orchestrator.workflows)
    console.print(f"[green]✅ {workflow_count} workflows available[/green]")

@app.command()
def update():
    """Update sheikh-cli to latest version"""
    console.print("[blue]🔄 Checking for updates...[/blue]")
    console.print("[yellow]Note: Manual update required - check GitHub repository[/yellow]")
    console.print("[dim]Visit: https://github.com/osamabinlikhon/sheikh-cli[/dim]")

@app.command()
def version():
    """Show version information"""
    version_info = Panel(
        "[bold]Sheikh-CLI[/bold] - Privacy-first AI coding assistant\n"
        "[bold]Version:[/bold] 1.0.0\n"
        "[bold]Author:[/bold] osama bin likhon\n"
        "[bold]Repository:[/bold] https://github.com/osamabinlikhon/sheikh-cli\n"
        "[bold]PyPI:[/bold] https://pypi.org/project/sheikh-cli/",
        title="ℹ️ Version Information",
        border_style="blue"
    )
    console.print(version_info)

if __name__ == "__main__":
    app()
