__version__ = "0.4.0"
__name__ = "MEROAI"
__author__ = "MERO"
__contact__ = "Telegram: @QP4RM"
__telegram__ = "https://t.me/QP4RM"

try:
    from MEROAI.meroai.core import (
        MEROAI,
        CodeAnalyzer,
        CodeFixer,
        LanguageDetector,
        ImageProcessor,
        FileHandler,
        FormatConverter,
        SystemManager,
        DocstringParser,
        JSONGenerator,
        FileSystemAnalyzer,
        PythonInterpreterManager,
        mero_schema,
        mero_log,
        mero_validate,
    )
except ImportError:
    from .core import (
        MEROAI,
        CodeAnalyzer,
        CodeFixer,
        LanguageDetector,
        ImageProcessor,
        FileHandler,
        FormatConverter,
        SystemManager,
        DocstringParser,
        JSONGenerator,
        FileSystemAnalyzer,
        PythonInterpreterManager,
        mero_schema,
        mero_log,
        mero_validate,
    )

__all__ = [
    "MEROAI",
    "CodeAnalyzer",
    "CodeFixer",
    "LanguageDetector",
    "ImageProcessor",
    "FileHandler",
    "FormatConverter",
    "SystemManager",
    "DocstringParser",
    "JSONGenerator",
    "FileSystemAnalyzer",
    "PythonInterpreterManager",
    "mero_schema",
    "mero_log",
    "mero_validate",
    "__version__",
    "__author__",
    "__contact__",
]

def get_info():
    return {
        "name": "MEROAI",
        "version": __version__,
        "developer": __author__,
        "contact": __contact__,
        "telegram": __telegram__,
        "supported_languages": ["Python", "C", "C++", "C#", "Java", "JavaScript", "TypeScript", "Go", "Rust", "Bash"],
        "python_support": "3.6 - 3.15",
        "platforms": ["Windows", "Linux", "Android", "macOS"],
    }

def credits():
    print("=" * 50)
    print(f"MEROAI v{__version__}")
    print(f"Developed by: {__author__}")
    print(f"Contact: {__contact__}")
    print(f"Telegram: {__telegram__}")
    print("=" * 50)
