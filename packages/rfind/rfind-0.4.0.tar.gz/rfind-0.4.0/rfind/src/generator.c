// rfind/src/generator.c
#include "scanner.h"
#include <stdlib.h>
#include <string.h>

// Combination generator structure
struct CombinationGenerator {
    char *chars;           // Character set
    int length;           // Length of combinations to generate
    long long total;      // Total number of combinations
    long long current;    // Current combination index
    char *current_comb;   // Current combination buffer
};

// Create a new combination generator
struct CombinationGenerator* generator_create(const char *chars, int length) {
    if (!chars || length <= 0) return NULL;
    
    struct CombinationGenerator *gen = malloc(sizeof(struct CombinationGenerator));
    if (!gen) return NULL;
    
    gen->chars = strdup(chars);
    if (!gen->chars) {
        free(gen);
        return NULL;
    }
    
    gen->length = length;
    
    // Calculate total combinations: chars_len^length
    size_t chars_len = strlen(chars);
    gen->total = 1;
    for (int i = 0; i < length; i++) {
        // Check for overflow
        if (chars_len > 0 && gen->total > (LLONG_MAX / (long long)chars_len)) {
            gen->total = LLONG_MAX;
            break;
        }
        gen->total *= (long long)chars_len;
    }
    
    gen->current = 0;
    gen->current_comb = calloc(length + 1, sizeof(char));
    if (!gen->current_comb) {
        free(gen->chars);
        free(gen);
        return NULL;
    }
    
    // Initialize with first combination
    for (int i = 0; i < length; i++) {
        gen->current_comb[i] = chars[0];
    }
    gen->current_comb[length] = '\0';
    
    return gen;
}

// Free a combination generator
void generator_free(struct CombinationGenerator *gen) {
    if (!gen) return;
    free(gen->chars);
    free(gen->current_comb);
    free(gen);
}

// Get the next combination
int generator_next(struct CombinationGenerator *gen, char *buffer) {
    if (!gen || !buffer || gen->current >= gen->total) {
        return 0;
    }
    
    // Convert current index to combination
    size_t chars_len = strlen(gen->chars);
    long long n = gen->current;
    
    for (int i = gen->length - 1; i >= 0; i--) {
        gen->current_comb[i] = gen->chars[n % chars_len];
        n /= chars_len;
    }
    gen->current_comb[gen->length] = '\0';
    
    strcpy(buffer, gen->current_comb);
    gen->current++;
    
    return 1;
}

// Set generator to specific index
int generator_set_index(struct CombinationGenerator *gen, long long index) {
    if (!gen || index < 0 || index >= gen->total) {
        return 0;
    }
    
    gen->current = index;
    size_t chars_len = strlen(gen->chars);
    long long n = index;
    
    // Convert index to combination
    for (int i = gen->length - 1; i >= 0; i--) {
        gen->current_comb[i] = gen->chars[n % chars_len];
        n /= chars_len;
    }
    gen->current_comb[gen->length] = '\0';
    
    return 1;
}
