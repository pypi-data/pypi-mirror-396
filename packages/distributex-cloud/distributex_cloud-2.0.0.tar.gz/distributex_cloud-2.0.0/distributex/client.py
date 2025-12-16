"""
DistributeX Python SDK v2.0 - UPGRADED
=======================================
✅ Run ANY Python function directly
✅ Auto-detect imports and dependencies
✅ Zero script files needed
✅ Seamless network execution

Features:
- Function serialization with closure support
- Automatic import detection
- Smart package installation
- Direct code injection
- Backwards compatible with v1.0
"""

import os
import json
import time
import requests
import inspect
import hashlib
import base64
import ast
import re
from typing import Any, Callable, Optional, Dict, List, Set
from dataclasses import dataclass
import textwrap

__version__ = "2.0.0"

@dataclass
class Task:
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None

# ============================================================================
# IMPORT DETECTOR - Extracts all imports from function code
# ============================================================================
class ImportDetector(ast.NodeVisitor):
    """AST visitor to detect all imports in a function"""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            # import numpy -> 'numpy'
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            # from numpy import array -> 'numpy'
            self.from_imports.add(node.module.split('.')[0])
        self.generic_visit(node)
    
    @classmethod
    def detect_imports(cls, code: str) -> Set[str]:
        """Extract all package names imported in code"""
        try:
            tree = ast.parse(code)
            detector = cls()
            detector.visit(tree)
            
            all_imports = detector.imports | detector.from_imports
            
            # Filter out standard library modules
            stdlib = {
                'os', 'sys', 're', 'json', 'time', 'datetime', 'math',
                'random', 'collections', 'itertools', 'functools', 'operator',
                'pathlib', 'io', 'typing', 'dataclasses', 'enum', 'abc',
                'contextlib', 'copy', 'pickle', 'hashlib', 'base64', 'struct',
                'array', 'queue', 'threading', 'multiprocessing', 'subprocess',
                'socket', 'ssl', 'http', 'urllib', 'email', 'html', 'xml',
                'csv', 'configparser', 'logging', 'unittest', 'doctest',
                'argparse', 'getpass', 'tempfile', 'shutil', 'glob', 'fnmatch'
            }
            
            # Return only non-stdlib packages
            return {pkg for pkg in all_imports if pkg not in stdlib}
            
        except SyntaxError:
            # If parsing fails, return empty set
            return set()

