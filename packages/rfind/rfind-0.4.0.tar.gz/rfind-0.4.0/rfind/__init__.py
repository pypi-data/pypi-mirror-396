# rfind/__init__.py
"""
rfind - Ultra-fast file discovery with pure C acceleration
Restricted File Finder for directories with execute-only permission
"""

__version__ = "0.4.0"

import sys
import os
import warnings

# Flag to indicate if C extension is available
HAS_CEXT = True

try:
    # Try to import C extension
    from ._rfind import scan_directory, smart_scan, get_system_info, calculate_combinations
    HAS_CEXT = True
    
except ImportError as e:
    # C extension not available, use pure Python fallback
    HAS_CEXT = False
    
    def scan_directory(path=".", chars="abcdefghijklmnopqrstuvwxyz", 
                      min_len=1, max_len=3, threads=1):
        """
        Pure Python fallback for scan_directory.
        
        Args:
            path: Directory to scan
            chars: Character set for filename generation
            min_len: Minimum filename length
            max_len: Maximum filename length  
            threads: Number of threads (ignored in fallback)
            
        Returns:
            List of (filename, is_dir) tuples
        """
        import os
        import itertools
        
        results = []
        
        # Try normal directory listing first
        try:
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                if os.path.exists(entry_path):
                    is_dir = 1 if os.path.isdir(entry_path) else 0
                    results.append((entry, is_dir))
            return results
        except PermissionError:
            # We don't have read permission, continue with enumeration
            pass
        except Exception:
            # Other errors, continue with enumeration
            pass
        
        # Generate all combinations
        for length in range(min_len, max_len + 1):
            # Generate all combinations of given length
            for combo in itertools.product(chars, repeat=length):
                filename = ''.join(combo)
                test_path = os.path.join(path, filename)
                
                try:
                    if os.path.exists(test_path):
                        is_dir = 1 if os.path.isdir(test_path) else 0
                        results.append((filename, is_dir))
                except Exception:
                    # Skip files we can't access
                    continue
        
        return results
    
    def smart_scan(path=".", chars="abcdefghijklmnopqrstuvwxyz", 
                  min_len=1, max_len=3):
        """
        Smart scanning with common patterns - pure Python version.
        
        Args:
            path: Directory to scan
            chars: Character set for validation
            min_len: Minimum filename length
            max_len: Maximum filename length
            
        Returns:
            List of (filename, is_dir) tuples
        """
        import os
        
        results = []
        
        # Common pattern list (same as in C version)
        common_patterns = [
            # Single characters
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            
            # Two-letter Unix commands
            "sh", "ls", "cp", "mv", "rm", "cd", "ps", "df", "du", "vi", "cc",
            
            # Three-letter Unix commands  
            "awk", "cat", "cut", "gcc", "gdb", "grep", "jar", "man", "perl",
            
            # System directories
            "bin", "dev", "etc", "lib", "tmp", "usr", "var", "sys", "proc",
            "mnt", "opt", "srv", "run", "home", "root", "boot", "media",
            
            # Common files
            ".bashrc", ".profile", ".gitignore", "Makefile", "README",
            "LICENSE", "Dockerfile", ".env", "setup.py",
        ]
        
        for pattern in common_patterns:
            # Check length constraints
            if not (min_len <= len(pattern) <= max_len):
                continue
            
            # Check character constraints
            valid = True
            for char in pattern:
                if char not in chars and char not in '._-':
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Check if file exists
            test_path = os.path.join(path, pattern)
            try:
                if os.path.exists(test_path):
                    is_dir = 1 if os.path.isdir(test_path) else 0
                    results.append((pattern, is_dir))
            except Exception:
                continue
        
        return results
    
    def get_system_info():
        """
        Get system information - pure Python version.
        
        Returns:
            Dictionary with system information
        """
        import multiprocessing
        import sys
        
        info = {
            "cpu_cores": multiprocessing.cpu_count(),
            "page_size": 4096,
            "total_memory": 0,
            "note": "Running in pure Python mode"
        }
        
        # Try to get real memory info on Linux
        if sys.platform == "linux":
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            parts = line.split()
                            if len(parts) >= 2:
                                # Convert from kB to bytes
                                info["total_memory"] = int(parts[1]) * 1024
                                break
            except:
                pass
        
        return info
    
    def calculate_combinations(chars="abcdefghijklmnopqrstuvwxyz", 
                             min_len=1, max_len=3):
        """
        Calculate total combinations - pure Python version.
        
        Args:
            chars: Character set
            min_len: Minimum length
            max_len: Maximum length
            
        Returns:
            Total number of combinations
        """
        chars_len = len(chars)
        total = 0
        
        for length in range(min_len, max_len + 1):
            total += chars_len ** length
        
        return total

# Alias for parallel_scan
parallel_scan = scan_directory

# Module exports
__all__ = [
    'scan_directory',
    'smart_scan',
    'parallel_scan',
    'get_system_info',
    'calculate_combinations',
    '__version__',
    'HAS_CEXT'
]

# Warn if using fallback
if not HAS_CEXT:
    warnings.warn(
        "C extension not available, using slower Python implementation. "
        "Install with 'pip install rfind' for optimal performance.",
        RuntimeWarning,
        stacklevel=2
    )
