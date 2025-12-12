#define PY_SSIZE_T_CLEAN
#include "Python.h"
typedef struct TypeAdapter TypeAdapter;

extern TypeAdapter*
TypeAdapter_Create_Literal(PyObject* hint);
extern int
validator_literal_setup(void);
extern void
validator_literal_free(void);