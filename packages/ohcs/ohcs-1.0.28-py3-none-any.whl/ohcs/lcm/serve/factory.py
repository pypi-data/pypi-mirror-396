# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import ast
import importlib
import inspect
import logging
import os
import re
import sys
from types import ModuleType
import typing
from typing import Any, Dict, Optional

from ohcs.common.utils import OhcsSdkException

log = logging.getLogger(__name__)

_interface_cache: Dict[str, Any] = {}
_pyi_file_path = os.path.join(os.path.dirname(__file__), "..", "LifecycleManagement.pyi")


def _load_pyi_cache():
    global _interface_cache

    if _interface_cache:
        return

    try:
        with open(_pyi_file_path, "r") as f:
            content = f.read()

        tree = ast.parse(content)

        function_names = []
        signatures = {}
        required_functions = []
        imports = {}  # Map short names to full module paths

        for node in ast.walk(tree):
            # Extract imports to resolve type names
            if isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    name = alias.name
                    asname = alias.asname if alias.asname else name
                    # Build full path for imported names
                    if module:
                        imports[asname] = f"{module}.{name}"
                    else:
                        imports[asname] = name

            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                function_names.append(node.name)

                params = []
                for arg in node.args.args:
                    param_info = {
                        "name": arg.arg,
                        "annotation": (ast.unparse(arg.annotation) if arg.annotation else None),
                    }
                    params.append(param_info)

                return_type = ast.unparse(node.returns) if node.returns else None

                signatures[node.name] = {
                    "parameters": params,
                    "return_type": return_type,
                    "line_number": node.lineno,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                }

            elif (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "required_functions"
                and isinstance(node.value, (ast.List, ast.Tuple))
            ):
                # Extracts the list of required function names as strings
                required_functions = [
                    elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                ]

        _interface_cache = {
            "function_names": function_names,
            "signatures": signatures,
            "required_functions": required_functions,
            "imports": imports,
            "file_path": _pyi_file_path,
        }

    except Exception as e:
        raise RuntimeError(f"Failed to parse .pyi file {_pyi_file_path}: {e}")


def _normalize_type_string(type_str: Optional[str], imports: Dict[str, str]) -> Optional[str]:
    """
    Normalize a type string by resolving imports to fully qualified names.

    Args:
        type_str: The type string to normalize (e.g., "VmInfo" or "ohcs.lcm.models.VmInfo")
        imports: Dictionary mapping short names to full module paths (e.g., {"VmInfo": "ohcs.lcm.models.VmInfo"})

    Returns:
        Normalized type string with whitespace removed and all names fully qualified
    """
    if not type_str:
        return None

    # Remove all whitespace
    normalized = type_str.replace(" ", "")

    # Replace short names with their fully qualified versions
    # Process in order of longest names first to avoid partial replacements
    for short_name in sorted(imports.keys(), key=len, reverse=True):
        full_path = imports[short_name]
        # Use word boundary to match only complete names
        pattern = r"\b" + re.escape(short_name) + r"\b"
        # Only replace if not already part of a longer qualified name
        # Check if the short name is preceded by a module path (indicating it's already qualified)
        if not re.search(r"\w+\." + re.escape(short_name) + r"\b", normalized):
            normalized = re.sub(pattern, full_path, normalized)

    return normalized


