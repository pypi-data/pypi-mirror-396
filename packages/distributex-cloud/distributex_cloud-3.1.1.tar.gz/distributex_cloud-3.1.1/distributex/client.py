"""
DistributeX Python SDK v5.2 - SMART PRE-INSTALL + AUTO-CLEANUP
===============================================================
✅ Auto-detects ALL imports (no predefined mappings)
✅ Intelligently separates pure-Python vs compiled packages
✅ Pure-Python packages: Bundled from YOUR environment
✅ Compiled packages: PRE-INSTALLED before execution
✅ AUTO-CLEANUP: Removes packages after execution (keeps worker clean)
✅ Architecture-safe (no .so file issues)

Usage:
    from distributex import DistributeX
    
    dx = DistributeX(api_key="your_key")
    
    # Function with numpy (compiled) - pre-installed then cleaned up
    def compute(data):
        import numpy as np
        return np.mean(data)
    
    result = dx.run(compute, args=([1,2,3],))
    
    # Worker flow:
    # 1. Install numpy
    # 2. Execute compute()
    # 3. Remove numpy (cleanup)
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

__version__ = "5.2.0"


# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class Task:
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None


# ============================================================================
# IMPORT DETECTOR
# ============================================================================
class ImportDetector(ast.NodeVisitor):
    """Pure AST-based import detection"""
    
    def __init__(self):
        self.imports = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])
        self.generic_visit(node)
    
    @classmethod
    def detect(cls, code: str) -> Set[str]:
        try:
            tree = ast.parse(code)
            detector = cls()
            detector.visit(tree)
            return detector.imports
        except SyntaxError:
            return set()


# ============================================================================
# PACKAGE FINDER
# ============================================================================
class PackageFinder:
    """Find packages in developer's Python environment"""
    
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
    def is_stdlib(cls, package: str) -> bool:
        return package.lower() in cls.STDLIB
    
    @classmethod
    def find_package_path(cls, package: str) -> Optional[Path]:
        try:
            module = __import__(package)
            if not hasattr(module, '__file__') or module.__file__ is None:
                return None
            
            module_file = Path(module.__file__)
            site_packages = module_file
            
            while site_packages.name not in ['site-packages', 'dist-packages']:
                site_packages = site_packages.parent
                if site_packages.parent == site_packages:
                    return None
            
            package_dir = site_packages / package
            if package_dir.exists() and package_dir.is_dir():
                return package_dir
            
            if module_file.stem == package:
                return module_file
            
            return None
        except ImportError:
            return None


# ============================================================================
# PACKAGE CLASSIFIER
# ============================================================================
class PackageClassifier:
    """Detect compiled vs pure-Python packages"""
    
    @staticmethod
    def is_compiled(package_path: Path) -> bool:
        """Check if package has .so/.pyd/.dll files"""
        if not package_path.exists():
            return False
        
        compiled_extensions = {'.so', '.pyd', '.dll', '.dylib'}
        
        if package_path.is_file():
            return package_path.suffix in compiled_extensions
        
        for file in package_path.rglob('*'):
            if file.suffix in compiled_extensions:
                return True
        
        return False
    
    @classmethod
    def classify_packages(cls, packages: List[str]) -> Tuple[List[str], List[str]]:
        """
        Separate pure-Python from compiled packages.
        Returns: (pure_python, compiled)
        """
        pure_python = []
        compiled = []
        
        for pkg in packages:
            pkg_path = PackageFinder.find_package_path(pkg)
            
            if not pkg_path:
                compiled.append(pkg)  # Can't find it - install on worker
                continue
            
            if cls.is_compiled(pkg_path):
                compiled.append(pkg)
            else:
                pure_python.append(pkg)
        
        return pure_python, compiled


# ============================================================================
# PACKAGE BUNDLER
# ============================================================================
class PackageBundler:
    """Bundle pure-Python packages from local environment"""
    
    @staticmethod
    def copy_package(src: Path, dest: Path) -> int:
        """Copy package, return size in bytes"""
        SKIP = {
            '__pycache__', '*.pyc', '*.pyo', '.git', '.svn',
            'tests', 'test', 'docs', 'doc', 'examples', 'example',
            '.egg-info', '.dist-info'
        }
        
        if src.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            return dest.stat().st_size
        
        dest.mkdir(parents=True, exist_ok=True)
        total_size = 0
        
        for item in src.rglob('*'):
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
        """Bundle pure-Python packages"""
        packages_dir = bundle_dir / 'packages'
        packages_dir.mkdir(parents=True, exist_ok=True)
        
        bundled = []
        missing = []
        total_size = 0
        
        if not packages:
            return {'bundled': [], 'missing': [], 'total_size': 0}
        
        print(f"\n📦 Bundling {len(packages)} pure-Python package(s)...")
        
        for pkg in sorted(packages):
            if PackageFinder.is_stdlib(pkg):
                continue
            
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
        
        if bundled:
            print(f"\n✅ Bundled: {total_size / 1024 / 1024:.2f} MB")
        
        return {
            'bundled': bundled,
            'missing': missing,
            'total_size': total_size
        }


