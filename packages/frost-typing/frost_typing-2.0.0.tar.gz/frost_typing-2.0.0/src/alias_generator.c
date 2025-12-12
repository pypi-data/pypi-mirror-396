#include "alias_generator.h"
#include "field.h"
#include "structmember.h"
#include "utils_common.h"

static PyObject*
alias_generator_new(PyTypeObject* cls, PyObject* args, PyObject* kw)
{
    PyObject *alias, *serialization_alias;
    alias = serialization_alias = NULL;

    char* kwlist[] = { "alias", "serialization_alias", NULL };
    if (FT_UNLIKELY(!PyArg_ParseTupleAndKeywords(args,
                                                 kw,
                                                 "|OO:AliasGenerator.__new__",
                                                 kwlist,
                                                 &alias,
                                                 &serialization_alias))) {
        return NULL;
    }

    if (alias) {
        if (FT_UNLIKELY(!PyCallable_Check(alias))) {
            return _RaiseInvalidType(
              "alias", "callable", Py_TYPE(alias)->tp_name);
        }
    }

    if (serialization_alias) {
        if (!PyCallable_Check(serialization_alias)) {
            return _RaiseInvalidType("serialization_alias",
                                     "callable",
                                     Py_TYPE(serialization_alias)->tp_name);
        }
    }

    AliasGenerator* self = (AliasGenerator*)cls->tp_alloc(cls, 0);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    self->alias = Py_XNewRef(alias);
    self->serialization_alias = Py_XNewRef(serialization_alias);
    return (PyObject*)self;
}

static void
alias_generator_dealloc(AliasGenerator* self)
{
    Py_XDECREF(self->alias);
    Py_XDECREF(self->serialization_alias);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
alias_generator_repr(AliasGenerator* self)
{
    return PyUnicode_FromFormat(
      "AliasGenerator(alias=%S, serialization_alias=%S)",
      self->alias ? self->alias : Py_None,
      self->serialization_alias ? self->serialization_alias : Py_None);
}

static PyMemberDef alias_generator_members[] = {
    { "alias", T_OBJECT, offsetof(AliasGenerator, alias), READONLY, NULL },
    { "serialization_alias",
      T_OBJECT,
      offsetof(AliasGenerator, serialization_alias),
      READONLY,
      NULL },
    { NULL }
};

PyTypeObject AliasGeneratorType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)alias_generator_dealloc,
    .tp_repr = (reprfunc)alias_generator_repr,
    .tp_name = "frost_typing.AliasGenerator",
    .tp_members = alias_generator_members,
    .tp_basicsize = sizeof(AliasGenerator),
    .tp_new = alias_generator_new,
};

static inline int
create_alias(PyObject* generator, PyObject* name, PyObject** result)
{
    if (generator) {
        *result = PyObject_CallOneArg(generator, name);
        return *result ? 0 : -1;
    }
    *result = NULL;
    return 0;
}

int
AliasGenerator_CreateAlias(AliasGenerator* self,
                           PyObject* name,
                           PyObject** alias,
                           PyObject** serialization_alias)
{
    if ((alias && create_alias(self->alias, name, alias) < 0) ||
        (serialization_alias &&
         create_alias(self->serialization_alias, name, serialization_alias) <
           0)) {
        return -1;
    }
    return 0;
}

int
alias_generator_setup(void)
{
    return PyType_Ready(&AliasGeneratorType);
}

void
alias_generator_free(void)
{
}