def _validate_implementation(module) -> tuple[list[dict[str, Any]], bool]:
    _load_pyi_cache()

    all_function_names = _interface_cache["function_names"]
    required_functions = _interface_cache["required_functions"]
    signatures = _interface_cache["signatures"]

    # Get only functions (not classes) that are directly defined in the module (not imported)
    module_functions = {
        name
        for name, obj in inspect.getmembers(module, callable)
        if not name.startswith("_")
        and not inspect.isclass(obj)
        and hasattr(obj, "__module__")
        and obj.__module__ == module.__name__
    }

    report = []
    error = False
    for func_name in all_function_names:
        if func_name not in module_functions:
            if func_name in required_functions:
                report.append({"func_name": func_name, "message": "missing (required)", "error": 2})
                error = True
            else:
                report.append({"func_name": func_name, "message": "missing (optional)", "error": 1})
            continue

        func = getattr(module, func_name)
        try:
            sig = inspect.signature(func)
            pyi_sig = signatures[func_name]
            expect_async = pyi_sig["is_async"]
            if expect_async != inspect.iscoroutinefunction(func):
                report.append(
                    {
                        "func_name": func_name,
                        "message": f"{func_name}: Expected async={expect_async}, got {not expect_async}",
                        "error": 2,
                    }
                )
                error = True
                continue
            if len(sig.parameters) != len(pyi_sig["parameters"]):
                report.append(
                    {
                        "func_name": func_name,
                        "message": f"{func_name}: parameter count mismatch. Expected {len(pyi_sig['parameters'])}, got {len(sig.parameters)}",
                        "error": 2,
                    }
                )
                error = True
                continue

            pyi_param_names = [p["name"] for p in pyi_sig["parameters"]]
            actual_param_names = list(sig.parameters.keys())

            if pyi_param_names != actual_param_names:
                report.append(
                    {
                        "func_name": func_name,
                        "message": f"{func_name}: parameter names mismatch. Expected {pyi_param_names}, got {actual_param_names}",
                        "error": 2,
                    }
                )
                error = True
                continue

            # Validate return type annotation
            expected_return_type = pyi_sig["return_type"]
            actual_return_annotation = sig.return_annotation

            # Convert actual annotation to string for comparison
            # Track whether the annotation is missing vs explicitly None
            is_annotation_missing = actual_return_annotation is inspect.Parameter.empty
            if is_annotation_missing:
                actual_return_type = None
            else:
                # Get the string representation of the annotation
                # We need to handle this carefully to preserve generic types like dict[str, Any]

                def _type_to_string(tp) -> str:
                    """Convert a type annotation to a string representation matching ast.unparse format"""
                    # Handle None type
                    if tp is type(None):
                        return "None"

                    # Check if it's a generic type (has origin and args)
                    origin = typing.get_origin(tp)
                    args = typing.get_args(tp)

                    if origin is not None:
                        # Handle generic types like dict[str, Any], list[VmInfo], Optional[X]
                        origin_name = getattr(origin, "__name__", str(origin))

                        # Special handling for Union (which Optional uses)
                        if origin is typing.Union:
                            # Check if it's Optional (Union[X, None])
                            if len(args) == 2 and type(None) in args:
                                non_none = args[0] if args[1] is type(None) else args[1]
                                return f"Optional[{_type_to_string(non_none)}]"
                            else:
                                args_str = ", ".join(_type_to_string(arg) for arg in args)
                                return f"Union[{args_str}]"

                        if args:
                            args_str = ", ".join(_type_to_string(arg) for arg in args)
                            return f"{origin_name}[{args_str}]"
                        else:
                            return origin_name
                    else:
                        # Not a generic type
                        # Check for typing special forms like Any
                        if hasattr(tp, "__module__") and tp.__module__ == "typing":
                            # Handle typing.Any and other special forms
                            type_str = str(tp)
                            if type_str.startswith("typing."):
                                return type_str[7:]  # Remove 'typing.' prefix
                            return type_str

                        # Regular class/type
                        if hasattr(tp, "__module__") and hasattr(tp, "__qualname__"):
                            if tp.__module__ == "builtins":
                                return tp.__qualname__
                            else:
                                return f"{tp.__module__}.{tp.__qualname__}"
                        elif hasattr(tp, "__name__"):
                            return tp.__name__
                        else:
                            return str(tp)

                try:
                    actual_return_type = _type_to_string(actual_return_annotation)
                except Exception:
                    # Fallback to string representation
                    actual_return_type = str(actual_return_annotation)

            # Normalize type strings for comparison using import resolution
            imports = _interface_cache.get("imports", {})
            expected_normalized = _normalize_type_string(expected_return_type, imports)
            actual_normalized = _normalize_type_string(actual_return_type, imports)

            if expected_normalized != actual_normalized:
                # Provide a clear error message depending on whether annotation is missing
                if is_annotation_missing:
                    error_msg = f"{func_name}: return type mismatch. Expected {expected_return_type}, got no type annotation (missing)"
                else:
                    error_msg = (
                        f"{func_name}: return type mismatch. Expected {expected_return_type}, got {actual_return_type}"
                    )
                report.append({"func_name": func_name, "message": error_msg, "error": 2})
                error = True
                continue

            report.append({"func_name": func_name, "message": "valid", "error": 0})
        except Exception as e:
            report.append(
                {"func_name": func_name, "message": f"Could not validate signature for {func_name}: {e}", "error": 2}
            )
            error = True
            continue

    # Check for extra functions in the module that are not defined in the .pyi file
    for func_name in module_functions:
        if func_name not in all_function_names:
            report.append(
                {
                    "func_name": func_name,
                    "message": "unexpected public function (not defined in interface)",
                    "error": 2,
                }
            )
            error = True

    if error:
        _log_validation_result(module.__name__, report, error)
        raise OhcsSdkException(f"Invalid plugin implementation: {module.__name__}.")
    return report, error