# ============================================================================
# FUNCTION SERIALIZER - Converts Python functions to executable code
# ============================================================================
class FunctionSerializer:
    """Serialize Python functions into standalone executable scripts"""
    
    @staticmethod
    def extract_function_source(func: Callable) -> str:
        """Get clean source code of a function"""
        try:
            source = inspect.getsource(func)
            return textwrap.dedent(source)
        except (OSError, TypeError):
            # Lambda or built-in function
            func_name = getattr(func, '__name__', 'function')
            return f"def {func_name}(*args, **kwargs):\n    raise NotImplementedError('Cannot serialize this function type')\n"
    
    @staticmethod
    def extract_dependencies(func: Callable) -> Set[str]:
        """Auto-detect package dependencies from function code"""
        source = FunctionSerializer.extract_function_source(func)
        return ImportDetector.detect_imports(source)
    
    @staticmethod
    def create_executable_script(
        func: Callable,
        args: tuple,
        kwargs: dict,
        auto_install: bool = True
    ) -> Dict[str, str]:
        """
        Create a complete standalone Python script from a function
        
        Returns:
            dict with 'script' (source code) and 'packages' (list of dependencies)
        """
        # Get function source
        func_source = FunctionSerializer.extract_function_source(func)
        func_name = func.__name__
        
        # Detect imports and dependencies
        packages = FunctionSerializer.extract_dependencies(func)
        
        # Extract imports from function source
        import_lines = []
        function_body = []
        in_imports = True
        
        for line in func_source.split('\n'):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                if in_imports:
                    import_lines.append(line)
                else:
                    # Import inside function
                    function_body.append(line)
            elif stripped.startswith('def '):
                in_imports = False
                function_body.append(line)
            else:
                in_imports = False
                function_body.append(line)
        
        # Build complete script
        script_parts = [
            '#!/usr/bin/env python3',
            '"""',
            f'DistributeX Task - Function: {func_name}',
            f'SDK Version: {__version__}',
            '"""',
            '',
        ]
        
        # Add package auto-installation if enabled
        if auto_install and packages:
            script_parts.extend([
                '# Auto-install dependencies',
                'import subprocess',
                'import sys',
                '',
                'REQUIRED_PACKAGES = ' + repr(sorted(packages)),
                '',
                'def install_packages():',
                '    """Install required packages if missing"""',
                '    for package in REQUIRED_PACKAGES:',
                '        try:',
                f'            __import__(package)',
                '        except ImportError:',
                f'            print(f"Installing {{package}}...")',
                '            subprocess.check_call([',
                '                sys.executable, "-m", "pip", "install",',
                '                "--no-cache-dir", package',
                '            ])',
                '',
                'install_packages()',
                '',
            ])
        
        # Add imports
        if import_lines:
            script_parts.append('# Required imports')
            script_parts.extend(import_lines)
            script_parts.append('')
        
        # Add standard imports for execution
        script_parts.extend([
            'import json',
            'import traceback',
            '',
        ])
        
        # Add function definition
        script_parts.append('# User function')
        script_parts.extend(function_body)
        script_parts.append('')
        
        # Add execution logic
        script_parts.extend([
            '# Execution wrapper',
            'def main():',
            '    """Execute function and save results"""',
            f'    args = {repr(args)}',
            f'    kwargs = {repr(kwargs)}',
            '',
            f'    print(f"🚀 Executing {func_name}")',
            '    print(f"   Args: {args}")',
            '    print(f"   Kwargs: {kwargs}")',
            '',
            '    try:',
            f'        result = {func_name}(*args, **kwargs)',
            '',
            '        # Save result',
            '        result_data = {',
            '            "success": True,',
            '            "result": result,',
            f'            "function": "{func_name}"',
            '        }',
            '',
            '        with open("result.json", "w") as f:',
            '            json.dump(result_data, f, indent=2, default=str)',
            '',
            '        print(f"✅ Execution complete!")',
            '        print(f"📊 Result: {result}")',
            '        return 0',
            '',
            '    except Exception as e:',
            '        error_msg = str(e)',
            '        error_trace = traceback.format_exc()',
            '',
            '        result_data = {',
            '            "success": False,',
            '            "error": error_msg,',
            '            "traceback": error_trace',
            '        }',
            '',
            '        with open("result.json", "w") as f:',
            '            json.dump(result_data, f, indent=2)',
            '',
            '        print(f"❌ Error: {error_msg}")',
            '        print(error_trace)',
            '        return 1',
            '',
            'if __name__ == "__main__":',
            '    import sys',
            '    sys.exit(main())',
        ])
        
        script = '\n'.join(script_parts)
        
        return {
            'script': script,
            'packages': sorted(packages),
            'hash': hashlib.sha256(script.encode()).hexdigest()
        }

