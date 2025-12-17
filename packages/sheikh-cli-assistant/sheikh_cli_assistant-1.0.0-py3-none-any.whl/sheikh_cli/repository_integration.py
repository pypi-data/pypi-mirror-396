"""
Advanced Repository Integration System for Sheikh-CLI
Provides AI-powered repository analysis, code review, and management capabilities.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .openrouter_ai import OpenRouterAI

class RepositoryIntegration:
    """Advanced repository integration with AI assistance"""
    
    def __init__(self, ai: OpenRouterAI):
        self.ai = ai
        self.repo_state = {}
        self.branches = []
        self.commits = []
        self.files_changed = []
        
    def detect_repository(self, directory: str = None) -> Dict[str, Any]:
        """Detect if directory is a git repository and get basic info"""
        if directory is None:
            directory = os.getcwd()
        
        repo_path = Path(directory) / ".git"
        if not repo_path.exists():
            return {"is_repository": False, "message": "Not a git repository"}
        
        try:
            # Get basic repository information
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            remotes = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            remotes.append({
                                'name': parts[0],
                                'url': parts[1].split(' ')[0]
                            })
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            return {
                "is_repository": True,
                "current_branch": current_branch,
                "remotes": remotes,
                "directory": directory
            }
            
        except Exception as e:
            return {"is_repository": False, "message": f"Error detecting repository: {str(e)}"}
    
    def analyze_repository_structure(self, directory: str = None) -> Dict[str, Any]:
        """Analyze repository structure and provide insights"""
        if directory is None:
            directory = os.getcwd()
        
        try:
            analysis = {
                "language_distribution": {},
                "file_types": {},
                "directory_structure": {},
                "complexity_score": 0,
                "main_files": []
            }
            
            # Analyze file types and languages
            for file_path in Path(directory).rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    extension = file_path.suffix.lower()
                    analysis["file_types"][extension] = analysis["file_types"].get(extension, 0) + 1
                    
                    # Map extensions to languages
                    language_map = {
                        '.py': 'Python',
                        '.js': 'JavaScript',
                        '.ts': 'TypeScript',
                        '.java': 'Java',
                        '.cpp': 'C++',
                        '.c': 'C',
                        '.h': 'C/C++ Header',
                        '.go': 'Go',
                        '.rs': 'Rust',
                        '.rb': 'Ruby',
                        '.php': 'PHP',
                        '.swift': 'Swift',
                        '.kt': 'Kotlin',
                        '.md': 'Markdown',
                        '.json': 'JSON',
                        '.yaml': 'YAML',
                        '.yml': 'YAML',
                        '.xml': 'XML',
                        '.html': 'HTML',
                        '.css': 'CSS',
                        '.scss': 'SCSS',
                        '.sass': 'SASS'
                    }
                    
                    language = language_map.get(extension, 'Other')
                    analysis["language_distribution"][language] = analysis["language_distribution"].get(language, 0) + 1
            
            # Find main files
            main_files = ['README.md', 'README.txt', 'package.json', 'requirements.txt', 
                         'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod', 'composer.json']
            
            for main_file in main_files:
                file_path = Path(directory) / main_file
                if file_path.exists():
                    analysis["main_files"].append(main_file)
            
            # Analyze directory structure
            dirs = [d for d in Path(directory).iterdir() if d.is_dir() and not d.name.startswith('.')]
            analysis["directory_structure"] = {d.name: "directory" for d in dirs[:10]}  # Top 10 dirs
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing repository: {str(e)}"}
    
    def get_recent_commits(self, count: int = 5) -> List[Dict[str, str]]:
        """Get recent commit information"""
        try:
            result = subprocess.run(
                ["git", "log", f"--oneline", f"-{count}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            commits = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            commits.append({
                                "hash": parts[0],
                                "message": parts[1]
                            })
            
            return commits
            
        except Exception as e:
            return [{"error": f"Error getting commits: {str(e)}"}]
    
    def get_uncommitted_changes(self) -> Dict[str, Any]:
        """Get information about uncommitted changes"""
        try:
            # Get git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            changes = {
                "modified": [],
                "added": [],
                "deleted": [],
                "untracked": []
            }
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status = line[:2]
                        filename = line[3:]
                        
                        if status == " M":
                            changes["modified"].append(filename)
                        elif status == "A ":
                            changes["added"].append(filename)
                        elif status == " D":
                            changes["deleted"].append(filename)
                        elif status == "??":
                            changes["untracked"].append(filename)
            
            return changes
            
        except Exception as e:
            return {"error": f"Error getting changes: {str(e)}"}
    
    def generate_ai_repository_summary(self, directory: str = None) -> str:
        """Generate AI-powered repository summary"""
        if directory is None:
            directory = os.getcwd()
        
        if not self.ai.is_available():
            return "AI not available for repository analysis"
        
        # Get repository information
        repo_info = self.detect_repository(directory)
        if not repo_info["is_repository"]:
            return f"❌ {repo_info['message']}"
        
        structure = self.analyze_repository_structure(directory)
        commits = self.get_recent_commits(3)
        changes = self.get_uncommitted_changes()
        
        # Prepare context for AI
        context = f"""
