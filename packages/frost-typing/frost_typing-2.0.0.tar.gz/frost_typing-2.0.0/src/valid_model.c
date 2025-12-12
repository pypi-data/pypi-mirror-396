#include "valid_model.h"
#include "convector.h"
#include "data_model.h"
#include "diff.h"
#include "field.h"
#include "hash_table.h"
#include "meta_valid_model.h"
#include "structmember.h"
#include "validator/validator.h"
#include "vector_dict.h"
#include "json/json.h"

#define GET_SCHEMA(obj, offset) _CAST(Schema*, GET_OBJ(obj, offset))

static inline ContextManager*
valid_model_get_ctx(ValidModel* self)
{
    ContextManager* ctx = self->ctx;
    if (!ctx) {
        ctx = _CAST(MetaValidModel*, Py_TYPE(self))->ctx;
        self->ctx = (ContextManager*)Py_NewRef(ctx);
    }
    return ctx;
}

static int
valid_model_clear(ValidModel* self)
{
    Py_CLEAR(self->ctx);
    return DataModelType.head.ht_type.tp_clear((PyObject*)self);
}

static inline int
valid_model_create_missing(PyObject* name,
                           PyObject* arg,
                           PyObject* model,
                           ValidationError** err)
{
    if (arg && VectorDict_Check(arg)) {
        arg = _VectorDict_GetDict((_VectorDict*)arg);
        if (FT_UNLIKELY(!arg)) {
            return -1;
        }
    }
    return ValidationError_CreateMissing(name, arg, model, err);
}

static inline int
valid_model_init_val(PyObject** restrict slots,
                     Schema* restrict sc,
                     ValidationError** restrict err,
                     ValidateContext* restrict ctx,
                     PyObject* arg)
{
    Field* field = sc->field;
    if (!IS_FIELD_INIT(field->flags)) {
        return _DataModel_SetDefault(field, slots);
    }

    PyObject *val, *name = SCHEMA_GET_NAME(sc);
    val = arg ? _Object_Gettr(arg, name) : NULL;
    if (val) {
        int r = ValidSchema_ValidateInit(sc, val, slots, ctx, err);
        Py_DECREF(val);
        return r;
    }

    int r = _DataModel_SetDefault(field, slots);
    return r ? r : valid_model_create_missing(name, arg, ctx->model, err);
}

static int
valid_model_universal_init(PyObject* self, PyObject* kwargs)
{
    ValidationError* err = NULL;
    ValidateContext ctx = _VALID_MODEL_GET_CTX(self);
    PyObject** restrict slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, Py_TYPE(self), slots++)
    {
        if (FT_UNLIKELY(valid_model_init_val(slots, sc, &err, &ctx, kwargs) <
                        0)) {
            Py_XDECREF(err);
            return -1;
        }
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx.model);
        return -1;
    }
    return 0;
}

static inline int
valid_model_init_from_attributes(PyObject* self, PyObject* obj)
{
    return valid_model_universal_init(self, obj);
}

static int
valid_model_init(PyObject* self, PyObject* args, PyObject* kw)
{
    Py_ssize_t size = PyTuple_GET_SIZE(args);
    if (!kw && size == 1) {
        kw = PyTuple_GET_ITEM(args, 0);
        return valid_model_init_from_attributes(self, kw);
    }

    if (!PyCheck_MaxArgs("__init__", size, 0)) {
        return -1;
    }

    MetaModel* m = _CAST_META(Py_TYPE(self));
    if (IS_FAIL_ON_EXTRA_INIT(m->config->flags) &&
        !HashTable_CheckExtraDict(m->init_map, m->schemas, kw, "__init__")) {
        return -1;
    }
    return valid_model_universal_init(self, kw);
}

