#include "validator/validator.h"

static PyObject*
validator_union_type_repr(TypeAdapter* self)
{
    return PyUnicode_FromFormat(
      "Type[%s]", _CAST(PyTypeObject*, self->cls)->tp_name, NULL);
}

TypeAdapter*
TypeAdapter_Create_UnionType(PyObject* hint, PyObject* tp)
{
    PyObject* type_args = PyTyping_Get_Args(hint);
    if (FT_UNLIKELY(!type_args)) {
        return NULL;
    }

    if (!TypeAdapter_CollectionCheckArgs(type_args, &PyType_Type, 1)) {
        Py_DECREF(type_args);
        return NULL;
    }

    PyObject* cls =
      PyEvaluateIfNeeded(PyTuple_GET_ITEM(type_args, 0), (PyTypeObject*)tp);
    if (!cls) {
        Py_DECREF(type_args);
        return NULL;
    }

    if (PyType_Check(cls)) {
        TypeAdapter* res = TypeAdapter_Create(cls,
                                              NULL,
                                              NULL,
                                              validator_union_type_repr,
                                              Not_Converter,
                                              Inspector_IsSubclass,
                                              NULL);
        Py_DECREF(type_args);
        Py_DECREF(cls);
        return res;
    }

    _RaiseInvalidType("Type[...]", "type", Py_TYPE(cls)->tp_name);
    Py_DECREF(cls);
    Py_DECREF(type_args);
    return NULL;
}