# ============================================================================
# SCRIPT PACKAGER
# ============================================================================
class ScriptPackager:
    """Create executable script with PRE-INSTALL + AUTO-CLEANUP"""
    
    @staticmethod
    def create_executable(func: Callable, args: tuple, kwargs: dict,
                         pure_python_pkgs: List[str],
                         compiled_pkgs: List[str]) -> str:
        """Generate script with pre-install and cleanup"""
        
        func_source = inspect.getsource(func)
        func_name = func.__name__
        
        install_section = ""
        if compiled_pkgs:
            pkg_list = "', '".join(compiled_pkgs)
            install_section = f'''
# PRE-INSTALL COMPILED PACKAGES
COMPILED_PACKAGES = ['{pkg_list}']
INSTALLED_PACKAGES = []

def install_compiled_packages():
    """Pre-install before execution"""
    if not COMPILED_PACKAGES:
        return []
    
    print(f"\\n⚙️  PRE-INSTALLING {{len(COMPILED_PACKAGES)}} package(s)...")
    print(f"   {{', '.join(COMPILED_PACKAGES)}}")
    
    import subprocess
    installed = []
    
    for pkg in COMPILED_PACKAGES:
        try:
            print(f"   {{pkg}}...", end=' ')
            cmd = [sys.executable, '-m', 'pip', 'install', '--quiet', pkg]
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            
            if result.returncode == 0:
                print("✓")
                installed.append(pkg)
            else:
                print("✗")
        except:
            print("✗")
    
    if installed:
        print(f"\\n✅ Installed {{len(installed)}} package(s)")
    return installed

def cleanup_installed_packages():
    """Remove packages after execution"""
    if not INSTALLED_PACKAGES:
        return
    
    print(f"\\n🧹 CLEANUP: Removing {{len(INSTALLED_PACKAGES)}} package(s)...")
    
    import subprocess
    for pkg in INSTALLED_PACKAGES:
        try:
            print(f"   {{pkg}}...", end=' ')
            cmd = [sys.executable, '-m', 'pip', 'uninstall', '-y', '--quiet', pkg]
            subprocess.run(cmd, capture_output=True, timeout=60)
            print("✓")
        except:
            print("✗")
    
    print("✅ Worker cleaned\\n")

# Install NOW
INSTALLED_PACKAGES = install_compiled_packages()
'''
        
        return f'''#!/usr/bin/env python3
"""DistributeX - PRE-INSTALL + AUTO-CLEANUP"""

import sys
import os
import json
import traceback
import atexit
{install_section}
# Bundled packages
packages_dir = os.path.join(os.getcwd(), 'packages')
if os.path.exists(packages_dir):
    sys.path.insert(0, packages_dir)
    print(f"📦 Loaded pure-Python packages")

# Cleanup on exit
atexit.register(cleanup_installed_packages)

# User function
{func_source}

def main():
    args = {repr(args)}
    kwargs = {repr(kwargs)}
    
    print(f"\\n▶️  Executing {func_name}...")
    
    try:
        result = {func_name}(*args, **kwargs)
        
        with open('result.json', 'w') as f:
            json.dump({{'success': True, 'result': result}}, f, indent=2, default=str)
        
        print("\\n✅ Complete!")
        return 0
    except Exception as e:
        with open('result.json', 'w') as f:
            json.dump({{'success': False, 'error': str(e), 'traceback': traceback.format_exc()}}, f, indent=2)
        
        print(f"\\n❌ Error: {{e}}")
        print(traceback.format_exc())
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
'''


