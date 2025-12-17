import os
import sys
import platform
import re
from typing import Optional, List, Dict, Any
__version__ = "0.2.0"
APP_NAME = "MEROAI"
__author__ = "MERO"
__contact__ = "Telegram: @QP4RM"
SUPPORTED_LANGUAGES = ["python", "c", "cpp", "csharp", "java", "javascript", "typescript", "go", "rust", "bash"]
def get_device_info() -> Dict[str, Any]:
    info = {
        "app_name": APP_NAME,
        "version": __version__,
        "developer": __author__,
        "contact": __contact__,
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "node": platform.node(),
    }
    if platform.system().lower() == "linux":
        if os.path.exists("/data/data"):
            info["device_type"] = "Android"
        else:
            info["device_type"] = "Linux"
    elif platform.system().lower() == "windows":
        info["device_type"] = "Windows"
    elif platform.system().lower() == "darwin":
        info["device_type"] = "macOS"
    else:
        info["device_type"] = "Unknown"
    info["current_directory"] = os.getcwd()
    info["home_directory"] = os.path.expanduser("~")
    info["credits"] = f"Analyzed by {APP_NAME} - {__author__} ({__contact__})"
    return info
def show_device_info():
    info = get_device_info()
    print(f"""
{'=' * 60}
Device Information - {APP_NAME} v{__version__}
{'=' * 60}
Device Type: {info['device_type']}
OS: {info['os']} {info['os_release']}
Platform: {info['platform']}
Machine: {info['machine']}
Processor: {info['processor']}
Node: {info['node']}

Python Version: {info['python_version']}
Python Implementation: {info['python_implementation']}

Current Directory: {info['current_directory']}
Home Directory: {info['home_directory']}
{'=' * 60}
Developer: {__author__} | Contact: {__contact__}
{'=' * 60}
""")
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".sh": "bash",
    ".bash": "bash",
}
LANGUAGE_PATTERNS = {
    "python": [
        (r"^\s*def\s+\w+\s*\(", 10),
        (r"^\s*class\s+\w+", 10),
        (r"^\s*import\s+\w+", 8),
        (r"^\s*from\s+\w+\s+import", 10),
        (r"print\s*\(", 5),
        (r"self\.", 8),
    ],
    "javascript": [
        (r"^\s*function\s+\w+\s*\(", 10),
        (r"^\s*const\s+\w+\s*=", 8),
        (r"^\s*let\s+\w+\s*=", 8),
        (r"=>\s*\{", 10),
        (r"console\.(log|error|warn)", 10),
    ],
    "typescript": [
        (r":\s*(string|number|boolean|any|void)", 15),
        (r"interface\s+\w+\s*\{", 15),
        (r"type\s+\w+\s*=", 12),
    ],
    "c": [
        (r"#include\s*<\w+\.h>", 15),
        (r"printf\s*\(", 10),
        (r"int\s+main\s*\(", 15),
    ],
    "cpp": [
        (r"#include\s*<iostream>", 20),
        (r"using\s+namespace\s+std", 20),
        (r"std::", 15),
        (r"cout\s*<<", 15),
    ],
    "csharp": [
        (r"using\s+System", 20),
        (r"namespace\s+\w+", 15),
        (r"Console\.(WriteLine|ReadLine)", 20),
    ],
    "java": [
        (r"public\s+class\s+\w+", 15),
        (r"public\s+static\s+void\s+main", 20),
        (r"System\.out\.print", 20),
    ],
    "go": [
        (r"package\s+\w+", 15),
        (r"func\s+\w+\s*\(", 15),
        (r"fmt\.(Print|Scan)", 18),
    ],
    "rust": [
        (r"fn\s+\w+\s*\(", 15),
        (r"let\s+mut\s+", 18),
        (r"println!\s*\(", 18),
    ],
    "bash": [
        (r"^#!/bin/(ba)?sh", 25),
        (r"^\s*if\s+\[\s+", 12),
        (r"echo\s+", 8),
    ],
}
def detect_language(code: str) -> str:
    scores = {}
    for language, patterns in LANGUAGE_PATTERNS.items():
        score = 0
        for pattern, weight in patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            score += len(matches) * weight
        if score > 0:
            scores[language] = score
    if not scores:
        return "unknown"
    return max(scores.items(), key=lambda x: x[1])[0]
def analyze_code(code: str, language: str) -> List[str]:
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
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            if re.match(r"^\s*(def|class|if|elif|else|for|while|try|except|finally|with)\s+.*[^:]\s*$", stripped):
                if not stripped.endswith(":") and not stripped.endswith("\\"):
                    errors.append(f"Line {i}: Missing colon after statement")
    return errors
def fix_code(code: str, language: str) -> str:
    fixed = code
    lines = fixed.split("\n")
    fixed_lines = [line.rstrip() for line in lines]
    while fixed_lines and not fixed_lines[-1]:
        fixed_lines.pop()
    if language == "python":
        new_lines = []
        for line in fixed_lines:
            stripped = line.rstrip()
            if re.match(r"^\s*(def|class|if|elif|else|for|while|try|except|finally|with)\s+.*[^:]\s*$", stripped):
                if not stripped.endswith(":") and not stripped.endswith("\\"):
                    open_p = stripped.count("(")
                    close_p = stripped.count(")")
                    if open_p > close_p:
                        stripped += ")" * (open_p - close_p)
                    stripped += ":"
            else:
                open_p = stripped.count("(")
                close_p = stripped.count(")")
                if open_p > close_p and not stripped.endswith(",") and not stripped.endswith("\\"):
                    stripped += ")" * (open_p - close_p)
            new_lines.append(stripped)
        fixed = "\n".join(new_lines)
        fixed = re.sub(r'\bprint\s+(["\'])', r'print(\1', fixed)
        fixed = re.sub(r'if\s+__name__\s*==\s*["\']__main__["\']\s*$', 'if __name__ == "__main__":', fixed, flags=re.MULTILINE)
        lines = fixed.split("\n")
        final_lines = []
        for line in lines:
            open_p = line.count("(")
            close_p = line.count(")")
            if open_p > close_p and not line.rstrip().endswith(",") and not line.rstrip().endswith("\\"):
                line = line.rstrip() + ")" * (open_p - close_p)
            final_lines.append(line)
        fixed = "\n".join(final_lines)
    else:
        fixed = "\n".join(fixed_lines)
    return fixed
