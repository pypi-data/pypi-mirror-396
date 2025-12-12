#include "validator/validator.h"

int
IsConstraints(PyObject* obj)
{
    PyTypeObject* tp = Py_TYPE(obj);
    return (tp == &ComparisonConstraintsType ||
            tp == &SequenceConstraintsType || tp == &StringConstraintsType ||
            tp == &DateTimeConstraintsType);
}

int
is_str_validator(TypeAdapter* validator)
{
    if (TypeAdapter_Check(validator->cls)) {
        return is_str_validator((TypeAdapter*)validator->cls);
    }
    if (!PyType_Check(validator->cls)) {
        return 0;
    }
    PyTypeObject* tp = (PyTypeObject*)validator->cls;
    return tp->tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS;
}

TypeAdapter*
TypeAdapter_Create_Constraints(TypeAdapter* validator, PyObject* constraints)
{
    PyTypeObject* tp_constraints = Py_TYPE(constraints);
    if (tp_constraints == &StringConstraintsType) {
        if (!is_str_validator(validator)) {
            PyErr_SetString(FrostUserError,
                            "StringConstraints supports only"
                            " the inheritors of str");
            return NULL;
        }
        return TypeAdapter_Create((PyObject*)validator,
                                  constraints,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  StringConstraints_Converter,
                                  Inspector_No,
                                  NULL);
    }

    if (tp_constraints == &ComparisonConstraintsType) {
        return TypeAdapter_Create((PyObject*)validator,
                                  constraints,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  ComparisonConstraints_Converter,
                                  Inspector_No,
                                  NULL);
    }
    if (tp_constraints == &SequenceConstraintsType) {
        return TypeAdapter_Create((PyObject*)validator,
                                  constraints,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  SequenceConstraints_Converter,
                                  Inspector_No,
                                  NULL);
    }
    if (tp_constraints == &DateTimeConstraintsType) {
        return TypeAdapter_Create((PyObject*)validator,
                                  constraints,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  DateTime_Converter,
                                  Inspector_No,
                                  NULL);
    }
    Py_INCREF(validator);
    return validator;
}

int
constraints_setup(void)
{
    if (comparison_constraint_setup() < 0 || sequence_constraint_setup() < 0 ||
        string_constraint_setup() < 0 || datetime_constraint_setup() < 0) {
        return -1;
    }
    return 0;
}

void
constraints_free(void)
{
    datetime_constraint_free();
    sequence_constraint_free();
    comparison_constraint_free();
    string_constraint_free();
}