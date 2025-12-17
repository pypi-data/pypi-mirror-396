"""
Code Search Tool Plugin
Handles code pattern searching using ripgrep and other search utilities.
"""

import subprocess
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import shlex

class CodeSearch:
    """Code search and pattern matching utilities"""
    
    def __init__(self):
        # File extensions to search in
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
            '.java', '.kt', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rs',
            '.rb', '.php', '.swift', '.m', '.mm', '.sh', '.bash', '.zsh',
            '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'
        }
    
    def search_code(self, pattern: str, directory: str = None, recursive: bool = True, 
                   file_extensions: List[str] = None, case_sensitive: bool = False) -> str:
        """Search for patterns in code files"""
        if directory is None:
            directory = str(Path.home() / "coding-agent")
        
        if file_extensions is None:
            file_extensions = list(self.code_extensions)
        
        try:
            directory = Path(directory)
            if not directory.exists():
                return f"❌ Directory not found: {directory}"
            
            # Build grep command
            cmd_parts = ['grep', '-r', '--color=never', '--line-number']
            
            if recursive:
                cmd_parts.append('-R')
            
            if not case_sensitive:
                cmd_parts.append('-i')
            
            if file_extensions:
                for ext in file_extensions:
                    cmd_parts.extend(['--include', f'*{ext}'])
            
            cmd_parts.extend([shlex.quote(pattern), str(directory)])
            
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return f"🔍 Found {len(lines)} matches for '{pattern}':\n\n" + '\n'.join(lines)
            elif result.returncode == 1:
                return f"🔍 No matches found for '{pattern}' in {directory}"
            else:
                return f"❌ Search failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"⏰ Search timed out"
        except Exception as e:
            return f"❌ Error searching code: {str(e)}"
    
    def find_functions(self, directory: str = None, language: str = "python") -> str:
        """Find function definitions in code"""
        if directory is None:
            directory = str(Path.home() / "coding-agent")
        
        patterns = {
            "python": r'def\s+(\w+)\s*\(',
            "javascript": r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(|(\w+)\s*:\s*function\s*\(',
            "java": r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\(',
            "cpp": r'(public|private|protected)?\s*\w+\s+(\w+)\s*\(',
            "go": r'func\s+(\w+)\s*\(',
            "rust": r'fn\s+(\w+)\s*\('
        }
        
        if language not in patterns:
            return f"❌ Unsupported language: {language}"
        
        pattern = patterns[language]
        
        try:
            cmd_parts = ['grep', '-r', '--color=never', '--line-number', '--include=*.py', '--include=*.js', '--include=*.java', '--include=*.cpp', '--include=*.go', '--include=*.rs']
            cmd_parts.extend([shlex.quote(pattern), directory])
            
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                matches = []
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        matches.append(line)
                return f"🔍 Found {len(matches)} function definitions:\n\n" + '\n'.join(matches)
            else:
                return f"🔍 No function definitions found in {language}"
                
        except Exception as e:
            return f"❌ Error finding functions: {str(e)}"
    
    def search_imports(self, directory: str = None) -> str:
        """Find import/require statements in code"""
        if directory is None:
            directory = str(Path.home() / "coding-agent")
        
        import_patterns = [
            r'import\s+.*\s+from\s+["\']([^"\']+)["\']',
            r'import\s+["\']([^"\']+)["\']',
            r'require\(["\']([^"\']+)["\']\)',
            r'from\s+["\']([^"\']+)["\']\s+import',
            r'using\s+(\w+)',
            r'#include\s+[<"]([^>"]+)[>"]'
        ]
        
        results = []
        for pattern in import_patterns:
            try:
                cmd_parts = ['grep', '-r', '--color=never', '--line-number']
                cmd_parts.extend(['--include=*.py', '--include=*.js', '--include=*.java', '--include=*.cpp', '--include=*.h'])
                cmd_parts.extend([shlex.quote(pattern), directory])
                
                result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    results.extend(result.stdout.strip().split('\n'))
                    
            except Exception as e:
                continue
        
        if results:
            return f"📦 Found {len(results)} import statements:\n\n" + '\n'.join(results)
        else:
            return f"📦 No import statements found"
    
    def find_classes(self, directory: str = None, language: str = "python") -> str:
        """Find class definitions in code"""
        if directory is None:
            directory = str(Path.home() / "coding-agent")
        
        class_patterns = {
            "python": r'class\s+(\w+)',
            "javascript": r'class\s+(\w+)',
            "java": r'class\s+(\w+)',
            "cpp": r'class\s+(\w+)',
            "go": r'type\s+(\w+)\s+struct',
            "rust": r'struct\s+(\w+)'
        }
        
        if language not in class_patterns:
            return f"❌ Unsupported language: {language}"
        
        pattern = class_patterns[language]
        
        try:
            cmd_parts = ['grep', '-r', '--color=never', '--line-number']
            cmd_parts.extend(['--include=*.py', '--include=*.js', '--include=*.java', '--include=*.cpp', '--include=*.go', '--include=*.rs'])
            cmd_parts.extend([shlex.quote(pattern), directory])
            
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                matches = []
                for line in result.stdout.strip().split('\n'):
                    if ':' in line:
                        matches.append(line)
                return f"🏗️ Found {len(matches)} class definitions:\n\n" + '\n'.join(matches)
            else:
                return f"🏗️ No class definitions found in {language}"
                
        except Exception as e:
            return f"❌ Error finding classes: {str(e)}"
    
    def get_code_stats(self, directory: str = None) -> str:
        """Get basic code statistics"""
        if directory is None:
            directory = str(Path.home() / "coding-agent")
        
        try:
            # Count lines of code
            cmd_parts = ['find', directory, '-type', 'f', '-name', '*.py', '-o', '-name', '*.js', '-name', '*.java', '-o', '-name', '*.cpp']
            cmd_parts.append('|')
            cmd_parts.append('xargs')
            cmd_parts.append('wc')
            cmd_parts.append('-l')
            
            # Use a simpler approach
            find_result = subprocess.run(
                ['find', directory, '-type', 'f', '-name', '*.py'],
                capture_output=True, text=True, timeout=30
            )
            
            py_files = find_result.stdout.strip().split('\n') if find_result.stdout.strip() else []
            py_lines = 0
            
            for file_path in py_files:
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            py_lines += len(f.readlines())
                    except:
                        continue
            
            find_result = subprocess.run(
                ['find', directory, '-type', 'f', '-name', '*.js'],
                capture_output=True, text=True, timeout=30
            )
            
            js_files = find_result.stdout.strip().split('\n') if find_result.stdout.strip() else []
            js_lines = 0
            
            for file_path in js_files:
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            js_lines += len(f.readlines())
                    except:
                        continue
            
            return f"📊 Code Statistics:\n\n📝 Python files: {len(py_files)} ({py_lines} lines)\n📝 JavaScript files: {len(js_files)} ({js_lines} lines)\n📝 Total code lines: {py_lines + js_lines}"
            
        except Exception as e:
            return f"❌ Error getting code stats: {str(e)}"
