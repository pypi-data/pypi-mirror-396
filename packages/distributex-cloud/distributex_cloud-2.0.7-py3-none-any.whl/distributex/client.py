"""
DistributeX Python SDK v2.1 - WITH PACKAGE BUNDLING
====================================================
Workers use packages from developer's environment
No installation needed on worker side
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
import subprocess
import tempfile
import tarfile
import shutil
from typing import Any, Callable, Optional, Dict, List, Set
from dataclasses import dataclass
import textwrap

__version__ = "2.1.0"

@dataclass
class Task:
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None

# ============================================================================
# PACKAGE BUNDLER - Bundles developer's packages with the script
# ============================================================================
class PackageBundler:
    """Bundles installed packages from developer's environment"""

    @staticmethod
    def get_package_info(package_name: str) -> Optional[Dict]:
        """Get information about an installed package"""
        try:
            import importlib.metadata
            dist = importlib.metadata.distribution(package_name)
            return {
                'name': dist.metadata['Name'],
                'version': dist.version,
                'location': str(dist.locate_file('')),
            }
        except:
            return None
        @staticmethod
        def get_all_dependencies(packages: List[str]) -> Set[str]:
            """Get all packages and their dependencies"""
            all_packages = set(packages)

            try:
                import importlib.metadata

                def get_deps(pkg_name: str):
                    try:
                        dist = importlib.metadata.distribution(pkg_name)
                        if dist.requires:
                            for req in dist.requires:
                                # Parse requirement string (e.g., "requests>=2.0.0")
                                dep_name = req.split()[0].split('>')[0].split('<')[0].split('=')[0].split('!')[0]
                                if dep_name not in all_packages:
                                    all_packages.add(dep_name)
                                    get_deps(dep_name)  # Recursive
                    except:
                        pass

                for pkg in list(packages):
                    get_deps(pkg)

            except:
                pass

            return all_packages

        @staticmethod
        def bundle_packages(packages: List[str], bundle_dir: str) -> str:
            """Bundle packages WITH all dependencies"""

            # Get all dependencies
            all_packages = PackageBundler.get_all_dependencies(packages)

            print(f"📦 Bundling {len(all_packages)} packages (including dependencies)...")

            packages_dir = os.path.join(bundle_dir, 'packages')
            os.makedirs(packages_dir, exist_ok=True)

            # Download all packages at once (more efficient)
            try:
                print(f"   Downloading packages...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'download',
                    '--dest', packages_dir,
                    *all_packages  # Download all at once
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️  Some packages failed to download: {e}")

            # Create tarball
            tarball_path = os.path.join(bundle_dir, 'packages.tar.gz')
            with tarfile.open(tarball_path, 'w:gz') as tar:
                tar.add(packages_dir, arcname='packages')

            package_files = [f for f in os.listdir(packages_dir) 
                             if f.endswith(('.whl', '.tar.gz'))]
            size_mb = os.path.getsize(tarball_path) / (1024 * 1024)
            print(f"✅ Bundled {len(package_files)} packages ({size_mb:.2f} MB)")

            return tarball_path

    @staticmethod
    def create_install_script(packages: List[str]) -> str:
        """Create script to install bundled packages on worker"""
        return f"""
# Install bundled packages (offline)
import subprocess
import sys
import os

packages_dir = os.path.join(os.getcwd(), 'packages')
if os.path.exists(packages_dir):
    print("Installing bundled packages...")

    # Find all .whl and .tar.gz files
    package_files = []
    for file in os.listdir(packages_dir):
        if file.endswith(('.whl', '.tar.gz')):
            package_files.append(os.path.join(packages_dir, file))

    if package_files:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            '--no-index',  # Don't use PyPI
            '--find-links', packages_dir,  # Use local files
            '--quiet',
            '--disable-pip-version-check',
            *package_files
        ], check=True)
        print(f"✅ Installed {{len(package_files)}} bundled packages")
    else:
        print("⚠️  No package files found in bundle")
else:
    print("⚠️  No packages directory found - packages may need to be installed")
"""

# ============================================================================
# IMPORT DETECTOR
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
                'argparse', 'getpass', 'tempfile', 'shutil', 'glob', 'fnmatch'
            }

            return {pkg for pkg in all_imports if pkg not in stdlib}

        except SyntaxError:
            return set()

# ============================================================================
# FUNCTION SERIALIZER - WITH PACKAGE BUNDLING
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
    def extract_dependencies(func: Callable) -> Set[str]:
        source = FunctionSerializer.extract_function_source(func)
        return ImportDetector.detect_imports(source)

    @staticmethod
    def create_executable_script(
        func: Callable,
        args: tuple,
        kwargs: dict,
        bundle_packages: bool = True
    ) -> Dict[str, Any]:
        """Create executable script with bundled packages"""

        func_source = FunctionSerializer.extract_function_source(func)
        func_name = func.__name__

        # Detect required packages
        packages = FunctionSerializer.extract_dependencies(func)

        # Separate import lines from function body
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

        # Build script
        script_parts = [
            '#!/usr/bin/env python3',
            '"""',
            f'DistributeX Task - Function: {func_name}',
            f'SDK Version: {__version__}',
            'Using bundled packages from developer environment',
            '"""',
            '',
        ]

        # Add package installer for bundled packages
        if bundle_packages and packages:
            script_parts.extend([
                '# Install bundled packages',
                PackageBundler.create_install_script(list(packages)),
                '',
            ])

        # Add imports
        if import_lines:
            script_parts.append('# Required imports')
            script_parts.extend(import_lines)
            script_parts.append('')

        script_parts.extend([
            'import json',
            'import traceback',
            '',
        ])

        # Add function
        script_parts.append('# User function')
        script_parts.extend(function_body)
        script_parts.append('')

        # Add execution wrapper
        script_parts.extend([
            '# Execution wrapper',
            'def main():',
            '    """Execute function and save results"""',
            f'    args = {repr(args)}',
            f'    kwargs = {repr(kwargs)}',
            '',
            f'    print(f"Executing {func_name} with bundled packages")',
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
            '        print(f"✅ Execution complete!")',
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
            '    import sys',
            '    sys.exit(main())',
        ])

        script = '\n'.join(script_parts)

        return {
            'script': script,
            'packages': sorted(packages),
            'hash': hashlib.sha256(script.encode()).hexdigest(),
            'bundle_packages': bundle_packages
        }

