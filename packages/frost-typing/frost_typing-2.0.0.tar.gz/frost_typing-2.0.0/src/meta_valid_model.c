#include "meta_valid_model.h"
#include "field.h"
#include "stddef.h"
#include "structmember.h"
#include "valid_model.h"
#include "validator/validator.h"

static int
meta_model_set_field(MetaValidModel* self)
{
    PyObject* par = PyObject_GetAttrString((PyObject*)self, "__parameters__");
    if (par) {
        if (!PyTuple_Check(par)) {
            _RaiseInvalidType("__parameters__", "tuple", Py_TYPE(par)->tp_name);
            Py_DECREF(par);
            return -1;
        }

        if (!PyTuple_GET_SIZE(par)) {
            Py_CLEAR(par);
        }
    } else {
        PyErr_Clear();
    }

    self->gtypes = par;
    self->ctx = _ContextManager_New(
      (PyObject*)self, _ValidModel_CtxCall, _ValidModel_CtxFromJson);
    if (!self->ctx) {
        return -1;
    }
    return _MetaModel_SetFunc((MetaModel*)self,
                              __frost_validate__,
                              TPFLAGS_META_VALID_SUBCLASS,
                              offsetof(MetaValidModel, __frost_validate__));
}

static PyObject*
meta_valid_model_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    MetaModel* self =
      MetaModel_New(type, args, kwargs, (SchemaCreate)ValidSchema_Create);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyType_IsSubtype((PyTypeObject*)self,
                                      (PyTypeObject*)&ValidModelType))) {
        PyErr_SetString(PyExc_TypeError,
                        "MetaValidModel can only instantiate"
                        " ValidModel subclasses");
        goto error;
    }

    _CAST(PyTypeObject*, self)->tp_flags |= TPFLAGS_META_VALID_SUBCLASS;
    if (FT_UNLIKELY(meta_model_set_field((MetaValidModel*)self) < 0 ||
                    FieldValidator_CheckRegistered((PyObject*)self) < 0)) {
        goto error;
    }

    return (PyObject*)self;

error:
    Py_DECREF(self);
    return NULL;
}

static int
meta_valid_model_traverse(MetaValidModel* self, visitproc visit, void* arg)
{
    Py_VISIT(self->ctx);
    // Py_VISIT(self->gtypes); No GC
    Py_VISIT(self->__frost_validate__);
    return MetaModelType.tp_traverse((PyObject*)self, visit, arg);
}

static int
meta_valid_model_clear(MetaValidModel* self)
{
    if (!(_CAST(PyTypeObject*, self)->tp_flags & Py_TPFLAGS_HEAPTYPE)) {
        return 0;
    }

    Py_CLEAR(self->ctx);
    Py_CLEAR(self->gtypes);
    Py_CLEAR(self->__frost_validate__);
    return MetaModelType.tp_clear((PyObject*)self);
}

static PyObject*
valid_model_subscript(MetaValidModel* cls, PyObject* key)
{
    return _ContextManager_CreateGetItem((PyObject*)cls,
                                         cls->gtypes,
                                         key,
                                         _ValidModel_CtxCall,
                                         _ValidModel_CtxFromJson);
}

static PyMemberDef meta_valid_members[] = {
    { "__context__", T_OBJECT, offsetof(MetaValidModel, ctx), READONLY, NULL },
    { NULL },
};

PyMappingMethods meta_valid_model_as_mapping = {
    .mp_subscript = (binaryfunc)valid_model_subscript
};

PyTypeObject MetaValidModelType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_TYPE_SUBCLASS |
      Py_TPFLAGS_HAVE_GC,
    .tp_traverse = (traverseproc)meta_valid_model_traverse,
    .tp_as_mapping = &meta_valid_model_as_mapping,
    .tp_clear = (inquiry)meta_valid_model_clear,
    .tp_name = "frost_typing.MetaValidModel",
    .tp_basicsize = sizeof(MetaValidModel),
    .tp_members = meta_valid_members,
    .tp_new = meta_valid_model_new,
    .tp_dealloc = _Object_Dealloc,
    .tp_free = PyObject_GC_Del,
};

void
meta_valid_model_free()
{
}

int
meta_valid_model_setup()
{
    MetaValidModelType.tp_base = &MetaModelType;
    return PyType_Ready(&MetaValidModelType);
}
