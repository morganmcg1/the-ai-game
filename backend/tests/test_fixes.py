"""
Tests for the code review fixes.

These tests verify:
1. asyncio import is available (no NameError on retry paths)
2. Input validation limits are enforced
3. Game state guards prevent invalid transitions
4. Prewarm retry logic handles eventual consistency
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAsyncioImport:
    """Test that asyncio is properly imported at module level."""
    
    def test_asyncio_available_in_module(self):
        """Verify asyncio is imported at module level in app.py."""
        # Read the app.py file and check for top-level asyncio import
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Check that asyncio is imported at the top level (not inside functions)
        lines = content.split('\n')
        top_level_imports = []
        in_function = False
        indent_level = 0
        
        for line in lines[:100]:  # Check first 100 lines for imports
            stripped = line.strip()
            if stripped.startswith('def ') or stripped.startswith('async def ') or stripped.startswith('class '):
                in_function = True
            elif not line.startswith(' ') and not line.startswith('\t') and stripped:
                in_function = False
            
            if not in_function and stripped.startswith('import asyncio'):
                top_level_imports.append(line)
        
        assert len(top_level_imports) > 0, "asyncio should be imported at module level"


class TestInputValidation:
    """Test input validation limits."""
    
    def test_max_constants_defined(self):
        """Verify max length constants are defined."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        assert 'MAX_STRATEGY_LENGTH' in content, "MAX_STRATEGY_LENGTH should be defined"
        assert 'MAX_TRAP_TEXT_LENGTH' in content, "MAX_TRAP_TEXT_LENGTH should be defined"
        assert 'MAX_SPEECH_LENGTH' in content, "MAX_SPEECH_LENGTH should be defined"
        assert 'MAX_NAME_LENGTH' in content, "MAX_NAME_LENGTH should be defined"
        assert 'MAX_CHARACTER_DESCRIPTION_LENGTH' in content, "MAX_CHARACTER_DESCRIPTION_LENGTH should be defined"
    
    def test_validation_in_submit_strategy(self):
        """Verify submit_strategy validates input length."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Find the submit_strategy function and check for validation
        assert 'MAX_STRATEGY_LENGTH' in content, "Strategy length validation should use MAX_STRATEGY_LENGTH"
        # Check that the validation is in the submit_strategy function
        submit_strategy_idx = content.find('async def api_submit_strategy')
        next_func_idx = content.find('async def ', submit_strategy_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        submit_strategy_code = content[submit_strategy_idx:next_func_idx]
        assert 'MAX_STRATEGY_LENGTH' in submit_strategy_code, "submit_strategy should validate strategy length"
    
    def test_validation_in_submit_trap(self):
        """Verify submit_trap validates input length."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        submit_trap_idx = content.find('async def api_submit_trap')
        next_func_idx = content.find('async def ', submit_trap_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        submit_trap_code = content[submit_trap_idx:next_func_idx]
        assert 'MAX_TRAP_TEXT_LENGTH' in submit_trap_code, "submit_trap should validate trap text length"
    
    def test_validation_in_join_game(self):
        """Verify join_game validates input lengths."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        join_game_idx = content.find('async def api_join_game')
        next_func_idx = content.find('async def ', join_game_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        join_game_code = content[join_game_idx:next_func_idx]
        assert 'MAX_NAME_LENGTH' in join_game_code, "join_game should validate name length"
        assert 'MAX_CHARACTER_DESCRIPTION_LENGTH' in join_game_code, "join_game should validate character description length"


class TestGameStateGuards:
    """Test game state transition guards."""
    
    def test_start_game_has_lobby_guard(self):
        """Verify start_game checks for lobby state."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        start_game_idx = content.find('async def api_start_game')
        next_func_idx = content.find('async def ', start_game_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        start_game_code = content[start_game_idx:next_func_idx]
        
        # Check for lobby status guard
        assert 'game.status != "lobby"' in start_game_code or "game.status != 'lobby'" in start_game_code, \
            "start_game should check that game is in lobby state"
        
        # Check for rounds guard
        assert 'len(game.rounds)' in start_game_code, \
            "start_game should check that game has no rounds"
    
    def test_next_round_has_playing_guard(self):
        """Verify next_round checks for playing state."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        next_round_idx = content.find('async def api_next_round')
        next_func_idx = content.find('async def ', next_round_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        next_round_code = content[next_round_idx:next_func_idx]
        
        # Check for playing status guard
        assert 'game.status != "playing"' in next_round_code or "game.status != 'playing'" in next_round_code, \
            "next_round should check that game is in playing state"
        
        # Check for results status guard
        assert 'current_round.status != "results"' in next_round_code or "current_round.status != 'results'" in next_round_code, \
            "next_round should check that current round is in results state"


class TestAsyncImageGeneration:
    """Test that submit_trap uses async image generation."""
    
    def test_submit_trap_uses_async_image_gen(self):
        """Verify submit_trap uses generate_image_fal_async instead of sync version."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        submit_trap_idx = content.find('async def api_submit_trap')
        next_func_idx = content.find('async def ', submit_trap_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        submit_trap_code = content[submit_trap_idx:next_func_idx]
        
        # Should use async version
        assert 'generate_image_fal_async' in submit_trap_code, \
            "submit_trap should use generate_image_fal_async"
        assert 'await generate_image_fal_async' in submit_trap_code, \
            "submit_trap should await generate_image_fal_async"


class TestAsyncScenarioGeneration:
    """Test that scenario generation uses asyncio.to_thread."""
    
    def test_start_game_uses_to_thread(self):
        """Verify start_game uses asyncio.to_thread for scenario generation."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        start_game_idx = content.find('async def api_start_game')
        next_func_idx = content.find('async def ', start_game_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        start_game_code = content[start_game_idx:next_func_idx]
        
        # Should use asyncio.to_thread for sync scenario generation
        assert 'asyncio.to_thread' in start_game_code, \
            "start_game should use asyncio.to_thread for scenario generation"
    
    def test_next_round_uses_to_thread(self):
        """Verify next_round uses asyncio.to_thread for scenario generation."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        next_round_idx = content.find('async def api_next_round')
        next_func_idx = content.find('async def ', next_round_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        next_round_code = content[next_round_idx:next_func_idx]
        
        # Should use asyncio.to_thread for sync scenario generation
        assert 'asyncio.to_thread' in next_round_code, \
            "next_round should use asyncio.to_thread for scenario generation"


class TestPrewarmRetryLogic:
    """Test prewarm_all_scenarios retry logic."""
    
    def test_prewarm_has_retry_logic(self):
        """Verify prewarm_all_scenarios has retry logic for eventual consistency."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        prewarm_idx = content.find('def prewarm_all_scenarios')
        next_func_idx = content.find('\n@app.function', prewarm_idx + 1)
        if next_func_idx == -1:
            next_func_idx = content.find('\ndef ', prewarm_idx + 100)
        if next_func_idx == -1:
            next_func_idx = len(content)
        prewarm_code = content[prewarm_idx:next_func_idx]
        
        # Should have retry logic
        assert 'max_fetch_retries' in prewarm_code or 'retry' in prewarm_code.lower(), \
            "prewarm_all_scenarios should have retry logic"
        assert 'asyncio.sleep' in prewarm_code, \
            "prewarm_all_scenarios should have sleep for backoff"


class TestFrontendApiErrorHandling:
    """Test frontend API error handling."""
    
    def test_api_has_error_class(self):
        """Verify api.js has ApiError class."""
        api_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'frontend', 'src', 'api.js')
        with open(api_path, 'r') as f:
            content = f.read()
        
        assert 'class ApiError' in content, "api.js should have ApiError class"
        assert 'extends Error' in content, "ApiError should extend Error"
    
    def test_api_has_fetch_helper(self):
        """Verify api.js has fetchJson helper."""
        api_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'frontend', 'src', 'api.js')
        with open(api_path, 'r') as f:
            content = f.read()
        
        assert 'async function fetchJson' in content or 'function fetchJson' in content, \
            "api.js should have fetchJson helper"
        assert 'res.ok' in content, "fetchJson should check res.ok"
    
    def test_api_methods_use_fetch_helper(self):
        """Verify API methods use fetchJson instead of raw fetch."""
        api_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'frontend', 'src', 'api.js')
        with open(api_path, 'r') as f:
            content = f.read()
        
        # Count uses of fetchJson vs raw fetch in API methods
        # The api object should use fetchJson, not raw fetch
        api_section_start = content.find('export const api = {')
        api_section = content[api_section_start:]
        
        # Should use fetchJson
        assert 'fetchJson(' in api_section, "API methods should use fetchJson"
        
        # Should not use raw fetch().then() or await fetch() followed by .json()
        # (fetchJson handles this internally)
        lines_with_return_fetch = [l for l in api_section.split('\n') 
                                   if 'return fetch(' in l or 'await fetch(' in l]
        # All fetch calls should be through fetchJson
        for line in lines_with_return_fetch:
            if 'fetchJson' not in line:
                # This is a raw fetch call - should not exist in API methods
                assert False, f"Found raw fetch call in API: {line}"


class TestUpdateGameWithRetry:
    """Test the update_game_with_retry helper function."""
    
    def test_helper_function_exists(self):
        """Verify update_game_with_retry helper exists."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        assert 'async def update_game_with_retry' in content, \
            "update_game_with_retry helper should exist"
    
    def test_helper_has_retry_logic(self):
        """Verify helper has retry logic with backoff."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Find the helper function
        helper_start = content.find('async def update_game_with_retry')
        helper_end = content.find('\n# ---', helper_start)
        if helper_end == -1:
            helper_end = content.find('\nfrom fastapi', helper_start)
        helper_code = content[helper_start:helper_end]
        
        assert 'max_retries' in helper_code, "Helper should have max_retries parameter"
        assert 'for attempt in range' in helper_code, "Helper should have retry loop"
        assert 'asyncio.sleep' in helper_code, "Helper should have backoff sleep"
        assert 'verify' in helper_code, "Helper should verify mutations"
    
    def test_submit_strategy_uses_helper(self):
        """Verify submit_strategy uses update_game_with_retry."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        submit_strategy_idx = content.find('async def api_submit_strategy')
        next_func_idx = content.find('@web_app', submit_strategy_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        submit_strategy_code = content[submit_strategy_idx:next_func_idx]
        
        assert 'update_game_with_retry' in submit_strategy_code, \
            "submit_strategy should use update_game_with_retry helper"
    
    def test_submit_trap_uses_helper(self):
        """Verify submit_trap uses update_game_with_retry."""
        app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
        with open(app_path, 'r') as f:
            content = f.read()
        
        submit_trap_idx = content.find('async def api_submit_trap')
        next_func_idx = content.find('@web_app', submit_trap_idx + 1)
        if next_func_idx == -1:
            next_func_idx = len(content)
        submit_trap_code = content[submit_trap_idx:next_func_idx]
        
        assert 'update_game_with_retry' in submit_trap_code, \
            "submit_trap should use update_game_with_retry helper"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
