import os
import sys
import platform
import re
import base64
import shutil
import json
import hashlib
import inspect
import functools
import logging
import traceback
from typing import Optional, List, Dict, Any, Union, Callable, get_type_hints
from datetime import datetime

__version__ = "0.5.0"
__name__ = "MEROAI"
__author__ = "MERO"
__contact__ = "Telegram: @QP4RM"


def mero_schema(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"MEROAI.{func.__name__}")
        start_time = datetime.now()
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} completed in {elapsed:.4f}s")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            logger.error(traceback.format_exc())
            raise
    wrapper._mero_schema = True
    wrapper._original_func = func
    return wrapper


def mero_log(level: str = "INFO") -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(f"MEROAI.{func.__name__}")
            log_level = getattr(logging, level.upper(), logging.INFO)
            logger.log(log_level, f"[MEROAI] Entering {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.log(log_level, f"[MEROAI] Exiting {func.__name__} successfully")
                return result
            except Exception as e:
                logger.error(f"[MEROAI] {func.__name__} raised {type(e).__name__}: {e}")
                raise
        return wrapper
    return decorator


def mero_validate(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for param_name, param_value in bound.arguments.items():
            if param_name in hints and param_name != 'return':
                expected_type = hints[param_name]
                if hasattr(expected_type, '__origin__'):
                    continue
                if not isinstance(param_value, expected_type):
                    raise TypeError(f"Parameter '{param_name}' expected {expected_type.__name__}, got {type(param_value).__name__}")
        return func(*args, **kwargs)
    return wrapper


class DocstringParser:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def parse_numpy(self, docstring: str) -> Dict[str, Any]:
        result = {"style": "numpy", "sections": {}}
        if not docstring:
            return result
        sections = re.split(r'\n\s*([A-Za-z]+)\s*\n\s*[-=]+\s*\n', docstring)
        if sections[0].strip():
            result["sections"]["summary"] = sections[0].strip()
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_name = sections[i].lower()
                section_content = sections[i + 1].strip()
                result["sections"][section_name] = self._parse_section(section_content)
        return result

    def parse_rst(self, docstring: str) -> Dict[str, Any]:
        result = {"style": "rst", "sections": {}}
        if not docstring:
            return result
        lines = docstring.strip().split('\n')
        current_section = "summary"
        content = []
        for line in lines:
            param_match = re.match(r':param\s+(\w+):\s*(.*)', line)
            type_match = re.match(r':type\s+(\w+):\s*(.*)', line)
            return_match = re.match(r':returns?:\s*(.*)', line)
            rtype_match = re.match(r':rtype:\s*(.*)', line)
            raises_match = re.match(r':raises?\s+(\w+):\s*(.*)', line)
            if param_match:
                if "parameters" not in result["sections"]:
                    result["sections"]["parameters"] = {}
                result["sections"]["parameters"][param_match.group(1)] = {"description": param_match.group(2)}
            elif type_match:
                if "parameters" in result["sections"] and type_match.group(1) in result["sections"]["parameters"]:
                    result["sections"]["parameters"][type_match.group(1)]["type"] = type_match.group(2)
            elif return_match:
                result["sections"]["returns"] = return_match.group(1)
            elif rtype_match:
                result["sections"]["return_type"] = rtype_match.group(1)
            elif raises_match:
                if "raises" not in result["sections"]:
                    result["sections"]["raises"] = []
                result["sections"]["raises"].append({"exception": raises_match.group(1), "description": raises_match.group(2)})
            else:
                content.append(line)
        if content:
            result["sections"]["summary"] = '\n'.join(content).strip()
        return result

    def parse_google(self, docstring: str) -> Dict[str, Any]:
        result = {"style": "google", "sections": {}}
        if not docstring:
            return result
        sections = re.split(r'\n\s*(Args|Returns|Raises|Yields|Examples?|Attributes|Note|Warning):\s*\n', docstring, flags=re.IGNORECASE)
        if sections[0].strip():
            result["sections"]["summary"] = sections[0].strip()
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_name = sections[i].lower()
                section_content = sections[i + 1].strip()
                result["sections"][section_name] = section_content
        return result

    def _parse_section(self, content: str) -> List[Dict[str, str]]:
        items = []
        current_item = None
        for line in content.split('\n'):
            match = re.match(r'^(\w+)\s*:\s*(.*)', line.strip())
            if match:
                if current_item:
                    items.append(current_item)
                current_item = {"name": match.group(1), "description": match.group(2)}
            elif current_item and line.strip():
                current_item["description"] += " " + line.strip()
        if current_item:
            items.append(current_item)
        return items

    def generate_numpy(self, func_name: str, params: Dict[str, str], returns: str, description: str = "") -> str:
        doc = f'"""{description}\n\n' if description else '"""\n'
        if params:
            doc += "Parameters\n----------\n"
            for name, ptype in params.items():
                doc += f"{name} : {ptype}\n    Description of {name}\n"
        if returns:
            doc += f"\nReturns\n-------\n{returns}\n    Description of return value\n"
        doc += '"""'
        return doc

    def generate_rst(self, func_name: str, params: Dict[str, str], returns: str, description: str = "") -> str:
        doc = f'"""{description}\n\n' if description else '"""\n'
        for name, ptype in params.items():
            doc += f":param {name}: Description of {name}\n"
            doc += f":type {name}: {ptype}\n"
        if returns:
            doc += f":returns: Description of return value\n"
            doc += f":rtype: {returns}\n"
        doc += '"""'
        return doc

    def to_json_schema(self, func: Callable) -> Dict[str, Any]:
        schema = {
            "type": "function",
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        try:
            hints = get_type_hints(func)
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name in ('self', 'cls'):
                    continue
                param_type = hints.get(param_name, Any)
                json_type = self._python_type_to_json(param_type)
                schema["parameters"]["properties"][param_name] = {"type": json_type}
                if param.default is inspect.Parameter.empty:
                    schema["parameters"]["required"].append(param_name)
            if 'return' in hints:
                schema["returns"] = {"type": self._python_type_to_json(hints['return'])}
        except Exception:
            pass
        return schema

    def _python_type_to_json(self, python_type) -> str:
        type_map = {
            str: "string", int: "integer", float: "number",
            bool: "boolean", list: "array", dict: "object",
            type(None): "null"
        }
        return type_map.get(python_type, "string")


class JSONGenerator:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def generate(self, data: Any, indent: int = 2) -> str:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

    def generate_schema(self, name: str, fields: Dict[str, str]) -> Dict[str, Any]:
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": name,
            "type": "object",
            "properties": {},
            "required": []
        }
        type_map = {
            "str": "string", "string": "string",
            "int": "integer", "integer": "integer",
            "float": "number", "number": "number",
            "bool": "boolean", "boolean": "boolean",
            "list": "array", "array": "array",
            "dict": "object", "object": "object"
        }
        for field_name, field_type in fields.items():
            json_type = type_map.get(field_type.lower(), "string")
            schema["properties"][field_name] = {"type": json_type}
            schema["required"].append(field_name)
        return schema

    def from_dict(self, data: Dict, filename: str) -> Dict[str, Any]:
        result = {"success": False, "path": filename}
        try:
            parent = os.path.dirname(filename)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            result["success"] = True
            result["absolute_path"] = os.path.abspath(filename)
        except Exception as e:
            result["error"] = str(e)
        return result

    def to_dict(self, filename: str) -> Dict[str, Any]:
        result = {"success": False, "path": filename}
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            result["success"] = True
            result["data"] = data
        except Exception as e:
            result["error"] = str(e)
        return result


class FileSystemAnalyzer:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    UNNECESSARY_PATTERNS = [
        r'\.pyc$', r'\.pyo$', r'__pycache__', r'\.git$',
        r'\.DS_Store$', r'Thumbs\.db$', r'\.swp$', r'\.swo$',
        r'\.bak$', r'\.tmp$', r'\.temp$', r'\.log$',
        r'node_modules', r'\.cache$', r'\.idea$', r'\.vscode$'
    ]

    def find_duplicates(self, path: str, recursive: bool = True) -> Dict[str, List[str]]:
        hash_map = {}
        duplicates = {}
        def process_file(filepath):
            try:
                file_hash = self._get_file_hash(filepath)
                if file_hash in hash_map:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = [hash_map[file_hash]]
                    duplicates[file_hash].append(filepath)
                else:
                    hash_map[file_hash] = filepath
            except Exception:
                pass
        if recursive:
            for root, dirs, files in os.walk(path):
                for f in files:
                    process_file(os.path.join(root, f))
        else:
            if os.path.isdir(path):
                for f in os.listdir(path):
                    fp = os.path.join(path, f)
                    if os.path.isfile(fp):
                        process_file(fp)
        return duplicates

    def find_hidden(self, path: str, recursive: bool = True) -> List[str]:
        hidden = []
        if recursive:
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    if name.startswith('.'):
                        hidden.append(os.path.join(root, name))
        else:
            if os.path.isdir(path):
                for name in os.listdir(path):
                    if name.startswith('.'):
                        hidden.append(os.path.join(path, name))
        return hidden

    def find_unnecessary(self, path: str, recursive: bool = True) -> List[str]:
        unnecessary = []
        compiled_patterns = [re.compile(p) for p in self.UNNECESSARY_PATTERNS]
        if recursive:
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    full_path = os.path.join(root, name)
                    for pattern in compiled_patterns:
                        if pattern.search(full_path):
                            unnecessary.append(full_path)
                            break
        else:
            if os.path.isdir(path):
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    for pattern in compiled_patterns:
                        if pattern.search(full_path):
                            unnecessary.append(full_path)
                            break
        return unnecessary

    def analyze_directory(self, path: str) -> Dict[str, Any]:
        result = {
            "path": path,
            "success": False,
            "credits": f"Analyzed by {self.NAME} - {self.DEVELOPER} ({self.CONTACT})"
        }
        if not os.path.exists(path):
            result["error"] = f"Path not found: {path}"
            return result
        try:
            total_files = 0
            total_dirs = 0
            total_size = 0
            extensions = {}
            for root, dirs, files in os.walk(path):
                total_dirs += len(dirs)
                for f in files:
                    total_files += 1
                    fp = os.path.join(root, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
                    ext = os.path.splitext(f)[1].lower() or "(no extension)"
                    extensions[ext] = extensions.get(ext, 0) + 1
            result["total_files"] = total_files
            result["total_directories"] = total_dirs
            result["total_size_bytes"] = total_size
            result["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            result["extensions"] = dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:20])
            result["duplicates"] = self.find_duplicates(path)
            result["hidden_files"] = self.find_hidden(path)
            result["unnecessary_files"] = self.find_unnecessary(path)
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        return result

    def _get_file_hash(self, filepath: str, chunk_size: int = 8192) -> str:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()


class PythonInterpreterManager:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def get_interpreter_info(self) -> Dict[str, Any]:
        return {
            "executable": sys.executable,
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro
            },
            "platform": sys.platform,
            "prefix": sys.prefix,
            "exec_prefix": sys.exec_prefix,
            "path": sys.path.copy(),
            "modules_loaded": len(sys.modules),
            "credits": f"MEROAI - {self.DEVELOPER} ({self.CONTACT})"
        }

    def modify_builtins(self, name: str, new_value: Any) -> Dict[str, Any]:
        result = {"success": False, "name": name}
        try:
            import builtins
            if hasattr(builtins, name):
                result["original"] = str(getattr(builtins, name))
            setattr(builtins, name, new_value)
            result["success"] = True
            result["new_value"] = str(new_value)
        except Exception as e:
            result["error"] = str(e)
        return result

    def add_to_path(self, path: str) -> Dict[str, Any]:
        result = {"success": False, "path": path}
        try:
            if path not in sys.path:
                sys.path.insert(0, path)
                result["success"] = True
                result["message"] = f"Added {path} to sys.path"
            else:
                result["success"] = True
                result["message"] = f"{path} already in sys.path"
        except Exception as e:
            result["error"] = str(e)
        return result

    def execute_code(self, code: str, globals_dict: Dict = None, locals_dict: Dict = None) -> Dict[str, Any]:
        result = {"success": False, "code": code[:100] + "..." if len(code) > 100 else code}
        try:
            if globals_dict is None:
                globals_dict = {}
            if locals_dict is None:
                locals_dict = {}
            exec(code, globals_dict, locals_dict)
            result["success"] = True
            result["locals"] = {k: str(v)[:100] for k, v in locals_dict.items() if not k.startswith('_')}
        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
        return result


class LanguageDetector:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"
    LANGUAGE_PATTERNS = {
        "python": [
            (r"^\s*def\s+\w+\s*\(", 10),
            (r"^\s*class\s+\w+(\s*\(|\s*:)", 10),
            (r"^\s*import\s+\w+", 8),
            (r"^\s*from\s+\w+\s+import", 10),
            (r"^\s*if\s+.*:\s*$", 5),
            (r"^\s*for\s+\w+\s+in\s+", 8),
            (r"print\s*\(", 5),
            (r"self\.", 8),
            (r"__\w+__", 10),
        ],
        "javascript": [
            (r"^\s*function\s+\w+\s*\(", 10),
            (r"^\s*const\s+\w+\s*=", 8),
            (r"^\s*let\s+\w+\s*=", 8),
            (r"^\s*var\s+\w+\s*=", 6),
            (r"=>\s*\{", 10),
            (r"console\.(log|error|warn)", 10),
            (r"require\s*\(", 8),
        ],
        "typescript": [
            (r":\s*(string|number|boolean|any|void)\s*[;=\)]", 15),
            (r"interface\s+\w+\s*\{", 15),
            (r"type\s+\w+\s*=", 12),
        ],
        "c": [
            (r"#include\s*<\w+\.h>", 15),
            (r"#include\s*\"\w+\.h\"", 15),
            (r"#define\s+\w+", 10),
            (r"^\s*int\s+main\s*\(", 15),
            (r"printf\s*\(", 10),
            (r"malloc\s*\(", 10),
        ],
        "cpp": [
            (r"#include\s*<iostream>", 20),
            (r"#include\s*<vector>", 15),
            (r"using\s+namespace\s+std", 20),
            (r"std::", 15),
            (r"cout\s*<<", 15),
            (r"cin\s*>>", 15),
            (r"nullptr", 15),
        ],
        "csharp": [
            (r"using\s+System", 20),
            (r"namespace\s+\w+", 15),
            (r"public\s+class", 15),
            (r"Console\.(WriteLine|ReadLine)", 20),
        ],
        "java": [
            (r"public\s+class\s+\w+", 15),
            (r"public\s+static\s+void\s+main", 20),
            (r"System\.out\.print", 20),
            (r"import\s+java\.", 20),
        ],
        "go": [
            (r"package\s+\w+", 15),
            (r"func\s+\w+\s*\(", 15),
            (r":=", 10),
            (r"fmt\.(Print|Scan)", 18),
        ],
        "rust": [
            (r"fn\s+\w+\s*\(", 15),
            (r"let\s+mut\s+", 18),
            (r"println!\s*\(", 18),
            (r"use\s+\w+::", 15),
        ],
        "bash": [
            (r"^#!/bin/(ba)?sh", 25),
            (r"^\s*if\s+\[\s+", 12),
            (r"echo\s+", 8),
        ],
    }

    def detect(self, code: str) -> str:
        scores = {}
        for language, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern, weight in patterns:
                matches = re.findall(pattern, code, re.MULTILINE)
                score += len(matches) * weight
            if score > 0:
                scores[language] = score
        if not scores:
            return "unknown"
        return max(scores.items(), key=lambda x: x[1])[0]

    def detect_from_extension(self, filename: str) -> str:
        extension_map = {
            ".py": "python", ".c": "c", ".h": "c",
            ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
            ".cs": "csharp", ".java": "java",
            ".js": "javascript", ".jsx": "javascript",
            ".ts": "typescript", ".tsx": "typescript",
            ".go": "go", ".rs": "rust",
            ".sh": "bash", ".bash": "bash",
        }
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        return "unknown"


class CodeAnalyzer:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def analyze(self, code: str, language: str) -> List[str]:
        errors = []
        open_parens = code.count("(")
        close_parens = code.count(")")
        if open_parens != close_parens:
            errors.append(f"Mismatched parentheses: {open_parens} '(' vs {close_parens} ')'")
        open_brackets = code.count("[")
        close_brackets = code.count("]")
        if open_brackets != close_brackets:
            errors.append(f"Mismatched brackets: {open_brackets} '[' vs {close_brackets} ']'")
        open_braces = code.count("{")
        close_braces = code.count("}")
        if open_braces != close_braces:
            errors.append(f"Mismatched braces: {open_braces} '{{' vs {close_braces} '}}'")
        if language == "python":
            errors.extend(self._analyze_python(code))
        elif language in ["c", "cpp"]:
            errors.extend(self._analyze_c_cpp(code))
        return list(set(errors))

    def _analyze_python(self, code: str) -> List[str]:
        errors = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            if re.match(r"^\s*(def|class|if|elif|for|while|try|except|finally|with)\s+.*[^:]\s*$", stripped):
                if not stripped.endswith(":") and not stripped.endswith("\\"):
                    if ":" not in stripped.split("#")[0] or stripped.count(":") < 1:
                        errors.append(f"Line {i}: Missing colon after statement")
            if re.match(r"^\s*else\s*$", stripped):
                errors.append(f"Line {i}: Missing colon after 'else'")
            if re.match(r"^\s*print\s+['\"]", stripped):
                errors.append(f"Line {i}: print statement syntax (use print() function)")
            if re.match(r"^\s*return\s*=", stripped):
                errors.append(f"Line {i}: Invalid 'return =' syntax")
            if "==" in stripped and "if" not in stripped and "while" not in stripped:
                if stripped.count("=") == 2 and "!=" not in stripped:
                    pass
            if re.search(r'\bindent\b', stripped.lower()) and 'IndentationError' not in stripped:
                pass
            if stripped.startswith(" ") and not stripped.startswith("    ") and stripped.strip():
                spaces = len(stripped) - len(stripped.lstrip())
                if spaces % 4 != 0 and spaces > 0:
                    errors.append(f"Line {i}: Inconsistent indentation ({spaces} spaces)")
            try:
                compile(line, '<string>', 'eval')
            except SyntaxError as e:
                if 'EOF' not in str(e) and 'unexpected indent' not in str(e):
                    pass
            except:
                pass
        return errors

    def _analyze_c_cpp(self, code: str) -> List[str]:
        errors = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith("//") and not stripped.startswith("#"):
                if not stripped.endswith(";") and not stripped.endswith("{") and not stripped.endswith("}"):
                    if not stripped.endswith(":") and not stripped.endswith(","):
                        if "if" not in stripped and "for" not in stripped and "while" not in stripped:
                            if "else" not in stripped and "//" not in stripped:
                                errors.append(f"Line {i}: Possible missing semicolon")
        return errors


class CodeFixer:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def fix(self, code: str, language: str) -> str:
        fixed = code
        lines = fixed.split("\n")
        fixed_lines = [line.rstrip() for line in lines]
        while fixed_lines and not fixed_lines[-1]:
            fixed_lines.pop()
        fixed = "\n".join(fixed_lines)
        if language == "python":
            fixed = self._fix_python(fixed)
        return fixed

    def _fix_python(self, code: str) -> str:
        fixed = code
        lines = fixed.split("\n")
        fixed_lines = []
        for line in lines:
            stripped = line.rstrip()
            indent = len(line) - len(line.lstrip())
            indent_str = line[:indent]
            line_content = stripped.lstrip()
            if re.match(r'^print\s+[^(]', line_content):
                match = re.match(r'^print\s+(.+)$', line_content)
                if match:
                    arg = match.group(1).rstrip()
                    if not arg.startswith('('):
                        line_content = f'print({arg})'
                        stripped = indent_str + line_content
            if re.match(r"^\s*(def|class|if|elif|for|while|try|except|finally|with)\s+.+[^:]\s*$", stripped):
                if not stripped.endswith(":") and not stripped.endswith("\\"):
                    stripped += ":"
            if re.match(r"^\s*else\s*$", stripped):
                stripped = stripped.replace("else", "else:")
            open_parens, close_parens = self._count_parens_outside_strings(stripped)
            if open_parens > close_parens:
                stripped += ')' * (open_parens - close_parens)
            fixed_lines.append(stripped)
        return "\n".join(fixed_lines)

    def _count_parens_outside_strings(self, line: str) -> tuple:
        open_count = 0
        close_count = 0
        in_string = False
        string_char = None
        i = 0
        while i < len(line):
            char = line[i]
            if in_string:
                if char == '\\' and i + 1 < len(line):
                    i += 2
                    continue
                if char == string_char:
                    in_string = False
                    string_char = None
            else:
                if char in '"\'':
                    in_string = True
                    string_char = char
                elif char == '(':
                    open_count += 1
                elif char == ')':
                    close_count += 1
            i += 1
        return open_count, close_count

    def remove_comments(self, code: str, language: str) -> str:
        if language == "python":
            lines = code.split("\n")
            fixed_lines = []
            for line in lines:
                comment_pos = line.find("#")
                if comment_pos >= 0:
                    in_string = False
                    for char in line[:comment_pos]:
                        if char in '"\'':
                            in_string = not in_string
                    if not in_string:
                        line = line[:comment_pos].rstrip()
                if line.strip():
                    fixed_lines.append(line)
            return "\n".join(fixed_lines)
        elif language in ["c", "cpp", "csharp", "java", "javascript", "typescript", "go", "rust"]:
            fixed = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            fixed = re.sub(r'//.*$', '', fixed, flags=re.MULTILINE)
            lines = [l for l in fixed.split("\n") if l.strip()]
            return "\n".join(lines)
        elif language == "bash":
            lines = code.split("\n")
            fixed_lines = []
            for line in lines:
                if line.strip().startswith("#") and not line.strip().startswith("#!"):
                    continue
                if line.strip():
                    fixed_lines.append(line)
            return "\n".join(fixed_lines)
        return code


class ImageProcessor:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"
    SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]

    def analyze(self, path: str) -> Dict[str, Any]:
        result = {
            "path": path,
            "success": False,
            "credits": f"Analyzed by {self.NAME} - {self.DEVELOPER} ({self.CONTACT})"
        }
        if not os.path.exists(path):
            result["error"] = f"File not found: {path}"
            return result
        try:
            from PIL import Image
            with Image.open(path) as img:
                result["width"] = img.width
                result["height"] = img.height
                result["mode"] = img.mode
                result["format"] = img.format
                result["size_bytes"] = os.path.getsize(path)
                result["success"] = True
        except ImportError:
            result["error"] = "PIL not available"
        except Exception as e:
            result["error"] = str(e)
        return result

    def analyze_with_ai(self, path: str) -> Dict[str, Any]:
        result = {
            "path": path,
            "success": False,
            "credits": f"Analyzed by {self.NAME} - {self.DEVELOPER} ({self.CONTACT})"
        }
        if not os.path.exists(path):
            result["error"] = f"File not found: {path}"
            return result
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                result["error"] = "OPENAI_API_KEY not set"
                return result
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(path)[1].lower()
            mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else f"image/{ext[1:]}"
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image in detail."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
                    ]
                }],
                max_tokens=2048
            )
            result["description"] = response.choices[0].message.content
            result["success"] = True
            basic_info = self.analyze(path)
            if basic_info["success"]:
                result.update({k: basic_info.get(k) for k in ["width", "height", "format", "mode", "size_bytes"]})
        except Exception as e:
            result["error"] = str(e)
        return result

    def describe_image(self, path: str) -> Dict[str, Any]:
        return self.analyze_with_ai(path)

    def convert(self, source: str, destination: str, quality: int = 95) -> Dict[str, Any]:
        result = {"source": source, "destination": destination, "success": False}
        try:
            from PIL import Image
            with Image.open(source) as img:
                dst_ext = os.path.splitext(destination)[1].lower()
                if dst_ext in [".jpg", ".jpeg"] and img.mode in ["RGBA", "P"]:
                    img = img.convert("RGB")
                img.save(destination, quality=quality)
                result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        return result


