"""
Advanced Workflow Orchestration System for Sheikh-CLI
Handles complex workflow automation, approval systems, and task management
"""

import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
import uuid

console = Console()

class ApprovalMode(Enum):
    """Approval modes for workflow execution"""
    AUTO = "auto"           # Execute without approval
    READ_ONLY = "readonly"  # Only safe read operations
    FULL = "full"           # Full access with approval
    CUSTOM = "custom"       # Custom approval rules

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    id: str
    name: str
    description: str
    action_type: str  # "command", "ai_task", "file_operation", "git_operation"
    command: Optional[str] = None
    ai_prompt: Optional[str] = None
    file_path: Optional[str] = None
    file_operation: Optional[str] = None  # "read", "write", "delete", "modify"
    git_operation: Optional[str] = None   # "status", "commit", "push", "pull"
    approval_required: bool = False
    timeout: int = 60
    retries: int = 1
    conditions: Dict[str, Any] = None
    environment: Dict[str, str] = None
    output_capture: bool = True
    continue_on_error: bool = False

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    id: str
    name: str
    description: str
    category: str  # "development", "deployment", "maintenance", "testing"
    version: str
    steps: List[WorkflowStep]
    approval_mode: ApprovalMode = ApprovalMode.FULL
    parallel_execution: bool = False
    max_parallel_steps: int = 3
    timeout: int = 3600
    tags: List[str] = None
    created_at: datetime = None
    author: str = "sheikh-cli"

@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_step: int = 0
    step_results: Dict[str, Any] = None
    error_message: Optional[str] = None
    approval_log: List[Dict[str, Any]] = None

