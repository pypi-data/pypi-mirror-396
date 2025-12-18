// rfind/src/rfindmodule.c
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "scanner.h"

// Function declarations (already in scanner.h, but we need them for linking)
extern ScanResult* c_parallel_scan(const char *path, const char *chars,
                                  int min_len, int max_len, int threads);
extern ScanResult* c_smart_scan(const char *path, const char *chars,
                               int min_len, int max_len);
extern void get_system_info(int *cpu_cores, long *page_size, long *total_memory);
extern long long calculate_total_combinations(const char *chars, int min_len, int max_len);

// Python wrapper for scan_directory
static PyObject* py_scan_directory(PyObject* self, PyObject* args, PyObject* kwargs) {
    (void)self;  // Unused parameter
    
    const char *path = ".";
    const char *chars = "abcdefghijklmnopqrstuvwxyz";
    int min_len = 1;
    int max_len = 3;
    int threads = 0;  // 0 means auto-detect
    
    static char *keywords[] = {"path", "chars", "min_len", "max_len", "threads", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ssiii", keywords,
                                     &path, &chars, &min_len, &max_len, &threads)) {
        return NULL;
    }
    
    // Validate parameters
    if (min_len <= 0) {
        PyErr_SetString(PyExc_ValueError, "min_len must be positive");
        return NULL;
    }
    
    if (max_len < min_len) {
        PyErr_SetString(PyExc_ValueError, "max_len must be >= min_len");
        return NULL;
    }
    
    if (max_len > 10) {  // Reasonable limit
        PyErr_SetString(PyExc_ValueError, "max_len too large (max 10)");
        return NULL;
    }
    
    // Call C function
    ScanResult *result = c_parallel_scan(path, chars, min_len, max_len, threads);
    if (!result) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to scan directory");
        return NULL;
    }
    
    // Convert to Python list of tuples
    PyObject *py_list = PyList_New(result->count);
    if (!py_list) {
        result_free(result);
        return NULL;
    }
    
    for (size_t i = 0; i < result->count; i++) {
        PyObject *tuple = Py_BuildValue("(si)", 
                                       result->items[i].name,
                                       result->items[i].is_dir);
        if (!tuple) {
            result_free(result);
            Py_DECREF(py_list);
            return NULL;
        }
        PyList_SetItem(py_list, i, tuple);
    }
    
    result_free(result);
    return py_list;
}

// Python wrapper for smart_scan
static PyObject* py_smart_scan(PyObject* self, PyObject* args, PyObject* kwargs) {
    (void)self;  // Unused parameter
    
    const char *path = ".";
    const char *chars = "abcdefghijklmnopqrstuvwxyz";
    int min_len = 1;
    int max_len = 3;
    
    static char *keywords[] = {"path", "chars", "min_len", "max_len", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|ssii", keywords,
                                     &path, &chars, &min_len, &max_len)) {
        return NULL;
    }
    
    // Validate parameters
    if (min_len <= 0 || max_len < min_len) {
        PyErr_SetString(PyExc_ValueError, "Invalid length parameters");
        return NULL;
    }
    
    ScanResult *result = c_smart_scan(path, chars, min_len, max_len);
    if (!result) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to smart scan directory");
        return NULL;
    }
    
    PyObject *py_list = PyList_New(result->count);
    if (!py_list) {
        result_free(result);
        return NULL;
    }
    
    for (size_t i = 0; i < result->count; i++) {
        PyObject *tuple = Py_BuildValue("(si)", 
                                       result->items[i].name,
                                       result->items[i].is_dir);
        if (!tuple) {
            result_free(result);
            Py_DECREF(py_list);
            return NULL;
        }
        PyList_SetItem(py_list, i, tuple);
    }
    
    result_free(result);
    return py_list;
}

// Python wrapper for get_system_info
static PyObject* py_get_system_info(PyObject* self, PyObject* args) {
    (void)self;  // Unused parameters
    (void)args;
    
    int cpu_cores = 0;
    long page_size = 0;
    long total_memory = 0;
    
    // Call the C function
    get_system_info(&cpu_cores, &page_size, &total_memory);
    
    PyObject *info = PyDict_New();
    if (!info) return NULL;
    
    // Add system information to dictionary
    PyDict_SetItemString(info, "cpu_cores", PyLong_FromLong(cpu_cores));
    PyDict_SetItemString(info, "page_size", PyLong_FromLong(page_size));
    PyDict_SetItemString(info, "total_memory", PyLong_FromLong(total_memory));
    
    return info;
}

