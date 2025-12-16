"""
DistributeX Python SDK v4.0 - TRUE LOCAL PACKAGE BUNDLING
==========================================================
Bundles packages from YOUR local Python environment (not PyPI)
Workers use your exact package versions to execute code
"""

import os
import json
import time
import requests
import inspect
import hashlib
import base64
import ast
import sys
import subprocess
import tempfile
import tarfile
import shutil
from pathlib import Path
from typing import Any, Callable, Optional, Dict, List, Set
from dataclasses import dataclass
import textwrap

__version__ = "4.0.1"


@dataclass
class Task:
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None


# ============================================================================
# IMPORT DETECTOR - Finds all packages used in code
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

            # Python standard library (don't bundle these)
            stdlib = {
                'os', 'sys', 're', 'json', 'time', 'datetime', 'math',
                'random', 'collections', 'itertools', 'functools', 'operator',
                'pathlib', 'io', 'typing', 'dataclasses', 'enum', 'abc',
                'contextlib', 'copy', 'pickle', 'hashlib', 'base64', 'struct',
                'array', 'queue', 'threading', 'multiprocessing', 'subprocess',
                'socket', 'ssl', 'http', 'urllib', 'email', 'html', 'xml',
                'csv', 'configparser', 'logging', 'unittest', 'doctest',
                'argparse', 'getpass', 'tempfile', 'shutil', 'glob', 'fnmatch',
                'warnings', 'traceback', 'inspect', 'types', 'weakref', 'gc',
                'codecs', 'string', 'textwrap', 'unicodedata', 'stringprep'
            }

            return {pkg for pkg in all_imports if pkg not in stdlib}

        except SyntaxError:
            return set()


