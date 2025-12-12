#define PY_SSIZE_T_CLEAN
#include "Python.h"
typedef struct TypeAdapter TypeAdapter;
extern TypeAdapter*
TypeAdapter_Create_UnionType(PyObject*, PyObject*);