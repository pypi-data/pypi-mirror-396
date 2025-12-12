#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define SequenceConstraints_CheckExact(op)                                     \
    Py_IS_TYPE((op), &SequenceConstraintsType)

typedef struct TypeAdapter TypeAdapter;
typedef struct ValidateContext ValidateContext;
typedef struct
{
    PyObject_HEAD Py_ssize_t min_length;
    Py_ssize_t max_length;
} SequenceConstraints;

extern PyTypeObject SequenceConstraintsType;
extern int
sequence_constraint_setup(void);
extern void
sequence_constraint_free(void);
extern PyObject*
SequenceConstraints_Converter(TypeAdapter*, ValidateContext*, PyObject*);
extern int
_SequenceConstraints_CheckSize(TypeAdapter* validator,
                               ValidateContext* ctx,
                               PyObject* val);