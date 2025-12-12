#include "computed_field.h"
#include "field.h"
#include "stddef.h"
#include "structmember.h"
#include "utils_common.h"
#include "validator/py_typing.h"

#define REQUIRED_FIELDS (FIELD_FROZEN_TYPE | _FIELD_COMPUTED_FIELD)
#define SUPPORT_FIELD_FLAGS                                                    \
    (FIELD_FROZEN | FIELD_JSON_SCHEMA_EXTRA | FIELD_REPR | FIELD_HASH |        \
     FIELD_DICT | FIELD_JSON | _FIELD_COMPUTED_FIELD | FIELD_EXAMPLES |        \
     FIELD_TITLE | FIELD_SERIALIZATION_ALIAS | FIELD_AUTO_ALIAS)

#define DEFAUL_FIELD                                                           \
    (FIELD_FROZEN | FIELD_REPR | FIELD_DICT | FIELD_JSON | FIELD_COMPARISON |  \
     FIELD_AUTO_ALIAS | FIELD_FROZEN_TYPE)

static Field* default_field;

static void
computed_field_dealloc(ComputedField* self)
{
    Py_XDECREF(self->field);
    Py_XDECREF(self->callable);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
computed_field_proxy_call(ComputedField* self,
                          PyObject* const* args,
                          size_t nargsf,
                          PyObject* kwnames)
{
    return PyObject_Vectorcall(self->callable, args, nargsf, kwnames);
}

static PyObject*
computed_field_set_func(ComputedField* self,
                        PyObject* const* args,
                        size_t nargs,
                        PyObject* kwn)
{
    self->callable = _VectorCall_GetCallable("__callable", args, nargs, kwn);
    if (FT_UNLIKELY(!self->callable)) {
        return NULL;
    }

    Py_INCREF(self->callable);
    self->vectorcall = (vectorcallfunc)computed_field_proxy_call;
    return Py_NewRef(self);
}

static PyObject*
computed_field_new(PyTypeObject* cls, PyObject* args, PyObject* kw)
{
    PyObject *callable = NULL, *cache = Py_True;
    Field* field = NULL;

    char* kwlist[] = { "__callable", "field", "cache", NULL };
    if (FT_UNLIKELY(
          !PyArg_ParseTupleAndKeywords(args,
                                       kw,
                                       "|O$O!O!:computed_field.__new__",
                                       kwlist,
                                       &callable,
                                       &FieldType,
                                       &field,
                                       &PyBool_Type,
                                       &cache))) {
        return NULL;
    }

    if (callable && !PyCallable_Check(callable)) {
        return _RaiseInvalidType(
          "__callable", "Callable", Py_TYPE(callable)->tp_name);
    }

    if (field) {
        field = Field_Inheritance(field, default_field);
        if (FT_UNLIKELY(!field)) {
            return NULL;
        }
    } else {
        field = (Field*)Py_NewRef(default_field);
    }

    ComputedField* self = (ComputedField*)cls->tp_alloc(cls, 0);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    if (callable) {
        self->callable = Py_NewRef(callable);
        self->vectorcall = (vectorcallfunc)computed_field_proxy_call;
    } else {
        self->vectorcall = (vectorcallfunc)computed_field_set_func;
    }

    self->field = field;
    self->cache = cache == Py_True;
    return (PyObject*)self;
}

static PyObject*
computed_field_repr(ComputedField* self)
{
    if (self->callable) {
        return PyObject_Repr(self->callable);
    }
    return PyUnicode_FromFormat("computed_field(field=%R, cache=%R)",
                                self->field,
                                self->cache ? Py_True : Py_False);
}

static PyMemberDef computed_field_members[] = {
    { "__func__", T_OBJECT, offsetof(ComputedField, callable), READONLY, NULL },
    { "field", T_OBJECT, offsetof(ComputedField, field), READONLY, NULL },
    { "cache", T_BOOL, offsetof(ComputedField, cache), READONLY, NULL },
    { NULL }
};

PyTypeObject ComputedFieldType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL,
    .tp_vectorcall_offset = offsetof(ComputedField, vectorcall),
    .tp_dealloc = (destructor)computed_field_dealloc,
    .tp_repr = (reprfunc)computed_field_repr,
    .tp_name = "frost_typing.computed_field",
    .tp_basicsize = sizeof(ComputedField),
    .tp_members = computed_field_members,
    .tp_call = PyVectorcall_Call,
    .tp_new = computed_field_new,
};

int
computed_field_setup(void)
{
    default_field = Field_Create(DEFAUL_FIELD, FIELD_FULL & ~FIELD_VALUES);
    if (FT_UNLIKELY(!default_field)) {
        return -1;
    }
    return PyType_Ready(&ComputedFieldType);
}

void
computed_field_free(void)
{
    Py_DECREF(default_field);
}

static inline PyObject*
computed_field_get_return_type(ComputedField* self)
{
    PyObject* res;
    int r = _PyObject_Get_ReturnHinst(self->callable, &res);
    if (FT_UNLIKELY(r < 0)) {
        return NULL;
    } else if (FT_UNLIKELY(!r)) {
        return Py_NewRef(PyAny);
    }
    return res;
}

PyObject*
ComputedField_GetAnnotated(ComputedField* self)
{
    if (FT_UNLIKELY(!self->callable)) {
        PyErr_SetString(PyExc_ValueError,
                        "There is no function for computed_field");
        return NULL;
    }

    PyObject* type = computed_field_get_return_type(self);
    uint32_t falgs = self->field->flags & SUPPORT_FIELD_FLAGS;
    Field* new_field = _Field_CreateComputed(
      (falgs | REQUIRED_FIELDS), self->field, (PyObject*)self);
    if (FT_UNLIKELY(!new_field)) {
        Py_DECREF(type);
        return NULL;
    }

    PyObject* key = PyTuple_Pack(2, type, new_field);
    Py_DECREF(new_field);
    Py_DECREF(type);
    if (FT_UNLIKELY(!key)) {
        return NULL;
    }

    PyObject* res = PyObject_GetItem(PyAnnotated, key);
    Py_DECREF(key);
    return res;
}
