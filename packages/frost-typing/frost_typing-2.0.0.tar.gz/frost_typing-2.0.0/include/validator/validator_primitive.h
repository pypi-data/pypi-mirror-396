#define PY_SSIZE_T_CLEAN
#include "Python.h"
typedef struct TypeAdapter TypeAdapter;

extern TypeAdapter*
TypeAdapter_Create_Primitive(PyObject*);
extern int
validator_primitive_setup(void);
extern void
validator_primitive_free(void);