# ============================================================================
# LOCAL PACKAGE BUNDLER - Uses developer's installed packages
# ============================================================================
class LocalPackageBundler:
    """Bundles packages from developer's LOCAL environment"""

    @staticmethod
    def find_package_location(package_name: str) -> Optional[Path]:
        """Find where a package is installed locally"""
        
        # Map common aliases to real package names
        aliases = {
            'bs4': 'beautifulsoup4',
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
        }
        
        real_name = aliases.get(package_name, package_name)
        
        try:
            # Try to import and get file location
            module = __import__(real_name.replace('-', '_'))
            if hasattr(module, '__file__') and module.__file__:
                pkg_path = Path(module.__file__).parent
                
                # For packages, go up to site-packages
                while pkg_path.name not in ['site-packages', 'dist-packages']:
                    if pkg_path.parent == pkg_path:  # Reached root
                        break
                    pkg_path = pkg_path.parent
                    
                # Now find the actual package directory
                pkg_root = pkg_path / package_name
                if pkg_root.exists():
                    return pkg_root
                    
                # Try with real name
                pkg_root = pkg_path / real_name.replace('-', '_')
                if pkg_root.exists():
                    return pkg_root
                
                # For single-file modules
                if module.__file__.endswith('.py'):
                    return Path(module.__file__)
                    
        except (ImportError, AttributeError, TypeError):
            pass
        
        # Fallback: use pip show
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', real_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Location:'):
                        location = Path(line.split(':', 1)[1].strip())
                        pkg_path = location / package_name.replace('-', '_')
                        if pkg_path.exists():
                            return pkg_path
        except Exception:
            pass
        
        return None

    @staticmethod
    def get_package_dependencies(package_name: str) -> Set[str]:
        """Get all dependencies of a package"""
        deps = set()
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Requires:'):
                        requires = line.split(':', 1)[1].strip()
                        if requires:
                            deps.update(r.strip() for r in requires.split(','))
        except Exception:
            pass
        
        return deps

    @staticmethod
    def copy_directory(src: Path, dst: Path, exclude_patterns: Set[str] = None):
        """Copy directory with exclusions"""
        if exclude_patterns is None:
            exclude_patterns = {
                '__pycache__', '*.pyc', '*.pyo', '.git', '.svn',
                'tests', 'test', 'docs', 'doc', 'examples', 'example'
            }
        
        dst.mkdir(parents=True, exist_ok=True)
        
        for item in src.iterdir():
            # Skip excluded
            if any(pattern in item.name for pattern in exclude_patterns):
                continue
            
            if item.is_dir():
                LocalPackageBundler.copy_directory(
                    item, 
                    dst / item.name, 
                    exclude_patterns
                )
            else:
                shutil.copy2(item, dst / item.name)

    @classmethod
    def bundle_packages(cls, packages: List[str], bundle_dir: Path) -> Dict[str, Any]:
        """Bundle packages from local environment"""
        
        print(f"\n📦 Bundling {len(packages)} package(s) from your environment...")
        
        packages_dir = bundle_dir / 'packages'
        packages_dir.mkdir(parents=True, exist_ok=True)
        
        bundled = []
        missing = []
        total_size = 0
        
        # Get all dependencies recursively
        all_packages = set(packages)
        for pkg in packages:
            deps = cls.get_package_dependencies(pkg)
            all_packages.update(deps)
        
        print(f"   Including dependencies: {len(all_packages)} total packages")
        
        for package_name in sorted(all_packages):
            pkg_location = cls.find_package_location(package_name)
            
            if pkg_location and pkg_location.exists():
                dest_path = packages_dir / package_name.replace('-', '_')
                
                try:
                    if pkg_location.is_dir():
                        cls.copy_directory(pkg_location, dest_path)
                        size = sum(
                            f.stat().st_size 
                            for f in dest_path.rglob('*') 
                            if f.is_file()
                        )
                    else:
                        # Single file module
                        shutil.copy2(pkg_location, dest_path.with_suffix('.py'))
                        size = dest_path.with_suffix('.py').stat().st_size
                    
                    bundled.append({
                        'name': package_name,
                        'size': size,
                        'location': str(pkg_location)
                    })
                    total_size += size
                    
                    print(f"   ✓ {package_name} ({size / 1024:.1f} KB)")
                    
                except Exception as e:
                    print(f"   ✗ {package_name}: {e}")
                    missing.append(package_name)
            else:
                print(f"   ⚠ {package_name} not found locally")
                missing.append(package_name)
        
        # Create a requirements.txt for fallback installation
        if missing:
            req_file = packages_dir / 'requirements.txt'
            req_file.write_text('\n'.join(missing))
            print(f"\n   ℹ️  {len(missing)} package(s) will be installed from PyPI on worker")
        
        print(f"\n✅ Bundle complete: {total_size / 1024 / 1024:.2f} MB")
        
        return {
            'bundled': bundled,
            'missing': missing,
            'total_size': total_size,
            'total_packages': len(all_packages)
        }


# ============================================================================
# FUNCTION SERIALIZER
# ============================================================================
class FunctionSerializer:
    """Serialize Python functions with bundled packages"""

    @staticmethod
    def extract_function_source(func: Callable) -> str:
        try:
            source = inspect.getsource(func)
            return textwrap.dedent(source)
        except (OSError, TypeError):
            func_name = getattr(func, '__name__', 'function')
            return f"def {func_name}(*args, **kwargs):\n    raise NotImplementedError('Cannot serialize this function type')\n"

    @staticmethod
    def create_executable_script(
        func: Callable,
        args: tuple,
        kwargs: dict,
        packages: List[str]
    ) -> str:
        """Create executable script that uses bundled packages"""

        func_source = FunctionSerializer.extract_function_source(func)
        func_name = func.__name__

        script_parts = [
            '#!/usr/bin/env python3',
            '"""',
            f'DistributeX Task - Function: {func_name}',
            f'SDK Version: {__version__}',
            'Using packages bundled from developer environment',
            '"""',
            '',
            'import sys',
            'import os',
            'import json',
            'import traceback',
            '',
        ]

        # Add package setup logic (WITHOUT pip install)
        if packages:
            script_parts.extend([
                '# Setup bundled packages (NO PIP INSTALL)',
                'def setup_packages():',
                '    """Add bundled packages to Python path"""',
                '    import sys',
                '    import os',
                '    ',
                '    packages_dir = os.path.join(os.getcwd(), "packages")',
                '    ',
                '    if os.path.exists(packages_dir):',
                '        print("📦 Setting up bundled packages...")',
                '        ',
                '        # Add packages directory to Python path',
                '        if packages_dir not in sys.path:',
                '            sys.path.insert(0, packages_dir)',
                '        ',
                '        print(f"   Added to PYTHONPATH: {packages_dir}")',
                '        ',
                '        # List what we have',
                '        try:',
                '            bundled = [d for d in os.listdir(packages_dir) ',
                '                      if os.path.isdir(os.path.join(packages_dir, d))]',
                '            print(f"   Bundled packages: {len(bundled)}")',
                '            for pkg in bundled[:5]:  # Show first 5',
                '                print(f"     • {pkg}")',
                '        except Exception:',
                '            pass',
                '        ',
                '        print("✅ Package setup complete")',
                '    else:',
                '        print("⚠️  No packages directory found")',
                '        print("   This may cause import errors if dependencies are missing")',
                '',
                'setup_packages()',
                '',
            ])

        # Add user function
        script_parts.extend([
            '# User function',
            func_source,
            '',
        ])

        # Add execution wrapper
        script_parts.extend([
            '# Execution wrapper',
            'def main():',
            '    """Execute function and save results"""',
            f'    args = {repr(args)}',
            f'    kwargs = {repr(kwargs)}',
            '',
            f'    print(f"▶️  Executing {func_name}...")',
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
            '        print("✅ Execution complete!")',
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
            '        print(f"❌ Error: {error_msg}")',
            '        print(error_trace)',
            '        return 1',
            '',
            'if __name__ == "__main__":',
            '    sys.exit(main())',
        ])

        return '\n'.join(script_parts)