class WorkflowOrchestrator:
    """Advanced workflow orchestration with approval systems"""
    
    def __init__(self, workflows_dir: Optional[Path] = None):
        self.workflows_dir = workflows_dir or Path.home() / ".sheikh-workflows"
        self.workflows_dir.mkdir(exist_ok=True)
        self.executions_dir = self.workflows_dir / "executions"
        self.executions_dir.mkdir(exist_ok=True)
        
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.approval_callbacks: Dict[str, Callable] = {}
        
        self.load_workflows()
        self.register_default_workflows()
    
    def load_workflows(self):
        """Load workflows from disk"""
        for workflow_file in self.workflows_dir.glob("*.yaml"):
            try:
                with open(workflow_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                workflow = self._dict_to_workflow(data)
                self.workflows[workflow.id] = workflow
            except Exception as e:
                console.print(f"[red]Failed to load workflow {workflow_file}: {e}[/red]")
    
    def _dict_to_workflow(self, data: Dict) -> WorkflowDefinition:
        """Convert dictionary to WorkflowDefinition"""
        # Convert steps
        steps = []
        for step_data in data.get('steps', []):
            step = WorkflowStep(
                id=step_data['id'],
                name=step_data['name'],
                description=step_data['description'],
                action_type=step_data['action_type'],
                **{k: v for k, v in step_data.items() if k not in ['id', 'name', 'description', 'action_type']}
            )
            steps.append(step)
        
        # Convert approval mode
        approval_mode = ApprovalMode(data.get('approval_mode', 'full'))
        
        return WorkflowDefinition(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            category=data.get('category', 'development'),
            version=data.get('version', '1.0.0'),
            steps=steps,
            approval_mode=approval_mode,
            parallel_execution=data.get('parallel_execution', False),
            max_parallel_steps=data.get('max_parallel_steps', 3),
            timeout=data.get('timeout', 3600),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data.get('created_at', datetime.now().isoformat())),
            author=data.get('author', 'sheikh-cli')
        )
    
    def register_default_workflows(self):
        """Register built-in workflow templates"""
        default_workflows = [
            self._create_code_review_workflow(),
            self._create_deployment_workflow(),
            self._create_testing_workflow(),
            self._create_refactoring_workflow(),
            self._create_security_audit_workflow(),
            self._create_backup_workflow()
        ]
        
        for workflow in default_workflows:
            if workflow.id not in self.workflows:
                self.workflows[workflow.id] = workflow
    
    def _create_code_review_workflow(self) -> WorkflowDefinition:
        """Create code review workflow"""
        steps = [
            WorkflowStep(
                id="git_status",
                name="Check Git Status",
                description="Check current git repository status",
                action_type="git_operation",
                git_operation="status",
                approval_required=False
            ),
            WorkflowStep(
                id="find_issues",
                name="Find Code Issues",
                description="Search for potential code issues",
                action_type="ai_task",
                ai_prompt="Analyze the codebase for potential issues, bugs, security vulnerabilities, and code quality problems. Provide specific recommendations.",
                approval_required=False
            ),
            WorkflowStep(
                id="generate_report",
                name="Generate Review Report",
                description="Create a comprehensive code review report",
                action_type="ai_task",
                ai_prompt="Generate a detailed code review report with findings, recommendations, and action items.",
                approval_required=True,
                output_capture=True
            )
        ]
        
        return WorkflowDefinition(
            id="code-review",
            name="Code Review",
            description="Comprehensive automated code review workflow",
            category="development",
            version="1.0.0",
            steps=steps,
            approval_mode=ApprovalMode.READ_ONLY,
            tags=["code-review", "quality", "security"]
        )
    
    def _create_deployment_workflow(self) -> WorkflowDefinition:
        """Create deployment workflow"""
        steps = [
            WorkflowStep(
                id="run_tests",
                name="Run Tests",
                description="Execute test suite",
                action_type="command",
                command="python -m pytest",
                approval_required=False
            ),
            WorkflowStep(
                id="build_package",
                name="Build Package",
                description="Build distribution package",
                action_type="command",
                command="python -m build",
                approval_required=False
            ),
            WorkflowStep(
                id="deploy",
                name="Deploy Application",
                description="Deploy to production environment",
                action_type="command",
                command="deploy-command",
                approval_required=True
            )
        ]
        
        return WorkflowDefinition(
            id="deployment",
            name="Deployment",
            description="Automated deployment workflow with testing",
            category="deployment",
            version="1.0.0",
            steps=steps,
            approval_mode=ApprovalMode.FULL,
            tags=["deployment", "production", "testing"]
        )
    
    def _create_testing_workflow(self) -> WorkflowDefinition:
        """Create testing workflow"""
        steps = [
            WorkflowStep(
                id="unit_tests",
                name="Run Unit Tests",
                description="Execute unit test suite",
                action_type="command",
                command="python -m pytest tests/unit",
                approval_required=False
            ),
            WorkflowStep(
                id="integration_tests",
                name="Run Integration Tests",
                description="Execute integration test suite",
                action_type="command",
                command="python -m pytest tests/integration",
                approval_required=False
            ),
            WorkflowStep(
                id="generate_coverage",
                name="Generate Coverage Report",
                description="Generate test coverage report",
                action_type="command",
                command="python -m pytest --cov=src --cov-report=html",
                approval_required=False
            )
        ]
        
        return WorkflowDefinition(
            id="testing",
            name="Testing Suite",
            description="Comprehensive testing workflow",
            category="testing",
            version="1.0.0",
            steps=steps,
            approval_mode=ApprovalMode.AUTO,
            tags=["testing", "quality", "coverage"]
        )
    
    def _create_refactoring_workflow(self) -> WorkflowDefinition:
        """Create refactoring workflow"""
        steps = [
            WorkflowStep(
                id="analyze_codebase",
                name="Analyze Codebase",
                description="Analyze codebase for refactoring opportunities",
                action_type="ai_task",
                ai_prompt="Analyze the codebase and identify refactoring opportunities including code duplication, long methods, complex functions, and architectural improvements.",
                approval_required=False
            ),
            WorkflowStep(
                id="generate_refactor_plan",
                name="Generate Refactoring Plan",
                description="Create detailed refactoring plan",
                action_type="ai_task",
                ai_prompt="Create a detailed refactoring plan with prioritized improvements and implementation steps.",
                approval_required=True
            ),
            WorkflowStep(
                id="implement_refactoring",
                name="Implement Refactoring",
                description="Execute refactoring plan",
                action_type="ai_task",
                ai_prompt="Implement the refactoring plan step by step, ensuring code quality and functionality are maintained.",
                approval_required=True
            )
        ]
        
        return WorkflowDefinition(
            id="refactoring",
            name="Code Refactoring",
            description="Automated refactoring workflow with AI assistance",
            category="development",
            version="1.0.0",
            steps=steps,
            approval_mode=ApprovalMode.FULL,
            tags=["refactoring", "maintenance", "quality"]
        )
    
    def _create_security_audit_workflow(self) -> WorkflowDefinition:
        """Create security audit workflow"""
        steps = [
            WorkflowStep(
                id="scan_dependencies",
                name="Scan Dependencies",
                description="Scan for vulnerable dependencies",
                action_type="command",
                command="safety check",
                approval_required=False
            ),
            WorkflowStep(
                id="analyze_security",
                name="Security Analysis",
                description="Perform comprehensive security analysis",
                action_type="ai_task",
                ai_prompt="Analyze the codebase for security vulnerabilities, insecure practices, and potential attack vectors. Focus on input validation, authentication, authorization, and data protection.",
                approval_required=False
            ),
            WorkflowStep(
                id="generate_security_report",
                name="Security Report",
                description="Generate detailed security report",
                action_type="ai_task",
                ai_prompt="Generate a comprehensive security audit report with findings, risk levels, and remediation recommendations.",
                approval_required=True
            )
        ]
        
        return WorkflowDefinition(
            id="security-audit",
            name="Security Audit",
            description="Comprehensive security audit workflow",
            category="security",
            version="1.0.0",
            steps=steps,
            approval_mode=ApprovalMode.READ_ONLY,
            tags=["security", "audit", "vulnerability"]
        )
    
    def _create_backup_workflow(self) -> WorkflowDefinition:
        """Create backup workflow"""
        steps = [
            WorkflowStep(
                id="create_backup",
                name="Create Backup",
                description="Create timestamped backup",
                action_type="command",
                command="backup-command",
                approval_required=False
            ),
            WorkflowStep(
                id="verify_backup",
                name="Verify Backup",
                description="Verify backup integrity",
                action_type="command",
                command="verify-backup-command",
                approval_required=False
            ),
            WorkflowStep(
                id="cleanup_old_backups",
                name="Cleanup Old Backups",
                description="Clean up old backup files",
                action_type="command",
                command="cleanup-backups-command",
                approval_required=False
            )
        ]
        
        return WorkflowDefinition(
            id="backup",
            name="Backup Workflow",
            description="Automated backup and cleanup workflow",
            category="maintenance",
            version="1.0.0",
            steps=steps,
            approval_mode=ApprovalMode.AUTO,
            tags=["backup", "maintenance", "safety"]
        )
    
    def list_workflows(self, category: Optional[str] = None):
        """List available workflows"""
        if not self.workflows:
            console.print("[yellow]No workflows available[/yellow]")
            return
        
        # Filter by category if specified
        filtered_workflows = self.workflows
        if category:
            filtered_workflows = {k: v for k, v in self.workflows.items() if v.category == category}
        
        if not filtered_workflows:
            console.print(f"[yellow]No workflows found for category: {category}[/yellow]")
            return
        
        workflow_table = Table(title="🔄 Available Workflows")
        workflow_table.add_column("ID", style="cyan")
        workflow_table.add_column("Name", style="magenta")
        workflow_table.add_column("Category", style="green")
        workflow_table.add_column("Steps", style="blue")
        workflow_table.add_column("Approval Mode", style="yellow")
        workflow_table.add_column("Tags", style="dim")
        
        for workflow in filtered_workflows.values():
            tags_str = ", ".join(workflow.tags) if workflow.tags else "None"
            workflow_table.add_row(
                workflow.id,
                workflow.name,
                workflow.category,
                str(len(workflow.steps)),
                workflow.approval_mode.value,
                tags_str
            )
        
        console.print(workflow_table)
    
    def show_workflow_details(self, workflow_id: str):
        """Show detailed information about a workflow"""
        if workflow_id not in self.workflows:
            console.print(f"[red]Workflow '{workflow_id}' not found[/red]")
            return
        
        workflow = self.workflows[workflow_id]
        
        # Main info panel
        created_time = workflow.created_at.strftime('%Y-%m-%d %H:%M:%S') if workflow.created_at else "Unknown"
        info_panel = Panel(
            f"[bold]Description:[/bold] {workflow.description}\n"
            f"[bold]Category:[/bold] {workflow.category}\n"
            f"[bold]Version:[/bold] {workflow.version}\n"
            f"[bold]Author:[/bold] {workflow.author}\n"
            f"[bold]Created:[/bold] {created_time}\n"
            f"[bold]Approval Mode:[/bold] {workflow.approval_mode.value}\n"
            f"[bold]Parallel Execution:[/bold] {workflow.parallel_execution}\n"
            f"[bold]Timeout:[/bold] {workflow.timeout}s",
            title=f"📋 {workflow.name}",
            border_style="blue"
        )
        console.print(info_panel)
        
        # Steps table
        steps_table = Table(title="🔧 Workflow Steps")
        steps_table.add_column("Step", style="cyan")
        steps_table.add_column("Name", style="magenta")
        steps_table.add_column("Action", style="green")
        steps_table.add_column("Description", style="blue")
        steps_table.add_column("Approval", style="yellow")
        
        for step in workflow.steps:
            approval_str = "Required" if step.approval_required else "Auto"
            steps_table.add_row(
                step.id,
                step.name,
                step.action_type,
                step.description,
                approval_str
            )
        
        console.print(steps_table)
    
    async def execute_workflow(self, workflow_id: str, params: Dict[str, Any] = None, auto_approve: bool = False):
        """Execute a workflow with approval handling"""
        if workflow_id not in self.workflows:
            console.print(f"[red]Workflow '{workflow_id}' not found[/red]")
            return
        
        workflow = self.workflows[workflow_id]
        execution_id = f"{workflow_id}_{uuid.uuid4().hex[:8]}"
        
        console.print(f"[bold blue]🚀 Starting workflow: {workflow.name}[/bold blue]")
        console.print(f"[dim]{workflow.description}[/dim]")
        
        # Create execution tracking
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            started_at=datetime.now(),
            step_results={},
            approval_log=[]
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            execution.status = WorkflowStatus.RUNNING
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Execute steps
                for i, step in enumerate(workflow.steps):
                    execution.current_step = i
                    task = progress.add_task(f"Executing: {step.name}", total=None)
                    
                    # Handle approval if required
                    if step.approval_required and not auto_approve:
                        if not await self._request_approval(step, execution):
                            execution.status = WorkflowStatus.CANCELLED
                            console.print(f"[yellow]Workflow cancelled by user at step: {step.name}[/yellow]")
                            break
                    
                    # Execute step
                    try:
                        result = await self._execute_step(step, params or {}, execution)
                        execution.step_results[step.id] = result
                        progress.update(task, description=f"✅ {step.name}")
                        
                        if not result.get("success", True):
                            if not step.continue_on_error:
                                execution.status = WorkflowStatus.FAILED
                                execution.error_message = result.get("error", "Step failed")
                                break
                    except Exception as e:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = str(e)
                        console.print(f"[red]Step '{step.name}' failed: {e}[/red]")
                        if not step.continue_on_error:
                            break
            
            # Finalize execution
            execution.completed_at = datetime.now()
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
            
            self._save_execution(execution)
            
            # Display results
            self._display_execution_results(execution)
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            console.print(f"[red]Workflow execution failed: {e}[/red]")
        
        finally:
            # Remove from active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _request_approval(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Request user approval for a workflow step"""
        approval_info = {
            "timestamp": datetime.now().isoformat(),
            "step_id": step.id,
            "step_name": step.name,
            "action_type": step.action_type,
            "description": step.description
        }
        
        console.print(f"\n[bold yellow]⚠️  Approval Required[/bold yellow]")
        console.print(f"Step: {step.name}")
        console.print(f"Action: {step.action_type}")
        console.print(f"Description: {step.description}")
        
        if step.action_type == "command" and step.command:
            console.print(f"Command: [cyan]{step.command}[/cyan]")
        elif step.action_type == "ai_task" and step.ai_prompt:
            console.print(f"AI Prompt: [dim]{step.ai_prompt[:100]}...[/dim]")
        elif step.action_type == "file_operation" and step.file_path:
            console.print(f"File: [cyan]{step.file_path}[/cyan]")
            console.print(f"Operation: [cyan]{step.file_operation}[/cyan]")
        
        # Log approval request
        execution.approval_log.append(approval_info)
        
        # Request approval
        approved = Confirm.ask("\nApprove this step?")
        approval_info["approved"] = approved
        approval_info["decision_time"] = datetime.now().isoformat()
        
        if not approved:
            console.print("[red]Step not approved - workflow will continue to next step if allowed[/red]")
        
        return approved
    
    async def _execute_step(self, step: WorkflowStep, params: Dict[str, Any], execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute an individual workflow step"""
        result = {"success": True, "output": "", "error": None, "timestamp": datetime.now().isoformat()}
        
        try:
            if step.action_type == "command":
                result = await self._execute_command_step(step, params)
            elif step.action_type == "ai_task":
                result = await self._execute_ai_task_step(step, params)
            elif step.action_type == "file_operation":
                result = await self._execute_file_operation_step(step, params)
            elif step.action_type == "git_operation":
                result = await self._execute_git_operation_step(step, params)
            else:
                result["error"] = f"Unknown action type: {step.action_type}"
                result["success"] = False
        
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    async def _execute_command_step(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command step"""
        import subprocess
        import os
        
        command = step.command
        if not command:
            return {"success": False, "error": "No command specified"}
        
        # Replace parameters in command
        for key, value in params.items():
            command = command.replace(f"{{{key}}}", str(value))
        
        console.print(f"[blue]Executing command: {command}[/blue]")
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **(step.environment or {})}
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=step.timeout
            )
            
            output = stdout.decode() + stderr.decode()
            
            return {
                "success": process.returncode == 0,
                "output": output,
                "return_code": process.returncode,
                "command": command
            }
        
        except asyncio.TimeoutError:
            return {"success": False, "error": f"Command timed out after {step.timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_ai_task_step(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI task step"""
        if not step.ai_prompt:
            return {"success": False, "error": "No AI prompt specified"}
        
        # This would integrate with the AI service
        # For now, return a placeholder response
        console.print(f"[blue]AI Task: {step.ai_prompt[:100]}...[/blue]")
        
        # Simulate AI processing
        await asyncio.sleep(2)
        
        return {
            "success": True,
            "output": f"AI task completed for: {step.ai_prompt}",
            "prompt": step.ai_prompt
        }
    
    async def _execute_file_operation_step(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a file operation step"""
        if not step.file_path or not step.file_operation:
            return {"success": False, "error": "File path or operation not specified"}
        
        file_path = Path(step.file_path)
        console.print(f"[blue]File Operation: {step.file_operation} {file_path}[/blue]")
        
        try:
            if step.file_operation == "read":
                if not file_path.exists():
                    return {"success": False, "error": f"File not found: {file_path}"}
                
                content = file_path.read_text()
                return {"success": True, "output": content, "operation": "read"}
            
            elif step.file_operation == "write":
                content = params.get("content", "")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                return {"success": True, "output": f"Written to {file_path}", "operation": "write"}
            
            elif step.file_operation == "delete":
                if file_path.exists():
                    file_path.unlink()
                    return {"success": True, "output": f"Deleted {file_path}", "operation": "delete"}
                else:
                    return {"success": False, "error": f"File not found: {file_path}"}
            
            else:
                return {"success": False, "error": f"Unknown file operation: {step.file_operation}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_git_operation_step(self, step: WorkflowStep, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a git operation step"""
        if not step.git_operation:
            return {"success": False, "error": "Git operation not specified"}
        
        console.print(f"[blue]Git Operation: {step.git_operation}[/blue]")
        
        # This would integrate with git operations
        # For now, return a placeholder response
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "output": f"Git operation '{step.git_operation}' completed",
            "operation": step.git_operation
        }
    
    def _save_execution(self, execution: WorkflowExecution):
        """Save execution to disk"""
        execution_file = self.executions_dir / f"{execution.execution_id}.json"
        
        try:
            data = asdict(execution)
            # Convert datetime objects to ISO format
            data['started_at'] = execution.started_at.isoformat()
            if execution.completed_at:
                data['completed_at'] = execution.completed_at.isoformat()
            
            with open(execution_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Failed to save execution: {e}[/red]")
    
    def _display_execution_results(self, execution: WorkflowExecution):
        """Display execution results"""
        status_color = {
            WorkflowStatus.COMPLETED: "green",
            WorkflowStatus.FAILED: "red",
            WorkflowStatus.CANCELLED: "yellow",
            WorkflowStatus.PENDING: "blue",
            WorkflowStatus.RUNNING: "blue"
        }
        
        color = status_color.get(execution.status, "white")
        
        # Summary panel
        summary_panel = Panel(
            f"[bold]Execution ID:[/bold] {execution.execution_id}\n"
            f"[bold]Status:[/bold] [{color}]{execution.status.value}[/{color}]\n"
            f"[bold]Started:[/bold] {execution.started_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Completed:[/bold] {execution.completed_at.strftime('%Y-%m-%d %H:%M:%S') if execution.completed_at else 'N/A'}\n"
            f"[bold]Current Step:[/bold] {execution.current_step + 1}/{len(self.workflows[execution.workflow_id].steps)}\n"
            f"[bold]Error:[/bold] {execution.error_message if execution.error_message else 'None'}",
            title="📊 Execution Summary",
            border_style=color
        )
        console.print(summary_panel)
        
        # Step results
        if execution.step_results:
            results_table = Table(title="🔍 Step Results")
            results_table.add_column("Step", style="cyan")
            results_table.add_column("Status", style="magenta")
            results_table.add_column("Output", style="green")
            results_table.add_column("Error", style="red")
            
            for step_id, result in execution.step_results.items():
                step = next((s for s in self.workflows[execution.workflow_id].steps if s.id == step_id), None)
                step_name = step.name if step else step_id
                
                status = "✅ Success" if result.get("success") else "❌ Failed"
                status_style = "green" if result.get("success") else "red"
                
                output_preview = result.get("output", "")[:100]
                if len(result.get("output", "")) > 100:
                    output_preview += "..."
                
                error = result.get("error", "")[:100]
                if len(result.get("error", "")) > 100:
                    error += "..."
                
                results_table.add_row(
                    step_name,
                    f"[{status_style}]{status}[/{status_style}]",
                    output_preview or "N/A",
                    error or "N/A"
                )
            
            console.print(results_table)
    
    def list_executions(self, limit: int = 10):
        """List recent workflow executions"""
        executions = []
        
        for execution_file in self.executions_dir.glob("*.json"):
            try:
                with open(execution_file, 'r') as f:
                    data = json.load(f)
                    executions.append(data)
            except:
                continue
        
        # Sort by start time, most recent first
        executions.sort(key=lambda x: x['started_at'], reverse=True)
        executions = executions[:limit]
        
        if not executions:
            console.print("[yellow]No executions found[/yellow]")
            return
        
        execution_table = Table(title="📜 Recent Executions")
        execution_table.add_column("Execution ID", style="cyan")
        execution_table.add_column("Workflow", style="magenta")
        execution_table.add_column("Status", style="green")
        execution_table.add_column("Started", style="blue")
        execution_table.add_column("Duration", style="yellow")
        
        for exec_data in executions:
            status_color = {
                "completed": "green",
                "failed": "red",
                "cancelled": "yellow",
                "pending": "blue",
                "running": "blue"
            }
            color = status_color.get(exec_data['status'], 'white')
            
            # Calculate duration
            started = datetime.fromisoformat(exec_data['started_at'])
            completed = datetime.fromisoformat(exec_data['completed_at']) if exec_data.get('completed_at') else datetime.now()
            duration = completed - started
            
            execution_table.add_row(
                exec_data['execution_id'],
                exec_data['workflow_id'],
                f"[{color}]{exec_data['status']}[/{color}]",
                started.strftime('%H:%M:%S'),
                f"{duration.total_seconds():.1f}s"
            )
        
        console.print(execution_table)

# Global orchestrator instance
workflow_orchestrator = WorkflowOrchestrator()