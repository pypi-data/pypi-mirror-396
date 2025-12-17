# MEROAI v0.5.0

![MEROAI](MEROAI.png)

**A comprehensive Python library for code analysis, language detection, image processing, file management, JSON generation, and smart decorators.**

---

## Developer

| | |
|---|---|
| **Name** | MERO |
| **Telegram** | [@QP4RM](https://t.me/QP4RM) |
| **GitHub** | [github.com/6x-u](https://github.com/6x-u) |

---

## Main Features

### Code Analysis
- Detect errors in Python, C, C++, Java, JavaScript, TypeScript, Go, Rust, Bash, C#
- Automatic fixing of common errors
- Automatic programming language detection

### Image Processing
- Analyze image information (dimensions, format, size)
- AI-powered image description (OpenAI GPT-4o)
- Image format conversion

### File Management
- Create files in any programming language
- Automatic README.md generation for projects
- Edit README sections
- Save analysis results to txt files

### File System Analysis
- Find duplicate files
- Detect hidden files
- Find unnecessary files

### Smart Decorators
- `@mero_schema` - logging, timing, error handling
- `@mero_log` - add logging to functions
- `@mero_validate` - type validation

---

## Installation

### Standard Installation
```bash
pip install pillow openai numpy requests
git clone https://github.com/6x-u/MEROAI-1V.git
```

### Termux Installation (Android)
```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install pillow numpy requests
git clone https://github.com/6x-u/MEROAI-1V.git
cd MEROAI-1V/scripts
./install_termux.sh
```

---

## Quick Start

```python
import sys
sys.path.insert(0, 'MEROAI-1V/src/MEROAI/meroai')
from core import MEROAI

m = MEROAI()
print(m.introduce())
```

---

## Main Commands

### Code Analysis and Fixing

```python
m = MEROAI()

# Analyze code
result = m.analyze_code("def hello() print('hi')")
print(result['errors'])  # ['Missing colon after statement']

# Fix code
fixed = m.fix_code("def hello() print('hi')")
print(fixed)  # def hello(): print('hi')

# Analyze file
result = m.analyze_file("script.py")

# Fix and save file
m.fix_file("script.py", save=True)

# Analyze, fix and save to new file
m.analyze_and_fix_file("broken.py", "fixed.py")
```

### Image Processing

```python
# Analyze image
info = m.analyze_image("photo.png")
print(info['width'], info['height'], info['format'])

# AI description (requires OPENAI_API_KEY)
desc = m.describe_image("photo.png")
print(desc['description'])

# Save analysis to file
m.save_analysis_to_file(info, "photo_analysis.txt")
```

### File Creation

```python
# Create C++ file
cpp_code = '''#include <iostream>
int main() {
    std::cout << "Hello MEROAI!" << std::endl;
    return 0;
}'''
m.create_file("hello.cpp", cpp_code, "cpp")

# Create directory
m.create_directory("my_project/src")
```

### README Generation

```python
# Generate README for project
m.generate_readme("/path/to/project", "MyProject")

# Edit README section
m.edit_readme("README.md", "Features", "- Feature 1\n- Feature 2")
```

### JSON Generation

```python
# Convert to JSON
data = {"name": "MEROAI", "version": "0.5.0"}
json_str = m.generate_json(data)

# Save as JSON file
m.generate_json(data, "config.json")

# Generate JSON Schema
schema = m.generate_json_schema("User", {
    "name": "string",
    "age": "integer",
    "email": "string"
})
```

### File System Analysis

```python
# Analyze full directory
analysis = m.analyze_directory("/path/to/folder")
print(analysis['total_files'])
print(analysis['total_size_mb'])
print(analysis['extensions'])

# Find duplicates
duplicates = m.find_duplicates("/path/to/folder")

# Hidden files
hidden = m.find_hidden_files("/path/to/folder")

# Unnecessary files
unnecessary = m.find_unnecessary_files("/path/to/folder")
```

### Docstrings

```python
# Parse docstring
doc = m.parse_docstring(my_docstring, "numpy")

# Generate docstring
doc = m.generate_docstring(
    "calculate",
    {"a": "int", "b": "int"},
    "int",
    style="numpy",
    description="Calculate sum"
)

# Convert function to JSON Schema
schema = m.function_to_json_schema(my_function)
```

### Smart Decorators

```python
from core import mero_schema, mero_log, mero_validate

@mero_schema
def my_function(x: int) -> int:
    return x * 2

@mero_log(level="INFO")
def process_data(data):
    return data.upper()

@mero_validate
def add(a: int, b: int) -> int:
    return a + b
```

### Python Interpreter

```python
# Interpreter info
info = m.get_interpreter_info()

# Execute code
result = m.execute_python("x = 1 + 2")
print(result['locals'])  # {'x': 3}
```

---

## Interactive Mode

```python
m = MEROAI()
m.chat()
```

### Available Commands

| Command | Description |
|---------|-------------|
| `help` | Show help |
| `info` | MEROAI info |
| `system` | System info |
| `analyze <path>` | Analyze file |
| `fix <path>` | Fix file |
| `create <path>` | Create file |
| `scandir <path>` | Analyze directory |
| `json <data>` | Convert to JSON |
| `readme <path>` | Generate README |
| `image <path>` | Analyze image |
| `saveimg <img> <out>` | Analyze image and save |
| `exit` | Exit |

---

## Termux Scripts

```bash
cd ~/MEROAI-1V/scripts

# Full installation
./install_termux.sh

# Run MEROAI
./meroai.sh

# Analyze image
./image_analyzer.sh photo.jpg report.txt

# Fix code
./code_fixer.sh broken.py fixed.py

# Generate README
./readme_generator.sh ~/project MyProject
```

---

## Supported Languages

| Language | Extensions |
|----------|------------|
| Python | .py |
| C | .c, .h |
| C++ | .cpp, .cc, .hpp |
| C# | .cs |
| Java | .java |
| JavaScript | .js, .jsx |
| TypeScript | .ts, .tsx |
| Go | .go |
| Rust | .rs |
| Bash | .sh, .bash |

---

## Requirements

| Package | Required | Function |
|---------|----------|----------|
| pillow | Yes | Image processing |
| numpy | Yes | Math operations |
| requests | Yes | HTTP requests |
| openai | Optional | AI image description |

---

## Supported Platforms

- Windows (7, 8, 10, 11)
- Linux (Ubuntu, Debian, Fedora, Arch)
- macOS (10.15+)
- Android (Termux)

---

## License

MIT License

---

## Contact

- **Developer**: MERO
- **Telegram**: [@QP4RM](https://t.me/QP4RM)
- **GitHub**: [github.com/6x-u](https://github.com/6x-u)

---

*MEROAI v0.5.0 - Made by MERO*
