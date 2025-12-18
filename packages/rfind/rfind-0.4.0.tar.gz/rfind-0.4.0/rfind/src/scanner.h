// rfind/src/scanner.h
#ifndef RFIND_SCANNER_H
#define RFIND_SCANNER_H

#include <stddef.h>
#include <pthread.h>
#include <unistd.h>
#include <limits.h>

#define MAX_PATH_LEN 4096
#define MAX_FILENAME_LEN 256
#define MAX_WORKERS 64

// Structure to hold file information
typedef struct {
    char *name;      // Filename
    int is_dir;      // 1 if directory, 0 if file
} FileItem;

// Structure to hold scan results
typedef struct {
    FileItem *items;     // Array of found items
    size_t count;        // Number of items found
    size_t capacity;     // Current array capacity
} ScanResult;

// Context for worker threads - WITH start_combo and end_combo
typedef struct {
    const char *base_path;   // Directory to scan
    const char *chars;       // Character set for filenames
    int min_len;            // Minimum filename length
    int max_len;            // Maximum filename length
    ScanResult *result;     // Shared results
    pthread_mutex_t *mutex; // Mutex for thread-safe operations
    int thread_id;          // Thread ID (0-based)
    int total_threads;      // Total number of threads
    long long start_combo;  // Starting combination index for this thread
    long long end_combo;    // Ending combination index for this thread
} WorkerContext;

// Forward declaration for combination generator
struct CombinationGenerator;

// Combination generator functions
struct CombinationGenerator* generator_create(const char *chars, int length);
void generator_free(struct CombinationGenerator *gen);
int generator_next(struct CombinationGenerator *gen, char *buffer);
int generator_set_index(struct CombinationGenerator *gen, long long index);

// Result management functions
ScanResult* result_create(void);
void result_free(ScanResult *result);
int result_add(ScanResult *result, const char *name, int is_dir);

// Filesystem functions
int check_file_type(const char *path);
int fast_file_exists(const char *path);

// Scanning functions
ScanResult* c_parallel_scan(const char *path, const char *chars,
                           int min_len, int max_len, int threads);
ScanResult* c_smart_scan(const char *path, const char *chars,
                        int min_len, int max_len);

// Utility functions
long long calculate_total_combinations(const char *chars, int min_len, int max_len);
void get_system_info(int *cpu_cores, long *page_size, long *total_memory);

#endif // RFIND_SCANNER_H
