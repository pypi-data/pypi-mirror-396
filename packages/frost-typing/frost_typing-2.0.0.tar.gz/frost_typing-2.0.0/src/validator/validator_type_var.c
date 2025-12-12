#include "validator/validator.h"

static PyObject*
validator_type_var_repr(TypeAdapter* self)
{
    PyObject* bound = PyTuple_GET_ITEM(self->args, 0);
    if (bound != Py_None) {
        if (PyType_Check(bound)) {
            return PyObject_Get__name__((PyTypeObject*)bound);
        }
        return PyObject_Repr(bound);
    }

    PyObject* constraints = PyTuple_GET_ITEM(self->args, 1);
    Py_ssize_t size = PyTuple_GET_SIZE(constraints);
    if (!size) {
        return PyObject_Repr(self->cls);
    }

    UnicodeWriter_Create(writer, 8);
    if (!writer) {
        return NULL;
    }

    _UNICODE_WRITE_STRING(writer, "TypeVar[", 8);
    for (Py_ssize_t i = 0; i != size; i++) {
        if (i) {
            _UNICODE_WRITE_STRING(writer, ", ", 2);
        }
        PyObject* tmp = PyTuple_GET_ITEM(constraints, i);
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
converter_type_var(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    TypeAdapter* validator;
    int r = _ContextManager_Get_TTypeAdapter(self->cls, ctx->ctx, &validator);
    if (FT_UNLIKELY(r < 0)) {
        return NULL;
    } else if (r) {
        PyObject* res = TypeAdapter_Conversion(validator, ctx, val);
        if (FT_UNLIKELY(!res)) {
            ValidationError_Raise(NULL, validator, val, ctx->model);
        }
        return res;
    }

#if PY313_PLUS
    if (FT_UNLIKELY(Py_SIZE(self->args) == 3)) {
        validator = (TypeAdapter*)PyTuple_GET_ITEM(self->args, 2);
        PyObject* res = TypeAdapter_Conversion(validator, ctx, val);
        if (FT_UNLIKELY(!res)) {
            ValidationError_Raise(NULL, validator, val, ctx->model);
        }
        return res;
    }
#endif

    PyObject *type, *bound, *constraints;
    type = (PyObject*)Py_TYPE(val);
    bound = PyTuple_GET_ITEM(self->args, 0);
    constraints = PyTuple_GET_ITEM(self->args, 1);

    if (bound != Py_None) {
        if (PyObject_IsSubclass(type, bound) != 1) {
            return NULL;
        }
    }

    if (PyTuple_GET_SIZE(constraints)) {
        if (PyObject_IsSubclass(type, constraints) != 1) {
            return NULL;
        }
    }
    return Py_NewRef(val);
}

static PyObject*
get_args(PyObject* hint)
{
    PyObject* bound = PyTyping_Get_Bound(hint);
    if (!bound) {
        return NULL;
    }

    PyObject* constraints = PyTyping_Get_Constraints(hint);
    if (!constraints) {
        Py_DECREF(bound);
        return NULL;
    }

    TupleForeach(tmp, constraints)
    {
        if (!PyType_Check(tmp)) {
            Py_DECREF(bound);
            Py_DECREF(constraints);
            _RaiseInvalidType("__constraints__", "type", Py_TYPE(tmp)->tp_name);
            return NULL;
        }
    }

#if PY313_PLUS
    PyObject* default_val = PyObject_GetAttrString(hint, "__default__");
    if (FT_UNLIKELY(!default_val)) {
        goto error;
    }

    PyObject* args;
    if (default_val == PyNoDefault) {
        args = PyTuple_Pack(2, bound, constraints);
        Py_DECREF(default_val);
    } else {
        TypeAdapter* d_vd = ParseHint(default_val, NULL);
        Py_DECREF(default_val);
        if (FT_UNLIKELY(!d_vd)) {
            goto error;
        }
        args = PyTuple_Pack(3, bound, constraints, d_vd);
        Py_DECREF(d_vd);
    }
#else
    PyObject* args = PyTuple_Pack(2, bound, constraints);
#endif

    Py_DECREF(constraints);
    Py_DECREF(bound);
    return args;

#if PY313_PLUS
error:
    Py_DECREF(constraints);
    Py_DECREF(bound);
    return NULL;
#endif
}

TypeAdapter*
TypeAdapter_Create_TypeVar(PyObject* hint)
{
    PyObject* args = get_args(hint);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    TypeAdapter* res = TypeAdapter_Create(hint,
                                          args,
                                          NULL,
                                          validator_type_var_repr,
                                          converter_type_var,
                                          Inspector_No,
                                          _JsonValidParse_TypeVar);
    Py_DECREF(args);
    return res;
}