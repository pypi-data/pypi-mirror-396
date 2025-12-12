#define PY_SSIZE_T_CLEAN
#include "Python.h"
#define ComputedField_Check(o) (Py_TYPE(o) == &ComputedFieldType)

typedef struct Field Field;
typedef struct ComputedField
{
    PyObject_HEAD PyObject* callable;
    vectorcallfunc vectorcall;
    Field* field;
    unsigned char cache;
} ComputedField;

extern PyTypeObject ComputedFieldType;
extern PyObject*
ComputedField_GetAnnotated(ComputedField*);
extern int
computed_field_setup(void);
extern void
computed_field_free(void);