Repository Analysis Request:

Repository Information:
- Current Branch: {repo_info.get('current_branch', 'unknown')}
- Remotes: {len(repo_info.get('remotes', []))}
- Directory: {directory}

Language Distribution:
{json.dumps(structure.get('language_distribution', {}), indent=2)}

Recent Commits (last 3):
{chr(10).join([f"- {c.get('hash', '')[:7]}: {c.get('message', '')}" for c in commits])}

Uncommitted Changes:
- Modified: {len(changes.get('modified', []))} files
- Added: {len(changes.get('added', []))} files
- Deleted: {len(changes.get('deleted', []))} files
- Untracked: {len(changes.get('untracked', []))} files

Please provide:
1. Repository overview and purpose
2. Code quality assessment
3. Development activity analysis
4. Recommendations for improvement
"""
        
        try:
            result = self.ai.chat_completion(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert software engineer analyzing repositories. Provide detailed, actionable insights about the codebase."},
                    {"role": "user", "content": context}
                ]
            )
            
            if "error" in result:
                return f"❌ AI Error: {result['error']}"
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"❌ Error generating repository summary: {str(e)}"
    
    def ai_code_review(self, files: List[str] = None, directory: str = None) -> str:
        """Perform AI-powered code review"""
        if directory is None:
            directory = os.getcwd()
        
        if not self.ai.is_available():
            return "AI not available for code review"
        
        review_context = f"""
Perform a comprehensive code review for the repository at: {directory}

"""
        
        if files:
            review_context += f"Focus on these specific files: {', '.join(files)}\n\n"
        
        # Add repository context
        repo_info = self.detect_repository(directory)
        if repo_info["is_repository"]:
            review_context += f"Current branch: {repo_info['current_branch']}\n"
            
            changes = self.get_uncommitted_changes()
            if any(changes.values()):
                review_context += "\nUncommitted changes detected:\n"
                for change_type, file_list in changes.items():
                    if file_list:
                        review_context += f"- {change_type.title()}: {', '.join(file_list[:5])}\n"
        
        review_context += """
Please provide a detailed code review covering:

1. **Code Quality**: Identify potential bugs, security issues, and performance problems
2. **Best Practices**: Check adherence to coding standards and best practices
3. **Architecture**: Evaluate code organization and design patterns
4. **Documentation**: Assess code documentation and comments
5. **Testing**: Review test coverage and quality
6. **Recommendations**: Provide specific, actionable improvement suggestions

Format your response with clear sections and bullet points for easy reading.
"""
        
        try:
            result = self.ai.chat_completion(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced senior software engineer and code reviewer. Provide thorough, constructive feedback that helps developers improve their code."},
                    {"role": "user", "content": review_context}
                ]
            )
            
            if "error" in result:
                return f"❌ AI Error: {result['error']}"
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"❌ Error performing code review: {str(e)}"
    
    def suggest_git_workflow(self, directory: str = None) -> str:
        """Suggest Git workflow based on repository analysis"""
        if directory is None:
            directory = os.getcwd()
        
        if not self.ai.is_available():
            return "AI not available for workflow suggestions"
        
        repo_info = self.detect_repository(directory)
        if not repo_info["is_repository"]:
            return f"❌ {repo_info['message']}"
        
        structure = self.analyze_repository_structure(directory)
        
        context = f"""
Analyze this repository and suggest an optimal Git workflow:

Repository: {directory}
Current Branch: {repo_info.get('current_branch', 'unknown')}

Project Characteristics:
- Primary Language: {max(structure.get('language_distribution', {}).items(), key=lambda x: x[1])[0] if structure.get('language_distribution') else 'Unknown'}
- File Types: {list(structure.get('file_types', {}).keys())[:10]}
- Has README: {'README.md' in structure.get('main_files', [])}

Please suggest:
1. Optimal branching strategy (GitFlow, GitHub Flow, etc.)
2. Commit message conventions
3. Code review process
4. Release management approach
5. CI/CD integration recommendations

Consider the project type and size based on the repository analysis.
"""
        
        try:
            result = self.ai.chat_completion(
                model="openai/gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a DevOps and Git workflow expert. Provide practical, tailored recommendations for Git workflows based on project characteristics."},
                    {"role": "user", "content": context}
                ]
            )
            
            if "error" in result:
                return f"❌ AI Error: {result['error']}"
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"❌ Error generating workflow suggestions: {str(e)}"
