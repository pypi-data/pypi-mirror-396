"""
DistributeX Python SDK v7.0 - FIXED VERSION
===========================================
✅ Fixed missing Task class
✅ Fixed missing os import
✅ Added proper error handling
✅ Improved type hints
"""

import os
import json
import time
import inspect
import hashlib
import base64
import requests
from typing import Any, Callable, Optional, Dict, List, Union
from dataclasses import dataclass

__version__ = "7.0.1"

@dataclass
class Task:
    """Task object for non-blocking execution"""
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None


class ResourceProfile:
    """Smart resource detection and profiling"""
    
    # Package → Resource requirements mapping
    PACKAGE_REQUIREMENTS = {
        # Deep Learning
        'torch': {'cpu': 4, 'ram': 8192, 'gpu': True, 'storage': 10},
        'tensorflow': {'cpu': 4, 'ram': 8192, 'gpu': True, 'storage': 10},
        'keras': {'cpu': 4, 'ram': 8192, 'gpu': True, 'storage': 5},
        'jax': {'cpu': 4, 'ram': 8192, 'gpu': True, 'storage': 5},
        
        # Computer Vision
        'cv2': {'cpu': 4, 'ram': 4096, 'storage': 20},
        'opencv': {'cpu': 4, 'ram': 4096, 'storage': 20},
        'PIL': {'cpu': 2, 'ram': 2048, 'storage': 5},
        'imageio': {'cpu': 2, 'ram': 2048, 'storage': 10},
        'scikit-image': {'cpu': 4, 'ram': 4096, 'storage': 10},
        
        # Data Processing
        'pandas': {'cpu': 4, 'ram': 8192, 'storage': 20},
        'dask': {'cpu': 8, 'ram': 16384, 'storage': 50},
        'numpy': {'cpu': 4, 'ram': 4096, 'storage': 5},
        'scipy': {'cpu': 4, 'ram': 4096, 'storage': 5},
        'polars': {'cpu': 8, 'ram': 8192, 'storage': 20},
        
        # NLP
        'transformers': {'cpu': 4, 'ram': 16384, 'gpu': True, 'storage': 20},
        'spacy': {'cpu': 4, 'ram': 4096, 'storage': 10},
        'nltk': {'cpu': 2, 'ram': 2048, 'storage': 5},
        
        # Scientific Computing
        'numba': {'cpu': 4, 'ram': 4096, 'storage': 5},
        'cupy': {'cpu': 4, 'ram': 8192, 'gpu': True, 'storage': 5},
        'scikit-learn': {'cpu': 4, 'ram': 4096, 'storage': 5},
        
        # Web/Network
        'scrapy': {'cpu': 2, 'ram': 2048, 'storage': 10},
        'requests': {'cpu': 1, 'ram': 1024, 'storage': 2},
        'aiohttp': {'cpu': 2, 'ram': 2048, 'storage': 2},
        'selenium': {'cpu': 2, 'ram': 4096, 'storage': 5},
        
        # Media Processing
        'moviepy': {'cpu': 4, 'ram': 8192, 'storage': 50},
        'ffmpeg': {'cpu': 8, 'ram': 8192, 'storage': 100},
        'pydub': {'cpu': 2, 'ram': 2048, 'storage': 20},
    }
    
    @classmethod
    def detect_from_packages(cls, packages: List[str]) -> Dict[str, Any]:
        """Detect resource needs from package list"""
        requirements = {
            'cpu': 2,
            'ram': 2048,
            'gpu': False,
            'storage': 10
        }
        
        for pkg in packages:
            if pkg in cls.PACKAGE_REQUIREMENTS:
                pkg_req = cls.PACKAGE_REQUIREMENTS[pkg]
                
                requirements['cpu'] = max(requirements['cpu'], pkg_req.get('cpu', 2))
                requirements['ram'] = max(requirements['ram'], pkg_req.get('ram', 2048))
                requirements['storage'] = max(requirements['storage'], pkg_req.get('storage', 10))
                requirements['gpu'] = requirements['gpu'] or pkg_req.get('gpu', False)
        
        return requirements
    
    @classmethod
    def analyze_code(cls, source_code: str) -> Dict[str, Any]:
        """Analyze code for resource hints"""
        requirements = {
            'cpu': 2,
            'ram': 2048,
            'gpu': False,
            'storage': 10
        }
        
        code_lower = source_code.lower()
        
        # GPU detection
        gpu_keywords = ['cuda', '.gpu()', '.to(device)', 'tensorflow', 'torch.nn']
        if any(kw in code_lower for kw in gpu_keywords):
            requirements['gpu'] = True
            requirements['cpu'] = max(requirements['cpu'], 4)
            requirements['ram'] = max(requirements['ram'], 8192)
        
        # Multi-processing detection
        if 'multiprocessing' in code_lower or 'pool.map' in code_lower:
            requirements['cpu'] = max(requirements['cpu'], 8)
            requirements['ram'] = max(requirements['ram'], 8192)
        
        # Large data detection
        large_data_keywords = ['read_csv', 'read_parquet', 'load_dataset', 'videofile']
        if any(kw in code_lower for kw in large_data_keywords):
            requirements['ram'] = max(requirements['ram'], 8192)
            requirements['storage'] = max(requirements['storage'], 50)
        
        # Video/image processing
        if 'cv2.videowriter' in code_lower or 'moviepy' in code_lower:
            requirements['cpu'] = max(requirements['cpu'], 4)
            requirements['ram'] = max(requirements['ram'], 8192)
            requirements['storage'] = max(requirements['storage'], 100)
        
        return requirements


