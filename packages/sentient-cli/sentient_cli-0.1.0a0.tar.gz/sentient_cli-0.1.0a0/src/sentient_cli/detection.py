"""
Project type and framework detection for AI projects
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import re


class ProjectDetector:
    """Detects project type and framework for AI projects"""
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        'langchain': {
            'imports': ['langchain', 'from langchain'],
            'files': ['requirements.txt', 'pyproject.toml', 'setup.py'],
            'keywords': ['langchain', 'llm', 'chain', 'agent']
        },
        'crewai': {
            'imports': ['crewai', 'from crewai'],
            'files': ['requirements.txt', 'pyproject.toml'],
            'keywords': ['crewai', 'crew', 'agent', 'task']
        },
        'autogen': {
            'imports': ['autogen', 'from autogen'],
            'files': ['requirements.txt', 'pyproject.toml'],
            'keywords': ['autogen', 'conversable', 'agent']
        },
        'openai': {
            'imports': ['openai', 'from openai'],
            'files': ['requirements.txt', 'pyproject.toml'],
            'keywords': ['openai', 'gpt', 'assistant']
        },
        'anthropic': {
            'imports': ['anthropic', 'from anthropic'],
            'files': ['requirements.txt', 'pyproject.toml'],
            'keywords': ['anthropic', 'claude']
        },
        'fastapi': {
            'imports': ['fastapi', 'from fastapi'],
            'files': ['requirements.txt', 'main.py', 'app.py'],
            'keywords': ['fastapi', 'api', 'endpoint']
        },
        'flask': {
            'imports': ['flask', 'from flask'],
            'files': ['requirements.txt', 'app.py'],
            'keywords': ['flask', 'api', 'route']
        },
        'mcp-server': {
            'imports': ['mcp', 'from mcp'],
            'files': ['requirements.txt', 'pyproject.toml'],
            'keywords': ['mcp', 'server', 'tool', 'resource']
        }
    }
    
    # File patterns that indicate project types
    PROJECT_TYPE_INDICATORS = {
        'agent': [
            'agent.py', 'agents.py', 'main.py', 'run.py',
            'chat.py', 'assistant.py', 'bot.py'
        ],
        'mcp': [
            'server.py', 'mcp_server.py', 'tools.py',
            'resources.py', 'mcp.py'
        ]
    }
    
    # Common Python entry points
    PYTHON_ENTRY_POINTS = [
        'main.py', 'app.py', 'run.py', 'server.py',
        'agent.py', 'bot.py', 'start.py'
    ]
    
    def __init__(self, project_path: Path):
        """
        Initialize detector for a project
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
    
    def detect_runtime(self) -> str:
        """
        Detect the runtime environment
        
        Returns:
            Runtime type ('python' or 'node')
        """
        # Check for Python indicators
        python_files = list(self.project_path.glob("*.py"))
        python_configs = [
            self.project_path / "requirements.txt",
            self.project_path / "pyproject.toml",
            self.project_path / "setup.py",
            self.project_path / "Pipfile"
        ]
        
        # Check for Node.js indicators
        node_files = list(self.project_path.glob("*.js")) + list(self.project_path.glob("*.ts"))
        node_configs = [
            self.project_path / "package.json",
            self.project_path / "yarn.lock",
            self.project_path / "package-lock.json"
        ]
        
        python_score = len(python_files) + sum(1 for f in python_configs if f.exists())
        node_score = len(node_files) + sum(1 for f in node_configs if f.exists())
        
        return "python" if python_score >= node_score else "node"
    
    def detect_project_type(self) -> str:
        """
        Detect if this is an agent or MCP server project
        
        Returns:
            Project type ('agent' or 'mcp')
        """
        all_files = self._get_all_python_files()
        
        agent_score = 0
        mcp_score = 0
        
        # Check file names
        for file_path in all_files:
            filename = file_path.name.lower()
            
            if any(indicator in filename for indicator in self.PROJECT_TYPE_INDICATORS['agent']):
                agent_score += 2
            
            if any(indicator in filename for indicator in self.PROJECT_TYPE_INDICATORS['mcp']):
                mcp_score += 2
        
        # Check file contents for keywords
        for file_path in all_files:
            try:
                content = file_path.read_text(encoding='utf-8').lower()
                
                # MCP-specific keywords
                mcp_keywords = ['mcp', 'model context protocol', 'tool', 'resource', 'server']
                for keyword in mcp_keywords:
                    if keyword in content:
                        mcp_score += 1
                
                # Agent-specific keywords
                agent_keywords = ['agent', 'chat', 'conversation', 'assistant', 'bot']
                for keyword in agent_keywords:
                    if keyword in content:
                        agent_score += 1
                        
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return "mcp" if mcp_score > agent_score else "agent"
    
    def detect_framework(self) -> str:
        """
        Detect the AI framework being used
        
        Returns:
            Framework name or 'custom' if not detected
        """
        framework_scores = {name: 0 for name in self.FRAMEWORK_PATTERNS.keys()}
        
        # Check imports in Python files
        python_files = self._get_all_python_files()
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                    for import_pattern in patterns['imports']:
                        if import_pattern in content:
                            framework_scores[framework] += 3
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Check requirements files
        self._check_requirements_files(framework_scores)
        
        # Check for framework-specific keywords
        self._check_framework_keywords(framework_scores)
        
        # Return framework with highest score
        if framework_scores:
            best_framework = max(framework_scores.items(), key=lambda x: x[1])
            if best_framework[1] > 0:
                return best_framework[0]
        
        return "custom"
    
    def detect_entry_point(self) -> str:
        """
        Detect the main entry point for the application
        
        Returns:
            Entry point command
        """
        runtime = self.detect_runtime()
        
        if runtime == "python":
            # Look for common Python entry points
            for entry_point in self.PYTHON_ENTRY_POINTS:
                if (self.project_path / entry_point).exists():
                    return f"python {entry_point}"
            
            # Check for package structure
            if (self.project_path / "__main__.py").exists():
                return f"python -m {self.project_path.name}"
            
            return "python main.py"
        
        else:  # node
            # Check package.json for start script
            package_json = self.project_path / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        data = json.load(f)
                    
                    scripts = data.get('scripts', {})
                    if 'start' in scripts:
                        return "npm start"
                    
                    main = data.get('main', 'index.js')
                    return f"node {main}"
                    
                except (json.JSONDecodeError, KeyError):
                    pass
            
            return "node index.js"
    
    def detect_port(self) -> int:
        """
        Detect the port the application runs on
        
        Returns:
            Port number (default 8000 for Python, 3000 for Node.js)
        """
        # Look for port configuration in files
        all_files = self._get_all_python_files()
        
        port_patterns = [
            r'port\s*=\s*(\d+)',
            r'PORT\s*=\s*(\d+)',
            r'listen\(\s*(\d+)',
            r'run\([^)]*port\s*=\s*(\d+)',
        ]
        
        for file_path in all_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for pattern in port_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        try:
                            port = int(matches[0])
                            if 1000 <= port <= 65535:  # Valid port range
                                return port
                        except ValueError:
                            continue
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Default ports based on runtime
        runtime = self.detect_runtime()
        return 8000 if runtime == "python" else 3000
    
    def get_detection_summary(self) -> Dict[str, str]:
        """
        Get a complete detection summary
        
        Returns:
            Dict with all detected information
        """
        return {
            'runtime': self.detect_runtime(),
            'type': self.detect_project_type(),
            'framework': self.detect_framework(),
            'entry_point': self.detect_entry_point(),
            'port': str(self.detect_port())
        }
    
    def _get_all_python_files(self) -> List[Path]:
        """Get all Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip common directories to ignore
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _check_requirements_files(self, framework_scores: Dict[str, int]) -> None:
        """Check requirements files for framework dependencies"""
        req_files = [
            self.project_path / "requirements.txt",
            self.project_path / "pyproject.toml",
            self.project_path / "setup.py"
        ]
        
        for req_file in req_files:
            if req_file.exists():
                try:
                    content = req_file.read_text(encoding='utf-8').lower()
                    
                    for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                        for keyword in patterns['keywords']:
                            if keyword in content:
                                framework_scores[framework] += 2
                                
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    def _check_framework_keywords(self, framework_scores: Dict[str, int]) -> None:
        """Check for framework-specific keywords in code"""
        python_files = self._get_all_python_files()
        
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8').lower()
                
                for framework, patterns in self.FRAMEWORK_PATTERNS.items():
                    for keyword in patterns['keywords']:
                        if keyword in content:
                            framework_scores[framework] += 1
                            
            except (UnicodeDecodeError, PermissionError):
                continue


def detect_project(project_path: Optional[Path] = None) -> Dict[str, str]:
    """
    Convenience function to detect project information
    
    Args:
        project_path: Path to project (defaults to current directory)
        
    Returns:
        Dict with detection results
    """
    path = project_path or Path.cwd()
    detector = ProjectDetector(path)
    return detector.get_detection_summary()