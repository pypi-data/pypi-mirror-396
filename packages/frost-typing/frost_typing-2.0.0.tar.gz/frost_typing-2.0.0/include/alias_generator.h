#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define AliasGenerator_Check(o) Py_IS_TYPE(o, &AliasGeneratorType)

typedef struct AliasGenerator
{
    PyObject_HEAD PyObject* alias;
    PyObject* serialization_alias;
} AliasGenerator;

extern PyTypeObject AliasGeneratorType;

extern int
alias_generator_setup(void);
extern void
alias_generator_free(void);
extern int
AliasGenerator_CreateAlias(AliasGenerator* self,
                           PyObject* name,
                           PyObject** alias,
                           PyObject** serialization_alias);