def _log_validation_result(name: str, report: list[dict[str, Any]], error: bool):
    log.info(f"----- Validation Result of {name} -----")
    for item in report:
        if item["error"] == 2:
            log.error(f"  {item['func_name']: <20}: {item['message']}")
        elif item["error"] == 1:
            log.info(f"  {item['func_name']: <20}: {item['message']}")
        else:
            log.info(f"  {item['func_name']: <20}: {item['message']}")
    log.info("----- Validation Result END -----")


_instance_cache: Dict[str, Any] = {}


def get_lifecycle_manager(module_name: str) -> ModuleType:
    if module_name in _instance_cache:
        return _instance_cache[module_name]

    module = importlib.import_module(module_name)
    _validate_implementation(module)
    _instance_cache[module_name] = module
    return module


def init(custom_plugin_path: str, custom_plugin_name: str):
    _register_custom_plugin(custom_plugin_path, custom_plugin_name)
    _register_plugin("ohcs.lcm.plugin.simulator")
    _register_plugin("ohcs.lcm.plugin.terraform")


def _register_plugin(module_name: str):
    if module_name in _instance_cache:
        error_message = f"Plugin alias already registered: {module_name}"
        raise OhcsSdkException(error_message)

    module = importlib.import_module(module_name)
    _validate_implementation(module)
    _instance_cache[module_name] = module
    log.info(f"Plugin registered: {module_name}")
    module.init()


def _register_custom_plugin(plugin_path: str, plugin_name: str):
    if not plugin_name:
        log.info("No plugin name specified. Skipping plugin registration.")
        return
    if plugin_path:
        abs_path = os.path.abspath(plugin_path)
        if not os.path.exists(abs_path):
            log.warning(f"Plugin path does not exist: {abs_path}")
            return
        sys.path.append(abs_path)
        log.info("Using custom plugin path: {abs_path}")
    else:
        log.info("No custom plugin path specified. Using default path.")
        abs_path = "<default>"

    try:
        module = importlib.import_module(plugin_name)
    except Exception as e:
        log.warning(f"Plugin module import failed: {plugin_name}: {e}.")
        log.warning(
            "If a custom plugin is installed, please check if the plugin name is correct and the plugin path is valid."
        )
        return

    report, error = _validate_implementation(module)
    _log_validation_result(abs_path + "/" + plugin_name, report, error)
    _instance_cache[plugin_name] = module
    log.info(f"Custom plugin implementation registered: {abs_path}/{plugin_name}")
    module.init()
