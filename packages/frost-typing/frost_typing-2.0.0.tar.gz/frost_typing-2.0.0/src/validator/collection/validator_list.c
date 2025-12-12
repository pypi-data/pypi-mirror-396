#include "validator/validator.h"

static PyObject*
converter_list_array(TypeAdapter* self,
                     ValidateContext* ctx,
                     PyObject** arr,
                     Py_ssize_t size)
{
    PyObject* res = PyList_New(size);
    if (!res) {
        return NULL;
    }

    if (_TypeAdapter_CollectionConverterArr(
          self, ctx, arr, size, LIST_ITEMS(res)) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_sequence_list(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (!PyObject_CheckIter(val) || PyUnicode_Check(val) ||
        PyBytes_Check(val) || PyByteArray_Check(val)) {
        return NULL;
    }

    PyObject* res = PySequence_List(val);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    PyObject** arr_res = LIST_ITEMS(res);
    if (_TypeAdapter_CollectionConverterArr(
          self, ctx, arr_res, PyList_GET_SIZE(res), arr_res) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_sequence_set(TypeAdapter* self, ValidateContext* ctx, PyObject* set)
{
    PyObject* res = PyList_New(PySet_GET_SIZE(set));
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (_TypeAdapter_CollectionConverterSet(self, ctx, set, LIST_ITEMS(res)) <
        0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
converter_list(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (PyDict_Check(val)) {
        return NULL;
    }
    if (PyList_Check(val)) {
        return converter_list_array(
          self, ctx, LIST_ITEMS(val), PyList_GET_SIZE(val));
    }
    if (PyTuple_Check(val)) {
        return converter_list_array(
          self, ctx, TUPLE_ITEMS(val), PyTuple_GET_SIZE(val));
    }
    if (_AnySetType_Check(Py_TYPE(val))) {
        return converter_sequence_set(self, ctx, val);
    }
    return converter_sequence_list(self, ctx, val);
}

TypeAdapter*
_TypeAdapter_Create_List(PyObject* cls, PyObject* type_args, PyObject* tp)
{
    if (!TypeAdapter_CollectionCheckArgs(type_args, (PyTypeObject*)cls, 1)) {
        return NULL;
    }

    PyObject* args = (PyObject*)ParseHint(PyTuple_GET_ITEM(type_args, 0), tp);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    TypeAdapter* res = _TypeAdapter_NewCollection(
      cls, args, converter_list, _JsonValidParse_List);
    Py_DECREF(args);
    return res;
}
