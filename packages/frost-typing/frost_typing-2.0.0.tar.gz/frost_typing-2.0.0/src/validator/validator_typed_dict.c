#include "validator/validator.h"

static int
converter_dict(PyObject* valid_dict,
               ValidateContext* ctx,
               PyObject* dict,
               PyObject* val,
               ValidationError** err,
               int optional)
{
    TypeAdapter* vd;
    PyObject* name;
    Py_ssize_t pos = 0;

    while (PyDict_Next(valid_dict, &pos, &name, (PyObject**)&vd)) {
        PyObject* item = _PyDict_GetItem_Ascii(val, name);
        if (!item) {
            if (optional) {
                continue;
            }
            if (FT_UNLIKELY(ValidationError_CreateMissing(
                              name, val, ctx->model, err) < 0)) {
                return -1;
            }
            continue;
        }

        PyObject* tmp = TypeAdapter_Conversion(vd, ctx, item);
        if (!tmp) {
            if (FT_UNLIKELY(ValidationError_Create(
                              name, vd, item, ctx->model, err) < 0)) {
                return -1;
            }
            continue;
        }

        int r = _PyDict_SetItem_Ascii(dict, name, tmp);
        Py_DECREF(tmp);
        if (FT_UNLIKELY(r < 0)) {
            return -1;
        }
    }
    return 0;
}

static PyObject*
converter_typed_dict(TypeAdapter* self, ValidateContext* ctx, PyObject* val);

static PyObject*
converter_typed_dict_iter(TypeAdapter* self,
                          ValidateContext* ctx,
                          PyObject* val)
{
    if (!PyObject_CheckIter(val)) {
        return NULL;
    }

    val = PyObject_CallOneArg((PyObject*)&PyDict_Type, val);
    if (!val) {
        PyErr_Clear();
        return NULL;
    }

    PyObject* res = converter_typed_dict(self, ctx, val);
    Py_DECREF(val);
    return res;
}

static PyObject*
converter_typed_dict(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (!PyDict_Check(val)) {
        return converter_typed_dict_iter(self, ctx, val);
    }

    PyObject* res = PyDict_New();
    if (!res) {
        return NULL;
    }

    ValidationError* err = NULL;
    PyObject* required_keys = PyTuple_GET_ITEM(self->args, 0);
    if (converter_dict(required_keys, ctx, res, val, &err, 0) < 0) {
        Py_XDECREF(err);
        Py_DECREF(res);
        return NULL;
    }

    PyObject* optional_keys = PyTuple_GET_ITEM(self->args, 1);
    if (converter_dict(optional_keys, ctx, res, val, &err, 1) < 0) {
        Py_XDECREF(err);
        Py_DECREF(res);
        return NULL;
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx->model);
        Py_DECREF(res);
        return NULL;
    }

    return res;
}

static int
parse_keys(PyObject* dict,
           PyObject* tp,
           PyObject* annot,
           PyObject* set,
           char* err,
           int include)
{
    Py_ssize_t pos = 0;
    PyObject *name, *hint;
    while (PyDict_Next(annot, &pos, &name, &hint)) {
        if (!PyUnicode_Check(name)) {
            PyErr_Format(
              PyExc_TypeError,
              "TypedDict item '%.100s' must be str, received '%.100s'",
              err,
              Py_TYPE(name)->tp_name);
            return -1;
        }

        int r = PySet_Contains(set, name);
        if (r < 0) {
            return -1;
        }

        if ((include && !r) || (!include && r)) {
            continue;
        }

        TypeAdapter* vd = ParseHint(hint, tp);
        if (!vd) {
            return -1;
        }
        if (_PyDict_SetItemAsciiDecrefVal(dict, name, (PyObject*)vd) < 0) {
            return -1;
        }
    }

    return 0;
}

static inline TypeAdapter*
type_adapter_create_typed_dict(PyObject* tp, PyObject* annot, PyObject* r_keys)
{
    PyObject *required_keys, *optional_keys;

    required_keys = PyDict_New();
    if (!required_keys) {
        return NULL;
    }

    if (parse_keys(required_keys, tp, annot, r_keys, "__required_keys__", 1) <
        0) {
        Py_DECREF(required_keys);
        return NULL;
    }

    optional_keys = PyDict_New();
    if (!optional_keys) {
        Py_DECREF(required_keys);
        return NULL;
    }

    if (parse_keys(optional_keys, tp, annot, r_keys, "__optional_keys__", 0) <
        0) {
        Py_DECREF(optional_keys);
        Py_DECREF(required_keys);
        return NULL;
    }

    PyObject* args = PyTuple_Pack(2, required_keys, optional_keys);
    Py_DECREF(optional_keys);
    Py_DECREF(required_keys);
    if (args == NULL) {
        return NULL;
    }

    TypeAdapter* res = TypeAdapter_Create((PyObject*)&PyDict_Type,
                                          args,
                                          NULL,
                                          TypeAdapter_Base_Repr,
                                          converter_typed_dict,
                                          Inspector_No,
                                          NULL);
    Py_DECREF(args);
    return res;
}

TypeAdapter*
TypeAdapter_Create_TypedDict(PyObject* hint, PyObject* tp)
{
    PyObject* annot = PyTypedDict_Getannotations(hint);
    if (!annot) {
        return NULL;
    }

    PyObject* r_keys = PyTyping_Get_RequiredKeys(hint);
    if (!r_keys) {
        Py_DECREF(annot);
        return NULL;
    }

    TypeAdapter* res = type_adapter_create_typed_dict(tp, annot, r_keys);
    Py_DECREF(annot);
    Py_DECREF(r_keys);
    return res;
}