// Python wrapper for calculate_combinations
static PyObject* py_calculate_combinations(PyObject* self, PyObject* args) {
    (void)self;  // Unused parameter
    
    const char *chars = "abcdefghijklmnopqrstuvwxyz";
    int min_len = 1;
    int max_len = 3;
    
    if (!PyArg_ParseTuple(args, "|sii", &chars, &min_len, &max_len)) {
        return NULL;
    }
    
    long long total = calculate_total_combinations(chars, min_len, max_len);
    
    // Python 3 has proper long support
    return PyLong_FromLongLong(total);
}

// Wrapper functions for METH_VARARGS
static PyObject* scan_directory_wrapper(PyObject* self, PyObject* args) {
    return py_scan_directory(self, args, NULL);
}

static PyObject* smart_scan_wrapper(PyObject* self, PyObject* args) {
    return py_smart_scan(self, args, NULL);
}

// Module method definitions
static PyMethodDef RFindMethods[] = {
    {"scan_directory", scan_directory_wrapper, 
     METH_VARARGS, 
     "Scan directory with brute force enumeration.\n"
     "Args:\n"
     "  path (str): Directory path (default: '.')\n"
     "  chars (str): Character set for filenames (default: 'a-z')\n"
     "  min_len (int): Minimum filename length (default: 1)\n"
     "  max_len (int): Maximum filename length (default: 3)\n"
     "  threads (int): Number of threads (0=auto, default: 0)\n"
     "Returns:\n"
     "  list: List of (filename, is_dir) tuples"},
    
    {"smart_scan", smart_scan_wrapper,
     METH_VARARGS,
     "Scan directory using common filename patterns.\n"
     "Args:\n"
     "  path (str): Directory path (default: '.')\n"
     "  chars (str): Character set for validation (default: 'a-z')\n"
     "  min_len (int): Minimum filename length (default: 1)\n"
     "  max_len (int): Maximum filename length (default: 3)\n"
     "Returns:\n"
     "  list: List of (filename, is_dir) tuples"},
    
    {"get_system_info", py_get_system_info,
     METH_NOARGS,
     "Get system information for optimization.\n"
     "Returns:\n"
     "  dict: Dictionary with cpu_cores, page_size, total_memory"},
    
    {"calculate_combinations", py_calculate_combinations,
     METH_VARARGS,
     "Calculate total number of possible combinations.\n"
     "Args:\n"
     "  chars (str): Character set (default: 'a-z')\n"
     "  min_len (int): Minimum length (default: 1)\n"
     "  max_len (int): Maximum length (default: 3)\n"
     "Returns:\n"
     "  int: Total number of combinations"},
    
    {NULL, NULL, 0, NULL}  // Sentinel
};

// Module definition
static struct PyModuleDef rfindmodule = {
    PyModuleDef_HEAD_INIT,
    "_rfind",                     // Module name
    "C-accelerated file discovery engine for directories with execute-only permission",  // Module doc
    -1,                          // Module state size
    RFindMethods,                // Method definitions
    NULL,                        // m_slots
    NULL,                        // m_traverse
    NULL,                        // m_clear
    NULL                         // m_free
};

// Module initialization
PyMODINIT_FUNC PyInit__rfind(void) {
    PyObject *module = PyModule_Create(&rfindmodule);
    if (module == NULL) {
        return NULL;
    }
    
    // Add version constant
    PyModule_AddStringConstant(module, "__version__", "0.4.2");
    
    // Add configuration constants
    PyModule_AddIntConstant(module, "MAX_WORKERS", MAX_WORKERS);
    PyModule_AddIntConstant(module, "MAX_PATH_LEN", MAX_PATH_LEN);
    PyModule_AddIntConstant(module, "MAX_FILENAME_LEN", MAX_FILENAME_LEN);
    
    // Add default character sets as constants
    PyModule_AddStringConstant(module, "CHARS_LOWERCASE", "abcdefghijklmnopqrstuvwxyz");
    PyModule_AddStringConstant(module, "CHARS_UPPERCASE", "ABCDEFGHIJKLMNOPQRSTUVWXYZ");
    PyModule_AddStringConstant(module, "CHARS_DIGITS", "0123456789");
    PyModule_AddStringConstant(module, "CHARS_ALPHANUM", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789");
    PyModule_AddStringConstant(module, "CHARS_ALL", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.");
    
    return module;
}