static int
valid_model_vec_init(PyObject* self,
                     PyObject* const* args,
                     size_t nargsf,
                     PyObject* kwnames)
{
    Py_ssize_t size = PyVectorcall_NARGS(nargsf);
    if (FT_UNLIKELY(!kwnames && size == 1)) {
        return valid_model_init_from_attributes(self, (PyObject*)*args);
    }

    if (FT_UNLIKELY(!PyCheck_ArgsCnt("__init__", size, 0))) {
        return -1;
    }

    MetaModel* meta = _CAST_META(Py_TYPE(self));
    PyObject** stack = DATA_MODEL_GET_SLOTS(self);
    if (FT_UNLIKELY(kwnames && _Schema_VectorInitKw(
                                 stack,
                                 meta->init_map,
                                 IS_FAIL_ON_EXTRA_INIT(meta->config->flags),
                                 args,
                                 kwnames) < 0)) {
        return -1;
    }

    ValidateContext ctx = _VALID_MODEL_GET_CTX(self);
    return _Schema_VecInitFinish(meta->schemas, stack, &ctx, args, kwnames);
}

static PyObject*
valid_model_from_attributes(PyTypeObject* cls, PyObject* obj)
{
    if (Py_IS_TYPE(obj, cls) && !_CAST(MetaValidModel*, cls)->gtypes) {
        return Py_NewRef(obj);
    }

    PyObject* self = _DataModel_Alloc(cls);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    if (valid_model_init_from_attributes(self, obj) < 0 ||
        _MetaModel_CallPostInit(self) < 0) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

inline void
_ValidModel_SetCtx(PyObject* self, ContextManager* ctx)
{
    PyObject* tp = (PyObject*)Py_TYPE(self);
    if (ctx->model != tp) {
        ctx = _CAST(MetaValidModel*, tp)->ctx;
    }
    _CAST(ValidModel*, self)->ctx = (ContextManager*)Py_XNewRef(ctx);
}

PyObject*
_ValidModel_FrostValidate(PyTypeObject* cls, PyObject* val, ContextManager* ctx)
{
    if (Py_IS_TYPE(val, cls) && !_CAST(MetaValidModel*, cls)->gtypes) {
        return Py_NewRef(val);
    }

    PyObject* self = _DataModel_Alloc(cls);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    _ValidModel_SetCtx(self, ctx);
    if (valid_model_init_from_attributes(self, val) < 0 ||
        _MetaModel_CallPostInit(self) < 0) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

static PyObject*
valid_model_frost_validate(PyTypeObject* cls,
                           PyObject* const* args,
                           Py_ssize_t nargs)
{
    PyObject* val;
    ContextManager* ctx;
    if (FT_UNLIKELY(_ParseFrostValidate(args, nargs, &val, &ctx) < 0)) {
        return NULL;
    }
    return _ValidModel_FrostValidate(cls, val, ctx);
}

static PyObject*
valid_model_from_json(PyTypeObject* cls,
                      PyObject** args,
                      size_t nargs,
                      PyObject* kwnames)
{
    Py_ssize_t cnt = PyVectorcall_NARGS(nargs);
    if (FT_UNLIKELY(!PyCheck_ArgsCnt(".from_json", cnt, 1))) {
        return NULL;
    }
    return JsonValidParse_ValidModel(
      cls, *args, _CAST(MetaValidModel*, cls)->ctx, args + 1, kwnames);
}

PyObject*
_ValidModel_Construct(PyTypeObject* cls,
                      PyObject* const* args,
                      Py_ssize_t nargs,
                      PyObject* kwnames)
{
    PyObject* self = _DataModel_Alloc(cls);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    if (FT_UNLIKELY(DataModelType.vec_init(self, args, nargs, kwnames) < 0 ||
                    _MetaModel_CallPostInit(self) < 0)) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

int
_ValidModel_Update(PyObject* self,
                   PyObject** args,
                   PyObject* kwnames,
                   ValidateContext* ctx,
                   ValidationError** err)
{
    MetaModel* meta = _CAST_META(Py_TYPE(self));
    HashTable* map = meta->attr_map;
    PyObject** stack = GET_ADDR(self, meta->slot_offset);
    Schema** schms = (Schema**)TUPLE_ITEMS(meta->schemas);

    TupleForeach(name, kwnames, args++)
    {
        const Py_ssize_t offset = _HashTable_Get(map, name);
        if (FT_UNLIKELY(offset < 0)) {
            continue;
        }

        PyObject** addr = GET_ADDR(stack, offset);
        Schema* sc = GET_SCHEMA(schms, offset);
        if (FT_UNLIKELY(ValidSchema_ValidateInit(sc, *args, addr, ctx, err) <
                        0)) {
            return -1;
        }
    }
    return 0;
}

static PyObject*
valid_model_copy(PyObject* self,
                 PyObject** args,
                 size_t nargsf,
                 PyObject* kwnames)
{
    if (!PyCheck_ArgsCnt("copy", PyVectorcall_NARGS(nargsf), 0)) {
        return NULL;
    }

    PyObject* res = _DataModel_CallCopy(self);
    if (!res || !kwnames) {
        return res;
    }

    ValidationError* err = NULL;
    ValidateContext ctx = _VALID_MODEL_GET_CTX(self);
    if (FT_UNLIKELY(_ValidModel_Update(res, args, kwnames, &ctx, &err) < 0)) {
        Py_DECREF(res);
        Py_XDECREF(err);
        return NULL;
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx.model);
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static int
valid_model__setstate__nested(PyObject* self, PyObject* state)
{
    if (FT_UNLIKELY(!PyDict_Check(state))) {
        _RaiseInvalidType("state", "dict", Py_TYPE(state)->tp_name);
        return -1;
    }

    ValidationError* err = NULL;
    ValidateContext ctx = _VALID_MODEL_GET_CTX(self);
    PyObject** restrict slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, Py_TYPE(self), slots++)
    {
        PyObject* val = _Dict_GetAscii(state, SCHEMA_GET_NAME(sc));
        if (!val) {
            continue;
        }

        if (FT_UNLIKELY(ValidSchema_ValidateInit(sc, val, slots, &ctx, &err) <
                        0)) {
            Py_XDECREF(err);
            return -1;
        }
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx.model);
        return -1;
    }
    return 0;
}

int
_ValidModel_Diff(PyObject* self,
                 PyObject* other,
                 uint32_t flags,
                 PyObject** res)
{
    PyObject* dict = NULL;
    PyObject** o_slots = DATA_MODEL_GET_SLOTS(other);
    PyObject** slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, Py_TYPE(self), slots++, o_slots++)
    {
        PyObject* val = _DataModel_FastGet(sc, slots, self);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        PyObject* o_val = _DataModel_FastGet(sc, o_slots, other);
        if (FT_UNLIKELY(!o_val)) {
            Py_DECREF(val);
            goto error;
        }

        PyObject* tmp;
        int r;
        if (IS_FIELD_DIFF_KEY(sc->field->flags)) {
            PyObject* key = Field_GET_DIFF_KEY(sc->field);
            r = _Diff_ObjByKey(val, o_val, flags, key, &tmp);
        } else {
            r = _Diff_Obj(val, o_val, flags, &tmp);
        }
        Py_DECREF(o_val);
        Py_DECREF(val);

        if (FT_UNLIKELY(r < 0)) {
            goto error;
        } else if (!r) {
            continue;
        }

        if (!dict) {
            dict = PyDict_New();
            if (FT_UNLIKELY(!dict)) {
                Py_DECREF(tmp);
                goto error;
            }
        }

        if (FT_UNLIKELY(_PyDict_SetItemAsciiDecrefVal(dict, sc->name, tmp) <
                        0)) {
            goto error;
        }
    }

    *res = dict;
    return dict ? 1 : 0;
error:
    Py_XDECREF(dict);
    *res = NULL;
    return -1;
}

static PyObject*
valid_model_diff(PyObject* self,
                 PyObject** args,
                 Py_ssize_t nargsf,
                 PyObject* kwnames)
{
    if (!PyCheck_ArgsCnt("model_diff", PyVectorcall_NARGS(nargsf), 1)) {
        return NULL;
    }

    PyObject* other = *args;
    PyObject* buff[2] = { NULL };
    static const char* const kwlist[] = { "skip_none", "copy_values", NULL };
    static _PyArg_Parser _parser = {
        .fname = "model_diff",
        .keywords = kwlist,
        .kwtuple = NULL,
    };

    args++;
    if (!PyArg_UnpackKeywords(args,
                              0,
                              NULL,
                              kwnames,
                              &_parser,
                              0, /*minpos*/
                              0, /*maxpos*/
                              0, /*minkw*/
                              buff)) {
        return NULL;
    }

    if (!_ValidateArg(other, Py_TYPE(self), "other")) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i != 2; i++) {
        if (!_ValidateArg(buff[i], &PyBool_Type, kwlist[i])) {
            return NULL;
        }
    }

    uint32_t flags = buff[0] == Py_True ? DIFF_SKIP_NONE : 0;
    if (buff[1] == Py_True) {
        flags |= DIFF_COPY_VALUES;
    }

    PyObject* res;
    if (!_ValidModel_Diff(self, other, flags, &res)) {
        return PyDict_New();
    }
    return res;
}

