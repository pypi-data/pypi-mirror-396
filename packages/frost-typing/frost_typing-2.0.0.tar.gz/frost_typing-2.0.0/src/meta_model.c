#include "alias_generator.h"
#include "computed_field.h"
#include "data_model.h"
#include "field.h"
#include "field_serializer.h"
#include "hash_table.h"
#include "json_schema.h"
#include "member_def.h"
#include "meta_valid_model.h"
#include "structmember.h"
#include "utils_common.h"
#include "valid_model.h"
#include "validator/field_validator.h"
#include "validator/py_typing.h"
#include "validator/validation_error.h"

static int
meta_model_set__slots__(PyObject* dict)
{
    PyObject* slots = _PyDict_GetItem_Ascii(dict, __slots__);
    if (!slots) {
        return _PyDict_SetItem_Ascii(dict, __slots__, VoidTuple);
    }

    if (PyObject_RichCompareBool(__dict__, slots, Py_EQ) ||
        PyObject_RichCompareBool(__weakref__, slots, Py_EQ)) {
        return 0;
    }

    if (!PyTuple_Check(slots)) {
        goto error;
    }

    TupleForeach(val, slots)
    {
        if (!PyObject_RichCompareBool(val, __dict__, Py_EQ) &&
            !PyObject_RichCompareBool(val, __weakref__, Py_EQ)) {
            goto error;
        }
    }
    return 0;

error:
    PyErr_SetString(PyExc_ValueError,
                    "The MetaModel supports __slots__ of the "
                    "tuple type with '__dict__' or '__weakref__'");
    return -1;
}

static inline PyObject*
get_root(PyTypeObject* self)
{
    PyObject* mro = self->tp_mro;
    for (Py_ssize_t i = 1; i < Py_SIZE(mro); i++) {
        PyObject* base = PyTuple_GET_ITEM(mro, i);
        if (Meta_IS_SUBCLASS(base)) {
            return base;
        }
    }
    return NULL;
}

static inline Field*
config_inheritance_decref(Field* self, Field* old)
{
    Field* res = Config_Inheritance(self, old);
    Py_DECREF(old);
    return res;
}

static int
set_config(MetaModel* self, PyObject* dict)
{
    Field* config = _CAST_FIELD(Py_NewRef(DefaultConfig));
    PyObject* mro = _CAST(PyTypeObject*, self)->tp_mro;
    for (Py_ssize_t i = Py_SIZE(mro) - 1; i != 0; i--) {
        PyObject* base = PyTuple_GET_ITEM(mro, i);
        if (Meta_IS_SUBCLASS(base)) {
            config =
              config_inheritance_decref(_CAST_META(base)->config, config);
            if (!config) {
                return -1;
            }
        }
    }

    Field* tmp = _CAST_FIELD(_PyDict_GetItem_Ascii(dict, __config__));
    if (tmp) {
        if (FT_UNLIKELY(!Config_Check(tmp))) {
            _RaiseInvalidType("__config__", "Config", Py_TYPE(tmp)->tp_name);
            return -1;
        }

        config = config_inheritance_decref(tmp, config);
        if (FT_UNLIKELY(!config)) {
            return -1;
        }
    }

    self->config = config;
    return 0;
}

static inline Field*
copy_config(Field* config)
{
    return Field_Create(config->flags & ~FIELD_VALUES,
                        config->def_flags & ~FIELD_VALUES);
}

static PyObject*
get_first_mro_field(PyTypeObject* self,
                    unsigned long check_flags,
                    Py_ssize_t offset)
{
    if (self->tp_base &&
        (_CAST(PyTypeObject*, self->tp_base)->tp_flags & check_flags)) {
        PyObject* obj = GET_OBJ(self->tp_base, offset);
        if (obj) {
            return Py_NewRef(obj);
        }
    }

    TupleForeach(tp, self->tp_mro)
    {
        if (FT_UNLIKELY(!(_CAST(PyTypeObject*, tp)->tp_flags & check_flags))) {
            continue;
        }

        PyObject* obj = GET_OBJ(tp, offset);
        if (obj) {
            return Py_NewRef(obj);
        }
    }
    return NULL;
}

int
_MetaModel_SetFunc(MetaModel* self,
                   PyObject* name,
                   unsigned long check_flags,
                   Py_ssize_t offset)
{
    PyObject* func =
      _PyDict_GetItem_Ascii(_CAST(PyTypeObject*, self)->tp_dict, name);
    if (func) {
        func = _PyObject_Get_Func(func, (const char*)PyUnicode_DATA(name));
        if (!func) {
            return -1;
        }
    } else {
        func = get_first_mro_field((PyTypeObject*)self, check_flags, offset);
    }

    SET_OBJ(self, offset, func);
    return 0;
}