class DistributeX:
    """DistributeX Client - Intelligent Resource Allocation"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://distributex.cloud"):
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
        })
    
    def run(self,
            func: Callable,
            args: tuple = (),
            kwargs: Optional[dict] = None,
            # Resource parameters (auto-detected if None)
            cpu: Optional[int] = None,
            ram: Optional[int] = None,
            gpu: Optional[bool] = None,
            storage: Optional[int] = None,
            # Advanced options
            workers: int = 1,
            cuda: bool = False,
            timeout: int = 3600,
            priority: int = 5,
            wait: bool = True,
            packages: Optional[List[str]] = None,
            auto_detect_resources: bool = True) -> Any:
        """
        Run function on distributed network with intelligent resource allocation.
        
        Resources are auto-detected from your code if not specified!
        
        Args:
            func: Your Python function to execute
            args: Arguments to pass
            kwargs: Keyword arguments
            
            # Resources (auto-detected if None)
            cpu: CPU cores per worker (auto: 2-16)
            ram: RAM in MB per worker (auto: 2048-32768)
            gpu: Require GPU (auto-detected from code)
            storage: Storage in GB per worker (auto: 10-500)
            
            # Advanced
            workers: Number of parallel workers
            cuda: Require CUDA specifically
            timeout: Max execution time
            priority: 1-10 (higher = faster)
            wait: Block until complete
            packages: Package list (auto-detected if None)
            auto_detect_resources: Auto-detect from code/packages
        
        Returns:
            Execution result or Task object if wait=False
        
        Examples:
            # Minimal - everything auto-detected
            result = dx.run(my_ml_function, args=(data,))
            
            # Explicit resources
            result = dx.run(
                process_video,
                args=(video,),
                cpu=8,
                ram=16384,
                gpu=True,
                storage=100
            )
        """
        
        kwargs = kwargs or {}
        
        print(f"\n{'=' * 70}")
        print(f"🚀 DISTRIBUTEX EXECUTION: {func.__name__}")
        print(f"{'=' * 70}\n")
        
        # Extract function source
        try:
            source_code = inspect.getsource(func)
        except Exception as e:
            raise ValueError(
                f"Cannot extract source for {func.__name__}. "
                f"Define function in a .py file, not in REPL. Error: {e}"
            )
        
        # Auto-detect packages
        if packages is None:
            packages = self._detect_imports(source_code)
        
        # Smart resource detection
        if auto_detect_resources:
            print("🧠 Analyzing resource requirements...")
            
            detected_resources = {
                'cpu': 2,
                'ram': 2048,
                'gpu': False,
                'storage': 10
            }
            
            # Detect from packages
            if packages:
                pkg_resources = ResourceProfile.detect_from_packages(packages)
                print(f"   📦 From packages: CPU={pkg_resources['cpu']}, "
                      f"RAM={pkg_resources['ram']}MB, "
                      f"GPU={pkg_resources['gpu']}, "
                      f"Storage={pkg_resources['storage']}GB")
                
                for key in detected_resources:
                    if key == 'gpu':
                        detected_resources[key] = detected_resources[key] or pkg_resources[key]
                    else:
                        detected_resources[key] = max(detected_resources[key], pkg_resources[key])
            
            # Detect from code analysis
            code_resources = ResourceProfile.analyze_code(source_code)
            print(f"   📝 From code: CPU={code_resources['cpu']}, "
                  f"RAM={code_resources['ram']}MB, "
                  f"GPU={code_resources['gpu']}, "
                  f"Storage={code_resources['storage']}GB")
            
            for key in detected_resources:
                if key == 'gpu':
                    detected_resources[key] = detected_resources[key] or code_resources[key]
                else:
                    detected_resources[key] = max(detected_resources[key], code_resources[key])
            
            # Use detected values if not explicitly provided
            cpu = cpu if cpu is not None else detected_resources['cpu']
            ram = ram if ram is not None else detected_resources['ram']
            gpu = gpu if gpu is not None else detected_resources['gpu']
            storage = storage if storage is not None else detected_resources['storage']
            
            print(f"\n   ✅ Final allocation: CPU={cpu}, RAM={ram}MB, "
                  f"GPU={gpu}, Storage={storage}GB")
        else:
            # Use provided or defaults
            cpu = cpu or 2
            ram = ram or 2048
            gpu = gpu if gpu is not None else False
            storage = storage or 10
        
        if packages:
            print(f"\n📦 Required packages: {', '.join(packages)}")
            print(f"   Workers will install: pip install {' '.join(packages)}")
        else:
            print(f"\n📦 No external packages detected")
        
        print(f"\n🎯 Requesting resources from network...")
        print(f"   Workers: {workers}")
        print(f"   CPU: {cpu} cores/worker")
        print(f"   RAM: {ram} MB/worker ({ram/1024:.1f} GB)")
        print(f"   GPU: {'✅ Required' if gpu else '❌ Not needed'}")
        print(f"   Storage: {storage} GB/worker")
        print(f"   Total: {workers * cpu} cores, {workers * ram / 1024:.1f} GB RAM")
        
        # Create execution script
        script = self._create_execution_script(
            func_name=func.__name__,
            func_source=source_code,
            args=args,
            kwargs=kwargs,
            packages=packages
        )
        
        # Submit task with full resource specification
        try:
            response = self.session.post(
                f'{self.base_url}/api/tasks/execute',
                json={
                    'name': f'Remote: {func.__name__}',
                    'taskType': 'script_execution',
                    'runtime': 'python',
                    'executionScript': base64.b64encode(script.encode()).decode(),
                    'scriptHash': hashlib.sha256(script.encode()).hexdigest(),
                    'workers': workers,
                    'cpuPerWorker': cpu,
                    'ramPerWorker': ram,
                    'gpuRequired': gpu,
                    'requiresCuda': cuda or (gpu and 'torch' in packages),
                    'storageRequired': storage * 1024,  # Convert GB to MB
                    'timeout': timeout,
                    'priority': priority
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', None)
            error_msg = f"Failed to submit task"
            if status_code:
                error_msg += f" (HTTP {status_code})"
            try:
                error_detail = e.response.json().get('message', str(e))
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {str(e)}"
            raise RuntimeError(error_msg)
        
        task_id = result['id']
        
        print(f"\n✅ Task submitted: {task_id}")
        print(f"   Status: {result.get('status', 'pending')}")
        
        if 'assignedWorker' in result and result['assignedWorker']:
            worker = result['assignedWorker']
            print(f"   Assigned to: {worker.get('name', 'Unknown worker')}")
        elif 'queuePosition' in result:
            print(f"   Queue position: {result['queuePosition']}")
        
        if not wait:
            return Task(
                id=task_id,
                status=result.get('status', 'pending'),
                progress=0.0
            )
        
        print(f"\n⏳ Executing on remote worker(s) with allocated resources...\n")
        return self._wait_for_result(task_id)
    
    def _detect_imports(self, source_code: str) -> List[str]:
        """Auto-detect imported packages"""
        import ast
        import sys
        
        packages = set()
        
        try:
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
        except:
            pass
        
        # Filter out stdlib
        stdlib = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else {
            'os', 'sys', 'json', 'time', 're', 'math', 'random', 'datetime',
            'collections', 'itertools', 'functools', 'io', 'pathlib', 'typing'
        }
        
        return sorted(packages - stdlib)
    
    def _create_execution_script(self, func_name: str, func_source: str, 
                                 args: tuple, kwargs: dict, packages: List[str]) -> str:
        """Create standalone script that workers execute"""
        
        install_section = ""
        if packages:
            pkg_list = "', '".join(packages)
            install_section = f'''
# Auto-install required packages
import subprocess
import sys

PACKAGES = ['{pkg_list}']

print("📦 Installing packages on worker...")
for pkg in PACKAGES:
    print(f"   Installing {{pkg}}...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '--quiet', '--no-warn-script-location', pkg
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Failed to install {{pkg}}")
        raise RuntimeError(f"Package installation failed: {{pkg}}")

print("✅ Packages installed\\n")
'''
        
        return f'''#!/usr/bin/env python3
"""
DistributeX Remote Execution with Full Resource Allocation
Worker has allocated CPU, RAM, GPU, and Storage as requested
"""

import json
import traceback
{install_section}

# Your function
{func_source}

# Execution
def main():
    args = {repr(args)}
    kwargs = {repr(kwargs)}
    
    print(f"▶️  Executing {func_name}...")
    print(f"   Resources allocated and ready")
    
    try:
        result = {func_name}(*args, **kwargs)
        
        with open('result.json', 'w') as f:
            json.dump({{'success': True, 'result': result}}, f, default=str)
        
        print("✅ Execution complete!")
        return 0
        
    except Exception as e:
        error_msg = str(e)
        stack = traceback.format_exc()
        
        with open('result.json', 'w') as f:
            json.dump({{'success': False, 'error': error_msg, 'traceback': stack}}, f)
        
        print(f"❌ Error: {{error_msg}}")
        print(stack)
        return 1

if __name__ == '__main__':
    exit(main())
'''
    
    def _wait_for_result(self, task_id: str) -> Any:
        """Poll for completion and return result"""
        last_progress = -1
        
        while True:
            try:
                r = self.session.get(f'{self.base_url}/api/tasks/{task_id}', timeout=10)
                r.raise_for_status()
                task = r.json()
                
                progress = task.get('progressPercent', 0)
                if progress != last_progress and progress > 0:
                    print(f"Progress: {progress:.1f}%", end='\r')
                    last_progress = progress
                
                if task['status'] == 'completed':
                    print('\r' + ' ' * 40 + '\r', end='')
                    print("✅ Completed!\n")
                    
                    # Get result
                    r = self.session.get(f'{self.base_url}/api/tasks/{task_id}/result', timeout=10)
                    r.raise_for_status()
                    result = r.json()
                    
                    if isinstance(result, dict) and 'result' in result:
                        return result['result']
                    return result
                
                if task['status'] == 'failed':
                    error = task.get('errorMessage', 'Unknown error')
                    print(f"\n❌ Task failed: {error}")
                    raise RuntimeError(f"Task failed: {error}")
                
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                status_code = getattr(e.response, 'status_code', None)
                error_msg = f"API request failed"
                if status_code:
                    error_msg += f" (HTTP {status_code})"
                error_msg += f": {str(e)}"
                raise RuntimeError(error_msg)
            except KeyboardInterrupt:
                print("\n⚠️  Interrupted")
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
                progress=data.get('progressPercent', 0),
                error=data.get('errorMessage')
            )
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', None)
            error_msg = f"Failed to get task status"
            if status_code:
                error_msg += f" (HTTP {status_code})"
            raise RuntimeError(error_msg)
    
    def network_stats(self) -> Dict:
        """Get network resource availability"""
        try:
            r = self.session.get(f'{self.base_url}/api/stats/network', timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', None)
            error_msg = f"Failed to get network stats"
            if status_code:
                error_msg += f" (HTTP {status_code})"
            raise RuntimeError(error_msg)
    
    def estimate_cost(self, cpu: int, ram: int, gpu: bool, storage: int, hours: float = 1.0) -> Dict:
        """Estimate cost for resource usage (future feature)"""
        return {
            'cpu_hours': cpu * hours,
            'ram_gb_hours': (ram / 1024) * hours,
            'gpu_hours': hours if gpu else 0,
            'storage_gb_hours': storage * hours,
            'estimated_cost_usd': 0.0  # Free during beta
        }


# ============================================================================
# EXAMPLES
# ============================================================================
if __name__ == '__main__':
    dx = DistributeX(api_key=os.getenv('DISTRIBUTEX_API_KEY'))
    
    # Example 1: Auto-detect everything (recommended)
    def train_model(epochs):
        import torch
        import numpy as np
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = torch.nn.Linear(1000, 100).to(device)
        
        for i in range(epochs):
            data = torch.randn(32, 1000).to(device)
            output = model(data)
            print(f"Epoch {i+1}: {output.sum().item()}")
        
        return {'device': str(device), 'epochs': epochs}
    
    # SDK auto-detects: GPU=True, CPU=4, RAM=8192
    result = dx.run(train_model, args=(5,))
    print(json.dumps(result, indent=2))
    
    # Example 2: Explicit resources
    def process_video(video_path):
        import cv2
        return {'frames': 1000}
    
    result = dx.run(
        process_video,
        args=('video.mp4',),
        cpu=8,
        ram=16384,
        gpu=False,
        storage=100
    )
