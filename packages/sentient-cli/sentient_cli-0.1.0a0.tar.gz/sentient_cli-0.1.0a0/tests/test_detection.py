"""
Tests for project detection functionality
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from sentient_cli.detection import ProjectDetector


class TestProjectDetector:
    """Test ProjectDetector functionality"""
    
    def test_detect_python_runtime(self):
        """Test Python runtime detection"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create Python files
            (project_path / "main.py").write_text("print('hello')")
            (project_path / "requirements.txt").write_text("requests==2.28.0")
            
            detector = ProjectDetector(project_path)
            assert detector.detect_runtime() == "python"
    
    def test_detect_agent_type(self):
        """Test agent project type detection"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create agent-like files
            (project_path / "agent.py").write_text("""
from langchain import Agent

class MyAgent:
    def chat(self, message):
        return "Hello"
            """)
            
            detector = ProjectDetector(project_path)
            assert detector.detect_project_type() == "agent"
    
    def test_detect_mcp_type(self):
        """Test MCP server project type detection"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create MCP-like files
            (project_path / "server.py").write_text("""
from mcp import Server

server = Server("my-mcp-server")

@server.tool()
def my_tool():
    return "result"
            """)
            
            detector = ProjectDetector(project_path)
            assert detector.detect_project_type() == "mcp"
    
    def test_detect_langchain_framework(self):
        """Test LangChain framework detection"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create LangChain project
            (project_path / "main.py").write_text("""
from langchain.llms import OpenAI
from langchain.chains import LLMChain

llm = OpenAI()
chain = LLMChain(llm=llm)
            """)
            
            (project_path / "requirements.txt").write_text("""
langchain==0.1.0
openai==1.0.0
            """)
            
            detector = ProjectDetector(project_path)
            assert detector.detect_framework() == "langchain"
    
    def test_detect_entry_point(self):
        """Test entry point detection"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create main.py
            (project_path / "main.py").write_text("print('hello')")
            
            detector = ProjectDetector(project_path)
            assert detector.detect_entry_point() == "python main.py"
    
    def test_detect_port(self):
        """Test port detection"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create file with port configuration
            (project_path / "app.py").write_text("""
from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run(port=5000)
            """)
            
            detector = ProjectDetector(project_path)
            assert detector.detect_port() == 5000
    
    def test_get_detection_summary(self):
        """Test complete detection summary"""
        with TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create a simple Python agent project
            (project_path / "agent.py").write_text("""
from langchain import Agent

agent = Agent()
            """)
            (project_path / "requirements.txt").write_text("langchain==0.1.0")
            
            detector = ProjectDetector(project_path)
            summary = detector.get_detection_summary()
            
            assert summary['runtime'] == 'python'
            assert summary['type'] == 'agent'
            assert summary['framework'] == 'langchain'
            assert 'entry_point' in summary
            assert 'port' in summary