class FileHandler:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"
    CODE_EXTENSIONS = {".py", ".c", ".h", ".cpp", ".cc", ".hpp", ".cs", ".java", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".sh", ".bash"}

    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding

    def read(self, path: str) -> str:
        try:
            with open(path, "r", encoding=self.encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    with open(path, "r", encoding=enc) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise

    def write(self, path: str, content: str) -> bool:
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding=self.encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False

    def list_code_files(self, path: str, recursive: bool = True) -> List[str]:
        files = []
        if recursive:
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in self.CODE_EXTENSIONS):
                        files.append(os.path.join(root, filename))
        return files


class FormatConverter:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def convert(self, source: str, destination: str) -> Dict[str, Any]:
        result = {"source": source, "destination": destination, "success": False}
        if not os.path.exists(source):
            result["error"] = f"Source not found: {source}"
            return result
        try:
            os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
            shutil.copy2(source, destination)
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        return result


class SystemManager:
    NAME = "MEROAI"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"

    def get_system_info(self) -> Dict[str, Any]:
        info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "node": platform.node(),
            "credits": f"MEROAI v{__version__} - {self.DEVELOPER} ({self.CONTACT})"
        }
        if platform.system().lower() == "linux":
            info["device_type"] = "Android" if os.path.exists("/data/data") else "Linux"
        elif platform.system().lower() == "windows":
            info["device_type"] = "Windows"
        elif platform.system().lower() == "darwin":
            info["device_type"] = "macOS"
        else:
            info["device_type"] = "Unknown"
        info["current_directory"] = os.getcwd()
        info["home_directory"] = os.path.expanduser("~")
        return info

    def list_paths(self, path: str = ".") -> List[str]:
        if not os.path.exists(path):
            return []
        if os.path.isfile(path):
            return [path]
        return os.listdir(path)

    def create_directory(self, path: str) -> Dict[str, Any]:
        result = {"path": path, "success": False}
        try:
            os.makedirs(path, exist_ok=True)
            result["success"] = True
            result["absolute_path"] = os.path.abspath(path)
        except Exception as e:
            result["error"] = str(e)
        return result

    def create_file(self, path: str, content: str = "", language: str = None) -> Dict[str, Any]:
        result = {"path": path, "success": False}
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            result["success"] = True
            result["absolute_path"] = os.path.abspath(path)
            if language:
                result["language"] = language
        except Exception as e:
            result["error"] = str(e)
        return result

    def get_path_info(self, path: str) -> Dict[str, Any]:
        result = {"path": path, "exists": os.path.exists(path)}
        if result["exists"]:
            result["is_file"] = os.path.isfile(path)
            result["is_directory"] = os.path.isdir(path)
            result["size"] = os.path.getsize(path) if os.path.isfile(path) else None
            result["absolute_path"] = os.path.abspath(path)
        return result


