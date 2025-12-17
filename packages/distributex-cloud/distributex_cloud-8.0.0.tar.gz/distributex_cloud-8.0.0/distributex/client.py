"""
DistributeX Python SDK v8.0
============================
Production-grade distributed computing for Python

Features:
- Automatic task sharding across multiple workers
- Smart package caching
- Real-time progress tracking
- Result streaming
- Fault tolerance

Example:
    dx = DistributeX(api_key="your_key")
    
    # Simple execution
    result = dx.run(my_function, args=(data,))
    
    # Multi-worker parallel execution
    results = dx.run(
        my_function,
        args=(large_dataset,),
        workers=10,
        strategy='data-parallel'
    )
"""

import os
import sys
import json
import time
import inspect
import hashlib
import base64
import requests
from typing import Any, Callable, Optional, Dict, List, Union, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

__version__ = "8.0.0"


@dataclass
class Task:
    """Task object for tracking execution"""
    id: str
    status: str
    progress: float = 0.0
    shards: List[Dict] = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None


@dataclass
class Shard:
    """Individual shard of a task"""
    id: str
    index: int
    total: int
    status: str
    worker_id: Optional[str] = None
    progress: float = 0.0
    result: Any = None


@dataclass
class ResourceProfile:
    """Resource requirements for a task"""
    cpu: int = 2
    ram: int = 2048
    gpu: int = 0
    storage: int = 10


class ResourceAnalyzer:
    """Analyzes code to determine resource requirements"""
    
    PACKAGE_REQUIREMENTS = {
        'torch': {'cpu': 4, 'ram': 8192, 'gpu': 1},
        'tensorflow': {'cpu': 4, 'ram': 8192, 'gpu': 1},
        'transformers': {'cpu': 4, 'ram': 16384, 'gpu': 1},
        'pandas': {'cpu': 4, 'ram': 8192},
        'numpy': {'cpu': 4, 'ram': 4096},
        'dask': {'cpu': 8, 'ram': 16384},
        'cv2': {'cpu': 4, 'ram': 4096},
        'pillow': {'cpu': 2, 'ram': 2048},
        'scikit-image': {'cpu': 4, 'ram': 4096},
        'default': {'cpu': 2, 'ram': 2048}
    }
    
    @classmethod
    def analyze(cls, func: Callable, packages: List[str]) -> Dict[str, Any]:
        """Analyze function to determine resource needs"""
        requirements = {'cpu': 2, 'ram': 2048, 'gpu': 0, 'storage': 10}
        
        for pkg in packages:
            pkg_name = pkg.split('[')[0].split('==')[0].split('>=')[0]
            pkg_req = cls.PACKAGE_REQUIREMENTS.get(pkg_name, cls.PACKAGE_REQUIREMENTS['default'])
            
            requirements['cpu'] = max(requirements['cpu'], pkg_req.get('cpu', 2))
            requirements['ram'] = max(requirements['ram'], pkg_req.get('ram', 2048))
            requirements['gpu'] = max(requirements['gpu'], pkg_req.get('gpu', 0))
        
        try:
            source = inspect.getsource(func)
            source_lower = source.lower()
            
            if any(kw in source_lower for kw in ['cuda', '.to(device)', '.gpu(', 'torch.nn']):
                requirements['gpu'] = max(requirements['gpu'], 1)
                requirements['cpu'] = max(requirements['cpu'], 4)
                requirements['ram'] = max(requirements['ram'], 8192)
            
            if any(kw in source_lower for kw in ['multiprocessing', 'concurrent.futures', 'threading']):
                requirements['cpu'] = max(requirements['cpu'], 8)
                requirements['ram'] = max(requirements['ram'], 8192)
            
            if any(kw in source_lower for kw in ['read_csv', 'read_parquet', 'large', 'big']):
                requirements['ram'] = max(requirements['ram'], 16384)
                requirements['storage'] = max(requirements['storage'], 50)
        
        except (OSError, TypeError):
            pass
        
        return requirements


