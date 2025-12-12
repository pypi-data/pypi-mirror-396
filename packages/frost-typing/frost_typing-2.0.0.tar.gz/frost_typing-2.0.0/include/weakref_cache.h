#define PY_SSIZE_T_CLEAN
#include "Python.h"

extern PyTypeObject WeakrefCacheType;
extern void
WeakrefCache_SetItem(PyObject* self, PyObject* key, PyObject* val);
extern PyObject*
WeakrefCache_GetItem(PyObject* self, PyObject* key);
extern int
weakref_cache_setup(void);
extern void
weakref_cache_free(void);