class MEROAI:
    NAME = "MEROAI"
    VERSION = "0.5.0"
    DEVELOPER = "MERO"
    CONTACT = "Telegram: @QP4RM"
    TELEGRAM = "https://t.me/QP4RM"
    GITHUB = "https://github.com/6x-u"
    SUPPORTED_LANGUAGES = ["python", "c", "cpp", "csharp", "java", "javascript", "typescript", "go", "rust", "bash"]

    def __init__(self, auto_fix: bool = True):
        self.auto_fix = auto_fix
        self._detector = LanguageDetector()
        self._analyzer = CodeAnalyzer()
        self._fixer = CodeFixer()
        self._image_processor = ImageProcessor()
        self._file_handler = FileHandler()
        self._format_converter = FormatConverter()
        self._system_manager = SystemManager()
        self._docstring_parser = DocstringParser()
        self._json_generator = JSONGenerator()
        self._fs_analyzer = FileSystemAnalyzer()
        self._interpreter_manager = PythonInterpreterManager()
        self._history = []

    def introduce(self) -> str:
        return f"""
{'=' * 60}
{self.NAME} v{self.VERSION}
{'=' * 60}
AI Programming Assistant for Code Analysis and Correction
Developer: {self.DEVELOPER}
Telegram: {self.CONTACT}
GitHub: {self.GITHUB}
Supported Languages: {', '.join(self.SUPPORTED_LANGUAGES)}
Python Support: 3.6 - 3.15
Platforms: Windows, Linux, Android, macOS
{'=' * 60}
"""

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.NAME,
            "version": self.VERSION,
            "developer": self.DEVELOPER,
            "contact": self.CONTACT,
            "telegram": self.TELEGRAM,
            "github": self.GITHUB,
            "supported_languages": self.SUPPORTED_LANGUAGES,
            "python_support": "3.6 - 3.15",
            "platforms": ["Windows", "Linux", "Android", "macOS"]
        }

    def analyze_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        if language is None:
            language = self._detector.detect(code)
        errors = self._analyzer.analyze(code, language)
        return {
            "language": language,
            "errors": errors,
            "error_count": len(errors),
            "credits": f"Analyzed by {self.NAME} - {self.DEVELOPER} ({self.CONTACT})"
        }

    def fix_code(self, code: str, language: Optional[str] = None) -> str:
        if language is None:
            language = self._detector.detect(code)
        return self._fixer.fix(code, language)

    def analyze_and_fix_file(self, path: str, save_as: str = None) -> Dict[str, Any]:
        result = {"source": path, "success": False}
        try:
            content = self._file_handler.read(path)
            language = self._detector.detect_from_extension(path)
            if language == "unknown":
                language = self._detector.detect(content)
            errors = self._analyzer.analyze(content, language)
            fixed = self._fixer.fix(content, language)
            save_path = save_as or path
            self._file_handler.write(save_path, fixed)
            result["language"] = language
            result["errors_found"] = len(errors)
            result["errors"] = errors
            result["saved_to"] = os.path.abspath(save_path)
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        return result

    def remove_comments(self, code: str, language: Optional[str] = None) -> str:
        if language is None:
            language = self._detector.detect(code)
        return self._fixer.remove_comments(code, language)

    def analyze_image(self, path: str, use_ai: bool = False) -> Dict[str, Any]:
        if use_ai:
            return self._image_processor.analyze_with_ai(path)
        return self._image_processor.analyze(path)

    def describe_image(self, path: str) -> Dict[str, Any]:
        return self._image_processor.describe_image(path)

    def convert_format(self, source: str, destination: str) -> Dict[str, Any]:
        return self._format_converter.convert(source, destination)

    def analyze_file(self, path: str) -> Dict[str, Any]:
        content = self._file_handler.read(path)
        language = self._detector.detect_from_extension(path)
        if language == "unknown":
            language = self._detector.detect(content)
        return self.analyze_code(content, language)

    def fix_file(self, path: str, save: bool = True) -> Dict[str, Any]:
        content = self._file_handler.read(path)
        language = self._detector.detect_from_extension(path)
        if language == "unknown":
            language = self._detector.detect(content)
        fixed = self.fix_code(content, language)
        if save:
            self._file_handler.write(path, fixed)
        return {"path": path, "language": language, "saved": save}

    def get_system_info(self) -> Dict[str, Any]:
        return self._system_manager.get_system_info()

    def get_path_info(self, path: str) -> Dict[str, Any]:
        return self._system_manager.get_path_info(path)

    def create_file(self, path: str, content: str = "", language: str = None) -> Dict[str, Any]:
        return self._system_manager.create_file(path, content, language)

    def create_directory(self, path: str) -> Dict[str, Any]:
        return self._system_manager.create_directory(path)

    def generate_json(self, data: Any, filename: str = None) -> Union[str, Dict[str, Any]]:
        json_str = self._json_generator.generate(data)
        if filename:
            return self._json_generator.from_dict(data, filename)
        return json_str

    def generate_json_schema(self, name: str, fields: Dict[str, str]) -> Dict[str, Any]:
        return self._json_generator.generate_schema(name, fields)

    def analyze_directory(self, path: str) -> Dict[str, Any]:
        return self._fs_analyzer.analyze_directory(path)

    def find_duplicates(self, path: str) -> Dict[str, List[str]]:
        return self._fs_analyzer.find_duplicates(path)

    def find_hidden_files(self, path: str) -> List[str]:
        return self._fs_analyzer.find_hidden(path)

    def find_unnecessary_files(self, path: str) -> List[str]:
        return self._fs_analyzer.find_unnecessary(path)

    def parse_docstring(self, docstring: str, style: str = "numpy") -> Dict[str, Any]:
        if style == "numpy":
            return self._docstring_parser.parse_numpy(docstring)
        elif style == "rst":
            return self._docstring_parser.parse_rst(docstring)
        elif style == "google":
            return self._docstring_parser.parse_google(docstring)
        return {}

    def generate_docstring(self, func_name: str, params: Dict[str, str], returns: str, style: str = "numpy", description: str = "") -> str:
        if style == "numpy":
            return self._docstring_parser.generate_numpy(func_name, params, returns, description)
        elif style == "rst":
            return self._docstring_parser.generate_rst(func_name, params, returns, description)
        return ""

    def function_to_json_schema(self, func: Callable) -> Dict[str, Any]:
        return self._docstring_parser.to_json_schema(func)

    def get_interpreter_info(self) -> Dict[str, Any]:
        return self._interpreter_manager.get_interpreter_info()

    def modify_interpreter(self, name: str, new_value: Any) -> Dict[str, Any]:
        return self._interpreter_manager.modify_builtins(name, new_value)

    def execute_python(self, code: str) -> Dict[str, Any]:
        return self._interpreter_manager.execute_code(code)

    def generate_readme(self, path: str, project_name: str = None, output_path: str = None) -> Dict[str, Any]:
        result = {"success": False, "path": path}
        try:
            if not os.path.exists(path):
                result["error"] = f"Path not found: {path}"
                return result
            if project_name is None:
                project_name = os.path.basename(os.path.abspath(path)) or "Project"
            analysis = self._fs_analyzer.analyze_directory(path)
            code_files = []
            main_languages = set()
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.git']]
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in ['.py', '.js', '.ts', '.go', '.rs', '.c', '.cpp', '.java', '.cs']:
                        code_files.append(os.path.join(root, f))
                        lang_map = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.go': 'Go', '.rs': 'Rust', '.c': 'C', '.cpp': 'C++', '.java': 'Java', '.cs': 'C#'}
                        if ext in lang_map:
                            main_languages.add(lang_map[ext])
            languages_str = ', '.join(sorted(main_languages)) if main_languages else 'Various'
            readme_content = f"""# {project_name}

Generated by MEROAI - {self.DEVELOPER} ({self.CONTACT})

## Overview

{project_name} is a project developed using {languages_str}.

## Project Structure

"""
            for ext, count in sorted(analysis.get('extensions', {}).items(), key=lambda x: -x[1])[:10]:
                readme_content += f"- **{ext}**: {count} files\n"
            readme_content += f"""
**Total Files**: {analysis.get('total_files', 0)}
**Total Directories**: {analysis.get('total_directories', 0)}
**Total Size**: {analysis.get('total_size_mb', 0)} MB

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
# Add your installation instructions here
```

## Usage

```bash
# Add your usage instructions here
```

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License

---

*Generated by MEROAI v{self.VERSION} - {self.DEVELOPER} ({self.CONTACT})*
"""
            save_path = output_path or os.path.join(path, "README.md")
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            result["success"] = True
            result["saved_to"] = os.path.abspath(save_path)
            result["project_name"] = project_name
            result["languages"] = list(main_languages)
            result["total_files"] = analysis.get('total_files', 0)
        except Exception as e:
            result["error"] = str(e)
        return result

    def edit_readme(self, path: str, section: str, new_content: str) -> Dict[str, Any]:
        result = {"success": False, "path": path, "section": section}
        try:
            if not os.path.exists(path):
                result["error"] = f"README not found: {path}"
                return result
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.split('\n')
            section_start = -1
            section_end = len(lines)
            for i, line in enumerate(lines):
                if line.strip() == f"## {section}":
                    section_start = i
                elif section_start >= 0 and line.startswith('## '):
                    section_end = i
                    break
            if section_start >= 0:
                new_lines = lines[:section_start] + [f"## {section}", "", new_content, ""] + lines[section_end:]
                content = '\n'.join(new_lines)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                result["success"] = True
                result["message"] = f"Section '{section}' updated"
            else:
                content = content.rstrip() + f"\n\n## {section}\n\n{new_content}\n"
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                result["success"] = True
                result["message"] = f"Section '{section}' added"
        except Exception as e:
            result["error"] = str(e)
        return result

    def save_analysis_to_file(self, analysis: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        result = {"success": False, "path": output_path}
        try:
            parent = os.path.dirname(output_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            content = f"""MEROAI Analysis Report
{'=' * 50}
Generated by: {self.NAME} v{self.VERSION}
Developer: {self.DEVELOPER} ({self.CONTACT})
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 50}

"""
            def format_value(val, indent=0):
                prefix = "  " * indent
                if isinstance(val, dict):
                    lines = []
                    for k, v in val.items():
                        lines.append(f"{prefix}{k}: {format_value(v, indent+1)}")
                    return "\n" + "\n".join(lines) if lines else "{}"
                elif isinstance(val, list):
                    if len(val) == 0:
                        return "[]"
                    items = val[:50]
                    lines = [f"{prefix}  - {str(item)[:200]}" for item in items]
                    if len(val) > 50:
                        lines.append(f"{prefix}  ... and {len(val) - 50} more")
                    return "\n" + "\n".join(lines)
                elif isinstance(val, bytes):
                    return f"<binary data: {len(val)} bytes>"
                else:
                    return str(val)[:500]
            for key, value in analysis.items():
                content += f"{key}: {format_value(value)}\n"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            result["success"] = True
            result["absolute_path"] = os.path.abspath(output_path)
        except Exception as e:
            result["error"] = str(e)
        return result

    def chat(self):
        print(self.introduce())
        print("\nType 'exit' to quit, 'help' for commands.\n")
        while True:
            try:
                user_input = input("MEROAI> ").strip()
                if not user_input:
                    continue
                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break
                elif user_input.lower() == "help":
                    self._print_help()
                elif user_input.lower() == "info":
                    print(json.dumps(self.get_info(), indent=2))
                elif user_input.lower() == "system":
                    print(json.dumps(self.get_system_info(), indent=2))
                elif user_input.lower().startswith("analyze "):
                    path = user_input[8:].strip()
                    result = self.analyze_file(path)
                    print(json.dumps(result, indent=2))
                elif user_input.lower().startswith("fix "):
                    path = user_input[4:].strip()
                    result = self.fix_file(path)
                    print(json.dumps(result, indent=2))
                elif user_input.lower().startswith("create "):
                    path = user_input[7:].strip()
                    result = self.create_file(path)
                    print(json.dumps(result, indent=2))
                elif user_input.lower().startswith("scandir "):
                    path = user_input[8:].strip()
                    result = self.analyze_directory(path)
                    print(json.dumps(result, indent=2, default=str))
                elif user_input.lower().startswith("json "):
                    data = user_input[5:].strip()
                    try:
                        parsed = eval(data)
                        print(self.generate_json(parsed))
                    except:
                        print("Invalid data format")
                elif user_input.lower().startswith("readme "):
                    path = user_input[7:].strip()
                    result = self.generate_readme(path)
                    print(json.dumps(result, indent=2))
                elif user_input.lower().startswith("image "):
                    path = user_input[6:].strip()
                    result = self.analyze_image(path)
                    print(json.dumps(result, indent=2))
                elif user_input.lower().startswith("saveimg "):
                    parts = user_input[8:].strip().split(" ")
                    if len(parts) >= 2:
                        img_path = parts[0]
                        out_path = parts[1]
                        analysis = self.analyze_image(img_path)
                        save_result = self.save_analysis_to_file(analysis, out_path)
                        print(json.dumps(save_result, indent=2))
                    else:
                        print("Usage: saveimg <image_path> <output_file>")
                else:
                    print(f"Unknown command. Type 'help' for available commands.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    def _print_help(self):
        print("""
Available Commands:
  help                     - Show this help message
  info                     - Show MEROAI info
  system                   - Show system info
  analyze <path>           - Analyze a code file
  fix <path>               - Fix and save a code file
  create <path>            - Create an empty file
  scandir <path>           - Analyze directory
  json <data>              - Convert Python dict/list to JSON
  readme <path>            - Generate README.md for project
  image <path>             - Analyze an image file
  saveimg <img> <out>      - Analyze image and save to file
  exit                     - Exit MEROAI
""")
