#include "field.h"
#include "validator/validator.h"

static PyObject*
converter_bool(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    if (Long_Zero == val) {
        Py_RETURN_FALSE;
    }
    if (Long_One == val) {
        Py_RETURN_TRUE;
    }

    int r = EqString(val, "1", 1);
    if (r != -1) {
        if (r == 1 || EqString(val, "true", 4) || EqString(val, "True", 4)) {
            Py_RETURN_TRUE;
        }

        if (EqString(val, "0", 1) || EqString(val, "false", 5) ||
            EqString(val, "False", 5)) {
            Py_RETURN_FALSE;
        }
    }

    if (PyFloat_Check(val)) {
        double double_val = PyFloat_AsDouble(val);
        if (double_val == 1.0) {
            Py_RETURN_TRUE;
        }
        if (double_val == 0.0) {
            Py_RETURN_FALSE;
        }
        return NULL;
    }
    return NULL;
}

TypeAdapter*
TypeAdapter_Create_Bool(PyObject* hint)
{
    return TypeAdapter_Create(hint,
                              NULL,
                              NULL,
                              TypeAdapter_Base_Repr,
                              converter_bool,
                              Inspector_IsType,
                              NULL);
}
