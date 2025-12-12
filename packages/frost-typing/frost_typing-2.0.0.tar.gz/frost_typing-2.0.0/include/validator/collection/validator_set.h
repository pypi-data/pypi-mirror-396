#define PY_SSIZE_T_CLEAN
#include "Python.h"
typedef struct TypeAdapter TypeAdapter;

extern TypeAdapter*
_TypeAdapter_Create_Set(PyObject* cls, PyObject* type_args, PyObject* tp);