#define PY_SSIZE_T_CLEAN
#include "Python.h"
typedef struct TypeAdapter TypeAdapter;

extern TypeAdapter*
_TypeAdapter_Create_Tuple(PyObject* cls, PyObject* type_args, PyObject* tp);
extern int
validator_tuple_setup(void);
extern void
validator_tuple_free(void);