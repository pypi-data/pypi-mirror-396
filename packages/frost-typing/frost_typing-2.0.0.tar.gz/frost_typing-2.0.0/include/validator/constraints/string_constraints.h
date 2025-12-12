#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "validator/constraints/sequence_constraints.h"

#define StringConstraints_CheckExact(op)                                       \
    Py_IS_TYPE((op), &StringConstraintsType)

extern PyObject *__string_too_short, *__string_too_long,
  *__string_not_printable, *__string_not_ascii;

typedef struct TypeAdapter TypeAdapter;
typedef struct ValidateContext ValidateContext;

typedef struct
{
    SequenceConstraints base;
    PyObject* pattern_string;
    PyMethodObject* pattern;
    char strip_whitespace;
    char is_printable;
    char to_upper;
    char to_lower;
    char is_ascii;
} StringConstraints;

extern PyTypeObject StringConstraintsType;
extern int
string_constraint_setup(void);
extern void
string_constraint_free(void);
extern PyObject*
StringConstraints_Converter(TypeAdapter*, ValidateContext*, PyObject*);