static void
meta_model_set_call(MetaModel* self, PyObject* root)
{
    PyTypeObject* tp = (PyTypeObject*)self;
    tp->tp_flags |= Py_TPFLAGS_HAVE_VECTORCALL;

    if (root && !PyDict_Contains(tp->tp_dict, __init__) &&
        !PyDict_Contains(tp->tp_dict, __new__) &&
        _CAST(PyTypeObject*, root)->tp_vectorcall) {
        tp->tp_vectorcall = _CAST(PyTypeObject*, root)->tp_vectorcall;
        self->vec_init = _CAST_META(root)->vec_init;
    } else {
        tp->tp_vectorcall = PyType_Type.tp_vectorcall;
    }
}

static int
meta_model_set_field(MetaModel* self)
{
    PyObject* dict = _CAST(PyTypeObject*, self)->tp_dict;
    if (set_config(self, dict) < 0) {
        return -1;
    }

    if (_MetaModel_SetFunc(self,
                           __as_dict__,
                           TPFLAGS_META_SUBCLASS,
                           offsetof(MetaModel, __as_dict__)) < 0) {
        return -1;
    }
    if (_MetaModel_SetFunc(self,
                           __post_init__,
                           TPFLAGS_META_SUBCLASS,
                           offsetof(MetaModel, __post_init__)) < 0) {
        return -1;
    }
    if (_MetaModel_SetFunc(self,
                           __as_json__,
                           TPFLAGS_META_SUBCLASS,
                           offsetof(MetaModel, __as_json__)) < 0) {
        return -1;
    }
    if (_MetaModel_SetFunc(self,
                           __copy__,
                           TPFLAGS_META_SUBCLASS,
                           offsetof(MetaModel, __copy__)) < 0) {
        return -1;
    }
    return 0;
}

static inline int
meta_model_set_map(MetaModel* self)
{
    self->attr_map = HashTable_Create(self->schemas, 0);
    if (!self->attr_map) {
        return -1;
    }

    SchemaForeach(sc, self)
    {
        uint32_t flags = sc->field->flags;
        if (IS_FIELD_ALIAS(flags) || !IS_FIELD_INIT(flags)) {
            self->init_map = HashTable_Create(self->schemas, 1);
            return self->init_map ? 0 : -1;
        }
    }

    self->init_map = (HashTable*)Py_NewRef(self->attr_map);
    return 0;
}

static inline int
meta_set_member_def(MetaModel* self)
{
    Py_ssize_t offset = self->slot_offset;
    _SchemaForeach(sc, self->schemas, offset += BASE_SIZE)
    {
        PyObject* member_def = MemberDef_Create(offset);
        if (!member_def) {
            return -1;
        }

        int r = PyType_Type.tp_setattro((PyObject*)self, sc->name, member_def);
        Py_DECREF(member_def);
        if (r < 0) {
            return -1;
        }
    }
    return 0;
}

static inline PyObject*
meta_model_get_base_schema(PyTypeObject* tp)
{
    PyObject* mro = tp->tp_mro;
    PyObject* res = Py_NewRef(VoidTuple);

    for (Py_ssize_t i = Py_SIZE(mro) - 1; i > 0; i--) {
        MetaModel* base = (MetaModel*)PyTuple_GET_ITEM(mro, i);
        if (PyType_Check(base) && Meta_IS_SUBCLASS(base)) {
            PyObject* tmp = Schema_Concat(res, base->schemas);
            Py_DECREF(res);
            if (FT_UNLIKELY(!tmp)) {
                return NULL;
            }
            res = tmp;
        }
    }
    return res;
}