class DistributeX:
    """DistributeX Client - Production-grade distributed computing"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://distributex.cloud"
    ):
        self.api_key = api_key or os.getenv("DISTRIBUTEX_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key required!\n\n"
                "Get your key: https://distributex.cloud/api-dashboard\n"
                "Then: export DISTRIBUTEX_API_KEY='your_key'"
            )
        
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'DistributeX-Python-SDK/{__version__}'
        })
    
    def run(
        self,
        func: Callable,
        args: Tuple = (),
        kwargs: Optional[Dict] = None,
        cpu: Optional[int] = None,
        ram: Optional[int] = None,
        gpu: Optional[int] = None,
        storage: Optional[int] = None,
        workers: int = 1,
        strategy: str = 'auto',
        timeout: int = 3600,
        priority: int = 5,
        wait: bool = True,
        packages: Optional[List[str]] = None,
        auto_detect: bool = True
    ) -> Any:
        """
        Run function on distributed network with intelligent sharding.
        
        Args:
            func: Python function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            cpu: CPU cores (total across all workers)
            ram: RAM in MB (total across all workers)
            gpu: Number of GPUs needed (total)
            storage: Storage in GB (per worker)
            workers: Number of workers to use (1-100)
            strategy: Distribution strategy ('auto', 'data-parallel', 'task-parallel', 'single')
            timeout: Max execution time in seconds
            priority: Task priority (1-10)
            wait: Block until complete
            packages: Required packages (auto-detected if None)
            auto_detect: Auto-detect resources from code
        
        Returns:
            Execution result(s)
        """
        
        kwargs = kwargs or {}
        
        print(f"\n{'=' * 70}")
        print(f"DISTRIBUTEX v8.0 - DISTRIBUTED EXECUTION")
        print(f"{'=' * 70}")
        print(f"Function: {func.__name__}")
        print(f"Workers: {workers}")
        print(f"Strategy: {strategy}")
        print(f"{'=' * 70}\n")
        
        try:
            source_code = inspect.getsource(func)
        except (OSError, TypeError) as e:
            raise ValueError(
                f"Cannot extract source for {func.__name__}. "
                f"Define function in a .py file, not in REPL. Error: {e}"
            )
        
        if packages is None:
            packages = self._detect_imports(source_code)
        
        print(f"Detected packages: {packages if packages else 'None'}")
        
        if auto_detect and (cpu is None or ram is None or gpu is None):
            print("\nAnalyzing resource requirements...")
            detected = ResourceAnalyzer.analyze(func, packages)
            
            cpu = cpu or detected['cpu'] * workers
            ram = ram or detected['ram'] * workers
            gpu = gpu if gpu is not None else detected['gpu'] * workers
            storage = storage or detected['storage']
            
            print(f"   Detected: {detected['cpu']} CPU, {detected['ram']} MB RAM, {detected['gpu']} GPU per worker")
        else:
            cpu = cpu or 2 * workers
            ram = ram or 2048 * workers
            gpu = gpu if gpu is not None else 0
            storage = storage or 10
        
        print(f"\nFinal allocation:")
        print(f"   Total: {cpu} CPU, {ram} MB RAM, {gpu} GPU")
        print(f"   Per worker: {cpu//workers} CPU, {ram//workers} MB RAM")
        
        sharding_strategy = strategy
        total_shards = workers
        
        if strategy == 'auto':
            if len(args) > 0 and hasattr(args[0], '__len__') and len(args[0]) > workers * 10:
                sharding_strategy = 'data-parallel'
                print(f"\nAuto-selected: data-parallel (large dataset detected)")
            elif workers > 1:
                sharding_strategy = 'task-parallel'
                print(f"\nAuto-selected: task-parallel")
            else:
                sharding_strategy = 'single'
                total_shards = 1
                print(f"\nSingle worker execution")
        
        is_sharded = total_shards > 1
        
        execution_config = {
            'runtime': 'python',
            'packages': packages,
            'function': {
                'name': func.__name__,
                'source': source_code,
                'args': args,
                'kwargs': kwargs
            },
            'sharding': {
                'strategy': sharding_strategy,
                'total_shards': total_shards,
                'is_sharded': is_sharded
            }
        }
        
        print(f"\nSubmitting task to network...")
        
        try:
            response = self.session.post(
                f'{self.base_url}/api/tasks/execute',
                json={
                    'name': f'{func.__name__}',
                    'taskType': 'distributed_execution',
                    'runtime': 'python',
                    'cpu_required': cpu,
                    'ram_required': ram,
                    'gpu_required': gpu,
                    'storage_required': storage * 1024,
                    'timeout': timeout,
                    'priority': priority,
                    'is_sharded': is_sharded,
                    'total_shards': total_shards,
                    'sharding_strategy': sharding_strategy,
                    'execution_config': execution_config
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Task submission failed"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('message', str(e))
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": HTTP {e.response.status_code}"
            raise RuntimeError(error_msg)
        
        task_id = result.get('id')
        if not task_id:
            raise RuntimeError(f"No task ID in response: {result}")
        
        print(f"Task submitted: {task_id}")
        print(f"   Status: {result.get('status', 'pending')}")
        
        if is_sharded:
            print(f"   Shards: {total_shards} (strategy: {sharding_strategy})")
        
        if not wait:
            return Task(
                id=task_id,
                status=result.get('status', 'pending'),
                progress=0.0
            )
        
        print(f"\nExecuting on distributed workers...")
        
        if is_sharded:
            print(f"   Sharding strategy: {sharding_strategy}")
            print(f"   Total shards: {total_shards}")
            print(f"   Workers will execute in parallel\n")
        
        return self._wait_for_result(task_id, is_sharded)
    
    def _detect_imports(self, source_code: str) -> List[str]:
        """Auto-detect imported packages from source code"""
        packages = set()
        
        try:
            import ast
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        pkg = alias.name.split('.')[0]
                        packages.add(pkg)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        pkg = node.module.split('.')[0]
                        packages.add(pkg)
        except SyntaxError:
            import re
            pattern = r'^\s*(?:from\s+(\S+)|import\s+(\S+))'
            for match in re.finditer(pattern, source_code, re.MULTILINE):
                pkg = (match.group(1) or match.group(2)).split('.')[0]
                packages.add(pkg)
        
        stdlib = self._get_stdlib()
        return sorted(packages - stdlib)
    
    def _get_stdlib(self) -> set:
        """Get standard library module names"""
        if hasattr(sys, 'stdlib_module_names'):
            return set(sys.stdlib_module_names)
        
        return {
            'os', 'sys', 'json', 'time', 're', 'math', 'random', 'datetime',
            'collections', 'itertools', 'functools', 'io', 'pathlib', 'typing',
            'abc', 'argparse', 'ast', 'asyncio', 'base64', 'hashlib', 'inspect'
        }
    
    def _wait_for_result(self, task_id: str, is_sharded: bool) -> Any:
        """Poll for completion and return result"""
        last_progress = -1
        
        while True:
            try:
                r = self.session.get(f'{self.base_url}/api/tasks/{task_id}', timeout=10)
                r.raise_for_status()
                task = r.json()
                
                progress = task.get('progress_percent', 0)
                status = task.get('status')
                
                if progress != last_progress and progress > 0:
                    if is_sharded:
                        shards = task.get('shards', [])
                        completed = sum(1 for s in shards if s.get('status') == 'completed')
                        total = len(shards) if shards else 1
                        print(f"\rProgress: {progress:.1f}% | Shards: {completed}/{total} complete", end='', flush=True)
                    else:
                        print(f"\rProgress: {progress:.1f}%", end='', flush=True)
                    last_progress = progress
                
                if status == 'completed':
                    print('\r' + ' ' * 80 + '\r', end='')
                    print("Task completed!\n")
                    
                    r = self.session.get(f'{self.base_url}/api/tasks/{task_id}/result', timeout=10)
                    r.raise_for_status()
                    result = r.json()
                    
                    if isinstance(result, dict) and 'result' in result:
                        return result['result']
                    return result
                
                if status == 'failed':
                    error = task.get('error_message', 'Unknown error')
                    print(f"\nTask failed: {error}")
                    raise RuntimeError(f"Task failed: {error}")
                
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"API request failed: {str(e)}")
            except KeyboardInterrupt:
                print("\nInterrupted")
                raise
    
    def get_task(self, task_id: str) -> Task:
        """Get task status"""
        try:
            r = self.session.get(f'{self.base_url}/api/tasks/{task_id}', timeout=10)
            r.raise_for_status()
            data = r.json()
            
            return Task(
                id=data['id'],
                status=data['status'],
                progress=data.get('progress_percent', 0),
                error=data.get('error_message')
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get task status: {str(e)}")
    
    def network_stats(self) -> Dict:
        """Get network statistics"""
        try:
            r = self.session.get(f'{self.base_url}/api/stats/network', timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get network stats: {str(e)}")


__all__ = ['DistributeX', 'Task', 'Shard', 'ResourceProfile']


if __name__ == '__main__':
    dx = DistributeX()
    
    def process_chunk(data_chunk):
        """Process a chunk of data"""
        import numpy as np
        return np.sum(data_chunk)
    
    result = dx.run(
        process_chunk,
        args=([1, 2, 3, 4, 5] * 1000,),
        workers=5,
        strategy='data-parallel'
    )
    print(f"Result: {result}")
