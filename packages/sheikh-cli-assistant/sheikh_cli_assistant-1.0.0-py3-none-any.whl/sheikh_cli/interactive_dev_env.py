"""
Advanced Interactive Development Environment for Sheikh-CLI
Provides full-screen terminal UI with AI assistance and repository integration.
"""

import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich.console import Group

from .openrouter_ai import OpenRouterAI
from .tools.file_operations import FileOperations
from .tools.shell_commands import ShellCommands
from .tools.code_search import CodeSearch
from .tools.git_operations import GitOperations

class InteractiveDevelopmentEnvironment:
    """Advanced interactive development environment with AI assistance"""
    
    def __init__(self, config):
        self.config = config
        self.console = Console()
        self.ai = OpenRouterAI(config.openrouter_api_key if hasattr(config, 'openrouter_api_key') else None)
        
        # Initialize tools
        self.file_ops = FileOperations(config.allowed_directories)
        self.shell_cmds = ShellCommands(config.max_execution_time)
        self.code_search = CodeSearch()
        self.git_ops = GitOperations()
        
        # Session state
        self.current_directory = Path.cwd()
        self.session_history = []
        self.last_output = ""
        self.is_running = False
        
        # Repository state
        self.current_repo = None
        self.repo_changes = []
        
        # AI state
        self.ai_model = "openai/gpt-3.5-turbo"  # Using free model for testing
        
    def create_layout(self) -> Layout:
        """Create the main terminal layout"""
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        return layout
    
    def render_header(self) -> Panel:
        """Render the header panel"""
        status_text = f"📁 {self.current_directory} | 🤖 AI: {'Connected' if self.ai.is_available() else 'Offline'} | ⏰ {datetime.now().strftime('%H:%M:%S')}"
        return Panel(
            Align.center(Text(status_text, style="bold blue")),
            style="blue"
        )
    
    def render_left_panel(self) -> Panel:
        """Render the left panel with file explorer and commands"""
        # File tree
        tree = Tree("📁 Project Files", guide_style="bold blue")
        
        try:
            for item in self.current_directory.iterdir():
                if item.is_dir():
                    if item.name.startswith('.'):
                        tree.add(f"📁 [dim]{item.name}[/dim]")
                    else:
                        tree.add(f"📁 {item.name}")
                else:
                    if item.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
                        icon = self.get_file_icon(item.suffix)
                        tree.add(f"{icon} {item.name}")
                    else:
                        tree.add(f"📄 {item.name}")
        except PermissionError:
            tree.add("❌ Permission denied")
        
        return Panel(tree, title="🔍 Explorer", border_style="green")
    
    def render_right_panel(self) -> Panel:
        """Render the right panel with AI chat and history"""
        if self.session_history:
            chat_content = []
            for item in self.session_history[-10:]:  # Last 10 interactions
                timestamp = item['timestamp'].strftime('%H:%M:%S')
                if item['type'] == 'user':
                    chat_content.append(f"[yellow]You ({timestamp}):[/yellow] {item['content']}")
                else:
                    chat_content.append(f"[cyan]AI ({timestamp}):[/cyan] {item['content'][:100]}{'...' if len(item['content']) > 100 else ''}")
            
            return Panel(
                "\n".join(chat_content),
                title="💬 AI Chat",
                border_style="cyan"
            )
        else:
            return Panel(
                "💡 Ask me anything about your code!\n\nExample prompts:\n• 'Read the main.py file'\n• 'Generate a function to calculate fibonacci'\n• 'Explain this code'\n• 'Run git status'",
                title="💬 AI Chat",
                border_style="cyan"
            )
    
    def render_footer(self) -> Panel:
        """Render the footer with help and commands"""
        help_text = "Commands: /help • /files • /git • /exit | AI Models: gpt-3.5-turbo | Free tier active"
        return Panel(
            Align.center(Text(help_text, style="dim")),
            style="dim"
        )
    
    def get_file_icon(self, extension: str) -> str:
        """Get appropriate icon for file type"""
        icons = {
            '.py': '🐍',
            '.js': '🟨',
            '.ts': '🔷',
            '.jsx': '⚛️',
            '.tsx': '⚛️',
            '.java': '☕',
            '.cpp': '⚙️',
            '.c': '⚙️',
            '.h': '📄',
            '.md': '📝',
            '.json': '📋',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.txt': '📄'
        }
        return icons.get(extension, '📄')
    
    async def process_ai_prompt(self, prompt: str) -> str:
        """Process AI prompt with enhanced intent detection"""
        if not self.ai.is_available():
            return "❌ AI not available. Please check your OpenRouter API key."
        
        try:
            # Use free model for better performance and cost
            result = self.ai.chat_completion(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": f"""You are an advanced coding assistant in an interactive development environment.

Current directory: {self.current_directory}
Repository: {self.current_repo if self.current_repo else 'None'}

You can help with:
1. Code analysis and explanations
2. File operations (read, write, search)
3. Git operations (status, diff, commit)
4. Shell command execution
5. Code generation and refactoring
6. Development workflow automation

Respond concisely and provide actionable code when needed. If you need to execute commands, suggest the exact command to run."""},
                    {"role": "user", "content": prompt}
                ]
            )
            
            if "error" in result:
                return f"❌ AI Error: {result['error']}"
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"❌ Error processing AI request: {str(e)}"
    
    async def execute_tool_action(self, action: str, params: Dict[str, Any]) -> str:
        """Execute tool-based actions"""
        try:
            if action == "read_file":
                result = self.file_ops.read_file(params.get("file_path", ""))
            elif action == "write_file":
                result = self.file_ops.write_file(
                    params.get("file_path", ""),
                    params.get("content", "")
                )
            elif action == "search_code":
                result = self.code_search.search_code(
                    params.get("pattern", ""),
                    str(self.current_directory)
                )
            elif action == "run_shell":
                result = self.shell_cmds.run_command(params.get("command", ""))
            elif action == "git_status":
                result = self.git_ops.status(str(self.current_directory))
            elif action == "git_diff":
                result = self.git_ops.diff(working_dir=str(self.current_directory))
            elif action == "list_files":
                result = self.file_ops.list_files(str(self.current_directory))
            else:
                result = f"❌ Unknown action: {action}"
            
            return result
            
        except Exception as e:
            return f"❌ Error executing {action}: {str(e)}"
    
    def handle_command(self, command: str) -> str:
        """Handle special commands"""
        command = command.lower().strip()
        
        if command in ["/exit", "/quit", "/q"]:
            return "EXIT"
        elif command == "/help":
            return """🤖 Available Commands:

📁 File Operations:
  • /files - Refresh file explorer
  • /read <file> - Read a file
  • /write <file> <content> - Write to file

🔍 Code Analysis:
  • /search <pattern> - Search for patterns
  • /find <pattern> - Find files by pattern
  • /grep <pattern> - Grep search

⚡ Git Operations:
  • /git status - Show git status
  • /git diff - Show git diff
  • /git log - Show commit history

🛠️ System:
  • /clear - Clear chat history
  • /help - Show this help
  • /exit - Exit environment

💡 Natural Language:
  • Just type your request in natural language
  • Example: "Read the main.py file"
  • Example: "Generate a Python function for sorting"
  • Example: "What's the git status?"
"""
        elif command.startswith("/files"):
            return "REFRESH_FILES"
        elif command.startswith("/clear"):
            self.session_history.clear()
            return "✅ Chat history cleared"
        elif command.startswith("/read "):
            file_path = command[6:].strip()
            return asyncio.run(self.execute_tool_action("read_file", {"file_path": file_path}))
        elif command.startswith("/search "):
            pattern = command[8:].strip()
            return asyncio.run(self.execute_tool_action("search_code", {"pattern": pattern}))
        elif command.startswith("/git"):
            if command == "/git status":
                return asyncio.run(self.execute_tool_action("git_status", {}))
            elif command == "/git diff":
                return asyncio.run(self.execute_tool_action("git_diff", {}))
            else:
                return "Available git commands: /git status, /git diff"
        else:
            return None  # Not a special command
    
    def add_to_history(self, content: str, is_user: bool = True):
        """Add interaction to session history"""
        self.session_history.append({
            'content': content,
            'type': 'user' if is_user else 'ai',
            'timestamp': datetime.now()
        })
    
    async def run(self):
        """Run the interactive development environment"""
        self.is_running = True
        layout = self.create_layout()
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            with Live(layout, refresh_per_second=10, screen=True) as live:
                while self.is_running:
                    # Update layout
                    layout["header"] = self.render_header()
                    layout["left"] = self.render_left_panel()
                    layout["right"] = self.render_right_panel()
                    layout["footer"] = self.render_footer()
                    
                    # Get user input
                    try:
                        user_input = Prompt.ask("\n[bold yellow]💬 Ask AI[/bold yellow]").strip()
                    except (KeyboardInterrupt, EOFError):
                        break
                    
                    if not user_input:
                        continue
                    
                    # Check for special commands
                    command_result = self.handle_command(user_input)
                    
                    if command_result == "EXIT":
                        break
                    elif command_result:
                        # Command handled
                        self.add_to_history(user_input, True)
                        self.add_to_history(command_result, False)
                        continue
                    
                    # Process AI request
                    self.add_to_history(user_input, True)
                    
                    # Show processing indicator
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=self.console
                    ) as progress:
                        task = progress.add_task("🤖 AI thinking...", total=None)
                        ai_response = await self.process_ai_prompt(user_input)
                        progress.update(task, description="✅ AI response ready")
                    
                    self.add_to_history(ai_response, False)
                    
                    # Check if AI suggests any tool actions
                    intent = self.ai.detect_intent(user_input)
                    if intent.get("confidence", 0) > 0.7:
                        action = intent.get("action")
                        params = intent.get("parameters", {})
                        
                        if action and action != "run_shell":  # Don't auto-execute shell commands
                            tool_result = await self.execute_tool_action(action, params)
                            if tool_result and not tool_result.startswith("❌"):
                                self.add_to_history(f"[Tool Result] {tool_result[:200]}...", False)
        
        except Exception as e:
            self.console.print(f"[red]Error in interactive environment: {e}[/red]")
        
        finally:
            self.console.print("[bold blue]👋 Interactive environment closed[/bold blue]")