def remove_comments(code: str, language: str) -> str:
    if language == "python":
        lines = code.split("\n")
        fixed_lines = []
        for line in lines:
            comment_pos = line.find("#")
            if comment_pos >= 0:
                in_string = False
                for i, char in enumerate(line[:comment_pos]):
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
def analyze_image(path: str) -> Dict[str, Any]:
    result = {
        "path": path,
        "success": False,
        "credits": f"Analyzed by {APP_NAME} - {__author__} ({__contact__})"
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
            result["success"] = True
    except ImportError:
        result["error"] = "PIL not available"
    except Exception as e:
        result["error"] = str(e)
    return result
def convert_format(source: str, destination: str) -> Dict[str, Any]:
    result = {
        "source": source,
        "destination": destination,
        "success": False,
        "credits": f"Converted by {APP_NAME} - {__author__} ({__contact__})"
    }
    if not os.path.exists(source):
        result["error"] = f"Source not found: {source}"
        return result
    try:
        src_ext = os.path.splitext(source)[1].lower()
        dst_ext = os.path.splitext(destination)[1].lower()
        image_formats = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
        if src_ext in image_formats and dst_ext in image_formats:
            from PIL import Image
            with Image.open(source) as img:
                if dst_ext in [".jpg", ".jpeg"] and img.mode in ["RGBA", "P"]:
                    img = img.convert("RGB")
                img.save(destination, quality=95)
                result["success"] = True
        else:
            import shutil
            shutil.copy2(source, destination)
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result
def generate_java_script() -> str:
    return '''package com.meroai.app;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;
import java.util.Date;
public class MeroAIApp {
    private static final String APP_NAME = "MEROAI Java App";
    private static final String VERSION = "1.0.0";
    private static final String AUTHOR = "MERO";
    private static final String CONTACT = "Telegram: @QP4RM";
    private static final String GITHUB = "https://github.com/6x-u";
    public static void main(String[] args) {
        MeroAIApp app = new MeroAIApp();
        app.run();
    }
    public void run() {
        printHeader();
        showSystemInfo();
        Calculator calc = new Calculator();
        System.out.println("\\nCalculator Demo:");
        System.out.println("10 + 5 = " + calc.add(10, 5));
        System.out.println("20 - 8 = " + calc.subtract(20, 8));
        System.out.println("4 * 7 = " + calc.multiply(4, 7));
        System.out.println("15 / 3 = " + calc.divide(15, 3));
        DataManager manager = new DataManager();
        manager.addItem("Item 1");
        manager.addItem("Item 2");
        manager.addItem("Item 3");
        System.out.println("\\nData Manager: " + manager.getItemCount() + " items");
        printFooter();
    }
    private void printHeader() {
        System.out.println("=".repeat(60));
        System.out.println(APP_NAME + " v" + VERSION);
        System.out.println("Developer: " + AUTHOR);
        System.out.println("GitHub: " + GITHUB);
        System.out.println("Contact: " + CONTACT);
        System.out.println("=".repeat(60));
    }
    private void showSystemInfo() {
        System.out.println("\\nSystem Information:");
        System.out.println("  OS: " + System.getProperty("os.name"));
        System.out.println("  Version: " + System.getProperty("os.version"));
        System.out.println("  Java: " + System.getProperty("java.version"));
        System.out.println("  User: " + System.getProperty("user.name"));
    }
    private void printFooter() {
        System.out.println("\\n" + "=".repeat(60));
        System.out.println("Created by MEROAI - " + AUTHOR + " (" + CONTACT + ")");
        System.out.println("=".repeat(60));
    }
}
class Calculator {
    private List<Double> history = new ArrayList<>();
    public double add(double a, double b) {
        double result = a + b;
        history.add(result);
        return result;
    }
    public double subtract(double a, double b) {
        double result = a - b;
        history.add(result);
        return result;
    }
    public double multiply(double a, double b) {
        double result = a * b;
        history.add(result);
        return result;
    }
    public double divide(double a, double b) {
        if (b == 0) {
            System.out.println("Error: Division by zero");
            return 0;
        }
        double result = a / b;
        history.add(result);
        return result;
    }
    public List<Double> getHistory() {
        return history;
    }
    public void clearHistory() {
        history.clear();
    }
}
class DataManager {
    private List<String> items = new ArrayList<>();
    private String name;
    public DataManager() {
        this.name = "DefaultManager";
    }
    public DataManager(String name) {
        this.name = name;
    }
    public void addItem(String item) {
        items.add(item);
    }
    public void removeItem(String item) {
        items.remove(item);
    }
    public int getItemCount() {
        return items.size();
    }
    public List<String> getAllItems() {
        return items;
    }
    public String getName() {
        return name;
    }
}
'''
def generate_cpp_script() -> str:
    return '''#include <iostream>
#include <string>
#include <cstdlib>
using namespace std;
const string APP_NAME = "MEROAI Script";
const string VERSION = "1.0.0";
const string AUTHOR = "MERO";
const string CONTACT = "Telegram: @QP4RM";
const string GITHUB = "https://github.com/6x-u";
class PlatformDetector {
public:
    string getOS() {
        #ifdef _WIN32
            return "Windows";
        #elif __ANDROID__
            return "Android";
        #elif __linux__
            return "Linux";
        #elif __APPLE__
            return "macOS";
        #else
            return "Unknown";
        #endif
    }
    bool isWindows() {
        #ifdef _WIN32
            return true;
        #else
            return false;
        #endif
    }
    bool isLinux() {
        #ifdef __linux__
            return true;
        #else
            return false;
        #endif
    }
};
class MeroApp {
private:
    PlatformDetector detector;
    string name;
    string version;
public:
    MeroApp() {
        name = APP_NAME;
        version = VERSION;
    }
    void showInfo() {
        cout << name << " v" << version << endl;
        cout << "Platform: " << detector.getOS() << endl;
        cout << "Developer: " << AUTHOR << endl;
        cout << "GitHub: " << GITHUB << endl;
        cout << "Contact: " << CONTACT << endl;
    }
    void run() {
        cout << string(50, '=') << endl;
        showInfo();
        cout << string(50, '=') << endl;
        cout << endl << "App is running..." << endl;
        cout << "Supports: Windows, Android, Linux, macOS" << endl;
        cout << endl << "Created by MEROAI - " << AUTHOR << " (" << CONTACT << ")" << endl;
    }
};
int main() {
    MeroApp app;
    app.run();
    return 0;
}
'''
def generate_large_script(lines: int = 1000, modules: Optional[List[str]] = None) -> str:
    if modules is None:
        modules = ["config", "logging", "utils", "models", "services", "cli", "tests"]
    sections = []
    sections.append(f'''"""
{'=' * 80}
MEROAI Generated Large Script
{'=' * 80}
Generated by: MEROAI v1.0.0
Developer: MERO
GitHub: https://github.com/6x-u
Contact: Telegram: @QP4RM

This is an auto-generated Python application with {lines}+ lines.
Includes: Configuration, Logging, Utilities, Models, Services, CLI, and Tests.
{'=' * 80}
"""
import os
import sys
import json
import time
import random
import hashlib
import logging
import platform
import threading
import functools
import argparse
import datetime
import collections
from typing import Optional, Dict, List, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from pathlib import Path
APP_NAME = "MEROAI Generated App"
VERSION = "1.0.0"
AUTHOR = "MERO"
CONTACT = "Telegram: @QP4RM"
GITHUB = "https://github.com/6x-u"
''')
    if "config" in modules:
        sections.append('''
class ConfigurationError(Exception):
    pass
class ValidationError(Exception):
    pass
class ServiceError(Exception):
    pass
@dataclass
class AppConfig:
    app_name: str = "MEROAI App"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    max_threads: int = 4
    timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600
    database_url: str = ""
    api_key: str = ""
    secret_key: str = ""
    allowed_hosts: List[str] = field(default_factory=list)
    cors_origins: List[str] = field(default_factory=list)
    rate_limit: int = 100
    retry_count: int = 3
    retry_delay: float = 1.0
    def validate(self) -> bool:
        if not self.app_name:
            raise ValidationError("App name is required")
        if self.max_threads < 1:
            raise ValidationError("max_threads must be >= 1")
        if self.timeout < 1:
            raise ValidationError("timeout must be >= 1")
        if self.rate_limit < 1:
            raise ValidationError("rate_limit must be >= 1")
        return True
    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "log_level": self.log_level,
            "max_threads": self.max_threads,
            "timeout": self.timeout,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "rate_limit": self.rate_limit,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            app_name=os.environ.get("APP_NAME", "MEROAI App"),
            version=os.environ.get("APP_VERSION", "1.0.0"),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            max_threads=int(os.environ.get("MAX_THREADS", "4")),
            timeout=int(os.environ.get("TIMEOUT", "30")),
            cache_enabled=os.environ.get("CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.environ.get("CACHE_TTL", "3600")),
            database_url=os.environ.get("DATABASE_URL", ""),
            api_key=os.environ.get("API_KEY", ""),
            secret_key=os.environ.get("SECRET_KEY", ""),
            rate_limit=int(os.environ.get("RATE_LIMIT", "100")),
            retry_count=int(os.environ.get("RETRY_COUNT", "3")),
            retry_delay=float(os.environ.get("RETRY_DELAY", "1.0")),
        )
    @classmethod
    def from_file(cls, path: str) -> "AppConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
    def save_to_file(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
''')
    if "logging" in modules:
        sections.append('''
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\\033[36m",
        "INFO": "\\033[32m",
        "WARNING": "\\033[33m",
        "ERROR": "\\033[31m",
        "CRITICAL": "\\033[35m",
    }
    RESET = "\\033[0m"
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)
class LogManager:
    _instance: Optional["LogManager"] = None
    _lock = threading.Lock()
    def __new__(cls) -> "LogManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: List[logging.Handler] = []
        self.default_level = logging.INFO
        self.default_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    def get_logger(self, name: str, level: Optional[int] = None) -> logging.Logger:
        if name in self.loggers:
            return self.loggers[name]
        logger = logging.getLogger(name)
        logger.setLevel(level or self.default_level)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(ColorFormatter(self.default_format))
            logger.addHandler(handler)
        self.loggers[name] = logger
        return logger
    def set_level(self, level: int) -> None:
        self.default_level = level
        for logger in self.loggers.values():
            logger.setLevel(level)
    def add_file_handler(self, filepath: str, level: Optional[int] = None) -> None:
        handler = logging.FileHandler(filepath)
        handler.setLevel(level or self.default_level)
        handler.setFormatter(logging.Formatter(self.default_format))
        self.handlers.append(handler)
        for logger in self.loggers.values():
            logger.addHandler(handler)
    def remove_all_handlers(self) -> None:
        for logger in self.loggers.values():
            logger.handlers.clear()
        self.handlers.clear()
log_manager = LogManager()
logger = log_manager.get_logger("MEROAI")
''')
    if "utils" in modules:
        sections.append('''
class Timer:
    def __init__(self, name: str = "Timer"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed: float = 0.0
    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self
    def __exit__(self, *args) -> None:
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        logger.debug(f"{self.name} completed in {self.elapsed:.4f}s")
    def start(self) -> None:
        self.start_time = time.perf_counter()
    def stop(self) -> float:
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - (self.start_time or self.end_time)
        return self.elapsed
class Cache:
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            value, timestamp = self._cache[key]
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                return None
            return value
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]
            self._cache[key] = (value, time.time())
    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
    def size(self) -> int:
        return len(self._cache)
    def cleanup(self) -> int:
        with self._lock:
            now = time.time()
            expired = [k for k, (_, ts) in self._cache.items() if now - ts > self.ttl]
            for key in expired:
                del self._cache[key]
            return len(expired)
def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exception
        return wrapper
    return decorator
def rate_limit(calls: int, period: float = 1.0):
    def decorator(func: Callable) -> Callable:
        timestamps: List[float] = []
        lock = threading.Lock()
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timestamps
            with lock:
                now = time.time()
                timestamps = [t for t in timestamps if now - t < period]
                if len(timestamps) >= calls:
                    sleep_time = period - (now - timestamps[0])
                    time.sleep(max(0, sleep_time))
                timestamps.append(time.time())
            return func(*args, **kwargs)
        return wrapper
    return decorator
def generate_id(prefix: str = "", length: int = 16) -> str:
    random_bytes = os.urandom(length)
    hash_str = hashlib.sha256(random_bytes).hexdigest()[:length]
    return f"{prefix}{hash_str}" if prefix else hash_str
def get_timestamp() -> str:
    return datetime.datetime.now().isoformat()
def hash_string(value: str, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(value.encode("utf-8"))
    return hasher.hexdigest()
def safe_json_loads(data: str, default: Any = None) -> Any:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return default
def merge_dicts(*dicts: Dict) -> Dict:
    result = {}
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result
def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
def chunk_list(lst: List, chunk_size: int) -> List[List]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
''')
    if "models" in modules:
        sections.append('''
class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
@dataclass
class BaseModel:
    id: str = field(default_factory=lambda: generate_id())
    created_at: str = field(default_factory=get_timestamp)
    updated_at: str = field(default_factory=get_timestamp)
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.name
            else:
                result[key] = value
        return result
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    def update(self) -> None:
        self.updated_at = get_timestamp()
@dataclass
class User(BaseModel):
    username: str = ""
    email: str = ""
    password_hash: str = ""
    is_active: bool = True
    is_admin: bool = False
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_login: Optional[str] = None
    def set_password(self, password: str) -> None:
        self.password_hash = hash_string(password)
        self.update()
    def check_password(self, password: str) -> bool:
        return self.password_hash == hash_string(password)
    def add_role(self, role: str) -> None:
        if role not in self.roles:
            self.roles.append(role)
            self.update()
    def remove_role(self, role: str) -> None:
        if role in self.roles:
            self.roles.remove(role)
            self.update()
    def has_role(self, role: str) -> bool:
        return role in self.roles
    def login(self) -> None:
        self.last_login = get_timestamp()
        self.update()
@dataclass
class Task(BaseModel):
    title: str = ""
    description: str = ""
    status: Status = Status.PENDING
    priority: Priority = Priority.NORMAL
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    def complete(self) -> None:
        self.status = Status.COMPLETED
        self.update()
    def fail(self, reason: str = "") -> None:
        self.status = Status.FAILED
        self.metadata["failure_reason"] = reason
        self.update()
    def cancel(self) -> None:
        self.status = Status.CANCELLED
        self.update()
    def assign(self, user_id: str) -> None:
        self.assignee_id = user_id
        self.status = Status.ACTIVE
        self.update()
    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
            self.update()
    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)
            self.update()
@dataclass
class Event(BaseModel):
    event_type: str = ""
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    def process(self) -> None:
        self.processed = True
        self.update()
@dataclass
class Workflow(BaseModel):
    name: str = ""
    description: str = ""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    status: Status = Status.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    def add_step(self, step: Dict[str, Any]) -> None:
        self.steps.append(step)
        self.update()
    def next_step(self) -> Optional[Dict[str, Any]]:
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            self.update()
            return step
        return None
    def is_complete(self) -> bool:
        return self.current_step >= len(self.steps)
    def reset(self) -> None:
        self.current_step = 0
        self.status = Status.PENDING
        self.update()
''')
    if "services" in modules:
        sections.append('''
class BaseService(ABC):
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.logger = log_manager.get_logger(self.__class__.__name__)
        self.cache = Cache(ttl=self.config.cache_ttl)
    @abstractmethod
    def initialize(self) -> None:
        pass
    @abstractmethod
    def shutdown(self) -> None:
        pass
    def health_check(self) -> Dict[str, Any]:
        return {
            "service": self.__class__.__name__,
            "status": "healthy",
            "timestamp": get_timestamp(),
        }
class UserService(BaseService):
    def __init__(self, config: Optional[AppConfig] = None):
        super().__init__(config)
        self.users: Dict[str, User] = {}
    def initialize(self) -> None:
        self.logger.info("UserService initialized")
    def shutdown(self) -> None:
        self.logger.info("UserService shutdown")
    def create_user(self, username: str, email: str, password: str) -> User:
        user = User(username=username, email=email)
        user.set_password(password)
        self.users[user.id] = user
        self.logger.info(f"Created user: {username}")
        return user
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        user = self.users.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.update()
            self.logger.info(f"Updated user: {user_id}")
        return user
    def delete_user(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            self.logger.info(f"Deleted user: {user_id}")
            return True
        return False
    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if user and user.check_password(password) and user.is_active:
            user.login()
            self.logger.info(f"User authenticated: {username}")
            return user
        self.logger.warning(f"Authentication failed: {username}")
        return None
    def list_users(self, active_only: bool = False) -> List[User]:
        users = list(self.users.values())
        if active_only:
            users = [u for u in users if u.is_active]
        return users
class TaskService(BaseService):
    def __init__(self, config: Optional[AppConfig] = None):
        super().__init__(config)
        self.tasks: Dict[str, Task] = {}
    def initialize(self) -> None:
        self.logger.info("TaskService initialized")
    def shutdown(self) -> None:
        self.logger.info("TaskService shutdown")
    def create_task(self, title: str, description: str = "", priority: Priority = Priority.NORMAL) -> Task:
        task = Task(title=title, description=description, priority=priority)
        self.tasks[task.id] = task
        self.logger.info(f"Created task: {title}")
        return task
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.update()
            self.logger.info(f"Updated task: {task_id}")
        return task
    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.logger.info(f"Deleted task: {task_id}")
            return True
        return False
    def assign_task(self, task_id: str, user_id: str) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            task.assign(user_id)
            self.logger.info(f"Assigned task {task_id} to {user_id}")
        return task
    def complete_task(self, task_id: str) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            task.complete()
            self.logger.info(f"Completed task: {task_id}")
        return task
    def list_tasks(self, status: Optional[Status] = None, assignee_id: Optional[str] = None) -> List[Task]:
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if assignee_id:
            tasks = [t for t in tasks if t.assignee_id == assignee_id]
        return sorted(tasks, key=lambda t: t.priority.value, reverse=True)
class WorkflowService(BaseService):
    def __init__(self, config: Optional[AppConfig] = None):
        super().__init__(config)
        self.workflows: Dict[str, Workflow] = {}
        self.event_handlers: Dict[str, List[Callable]] = collections.defaultdict(list)
    def initialize(self) -> None:
        self.logger.info("WorkflowService initialized")
    def shutdown(self) -> None:
        self.logger.info("WorkflowService shutdown")
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        workflow = Workflow(name=name, description=description)
        self.workflows[workflow.id] = workflow
        self.logger.info(f"Created workflow: {name}")
        return workflow
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflows.get(workflow_id)
    def execute_workflow(self, workflow_id: str) -> bool:
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        workflow.status = Status.ACTIVE
        workflow.update()
        self.logger.info(f"Executing workflow: {workflow.name}")
        while not workflow.is_complete():
            step = workflow.next_step()
            if step:
                self._execute_step(workflow, step)
        workflow.status = Status.COMPLETED
        workflow.update()
        self.logger.info(f"Workflow completed: {workflow.name}")
        return True
    def _execute_step(self, workflow: Workflow, step: Dict[str, Any]) -> None:
        step_name = step.get("name", "unknown")
        self.logger.debug(f"Executing step: {step_name}")
        time.sleep(0.01)
    def register_handler(self, event_type: str, handler: Callable) -> None:
        self.event_handlers[event_type].append(handler)
    def emit_event(self, event: Event) -> None:
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Handler error: {e}")
        event.process()
class ServiceContainer:
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.services: Dict[str, BaseService] = {}
        self.logger = log_manager.get_logger("ServiceContainer")
    def register(self, name: str, service: BaseService) -> None:
        self.services[name] = service
        self.logger.info(f"Registered service: {name}")
    def get(self, name: str) -> Optional[BaseService]:
        return self.services.get(name)
    def initialize_all(self) -> None:
        for name, service in self.services.items():
            try:
                service.initialize()
                self.logger.info(f"Initialized: {name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name}: {e}")
    def shutdown_all(self) -> None:
        for name, service in self.services.items():
            try:
                service.shutdown()
                self.logger.info(f"Shutdown: {name}")
            except Exception as e:
                self.logger.error(f"Failed to shutdown {name}: {e}")
    def health_check_all(self) -> Dict[str, Any]:
        results = {}
        for name, service in self.services.items():
            results[name] = service.health_check()
        return results
''')
    if "cli" in modules:
        sections.append('''
class CLI:
    def __init__(self, container: ServiceContainer):
        self.container = container
        self.logger = log_manager.get_logger("CLI")
        self.commands: Dict[str, Callable] = {}
        self._register_default_commands()
    def _register_default_commands(self) -> None:
        self.register("help", self._cmd_help)
        self.register("version", self._cmd_version)
        self.register("status", self._cmd_status)
        self.register("info", self._cmd_info)
        self.register("users", self._cmd_users)
        self.register("tasks", self._cmd_tasks)
        self.register("exit", self._cmd_exit)
    def register(self, name: str, handler: Callable) -> None:
        self.commands[name] = handler
    def _cmd_help(self, args: List[str]) -> str:
        lines = ["Available commands:"]
        for name in sorted(self.commands.keys()):
            lines.append(f"  {name}")
        return "\\n".join(lines)
    def _cmd_version(self, args: List[str]) -> str:
        return f"{APP_NAME} v{VERSION} by {AUTHOR}"
    def _cmd_status(self, args: List[str]) -> str:
        health = self.container.health_check_all()
        lines = ["Service Status:"]
        for name, status in health.items():
            lines.append(f"  {name}: {status.get('status', 'unknown')}")
        return "\\n".join(lines)
    def _cmd_info(self, args: List[str]) -> str:
        return f"""
Application: {APP_NAME}
Version: {VERSION}
Developer: {AUTHOR}
GitHub: {GITHUB}
Contact: {CONTACT}
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}
"""
    def _cmd_users(self, args: List[str]) -> str:
        user_service = self.container.get("users")
        if not user_service:
            return "UserService not available"
        users = user_service.list_users()
        if not users:
            return "No users found"
        lines = ["Users:"]
        for user in users:
            lines.append(f"  {user.id}: {user.username} ({user.email})")
        return "\\n".join(lines)
    def _cmd_tasks(self, args: List[str]) -> str:
        task_service = self.container.get("tasks")
        if not task_service:
            return "TaskService not available"
        tasks = task_service.list_tasks()
        if not tasks:
            return "No tasks found"
        lines = ["Tasks:"]
        for task in tasks:
            lines.append(f"  [{task.status.name}] {task.title}")
        return "\\n".join(lines)
    def _cmd_exit(self, args: List[str]) -> str:
        self.container.shutdown_all()
        return "Goodbye!"
    def execute(self, command: str, args: List[str] = None) -> str:
        args = args or []
        handler = self.commands.get(command)
        if not handler:
            return f"Unknown command: {command}. Type 'help' for available commands."
        try:
            return handler(args)
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            return f"Error: {e}"
    def run_interactive(self) -> None:
        print(f"\\n{'=' * 60}")
        print(f"{APP_NAME} v{VERSION}")
        print(f"Developer: {AUTHOR} | Contact: {CONTACT}")
        print(f"{'=' * 60}\\n")
        self.container.initialize_all()
        while True:
            try:
                user_input = input(f"{APP_NAME}> ").strip()
                if not user_input:
                    continue
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                result = self.execute(command, args)
                print(result)
                if command == "exit":
                    break
            except KeyboardInterrupt:
                print("\\n" + self.execute("exit"))
                break
            except EOFError:
                print("\\n" + self.execute("exit"))
                break
''')
    if "tests" in modules:
        sections.append('''
class TestRunner:
    def __init__(self):
        self.tests: List[Tuple[str, Callable]] = []
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []
    def add_test(self, name: str, test_func: Callable) -> None:
        self.tests.append((name, test_func))
    def run_all(self) -> Dict[str, Any]:
        print(f"\\nRunning {len(self.tests)} tests...\\n")
        for name, test_func in self.tests:
            try:
                test_func()
                print(f"  [PASS] {name}")
                self.passed += 1
            except AssertionError as e:
                print(f"  [FAIL] {name}: {e}")
                self.failed += 1
                self.errors.append(f"{name}: {e}")
            except Exception as e:
                print(f"  [ERROR] {name}: {e}")
                self.failed += 1
                self.errors.append(f"{name}: {e}")
        print(f"\\nResults: {self.passed} passed, {self.failed} failed\\n")
        return {
            "total": len(self.tests),
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
        }
def test_config():
    config = AppConfig()
    assert config.app_name == "MEROAI App"
    assert config.version == "1.0.0"
    assert config.validate() == True
def test_cache():
    cache = Cache(ttl=1)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    cache.delete("key1")
    assert cache.get("key1") is None
def test_user_model():
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    assert user.check_password("password123") == True
    assert user.check_password("wrongpassword") == False
def test_task_model():
    task = Task(title="Test Task", description="Description")
    assert task.status == Status.PENDING
    task.complete()
    assert task.status == Status.COMPLETED
def test_user_service():
    service = UserService()
    service.initialize()
    user = service.create_user("testuser", "test@example.com", "password")
    assert service.get_user(user.id) is not None
    assert service.authenticate("testuser", "password") is not None
    service.shutdown()
def test_task_service():
    service = TaskService()
    service.initialize()
    task = service.create_task("Test", priority=Priority.HIGH)
    assert service.get_task(task.id) is not None
    service.complete_task(task.id)
    assert task.status == Status.COMPLETED
    service.shutdown()
def test_utilities():
    assert len(generate_id()) == 16
    assert len(generate_id(prefix="test_", length=8)) == 13
    assert hash_string("test") == hash_string("test")
    assert hash_string("test") != hash_string("test2")
def run_tests() -> None:
    runner = TestRunner()
    runner.add_test("Config validation", test_config)
    runner.add_test("Cache operations", test_cache)
    runner.add_test("User model", test_user_model)
    runner.add_test("Task model", test_task_model)
    runner.add_test("User service", test_user_service)
    runner.add_test("Task service", test_task_service)
    runner.add_test("Utilities", test_utilities)
    runner.run_all()
''')
    sections.append(f'''
def main():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description=f"{{APP_NAME}} v{{VERSION}} - Generated by MEROAI"
    )
    parser.add_argument("--version", action="version", version=f"{{APP_NAME}} v{{VERSION}}")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--info", action="store_true", help="Show info")
    args = parser.parse_args()
    if args.test:
        run_tests()
        return
    if args.info:
        print(f"""
{{'=' * 60}}
{{APP_NAME}} v{{VERSION}}
{{'=' * 60}}
Developer: {{AUTHOR}}
GitHub: {{GITHUB}}
Contact: {{CONTACT}}
Platform: {{platform.system()}} {{platform.release()}}
Python: {{platform.python_version()}}
{{'=' * 60}}
Generated by MEROAI - {{AUTHOR}} ({{CONTACT}})
{{'=' * 60}}
""")
        return
    config = AppConfig.from_env()
    container = ServiceContainer(config)
    container.register("users", UserService(config))
    container.register("tasks", TaskService(config))
    container.register("workflows", WorkflowService(config))
    cli = CLI(container)
    cli.run_interactive()
if __name__ == "__main__":
    main()
''')
    full_script = "\n".join(sections)
    current_lines = len(full_script.split("\n"))
    if current_lines < lines:
        extra_needed = lines - current_lines
        extra_sections = []
        for i in range((extra_needed // 15) + 2):
            extra_sections.append(f'''
class DataProcessor{i}:
    def __init__(self, name: str = "processor{i}"):
        self.name = name
        self.data: Dict[str, Any] = {{}}
        self.counter = 0
        self.history: List[Any] = []
    def process(self, value: Any) -> Any:
        self.counter += 1
        self.data[f"item_{{self.counter}}"] = value
        self.history.append(value)
        return value
    def get_stats(self) -> Dict[str, Any]:
        return {{"name": self.name, "count": self.counter, "items": len(self.data), "history_size": len(self.history)}}
    def reset(self) -> None:
        self.data.clear()
        self.counter = 0
        self.history.clear()
    def to_dict(self) -> Dict[str, Any]:
        return {{"name": self.name, "data": self.data, "counter": self.counter, "history": self.history}}
    def get_last(self, n: int = 5) -> List[Any]:
        return self.history[-n:] if len(self.history) >= n else self.history
''')
        full_script += "\n".join(extra_sections)
    return full_script
def generate_script(script_type: str = "basic", lines: int = 50) -> str:
    header = f'''import os
import sys
import platform
from typing import Optional, Dict, List, Any
APP_NAME = "MEROAI Script"
VERSION = "1.0.0"
AUTHOR = "MERO"
CONTACT = "Telegram: @QP4RM"
'''
    platform_code = '''
class PlatformDetector:
    def __init__(self):
        self.system = platform.system().lower()
    def is_windows(self) -> bool:
        return self.system == "windows"
    def is_android(self) -> bool:
        return "android" in self.system or os.path.exists("/data/data")
    def is_linux(self) -> bool:
        return self.system == "linux" and not self.is_android()
    def get_platform(self) -> str:
        if self.is_android():
            return "Android"
        elif self.is_windows():
            return "Windows"
        elif self.is_linux():
            return "Linux"
        return "Unknown"
'''
    main_code = f'''
class MeroApp:
    def __init__(self):
        self.detector = PlatformDetector()
        self.name = APP_NAME
        self.version = VERSION
    def show_info(self):
        print(f"{{self.name}} v{{self.version}}")
        print(f"Platform: {{self.detector.get_platform()}}")
        print(f"Developer: {{AUTHOR}}")
        print(f"Contact: {{CONTACT}}")
    def run(self):
        print("=" * 50)
        self.show_info()
        print("=" * 50)
        print("\\nApp is running...")
        print("Supports: Windows, Android, Linux")
        print(f"\\nCreated by MEROAI - {{AUTHOR}} ({{CONTACT}})")
def main():
    app = MeroApp()
    app.run()
if __name__ == "__main__":
    main()
'''
    return header + platform_code + main_code
def show_intro():
    info = f"""
{'=' * 60}
MEROAI v1.0.0 - Programming Only AI
{'=' * 60}
I am MEROAI, an AI programming assistant.
Developed by: MERO
GitHub: https://github.com/6x-u
Contact: Telegram: @QP4RM

Supported Languages:
  - Python (.py)
  - C (.c, .h)
  - C++ (.cpp, .cc, .cxx, .hpp)
  - C# (.cs)
  - Java (.java)
  - JavaScript (.js, .jsx)
  - TypeScript (.ts, .tsx)
  - Go (.go)
  - Rust (.rs)
  - Bash (.sh, .bash)

Features:
  - Automatic error detection
  - Automatic code fixing
  - Script generation (Python, C++, Java)
  - Large script generation (1000+ lines)
{'=' * 60}
"""
    return info
def show_help():
    print(f"""
{'=' * 60}
MEROAI Commands - Programming AI
{'=' * 60}

ERROR DETECTION & FIXING:
  analyze <path>      - Detect all errors in code file
  fix <path>          - Auto-fix all errors automatically
  autofix <path>      - Same as fix (auto-fix errors)

SCRIPT GENERATION:
  create script       - Generate Python script
  create java         - Generate Java application
  create cpp          - Generate C++ script
  large-script [N]    - Generate large script (1000+ lines)

UTILITIES:
  image <path>        - Analyze image file
  convert <src> <dst> - Convert file format
  system              - Show system info
  help                - Show this help message
  info                - Show introduction
  credits             - Show developer credits
  exit                - Exit MEROAI

SUPPORTED LANGUAGES:
  Python, C, C++, C#, Java, JavaScript, 
  TypeScript, Go, Rust, Bash

EXAMPLES:
  analyze mycode.py   - Find errors in Python file
  fix mycode.py       - Auto-fix all errors
  create java         - Generate Java code
  large-script 2000   - Generate 2000+ line script

{'=' * 60}
Developer: MERO | GitHub: @6x-u | Telegram: @QP4RM
{'=' * 60}
""")
def show_credits():
    print(f"""
MEROAI v1.0.0
Developer: MERO
Telegram: https://t.me/QP4RM
""")
def process_input(text: str) -> str:
    text_lower = text.lower()
    non_programming_keywords = ["physics", "فيزياء", "chemistry", "كيمياء", "math problem", "history", "تاريخ", "geography", "جغرافيا", "biology", "احياء", "weather", "طقس", "news", "اخبار", "sports", "رياضة", "music", "موسيقى", "movies", "افلام", "food", "طعام", "recipe", "وصفة"]
    if any(word in text_lower for word in non_programming_keywords):
        return f"I am {APP_NAME}, a programming-only AI. I can only help with:\n- Code analysis and error detection\n- Code fixing and optimization\n- Script generation (Python, C++, etc.)\n- Programming questions\n\nSupported Languages: Python, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust, Bash\n\nI cannot answer questions about physics, chemistry, history, or other non-programming topics.\nDeveloper: {__author__} | Contact: {__contact__}"
    if any(word in text_lower for word in ["who are you", "what is your name", "introduce", "عرف نفسك", "من انت", "ما اسمك"]):
        return f"I am {APP_NAME}, a programming-only AI assistant developed by {__author__}.\nI specialize in code analysis, error detection, and script generation.\nSupported Languages: Python, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust, Bash\nContact: {__contact__}"
    elif any(word in text_lower for word in ["developer", "creator", "made you", "مطورك", "صنعك", "من طورك", "صانعك"]):
        return f"I was developed by {__author__}. GitHub: https://github.com/6x-u | Contact: {__contact__}"
    elif any(word in text_lower for word in ["where from", "origin", "من اين", "اتيت", "جئت", "اين صنعت"]):
        return f"I am {APP_NAME}, created by {__author__}. I was built to help developers analyze and fix code. GitHub: https://github.com/6x-u | Telegram: {__contact__}"
    elif any(word in text_lower for word in ["languages", "support", "اللغات", "تدعم"]):
        return f"I support: Python, C, C++, C#, Java, JavaScript, TypeScript, Go, Rust, and Bash."
    elif any(word in text_lower for word in ["java script", "java code", "سكربت جافا", "كود جافا"]):
        script = generate_java_script()
        return f"Here is a Java application created by {APP_NAME}:\n\n{script}\n\nCreated by: {__author__} ({__contact__})"
    elif any(word in text_lower for word in ["c++ script", "cpp script", "سكربت c++", "سكربت سي بلس"]):
        script = generate_cpp_script()
        return f"Here is a C++ script created by {APP_NAME}:\n\n{script}\n\nCreated by: {__author__} ({__contact__})"
    elif any(word in text_lower for word in ["large script", "big script", "1000 lines", "سكربت كبير", "سكربت طويل"]):
        script = generate_large_script(lines=1000)
        line_count = len(script.split("\n"))
        return f"Here is a large Python script ({line_count} lines) created by {APP_NAME}:\n\n{script}\n\nCreated by: {__author__} ({__contact__})"
    elif any(word in text_lower for word in ["create script", "make script", "generate script", "اصنع سكربت", "انشئ سكربت", "اكتب كود", "python script"]):
        script = generate_script()
        return f"Here is a Python script created by {APP_NAME}:\n\n{script}\n\nCreated by: {__author__} ({__contact__})"
    elif any(word in text_lower for word in ["help", "how to use", "مساعدة", "كيف استخدمك"]):
        return "Type 'help' to see all available commands."
    else:
        code_indicators = ["def ", "class ", "import ", "function ", "const ", "let ", "int ", "void "]
        if any(indicator in text for indicator in code_indicators):
            lang = detect_language(text)
            errors = analyze_code(text, lang)
            if errors:
                response = f"Detected language: {lang}\nErrors found:\n" + "\n".join(f"- {e}" for e in errors)
                fixed = fix_code(text, lang)
                response += f"\n\nAuto-fixed code:\n{fixed}"
                return response
            else:
                return f"Detected language: {lang}\nNo errors found. Code looks good!"
        else:
            return f"I am {APP_NAME}, a code-focused AI. I can help you with:\n- Code analysis\n- Error detection and fixing\n- Image analysis (code screenshots)\n- File format conversion\n\nType 'help' for commands."
def chat():
    print(show_intro())
    print("\nType 'exit' to quit, 'help' for commands.\n")
    while True:
        try:
            user_input = input(f"{APP_NAME}> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\nGoodbye! - {APP_NAME} by {__author__}")
                print(f"Contact: {__contact__}")
                break
            if user_input.lower() == "help":
                show_help()
                continue
            if user_input.lower() == "info":
                print(show_intro())
                continue
            if user_input.lower() == "credits":
                show_credits()
                continue
            if user_input.lower().startswith("analyze "):
                path = user_input[8:].strip()
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    ext = os.path.splitext(path)[1]
                    language = SUPPORTED_EXTENSIONS.get(ext, detect_language(content))
                    errors = analyze_code(content, language)
                    print(f"\nLanguage: {language}")
                    print(f"Errors: {len(errors)}")
                    for e in errors:
                        print(f"  - {e}")
                    print(f"\nCredits: {APP_NAME} - {__author__} ({__contact__})\n")
                else:
                    print(f"\nError: Path not found: {path}\n")
                continue
            if user_input.lower().startswith("fix ") or user_input.lower().startswith("autofix "):
                if user_input.lower().startswith("fix "):
                    path = user_input[4:].strip()
                else:
                    path = user_input[8:].strip()
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    ext = os.path.splitext(path)[1]
                    language = SUPPORTED_EXTENSIONS.get(ext, detect_language(content))
                    errors_before = analyze_code(content, language)
                    fixed = fix_code(content, language)
                    errors_after = analyze_code(fixed, language)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(fixed)
                    print(f"\nLanguage: {language}")
                    print(f"Errors before: {len(errors_before)}")
                    print(f"Errors after: {len(errors_after)}")
                    print(f"Fixed {len(errors_before) - len(errors_after)} errors automatically!")
                    print(f"\nFile saved: {path}")
                    print(f"Credits: {APP_NAME} - {__author__} ({__contact__})\n")
                else:
                    print(f"\nError: Path not found: {path}\n")
                continue
            if user_input.lower() in ["create java", "java code", "generate java"]:
                script = generate_java_script()
                print(f"\nGenerated Java Application:\n")
                print(script)
                print(f"\nCreated by: {__author__} ({__contact__})\n")
                continue
            if user_input.lower() in ["create cpp", "cpp code", "generate cpp", "c++ code"]:
                script = generate_cpp_script()
                print(f"\nGenerated C++ Script:\n")
                print(script)
                print(f"\nCreated by: {__author__} ({__contact__})\n")
                continue
            if user_input.lower() in ["create script", "python script", "generate script"]:
                script = generate_script()
                print(f"\nGenerated Python Script:\n")
                print(script)
                print(f"\nCreated by: {__author__} ({__contact__})\n")
                continue
            if user_input.lower().startswith("image "):
                path = user_input[6:].strip()
                result = analyze_image(path)
                print(f"\nImage Analysis: {result}\n")
                continue
            if user_input.lower().startswith("convert "):
                args = user_input[8:].strip().split()
                if len(args) >= 2:
                    result = convert_format(args[0], args[1])
                    print(f"\nConversion Result: {result}\n")
                else:
                    print("\nUsage: convert <source> <destination>\n")
                continue
            if user_input.lower() == "system":
                print(f"""
System Information:
  OS: {platform.system()} {platform.release()}
  Python: {platform.python_version()}
  MEROAI: v{__version__}
  Developer: {__author__}
  Contact: {__contact__}
""")
                continue
            if user_input.lower().startswith("large-script"):
                parts = user_input.split()
                lines = 1000
                if len(parts) > 1:
                    try:
                        lines = int(parts[1])
                    except ValueError:
                        lines = 1000
                script = generate_large_script(lines=lines)
                line_count = len(script.split("\n"))
                print(f"\nGenerated large Python script ({line_count} lines):\n")
                print(script)
                print(f"\nCreated by: {__author__} ({__contact__})\n")
                continue
            response = process_input(user_input)
            print(f"\n{response}\n")
        except KeyboardInterrupt:
            print(f"\n\nGoodbye! - {APP_NAME} by {__author__}")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")
def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ["--version", "-v"]:
            print(f"{APP_NAME} v{__version__} by {__author__} ({__contact__})")
            return
        if cmd in ["--help", "-h"]:
            show_help()
            return
        if cmd == "chat":
            chat()
            return
        if cmd == "analyze" and len(sys.argv) > 2:
            path = sys.argv[2]
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                ext = os.path.splitext(path)[1]
                language = SUPPORTED_EXTENSIONS.get(ext, detect_language(content))
                errors = analyze_code(content, language)
                print(f"Language: {language}")
                print(f"Errors: {len(errors)}")
                for e in errors:
                    print(f"  - {e}")
                print(f"\nCredits: {APP_NAME} - {__author__} ({__contact__})")
            else:
                print(f"Error: File not found: {path}")
            return
        if cmd == "fix" and len(sys.argv) > 2:
            path = sys.argv[2]
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                ext = os.path.splitext(path)[1]
                language = SUPPORTED_EXTENSIONS.get(ext, detect_language(content))
                fixed = fix_code(content, language)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed)
                print(f"Fixed: {path}")
                print(f"Credits: {APP_NAME} - {__author__} ({__contact__})")
            else:
                print(f"Error: File not found: {path}")
            return
        if cmd == "large-script":
            lines = 1000
            if len(sys.argv) > 2:
                try:
                    lines = int(sys.argv[2])
                except ValueError:
                    lines = 1000
            script = generate_large_script(lines=lines)
            line_count = len(script.split("\n"))
            print(f"Generated large Python script ({line_count} lines):\n")
            print(script)
            print(f"\nCreated by: {__author__} ({__contact__})")
            return
    chat()
if __name__ == "__main__":
    main()