#define PY_SSIZE_T_CLEAN
#include "Python.h"

extern PyObject*
Schema_JsonSchema(PyObject* schema);
extern int
json_schema_setup(void);
extern void
json_schema_free(void);