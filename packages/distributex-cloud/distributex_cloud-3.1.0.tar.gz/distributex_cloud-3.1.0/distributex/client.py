"""
DistributeX Python SDK v5.0 - PURE AUTO-DETECTION
==================================================
✅ NO predefined package mappings
✅ Auto-detects ALL imports from your script
✅ Bundles packages from YOUR local environment
✅ Tells you what to install if missing (no auto-install)
✅ Runs on distributed workers using pooled resources

Philosophy:
- Developer knows their environment best
- SDK just detects, bundles, and executes
- No magic, no assumptions, full transparency
"""

import os
import sys
import json
import time
import ast
import inspect
import hashlib
import base64
import tempfile
import tarfile
import shutil
import subprocess
import requests
from pathlib import Path
from typing import Any, Callable, Optional, Dict, List, Set, Tuple
from dataclasses import dataclass

__version__ = "5.0.0"


# ============================================================================
# SIMPLE IMPORT DETECTOR
# ============================================================================
class ImportDetector(ast.NodeVisitor):
    """Detects all imports in Python code - no assumptions, pure detection"""
    
    def __init__(self):
        self.imports = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            # Get top-level package name
            pkg = alias.name.split('.')[0]
            self.imports.add(pkg)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            # Get top-level package name
            pkg = node.module.split('.')[0]
            self.imports.add(pkg)
        self.generic_visit(node)
    
    @classmethod
    def detect(cls, code: str) -> Set[str]:
        """Detect all imports from code"""
        try:
            tree = ast.parse(code)
            detector = cls()
            detector.visit(tree)
            return detector.imports
        except SyntaxError:
            return set()