# ============================================================================
# MAIN CLIENT - WITH PACKAGE BUNDLING
# ============================================================================
class DistributeX:
    """DistributeX Client with Package Bundling"""

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
            print(f"DistributeX SDK v{__version__} - Package Bundling Enabled")
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
            wait: bool = True,
            bundle_packages: bool = True) -> Any:
        """
        Run a function on the distributed network

        Args:
            bundle_packages: If True, bundles packages from your environment
                           If False, workers will install packages from PyPI
        """
        kwargs = kwargs or {}

        print(f"\n{'=' * 60}")
        print(f"SUBMITTING TASK: {func.__name__}")
        print(f"{'=' * 60}")

        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Serialize function
            serialized = FunctionSerializer.create_executable_script(
                func, args, kwargs, bundle_packages=bundle_packages
            )

            script_source = serialized['script']
            detected_packages = serialized['packages']
            script_hash = serialized['hash']

            if detected_packages:
                print(f"📦 Detected packages: {', '.join(detected_packages)}")

            # Bundle packages if requested
            packages_tarball = None
            if bundle_packages and detected_packages:
                packages_tarball = PackageBundler.bundle_packages(
                    list(detected_packages),
                    temp_dir
                )

            # Create combined archive (script + packages)
            archive_path = os.path.join(temp_dir, 'task.tar.gz')
            with tarfile.open(archive_path, 'w:gz') as tar:
                # Add script
                script_path = os.path.join(temp_dir, 'script.py')
                with open(script_path, 'w') as f:
                    f.write(script_source)
                tar.add(script_path, arcname='script.py')

                # Add bundled packages if available
                if packages_tarball and os.path.exists(packages_tarball):
                    with tarfile.open(packages_tarball, 'r:gz') as pkg_tar:
                        for member in pkg_tar.getmembers():
                            tar.addfile(member, pkg_tar.extractfile(member))

            # Read archive as base64
            with open(archive_path, 'rb') as f:
                archive_data = f.read()

            archive_b64 = base64.b64encode(archive_data).decode('ascii')
            archive_size = len(archive_data) / (1024 * 1024)

            print(f"📤 Uploading task bundle ({archive_size:.2f} MB)...")

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
                'bundledPackages': bundle_packages,
                'packageList': list(detected_packages) if detected_packages else []
            }

            try:
                resp = self.session.post(
                    f"{self.base_url}/api/tasks/execute",
                    json=task_data,
                    timeout=60  # Longer timeout for upload
                )
                resp.raise_for_status()
                result = resp.json()

            except requests.exceptions.RequestException as e:
                print(f"❌ API request failed: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response: {e.response.text[:500]}")
                raise RuntimeError(f"Failed to submit task: {e}")

            if not result.get('success', True):
                error_msg = result.get('message', 'Unknown error')
                raise RuntimeError(f"Task submission failed: {error_msg}")

            task_id = result.get('id')
            if not task_id:
                raise RuntimeError("API did not return task ID")

            print(f"✅ Task submitted successfully!")
            print(f"   Task ID: {task_id}")
            print(f"   Status: {result.get('status', 'pending')}")

            if bundle_packages and detected_packages:
                print(f"   📦 Using bundled packages from your environment")
            else:
                print(f"   📥 Worker will install packages from PyPI")

            task = Task(id=task_id, status=result.get('status', 'pending'))

            if not wait:
                return task

            print(f"\n⏳ Waiting for execution...\n")
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
                print(f"\nInterrupted")
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
    api_key = os.getenv('DISTRIBUTEX_API_KEY')
    if not api_key:
        print("❌ Set DISTRIBUTEX_API_KEY environment variable")
        sys.exit(1)

    dx = DistributeX(api_key=api_key, debug=True)

    print("\n" + "=" * 60)
    print("Example: Using bundled packages from your environment")
    print("=" * 60)

    def compute_with_numpy(n):
        import numpy as np
        print(f"Using NumPy version: {np.__version__}")

        # Heavy computation
        matrix = np.random.rand(n, n)
        result = np.linalg.eigvals(matrix)

        return f"Computed eigenvalues for {n}x{n} matrix using YOUR NumPy installation"

    # Run with bundled packages
    result = dx.run(
        compute_with_numpy,
        args=(1000,),
        cpu_per_worker=4,
        ram_per_worker=4096,
        bundle_packages=True,  # Use your installed packages
        wait=True
    )

    print(f"\n✅ Result: {result}")
    print("\n🎉 Worker used your bundled NumPy - no installation needed!")
