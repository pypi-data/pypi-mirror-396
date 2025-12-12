#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define FieldValidator_Check(op)                                               \
    PyType_IsSubtype(Py_TYPE(op), &FieldValidatorType)
#define FieldValidator_CheckExact(op) Py_IS_TYPE((op), &FieldValidatorType)

#define FIELD_VALIDATOR_WRAP (uint8_t)(1)
#define FIELD_VALIDATOR_BEFORE (uint8_t)(1 << 1)
#define FIELD_VALIDATOR_AFRET (uint8_t)(1 << 2)

typedef struct TypeAdapter TypeAdapter;
typedef struct
{
    PyObject_HEAD PyObject* func;
    vectorcallfunc vectorcall;
    PyObject* fields_name;
    uint8_t flags;
} FieldValidator;

extern PyTypeObject FieldValidatorType;
extern int
field_validator_setup(void);
extern void
field_validator_free(void);
extern int
FieldValidator_CheckRegistered(PyObject*);
extern void
_FieldValidator_Clear(PyObject* tp);
extern TypeAdapter*
TypeAdapter_Create_FieldValidator(PyObject* hint,
                                  PyObject* type,
                                  PyObject* name);
extern TypeAdapter*
_TypeAdapter_Create_FieldValidator(TypeAdapter* validator,
                                   PyObject* type,
                                   PyObject* name);