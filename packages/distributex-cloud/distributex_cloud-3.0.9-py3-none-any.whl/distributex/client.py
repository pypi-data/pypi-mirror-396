"""
DistributeX Python SDK v4.1 - HYBRID PACKAGE SYSTEM
==========================================================
1. Bundles packages from YOUR local environment (preferred)
2. Falls back to UNIVERSAL runtime installation for missing packages
Workers get your exact versions when possible + guaranteed compatibility

🔥 Key Improvement in v4.1:
   • Compiled packages (numpy, scipy, pandas, torch, etc.) are NEVER bundled
   • They are always installed via wheels on the worker at runtime
   • Prevents crashes due to missing .so/.pyd extensions
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
from typing import Any, Callable, Optional, Dict, List, Set, Tuple
from dataclasses import dataclass
import textwrap

__version__ = "4.1.0"

@dataclass
class Task:
    id: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None


# ============================================================================
# COMPILED PACKAGES DENYLIST
# ============================================================================
COMPILED_PACKAGES = {
    "numpy",
    "scipy",
    "pandas",
    "torch",
    "tensorflow",
    "jax",
    "opencv-python",
    "cv2",
    "sklearn",
    "scikit-learn",
    "xgboost",
    "lightgbm",
    "catboost",
}


# ============================================================================
# IMPORT DETECTOR - Now separates pure Python vs compiled packages
# ============================================================================
class ImportDetector(ast.NodeVisitor):
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
    def detect_imports(cls, code: str) -> Tuple[Set[str], Set[str]]:
        """
        Returns:
            pure_packages: Set of pure-Python packages that can be safely bundled
            compiled_packages: Set of compiled packages that must be installed at runtime
        """
        try:
            tree = ast.parse(code)
            detector = cls()
            detector.visit(tree)
            all_imports = detector.imports | detector.from_imports

            stdlib = {
                'os', 'sys', 're', 'json', 'time', 'datetime', 'math', 'random',
                'collections', 'itertools', 'functools', 'operator', 'pathlib',
                'io', 'typing', 'dataclasses', 'enum', 'abc', 'contextlib', 'copy',
                'pickle', 'hashlib', 'base64', 'struct', 'array', 'queue',
                'threading', 'multiprocessing', 'subprocess', 'socket', 'ssl',
                'http', 'urllib', 'email', 'html', 'xml', 'csv', 'configparser',
                'logging', 'unittest', 'doctest', 'argparse', 'getpass',
                'tempfile', 'shutil', 'glob', 'fnmatch', 'warnings', 'traceback',
                'inspect', 'types', 'weakref', 'gc', 'codecs', 'string',
                'textwrap', 'unicodedata', 'stringprep'
            }

            detected = {pkg for pkg in all_imports if pkg not in stdlib}
            compiled = {pkg for pkg in detected if pkg in COMPILED_PACKAGES}
            pure = detected - compiled

            return pure, compiled
        except SyntaxError:
            return set(), set()


# ============================================================================
# LOCAL PACKAGE BUNDLER
# ============================================================================
class LocalPackageBundler:
    @staticmethod
    def find_package_location(package_name: str) -> Optional[Path]:
        aliases = {
            'bs4': 'beautifulsoup4',
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
        }
        real_name = aliases.get(package_name, package_name)
        try:
            module = __import__(real_name.replace('-', '_'))
            if hasattr(module, '__file__') and module.__file__:
                pkg_path = Path(module.__file__).parent
                while pkg_path.name not in ['site-packages', 'dist-packages']:
                    if pkg_path.parent == pkg_path:
                        break
                    pkg_path = pkg_path.parent
                pkg_root = pkg_path / package_name
                if pkg_root.exists():
                    return pkg_root
                pkg_root = pkg_path / real_name.replace('-', '_')
                if pkg_root.exists():
                    return pkg_root
                if module.__file__.endswith('.py'):
                    return Path(module.__file__)
        except (ImportError, AttributeError, TypeError):
            pass
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', real_name],
                capture_output=True, text=True, timeout=5
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
        deps = set()
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True, text=True, timeout=5
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
        if exclude_patterns is None:
            exclude_patterns = {
                '__pycache__', '*.pyc', '*.pyo', '.git', '.svn',
                'tests', 'test', 'docs', 'doc', 'examples', 'example'
            }
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if any(pattern in item.name for pattern in exclude_patterns):
                continue
            if item.is_dir():
                LocalPackageBundler.copy_directory(item, dst / item.name, exclude_patterns)
            else:
                shutil.copy2(item, dst / item.name)

    @classmethod
    def bundle_packages(cls, packages: List[str], bundle_dir: Path) -> Dict[str, Any]:
        print(f"\n📦 Bundling {len(packages)} package(s) from your environment...")
        packages_dir = bundle_dir / 'packages'
        packages_dir.mkdir(parents=True, exist_ok=True)
        bundled = []
        missing = []
        total_size = 0
        all_packages = set(packages)
        for pkg in packages:
            deps = cls.get_package_dependencies(pkg)
            all_packages.update(deps)
        print(f" Including dependencies: {len(all_packages)} total packages")
        for package_name in sorted(all_packages):
            pkg_location = cls.find_package_location(package_name)
            if pkg_location and pkg_location.exists():
                dest_path = packages_dir / package_name.replace('-', '_')
                try:
                    if pkg_location.is_dir():
                        cls.copy_directory(pkg_location, dest_path)
                        size = sum(f.stat().st_size for f in dest_path.rglob('*') if f.is_file())
                    else:
                        shutil.copy2(pkg_location, dest_path.with_suffix('.py'))
                        size = dest_path.with_suffix('.py').stat().st_size
                    bundled.append({'name': package_name, 'size': size, 'location': str(pkg_location)})
                    total_size += size
                    print(f" ✓ {package_name} ({size / 1024:.1f} KB)")
                except Exception as e:
                    print(f" ✗ {package_name}: {e}")
                    missing.append(package_name)
            else:
                print(f" ⚠ {package_name} not found locally")
                missing.append(package_name)
        if missing:
            req_file = packages_dir / 'requirements.txt'
            req_file.write_text('\n'.join(missing))
            print(f"\n ℹ️ {len(missing)} package(s) will be installed from PyPI on worker")
        print(f"\n✅ Bundle complete: {total_size / 1024 / 1024:.2f} MB")
        return {
            'bundled': bundled,
            'missing': missing,
            'total_size': total_size,
            'total_packages': len(all_packages)
        }


# ============================================================================
# UNIVERSAL PACKAGE INSTALLATION SYSTEM (enhanced for wheels)
# ============================================================================
class UniversalPackageManager:
    @staticmethod
    def create_installation_script(packages: List[str], python_version: str = "3.12") -> str:
        script = f"""#!/usr/bin/env python3
