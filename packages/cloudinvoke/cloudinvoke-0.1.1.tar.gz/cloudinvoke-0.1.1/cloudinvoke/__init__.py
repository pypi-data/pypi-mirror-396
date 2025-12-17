"""
CloudInvoke - The easiest way to run code on the cloud

Features:
- Automatic dependency detection and bundling
- Module-level import detection
- Global variable and function capture
- File upload support with automatic detection
- Decorator-based remote execution
- Async execution support
- Full stdout/stderr capture
"""
import requests
import time
import inspect
import textwrap
import ast
import sys
import os
import base64
from pathlib import Path
from typing import Any, Callable, Optional, Set, Tuple, List, Dict
from functools import wraps

__version__ = "0.1.1"
__all__ = ["CloudRunner"]


class CloudRunner:
    """
    Main class for executing functions on RunPod cloud infrastructure.

    Usage:
        runner = CloudRunner(
            api_key="your_api_key",
            endpoint_id="your_endpoint_id"
        )

        @runner.remote
        def my_function(x, y):
            import torch
            return x + y

        result = my_function(5, 3)  # Runs on cloud
    """

    def __init__(
        self,
        api_key: str,
        endpoint_id: str = "yv68hhady2hgii",
        base_url: str = "https://api.runpod.ai/v2",
        poll_interval: float = 1.0,
        timeout: int = 300,
        debug: bool = False,
        auto_upload_files: bool = True,
        base_dir: str = '.'
    ):
        """
        Initialize the CloudRunner.

        Args:
            api_key: RunPod API key
            endpoint_id: RunPod endpoint ID
            base_url: Base URL for RunPod API
            poll_interval: Seconds to wait between status polls
            timeout: Maximum seconds to wait for execution
            debug: If True, print generated code before execution
            auto_upload_files: If True, automatically detect and upload file dependencies
            base_dir: Base directory for resolving file paths
        """
        self.api_key = api_key
        self.endpoint_id = endpoint_id
        self.base_url = base_url
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.debug = debug
        self.auto_upload_files = auto_upload_files
        self.base_dir = Path(base_dir).resolve()

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def _get_function_source(self, func: Callable) -> str:
        """Extract the source code of a function."""
        source = inspect.getsource(func)
        # Remove decorator lines
        lines = source.split('\n')
        filtered_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('@') and 'remote' in stripped:
                continue
            filtered_lines.append(line)

        source = '\n'.join(filtered_lines)
        return textwrap.dedent(source)

    def _extract_imports_from_source(self, source: str) -> Set[str]:
        """
        Extract import statements from source code.
        """
        try:
            tree = ast.parse(source)
        except:
            return set()

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    if alias.name == '*':
                        imports.add(f"from {module} import *")
                    else:
                        imports.add(f"from {module} import {alias.name}")

        return imports

    def _get_used_names(self, source: str) -> Set[str]:
        """
        Get all names used in the source code.
        """
        try:
            tree = ast.parse(source)
        except:
            return set()

        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    used_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    if isinstance(node.func.value, ast.Name):
                        used_names.add(node.func.value.id)

        return used_names

    def _get_module_level_imports(self, func: Callable) -> Set[str]:
        """
        Extract module-level imports from the function's module.

        Returns:
            Set of import statements from the module
        """
        try:
            # Get the module
            module = sys.modules.get(func.__module__)
            if not module:
                return set()

            # Get module source file
            module_file = inspect.getsourcefile(module)
            if not module_file or not os.path.exists(module_file):
                return set()

            # Read and parse module source
            with open(module_file, 'r', encoding='utf-8') as f:
                module_source = f.read()

            # Extract imports
            imports = self._extract_imports_from_source(module_source)

            # Filter out cloudrun/cloudinvoke imports (not needed on cloud side)
            filtered_imports = set()
            for imp in imports:
                if 'cloudrun' not in imp.lower() and 'cloudinvoke' not in imp.lower():
                    filtered_imports.add(imp)

            return filtered_imports
        except:
            return set()

    def _serialize_value(self, value: Any) -> Optional[str]:
        """
        Serialize a value to Python code string.

        Returns:
            String representation of the value, or None if not serializable
        """
        import json

        # Handle None, bool, int, float, str
        if value is None or isinstance(value, (bool, int, float)):
            return repr(value)

        if isinstance(value, str):
            return repr(value)

        # Handle lists, tuples, sets
        if isinstance(value, (list, tuple, set)):
            try:
                return repr(value)
            except:
                return None

        # Handle dicts
        if isinstance(value, dict):
            try:
                return repr(value)
            except:
                return None

        # For other types, try repr
        try:
            # Test if repr is valid by trying to evaluate it
            repr_str = repr(value)
            # Basic sanity check - if it contains object address, it's probably not serializable
            if '<' in repr_str and 'object at 0x' in repr_str:
                return None
            return repr_str
        except:
            return None

    def _collect_all_dependencies(self, func: Callable) -> Tuple[Set[str], List[str], Dict[str, Any]]:
        """
        Recursively collect all dependencies (imports, helper functions/classes, and global variables).

        Returns:
            tuple: (set of import statements, list of dependency sources, dict of global variables)
        """
        all_imports = set()
        all_dependencies = []
        global_vars = {}
        processed = set()  # Track processed objects to avoid infinite loops

        # First, collect module-level imports
        module_imports = self._get_module_level_imports(func)
        all_imports.update(module_imports)

        def process_function(f: Callable):
            # Avoid reprocessing
            if id(f) in processed:
                return
            processed.add(id(f))

            # Get function source
            try:
                source = self._get_function_source(f)
            except:
                return

            # Collect imports from this function
            imports = self._extract_imports_from_source(source)
            all_imports.update(imports)

            # Get names used in this function
            used_names = self._get_used_names(source)

            # Get the function's globals
            func_globals = f.__globals__

            # Process each used name
            for name in used_names:
                if name in func_globals:
                    obj = func_globals[name]

                    # Check if it's a user-defined function
                    if inspect.isfunction(obj) and obj.__module__ == f.__module__:
                        if id(obj) not in processed:
                            try:
                                dep_source = inspect.getsource(obj)
                                dep_source = textwrap.dedent(dep_source)
                                all_dependencies.append(dep_source)

                                # Recursively process this dependency
                                process_function(obj)
                            except:
                                pass

                    # Check if it's a user-defined class
                    elif inspect.isclass(obj) and obj.__module__ == f.__module__:
                        if id(obj) not in processed:
                            processed.add(id(obj))
                            try:
                                dep_source = inspect.getsource(obj)
                                dep_source = textwrap.dedent(dep_source)
                                all_dependencies.append(dep_source)

                                # Collect imports from class source
                                class_imports = self._extract_imports_from_source(dep_source)
                                all_imports.update(class_imports)
                            except:
                                pass

                    # Check if it's a global variable (not a built-in, not a module, not already processed)
                    elif (not inspect.isbuiltin(obj) and
                          not inspect.ismodule(obj) and
                          not inspect.isfunction(obj) and
                          not inspect.isclass(obj) and
                          name not in global_vars):
                        # Try to serialize the value
                        serialized = self._serialize_value(obj)
                        if serialized is not None:
                            global_vars[name] = serialized

        # Start processing from the main function
        process_function(func)

        return all_imports, all_dependencies, global_vars

    def _detect_file_references(self, code: str) -> Set[Path]:
        """
        Detect file references in code.

        Returns:
            Set of file paths referenced in the code
        """
        file_patterns = [
            r'open\s*\(\s*["\']([^"\']+)["\']',  # open('file.txt')
            r'Path\s*\(\s*["\']([^"\']+)["\']',  # Path('file.txt')
            r'read_csv\s*\(\s*["\']([^"\']+)["\']',  # pd.read_csv('file.csv')
            r'read_excel\s*\(\s*["\']([^"\']+)["\']',  # pd.read_excel('file.xlsx')
            r'read_json\s*\(\s*["\']([^"\']+)["\']',  # pd.read_json('file.json')
            r'read_parquet\s*\(\s*["\']([^"\']+)["\']',  # pd.read_parquet('file.parquet')
            r'load\s*\(\s*["\']([^"\']+)["\']',  # np.load('file.npy')
            r'loadtxt\s*\(\s*["\']([^"\']+)["\']',  # np.loadtxt('file.txt')
            r'torch\.load\s*\(\s*["\']([^"\']+)["\']',  # torch.load('model.pth')
        ]

        import re
        file_paths = set()

        for pattern in file_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                file_path = match.group(1)
                path = Path(file_path)

                # Try absolute path
                if path.is_absolute() and path.exists():
                    file_paths.add(path)
                    continue

                # Try relative to base directory
                abs_path = (self.base_dir / path).resolve()
                if abs_path.exists():
                    file_paths.add(abs_path)

        return file_paths

    def _encode_files(self, file_paths: Set[Path]) -> List[Dict[str, str]]:
        """
        Encode files to base64 for upload.

        Args:
            file_paths: Set of file paths to encode

        Returns:
            List of dicts with 'path' and 'content' (base64)
        """
        files = []

        for file_path in file_paths:
            try:
                # Get relative path from base directory
                try:
                    rel_path = file_path.relative_to(self.base_dir)
                except ValueError:
                    # File is outside base directory, use filename only
                    rel_path = file_path.name

                # Read and encode file
                with open(file_path, 'rb') as f:
                    content = f.read()
                    content_b64 = base64.b64encode(content).decode('utf-8')

                files.append({
                    'path': str(rel_path).replace('\\', '/'),  # Use forward slashes
                    'content': content_b64
                })

                if self.debug:
                    print(f"[DEBUG] Added file: {rel_path} ({len(content)} bytes)")

            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Error encoding file {file_path}: {e}")

        return files

    def _build_execution_code(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict
    ) -> Tuple[str, str, list, dict]:
        """
        Build the code and execution parameters for the cloud.

        Returns:
            Tuple of (code, function_name, function_args, function_kwargs)
        """
        # Collect all imports, dependencies, and global variables recursively
        imports, dependency_sources, global_vars = self._collect_all_dependencies(func)

        # Get function source
        func_source = self._get_function_source(func)

        # Build the execution call
        func_name = func.__name__

        # Build complete code
        code_parts = []

        # Add collected imports
        if imports:
            code_parts.append('\n'.join(sorted(imports)))

        # Add global variables
        if global_vars:
            global_vars_code = []
            for var_name, var_value in sorted(global_vars.items()):
                global_vars_code.append(f"{var_name} = {var_value}")
            code_parts.append('\n'.join(global_vars_code))

        # Add dependencies (helper functions/classes)
        if dependency_sources:
            code_parts.append('\n\n'.join(dependency_sources))

        # Add function definition
        code_parts.append(func_source)

        code = '\n\n'.join(code_parts)

        return code, func_name, list(args), kwargs

    def _execute_on_cloud(
        self,
        code: str,
        function_name: str = None,
        function_args: list = None,
        function_kwargs: dict = None,
        files: List[Dict[str, str]] = None
    ) -> Any:
        """
        Execute code on RunPod and return the result.

        Args:
            code: Python code to execute
            function_name: Name of function to call
            function_args: Positional arguments for the function
            function_kwargs: Keyword arguments for the function
            files: List of files to upload (base64 encoded)

        Returns:
            Function result
        """
        # Submit job
        data = {
            "input": {
                "code": code
            }
        }

        # Add function execution parameters if specified
        if function_name:
            data["input"]["function_name"] = function_name
            data["input"]["function_args"] = function_args or []
            data["input"]["function_kwargs"] = function_kwargs or {}

        # Add files if specified
        if files:
            data["input"]["files"] = files

        if self.debug:
            print(f"[DEBUG] Payload:")
            print(f"  - Code: {len(code)} bytes")
            if function_name:
                print(f"  - Function: {function_name}()")
            if files:
                print(f"  - Files: {len(files)} file(s)")

        run_url = f"{self.base_url}/{self.endpoint_id}/run"
        response = requests.post(run_url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to submit job: {response.text}")

        request_id = response.json()['id']

        if self.debug:
            print(f"[DEBUG] Request ID: {request_id}")

        # Poll for result
        start_time = time.time()
        status_url = f"{self.base_url}/{self.endpoint_id}/status/{request_id}"

        while True:
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"Execution timeout after {self.timeout} seconds")

            result = requests.get(status_url, headers=self.headers)

            if result.status_code != 200:
                raise RuntimeError(f"Failed to get status: {result.text}")

            status = result.json()

            if status['status'] == 'COMPLETED':
                output = status.get('output', {})

                # Handle new response format
                if isinstance(output, dict):
                    # Check for errors
                    if output.get('error'):
                        error_msg = output['error']
                        stderr = output.get('stderr', '')
                        raise RuntimeError(f"Execution error: {error_msg}\nStderr: {stderr}")

                    # Print stdout if any
                    if output.get('stdout'):
                        print(output['stdout'], end='')

                    # Print stderr if any (non-error)
                    if output.get('stderr') and not output.get('error'):
                        print(output['stderr'], end='', file=sys.stderr)

                    return output.get('result')

                return output

            elif status['status'] == 'FAILED':
                error_msg = status.get('error', 'Unknown error')
                raise RuntimeError(f"Execution failed: {error_msg}")

            time.sleep(self.poll_interval)

    def remote(self, func: Callable) -> Callable:
        """
        Decorator to mark a function for remote execution.

        Usage:
            @runner.remote
            def my_function(x, y):
                return x + y
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build execution code and parameters
            code, func_name, func_args, func_kwargs = self._build_execution_code(func, args, kwargs)

            # Detect and encode files if auto_upload_files is enabled
            files = []
            if self.auto_upload_files:
                file_paths = self._detect_file_references(code)
                if file_paths:
                    files = self._encode_files(file_paths)
                    if self.debug:
                        print(f"[DEBUG] Detected {len(file_paths)} file dependencies")

            # Debug output
            if self.debug:
                print("\n" + "=" * 70)
                print("GENERATED CODE FOR CLOUD EXECUTION:")
                print("=" * 70)
                print(code)
                print("=" * 70)
                print(f"Function: {func_name}()")
                print(f"Args: {func_args}")
                print(f"Kwargs: {func_kwargs}")
                if files:
                    print(f"Files: {[f['path'] for f in files]}")
                print("=" * 70 + "\n")

            # Execute on cloud
            return self._execute_on_cloud(
                code=code,
                function_name=func_name,
                function_args=func_args,
                function_kwargs=func_kwargs,
                files=files
            )

        # Store original function for inspection
        wrapper.__wrapped__ = func

        return wrapper

    def remote_async(self, func: Callable) -> Callable:
        """
        Decorator for async remote execution (returns request ID immediately).

        Usage:
            @runner.remote_async
            def my_function(x, y):
                return x + y

            request_id = my_function(5, 3)
            result = runner.get_result(request_id)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build execution code and parameters
            code, func_name, func_args, func_kwargs = self._build_execution_code(func, args, kwargs)

            # Detect and encode files if auto_upload_files is enabled
            files = []
            if self.auto_upload_files:
                file_paths = self._detect_file_references(code)
                if file_paths:
                    files = self._encode_files(file_paths)

            # Submit job
            data = {
                "input": {
                    "code": code,
                    "function_name": func_name,
                    "function_args": func_args,
                    "function_kwargs": func_kwargs
                }
            }

            # Add files if any
            if files:
                data["input"]["files"] = files

            run_url = f"{self.base_url}/{self.endpoint_id}/run"
            response = requests.post(run_url, headers=self.headers, json=data)

            if response.status_code != 200:
                raise RuntimeError(f"Failed to submit job: {response.text}")

            return response.json()['id']

        wrapper.__wrapped__ = func
        return wrapper

    def get_result(self, request_id: str, wait: bool = True) -> Any:
        """
        Get the result of an async execution.

        Args:
            request_id: The request ID returned from remote_async
            wait: If True, poll until complete. If False, return current status.
        """
        status_url = f"{self.base_url}/{self.endpoint_id}/status/{request_id}"

        if not wait:
            result = requests.get(status_url, headers=self.headers)
            if result.status_code != 200:
                raise RuntimeError(f"Failed to get status: {result.text}")
            return result.json()

        # Poll for result
        start_time = time.time()

        while True:
            if time.time() - start_time > self.timeout:
                raise TimeoutError(f"Execution timeout after {self.timeout} seconds")

            result = requests.get(status_url, headers=self.headers)

            if result.status_code != 200:
                raise RuntimeError(f"Failed to get status: {result.text}")

            status = result.json()

            if status['status'] == 'COMPLETED':
                output = status.get('output', {})

                # Handle new response format
                if isinstance(output, dict):
                    # Check for errors
                    if output.get('error'):
                        error_msg = output['error']
                        stderr = output.get('stderr', '')
                        raise RuntimeError(f"Execution error: {error_msg}\nStderr: {stderr}")

                    # Print stdout if any
                    if output.get('stdout'):
                        print(output['stdout'], end='')

                    # Print stderr if any (non-error)
                    if output.get('stderr') and not output.get('error'):
                        print(output['stderr'], end='', file=sys.stderr)

                    return output.get('result')

                return output

            elif status['status'] == 'FAILED':
                error_msg = status.get('error', 'Unknown error')
                raise RuntimeError(f"Execution failed: {error_msg}")

            time.sleep(self.poll_interval)
