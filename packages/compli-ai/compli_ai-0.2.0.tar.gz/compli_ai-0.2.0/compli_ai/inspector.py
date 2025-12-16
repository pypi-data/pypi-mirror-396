import ast
from pathlib import Path
from typing import List, Set

from compli_ai.schema import ModelInfo

# A partial list of Python 3.9 standard library modules for filtering.
# This is used for compatibility as sys.stdlib_module_names is 3.10+
STD_LIB_MODULES = {
    "__future__", "abc", "aifc", "argparse", "array", "ast", "asynchat",
    "asyncio", "asyncore", "atexit", "audioop", "base64", "bdb", "binascii",
    "binhex", "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb",
    "chunk", "cmath", "cmd", "code", "codecs", "codeop", "collections",
    "colorsys", "compileall", "concurrent", "configparser", "contextlib",
    "contextvars", "copy", "copyreg", "cProfile", "crypt", "csv", "ctypes",
    "curses", "dataclasses", "datetime", "dbm", "decimal", "difflib",
    "dis", "distutils", "doctest", "email", "encodings", "enum", "errno",
    "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch", "fractions",
    "ftplib", "functools", "gc", "getopt", "getpass", "gettext", "glob",
    "grp", "gzip", "hashlib", "heapq", "hmac", "html", "http", "imaplib",
    "imghdr", "imp", "importlib", "inspect", "io", "ipaddress", "itertools",
    "json", "keyword", "lib2to3", "linecache", "locale", "logging", "lzma",
    "mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap", "modulefinder",
    "multiprocessing", "netrc", "nntplib", "numbers", "operator", "optparse",
    "os", "ossaudiodev", "parser", "pathlib", "pdb", "pickle", "pickletools",
    "pipes", "pkgutil", "platform", "plistlib", "poplib", "posix", "pprint",
    "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc",
    "queue", "quopri", "random", "re", "readline", "reprlib", "resource",
    "rlcompleter", "runpy", "sched", "secrets", "select", "selectors",
    "shelve", "shlex", "shutil", "signal", "site", "smtpd", "smtplib",
    "sndhdr", "socket", "socketserver", "sqlite3", "ssl", "stat", "statistics",
    "string", "stringprep", "struct", "subprocess", "sunau", "symbol", "sys",
    "sysconfig", "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile",
    "termios", "textwrap", "threading", "time", "timeit", "tkinter", "token",
    "tokenize", "trace", "traceback", "tracemalloc", "tty", "turtle",
    "turtledemo", "types", "typing", "unicodedata", "unittest", "urllib",
    "uu", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser", "wsgiref",
    "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib"
}

def analyze_imports(content: str, file_path: Path) -> Set[str]:
    """
    Parses Python code content and extracts top-level imported module names,
    filtering out standard library modules.
    """
    libraries = set()
    tree = ast.parse(content, filename=str(file_path))
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level = alias.name.split('.')[0]
                if top_level not in STD_LIB_MODULES:
                    libraries.add(top_level)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # Ignore relative imports
                continue
            if node.module:
                top_level = node.module.split('.')[0]
                if top_level not in STD_LIB_MODULES:
                    libraries.add(top_level)
    return libraries

def detect_models(content: str, file_path: Path) -> List[ModelInfo]:
    """
    Detects AI models in Python code content.
    """
    models = []
    tree = ast.parse(content, filename=file_path)

    for node in ast.walk(tree):
        # Detect Hugging Face models: x = AutoModel.from_pretrained('name') or pipeline(..., model='name')
        if (isinstance(node, ast.Assign) and
                isinstance(node.value, ast.Call) and
                isinstance(node.value.func, ast.Attribute) and
                node.value.func.attr == 'from_pretrained' and
                node.value.args and
                isinstance(node.value.args[0], ast.Constant)):
            model_name = node.value.args[0].value
            models.append(ModelInfo(
                name=model_name,
                framework="Hugging Face",
                line_number=node.lineno,
                file_path=file_path
            ))
        
        # Detect models loaded via transformers.pipeline(model='name')
        if (isinstance(node, ast.Call) and
            isinstance(node.func, (ast.Name, ast.Attribute))):
            
            func_name = None
            if isinstance(node.func, ast.Name) and node.func.id == 'pipeline':
                func_name = 'pipeline'
            elif (isinstance(node.func, ast.Attribute) and 
                  node.func.attr == 'pipeline' and
                  isinstance(node.func.value, ast.Name) and 
                  node.func.value.id == 'transformers'): # e.g., transformers.pipeline(...)
                func_name = 'pipeline'

            if func_name == 'pipeline':
                for keyword in node.keywords:
                    if keyword.arg == 'model' and isinstance(keyword.value, ast.Constant):
                        model_name = keyword.value.value
                        models.append(ModelInfo(
                            name=model_name,
                            framework="Hugging Face (Pipeline)",
                            line_number=node.lineno,
                            file_path=file_path
                        ))

        # Detect PyTorch models: class MyModel(torch.nn.Module)
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if (isinstance(base, ast.Attribute) and
                    isinstance(base.value, ast.Attribute) and
                    base.value.value.id == 'torch' and
                    base.value.attr == 'nn' and
                        base.attr == 'Module'):
                    models.append(ModelInfo(
                        name=node.name,
                        framework="PyTorch",
                        line_number=node.lineno,
                        file_path=file_path
                    ))
    return models
