#include "field_serializer.h"
#include "convector.h"
#include "field.h"
#include "meta_model.h"
#include "stddef.h"
#include "utils_common.h"

static PyObject* registered_field_serializer;

static int
registration_field_serializer(FieldSerializer* self, PyObject* type)
{
    // The object has not been initialized yet, flag comparison is not available
    if (FT_UNLIKELY(
          !PyType_IsSubtype(Py_TYPE(type), (PyTypeObject*)&MetaModelType))) {
        _RaiseInvalidType(
          "owner", "subtype of the DataModel", Py_TYPE(type)->tp_name);
        return -1;
    }

    if (FT_UNLIKELY(Meta_IS_SUBCLASS(type))) {
        PyErr_SetString(PyExc_TypeError,
                        "Cannot register after type is created");
        return -1;
    }

    PyObject* dict = Dict_GetItemNoError(registered_field_serializer, type);
    if (!dict) {
        dict = PyDict_New();
        if (FT_UNLIKELY(!dict)) {
            return -1;
        }
        if (FT_UNLIKELY(PyDict_SetItemDecrefVal(
                          registered_field_serializer, type, dict) < 0)) {
            return -1;
        }
    }

    TupleForeach(name, self->fields_name)
    {
        if (FT_UNLIKELY(PyDict_SetItem(dict, name, self->func) < 0)) {
            PyDict_DelItem(registered_field_serializer, type);
            return -1;
        }
    }
    return 0;
}

static void
field_serializer_dealloc(FieldSerializer* self)
{
    Py_XDECREF(self->func);
    Py_DECREF(self->fields_name);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
field_serializer_proxy_call(FieldSerializer* self,
                            PyObject* const* args,
                            size_t nargsf,
                            PyObject* kwnames)
{
    return PyObject_Vectorcall(self->func, args, nargsf, kwnames);
}

static PyObject*
field_serializer_set_func(FieldSerializer* self,
                          PyObject* const* args,
                          size_t nargs,
                          PyObject* kwn)
{
    self->func = _VectorCall_GetFuncArg("field_serializer", args, nargs, kwn);
    if (FT_UNLIKELY(!self->func)) {
        return NULL;
    }
    self->vectorcall = (vectorcallfunc)field_serializer_proxy_call;
    return Py_NewRef(self);
}

static PyObject*
field_serializer_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    FieldSerializer* self;
    Py_ssize_t args_size = PyTuple_GET_SIZE(args);

    if (!_PyArg_NoKeywords(type->tp_name, kwargs)) {
        return NULL;
    }

    if (args_size == 0) {
        return PyErr_Format(PyExc_TypeError,
                            "%.100s() missing 1 required "
                            "positional argument: 'field'",
                            type->tp_name);
    }

    for (Py_ssize_t i = 0; i < args_size; i++) {
        PyObject* field = PyTuple_GET_ITEM(args, i);
        if (!PyUnicode_Check(field)) {
            return PyErr_Format(PyExc_TypeError,
                                "Argument %zu must be string, not '%.100s'",
                                i,
                                Py_TYPE(field)->tp_name);
        }
    }

    self = (FieldSerializer*)type->tp_alloc(type, 0);
    if (self) {
        self->fields_name = Py_NewRef(args);
        self->vectorcall = (vectorcallfunc)field_serializer_set_func;
    }
    return (PyObject*)self;
}

static PyObject*
field_serializer_set_name(FieldSerializer* self,
                          PyObject* const* args,
                          Py_ssize_t nargs)
{
    Py_ssize_t cnt = PyVectorcall_NARGS(nargs);
    if (!PyCheck_ArgsCnt("__set_name__", cnt, 2)) {
        return NULL;
    }

    PyObject* owner = (PyObject*)args[0];
    if (registration_field_serializer(self, owner) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyObject*
field_serializer_get(FieldSerializer* self, PyObject* instance, PyObject* owner)
{
    return Py_TYPE(self->func)->tp_descr_get(self->func, instance, owner);
}

static PyMethodDef field_serializer_methods[] = {
    { "__set_name__",
      PY_METHOD_CAST(field_serializer_set_name),
      METH_FASTCALL,
      NULL },
    { NULL }
};

PyTypeObject FieldSerializerType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_dealloc =
      (destructor)field_serializer_dealloc,
    .tp_vectorcall_offset = offsetof(FieldSerializer, vectorcall),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL,
    .tp_descr_get = (descrgetfunc)field_serializer_get,
    .tp_name = "frost_typing.field_serializer",
    .tp_basicsize = sizeof(FieldSerializer),
    .tp_methods = field_serializer_methods,
    .tp_new = field_serializer_new,
    .tp_call = PyVectorcall_Call,
};

int
field_serializer_setup(void)
{
    registered_field_serializer = PyDict_New();
    if (FT_UNLIKELY(!registered_field_serializer)) {
        return -1;
    }
    return PyType_Ready(&FieldSerializerType);
}

void
field_serializer_free(void)
{
    Py_DECREF(registered_field_serializer);
}

int
FieldSerializer_CheckRegistered(PyObject* type)
{
    PyObject* dict = Dict_GetItemNoError(registered_field_serializer, type);
    if (!dict) {
        return 0;
    }

    if (!PyDict_GET_SIZE(dict)) {
        PyDict_DelItem(registered_field_serializer, type);
        return 1;
    }

    PyObject* join = PyUnicode_Join(__sep_and__, dict);
    PyDict_DelItem(registered_field_serializer, type);
    if (!FT_UNLIKELY(join)) {
        return -1;
    }

    PyErr_Format(
      PyExc_ValueError, "Decorator refers to unknown field(s): '%U'", join);
    Py_DECREF(join);
    return -1;
}

PyObject*
FieldSerializer_RegisteredPop(PyObject* type, PyObject* name)
{
    PyObject* dict = Dict_GetItemNoError(registered_field_serializer, type);
    if (!dict) {
        return NULL;
    }

    PyObject* res = Dict_GetItemNoError(dict, name);
    if (!res) {
        return NULL;
    }

    Py_INCREF(res);
    PyDict_DelItem(dict, name);
    if (!PyDict_GET_SIZE(dict)) {
        PyDict_DelItem(registered_field_serializer, type);
    }
    return res;
}

void
_FieldSerializer_Clear(PyObject* tp)
{
    if (PyDict_Contains(registered_field_serializer, tp)) {
        PyDict_DelItem(registered_field_serializer, tp);
    }
}

PyObject*
_FieldSerializer_Call(Field* self,
                      PyObject* this,
                      PyObject* val,
                      ConvParams* params)
{
    PyObject* func = Field_GET_SERIALIZER(self);
    if (FT_LIKELY(_FUNC_GET_ACNT(func) == 2)) {
        return PyObject_CallTwoArg(func, this, val);
    }

    PyObject* info = _ConvParams_GetSerializationInfo(params);
    if (FT_UNLIKELY(!info)) {
        return NULL;
    }

    return PyObject_CallThreeArg(func, this, val, info);
}