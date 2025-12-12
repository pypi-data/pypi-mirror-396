#include "validator/discriminator.h"
#include "structmember.h"
#include "validator/validator.h"

static void
discriminator_dealloc(Discriminator* self)
{
    Py_XDECREF(self->discriminator);
    Py_XDECREF(self->mapping);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
discriminator_repr(Discriminator* self)
{
    return PyUnicode_FromFormat("%s(discriminator=%S, mapping=%S)",
                                Py_TYPE(self)->tp_name,
                                self->discriminator,
                                self->mapping);
}

static PyObject*
discriminator_new(PyTypeObject* cls, PyObject* args, PyObject* kwargs)
{
    PyObject *discriminator, *mapping, *raise_on_missing = Py_False;
    char* kwlist[] = { "discriminator", "mapping", "raise_on_missing", NULL };
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "UO!|O!:Discriminator.__new__",
                                     kwlist,
                                     &discriminator,
                                     &PyDict_Type,
                                     &mapping,
                                     &PyBool_Type,
                                     &raise_on_missing)) {
        return NULL;
    }
    if (!CheckValidityOfAttribute(discriminator)) {
        return NULL;
    }

    Discriminator* self = (Discriminator*)cls->tp_alloc(cls, 0);
    if (FT_LIKELY(self)) {
        _Hash_String(discriminator);
        self->raise_on_missing = Py_NewRef(raise_on_missing);
        self->discriminator = Py_NewRef(discriminator);
        self->mapping = Py_NewRef(mapping);
    }
    return (PyObject*)self;
}

static PyMemberDef discriminator_members[] = {
    { "raise_on_missing",
      T_OBJECT,
      offsetof(Discriminator, raise_on_missing),
      READONLY,
      NULL },
    { "discriminator",
      T_OBJECT,
      offsetof(Discriminator, discriminator),
      READONLY,
      NULL },
    { "mapping", T_OBJECT, offsetof(Discriminator, mapping), READONLY, NULL },
    { NULL }
};

PyTypeObject DiscriminatorType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)discriminator_dealloc,
    .tp_name = "frost_typing.Discriminator",
    .tp_repr = (reprfunc)discriminator_repr,
    .tp_basicsize = sizeof(Discriminator),
    .tp_members = discriminator_members,
    .tp_new = discriminator_new,
};

static PyObject*
discriminator_parse_mapping(PyObject* mapping, PyObject* tp)
{
    PyObject* res = PyDict_New();
    if (!res) {
        return NULL;
    }

    Py_ssize_t pos = 0;
    PyObject *key, *val;
    while (PyDict_Next(mapping, &pos, &key, &val)) {
        TypeAdapter* vd = ParseHint(val, tp);
        if (!vd || PyDict_SetItemDecrefVal(res, key, (PyObject*)vd) < 0) {
            goto error;
        }
    }

    return res;
error:
    Py_DECREF(res);
    return NULL;
}

static PyObject*
discriminator_converter(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    int raise_on_missing = PyTuple_GET_ITEM(self->args, 2) == Py_True;
    PyObject* name = PyTuple_GET_ITEM(self->args, 0);
    PyObject* type = _Object_Gettr(ctx->data, name);
    if (type == _PySet_Dummy) {
        Py_DECREF(type);
        type = NULL;
    }

    if (!type) {
        return raise_on_missing
                 ? NULL
                 : TypeAdapter_Conversion((TypeAdapter*)self->cls, ctx, val);
    }

    PyObject* mapping = PyTuple_GET_ITEM(self->args, 1);
    TypeAdapter* vd = (TypeAdapter*)PyDict_GetItemWithError(mapping, type);
    Py_DECREF(type);
    if (!vd) {
        if (raise_on_missing) {
            return NULL;
        }
        PyErr_Clear();
        vd = (TypeAdapter*)self->cls;
    }

    PyObject* res = TypeAdapter_Conversion(vd, ctx, val);
    if (!res) {
        ValidationError_Raise(NULL, vd, val, ctx->model);
    }
    return res;
}

TypeAdapter*
TypeAdapter_Create_Discriminator(TypeAdapter* validator,
                                 Discriminator* discriminator,
                                 PyObject* tp)
{
    if (validator->inspector != Inspector_IsInstanceTypeAdapter) {
        Py_INCREF(validator);
        return validator;
    }

    PyObject* mapping = discriminator_parse_mapping(discriminator->mapping, tp);
    if (FT_UNLIKELY(!mapping)) {
        return NULL;
    }

    PyObject* args = PyTuple_Pack(3,
                                  discriminator->discriminator,
                                  mapping,
                                  discriminator->raise_on_missing);
    Py_DECREF(mapping);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    TypeAdapter* res = TypeAdapter_Create((PyObject*)validator,
                                          args,
                                          NULL,
                                          TypeAdapter_Base_Repr,
                                          discriminator_converter,
                                          Inspector_No,
                                          NULL);
    Py_DECREF(args);
    return res;
}

int
_TypeAdapter_СontainsDiscriminator(TypeAdapter* self)
{
    if (self->conv == discriminator_converter) {
        return 1;
    }

    if (TypeAdapter_Check(self->cls)) {
        if (_TypeAdapter_СontainsDiscriminator((TypeAdapter*)(self->cls))) {
            return 1;
        }
    }

    if (!self->args) {
        return 0;
    }

    if (TypeAdapter_Check(self->args)) {
        return _TypeAdapter_СontainsDiscriminator((TypeAdapter*)(self->args));
    } else if (!PyTuple_Check(self->args)) {
        return 0;
    }

    TupleForeach(arg, self->args)
    {
        if (arg && TypeAdapter_Check(self->cls)) {
            if (_TypeAdapter_СontainsDiscriminator((TypeAdapter*)arg)) {
                return 1;
            }
        }
    }
    return 0;
}

int
discriminator_setup(void)
{
    return PyType_Ready(&DiscriminatorType);
}

void
discriminator_free(void)
{
}