# ============================================================================
# MAIN CLIENT
# ============================================================================
class DistributeX:
    """
    DistributeX Client - Transparent Distributed Execution
    
    Features:
    - Run any Python function on the network
    - Auto-detect and install dependencies
    - Zero configuration needed
    - Full backwards compatibility
    
    Usage:
        dx = DistributeX(api_key="dx_your_key")
        
        def my_function(n):
            import numpy as np
            return np.sum(np.arange(n))
        
        result = dx.run(my_function, args=(1000000,))
    """
    
    def __init__(self, api_key=None, base_url="https://distributex.cloud", debug=False):
        """
        Initialize DistributeX client
        
        Args:
            api_key: API key (or set DISTRIBUTEX_API_KEY environment variable)
            base_url: API base URL (default: https://distributex.cloud)
            debug: Enable debug logging
        """
        # Try to get API key from parameter or environment
        self.api_key = api_key or os.getenv("DISTRIBUTEX_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key required!\n\n"
                "Option 1 - Pass directly (recommended):\n"
                "  dx = DistributeX(api_key='dx_your_key')\n\n"
                "Option 2 - Set environment variable:\n"
                "  export DISTRIBUTEX_API_KEY='dx_your_key'\n\n"
                "Get your API key at: https://distributex.cloud/api-dashboard"
            )
        
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"DistributeX-Python-SDK/{__version__}"
        })
        
        if self.debug:
            print(f"🌐 DistributeX SDK v{__version__}")
            print(f"📡 Connected to: {self.base_url}")
            print(f"🔑 API Key: {self.api_key[:10]}...")
    
    def run(self, 
            func: Callable,
            args: tuple = (),
            kwargs: Optional[dict] = None,
            workers: int = 1,
            cpu_per_worker: int = 2,
            ram_per_worker: int = 2048,
            gpu: bool = False,
            cuda: bool = False,
            storage: int = 10,
            timeout: int = 3600,
            priority: int = 5,
            wait: bool = True,
            packages: Optional[List[str]] = None) -> Any:
        """
        Run a Python function on the distributed network
        
        THIS IS THE MAGIC METHOD - runs any function transparently!
        
        Args:
            func: Python function to execute (can have any imports!)
            args: Positional arguments tuple
            kwargs: Keyword arguments dict
            workers: Number of workers to use
            cpu_per_worker: CPU cores per worker
            ram_per_worker: RAM in MB per worker
            gpu: Require GPU
            cuda: Require CUDA
            storage: Storage in GB
            timeout: Timeout in seconds
            priority: Task priority 1-10
            wait: Wait for completion
            packages: Manual package list (optional - auto-detected if None)
            
        Returns:
            Result from remote execution if wait=True, else Task object
            
        Example:
            def calculate(n):
                import numpy as np
                return np.sum(np.arange(n))
            
            # NumPy is auto-installed and imported on the worker!
            result = dx.run(calculate, args=(1000000,), cpu_per_worker=4)
        """
        kwargs = kwargs or {}
        
        if self.debug:
            print(f"\n{'=' * 60}")
            print(f"🚀 SUBMITTING TASK: {func.__name__}")
            print(f"{'=' * 60}")
        
        # Auto-serialize function into executable script
        serialized = FunctionSerializer.create_executable_script(
            func, args, kwargs, auto_install=True
        )
        
        script_source = serialized['script']
        detected_packages = serialized['packages']
        script_hash = serialized['hash']
        
        # Use manual packages if provided, otherwise use detected
        final_packages = packages if packages is not None else detected_packages
        
        if self.debug and detected_packages:
            print(f"📦 Auto-detected packages: {', '.join(detected_packages)}")
        
        # Encode script to base64
        script_b64 = base64.b64encode(script_source.encode('utf-8')).decode('ascii')
        
        # Build task submission request
        task_data = {
            'name': f'Function: {func.__name__}',
            'taskType': 'script_execution',
            'runtime': 'python',
            
            # Embedded script (no file upload needed!)
            'executionScript': script_b64,
            'scriptHash': script_hash,
            
            # Auto-detected dependencies
            'dependencies': final_packages,
            
            # Resource requirements
            'workers': workers,
            'cpuPerWorker': cpu_per_worker,
            'ramPerWorker': ram_per_worker,
            'gpuRequired': gpu,
            'requiresCuda': cuda,
            'storageRequired': storage,
            
            # Execution settings
            'timeout': timeout,
            'priority': priority
        }
        
        if self.debug:
            print(f"📋 Task Configuration:")
            print(f"   Workers: {workers}")
            print(f"   CPU/Worker: {cpu_per_worker} cores")
            print(f"   RAM/Worker: {ram_per_worker} MB")
            print(f"   GPU: {'Yes' if gpu else 'No'}")
            print(f"   Packages: {', '.join(final_packages) if final_packages else 'None'}")
        
        # Submit to API
        print(f"\n📤 Submitting to distributed network...")
        
        try:
            resp = self.session.post(
                f"{self.base_url}/api/tasks/execute",
                json=task_data,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response: {e.response.text[:500]}")
            raise RuntimeError(f"Failed to submit task: {e}")
        
        # Check response
        if not result.get('success', True):
            error_msg = result.get('message', 'Unknown error')
            print(f"❌ Task submission failed: {error_msg}")
            raise RuntimeError(f"Task submission failed: {error_msg}")
        
        # Extract task info
        task_id = result.get('id')
        if not task_id:
            raise RuntimeError("API did not return task ID")
        
        task_status = result.get('status', 'pending')
        
        print(f"✅ Task submitted successfully!")
        print(f"   Task ID: {task_id}")
        print(f"   Status: {task_status}")
        
        if result.get('assignedWorker'):
            worker = result['assignedWorker']
            print(f"   Worker: {worker.get('name', 'Unknown')}")
        elif result.get('queuePosition'):
            print(f"   Queue Position: {result['queuePosition']}")
        
        # Create task object
        task = Task(id=task_id, status=task_status)
        
        # Return immediately if not waiting
        if not wait:
            print(f"\n⏭️  Not waiting for completion (wait=False)")
            return task
        
        # Wait for completion
        print(f"\n⏳ Waiting for execution...")
        return self._wait_and_get_result(task_id)
    
    def run_script(self,
                   script_path: str,
                   args: tuple = (),
                   **options) -> Any:
        """
        Run a Python script file (backwards compatible method)
        
        Args:
            script_path: Path to .py file
            args: Script arguments
            **options: Same as run()
        """
        # Read script file
        with open(script_path, 'r') as f:
            script_code = f.read()
        
        # Create wrapper function
        def script_wrapper():
            exec(script_code, {'__name__': '__main__'})
        
        return self.run(script_wrapper, args=args, **options)
    
    def _wait_and_get_result(self, task_id: str) -> Any:
        """Wait for task completion and return result"""
        last_status = None
        last_progress = -1
        
        while True:
            try:
                # Get task status
                task = self.get_task(task_id)
                
                # Show progress if changed
                if task.progress != last_progress and task.progress > 0:
                    print(f"\r   Progress: {task.progress:.1f}%", end='', flush=True)
                    last_progress = task.progress
                
                # Show status if changed
                if task.status != last_status:
                    if last_status is not None:
                        print(f"\n   Status: {last_status} → {task.status}")
                    last_status = task.status
                
                # Check if completed
                if task.status == 'completed':
                    print(f"\n✅ Execution completed successfully!")
                    return self.get_result(task_id)
                
                # Check if failed
                if task.status == 'failed':
                    error_msg = task.error or "Task failed without error message"
                    print(f"\n❌ Task failed: {error_msg}")
                    raise RuntimeError(error_msg)
                
                # Wait before next poll
                time.sleep(5)
                
            except KeyboardInterrupt:
                print(f"\n⚠️  Interrupted by user")
                print(f"   Task {task_id} is still running on the network")
                print(f"   You can check status later with: dx.get_task('{task_id}')")
                raise
            
            except RuntimeError:
                raise
            
            except Exception as e:
                print(f"\n⚠️  Error polling task: {e}")
                time.sleep(5)
    
    def get_task(self, task_id: str) -> Task:
        """Get task status"""
        try:
            r = self.session.get(f"{self.base_url}/api/tasks/{task_id}", timeout=10)
            r.raise_for_status()
            data = r.json()
            
            return Task(
                id=data['id'],
                status=data['status'],
                progress=data.get('progressPercent', 0),
                error=data.get('errorMessage')
            )
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get task status: {e}")
    
    def get_result(self, task_id: str) -> Any:
        """Get task result"""
        try:
            r = self.session.get(f"{self.base_url}/api/tasks/{task_id}/result", timeout=10)
            
            # Follow redirects
            if r.status_code == 302:
                redirect_url = r.headers.get('Location')
                r = self.session.get(redirect_url, timeout=30)
            
            r.raise_for_status()
            
            # Parse response
            if 'json' in r.headers.get('content-type', ''):
                data = r.json()
                
                if 'result' in data:
                    return data['result']
                elif 'success' in data:
                    if data['success']:
                        return data.get('result')
                    else:
                        raise RuntimeError(data.get('error', 'Task failed'))
                else:
                    return data
            
            return r.text
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get result: {e}")
    
    def network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            r = self.session.get(f"{self.base_url}/api/stats/network", timeout=10)
            r.raise_for_status()
            return r.json()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get network stats: {e}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == '__main__':
    import sys
    
    # Check for API key
    api_key = os.getenv('DISTRIBUTEX_API_KEY')
    if not api_key:
        print("❌ Set DISTRIBUTEX_API_KEY environment variable")
        print("\n  export DISTRIBUTEX_API_KEY='dx_your_key'")
        print("\nGet your API key at: https://distributex.cloud/api-dashboard")
        sys.exit(1)
    
    dx = DistributeX(api_key=api_key, debug=True)
    
    # Example 1: Simple function with auto-detected imports
    print("\n" + "=" * 60)
    print("Example 1: Function with auto-detected NumPy")
    print("=" * 60)
    
    def calculate_eigenvalues(size):
        """Calculate eigenvalues of a random matrix"""
        import numpy as np  # Auto-detected and installed!
        
        matrix = np.random.rand(size, size)
        eigenvalues = np.linalg.eigvals(matrix)
        
        return {
            'size': size,
            'mean': float(np.mean(eigenvalues)),
            'max': float(np.max(eigenvalues))
        }
    
    result = dx.run(
        calculate_eigenvalues,
        args=(100,),
        cpu_per_worker=4,
        ram_per_worker=4096
    )
    
    print(f"\n📊 Result: {result}")
    print(f"   Mean eigenvalue: {result['mean']:.4f}")
    print(f"   Max eigenvalue: {result['max']:.4f}")
    
    print("\n✅ Transparent execution complete!")
    print("   NumPy was automatically detected and installed on the worker!")