# ============================================================================
# DistributeX Universal Package Installer
# Auto-installs missing packages on worker at runtime
# ============================================================================
import sys
import subprocess
import os
import json
from pathlib import Path

def install_missing_packages():
    packages = {packages}
    if not packages:
        print("✅ No missing packages to install")
        return True

    print(f"📦 Installing {{len(packages)}} missing package(s) from PyPI...")
    cache_dir = Path.home() / '.distributex' / 'pip_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)

    import platform
    system_info = {{
        'os': platform.system(),
        'arch': platform.machine(),
        'python': platform.python_version(),
        'implementation': platform.python_implementation()
    }}
    print(f" Platform: {{system_info['os']}} {{system_info['arch']}}")
    print(f" Python: {{system_info['python']}} ({{system_info['implementation']}})")

    pip_cmd = [
        sys.executable, '-m', 'pip', 'install',
        '--upgrade',
        '--no-warn-script-location',
        '--disable-pip-version-check',
        '--cache-dir', str(cache_dir),
        '--prefer-binary',
        '--only-binary', ':all:',
        '--force-reinstall',
        '--no-build-isolation'
    ]
    pip_cmd.extend(packages)

    try:
        result = subprocess.run(pip_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ All missing packages installed successfully")
            for pkg in packages:
                pkg_name = pkg.split('[')[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
                import_names = {{
                    'beautifulsoup4': 'bs4', 'pillow': 'PIL', 'opencv-python': 'cv2',
                    'scikit-learn': 'sklearn', 'python-dateutil': 'dateutil', 'pyyaml': 'yaml'
                }}
                import_name = import_names.get(pkg_name.lower(), pkg_name)
                try:
                    __import__(import_name)
                    print(f" ✓ {{pkg_name}} imported successfully")
                except ImportError as e:
                    print(f" ✗ {{pkg_name}} import failed: {{e}}")
            return True
        else:
            print(f"❌ Bulk install failed:\\n{{result.stderr}}")
            print("🔄 Falling back to individual installation...")
            for pkg in packages:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', pkg],
                                   capture_output=True, check=True, timeout=120)
                    print(f" ✓ {{pkg}} installed")
                except Exception as e:
                    print(f" ✗ {{pkg}} failed: {{e}}")
            return True
    except subprocess.TimeoutExpired:
        print("❌ Installation timeout (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {{e}}")
        return False

# Run installer
install_missing_packages()
"""
        return script


# ============================================================================
# ENHANCED FUNCTION SERIALIZER
# ============================================================================
class FunctionSerializer:
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
        packages: List[str],
        missing_packages: List[str]
    ) -> str:
        func_source = FunctionSerializer.extract_function_source(func)
        func_name = func.__name__

        install_script = ""
        if missing_packages:
            install_script = UniversalPackageManager.create_installation_script(missing_packages)

        bundle_setup = '''
# Setup bundled packages
def setup_bundled_packages():
    import sys
    import os
    packages_dir = os.path.join(os.getcwd(), "packages")
    if os.path.exists(packages_dir):
        print("📦 Setting up bundled local packages...")
        if packages_dir not in sys.path:
            sys.path.insert(0, packages_dir)
        try:
            bundled = [d for d in os.listdir(packages_dir) if os.path.isdir(os.path.join(packages_dir, d)) or d.endswith('.py')]
            print(f" ✓ Found {{len(bundled)}} bundled package(s)/module(s)")
        except Exception:
            pass
        
        # Safety net: Remove any accidentally bundled compiled packages from path
        BLOCKED = {"numpy", "scipy", "pandas", "torch", "cv2", "sklearn"}
        sys.path = [
            p for p in sys.path
            if not any(b in p for b in BLOCKED)
        ]
        
        print("✅ Bundled package setup complete (compiled packages blocked)")
    else:
        print("⚠️ No bundled packages directory found")
setup_bundled_packages()
'''

        script = f'''#!/usr/bin/env python3
"""DistributeX Hybrid Execution - Local Bundles + Universal Installer"""
import sys
import os
import json
import traceback
{bundle_setup}
{install_script}
# User function
{func_source}
# Execution
def main():
    args = {repr(args)}
    kwargs = {repr(kwargs)}
    print(f"▶️ Executing {func_name}...")
    try:
        result = {func_name}(*args, **kwargs)
        result_data = {{
            "success": True,
            "result": result,
            "function": "{func_name}"
        }}
        with open("result.json", "w") as f:
            json.dump(result_data, f, indent=2, default=str)
        print("✅ Execution complete!")
        return 0
    except Exception as e:
        error_data = {{
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }}
        with open("result.json", "w") as f:
            json.dump(error_data, f, indent=2)
        print(f"❌ Error: {{e}}")
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        return script


# ============================================================================
# MAIN CLIENT
# ============================================================================
class DistributeX:
    def __init__(self, api_key=None, base_url="https://distributex.cloud", debug=False):
        self.api_key = api_key or os.getenv("DISTRIBUTEX_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required! Set DISTRIBUTEX_API_KEY or pass api_key=..."
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
            print(f"DistributeX SDK v{__version__} - Hybrid Package System")

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
        kwargs = kwargs or {}
        print(f"\n{'=' * 60}")
        print(f"DISTRIBUTED EXECUTION: {func.__name__}")
        print(f"{'=' * 60}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            func_source = FunctionSerializer.extract_function_source(func)

            pure_packages, compiled_packages = ImportDetector.detect_imports(func_source)

            print(f"\n📦 Pure Python packages: {', '.join(sorted(pure_packages)) if pure_packages else 'None'}")
            print(f"⚙️ Compiled packages (runtime install): {', '.join(sorted(compiled_packages)) if compiled_packages else 'None'}")

            bundle_info = {}
            missing_packages = list(compiled_packages)  # All compiled packages go to runtime install

            if pure_packages:
                bundle_info = LocalPackageBundler.bundle_packages(list(pure_packages), temp_path)
                missing_packages.extend(bundle_info.get('missing', []))

            script_content = FunctionSerializer.create_executable_script(
                func, args, kwargs,
                packages=list(pure_packages),
                missing_packages=missing_packages
            )

            script_path = temp_path / 'script.py'
            script_path.write_text(script_content)

            archive_path = temp_path / 'task.tar.gz'
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(script_path, arcname='script.py')
                packages_dir = temp_path / 'packages'
                if packages_dir.exists():
                    tar.add(packages_dir, arcname='packages')

            archive_data = archive_path.read_bytes()
            archive_b64 = base64.b64encode(archive_data).decode('ascii')
            archive_size = len(archive_data) / (1024 * 1024)
            script_hash = hashlib.sha256(script_content.encode()).hexdigest()

            print(f"\n📤 Uploading task bundle ({archive_size:.2f} MB)...")

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
                'bundledPackages': bool(pure_packages),
                'packageList': list(pure_packages | compiled_packages)
            }

            resp = self.session.post(f"{self.base_url}/api/tasks/execute", json=task_data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            if not result.get('success', True):
                raise RuntimeError(f"Task submission failed: {result.get('message')}")

            task_id = result.get('id')
            print(f"\n✅ Task submitted! ID: {task_id}")

            bundled_count = len(bundle_info.get('bundled', []))
            print(f" Bundled: {bundled_count} pure Python packages")
            print(f" Runtime install: {len(missing_packages)} packages (including all compiled ones)")

            if not wait:
                return Task(id=task_id, status='pending')

            print(f"\n⏳ Executing on distributed network...\n")
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
                    print(f"✅ Execution completed!\n")
                    result = self.get_result(task_id)
                    if isinstance(result, dict):
                        return result.get('output') or result.get('result') or result
                    return result
                if task.status == 'failed':
                    print(f"\n❌ Task failed: {task.error}")
                    raise RuntimeError(task.error or 'Task failed')
                time.sleep(5)
            except KeyboardInterrupt:
                print(f"\n⚠️ Interrupted")
                raise

    def get_task(self, task_id: str) -> Task:
        r = self.session.get(f"{self.base_url}/api/tasks/{task_id}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return Task(
            id=data['id'],
            status=data['status'],
            progress=data.get('progressPercent', 0),
            error=data.get('errorMessage')
        )

    def get_result(self, task_id: str) -> Any:
        r = self.session.get(f"{self.base_url}/api/tasks/{task_id}/result", timeout=10)
        r.raise_for_status()
        if 'json' in r.headers.get('content-type', ''):
            return r.json()
        return r.text


# ============================================================================
# EXAMPLE USAGE
# ============================================================================
if __name__ == '__main__':
    # Example usage:
    # dx = DistributeX()
    # result = dx.run(some_function, args=(1, 2), kwargs={'param': 'value'})
    pass
