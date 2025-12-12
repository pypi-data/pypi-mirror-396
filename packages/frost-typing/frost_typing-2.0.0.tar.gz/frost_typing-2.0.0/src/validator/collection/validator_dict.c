#include "validator/validator.h"

static int
converter_dict_dict_nested(TypeAdapter* self,
                           ValidateContext* ctx,
                           PyObject* val,
                           PyObject* dict)
{
    Py_ssize_t pos = 0;
    ValidationError* err = NULL;
    PyObject *key, *item, *tmp_key, *tmp_val;

    TypeAdapter* vd_key = (TypeAdapter*)PyTuple_GET_ITEM(self->args, 0);
    TypeAdapter* vd_val = (TypeAdapter*)PyTuple_GET_ITEM(self->args, 1);
    while (PyDict_Next(val, &pos, &key, &item)) {
        tmp_key = TypeAdapter_Conversion(vd_key, ctx, key);
        if (!tmp_key) {
            if (FT_UNLIKELY(ValidationError_IndexCreate(
                              pos - 1, vd_key, key, ctx->model, &err) < 0)) {
                goto error;
            }
            continue;
        }

        tmp_val = TypeAdapter_Conversion(vd_val, ctx, item);
        if (!tmp_val) {
            Py_DECREF(tmp_key);
            if (FT_UNLIKELY(ValidationError_IndexCreate(
                              pos - 1, vd_val, item, ctx->model, &err) < 0)) {
                goto error;
            }
            continue;
        }

        int r = PyDict_SetItem(dict, tmp_key, tmp_val);
        Py_DECREF(tmp_key);
        Py_DECREF(tmp_val);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx->model);
        return -1;
    }

    return 0;

error:
    Py_XDECREF(err);
    return -1;
}

static PyObject*
converter_dict_dict(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    PyObject* res = _PyDict_NewPresized(PyDict_GET_SIZE(val));
    if (!res) {
        return NULL;
    }

    if (converter_dict_dict_nested(self, ctx, val, res) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_sequence_dict(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    PyObject* dict = PyObject_CallOneArg((PyObject*)&PyDict_Type, val);
    if (!dict) {
        PyErr_Clear();
        return NULL;
    }

    PyObject* res = converter_dict_dict(self, ctx, dict);
    Py_DECREF(dict);
    return res;
}

static PyObject*
converter_dict(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (PyDict_Check(val)) {
        return converter_dict_dict(self, ctx, val);
    }
    return converter_sequence_dict(self, ctx, val);
}

TypeAdapter*
_TypeAdapter_Create_Dict(PyObject* cls, PyObject* type_args, PyObject* tp)
{
    if (FT_UNLIKELY(
          !TypeAdapter_CollectionCheckArgs(type_args, (PyTypeObject*)cls, 2))) {
        return NULL;
    }

    PyObject* args = TypeAdapter_MapParseHintTuple(type_args, tp);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    TypeAdapter* res = _TypeAdapter_NewCollection(
      cls, args, converter_dict, _JsonValidParse_Dict);
    Py_DECREF(args);
    return res;
}
