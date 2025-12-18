// rfind/src/worker.c
#include "scanner.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>

// 在文件开头添加函数声明，避免隐式声明错误
struct CombinationGenerator* generator_create(const char *chars, int length);
void generator_free(struct CombinationGenerator *gen);
int generator_next(struct CombinationGenerator *gen, char *buffer);
int generator_set_index(struct CombinationGenerator *gen, long long index);
int check_file_type(const char *path);
int fast_file_exists(const char *path);
ScanResult* result_create(void);
void result_free(ScanResult *result);
int result_add(ScanResult *result, const char *name, int is_dir);
long long calculate_total_combinations(const char *chars, int min_len, int max_len);

// Worker thread function
void* scan_worker(void *arg) {
    WorkerContext *ctx = (WorkerContext *)arg;
    char test_path[MAX_PATH_LEN];
    char filename[MAX_FILENAME_LEN];
    
    // Get character set length
    size_t chars_len = strlen(ctx->chars);
    if (chars_len == 0) return NULL;
    
    // Process all lengths in the range
    for (int length = ctx->min_len; length <= ctx->max_len; length++) {
        // Calculate combinations for this specific length
        long long combos_for_length = 1;
        for (int i = 0; i < length; i++) {
            if (chars_len > 0 && combos_for_length > (LLONG_MAX / (long long)chars_len)) {
                combos_for_length = LLONG_MAX;
                break;
            }
            combos_for_length *= (long long)chars_len;
        }
        
        // Calculate start and end indices for this thread for this length
        long long start_idx = 0;
        long long end_idx = combos_for_length;
        
        // If start_combo/end_combo are specified (for parallel by index)
        if (ctx->start_combo >= 0 && ctx->end_combo >= ctx->start_combo) {
            // Convert global index range to per-length ranges
            long long length_start = 0;
            for (int l = ctx->min_len; l < length; l++) {
                long long len_combos = 1;
                for (int i = 0; i < l; i++) {
                    if (chars_len > 0 && len_combos > (LLONG_MAX / (long long)chars_len)) {
                        len_combos = LLONG_MAX;
                        break;
                    }
                    len_combos *= (long long)chars_len;
                }
                if (length_start > LLONG_MAX - len_combos) {
                    length_start = LLONG_MAX;
                    break;
                }
                length_start += len_combos;
            }
            
            start_idx = (ctx->start_combo > length_start) ? 
                       (ctx->start_combo - length_start) : 0;
            end_idx = (ctx->end_combo < length_start + combos_for_length) ?
                     (ctx->end_combo - length_start) : combos_for_length;
            
            if (start_idx >= combos_for_length || end_idx <= start_idx) {
                continue; // This thread has no work for this length
            }
        }
        
        // Create generator for this length
        struct CombinationGenerator *gen = generator_create(ctx->chars, length);
        if (!gen) continue;
        
        // Set generator to start index
        if (!generator_set_index(gen, start_idx)) {
            generator_free(gen);
            continue;
        }
        
        // Process combinations
        long long processed = 0;
        long long to_process = end_idx - start_idx;
        
        while (processed < to_process && generator_next(gen, filename)) {
            // Construct full path
            snprintf(test_path, sizeof(test_path), "%s/%s", ctx->base_path, filename);
            
            // Check if file exists and get its type
            int file_type = check_file_type(test_path);
            if (file_type >= 0) {
                // Lock mutex and add result
                pthread_mutex_lock(ctx->mutex);
                result_add(ctx->result, filename, file_type == 1);
                pthread_mutex_unlock(ctx->mutex);
            }
            
            processed++;
        }
        
        generator_free(gen);
    }
    
    return NULL;
}

// Main parallel scanning function
ScanResult* c_parallel_scan(const char *path, const char *chars,
                           int min_len, int max_len, int threads) {
    // Validate parameters
    if (!path || !chars || min_len <= 0 || max_len < min_len) {
        return NULL;
    }
    
    // Auto-detect CPU cores if threads <= 0
    if (threads <= 0) {
        #ifdef _SC_NPROCESSORS_ONLN
        threads = sysconf(_SC_NPROCESSORS_ONLN);
        #else
        threads = 1;
        #endif
    }
    
    // Limit threads to MAX_WORKERS
    if (threads > MAX_WORKERS) {
        threads = MAX_WORKERS;
    }
    
    // If single thread or small search space, use single-threaded approach
    size_t chars_len = strlen(chars);
    long long total_combinations = calculate_total_combinations(chars, min_len, max_len);
    
    if (threads == 1 || total_combinations < 1000) {
        // Single-threaded implementation
        ScanResult *result = result_create();
        if (!result) return NULL;
        
        for (int length = min_len; length <= max_len; length++) {
            struct CombinationGenerator *gen = generator_create(chars, length);
            if (!gen) continue;
            
            char filename[MAX_FILENAME_LEN];
            char test_path[MAX_PATH_LEN];
            
            while (generator_next(gen, filename)) {
                snprintf(test_path, sizeof(test_path), "%s/%s", path, filename);
                int file_type = check_file_type(test_path);
                if (file_type >= 0) {
                    result_add(result, filename, file_type == 1);
                }
            }
            
            generator_free(gen);
        }
        
        return result;
    }
    
    // Multi-threaded implementation
    ScanResult *result = result_create();
    if (!result) return NULL;
    
    pthread_mutex_t mutex;
    if (pthread_mutex_init(&mutex, NULL) != 0) {
        result_free(result);
        return NULL;
    }
    
    pthread_t workers[MAX_WORKERS];
    WorkerContext contexts[MAX_WORKERS];
    
    // Calculate combinations per thread
    long long combos_per_thread = total_combinations / threads;
    long long remainder = total_combinations % threads;
    
    // Create worker threads
    for (int i = 0; i < threads; i++) {
        contexts[i].base_path = path;
        contexts[i].chars = chars;
        contexts[i].min_len = min_len;
        contexts[i].max_len = max_len;
        contexts[i].result = result;
        contexts[i].mutex = &mutex;
        contexts[i].thread_id = i;
        contexts[i].total_threads = threads;
        contexts[i].start_combo = i * combos_per_thread;
        contexts[i].end_combo = (i == threads - 1) ? 
                               total_combinations : 
                               (i + 1) * combos_per_thread;
        
        // Adjust for remainder
        if (i < remainder) {
            contexts[i].start_combo += i;
            contexts[i].end_combo += (i + 1);
        } else {
            contexts[i].start_combo += remainder;
            contexts[i].end_combo += remainder;
        }
        
        if (pthread_create(&workers[i], NULL, scan_worker, &contexts[i]) != 0) {
            // Clean up created threads on error
            for (int j = 0; j < i; j++) {
                pthread_join(workers[j], NULL);
            }
            pthread_mutex_destroy(&mutex);
            result_free(result);
            return NULL;
        }
    }
    
    // Wait for all threads to complete
    for (int i = 0; i < threads; i++) {
        pthread_join(workers[i], NULL);
    }
    
    pthread_mutex_destroy(&mutex);
    return result;
}