static int
meta_model_sub_new(MetaModel* self,
                   PyObject* annot,
                   PyObject* dict,
                   SchemaCreate schema_create)
{
    PyTypeObject* tp = (PyTypeObject*)self;
#if PY313_PLUS && !PY314_PLUS
    // Python 3.13 bug workaround:
    // In Python 3.13, __dict__ may be placed at the *end* of the type layout,
    // instead of at the beginning as in previous versions.
    // This adjustment ensures proper memory layout alignment.
    tp->tp_basicsize += BASE_SIZE * (tp->tp_dictoffset == -1);
#endif

    self->slot_offset = tp->tp_basicsize;

    PyObject* base_schemas = meta_model_get_base_schema(tp);
    if (FT_UNLIKELY(!base_schemas)) {
        return -1;
    }

    Field* default_field = copy_config(self->config);
    if (FT_UNLIKELY(!default_field)) {
        Py_DECREF(base_schemas);
        return -1;
    }

    self->schemas = Schema_CreateTuple(base_schemas,
                                       schema_create,
                                       annot,
                                       self,
                                       default_field,
                                       self->config,
                                       dict);
    Py_DECREF(default_field);
    Py_DECREF(base_schemas);
    if (FT_UNLIKELY(!self->schemas)) {
        return -1;
    }

    tp->tp_flags |= TPFLAGS_META_SUBCLASS;
    self->args_only = Schema_GetArgsCnt(self->schemas);
    tp->tp_basicsize += BASE_SIZE * Py_SIZE(self->schemas);

    if (IS_FIELD_GC(self->config->flags)) {
        tp->tp_flags |= Py_TPFLAGS_HAVE_GC;
        tp->tp_free = PyObject_GC_Del;
    } else {
        tp->tp_flags &= ~Py_TPFLAGS_HAVE_GC;
        tp->tp_free = PyObject_Free;
    }

    if (FT_UNLIKELY(meta_set_member_def(self) < 0)) {
        return -1;
    }
    return meta_model_set_map(self);
}

static PyObject*
meta_model_get_annotations(PyObject* self)
{
    PyObject *annot, *new_annot, *name, *hint;
#if PY310_PLUS
    annot = _Object_Gettr(self, __annotations__);
#else
    annot =
      _Dict_GetAscii(_CAST(PyTypeObject*, self)->tp_dict, __annotations__);
#endif

    new_annot = PyDict_New();
    if (!new_annot) {
        Py_XDECREF(annot);
        return NULL;
    }

    if (!annot) {
        annot = Py_NewRef(VoidDict);
    }

    if (!PyDict_Check(annot)) {
        _RaiseInvalidType("__annotations__", "dict", Py_TYPE(annot)->tp_name);
        goto error;
    }

    Py_ssize_t pos = 0;
    while (PyDict_Next(annot, &pos, &name, &hint)) {
        if (PyTyping_Is_Origin(hint, PyClassVar)) {
            continue;
        }

        if (PyDict_SetItem(new_annot, name, hint) < 0) {
            goto error;
        }
    }

    PyObject* dict = _CAST(PyTypeObject*, self)->tp_dict;
    pos = 0;
    while (PyDict_Next(dict, &pos, &name, &hint)) {
        if (!ComputedField_Check(hint)) {
            continue;
        }

        PyObject* annotated = ComputedField_GetAnnotated((ComputedField*)hint);
        if (!annotated) {
            goto error;
        }

        if (PyDict_SetItemDecrefVal(new_annot, name, annotated) < 0) {
            goto error;
        }
    }

    Py_DECREF(annot);
    return new_annot;

error:
    Py_DECREF(new_annot);
    Py_DECREF(annot);
    return NULL;
}

static int
check_bases(PyObject* bases)
{
    Py_ssize_t size = PyTuple_GET_SIZE(bases);
    for (Py_ssize_t i = 0; i != size; i++) {
        PyTypeObject* tp = _CAST(PyTypeObject*, PyTuple_GET_ITEM(bases, 0));
        if (PyType_Check(tp) && !Meta_IS_SUBCLASS(tp) && tp->tp_itemsize) {
            PyErr_Format(PyExc_TypeError,
                         "Not supported for subtype of '%s'",
                         tp->tp_name);
            return -1;
        }
    }
    return 0;
}

static inline PyObject*
collect_model(PyObject* bases)
{
    PyObject* res = PyList_New(0);
    TupleForeach(base, bases)
    {
        if (PyType_Check(base) && Meta_IS_SUBCLASS(base) &&
            PyList_Append(res, base) < 0) {
            Py_DECREF(res);
            return NULL;
        }
    }
    return res;
}

static Py_ssize_t
get_slots_size(MetaModel* self)
{
    return BASE_SIZE * META_GET_SIZE(self);
}

static inline void
rm_flag_and_size(PyObject* list)
{
    ListForeach(tp, list)
    {
        _CAST(PyTypeObject*, tp)->tp_flags &= ~TPFLAGS_META_SUBCLASS;
        _CAST(PyTypeObject*, tp)->tp_basicsize -=
          get_slots_size((MetaModel*)tp);
    }
}