# ============================================================================
# MAIN CLIENT
# ============================================================================
class DistributeX:
    """DistributeX Client - Smart Hybrid Package System"""
    
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
        """Run function on distributed network"""
        
        kwargs = kwargs or {}
        
        print(f"\n{'=' * 60}")
        print(f"DISTRIBUTED EXECUTION: {func.__name__}")
        print(f"{'=' * 60}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Detect imports
            print("\n📋 Analyzing dependencies...")
            func_source = inspect.getsource(func)
            detected = ImportDetector.detect(func_source)
            
            third_party = {
                pkg for pkg in detected
                if not PackageFinder.is_stdlib(pkg)
            }
            
            if third_party:
                print(f"   Found: {', '.join(sorted(third_party))}")
            
            # Classify packages
            pure_python, compiled = PackageClassifier.classify_packages(list(third_party))
            
            if pure_python or compiled:
                print(f"\n📦 Classification:")
                if pure_python:
                    print(f"   Pure-Python (bundle): {', '.join(sorted(pure_python))}")
                if compiled:
                    print(f"   Compiled (install): {', '.join(sorted(compiled))}")
            
            # Check local availability
            missing = [pkg for pkg in third_party if not PackageFinder.find_package_path(pkg)]
            
            if missing:
                raise RuntimeError(
                    f"\n❌ Missing in YOUR environment:\n"
                    f"   {', '.join(missing)}\n\n"
                    f"Install: pip install {' '.join(missing)}"
                )
            
            # Bundle pure-Python only
            bundle_info = {'bundled': [], 'missing': [], 'total_size': 0}
            
            if pure_python:
                bundle_info = PackageBundler.bundle(pure_python, temp_path)
                if bundle_info['missing']:
                    compiled.extend(bundle_info['missing'])
            
            # Create script
            script = ScriptPackager.create_executable(
                func, args, kwargs, pure_python, compiled
            )
            
            script_path = temp_path / 'script.py'
            script_path.write_text(script)
            
            # Create archive
            print("\n📦 Creating bundle...")
            archive_path = temp_path / 'task.tar.gz'
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(script_path, arcname='script.py')
                packages_dir = temp_path / 'packages'
                if packages_dir.exists() and bundle_info['bundled']:
                    tar.add(packages_dir, arcname='packages')
            
            archive_data = archive_path.read_bytes()
            archive_b64 = base64.b64encode(archive_data).decode('ascii')
            script_hash = hashlib.sha256(archive_data).digest().hex()
            
            print(f"   Size: {len(archive_data) / 1024 / 1024:.2f} MB")
            
            # Submit
            print(f"\n🚀 Submitting...")
            
            resp = self.session.post(
                f'{self.base_url}/api/tasks/execute',
                json={
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
                },
                timeout=60
            )
            resp.raise_for_status()
            result = resp.json()
            
            task_id = result['id']
            
            print(f"✅ Task ID: {task_id}")
            
            if not wait:
                return Task(id=task_id, status='pending')
            
            print(f"\n⏳ Executing...\n")
            return self._wait_for_result(task_id)
    
    def _wait_for_result(self, task_id: str) -> Any:
        last_progress = -1
        
        while True:
            try:
                task = self.get_task(task_id)
                
                if task.progress != last_progress and task.progress > 0:
                    print(f"Progress: {task.progress:.1f}%", end='\r')
                    last_progress = task.progress
                
                if task.status == 'completed':
                    print('\r' + ' ' * 40 + '\r', end='')
                    print("✅ Completed!\n")
                    result = self.get_result(task_id)
                    return result.get('result', result) if isinstance(result, dict) else result
                
                if task.status == 'failed':
                    print(f"\n❌ Failed: {task.error}")
                    raise RuntimeError(task.error)
                
                time.sleep(5)
            except KeyboardInterrupt:
                print("\n⚠️  Interrupted")
                raise
    
    def get_task(self, task_id: str) -> Task:
        r = self.session.get(f'{self.base_url}/api/tasks/{task_id}', timeout=10)
        r.raise_for_status()
        d = r.json()
        return Task(
            id=d['id'],
            status=d['status'],
            progress=d.get('progressPercent', 0),
            error=d.get('errorMessage')
        )
    
    def get_result(self, task_id: str) -> Any:
        r = self.session.get(f'{self.base_url}/api/tasks/{task_id}/result', timeout=10)
        r.raise_for_status()
        return r.json() if 'json' in r.headers.get('content-type', '') else r.text
    
    def network_stats(self) -> Dict:
        r = self.session.get(f'{self.base_url}/api/stats/network', timeout=10)
        r.raise_for_status()
        return r.json()
