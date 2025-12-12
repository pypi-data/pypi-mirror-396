#include "validator/validator.h"

static PyObject* __incorrect_size;

static PyObject*
converter_tuple_arr(TypeAdapter* self,
                    ValidateContext* ctx,
                    PyObject** arr,
                    Py_ssize_t size)
{
    PyObject* res = PyTuple_New(size);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (_TypeAdapter_CollectionConverterArr(
          self, ctx, arr, size, TUPLE_ITEMS(res)) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_sequence_tuple(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (!PyObject_CheckIter(val) || PyUnicode_Check(val) ||
        PyBytes_Check(val) || PyByteArray_Check(val)) {
        return NULL;
    }

    PyObject* res = PySequence_Tuple(val);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    PyObject** arr = TUPLE_ITEMS(res);
    if (_TypeAdapter_CollectionConverterArr(
          self, ctx, arr, PyTuple_GET_SIZE(res), arr) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_sequence_set(TypeAdapter* self, ValidateContext* ctx, PyObject* set)
{
    PyObject* res = PyTuple_New(PySet_GET_SIZE(set));
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (_TypeAdapter_CollectionConverterSet(self, ctx, set, TUPLE_ITEMS(res)) <
        0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static int
check_size(TypeAdapter* self,
           ValidateContext* ctx,
           PyObject* val,
           Py_ssize_t length)
{
    Py_ssize_t size = PyTuple_GET_SIZE(self->args);
    if (length == size) {
        return 1;
    }
    ValidationError_RaiseFormat(
      "Tuple should have %zu items after validation, not %zu",
      NULL,
      __incorrect_size,
      val,
      ctx->model,
      size,
      length);
    return 0;
}

static int
converter_tuple_array_fix_size_nested(TypeAdapter* self,
                                      ValidateContext* ctx,
                                      PyObject* val,
                                      PyObject** arr,
                                      PyObject** res_arr)
{
    TypeAdapter* vd;
    ValidationError* err = NULL;
    Py_ssize_t size = PyTuple_GET_SIZE(self->args);
    for (Py_ssize_t i = 0; i != size; i++) {
        vd = (TypeAdapter*)PyTuple_GET_ITEM(self->args, i);
        Py_XDECREF(res_arr[i]);
        res_arr[i] = TypeAdapter_Conversion(vd, ctx, arr[i]);
        if (res_arr[i]) {
            continue;
        }

        if (FT_UNLIKELY(
              ValidationError_IndexCreate(i, vd, val, ctx->model, &err) < 0)) {
            Py_XDECREF(err);
            return -1;
        }
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx->model);
        return -1;
    }
    return 0;
}

static PyObject*
converter_tuple_array_fix_size(TypeAdapter* self,
                               ValidateContext* ctx,
                               PyObject* val,
                               PyObject** arr)
{
    PyObject* res = PyTuple_New(PyTuple_GET_SIZE(self->args));
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    PyObject** res_arr = TUPLE_ITEMS(res);
    if (converter_tuple_array_fix_size_nested(self, ctx, val, arr, res_arr) <
        0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_sequence_tuple_fix_size(TypeAdapter* self,
                                  ValidateContext* ctx,
                                  PyObject* val)
{
    if (!PyObject_CheckIter(val) || PyUnicode_Check(val) ||
        PyBytes_Check(val) || PyByteArray_Check(val)) {
        return NULL;
    }

    PyObject* res = PySequence_Tuple(val);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (!check_size(self, ctx, val, PyTuple_GET_SIZE(res))) {
        Py_DECREF(res);
        return NULL;
    }

    PyObject** arr = TUPLE_ITEMS(res);
    if (converter_tuple_array_fix_size_nested(self, ctx, val, arr, arr) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_tuple(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (PyList_Check(val)) {
        return converter_tuple_arr(
          self, ctx, LIST_ITEMS(val), PyList_GET_SIZE(val));
    }
    if (PyTuple_Check(val)) {
        return converter_tuple_arr(
          self, ctx, TUPLE_ITEMS(val), PyTuple_GET_SIZE(val));
    }
    if (_AnySetType_Check(Py_TYPE(val))) {
        return converter_sequence_set(self, ctx, val);
    }
    if (PyDict_Check(val)) {
        return NULL;
    }
    return converter_sequence_tuple(self, ctx, val);
}

static PyObject*
converter_tuple_fix_size(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (PyList_Check(val)) {
        if (!check_size(self, ctx, val, PyList_GET_SIZE(val))) {
            return NULL;
        }
        return converter_tuple_array_fix_size(self, ctx, val, LIST_ITEMS(val));
    }
    if (PyTuple_Check(val)) {
        if (!check_size(self, ctx, val, PyTuple_GET_SIZE(val))) {
            return NULL;
        }
        return converter_tuple_array_fix_size(self, ctx, val, TUPLE_ITEMS(val));
    }
    if (PyDict_Check(val)) {
        return NULL;
    }
    return converter_sequence_tuple_fix_size(self, ctx, val);
}

TypeAdapter*
_TypeAdapter_Create_Tuple(PyObject* cls, PyObject* type_args, PyObject* tp)
{
    PyObject* args;
    TypeAdapter* res;

    if (PyTuple_GET_SIZE(type_args) == 2) {
        if (PyTuple_GET_ITEM(type_args, 1) == Py_Ellipsis) {
            args = (PyObject*)ParseHint(PyTuple_GET_ITEM(type_args, 0), tp);
            if (!args) {
                return NULL;
            }
            res = _TypeAdapter_NewCollection(
              cls, args, converter_tuple, _JsonValidParse_Tuple);
            Py_DECREF(args);
            return res;
        }
    }

    args = TypeAdapter_MapParseHintTuple(type_args, tp);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    res = _TypeAdapter_NewCollection(
      cls, args, converter_tuple_fix_size, _JsonValidParse_TupleFixSize);
    Py_DECREF(args);
    return res;
}

int
validator_tuple_setup(void)
{
    CREATE_VAR_INTERN___STING(incorrect_size);
    return 0;
}

void
validator_tuple_free(void)
{
    Py_DECREF(__incorrect_size);
}