static inline void
set_flag_and_size(PyObject* list)
{
    ListForeach(tp, list)
    {
        _CAST(PyTypeObject*, tp)->tp_flags |= TPFLAGS_META_SUBCLASS;
        _CAST(PyTypeObject*, tp)->tp_basicsize +=
          get_slots_size((MetaModel*)tp);
    }
}

MetaModel*
MetaModel_New(PyTypeObject* type,
              PyObject* args,
              PyObject* kwargs,
              SchemaCreate schema_create)
{
    MetaModel* self;
    PyObject *name, *bases, *dict, *annot, *models;

    if (!PyArg_ParseTuple(args,
                          "UO!O!:MetaModel.__new__",
                          &name,
                          &PyTuple_Type,
                          &bases,
                          &PyDict_Type,
                          &dict)) {
        return NULL;
    }

    if (FT_UNLIKELY(check_bases(bases) < 0 ||
                    meta_model_set__slots__(dict) < 0)) {
        return NULL;
    }

    models = collect_model(bases);
    if (FT_UNLIKELY(!models)) {
        return NULL;
    }

    rm_flag_and_size(models);
    self = _CAST_META(PyType_Type.tp_new(type, args, kwargs));
    set_flag_and_size(models);
    Py_DECREF(models);
    if (!self) {
        return NULL;
    }

    if (FT_UNLIKELY(meta_model_set_field(self) < 0)) {
        goto error_clear;
    }

    annot = meta_model_get_annotations((PyObject*)self);
    if (!annot) {
        goto error_clear;
    }

    int r = meta_model_sub_new(self, annot, dict, schema_create);
    Py_DECREF(annot);
    if (r < 0) {
        goto error_clear;
    }

    PyObject* root = get_root((PyTypeObject*)self);
    meta_model_set_call(self, root);
    if (FieldSerializer_CheckRegistered((PyObject*)self) < 0) {
        goto error;
    }

    return self;

error_clear:
    _FieldSerializer_Clear((PyObject*)self);
    _FieldValidator_Clear((PyObject*)self);

error:
    Py_DECREF(self);
    return NULL;
}

static PyObject*
meta_model_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    PyObject* self =
      (PyObject*)MetaModel_New(type, args, kwargs, Schema_Create);
    if (FT_UNLIKELY(PyType_IsSubtype((PyTypeObject*)self,
                                     (PyTypeObject*)&ValidModelType))) {
        Py_DECREF(self);
        PyErr_SetString(PyExc_TypeError,
                        "MetaModel cannot create instances"
                        " of ValidModel subclasses");
        return NULL;
    }
    return self;
}

int
_MetaModel_CallPostInit(PyObject* self)
{
    PyTypeObject* tp = Py_TYPE(self);
    PyObject* call = _CAST_META(tp)->__post_init__;
    if (FT_LIKELY(!call)) {
        return 0;
    }

    PyObject* res = PyObject_CallOneArg(call, self);
    if (FT_LIKELY(res)) {
        Py_DECREF(res);
        return 0;
    }

    if (MetaValid_IS_SUBCLASS(tp)) {
        ValidationError_RaiseModelType((PyObject*)tp, self);
    }
    return -1;
}

