"""
DistributeX Python SDK v2.0 - UPGRADED
=======================================
Run ANY Python function directly
Auto-detect imports and dependencies
Zero script files needed
Seamless network execution
Features:
- Function serialization with closure support
- Automatic import detection
- Smart package installation
- Direct code injection
- Real-time stdout/stderr streaming
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
import sys
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
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)
   
    def visit_ImportFrom(self, node):
        if node.module:
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
           
            return {pkg for pkg in all_imports if pkg not in stdlib}
           
        except SyntaxError:
            return set()


# ============================================================================
# FUNCTION SERIALIZER - Converts Python functions to executable code
# ============================================================================
class FunctionSerializer:
    """Serialize Python functions into standalone executable scripts"""
   
    @staticmethod
    def extract_function_source(func: Callable) -> str:
        try:
            source = inspect.getsource(func)
            return textwrap.dedent(source)
        except (OSError, TypeError):
            func_name = getattr(func, '__name__', 'function')
            return f"def {func_name}(*args, **kwargs):\n    raise NotImplementedError('Cannot serialize this function type')\n"

    @staticmethod
    def extract_dependencies(func: Callable) -> Set[str]:
        source = FunctionSerializer.extract_function_source(func)
        return ImportDetector.detect_imports(source)
   
    @staticmethod
    def create_executable_script(
        func: Callable,
        args: tuple,
        kwargs: dict,
        auto_install: bool = True
    ) -> Dict[str, str]:
        func_source = FunctionSerializer.extract_function_source(func)
        func_name = func.__name__
       
        packages = FunctionSerializer.extract_dependencies(func)
       
        import_lines = []
        function_body = []
        in_imports = True
       
        for line in func_source.split('\n'):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                if in_imports:
                    import_lines.append(line)
                else:
                    function_body.append(line)
            elif stripped.startswith('def '):
                in_imports = False
                function_body.append(line)
            else:
                in_imports = False
                function_body.append(line)
       
        script_parts = [
            '#!/usr/bin/env python3',
            '"""',
            f'DistributeX Task - Function: {func_name}',
            f'SDK Version: {__version__}',
            '"""',
            '',
        ]
       
        if auto_install and packages:
            script_parts.extend([
                '# Auto-install dependencies',
                'import subprocess',
                'import sys',
                '',
                'REQUIRED_PACKAGES = ' + repr(sorted(packages)),
                '',
                'def install_packages():',
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
       
        if import_lines:
            script_parts.append('# Required imports')
            script_parts.extend(import_lines)
            script_parts.append('')
       
        script_parts.extend([
            'import json',
            'import traceback',
            '',
        ])
       
        script_parts.append('# User function')
        script_parts.extend(function_body)
        script_parts.append('')
       
        script_parts.extend([
            '# Execution wrapper',
            'def main():',
            '    """Execute function and save results"""',
            f'    args = {repr(args)}',
            f'    kwargs = {repr(kwargs)}',
            '',
            f'    print(f"Executing {func_name}")',
            '    print(f" Args: {args}")',
            '    print(f" Kwargs: {kwargs}")',
            '',
            '    try:',
            f'        result = {func_name}(*args, **kwargs)',
            '',
            '        result_data = {',
            '            "success": True,',
            '            "result": result,',
            f'            "function": "{func_name}"',
            '        }',
            '',
            '        with open("result.json", "w") as f:',
            '            json.dump(result_data, f, indent=2, default=str)',
            '',
            '        print(f"Execution complete!")',
            '        print(f"Result: {result}")',
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
            '        print(f"Error: {error_msg}")',
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
    """
   
    def __init__(self, api_key=None, base_url="https://distributex.cloud", debug=False):
        self.api_key = api_key or os.getenv("DISTRIBUTEX_API_KEY")
       
        if not self.api_key:
            raise ValueError(
                "API key required!\n\n"
                "Option 1 - Pass directly:\n"
                " dx = DistributeX(api_key='dx_your_key')\n\n"
                "Option 2 - Set environment variable:\n"
                " export DISTRIBUTEX_API_KEY='dx_your_key'\n\n"
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
            print(f"DistributeX SDK v{__version__}")
            print(f"Connected to: {self.base_url}")
            print(f"API Key: {self.api_key[:10]}...")

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
            stream_output: bool = True,  # New: control live streaming
            packages: Optional[List[str]] = None) -> Any:

        kwargs = kwargs or {}
       
        if self.debug:
            print(f"\n{'=' * 60}")
            print(f"SUBMITTING TASK: {func.__name__}")
            print(f"{'=' * 60}")
       
        serialized = FunctionSerializer.create_executable_script(
            func, args, kwargs, auto_install=True
        )
       
        script_source = serialized['script']
        detected_packages = serialized['packages']
        script_hash = serialized['hash']
       
        final_packages = packages if packages is not None else detected_packages
       
        if self.debug and detected_packages:
            print(f"Auto-detected packages: {', '.join(detected_packages)}")
       
        script_b64 = base64.b64encode(script_source.encode('utf-8')).decode('ascii')
       
        task_data = {
            'name': f'Function: {func.__name__}',
            'taskType': 'script_execution',
            'runtime': 'python',
            'executionScript': script_b64,
            'scriptHash': script_hash,
            'dependencies': final_packages,
            'workers': workers,
            'cpuPerWorker': cpu_per_worker,
            'ramPerWorker': ram_per_worker,
            'gpuRequired': gpu,
            'requiresCuda': cuda,
            'storageRequired': storage,
            'timeout': timeout,
            'priority': priority
        }
       
        print(f"\nSubmitting to distributed network...")
       
        try:
            resp = self.session.post(
                f"{self.base_url}/api/tasks/execute",
                json=task_data,
                timeout=30
            )
            resp.raise_for_status()
            result = resp.json()
           
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f" Response: {e.response.text[:500]}")
            raise RuntimeError(f"Failed to submit task: {e}")
       
        if not result.get('success', True):
            error_msg = result.get('message', 'Unknown error')
            print(f"Task submission failed: {error_msg}")
            raise RuntimeError(f"Task submission failed: {error_msg}")
       
        task_id = result.get('id')
        if not task_id:
            raise RuntimeError("API did not return task ID")
       
        print(f"Task submitted successfully!")
        print(f" Task ID: {task_id}")
        print(f" Status: {result.get('status', 'pending')}")
       
        if result.get('assignedWorker'):
            worker = result['assignedWorker']
            print(f" Worker: {worker.get('name', 'Unknown')}")
        elif result.get('queuePosition'):
            print(f" Queue Position: {result['queuePosition']}")
       
        task = Task(id=task_id, status=result.get('status', 'pending'))
       
        if not wait:
            print(f"\nNot waiting for completion (wait=False)")
            return task
       
        # Use real-time streaming when waiting
        print(f"\nWaiting for execution with live output...\n")
        return self._wait_and_stream_output(task_id, stream_output=stream_output)

    def run_script(self, script_path: str, args: tuple = (), **options) -> Any:
        with open(script_path, 'r') as f:
            script_code = f.read()
       
        def script_wrapper():
            exec(script_code, {'__name__': '__main__'})
       
        return self.run(script_wrapper, args=args, **options)

    # ==================== NEW: REAL-TIME STREAMING ====================
    def _get_task_output(self, task_id: str, since_id: int = 0) -> dict:
        """Get incremental output from task"""
        try:
            r = self.session.get(
                f"{self.base_url}/api/tasks/{task_id}/output?since={since_id}",
                timeout=5
            )
            r.raise_for_status()
            return r.json()
        except:
            return {'output': [], 'lastId': since_id}

    def _wait_and_stream_output(self, task_id: str, stream_output: bool = True) -> Any:
        """Stream output in real-time to developer terminal"""
        last_output_id = 0
        last_progress = -1
       
        print(f"{'=' * 60}")
        print(f"LIVE EXECUTION OUTPUT:")
        print(f"{'=' * 60}\n")
       
        while True:
            try:
                task = self.get_task(task_id)
               
                # Stream new output lines
                if stream_output and task.status in ['active', 'completed']:
                    output_data = self._get_task_output(task_id, last_output_id)
                   
                    for line in output_data['output']:
                        if line['type'] == 'stdout':
                            print(line['data'], end='')
                        elif line['type'] == 'stderr':
                            print(f"\033[91m{line['data']}\033[0m", end='')  # Red
                   
                    last_output_id = output_data['lastId']
               
                # Show progress
                if task.progress != last_progress and task.progress > 0:
                    sys.stdout.write(f"\rProgress: {task.progress:.1f}%")
                    sys.stdout.flush()
                    last_progress = task.progress
               
                # Completion handling
                if task.status == 'completed':
                    print(f"\n\n{'=' * 60}")
                    print(f"EXECUTION COMPLETED")
                    print(f"{'=' * 60}\n")
                    return self.get_result(task_id)
               
                if task.status == 'failed':
                    error_msg = task.error or "Task failed"
                    print(f"\n\nTASK FAILED: {error_msg}\n")
                    raise RuntimeError(error_msg)
               
                time.sleep(2)  # Poll every 2 seconds
               
            except KeyboardInterrupt:
                print(f"\nInterrupted - task still running remotely")
                raise

    # ==================== LEGACY METHOD (kept for compatibility) ====================
	def _wait_and_get_result(self, task_id: str) -> Any:
	    """Wait for task completion and SHOW output on developer terminal"""
	    last_status = None
	    last_progress = -1
	    
	    print(f"\n{'=' * 60}")
	    print(f"📺 EXECUTION OUTPUT (from remote worker):")
	    print(f"{'=' * 60}\n")
	    
	    while True:
	        try:
	            task = self.get_task(task_id)
	            
	            # Show progress
	            if task.progress != last_progress and task.progress > 0:
	                print(f"⚙️  Progress: {task.progress:.1f}%", end='\r', flush=True)
	                last_progress = task.progress
	            
	            # Check completion
	            if task.status == 'completed':
	                print('\r' + ' ' * 40 + '\r', end='', flush=True)  # Clear progress
	                
	                result_data = self.get_result(task_id)
	                
	                # Extract and DISPLAY the output that was captured on worker
	                if isinstance(result_data, dict):
	                    if 'output' in result_data:
	                        # Print the captured output from worker
	                        print("\n" + "─" * 60)
	                        print("OUTPUT FROM WORKER:")
	                        print("─" * 60)
	                        print(result_data['output'])  # All print() statements appear here!
	                        print("─" * 60)
	                    
	                    # Return the actual result
	                    if 'result' in result_data:
	                        return result_data['result']
	                
	                return result_data
	            
	            # Check failure
	            if task.status == 'failed':
	                print(f"\n❌ Task failed: {task.error}")
	                raise RuntimeError(task.error or 'Task failed')
	            
	            time.sleep(5)
	            
	        except KeyboardInterrupt:
	            print(f"\n⚠️  Interrupted")
	            raise

    # ==================== HELPER METHODS ====================
    def get_task(self, task_id: str) -> Task:
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
        try:
            r = self.session.get(f"{self.base_url}/api/tasks/{task_id}/result", timeout=10)
           
            if r.status_code == 302:
                redirect_url = r.headers.get('Location')
                r = self.session.get(redirect_url, timeout=30)
           
            r.raise_for_status()
           
            if 'json' in r.headers.get('content-type', ''):
                data = r.json()
                if 'result' in data:
                    return data['result']
                elif data.get('success') is False:
                    raise RuntimeError(data.get('error', 'Task failed'))
                return data
           
            return r.text
           
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get result: {e}")

    def network_stats(self) -> Dict[str, Any]:
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
   
    api_key = os.getenv('DISTRIBUTEX_API_KEY')
    if not api_key:
        print("Set DISTRIBUTEX_API_KEY environment variable")
        print("\n export DISTRIBUTEX_API_KEY='dx_your_key'")
        print("\nGet your API key at: https://distributex.cloud/api-dashboard")
        sys.exit(1)
   
    dx = DistributeX(api_key=api_key, debug=True)
   
    print("\n" + "=" * 60)
    print("Example: Live streaming + NumPy auto-detection")
    print("=" * 60)
   
    def long_running_task():
        import time
        import numpy as np
        print("Starting heavy computation...")
        for i in range(10):
            time.sleep(1)
            print(f"Progress step {i+1}/10 - computing...")
            arr = np.random.rand(1000, 1000)
            _ = np.linalg.eigvals(arr)  # heavy op
        print("Done! Returning result...")
        return "Success! NumPy worked perfectly on remote worker"

    result = dx.run(
        long_running_task,
        cpu_per_worker=4,
        ram_per_worker=4096,
        wait=True,
        stream_output=True  # Live output!
    )
   
    print(f"\nFinal result: {result}")
    print("\nTransparent distributed execution with real-time streaming complete!")
