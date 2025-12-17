"""
Advanced Session Management for Sheikh-CLI
Handles persistent sessions, context management, and workflow state
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm
import uuid

console = Console()

@dataclass
class SessionContext:
    """Session context data structure"""
    session_id: str
    created_at: datetime
    last_active: datetime
    working_directory: str
    git_repo: Optional[str]
    active_branch: Optional[str]
    workflow_state: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    file_cache: Dict[str, str]
    preferences: Dict[str, Any]

@dataclass
class ModelConfig:
    """Model configuration for switching between providers"""
    name: str
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_type: str = "text"
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True

class SessionManager:
    """Advanced session management with persistence and context awareness"""
    
    def __init__(self, session_dir: Optional[Path] = None):
        self.session_dir = session_dir or Path.home() / ".sheikh-sessions"
        self.session_dir.mkdir(exist_ok=True)
        self.active_session: Optional[SessionContext] = None
        self.model_configs: Dict[str, ModelConfig] = {}
        self.load_model_configs()
    
    def create_session(self, name: str = None, working_dir: str = None) -> str:
        """Create a new session with auto-generated ID"""
        session_id = name or f"session_{uuid.uuid4().hex[:8]}"
        working_directory = working_dir or os.getcwd()
        
        # Check for existing git repo
        git_repo = None
        active_branch = None
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], 
                capture_output=True, text=True, cwd=working_directory
            )
            if result.returncode == 0:
                git_repo = result.stdout.strip()
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"], 
                    capture_output=True, text=True, cwd=git_repo
                )
                if branch_result.returncode == 0:
                    active_branch = branch_result.stdout.strip()
        except:
            pass
        
        self.active_session = SessionContext(
            session_id=session_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            working_directory=working_directory,
            git_repo=git_repo,
            active_branch=active_branch,
            workflow_state={},
            conversation_history=[],
            file_cache={},
            preferences={
                "auto_save": True,
                "max_history": 100,
                "enable_file_caching": True
            }
        )
        
        self.save_session()
        console.print(f"[green]✅ Created session: {session_id}[/green]")
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session"""
        session_file = self.session_dir / f"{session_id}.json"
        if not session_file.exists():
            console.print(f"[red]Session '{session_id}' not found[/red]")
            return False
        
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            data['last_active'] = datetime.fromisoformat(data['last_active'])
            
            self.active_session = SessionContext(**data)
            console.print(f"[green]✅ Loaded session: {session_id}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to load session: {e}[/red]")
            return False
    
    def save_session(self):
        """Save current session to disk"""
        if not self.active_session:
            return
        
        session_file = self.session_dir / f"{self.active_session.session_id}.json"
        
        # Update last active time
        self.active_session.last_active = datetime.now()
        
        try:
            data = asdict(self.active_session)
            # Convert datetime objects to ISO format strings
            data['created_at'] = self.active_session.created_at.isoformat()
            data['last_active'] = self.active_session.last_active.isoformat()
            
            with open(session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Failed to save session: {e}[/red]")
    
    def list_sessions(self) -> List[str]:
        """List all available sessions"""
        sessions = []
        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    session_id = data['session_id']
                    last_active = datetime.fromisoformat(data['last_active'])
                    sessions.append((session_id, last_active))
            except:
                continue
        
        # Sort by last active time, most recent first
        sessions.sort(key=lambda x: x[1], reverse=True)
        return [session_id for session_id, _ in sessions]
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        session_file = self.session_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            console.print(f"[red]Deleted session: {session_id}[/red]")
        else:
            console.print(f"[yellow]Session '{session_id}' not found[/yellow]")
    
    def update_working_directory(self, path: str):
        """Update the working directory of active session"""
        if self.active_session:
            self.active_session.working_directory = path
            self.save_session()
    
    def add_conversation_entry(self, user_input: str, agent_response: str):
        """Add conversation entry to session history"""
        if not self.active_session:
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_response
        }
        
        self.active_session.conversation_history.append(entry)
        
        # Maintain history limit
        max_history = self.active_session.preferences.get("max_history", 100)
        if len(self.active_session.conversation_history) > max_history:
            self.active_session.conversation_history = self.active_session.conversation_history[-max_history:]
        
        self.save_session()
    
    def get_conversation_context(self, limit: int = 10) -> str:
        """Get recent conversation context for AI processing"""
        if not self.active_session or not self.active_session.conversation_history:
            return ""
        
        recent_history = self.active_session.conversation_history[-limit:]
        context_lines = ["Recent conversation context:"]
        
        for entry in recent_history:
            context_lines.append(f"User: {entry['user']}")
            context_lines.append(f"Agent: {entry['agent']}")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def cache_file_content(self, file_path: str, content: str):
        """Cache file content for faster access"""
        if not self.active_session or not self.active_session.preferences.get("enable_file_caching", True):
            return
        
        self.active_session.file_cache[file_path] = content
        self.save_session()
    
    def get_cached_file(self, file_path: str) -> Optional[str]:
        """Get cached file content"""
        if not self.active_session:
            return None
        
        return self.active_session.file_cache.get(file_path)
    
    def update_workflow_state(self, key: str, value: Any):
        """Update workflow state"""
        if self.active_session:
            self.active_session.workflow_state[key] = value
            self.save_session()
    
    def get_workflow_state(self, key: str, default: Any = None) -> Any:
        """Get workflow state value"""
        if not self.active_session:
            return default
        
        return self.active_session.workflow_state.get(key, default)
    
    def show_session_info(self):
        """Display current session information"""
        if not self.active_session:
            console.print("[yellow]No active session[/yellow]")
            return
        
        # Create info table
        info_table = Table(title="📋 Current Session Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="magenta")
        
        info_table.add_row("Session ID", self.active_session.session_id)
        info_table.add_row("Created", self.active_session.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        info_table.add_row("Last Active", self.active_session.last_active.strftime("%Y-%m-%d %H:%M:%S"))
        info_table.add_row("Working Directory", self.active_session.working_directory)
        info_table.add_row("Git Repository", self.active_session.git_repo or "None")
        info_table.add_row("Active Branch", self.active_session.active_branch or "None")
        info_table.add_row("Conversation Entries", str(len(self.active_session.conversation_history)))
        info_table.add_row("Cached Files", str(len(self.active_session.file_cache)))
        
        console.print(info_table)
        
        # Show workflow state if any
        if self.active_session.workflow_state:
            workflow_panel = Panel(
                json.dumps(self.active_session.workflow_state, indent=2),
                title="🔄 Workflow State",
                border_style="blue"
            )
            console.print(workflow_panel)
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    last_active = datetime.fromisoformat(data['last_active'])
                
                if last_active < cutoff_date:
                    session_file.unlink()
                    deleted_count += 1
            except:
                continue
        
        if deleted_count > 0:
            console.print(f"[green]Cleaned up {deleted_count} old sessions[/green]")
        else:
            console.print("[dim]No old sessions to clean up[/dim]")
    
    # Model Configuration Management
    def load_model_configs(self):
        """Load model configurations from file"""
        config_file = Path.home() / ".config" / "sheikh-cli" / "models.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    for name, config_data in data.items():
                        self.model_configs[name] = ModelConfig(**config_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load model configs: {e}[/yellow]")
        
        # Load default configs if none exist
        if not self.model_configs:
            self.load_default_models()
    
    def load_default_models(self):
        """Load default model configurations"""
        default_models = {
            "local-ollama": ModelConfig(
                name="local-ollama",
                provider="ollama",
                base_url="http://localhost:11434",
                model_type="local",
                max_tokens=4096,
                temperature=0.7
            ),
            "openai-gpt4": ModelConfig(
                name="openai-gpt4",
                provider="openai",
                model_type="api",
                max_tokens=4096,
                temperature=0.7
            ),
            "anthropic-claude": ModelConfig(
                name="anthropic-claude",
                provider="anthropic",
                model_type="api",
                max_tokens=4096,
                temperature=0.7
            ),
            "openrouter": ModelConfig(
                name="openrouter",
                provider="openrouter",
                model_type="api",
                max_tokens=4096,
                temperature=0.7
            ),
            "huggingface": ModelConfig(
                name="huggingface",
                provider="huggingface",
                model_type="api",
                max_tokens=2048,
                temperature=0.7
            )
        }
        
        self.model_configs.update(default_models)
        self.save_model_configs()
    
    def save_model_configs(self):
        """Save model configurations to file"""
        config_file = Path.home() / ".config" / "sheikh-cli" / "models.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {}
            for name, config in self.model_configs.items():
                data[name] = asdict(config)
            
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Failed to save model configs: {e}[/red]")
    
    def add_model_config(self, name: str, provider: str, **kwargs):
        """Add or update a model configuration"""
        self.model_configs[name] = ModelConfig(
            name=name,
            provider=provider,
            **kwargs
        )
        self.save_model_configs()
        console.print(f"[green]✅ Added model config: {name}[/green]")
    
    def remove_model_config(self, name: str):
        """Remove a model configuration"""
        if name in self.model_configs:
            del self.model_configs[name]
            self.save_model_configs()
            console.print(f"[red]Removed model config: {name}[/red]")
        else:
            console.print(f"[yellow]Model config '{name}' not found[/yellow]")
    
    def list_models(self):
        """List all available model configurations"""
        if not self.model_configs:
            console.print("[yellow]No model configurations found[/yellow]")
            return
        
        model_table = Table(title="🤖 Available Models")
        model_table.add_column("Name", style="cyan")
        model_table.add_column("Provider", style="magenta")
        model_table.add_column("Type", style="green")
        model_table.add_column("Max Tokens", style="blue")
        model_table.add_column("Status", style="yellow")
        
        for name, config in self.model_configs.items():
            status = "Enabled" if config.enabled else "Disabled"
            model_table.add_row(
                name,
                config.provider,
                config.model_type,
                str(config.max_tokens),
                status
            )
        
        console.print(model_table)
    
    def switch_model(self, name: str) -> Optional[ModelConfig]:
        """Switch to a different model configuration"""
        if name not in self.model_configs:
            console.print(f"[red]Model '{name}' not found[/red]")
            console.print(f"Available models: {', '.join(self.model_configs.keys())}")
            return None
        
        config = self.model_configs[name]
        if not config.enabled:
            console.print(f"[yellow]Model '{name}' is disabled[/yellow]")
            return None
        
        console.print(f"[green]✅ Switched to model: {name}[/green]")
        return config
    
    def test_model_connection(self, name: str) -> bool:
        """Test connection to a model"""
        if name not in self.model_configs:
            console.print(f"[red]Model '{name}' not found[/red]")
            return False
        
        config = self.model_configs[name]
        console.print(f"[blue]Testing connection to {name}...[/blue]")
        
        # This would implement actual connection testing
        # For now, just return True if model is configured
        try:
            if config.provider == "ollama":
                import requests
                response = requests.get(f"{config.base_url}/api/tags", timeout=5)
                return response.status_code == 200
            elif config.provider in ["openai", "anthropic", "openrouter"]:
                return bool(config.api_key)
            else:
                return True
        except Exception as e:
            console.print(f"[red]Connection test failed: {e}[/red]")
            return False

# Global session manager instance
session_manager = SessionManager()