static PyObject*
meta_mode_call(PyTypeObject* cls, PyObject* args, PyObject* kwds)
{
    if (FT_UNLIKELY(!cls->tp_new)) {
        return PyErr_Format(
          PyExc_TypeError, "cannot create '%s' instances", cls->tp_name);
    }

    PyObject* self = cls->tp_new(cls, args, kwds);
    if (FT_UNLIKELY(!self || !PyObject_TypeCheck(self, cls))) {
        return self;
    }

    cls = Py_TYPE(self);
    if (FT_UNLIKELY((cls->tp_init && cls->tp_init(self, args, kwds) < 0) ||
                    _MetaModel_CallPostInit(self) < 0)) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

PyObject*
_MetaModel_Vectorcall(MetaModel* cls,
                      PyObject* const* args,
                      size_t nargsf,
                      PyObject* kwnames)
{
    PyObject* self = _DataModel_Alloc((PyTypeObject*)cls);
    if (FT_UNLIKELY(self && ((cls->vec_init &&
                              cls->vec_init(self, args, nargsf, kwnames) < 0) ||
                             _MetaModel_CallPostInit(self) < 0))) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

static int
meta_model_setattro(MetaModel* self, PyObject* name, PyObject* val)
{
    const Py_ssize_t offset = HashTable_Get(self->attr_map, name);
    if (offset < 0) {
        return PyType_Type.tp_setattro((PyObject*)self, name, val);
    }

    Schema* schema = META_GET_SCHEMA_BY_OFFSET(self, offset);
    if (IS_FIELD_FROZEN_TYPE(schema->field->flags)) {
        PyErr_Format(PyExc_AttributeError,
                     "'%.100s' type object attribute '%U' is read-only",
                     _CAST(PyTypeObject*, self)->tp_name,
                     schema->name);
        return -1;
    }

    if (val) {
        Py_XDECREF(schema->value);
        schema->value = Py_NewRef(val);
        return 0;
    }

    if (schema->value) {
        Py_DECREF(schema->value);
        schema->value = NULL;
        return 0;
    }

    PyErr_Format(PyExc_AttributeError,
                 "type object '%.100s' has no attribute '%.100U'",
                 _CAST(PyTypeObject*, self)->tp_name,
                 schema->name);
    return -1;
}

static int
meta_model_traverse(MetaModel* self, visitproc visit, void* arg)
{
    if (!(_CAST(PyTypeObject*, self)->tp_flags & Py_TPFLAGS_HEAPTYPE)) {
        return 0;
    }

    Py_VISIT(self->config);
    // No GC
    // Py_VISIT(self->schemas);
    Py_VISIT(self->__copy__);
    Py_VISIT(self->__as_dict__);
    Py_VISIT(self->__as_json__);
    Py_VISIT(self->__post_init__);
    return PyType_Type.tp_traverse((PyObject*)self, visit, arg);
}

static int
meta_model_clear(MetaModel* self)
{
    if (!(_CAST(PyTypeObject*, self)->tp_flags & Py_TPFLAGS_HEAPTYPE)) {
        return 0;
    }

    Py_CLEAR(self->init_map);
    Py_CLEAR(self->attr_map);
    Py_CLEAR(self->config);
    Py_CLEAR(self->schemas);
    Py_CLEAR(self->__copy__);
    Py_CLEAR(self->__as_dict__);
    Py_CLEAR(self->__as_json__);
    Py_CLEAR(self->__post_init__);
    return PyType_Type.tp_clear((PyObject*)self);
}

static void
meta_model_dealloc(MetaModel* self)
{
    if (!(_CAST(PyTypeObject*, self)->tp_flags & Py_TPFLAGS_HEAPTYPE)) {
        return;
    }

    PyObject_GC_UnTrack(self);
    Py_TRASHCAN_BEGIN(self, meta_model_dealloc);
    meta_model_clear(self);
    Py_TYPE(self)->tp_free(self);
    Py_TRASHCAN_END;
}

static PyMethodDef meta_model_methods[] = {
    { "json_schema", PY_METHOD_CAST(Schema_JsonSchema), METH_NOARGS, NULL },
    { NULL }
};

static PyMemberDef meta_members[] = {
    { "__config__", T_OBJECT, offsetof(MetaModel, config), READONLY, NULL },
    { "__schemas__", T_OBJECT, offsetof(MetaModel, schemas), READONLY, NULL },
    { "__post_init__",
      T_OBJECT,
      offsetof(MetaModel, __post_init__),
      READONLY,
      NULL },
    { "__as_dict__",
      T_OBJECT,
      offsetof(MetaModel, __as_dict__),
      READONLY,
      NULL },
    { "__as_json__",
      T_OBJECT,
      offsetof(MetaModel, __as_json__),
      READONLY,
      NULL },
    { "__copy__", T_OBJECT, offsetof(MetaModel, __copy__), READONLY, NULL },
    { "__slots_offset__",
      T_PYSSIZET,
      offsetof(MetaModel, slot_offset),
      READONLY,
      NULL },
    { NULL }
};

PyTypeObject MetaModelType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_TYPE_SUBCLASS |
      Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_HAVE_VECTORCALL,
    .tp_traverse = (traverseproc)meta_model_traverse,
    .tp_setattro = (setattrofunc)meta_model_setattro,
    .tp_dealloc = (destructor)meta_model_dealloc,
    .tp_call = (ternaryfunc)meta_mode_call,
    .tp_clear = (inquiry)meta_model_clear,
    .tp_name = "frost_typing.MetaModel",
    .tp_basicsize = sizeof(MetaModel),
    .tp_methods = meta_model_methods,
    .tp_free = PyObject_GC_Del,
    .tp_members = meta_members,
    .tp_new = meta_model_new,
};

int
meta_model_setup()
{
    MetaModelType.tp_base = &PyType_Type;
    Py_INCREF(&PyType_Type);
    return PyType_Ready(&MetaModelType);
}

void
meta_model_free()
{
}
