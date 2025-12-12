#include "validator/validator.h"

static int
converter_set_set(TypeAdapter* self,
                  ValidateContext* ctx,
                  PyObject* val,
                  PyObject* res)
{
    Py_ssize_t pos = 0;
    PyObject *item, *tmp;
    ValidationError* err = NULL;
    TypeAdapter* vd = (TypeAdapter*)self->args;

    for (Py_ssize_t i = 0; _PySet_Next(val, &pos, &item); i++) {
        tmp = TypeAdapter_Conversion(vd, ctx, item);
        if (!tmp) {
            if (FT_UNLIKELY(ValidationError_IndexCreate(
                              i, vd, item, ctx->model, &err) < 0)) {
                goto error;
            }
            continue;
        }

        int r = PySet_Add(res, tmp);
        Py_DECREF(tmp);
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

static int
converter_set_array(TypeAdapter* self,
                    ValidateContext* ctx,
                    PyObject** arr,
                    Py_ssize_t size,
                    PyObject* res)
{
    ValidationError* err = NULL;
    TypeAdapter* vd = (TypeAdapter*)self->args;

    for (Py_ssize_t i = 0; i != size; i++) {
        PyObject* tmp = TypeAdapter_Conversion(vd, ctx, arr[i]);
        if (!tmp) {
            if (FT_UNLIKELY(ValidationError_IndexCreate(
                              i, vd, arr[i], ctx->model, &err) < 0)) {
                goto error;
            }
            continue;
        }

        int r = PySet_Add(res, tmp);
        Py_DECREF(tmp);
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

static int
converter_iter_set(TypeAdapter* self,
                   ValidateContext* ctx,
                   PyObject* val,
                   PyObject* res)
{
    if (!PyObject_CheckIter(val) || PyUnicode_Check(val) ||
        PyBytes_Check(val) || PyByteArray_Check(val)) {
        return -1;
    }

    PyObject *item, *tmp, *iter;
    iter = PyObject_GetIter(val);
    if (FT_UNLIKELY(!iter)) {
        return -1;
    }

    Py_ssize_t i = 0;
    ValidationError* err = NULL;
    TypeAdapter* vd = (TypeAdapter*)self->args;
    for (;; i++) {
        int r = _PyIter_GetNext(iter, &item);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
        if (!r) {
            break;
        }

        tmp = TypeAdapter_Conversion(vd, ctx, item);
        Py_DECREF(item);
        if (!tmp) {
            if (FT_UNLIKELY(ValidationError_IndexCreate(
                              i, vd, val, ctx->model, &err) < 0)) {
                goto error;
            }
            continue;
        }

        r = PySet_Add(res, tmp);
        Py_DECREF(tmp);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    Py_DECREF(iter);

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx->model);
        return -1;
    }

    return 0;

error:
    Py_XDECREF(err);
    Py_DECREF(iter);
    return -1;
}

static PyObject*
_converter_set(TypeAdapter* self,
               ValidateContext* ctx,
               PyObject* val,
               PyObject* (*set_new)(PyObject*))
{
    if (!PyObject_CheckIter(val)) {
        return NULL;
    }

    PyObject* res = set_new(NULL);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (PyList_Check(val)) {
        if (converter_set_array(
              self, ctx, LIST_ITEMS(val), PyList_GET_SIZE(val), res) < 0) {
            goto error;
        }
        return res;
    }

    if (PyList_Check(val)) {
        if (converter_set_array(
              self, ctx, LIST_ITEMS(val), PyList_GET_SIZE(val), res) < 0) {
            goto error;
        }
        return res;
    }

    if (_AnySetType_Check(Py_TYPE(val))) {
        if (converter_set_set(self, ctx, val, res) < 0) {
            goto error;
        }
        return res;
    }

    if (!converter_iter_set(self, ctx, val, res)) {
        return res;
    }

error:
    Py_DECREF(res);
    return NULL;
}

static PyObject*
converter_set(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    return _converter_set(self, ctx, val, PySet_New);
}

static PyObject*
converter_frozenset(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    return _converter_set(self, ctx, val, PyFrozenSet_New);
}

TypeAdapter*
_TypeAdapter_Create_Set(PyObject* cls, PyObject* type_args, PyObject* tp)
{
    if (!TypeAdapter_CollectionCheckArgs(type_args, (PyTypeObject*)cls, 1)) {
        return NULL;
    }

    PyObject* args = (PyObject*)ParseHint(PyTuple_GET_ITEM(type_args, 0), tp);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    TypeAdapter* res = _TypeAdapter_NewCollection(
      cls,
      args,
      cls == (PyObject*)&PySet_Type ? converter_set : converter_frozenset,
      _JsonValidParse_AnySet);
    Py_DECREF(args);
    return res;
}