# ============================================================================
# PACKAGE FINDER - Find packages in developer's environment
# ============================================================================
class PackageFinder:
    """Finds packages in the developer's local Python environment"""
    
    # Python standard library (don't bundle these)
    STDLIB = {
        'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
        'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
        'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
        'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
        'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
        'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
        'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
        'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib',
        'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp',
        'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp',
        'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword',
        'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap',
        'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'multiprocessing',
        'netrc', 'nis', 'nntplib', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev',
        'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform',
        'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty',
        'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're',
        'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets',
        'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd',
        'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'ssl', 'stat',
        'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau', 'symbol',
        'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib',
        'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit', 'tkinter',
        'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo',
        'types', 'typing', 'unicodedata', 'unittest', 'urllib', 'uu', 'uuid', 'venv',
        'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound', 'wsgiref',
        'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile', 'zipimport', 'zlib', '_thread'
    }
    
    @classmethod
    def is_stdlib(cls, package_name: str) -> bool:
        """Check if package is in standard library"""
        return package_name.lower() in cls.STDLIB
    
    @classmethod
    def find_package_path(cls, package_name: str) -> Optional[Path]:
        """
        Find where a package is installed in the developer's environment.
        Returns None if not found.
        """
        # Try to import it
        try:
            module = __import__(package_name)
            
            if not hasattr(module, '__file__') or module.__file__ is None:
                # Built-in module (like sys, os)
                return None
            
            module_file = Path(module.__file__)
            
            # Find site-packages directory
            site_packages = module_file
            while site_packages.name not in ['site-packages', 'dist-packages']:
                site_packages = site_packages.parent
                if site_packages.parent == site_packages:  # Reached root
                    return None
            
            # Look for package directory
            package_dir = site_packages / package_name
            if package_dir.exists() and package_dir.is_dir():
                return package_dir
            
            # If it's a single file module
            if module_file.stem == package_name:
                return module_file
            
            return None
            
        except ImportError:
            return None
    
    @classmethod
    def get_package_info(cls, package_name: str) -> Optional[Dict]:
        """Get package info using pip show"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower()] = value.strip()
            
            return info
        except:
            return None


# ============================================================================
# PACKAGE BUNDLER
# ============================================================================
class PackageBundler:
    """Bundles packages from developer's local environment"""
    
    @staticmethod
    def get_directory_size(path: Path) -> int:
        """Get total size of directory"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total
    
    @staticmethod
    def copy_package(src: Path, dest: Path) -> int:
        """
        Copy package directory/file to destination.
        Returns size in bytes.
        """
        # Skip patterns
        SKIP = {'__pycache__', '*.pyc', '*.pyo', '.git', '.svn', 
                'tests', 'test', 'docs', 'doc', 'examples', 'example',
                '.egg-info', '.dist-info'}
        
        if src.is_file():
            # Single file module
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            return dest.stat().st_size
        
        # Directory
        dest.mkdir(parents=True, exist_ok=True)
        total_size = 0
        
        for item in src.rglob('*'):
            # Check if should skip
            if any(pattern in item.name for pattern in SKIP):
                continue
            
            rel_path = item.relative_to(src)
            dest_path = dest / rel_path
            
            if item.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)
                total_size += dest_path.stat().st_size
        
        return total_size
    
    @classmethod
    def bundle(cls, packages: List[str], bundle_dir: Path) -> Dict[str, Any]:
        """
        Bundle packages from local environment.
        
        Returns:
            {
                'bundled': [{'name': 'pkg', 'size': 123, 'path': '/path'}],
                'missing': ['pkg2', 'pkg3'],
                'total_size': 12345
            }
        """
        packages_dir = bundle_dir / 'packages'
        packages_dir.mkdir(parents=True, exist_ok=True)
        
        bundled = []
        missing = []
        total_size = 0
        
        print(f"\n📦 Bundling {len(packages)} package(s) from your environment...")
        
        for pkg in sorted(packages):
            # Skip if stdlib
            if PackageFinder.is_stdlib(pkg):
                continue
            
            # Find package
            pkg_path = PackageFinder.find_package_path(pkg)
            
            if pkg_path:
                try:
                    dest = packages_dir / pkg
                    size = cls.copy_package(pkg_path, dest)
                    
                    bundled.append({
                        'name': pkg,
                        'size': size,
                        'path': str(pkg_path)
                    })
                    total_size += size
                    
                    print(f"   ✓ {pkg} ({size / 1024:.1f} KB)")
                except Exception as e:
                    print(f"   ✗ {pkg}: {e}")
                    missing.append(pkg)
            else:
                print(f"   ✗ {pkg}: Not found")
                missing.append(pkg)
        
        if missing:
            print(f"\n⚠️  Missing packages: {', '.join(missing)}")
            print(f"   Install them with: pip install {' '.join(missing)}")
        
        print(f"\n✅ Bundle complete: {total_size / 1024 / 1024:.2f} MB")
        
        return {
            'bundled': bundled,
            'missing': missing,
            'total_size': total_size
        }


# ============================================================================
# SCRIPT PACKAGER
# ============================================================================
class ScriptPackager:
    """Packages function into executable script"""
    
    @staticmethod
    def create_executable(func: Callable, args: tuple, kwargs: dict, 
                         packages: List[str]) -> str:
        """Create standalone Python script"""
        
        func_source = inspect.getsource(func)
        func_name = func.__name__
        
        return f'''#!/usr/bin/env python3
"""
DistributeX Task Execution
Using packages from developer's environment
"""

import sys
import os
import json
import traceback

# Add bundled packages to path
packages_dir = os.path.join(os.getcwd(), 'packages')
if os.path.exists(packages_dir):
    sys.path.insert(0, packages_dir)
    print(f"📦 Loaded packages from: {{packages_dir}}")

# User's function
{func_source}

# Execution
def main():
    args = {repr(args)}
    kwargs = {repr(kwargs)}
    
    print(f"▶️  Executing {func_name}...")
    
    try:
        result = {func_name}(*args, **kwargs)
        
        # Save result
        with open('result.json', 'w') as f:
            json.dump({{
                'success': True,
                'result': result
            }}, f, indent=2, default=str)
        
        print("✅ Execution complete!")
        return 0
        
    except Exception as e:
        # Save error
        with open('result.json', 'w') as f:
            json.dump({{
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }}, f, indent=2)
        
        print(f"❌ Error: {{e}}")
        print(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())
'''


# ============================================================================
# MAIN CLIENT
# ============================================================================
@dataclass
class Task:
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None


class DistributeX:
    """
    DistributeX Client - Run functions on distributed workers
    
    Example:
        dx = DistributeX(api_key="your_key")
        
        result = dx.run(
            lambda x: x ** 2,
            args=(10,),
            workers=4
        )
    """
    
    def __init__(self, api_key: str = None, base_url: str = "https://distributex.cloud"):
        self.api_key = api_key or os.getenv("DISTRIBUTEX_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key required!\n\n"
                "Option 1: Pass directly\n"
                "  dx = DistributeX(api_key='your_key')\n\n"
                "Option 2: Set environment variable\n"
                "  export DISTRIBUTEX_API_KEY='your_key'\n\n"
                "Get your key at: https://distributex.cloud/api-dashboard"
            )
        
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'DistributeX-Python-SDK/{__version__}'
        })
    
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
            wait: bool = True) -> Any:
        """
        Run function on distributed network
        
        Args:
            func: Python function to execute
            args: Positional arguments for function
            kwargs: Keyword arguments for function
            workers: Number of workers to use
            cpu_per_worker: CPU cores per worker
            ram_per_worker: RAM in MB per worker
            gpu: Require GPU
            cuda: Require CUDA
            storage: Storage in GB
            timeout: Timeout in seconds
            priority: Priority (1-10)
            wait: Wait for completion
            
        Returns:
            Result from function execution
        """
        kwargs = kwargs or {}
        
        print(f"\n{'=' * 60}")
        print(f"DISTRIBUTED EXECUTION: {func.__name__}")
        print(f"{'=' * 60}")
        
        # Create temporary workspace
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Detect imports
            print("\n📋 Analyzing function dependencies...")
            func_source = inspect.getsource(func)
            detected_imports = ImportDetector.detect(func_source)
            
            # Filter out stdlib
            third_party = {
                pkg for pkg in detected_imports 
                if not PackageFinder.is_stdlib(pkg)
            }
            
            if third_party:
                print(f"   Found {len(third_party)} third-party package(s):")
                for pkg in sorted(third_party):
                    print(f"   • {pkg}")
            else:
                print("   No third-party packages detected")
            
            # Step 2: Bundle packages
            bundle_info = {'bundled': [], 'missing': [], 'total_size': 0}
            
            if third_party:
                bundle_info = PackageBundler.bundle(list(third_party), temp_path)
                
                # If missing packages, stop and tell user
                if bundle_info['missing']:
                    missing_str = ' '.join(bundle_info['missing'])
                    raise RuntimeError(
                        f"\n❌ Missing packages in your environment:\n"
                        f"   {', '.join(bundle_info['missing'])}\n\n"
                        f"Install them with:\n"
                        f"   pip install {missing_str}\n"
                    )
            
            # Step 3: Create executable script
            script = ScriptPackager.create_executable(
                func, args, kwargs, list(third_party)
            )
            
            script_path = temp_path / 'script.py'
            script_path.write_text(script)
            
            # Step 4: Create tarball
            print("\n📦 Creating task bundle...")
            archive_path = temp_path / 'task.tar.gz'
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(script_path, arcname='script.py')
                
                packages_dir = temp_path / 'packages'
                if packages_dir.exists():
                    tar.add(packages_dir, arcname='packages')
            
            # Step 5: Encode for upload
            archive_data = archive_path.read_bytes()
            archive_b64 = base64.b64encode(archive_data).decode('ascii')
            script_hash = hashlib.sha256(archive_data).digest().hex()
            
            print(f"   Bundle size: {len(archive_data) / 1024 / 1024:.2f} MB")
            print(f"   Packages bundled: {len(bundle_info['bundled'])}")
            
            # Step 6: Submit to API
            print(f"\n🚀 Submitting to distributed network...")
            
            task_data = {
                'name': f'Function: {func.__name__}',
                'taskType': 'script_execution',
                'runtime': 'python',
                'executionScript': archive_b64,
                'scriptHash': script_hash,
                'workers': workers,
                'cpuPerWorker': cpu_per_worker,
                'ramPerWorker': ram_per_worker,
                'gpuRequired': gpu,
                'requiresCuda': cuda,
                'storageRequired': storage,
                'timeout': timeout,
                'priority': priority
            }
            
            resp = self.session.post(
                f'{self.base_url}/api/tasks/execute',
                json=task_data,
                timeout=60
            )
            resp.raise_for_status()
            result = resp.json()
            
            if not result.get('success', True):
                raise RuntimeError(f"Task submission failed: {result.get('message')}")
            
            task_id = result['id']
            
            print(f"\n✅ Task submitted!")
            print(f"   Task ID: {task_id}")
            print(f"   Workers requested: {workers}")
            
            if not wait:
                return Task(id=task_id, status='pending')
            
            print(f"\n⏳ Executing on distributed network...\n")
            return self._wait_for_result(task_id)
    
    def _wait_for_result(self, task_id: str) -> Any:
        """Wait for task to complete and return result"""
        last_progress = -1
        
        while True:
            try:
                task = self.get_task(task_id)
                
                # Show progress
                if task.progress != last_progress and task.progress > 0:
                    print(f"Progress: {task.progress:.1f}%", end='\r')
                    last_progress = task.progress
                
                # Check completion
                if task.status == 'completed':
                    print('\r' + ' ' * 40 + '\r', end='')
                    print("✅ Execution completed!\n")
                    
                    result = self.get_result(task_id)
                    
                    # Extract actual result
                    if isinstance(result, dict):
                        return result.get('result', result)
                    return result
                
                # Check failure
                if task.status == 'failed':
                    print(f"\n❌ Task failed: {task.error}")
                    raise RuntimeError(task.error or 'Task failed')
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n⚠️  Interrupted")
                raise
    
    def get_task(self, task_id: str) -> Task:
        """Get task status"""
        resp = self.session.get(f'{self.base_url}/api/tasks/{task_id}', timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        return Task(
            id=data['id'],
            status=data['status'],
            progress=data.get('progressPercent', 0),
            error=data.get('errorMessage')
        )
    
    def get_result(self, task_id: str) -> Any:
        """Get task result"""
        resp = self.session.get(f'{self.base_url}/api/tasks/{task_id}/result', timeout=10)
        resp.raise_for_status()
        
        if 'json' in resp.headers.get('content-type', ''):
            return resp.json()
        return resp.text
    
    def network_stats(self) -> Dict:
        """Get network statistics"""
        resp = self.session.get(f'{self.base_url}/api/stats/network', timeout=10)
        resp.raise_for_status()
        return resp.json()


# ============================================================================
# EXAMPLES
# ============================================================================
def example_usage():
    """Example usage of the SDK"""
    
    # Initialize client
    dx = DistributeX(api_key="your_api_key_here")
    
    # Example 1: Simple computation
    result = dx.run(
        lambda x: x ** 2,
        args=(10,)
    )
    print(f"Result: {result}")
    
    # Example 2: Using third-party packages
    # Make sure you have requests installed: pip install requests
    def fetch_data(url):
        import requests
        response = requests.get(url)
        return {
            'status': response.status_code,
            'length': len(response.text)
        }
    
    result = dx.run(
        fetch_data,
        args=('https://example.com',),
        cpu_per_worker=2
    )
    print(f"Fetch result: {result}")
    
    # Example 3: Multi-worker task
    def process_chunk(data, multiplier):
        return sum(x * multiplier for x in data)
    
    result = dx.run(
        process_chunk,
        args=([1, 2, 3, 4, 5], 10),
        workers=4
    )
    print(f"Processing result: {result}")


if __name__ == '__main__':
    print(f"DistributeX Python SDK v{__version__}")
    print("=" * 60)
    print("\nFeatures:")
    print("✓ Auto-detects packages from your script")
    print("✓ Bundles YOUR installed packages")
    print("✓ No predefined assumptions")
    print("✓ Runs on distributed workers\n")
    print("Get started: pip install distributex-cloud")
    print("Documentation: https://distributex.cloud/docs")