PyObject*
_ValidModel_WithDiff(PyObject* self, PyObject* diff, uint32_t flags)
{
    if (FT_UNLIKELY(!_ValidateArg(diff, &PyDict_Type, "diff"))) {
        return NULL;
    }

    PyObject* res = _DataModel_Copy(self);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    ValidationError* err = NULL;
    PyObject *diff_key, *item, *val, *new_val;
    ValidateContext ctx = _VALID_MODEL_GET_CTX(res);
    PyObject** restrict slots = DATA_MODEL_GET_SLOTS(res);

    SchemaForeach(sc, Py_TYPE(res), slots++)
    {
        item = _PyDict_GetItem_Ascii(diff, sc->name);
        if (!item) {
            continue;
        }

        val = _DataModel_FastGet(sc, slots, res);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        diff_key = Field_GET_DIFF_KEY(sc->field);
        if (diff_key) {
            new_val = WithDiff_UpdateByDiffKey(val, item, flags, diff_key);
        } else {
            new_val = WithDiff_Update(val, item, flags);
        }
        Py_DECREF(val);

        if (FT_UNLIKELY(!new_val)) {
            goto error;
        }

        int r = ValidSchema_ValidateInit(sc, new_val, slots, &ctx, &err);
        Py_DECREF(new_val);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx.model);
        Py_DECREF(res);
        return NULL;
    }

    return res;

