#include "field.h"
#include "validator/validator.h"

static PyObject*
validator_union_repr(TypeAdapter* self)
{
    PyObject* tmp;
    UnicodeWriter_Create(writer, 16);
    if (!writer) {
        return NULL;
    }

    _UNICODE_WRITE_STRING(writer, "Union[", 6);
    Py_ssize_t size = PyTuple_GET_SIZE(self->cls);
    for (Py_ssize_t i = 0; i != size; i++) {
        if (i) {
            _UNICODE_WRITE_STRING(writer, ", ", 2);
        }
        tmp = PyTuple_GET_ITEM(self->cls, i);
        if (_ContextManager_ReprModel(writer, tmp) < 0) {
            goto error;
        }
    }

    _UNICODE_WRITE_CHAR(writer, ']');
    return UnicodeWriter_Finish(writer);

error:
    UnicodeWriter_Discard(writer);
    return NULL;
}

static PyObject*
converter_union(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    TupleForeach(vd, self->args)
    {
        TypeAdapter* adapter = (TypeAdapter*)vd;
        PyObject* tmp = adapter->conv(adapter, ctx, val);
        if (tmp) {
            return tmp;
        }
        PyErr_Clear();
    }

    return NULL;
}

TypeAdapter*
TypeAdapter_Create_Union(PyObject* hint, PyObject* tp)
{
    PyObject* type_args = PyTyping_Get_Args(hint);
    if (FT_UNLIKELY(!type_args)) {
        return NULL;
    }

    PyObject *args, *cls;
    args = cls = TypeAdapter_MapParseHintTuple(type_args, tp);
    Py_DECREF(type_args);
    if (FT_UNLIKELY(!cls)) {
        return NULL;
    }

    TypeAdapter* res = TypeAdapter_Create(cls,
                                          args,
                                          NULL,
                                          validator_union_repr,
                                          converter_union,
                                          Inspector_IsInstanceTypeAdapter,
                                          NULL);
    Py_DECREF(args);
    return res;
}