"""
Script-based runtimes (Lean, R, Julia).

These runtimes execute script files via interpreter subprocess.
"""

import json
from typing import Any, Dict, List

from mcard import MCard

from .base import SubprocessRuntime, RUNTIME_CONFIG, LEAN_TIMEOUT, R_TIMEOUT, JULIA_TIMEOUT


class ScriptRuntime(SubprocessRuntime):
    """Base class for runtimes that execute script files."""
    
    file_key = 'code_file'
    run_args: List[str] = []
    
    def execute(self, impl: Dict[str, Any], target: MCard, ctx: Dict[str, Any]) -> Any:
        code_file = impl.get(self.file_key)
        if not code_file:
            return f"Error: No {self.runtime_name} code file provided"
        
        cmd = [self.command] + self.run_args + [code_file, json.dumps(ctx)]
        return self._run_subprocess(cmd, target, ctx, self.timeout)


class LeanRuntime(ScriptRuntime):
    """Lean 4 runtime executor."""
    runtime_name = "Lean"
    command = RUNTIME_CONFIG.get('lean', {}).get('command', 'lean')
    run_args = ['--run']
    timeout = LEAN_TIMEOUT
    
    def validate_environment(self) -> bool:
        # Lean 4 takes longer to initialize, use extended timeout
        return self._check_command(self.command, self.version_flag, timeout=30)
    
    def execute(self, impl: Dict[str, Any], target: MCard, ctx: Dict[str, Any]) -> Any:
        """Execute Lean script, passing input as the argument."""
        code_file = impl.get(self.file_key)
        if not code_file:
            return f"Error: No {self.runtime_name} code file provided"
        
        # Determine what to pass as the argument:
        # 1. If context has 'op', 'a', 'b' keys (polyglot mode), use context as JSON
        # 2. Otherwise, use target content (standalone CLM mode)
        if ctx and ('op' in ctx or 'a' in ctx or 'n' in ctx):
            # Polyglot/advanced mode - context contains the actual input data
            input_data = json.dumps(ctx)
        else:
            # Standalone CLM mode - target content is the JSON input
            input_data = target.get_content().decode('utf-8', errors='ignore')
        
        cmd = [self.command] + self.run_args + [code_file, input_data]
        return self._run_subprocess(cmd, target, ctx, self.timeout)


class RRuntime(ScriptRuntime):
    """R runtime executor."""
    runtime_name = "R"
    command = RUNTIME_CONFIG.get('r', {}).get('command', 'Rscript')
    timeout = R_TIMEOUT


class JuliaRuntime(ScriptRuntime):
    """Julia runtime executor."""
    runtime_name = "Julia"
    command = RUNTIME_CONFIG.get('julia', {}).get('command', 'julia')
    timeout = JULIA_TIMEOUT