error:
    Py_XDECREF(err);
    Py_DECREF(res);
    return NULL;
}

static PyObject*
valid_model_with_diff(PyObject* self,
                      PyObject** args,
                      Py_ssize_t nargsf,
                      PyObject* kwnames)
{
    if (!PyCheck_ArgsCnt("with_diff", PyVectorcall_NARGS(nargsf), 1)) {
        return NULL;
    }

    PyObject *update = *args, *revert = NULL;
    static const char* const kwlist[] = { "revert", NULL };
    static _PyArg_Parser _parser = {
        .fname = "with_diff",
        .keywords = kwlist,
        .kwtuple = NULL,
    };

    args++;
    if (!PyArg_UnpackKeywords(args,
                              0,
                              NULL,
                              kwnames,
                              &_parser,
                              0, /*minpos*/
                              0, /*maxpos*/
                              0, /*minkw*/
                              &revert)) {
        return NULL;
    }

    if (!_ValidateArg(revert, &PyBool_Type, "revert")) {
        return NULL;
    }
    uint32_t flags = revert == Py_True ? WITH_DIFF_REVERT : 0;
    return _ValidModel_WithDiff(self, update, flags);
}

static PyObject*
valid_model__setstate__(PyObject* self, PyObject* state)
{
    if (valid_model__setstate__nested(self, state) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

static PyMethodDef valid_model_methods[] = {
    { "__setstate__", PY_METHOD_CAST(valid_model__setstate__), METH_O, NULL },
    { "__frost_validate__",
      PY_METHOD_CAST(valid_model_frost_validate),
      METH_CLASS | METH_FASTCALL,
      NULL },
    { "model_diff",
      PY_METHOD_CAST(valid_model_diff),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "with_diff",
      PY_METHOD_CAST(valid_model_with_diff),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "copy",
      PY_METHOD_CAST(valid_model_copy),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "from_attributes",
      PY_METHOD_CAST(valid_model_from_attributes),
      METH_CLASS | METH_O,
      NULL },
    { "from_json",
      PY_METHOD_CAST(valid_model_from_json),
      METH_CLASS | METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "construct",
      PY_METHOD_CAST(_ValidModel_Construct),
      METH_CLASS | METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { NULL }
};

static PyMemberDef meta_valid_members[] = {
    { "__context__", T_OBJECT, offsetof(ValidModel, ctx), READONLY, NULL },
    { NULL },
};

MetaValidModel ValidModelType = {
    .gtypes = NULL,
    .ctx = NULL,
    .head= {
        .slot_offset = (Py_ssize_t)sizeof(ValidModel),
        .vec_init = valid_model_vec_init,
        .head = {
            .ht_type = {
            PyVarObject_HEAD_INIT(&MetaValidModelType, 0)
            .tp_flags =
            Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | TPFLAGS_META_SUBCLASS |
            TPFLAGS_META_VALID_SUBCLASS | Py_TPFLAGS_HAVE_VECTORCALL,
            .tp_vectorcall = (vectorcallfunc)_MetaModel_Vectorcall,
            .tp_traverse = (traverseproc)_DataModel_Traverse,
            .tp_dealloc = (destructor)_Object_Dealloc,
            .tp_base = (PyTypeObject *)&DataModelType,
            .tp_clear = (inquiry)valid_model_clear,
            .tp_name = "frost_typing.ValidModel",
            .tp_basicsize = sizeof(ValidModel),
            .tp_methods = valid_model_methods,
            .tp_members = meta_valid_members,
            .tp_init = valid_model_init,
            }
        },
    },
};

PyObject*
_ValidModel_CtxFromJson(ContextManager* ctx,
                        PyObject* obj,
                        PyObject** args,
                        PyObject* kwnames)
{
    PyTypeObject* cls = _CAST(PyTypeObject*, ctx->model);
    return JsonValidParse_ValidModel(cls, obj, ctx, args, kwnames);
}

PyObject*
_ValidModel_CtxCall(ContextManager* ctx,
                    PyObject** args,
                    Py_ssize_t nargsf,
                    PyObject* kwnames)
{
    PyTypeObject* cls = _CAST(PyTypeObject*, ctx->model);
    int frost_validate;
    nargsf = Ctx_NARGS(nargsf, &frost_validate);
    if (frost_validate) {
        PyObject* obj = *args;
        PyObject* fv = _CAST(MetaValidModel*, cls)->__frost_validate__;
        if (FT_LIKELY(fv == ValidModelType.__frost_validate__)) {
            return _ValidModel_FrostValidate(cls, obj, ctx);
        }
        PyObject* res =
          PyObject_CallThreeArg(fv, (PyObject*)cls, obj, (PyObject*)ctx);
        if (!res) {
            ValidationError_ExceptionHandling((PyObject*)ctx, obj);
        }
        return res;
    }

    PyObject* self = _DataModel_Alloc(cls);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    _ValidModel_SetCtx(self, ctx);
    if (valid_model_vec_init(self, args, nargsf, kwnames) < 0 ||
        _MetaModel_CallPostInit(self) < 0) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

inline ValidateContext
_ValidModel_GetCtx(ValidModel* self)
{
    ContextManager* ctx = valid_model_get_ctx(self);
    return ValidateCtx_Create(
      ctx,
      self,
      self,
      ctx,
      _CTX_CONFIG_GET_FLAGS(_CAST_META(Py_TYPE(self))->config));
}

int
valid_model_setup(void)
{
    Py_SET_TYPE(&ValidModelType, &MetaValidModelType);
    Py_INCREF(DefaultConfigValid);

    ValidModelType.head.config = DefaultConfigValid;
    ValidModelType.head.schemas = Py_NewRef(VoidTuple);
    if (!ValidModelType.head.schemas) {
        return -1;
    }

    if (PyType_Ready((PyTypeObject*)&ValidModelType) < 0) {
        return -1;
    }

    Py_INCREF(&MetaValidModelType);
    Py_SET_TYPE(&ValidModelType, &MetaValidModelType);

    ValidModelType.ctx = ContextManager_CREATE(&ValidModelType);
    if (!ValidModelType.ctx) {
        return -1;
    }

    ValidModelType.head.__copy__ = Py_NewRef(DataModelType.__copy__);
    ValidModelType.head.__as_dict__ = Py_NewRef(DataModelType.__as_dict__);
    ValidModelType.head.__as_json__ = Py_NewRef(DataModelType.__as_json__);
    ValidModelType.__frost_validate__ = _Dict_GetAscii(
      ValidModelType.head.head.ht_type.tp_dict, __frost_validate__);
    if (!ValidModelType.__frost_validate__) {
        return -1;
    }
    return 0;
}

void
valid_model_free(void)
{
}