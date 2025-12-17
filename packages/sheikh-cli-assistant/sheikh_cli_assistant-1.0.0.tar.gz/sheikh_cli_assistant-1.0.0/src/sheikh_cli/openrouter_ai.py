"""
OpenRouter AI Integration for Sheikh-CLI
Enhanced AI capabilities using OpenRouter's unified API
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

class OpenRouterAI:
    """OpenRouter API integration for enhanced AI capabilities"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
    def is_available(self) -> bool:
        """Check if OpenRouter integration is available"""
        return self.api_key is not None and requests is not None
    
    def chat_completion(self, model: str = "openai/gpt-4o", messages: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send chat completion request to OpenRouter"""
        if not self.is_available():
            return {"error": "OpenRouter integration not available"}
        
        if messages is None:
            messages = [{"role": "user", "content": "Hello"}]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/osamabinlikhon/sheikh-cli",
            "X-Title": "Sheikh-CLI",
        }
        
        data = {
            "model": model,
            "messages": messages
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def detect_intent(self, prompt: str) -> Dict[str, Any]:
        """Enhanced intent detection using OpenRouter AI"""
        if not self.is_available():
            return self._fallback_intent_detection(prompt)
        
        system_prompt = """
You are an AI assistant that analyzes user prompts for a coding agent.
Classify the user's intent and return a JSON response with the following structure:

{
  "action": "read_file|write_file|search_code|run_shell|git_status|git_diff|list_files|find_files|help",
  "confidence": 0.8,
  "parameters": {
    "file_path": "optional file path",
    "content": "optional content to write",
    "pattern": "optional search pattern",
    "command": "optional shell command"
  },
  "explanation": "Brief explanation of the detected intent"
}

Available actions:
- read_file: Read contents of a file
- write_file: Create or write to a file
- search_code: Search for patterns in code
- run_shell: Execute shell commands
- git_status: Show git repository status
- git_diff: Show git changes
- list_files: List directory contents
- find_files: Find files by pattern
- help: Show help information

Analyze this user prompt and respond with the JSON only.
"""
        
        user_prompt = f"User prompt: {prompt}"
        
        result = self.chat_completion(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        if "error" in result:
            return self._fallback_intent_detection(prompt)
        
        try:
            # Extract the response content
            content = result["choices"][0]["message"]["content"]
            # Parse JSON response
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return self._fallback_intent_detection(prompt)
    
    def _fallback_intent_detection(self, prompt: str) -> Dict[str, Any]:
        """Fallback intent detection using simple patterns"""
        prompt_lower = prompt.lower()
        
        if "read" in prompt_lower and any(ext in prompt_lower for ext in [".py", ".js", ".md", ".txt"]):
            return {
                "action": "read_file",
                "confidence": 0.7,
                "parameters": {"file_path": self._extract_file_path(prompt)},
                "explanation": "Detected file reading intent"
            }
        elif "write" in prompt_lower or "create" in prompt_lower:
            return {
                "action": "write_file",
                "confidence": 0.7,
                "parameters": {"content": self._extract_content(prompt)},
                "explanation": "Detected file writing intent"
            }
        elif "search" in prompt_lower or "find" in prompt_lower:
            return {
                "action": "search_code",
                "confidence": 0.7,
                "parameters": {"pattern": self._extract_search_pattern(prompt)},
                "explanation": "Detected code search intent"
            }
        elif "git" in prompt_lower:
            if "status" in prompt_lower:
                return {"action": "git_status", "confidence": 0.9, "parameters": {}, "explanation": "Detected git status intent"}
            elif "diff" in prompt_lower:
                return {"action": "git_diff", "confidence": 0.9, "parameters": {}, "explanation": "Detected git diff intent"}
        elif "list" in prompt_lower or "show" in prompt_lower:
            return {
                "action": "list_files",
                "confidence": 0.7,
                "parameters": {"directory": self._extract_directory(prompt)},
                "explanation": "Detected file listing intent"
            }
        else:
            return {
                "action": "run_shell",
                "confidence": 0.6,
                "parameters": {"command": prompt},
                "explanation": "Detected shell command intent"
            }
    
    def _extract_file_path(self, prompt: str) -> str:
        """Extract file path from prompt"""
        words = prompt.split()
        for word in words:
            if "." in word and len(word) > 2:
                return word
        return str(Path.home() / "coding-agent")
    
    def _extract_content(self, prompt: str) -> str:
        """Extract content to write from prompt"""
        if "create" in prompt.lower():
            return f"# Generated content for: {prompt}\n\n"
        return f"# Content for: {prompt}\n\n"
    
    def _extract_search_pattern(self, prompt: str) -> str:
        """Extract search pattern from prompt"""
        words = prompt.lower().replace("search", "").replace("find", "").replace("for", "").strip().split()
        return " ".join(words[:3])
    
    def _extract_directory(self, prompt: str) -> str:
        """Extract directory from prompt"""
        return str(Path.home() / "coding-agent")
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code based on description"""
        if not self.is_available():
            return f"# AI code generation not available. Description: {description}"
        
        prompt = f"""
Generate {language} code for the following description:
{description}

Provide clean, well-commented code that follows best practices.
"""
        
        result = self.chat_completion(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a {language} expert. Generate clean, well-commented code."},
                {"role": "user", "content": prompt}
            ]
        )
        
        if "error" in result:
            return f"# Code generation failed: {result['error']}"
        
        try:
            return result["choices"][0]["message"]["content"]
        except KeyError:
            return f"# Code generation failed: Invalid response format"
    
    def explain_code(self, code: str, language: str = "python") -> str:
        """Explain code functionality"""
        if not self.is_available():
            return f"# Code explanation not available for:\n{code}"
        
        prompt = f"""
Explain the following {language} code clearly and concisely:

```{language}
{code}
```

Provide:
1. What the code does
2. Key functions/classes used
3. Potential improvements
"""
        
        result = self.chat_completion(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a code expert. Explain code clearly and helpfully."},
                {"role": "user", "content": prompt}
            ]
        )
        
        if "error" in result:
            return f"# Code explanation failed: {result['error']}"
        
        try:
            return result["choices"][0]["message"]["content"]
        except KeyError:
            return f"# Code explanation failed: Invalid response format"
