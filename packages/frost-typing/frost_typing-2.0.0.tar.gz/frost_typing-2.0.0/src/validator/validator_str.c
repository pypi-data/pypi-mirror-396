#include "field.h"
#include "validator/validator.h"

static PyObject*
converter_unicode(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    if (PyUnicode_Check(val)) {
        return PyUnicode_FromObject(val);
    }

    if (PyBytes_Check(val) || PyByteArray_Check(val)) {
        return PyUnicode_FromEncodedObject(val, NULL, NULL);
    }

    if ((ctx->flags & FIELD_NUM_TO_STR) &&
        (PyLong_Check(val) || PyFloat_Check(val))) {
        return PyObject_Str(val);
    }
    return NULL;
}

TypeAdapter*
TypeAdapter_Create_Str(PyObject* hint)
{
    return TypeAdapter_Create(hint,
                              NULL,
                              NULL,
                              TypeAdapter_Base_Repr,
                              converter_unicode,
                              Inspector_IsType,
                              NULL);
}
