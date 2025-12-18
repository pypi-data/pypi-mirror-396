# setup.py
"""
Build configuration for rfind C extension
Core fix: include_dirs path corrected to point to actual header location
"""

from setuptools import setup, Extension
import os

# ------------------------------------------------------------
# 1. C EXTENSION CONFIGURATION
# ------------------------------------------------------------
# Fix: Changed include_dirs from 'rfind/include' to 'rfind/src'
# because scanner.h is actually in rfind/src/ directory
extension = Extension(
    'rfind._rfind',  # The name of the compiled module (must match PyInit__rfind)
    sources=[
        'rfind/src/scanner.c',
        'rfind/src/generator.c', 
        'rfind/src/worker.c',
        'rfind/src/rfindmodule.c',
    ],
    # CRITICAL FIX: Header files are in rfind/src/, not rfind/include/
    include_dirs=['rfind/src'],
    # Optional: Add current directory to help find headers
    # include_dirs=['rfind/src', '.'],
    
    # Compiler optimization flags
    extra_compile_args=['-O3', '-pthread', '-Wall'],
    
    # Linker flags  
    extra_link_args=['-pthread'],
)

# ------------------------------------------------------------
# 2. PACKAGE METADATA
# ------------------------------------------------------------
# Read long description from README
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "⚡ Ultra-fast file discovery with pure C acceleration"

setup(
    # Basic metadata
    name='rfind',
    version='0.4.0',
    author='nsyhykui',
    author_email='nsyhykui@outlook.com',
    description='⚡ Ultra-fast file discovery with pure C acceleration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nsyhykui/rfind',
    
    # Extension modules
    ext_modules=[extension],
    
    # Python package discovery
    packages=['rfind'],
    
    # Python version requirement
    python_requires='>=3.6',
    
    # Package classifiers for PyPI
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: C',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Android',
    ],
    
    # Console script entry point
    entry_points={
        'console_scripts': [
            'rfind=rfind.cli:main',
        ],
    },
    
    # Optional dependencies for development and benchmarking
    extras_require={
        'dev': [
            'build>=0.10.0',
            'twine>=4.0.0',
            'pytest>=7.0.0',
            'coverage>=7.0.0',
        ],
        'benchmark': [
            'psutil>=5.9.0',
            'rich>=13.0.0',
        ],
    },
)
# 添加在 setup() 函数调用之前，文件末尾
import os
import sys

print("\n" + "="*60, file=sys.stderr)
print("DEBUG: FILE STRUCTURE CHECK", file=sys.stderr)
print("="*60, file=sys.stderr)

print(f"1. Current dir: {os.getcwd()}", file=sys.stderr)
print(f"2. Setup.py dir: {os.path.dirname(os.path.abspath(__file__))}", file=sys.stderr)

# 检查关键目录和文件
print("\n3. Critical paths:", file=sys.stderr)
key_paths = [
    'rfind/src',
    'rfind/include', 
    os.path.join('rfind', 'src', 'scanner.h'),
    os.path.join('rfind', 'include', 'scanner.h')
]

for path in key_paths:
    exists = os.path.exists(path)
    print(f"   {path:40} -> {'EXISTS' if exists else 'MISSING'}", file=sys.stderr)

# 列出当前目录
print("\n4. Current directory listing:", file=sys.stderr)
for item in sorted(os.listdir('.')):
    print(f"   - {item}", file=sys.stderr)

print("="*60 + "\n", file=sys.stderr)
