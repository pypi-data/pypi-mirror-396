#define PY_SSIZE_T_CLEAN
#include "Python.h"
#define ComparisonConstraints_CheckExact(op)                                   \
    Py_IS_TYPE((op), &ComparisonConstraintsType)

typedef struct TypeAdapter TypeAdapter;
typedef struct ValidateContext ValidateContext;
typedef struct
{
    PyObject_HEAD PyObject* gt; // >
    PyObject* ge;               // >=
    PyObject* lt;               // <
    PyObject* le;               // <=
} ComparisonConstraints;

extern PyTypeObject ComparisonConstraintsType;
extern int
comparison_constraint_setup(void);
extern void
comparison_constraint_free(void);
extern PyObject*
ComparisonConstraints_Converter(TypeAdapter*, ValidateContext*, PyObject*);