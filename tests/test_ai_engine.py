"""
Tests for Boni AI Engine
"""

import pytest
from src.core.ai_engine import AIEngine

class TestAIEngine:
    """Test cases for AIEngine class"""
    
    def test_initialization(self):
        """Test AI engine initialization"""
        engine = AIEngine()
        assert engine.is_running == False
        assert isinstance(engine.config, dict)
        assert isinstance(engine.models, dict)
    
    def test_process_input(self):
        """Test input processing"""
        engine = AIEngine()
        test_input = "Hello, AI!"
        response = engine.process_input(test_input)
        assert "AI processed:" in response
        assert test_input in response
    
    def test_start_stop(self):
        """Test engine start and stop"""
        engine = AIEngine()
        assert engine.is_running == False
        
        # Start the engine
        engine.is_running = True
        assert engine.is_running == True
        
        # Stop the engine
        engine.stop()
        assert engine.is_running == False
