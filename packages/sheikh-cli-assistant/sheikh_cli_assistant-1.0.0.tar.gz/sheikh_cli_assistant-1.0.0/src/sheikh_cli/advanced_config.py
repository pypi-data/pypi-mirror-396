"""
Advanced Configuration Management for Sheikh-CLI
Supports local models, multiple providers, and complex configuration options
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
import os

console = Console()

class ProviderType(Enum):
    """AI provider types"""
    LOCAL = "local"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"

class ModelCapability(Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    CODE_EXPLANATION = "code_explanation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    TRANSLATION = "translation"

class SecurityLevel(Enum):
    """Security levels for command execution"""
    SAFE = "safe"           # Only read operations
    MODERATE = "moderate"   # Read and safe write operations
    UNSAFE = "unsafe"       # All operations with approval
    FULL = "full"           # Full access without approval

@dataclass
class ModelInfo:
    """Model information and capabilities"""
    id: str
    name: str
    provider: ProviderType
    description: str
    capabilities: List[ModelCapability]
    max_tokens: int
    context_length: int
    cost_per_token: float
    speed_rating: int  # 1-5 scale
    quality_rating: int  # 1-5 scale
    local_model: bool
    model_path: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key_env: Optional[str] = None
    enabled: bool = True
    priority: int = 0  # Higher priority = preferred model

@dataclass
class SecurityConfig:
    """Security configuration for command execution"""
    level: SecurityLevel
    allowed_commands: List[str]
    blocked_commands: List[str]
    max_execution_time: int
    require_approval_for: List[str]
    sandbox_enabled: bool
    allowed_file_operations: List[str]
    git_operations_allowed: bool
    network_access: bool

@dataclass
class AdvancedConfig:
    """Advanced configuration structure"""
    # Model Configuration
    models: Dict[str, ModelInfo]
    active_model: str
    fallback_models: List[str]
    
    # Security Settings
    security: SecurityConfig
    
    # Performance Settings
    max_parallel_requests: int
    request_timeout: int
    retry_attempts: int
    cache_enabled: bool
    cache_ttl: int
    
    # UI/UX Settings
    theme: str
    color_scheme: str
    enable_syntax_highlighting: bool
    show_timestamps: bool
    max_output_length: int
    
    # Automation Settings
    auto_approve_safe: bool
    default_approval_mode: str
    workflow_timeout: int
    max_workflow_steps: int
    
    # Integration Settings
    git_auto_commit: bool
    git_commit_message_template: str
    file_backup_enabled: bool
    backup_retention_days: int
    
    # Advanced Features
    enable_code_analysis: bool
    enable_security_scanning: bool
    enable_performance_monitoring: bool
    enable_audit_logging: bool

class ConfigManager:
    """Advanced configuration management with validation and templates"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".config" / "sheikh-cli"
        self.config_file = self.config_dir / "advanced_config.yaml"
        self.backup_dir = self.config_dir / "backups"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.config: Optional[AdvancedConfig] = None
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                self.config = self._dict_to_config(data)
            except Exception as e:
                console.print(f"[red]Failed to load configuration: {e}[/red]")
                console.print("[yellow]Using default configuration[/yellow]")
                self.config = self._create_default_config()
        else:
            console.print("[blue]Configuration file not found, creating default configuration[/blue]")
            self.config = self._create_default_config()
            self.save_configuration()
    
    def _dict_to_config(self, data: Dict) -> AdvancedConfig:
        """Convert dictionary to AdvancedConfig"""
        # Convert model info
        models = {}
        for model_id, model_data in data.get('models', {}).items():
            capabilities = [ModelCapability(cap) for cap in model_data.get('capabilities', [])]
            models[model_id] = ModelInfo(
                id=model_id,
                name=model_data['name'],
                provider=ProviderType(model_data['provider']),
                description=model_data['description'],
                capabilities=capabilities,
                max_tokens=model_data['max_tokens'],
                context_length=model_data['context_length'],
                cost_per_token=model_data['cost_per_token'],
                speed_rating=model_data['speed_rating'],
                quality_rating=model_data['quality_rating'],
                local_model=model_data['local_model'],
                model_path=model_data.get('model_path'),
                api_endpoint=model_data.get('api_endpoint'),
                api_key_env=model_data.get('api_key_env'),
                enabled=model_data.get('enabled', True),
                priority=model_data.get('priority', 0)
            )
        
        # Convert security config
        security_data = data.get('security', {})
        security = SecurityConfig(
            level=SecurityLevel(security_data.get('level', 'moderate')),
            allowed_commands=security_data.get('allowed_commands', []),
            blocked_commands=security_data.get('blocked_commands', []),
            max_execution_time=security_data.get('max_execution_time', 60),
            require_approval_for=security_data.get('require_approval_for', []),
            sandbox_enabled=security_data.get('sandbox_enabled', True),
            allowed_file_operations=security_data.get('allowed_file_operations', ['read', 'write']),
            git_operations_allowed=security_data.get('git_operations_allowed', True),
            network_access=security_data.get('network_access', False)
        )
        
        return AdvancedConfig(
            models=models,
            active_model=data.get('active_model', 'openrouter'),
            fallback_models=data.get('fallback_models', []),
            security=security,
            max_parallel_requests=data.get('max_parallel_requests', 3),
            request_timeout=data.get('request_timeout', 30),
            retry_attempts=data.get('retry_attempts', 3),
            cache_enabled=data.get('cache_enabled', True),
            cache_ttl=data.get('cache_ttl', 3600),
            theme=data.get('theme', 'dark'),
            color_scheme=data.get('color_scheme', 'default'),
            enable_syntax_highlighting=data.get('enable_syntax_highlighting', True),
            show_timestamps=data.get('show_timestamps', True),
            max_output_length=data.get('max_output_length', 10000),
            auto_approve_safe=data.get('auto_approve_safe', True),
            default_approval_mode=data.get('default_approval_mode', 'full'),
            workflow_timeout=data.get('workflow_timeout', 3600),
            max_workflow_steps=data.get('max_workflow_steps', 50),
            git_auto_commit=data.get('git_auto_commit', False),
            git_commit_message_template=data.get('git_commit_message_template', 'Auto-commit by Sheikh-CLI: {description}'),
            file_backup_enabled=data.get('file_backup_enabled', True),
            backup_retention_days=data.get('backup_retention_days', 30),
            enable_code_analysis=data.get('enable_code_analysis', True),
            enable_security_scanning=data.get('enable_security_scanning', True),
            enable_performance_monitoring=data.get('enable_performance_monitoring', True),
            enable_audit_logging=data.get('enable_audit_logging', True)
        )
    
    def _create_default_config(self) -> AdvancedConfig:
        """Create default configuration with popular models"""
        models = {}
        
        # Local models
        models["ollama-codellama"] = ModelInfo(
            id="ollama-codellama",
            name="CodeLlama 7B (Local)",
            provider=ProviderType.LOCAL,
            description="Meta's CodeLlama 7B model running locally via Ollama",
            capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION, ModelCapability.DEBUGGING],
            max_tokens=4096,
            context_length=16384,
            cost_per_token=0.0,
            speed_rating=3,
            quality_rating=4,
            local_model=True,
            model_path="codellama:7b",
            api_endpoint="http://localhost:11434",
            enabled=True,
            priority=5
        )
        
        models["ollama-phi3"] = ModelInfo(
            id="ollama-phi3",
            name="Phi-3 Mini (Local)",
            provider=ProviderType.LOCAL,
            description="Microsoft's Phi-3 Mini 3.8B model for efficient coding tasks",
            capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION],
            max_tokens=2048,
            context_length=128000,
            cost_per_token=0.0,
            speed_rating=4,
            quality_rating=3,
            local_model=True,
            model_path="phi3:mini",
            api_endpoint="http://localhost:11434",
            enabled=True,
            priority=4
        )
        
        # API models
        models["openrouter-gpt4"] = ModelInfo(
            id="openrouter-gpt4",
            name="GPT-4 (via OpenRouter)",
            provider=ProviderType.OPENROUTER,
            description="OpenAI's GPT-4 via OpenRouter API with better availability",
            capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION, 
                         ModelCapability.CODE_REVIEW, ModelCapability.DEBUGGING, ModelCapability.REFACTORING],
            max_tokens=8192,
            context_length=128000,
            cost_per_token=0.00003,
            speed_rating=2,
            quality_rating=5,
            local_model=False,
            api_endpoint="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEY",
            enabled=True,
            priority=9
        )
        
        models["openrouter-claude3"] = ModelInfo(
            id="openrouter-claude3",
            name="Claude 3 Haiku (via OpenRouter)",
            provider=ProviderType.OPENROUTER,
            description="Anthropic's Claude 3 Haiku via OpenRouter - fast and efficient",
            capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION, ModelCapability.CODE_REVIEW],
            max_tokens=8192,
            context_length=200000,
            cost_per_token=0.00000025,
            speed_rating=4,
            quality_rating=4,
            local_model=False,
            api_endpoint="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEY",
            enabled=True,
            priority=8
        )
        
        models["huggingface-codellama"] = ModelInfo(
            id="huggingface-codellama",
            name="CodeLlama (Hugging Face)",
            provider=ProviderType.HUGGINGFACE,
            description="Meta's CodeLlama via Hugging Face Inference API",
            capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION],
            max_tokens=2048,
            context_length=16384,
            cost_per_token=0.000001,
            speed_rating=3,
            quality_rating=4,
            local_model=False,
            api_endpoint="https://api-inference.huggingface.co/models/codellama/CodeLlama-7b-Instruct-hf",
            api_key_env="HUGGINGFACE_API_KEY",
            enabled=True,
            priority=6
        )
        
        security = SecurityConfig(
            level=SecurityLevel.MODERATE,
            allowed_commands=["ls", "cat", "grep", "find", "head", "tail", "wc", "sort", "uniq"],
            blocked_commands=["rm -rf", "sudo", "chmod 777", "mkfs", "dd"],
            max_execution_time=60,
            require_approval_for=["git commit", "git push", "file delete", "command sudo"],
            sandbox_enabled=True,
            allowed_file_operations=["read", "write", "append"],
            git_operations_allowed=True,
            network_access=False
        )
        
        return AdvancedConfig(
            models=models,
            active_model="ollama-codellama",
            fallback_models=["ollama-phi3", "openrouter-claude3"],
            security=security,
            max_parallel_requests=3,
            request_timeout=30,
            retry_attempts=3,
            cache_enabled=True,
            cache_ttl=3600,
            theme="dark",
            color_scheme="monokai",
            enable_syntax_highlighting=True,
            show_timestamps=True,
            max_output_length=10000,
            auto_approve_safe=True,
            default_approval_mode="full",
            workflow_timeout=3600,
            max_workflow_steps=50,
            git_auto_commit=False,
            git_commit_message_template="Auto-commit by Sheikh-CLI: {description}",
            file_backup_enabled=True,
            backup_retention_days=30,
            enable_code_analysis=True,
            enable_security_scanning=True,
            enable_performance_monitoring=True,
            enable_audit_logging=True
        )
    
    def save_configuration(self):
        """Save configuration to file"""
        if not self.config:
            return
        
        try:
            # Create backup
            if self.config_file.exists():
                backup_file = self.backup_dir / f"config_backup_{int(os.path.getmtime(self.config_file))}.yaml"
                self.config_file.rename(backup_file)
            
            # Save current config
            with open(self.config_file, 'w') as f:
                yaml.dump(asdict(self.config), f, default_flow_style=False, indent=2)
            
            console.print("[green]✅ Configuration saved successfully[/green]")
        
        except Exception as e:
            console.print(f"[red]Failed to save configuration: {e}[/red]")
    
    def list_models(self):
        """List all configured models"""
        if not self.config or not self.config.models:
            console.print("[yellow]No models configured[/yellow]")
            return
        
        model_table = Table(title="🤖 Configured Models")
        model_table.add_column("ID", style="cyan")
        model_table.add_column("Name", style="magenta")
        model_table.add_column("Provider", style="green")
        model_table.add_column("Type", style="blue")
        model_table.add_column("Max Tokens", style="yellow")
        model_table.add_column("Rating", style="red")
        model_table.add_column("Status", style="dim")
        
        # Sort by priority
        sorted_models = sorted(
            self.config.models.values(),
            key=lambda x: (x.priority, -x.quality_rating),
            reverse=True
        )
        
        for model in sorted_models:
            model_type = "Local" if model.local_model else "API"
            rating = f"{model.quality_rating}/5"
            status = "Active" if model.id == self.config.active_model else ("Enabled" if model.enabled else "Disabled")
            
            status_style = "green" if model.id == self.config.active_model else ("yellow" if model.enabled else "red")
            
            model_table.add_row(
                model.id,
                model.name,
                model.provider.value,
                model_type,
                str(model.max_tokens),
                rating,
                f"[{status_style}]{status}[/{status_style}]"
            )
        
        console.print(model_table)
    
    def add_model(self, model_id: str, **kwargs):
        """Add a new model configuration"""
        if not self.config:
            self.config = self._create_default_config()
        
        try:
            capabilities = [ModelCapability(cap) for cap in kwargs.get('capabilities', [])]
            model = ModelInfo(
                id=model_id,
                name=kwargs['name'],
                provider=ProviderType(kwargs['provider']),
                description=kwargs['description'],
                capabilities=capabilities,
                max_tokens=kwargs.get('max_tokens', 4096),
                context_length=kwargs.get('context_length', 16384),
                cost_per_token=kwargs.get('cost_per_token', 0.0),
                speed_rating=kwargs.get('speed_rating', 3),
                quality_rating=kwargs.get('quality_rating', 3),
                local_model=kwargs.get('local_model', False),
                model_path=kwargs.get('model_path'),
                api_endpoint=kwargs.get('api_endpoint'),
                api_key_env=kwargs.get('api_key_env'),
                enabled=kwargs.get('enabled', True),
                priority=kwargs.get('priority', 0)
            )
            
            self.config.models[model_id] = model
            self.save_configuration()
            console.print(f"[green]✅ Added model: {model_id}[/green]")
        
        except Exception as e:
            console.print(f"[red]Failed to add model: {e}[/red]")
    
    def remove_model(self, model_id: str):
        """Remove a model configuration"""
        if not self.config or model_id not in self.config.models:
            console.print(f"[red]Model '{model_id}' not found[/red]")
            return
        
        if model_id == self.config.active_model:
            console.print("[yellow]Cannot remove active model. Switch to another model first.[/yellow]")
            return
        
        del self.config.models[model_id]
        self.save_configuration()
        console.print(f"[red]Removed model: {model_id}[/red]")
    
    def switch_model(self, model_id: str):
        """Switch active model"""
        if not self.config or model_id not in self.config.models:
            console.print(f"[red]Model '{model_id}' not found[/red]")
            return
        
        model = self.config.models[model_id]
        if not model.enabled:
            console.print(f"[yellow]Model '{model_id}' is disabled[/yellow]")
            return
        
        self.config.active_model = model_id
        self.save_configuration()
        console.print(f"[green]✅ Switched to model: {model.name}[/green]")
    
    def test_model(self, model_id: str):
        """Test a model's connectivity"""
        if not self.config or model_id not in self.config.models:
            console.print(f"[red]Model '{model_id}' not found[/red]")
            return
        
        model = self.config.models[model_id]
        console.print(f"[blue]Testing connection to {model.name}...[/blue]")
        
        try:
            if model.provider == ProviderType.LOCAL and model.api_endpoint:
                import requests
                response = requests.get(f"{model.api_endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    console.print("[green]✅ Connection successful[/green]")
                else:
                    console.print(f"[red]❌ Connection failed: HTTP {response.status_code}[/red]")
            elif model.provider in [ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.OPENROUTER, ProviderType.HUGGINGFACE]:
                # Check if API key is available
                if model.api_key_env:
                    api_key = os.getenv(model.api_key_env)
                    if api_key:
                        console.print("[green]✅ API key found[/green]")
                    else:
                        console.print(f"[yellow]⚠️ API key not found (expected in {model.api_key_env})[/yellow]")
                else:
                    console.print("[yellow]⚠️ No API key environment variable specified[/yellow]")
            else:
                console.print("[green]✅ Model configuration appears valid[/green]")
        
        except Exception as e:
            console.print(f"[red]❌ Connection test failed: {e}[/red]")
    
    def show_configuration(self):
        """Display current configuration"""
        if not self.config:
            console.print("[yellow]No configuration loaded[/yellow]")
            return
        
        # General settings
        general_panel = Panel(
            f"[bold]Active Model:[/bold] {self.config.active_model}\n"
            f"[bold]Fallback Models:[/bold] {', '.join(self.config.fallback_models)}\n"
            f"[bold]Parallel Requests:[/bold] {self.config.max_parallel_requests}\n"
            f"[bold]Request Timeout:[/bold] {self.config.request_timeout}s\n"
            f"[bold]Cache Enabled:[/bold] {self.config.cache_enabled}\n"
            f"[bold]Theme:[/bold] {self.config.theme}\n"
            f"[bold]Auto-approve Safe:[/bold] {self.config.auto_approve_safe}",
            title="⚙️ General Settings",
            border_style="blue"
        )
        console.print(general_panel)
        
        # Security settings
        security_panel = Panel(
            f"[bold]Security Level:[/bold] {self.config.security.level.value}\n"
            f"[bold]Sandbox Enabled:[/bold] {self.config.security.sandbox_enabled}\n"
            f"[bold]Max Execution Time:[/bold] {self.config.security.max_execution_time}s\n"
            f"[bold]Git Operations:[/bold] {'Allowed' if self.config.security.git_operations_allowed else 'Blocked'}\n"
            f"[bold]Network Access:[/bold] {'Enabled' if self.config.security.network_access else 'Disabled'}\n"
            f"[bold]Allowed Commands:[/bold] {len(self.config.security.allowed_commands)}\n"
            f"[bold]Blocked Commands:[/bold] {len(self.config.security.blocked_commands)}",
            title="🔒 Security Settings",
            border_style="yellow"
        )
        console.print(security_panel)
        
        # Model count summary
        total_models = len(self.config.models)
        enabled_models = sum(1 for model in self.config.models.values() if model.enabled)
        local_models = sum(1 for model in self.config.models.values() if model.local_model)
        
        summary_panel = Panel(
            f"[bold]Total Models:[/bold] {total_models}\n"
            f"[bold]Enabled Models:[/bold] {enabled_models}\n"
            f"[bold]Local Models:[/bold] {local_models}\n"
            f"[bold]API Models:[/bold] {total_models - local_models}",
            title="📊 Model Summary",
            border_style="green"
        )
        console.print(summary_panel)
    
    def export_configuration(self, output_path: Path):
        """Export configuration to a file"""
        if not self.config:
            console.print("[yellow]No configuration to export[/yellow]")
            return
        
        try:
            with open(output_path, 'w') as f:
                yaml.dump(asdict(self.config), f, default_flow_style=False, indent=2)
            console.print(f"[green]✅ Configuration exported to {output_path}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to export configuration: {e}[/red]")
    
    def import_configuration(self, input_path: Path):
        """Import configuration from a file"""
        try:
            with open(input_path, 'r') as f:
                data = yaml.safe_load(f)
            
            self.config = self._dict_to_config(data)
            self.save_configuration()
            console.print(f"[green]✅ Configuration imported from {input_path}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to import configuration: {e}[/red]")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._create_default_config()
        self.save_configuration()
        console.print("[green]✅ Configuration reset to defaults[/green]")
    
    def get_active_model_info(self) -> Optional[ModelInfo]:
        """Get information about the currently active model"""
        if not self.config or not self.config.active_model:
            return None
        
        return self.config.models.get(self.config.active_model)
    
    def get_model_by_capability(self, capability: ModelCapability) -> List[ModelInfo]:
        """Get models that support a specific capability"""
        if not self.config:
            return []
        
        return [
            model for model in self.config.models.values()
            if model.enabled and capability in model.capabilities
        ]
    
    def get_fallback_models(self) -> List[ModelInfo]:
        """Get fallback model information"""
        if not self.config:
            return []
        
        fallback_models = []
        for model_id in self.config.fallback_models:
            model = self.config.models.get(model_id)
            if model and model.enabled:
                fallback_models.append(model)
        
        return fallback_models

# Global configuration manager instance
config_manager = ConfigManager()