# ============================================================================
# MAIN CLIENT
# ============================================================================
class DistributeX:
    """DistributeX Client with Local Package Bundling"""

    def __init__(self, api_key=None, base_url="https://distributex.cloud", debug=False):
        self.api_key = api_key or os.getenv("DISTRIBUTEX_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key required!\n\n"
                "Option 1 - Pass directly:\n"
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
            print(f"DistributeX SDK v{__version__} - Local Package Bundling")
            print(f"Connected to: {self.base_url}")

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
        Run a function on the distributed network using LOCAL packages
        
        Your installed packages are bundled and sent to workers
        Workers use YOUR exact package versions
        """
        kwargs = kwargs or {}

        print(f"\n{'=' * 60}")
        print(f"DISTRIBUTED EXECUTION: {func.__name__}")
        print(f"{'=' * 60}")

        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Detect required packages
            func_source = FunctionSerializer.extract_function_source(func)
            detected_packages = ImportDetector.detect_imports(func_source)
            
            if detected_packages:
                print(f"\n📦 Detected {len(detected_packages)} package(s):")
                for pkg in sorted(detected_packages):
                    print(f"   • {pkg}")
            
            # Bundle packages from local environment
            bundle_info = None
            if detected_packages:
                bundle_info = LocalPackageBundler.bundle_packages(
                    list(detected_packages),
                    temp_path
                )
            
            # Create execution script
            script_content = FunctionSerializer.create_executable_script(
                func, args, kwargs, list(detected_packages)
            )
            
            script_path = temp_path / 'script.py'
            script_path.write_text(script_content)
            
            # Create archive (script + bundled packages)
            archive_path = temp_path / 'task.tar.gz'
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                # Add script
                tar.add(script_path, arcname='script.py')
                
                # Add bundled packages directory if exists
                packages_dir = temp_path / 'packages'
                if packages_dir.exists():
                    tar.add(packages_dir, arcname='packages')
            
            # Read as base64
            archive_data = archive_path.read_bytes()
            archive_b64 = base64.b64encode(archive_data).decode('ascii')
            archive_size = len(archive_data) / (1024 * 1024)
            
            script_hash = hashlib.sha256(script_content.encode()).hexdigest()
            
            print(f"\n📤 Uploading task bundle ({archive_size:.2f} MB)...")
            
            # Submit task
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
                'priority': priority,
                'bundledPackages': True,
                'packageList': list(detected_packages) if detected_packages else []
            }
            
            try:
                resp = self.session.post(
                    f"{self.base_url}/api/tasks/execute",
                    json=task_data,
                    timeout=60
                )
                resp.raise_for_status()
                result = resp.json()
                
            except requests.exceptions.RequestException as e:
                print(f"\n❌ API request failed: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response: {e.response.text[:500]}")
                raise RuntimeError(f"Failed to submit task: {e}")
            
            if not result.get('success', True):
                error_msg = result.get('message', 'Unknown error')
                raise RuntimeError(f"Task submission failed: {error_msg}")
            
            task_id = result.get('id')
            if not task_id:
                raise RuntimeError("API did not return task ID")
            
            print(f"\n✅ Task submitted successfully!")
            print(f"   Task ID: {task_id}")
            print(f"   Workers: {workers}")
            
            if bundle_info:
                print(f"   Bundled: {bundle_info['total_packages']} packages ({bundle_info['total_size'] / 1024 / 1024:.2f} MB)")
                if bundle_info['missing']:
                    print(f"   Missing: {len(bundle_info['missing'])} (will install from PyPI)")
            
            task = Task(id=task_id, status=result.get('status', 'pending'))
            
            if not wait:
                return task
            
            print(f"\n⏳ Executing on distributed network...\n")
            return self._wait_for_result(task_id)

    def _wait_for_result(self, task_id: str) -> Any:
        """Wait for task completion and return result"""
        last_progress = -1

        while True:
            try:
                task = self.get_task(task_id)

                # Show progress
                if task.progress != last_progress and task.progress > 0:
                    print(f"Progress: {task.progress:.1f}%", end='\r', flush=True)
                    last_progress = task.progress

                # Check completion
                if task.status == 'completed':
                    print('\r' + ' ' * 40 + '\r', end='', flush=True)
                    print(f"✅ Execution completed!\n")
                    result = self.get_result(task_id)

                    # Extract clean result
                    if isinstance(result, dict):
                        if 'output' in result:
                            return result['output']
                        if 'result' in result:
                            return result['result']
                        return result
                    return result

                # Check failure
                if task.status == 'failed':
                    print(f"\n❌ Task failed: {task.error}")
                    raise RuntimeError(task.error or 'Task failed')

                time.sleep(5)

            except KeyboardInterrupt:
                print(f"\n⚠️  Interrupted")
                raise

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
            r.raise_for_status()

            content_type = r.headers.get('content-type', '')

            if 'json' in content_type:
                data = r.json()
                if isinstance(data, dict) and 'result' in data:
                    return data['result']
                return data

            return r.text

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get result: {e}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == '__main__':
    import os
    
    # Example: Install packages locally first
    print("=" * 60)
    print("SETUP: Install packages locally")
    print("=" * 60)
    print("Run: pip install requests beautifulsoup4 numpy pandas")
    print("Then your code will use YOUR installed versions\n")
    
    api_key = os.getenv('DISTRIBUTEX_API_KEY')
    if not api_key:
        print("❌ Set DISTRIBUTEX_API_KEY environment variable")
        exit(1)
    
    dx = DistributeX(api_key=api_key, debug=True)
    
    # Example function that uses packages installed on YOUR system
    def scrape_and_analyze(url):
        """
        This function uses packages from YOUR environment:
        - requests (your version)
        - beautifulsoup4 (your version)
        
        Workers will use the EXACT versions you have installed locally!
        """
        import requests
        from bs4 import BeautifulSoup
        
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=30)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        return {
            "url": url,
            "title": title_text,
            "status_code": response.status_code,
            "link_count": len(links),
            "first_links": links[:10]
        }
    
    # Run on distributed network using YOUR local packages
    print("\n" + "=" * 60)
    print("EXECUTION: Running with your local packages")
    print("=" * 60)
    
    result = dx.run(
        scrape_and_analyze,
        args=("https://example.com",),
        cpu_per_worker=2,
        ram_per_worker=2048,
        workers=1,
        wait=True
    )
    
    print(f"\n📊 Result:")
    print(json.dumps(result, indent=2))
    
    print("\n🎉 Success! Worker used packages from YOUR environment!")
    print("   Benefits:")
    print("   ✓ No PyPI downloads needed")
    print("   ✓ Consistent package versions")
    print("   ✓ Works offline")
    print("   ✓ Your compute, worker's resources")
