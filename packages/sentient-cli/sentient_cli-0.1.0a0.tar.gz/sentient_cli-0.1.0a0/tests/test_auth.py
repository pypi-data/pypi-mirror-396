"""
Tests for authentication functionality
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

from sentient_cli.auth import CLIAuthManager


class TestCLIAuthManager:
    """Test CLIAuthManager functionality"""
    
    def test_token_storage_and_retrieval(self):
        """Test storing and retrieving authentication tokens"""
        with TemporaryDirectory() as temp_dir:
            # Mock home directory
            with patch('sentient_cli.auth.Path.home', return_value=Path(temp_dir)):
                manager = CLIAuthManager()
                
                # Initially no token
                assert manager.get_stored_token() is None
                assert manager.get_valid_token() is None
                
                # Store token
                token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjo5OTk5OTk5OTk5fQ.test"
                user_info = {
                    "clerk_id": "user123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
                
                manager.store_token(token, user_info)
                
                # Retrieve token
                stored_data = manager.get_stored_token()
                assert stored_data is not None
                assert stored_data["token"] == token
                assert stored_data["user_info"] == user_info
    
    def test_token_validation(self):
        """Test token validation"""
        manager = CLIAuthManager()
        
        # Valid JWT format but expired
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxfQ.test"
        assert not manager.is_token_valid(expired_token)
        
        # Invalid token format
        assert not manager.is_token_valid("invalid-token")
        assert not manager.is_token_valid("")
        assert not manager.is_token_valid(None)
    
    def test_clear_token(self):
        """Test clearing stored tokens"""
        with TemporaryDirectory() as temp_dir:
            with patch('sentient_cli.auth.Path.home', return_value=Path(temp_dir)):
                manager = CLIAuthManager()
                
                # Store a token
                token = "test-token"
                user_info = {"clerk_id": "user123"}
                manager.store_token(token, user_info)
                
                assert manager.get_stored_token() is not None
                
                # Clear token
                manager.clear_token()
                assert manager.get_stored_token() is None
    
    def test_extract_user_from_token(self):
        """Test extracting user info from JWT token"""
        manager = CLIAuthManager()
        
        # Mock JWT token with user info
        with patch('jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "sub": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "exp": 9999999999
            }
            
            user_info = manager.extract_user_from_token("mock-token")
            
            assert user_info["clerk_id"] == "user123"
            assert user_info["email"] == "test@example.com"
            assert user_info["name"] == "Test User"
    
    def test_create_auth_header(self):
        """Test creating authorization headers"""
        manager = CLIAuthManager()
        
        token = "test-token"
        header = manager.create_auth_header(token)
        
        assert header == {"Authorization": "Bearer test-token"}
    
    @patch('webbrowser.open')
    @patch('sentient_cli.auth.console.input')
    def test_token_login(self, mock_input, mock_browser):
        """Test token login flow (current implementation, will be replaced with Clerk browser flow)"""
        with TemporaryDirectory() as temp_dir:
            with patch('sentient_cli.auth.Path.home', return_value=Path(temp_dir)):
                manager = CLIAuthManager()
                
                # Mock user input
                mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjo5OTk5OTk5OTk5fQ.test"
                mock_input.return_value = mock_token
                
                # Mock JWT decode
                with patch('jwt.decode') as mock_decode:
                    mock_decode.return_value = {
                        "sub": "user123",
                        "email": "test@example.com",
                        "name": "Test User",
                        "exp": 9999999999
                    }
                    
                    token = manager.initiate_browser_login()
                    
                    assert token == mock_token
                    # Note: Browser will be used in future Clerk implementation
                    # For now, token-based login doesn't use browser
                    
                    # Verify token was stored
                    stored_data = manager.get_stored_token()
                    assert stored_data["token"] == mock_token