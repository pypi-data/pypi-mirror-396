// rfind/src/scanner.c
#include "scanner.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include <errno.h>
#include <math.h>

// Create a new ScanResult structure
ScanResult* result_create(void) {
    ScanResult *result = malloc(sizeof(ScanResult));
    if (!result) return NULL;
    
    result->capacity = 100;
    result->count = 0;
    result->items = malloc(sizeof(FileItem) * result->capacity);
    if (!result->items) {
        free(result);
        return NULL;
    }
    
    return result;
}

// Free a ScanResult structure
void result_free(ScanResult *result) {
    if (!result) return;
    
    // Free all allocated names
    for (size_t i = 0; i < result->count; i++) {
        free(result->items[i].name);
    }
    free(result->items);
    free(result);
}

// Add an item to ScanResult
int result_add(ScanResult *result, const char *name, int is_dir) {
    if (!result || !name) return 0;
    
    // Expand capacity if needed
    if (result->count >= result->capacity) {
        size_t new_capacity = result->capacity * 2;
        FileItem *new_items = realloc(result->items, sizeof(FileItem) * new_capacity);
        if (!new_items) return 0;
        
        result->items = new_items;
        result->capacity = new_capacity;
    }
    
    // Add item
    FileItem *item = &result->items[result->count];
    item->name = strdup(name);
    item->is_dir = is_dir;
    
    if (!item->name) return 0;
    
    result->count++;
    return 1;
}

// Check if a path exists and return its type
int check_file_type(const char *path) {
    struct stat st;
    
    if (stat(path, &st) != 0) {
        return -1;  // Does not exist
    }
    
    if (S_ISDIR(st.st_mode)) {
        return 1;   // Directory
    } else {
        return 0;   // Regular file
    }
}

// Fast existence check using access()
int fast_file_exists(const char *path) {
    return access(path, F_OK) == 0;
}

// Calculate total number of possible combinations
long long calculate_total_combinations(const char *chars, int min_len, int max_len) {
    if (!chars || min_len <= 0 || max_len < min_len) return 0;
    
    size_t chars_len = strlen(chars);
    if (chars_len == 0) return 0;
    
    long long total = 0;
    
    for (int length = min_len; length <= max_len; length++) {
        long long combinations = 1;
        // Calculate chars_len^length
        for (int i = 0; i < length; i++) {
            combinations *= chars_len;
            // Check for overflow
            if (combinations < 0) return LLONG_MAX;
        }
        total += combinations;
        if (total < 0) return LLONG_MAX; // Overflow
    }
    
    return total;
}

// Get system information
void get_system_info(int *cpu_cores, long *page_size, long *total_memory) {
    if (cpu_cores) {
        *cpu_cores = sysconf(_SC_NPROCESSORS_ONLN);
        if (*cpu_cores < 1) *cpu_cores = 1;
    }
    
    if (page_size) {
        *page_size = sysconf(_SC_PAGESIZE);
        if (*page_size <= 0) *page_size = 4096;
    }
    
    if (total_memory) {
        long phys_pages = sysconf(_SC_PHYS_PAGES);
        long page_sz = sysconf(_SC_PAGESIZE);
        if (phys_pages > 0 && page_sz > 0) {
            *total_memory = phys_pages * page_sz;
        } else {
            *total_memory = 0;
        }
    }
}

// Smart scanning using common filename patterns
ScanResult* c_smart_scan(const char *path, const char *chars,
                        int min_len, int max_len) {
    ScanResult *result = result_create();
    if (!result) return NULL;
    
    // List of common filename patterns to check
    static const char *common_patterns[] = {
        // Single characters (a-z)
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        
        // Two-letter Unix commands
        "sh", "ls", "cp", "mv", "rm", "cd", "ps", "df", "du", "vi", "cc",
        "ln", "wc", "dd", "ed", "ex", "ks", "tc", "vi", "em", "pg",
        
        // Three-letter Unix commands
        "awk", "cat", "cut", "gcc", "gdb", "grep", "jar", "man", "noh",
        "perl", "php", "pwd", "sed", "ssh", "tar", "top", "vim", "who",
        "yes", "zip", "zsh", "ftp", "tel", "nsl", "dig", "wget", "curl",
        
        // System directories (3-4 chars)
        "bin", "dev", "etc", "lib", "tmp", "usr", "var", "sys", "proc",
        "mnt", "opt", "srv", "run", "home", "root", "boot", "media",
        "sbin", "lib64", "share", "local", "cache", "log", "spool",
        
        // Android specific directories
        "system", "vendor", "data", "cache", "acct", "apex", "config",
        "odm", "oem", "firmware", "persist", "metadata", "storage",
        
        // Common configuration files
        ".bashrc", ".profile", ".gitignore", "Makefile", "README",
        "LICENSE", "Dockerfile", ".env", "setup.py", "requirements.txt",
        "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
        
        // Common file extensions
        ".txt", ".log", ".cfg", ".conf", ".ini", ".yml", ".yaml", ".json",
        ".xml", ".html", ".php", ".py", ".c", ".cpp", ".java", ".js",
        
        NULL  // End marker
    };
    
    char test_path[MAX_PATH_LEN];
    
    // Check all common patterns
    for (int i = 0; common_patterns[i] != NULL; i++) {
        const char *pattern = common_patterns[i];
        size_t pattern_len = strlen(pattern);
        int pattern_len_int = (int)pattern_len;
        
        // Check length constraints
        if (pattern_len_int < min_len || pattern_len_int > max_len) {
            continue;
        }
        
        // Check character constraints (skip dots in pattern validation)
        int valid = 1;
        for (size_t j = 0; j < pattern_len; j++) {
            char c = pattern[j];
            // Skip dot at the beginning (hidden files) and common separators
            if (c != '.' && c != '_' && c != '-' && strchr(chars, c) == NULL) {
                valid = 0;
                break;
            }
        }
        
        if (!valid) continue;
        
        // Construct full path and check existence
        snprintf(test_path, sizeof(test_path), "%s/%s", path, pattern);
        int file_type = check_file_type(test_path);
        if (file_type >= 0) {
            result_add(result, pattern, file_type == 1);
        }
    }
    
    return result;
}
