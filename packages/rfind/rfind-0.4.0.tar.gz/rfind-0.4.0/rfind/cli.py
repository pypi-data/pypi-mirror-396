# rfind/cli.py - IMPROVED VERSION
#!/usr/bin/env python3
"""
Command line interface for rfind - Restricted File Finder
Ultra-fast file discovery in directories with execute-only permission
"""

import argparse
import sys
import time
import math
from . import scan_directory, smart_scan, get_system_info, calculate_combinations, __version__, HAS_CEXT

def format_number(num):
    """Format number with commas for readability."""
    return f"{num:,}"

def format_size(size_bytes):
    """Format bytes to human readable size."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def main():
    parser = argparse.ArgumentParser(
        prog="rfind",
        description="""Discover files when you have execute but not read permission.
        
Use cases:
  • Security auditing - discovering hidden or protected files
  • Digital forensics - investigating system directories  
  • System administration - recovering from permission issues
  • Penetration testing - exploring restricted environments
  • Android device analysis - accessing protected system directories
  
Examples:
  rfind /system/bin
  rfind -M 4 -c 'a-z0-9' /dev
  rfind --smart /dev
  rfind -t 4 -c 'abcdefghijklmnopqrstuvwxyz0123456789_-.' --estimate
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Note: Use responsibly and only on systems you own or have permission to test."
    )
    
    # Required arguments
    parser.add_argument("path", nargs="?", default=".", 
                       help="target directory (default: current directory)")
    
    # Scanning options
    parser.add_argument("-m", "--min", type=int, default=1,
                       help="minimum filename length (default: 1)")
    parser.add_argument("-M", "--max", type=int, default=3,
                       help="maximum filename length (default: 3)")
    parser.add_argument("-c", "--chars", default="abcdefghijklmnopqrstuvwxyz",
                       help="character set to use (default: a-z)")
    parser.add_argument("-t", "--threads", type=int, default=0,
                       help="number of threads (0=auto-detect, default: 0)")
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-s", "--smart", action="store_true",
                           help="use smart pattern scanning (common filenames)")
    mode_group.add_argument("-e", "--estimate", action="store_true",
                           help="only estimate search space, don't scan")
    
    # Output options
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="verbose output with statistics")
    parser.add_argument("-q", "--quiet", action="store_true",
                       help="suppress non-essential output")
    parser.add_argument("-o", "--output", type=str,
                       help="output file (default: stdout)")
    
    # Info options
    parser.add_argument("--version", action="store_true",
                       help="show version and exit")
    parser.add_argument("--benchmark", action="store_true",
                       help="run benchmark test")
    parser.add_argument("--list-charsets", action="store_true",
                       help="list available character sets and exit")
    
    args = parser.parse_args()
    
    # Handle info options first
    if args.version:
        print(f"rfind v{__version__}")
        print(f"C extension: {'enabled' if HAS_CEXT else 'disabled (using Python fallback)'}")
        if args.verbose:
            info = get_system_info()
            print(f"System: {info.get('cpu_cores', '?')} CPU cores")
            if info.get('total_memory'):
                print(f"Memory: {format_size(info['total_memory'])}")
        return 0
    
    if args.list_charsets:
        print("Available character sets (use with -c option):")
        print("  a-z  : Lowercase letters (default)")
        print("  A-Z  : Uppercase letters")
        print("  0-9  : Digits")
        print("  a-zA-Z0-9 : Alphanumeric")
        print("  a-zA-Z0-9_- : Alphanumeric with underscore and hyphen")
        print("  a-zA-Z0-9_-.: Alphanumeric with common filename characters")
        print("\nExamples:")
        print("  rfind -c 'a-z0-9' /path")
        print("  rfind -c 'abcdefghijklmnopqrstuvwxyz0123456789_-.' /path")
        return 0
    
    # Validate arguments
    if args.min <= 0:
        print("Error: min length must be positive", file=sys.stderr)
        return 1
    
    if args.max < args.min:
        print("Error: max length must be >= min length", file=sys.stderr)
        return 1
    
    if args.max > 10:
        print("Warning: max length > 10 may generate huge search space", file=sys.stderr)
        if not args.estimate:
            print("Use --estimate to check search space first", file=sys.stderr)
    
    # Calculate search space
    total_combinations = calculate_combinations(args.chars, args.min, args.max)
    
    if args.estimate:
        print(f"Search space estimation for '{args.path}':")
        print(f"  Character set: {args.chars} ({len(args.chars)} characters)")
        print(f"  Length range: {args.min}-{args.max}")
        print(f"  Total combinations: {format_number(total_combinations)}")
        
        if total_combinations > 1000000:
            print(f"  Warning: Large search space ({format_number(total_combinations)} combinations)")
            print(f"  Consider using --smart mode or limiting length/characters")
        
        return 0
    
    if not args.quiet:
        print(f"Scanning: {args.path}")
        print(f"Mode: {'smart' if args.smart else 'brute force'}")
        print(f"Character set: {len(args.chars)} characters")
        print(f"Length range: {args.min}-{args.max}")
        if args.verbose:
            print(f"Total possible combinations: {format_number(total_combinations)}")
            if args.threads == 0:
                print(f"Threads: auto-detect")
            else:
                print(f"Threads: {args.threads}")
    
    # Start timing
    start_time = time.time()
    
    try:
        # Perform scan
        if args.smart:
            results = smart_scan(args.path, args.chars, args.min, args.max)
        else:
            results = scan_directory(args.path, args.chars, args.min, args.max, args.threads)
        
        scan_time = time.time() - start_time
        
        # Process results
        if not results:
            if not args.quiet:
                print("No files found.")
            return 0
        
        # Separate directories and files
        dirs = []
        files = []
        
        for item in results:
            if isinstance(item, tuple) and len(item) == 2:
                name, is_dir = item
                if is_dir == 1:
                    dirs.append(name)
                else:
                    files.append(name)
            else:
                if not args.quiet:
                    print(f"Warning: Unexpected result format: {item}", file=sys.stderr)
        
        # Sort results
        dirs.sort()
        files.sort()
        
        # Output results
        output_file = None
        if args.output:
            try:
                output_file = open(args.output, 'w')
            except Exception as e:
                print(f"Error opening output file: {e}", file=sys.stderr)
                output_file = None
        
        def write_output(text):
            if output_file:
                output_file.write(text + '\n')
            else:
                print(text)
        
        # Write results
        if dirs:
            write_output("\nDIRECTORIES:")
            for name in dirs:
                write_output(f"  {name}/")
        
        if files:
            write_output("\nFILES:")
            for name in files:
                write_output(f"  {name}")
        
        # Statistics
        if args.verbose or args.benchmark:
            total_found = len(dirs) + len(files)
            
            if not args.quiet:
                write_output(f"\nSTATISTICS:")
                write_output(f"  Directories found: {len(dirs)}")
                write_output(f"  Files found: {len(files)}")
                write_output(f"  Total found: {total_found}")
                write_output(f"  Scan time: {scan_time:.3f} seconds")
            
            if args.benchmark and scan_time > 0:
                if not args.quiet:
                    write_output(f"\n{'='*60}")
                    write_output("PERFORMANCE BENCHMARK")
                    write_output(f"{'='*60}")
                
                write_output(f"Search space: {format_number(total_combinations)} combinations")
                write_output(f"Scan completed in {scan_time:.3f} seconds")
                
                # Calculate speed
                checks_per_sec = total_combinations / scan_time
                write_output(f"Speed: {format_number(int(checks_per_sec))} checks/second")
                
                # Effectiveness
                if total_combinations > 0:
                    effectiveness = (total_found / total_combinations) * 100
                    write_output(f"Effectiveness: {total_found}/{format_number(total_combinations)} "
                                f"({effectiveness:.6f}%)")
                
                # System info
                info = get_system_info()
                write_output(f"\nSYSTEM INFO:")
                write_output(f"  CPU cores: {info.get('cpu_cores', 'N/A')}")
                write_output(f"  Page size: {info.get('page_size', 'N/A')} bytes")
                if info.get('total_memory'):
                    write_output(f"  Total memory: {format_size(info['total_memory'])}")
                write_output(f"  C extension: {'enabled' 
if HAS_CEXT else 'disabled'}")
        
        if output_file:
            output_file.close()
            if not args.quiet:
                print(f"\nResults saved to: {args.output}")
    
    except KeyboardInterrupt:
        if not args.quiet:
            print("\nScan interrupted by user")
        return 130
    except PermissionError as e:
        print(f"Permission error: {e}", file=sys.stderr)
        print("You may need execute permission on the directory.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
