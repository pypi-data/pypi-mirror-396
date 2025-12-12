#include "field.h"
#include "json_schema.h"
#include "meta_valid_model.h"
#include "stddef.h"
#include "structmember.h"
#include "valid_model.h"
#include "validated_func.h"
#include "validator/validator.h"
#include "json/deserialize/decoder.h"

static int
context_repr_nested(ContextManager* self, UnicodeWriter* writer)
{
    if (FT_UNLIKELY(_ContextManager_ReprModel(writer, self->model) < 0)) {
        return -1;
    }

    if (!CTX_NUM_ITEMS(self)) {
        return 0;
    }

    _UNICODE_WRITE_CHAR(writer, '[');
    for (Py_ssize_t i = 0; i != CTX_NUM_ITEMS(self); i++) {
        if (i) {
            _UNICODE_WRITE_STRING(writer, ", ", 2);
        }

        PyObject* val = self->items[i].hint;
        if (PyType_Check(val)) {
            _UNICODE_WRITE_STRING(
              writer, _CAST(PyTypeObject*, val)->tp_name, -1);
        } else {
            _UNICODE_WRITE(writer, val, PyObject_Repr);
        }
    }

    _UNICODE_WRITE_CHAR(writer, ']');
    return 0;

error:
    return -1;
}

static PyObject*
context_repr(ContextManager* self)
{
    int r = Py_ReprEnter((PyObject*)self);
    if (r) {
        return r > 0 ? PyObject_Repr(self->model) : NULL;
    }

    UnicodeWriter_Create(writer, 4);
    if (FT_UNLIKELY(!writer)) {
        return NULL;
    }

    if (FT_UNLIKELY(context_repr_nested(self, writer) < 0)) {
        UnicodeWriter_Discard(writer);
        Py_ReprLeave((PyObject*)self);
        return NULL;
    }

    Py_ReprLeave((PyObject*)self);
    return UnicodeWriter_Finish(writer);
}

static int
context_clear(ContextManager* self)
{
    if (PyType_SUPPORTS_WEAKREFS(Py_TYPE(self))) {
        PyObject_ClearWeakRefs((PyObject*)self);
    }

    Py_CLEAR(self->model);
    Py_CLEAR(self->gtypes);
    for (Py_ssize_t i = 0; i != CTX_NUM_ITEMS(self); i++) {
        ContextManagerItem* item = self->items + i;
        Py_CLEAR(item->validator);
        Py_CLEAR(item->hint);
    }
    return 0;
}

static int
context_traverse(ContextManager* self, visitproc visit, void* arg)
{
    Py_VISIT(self->model);
    Py_VISIT(self->gtypes);
    for (Py_ssize_t i = 0; i != CTX_NUM_ITEMS(self); i++) {
        ContextManagerItem* item = self->items + i;
        Py_VISIT(item->validator);
        Py_VISIT(item->hint);
    }
    return 0;
}

static ContextManager*
context_new(Py_ssize_t size,
            PyObject* model,
            PyObject* gtypes,
            ContextManagerCall validate_call,
            ContextManagerFromJson from_json)
{
    ContextManager* self =
      Object_NewVar(ContextManager, &ContextManager_Type, size);
    if (FT_LIKELY(self)) {
        self->model = Py_NewRef(model);
        self->gtypes = Py_NewRef(gtypes ? gtypes : VoidTuple);
        self->validate_call = validate_call;
        self->from_json = from_json;
    }

    return self;
}

static inline int
context_check_size(PyObject* model, PyObject* gtypes, Py_ssize_t key_size)
{
    if (FT_UNLIKELY(!gtypes)) {
        PyErr_Format(PyExc_TypeError,
                     "type '%.100s' is not subscriptable",
                     Py_TYPE(model)->tp_name);
        return 0;
    }

    Py_ssize_t gtypes_size = PyTuple_GET_SIZE(gtypes);
    for (Py_ssize_t i = 0; i != gtypes_size; i++) {
        PyObject* hint = PyTuple_GET_ITEM(gtypes, i);
        if (FT_UNLIKELY(!Py_IS_TYPE(hint, (PyTypeObject*)PyTypeVar))) {
            PyErr_SetString(
              PyExc_TypeError,
              "Parameters to Generic[...] must all be type variables");
            return 0;
        }
    }
    return PyCheck_ArgsCnt("__class_getitem__", key_size, gtypes_size);
}

static PyObject*
context_creat_by_key(PyObject* model,
                     PyObject* gtypes,
                     PyObject* key,
                     ContextManagerCall validate_call,
                     ContextManagerFromJson from_json)
{
    int is_tuple = PyTuple_Check(key);
    Py_ssize_t key_size = is_tuple ? PyTuple_GET_SIZE(key) : 1;
    PyObject* const* keys =
      is_tuple ? (PyObject* const*)TUPLE_ITEMS(key) : &key;
    if (FT_UNLIKELY(!context_check_size(model, gtypes, key_size))) {
        return NULL;
    }

    ContextManager* self;
    self = context_new(key_size, model, gtypes, validate_call, from_json);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    PyObject* tp = (PyObject*)(PyTuple_Check(model) ? model : NULL);
    for (Py_ssize_t i = 0; i != CTX_NUM_ITEMS(self); i++) {
        PyObject* key_item = keys[i];
        TypeAdapter* validator = ParseHint(key_item, tp);
        if (FT_UNLIKELY(!validator)) {
            Py_DECREF(self);
            return NULL;
        }
        self->items[i].hint = Py_NewRef(key_item);
        self->items[i].validator = validator;
    }
    return (PyObject*)self;
}

inline PyObject*
_ContextManager_CreateGetItem(PyObject* model,
                              PyObject* gtypes,
                              PyObject* key,
                              ContextManagerCall call,
                              ContextManagerFromJson from_json)
{
    return context_creat_by_key(model, gtypes, key, call, from_json);
}

int
_ContextManager_ReprModel(UnicodeWriter* writer, PyObject* model)
{
    if (ContextManager_Check(model)) {
        return context_repr_nested((ContextManager*)model, writer);
    }

    if (PyUnicode_Check(model)) {
        return UnicodeWriter_WriteStr(writer, model);
    }

    ConverterObject conv;
    if (PyType_Check(model)) {
        conv = (ConverterObject)PyObject_Get__name__;
    } else if (ValidatedFunc_Check(model)) {
        conv = (ConverterObject)_ValidatedFunc_GetName;
    } else {
        conv = PyObject_Repr;
    }
    return _UnicodeWriter_Write(writer, model, conv);
}

PyObject*
_ContextManager_Get_THint(PyObject* cls, ContextManager* ctx)
{
    if (FT_UNLIKELY(!ctx->gtypes)) {
        return NULL;
    }

    PyObject** items = TUPLE_ITEMS(ctx->gtypes);
    Py_ssize_t size = PyTuple_GET_SIZE(ctx->gtypes);
    Py_ssize_t i = _ArrayFastSearh(items, cls, size);
    if (i < 0 || i >= CTX_NUM_ITEMS(ctx)) {
        return NULL;
    }

    /* Protection against recursion if the
        user has passed himself as a parameter.*/
    PyObject* res = ctx->items[i].hint;
    return _ArrayFastSearh(items, res, size) < 0 ? res : NULL;
}

int
_ContextManager_Get_TTypeAdapter(PyObject* cls,
                                 ContextManager* ctx,
                                 TypeAdapter** validator)
{
    if (!ctx->gtypes) {
        return 0;
    }

    PyObject** items = TUPLE_ITEMS(ctx->gtypes);
    Py_ssize_t size = PyTuple_GET_SIZE(ctx->gtypes);
    Py_ssize_t i = _ArrayFastSearh(items, cls, size);
    if (i < 0 || i >= CTX_NUM_ITEMS(ctx)) {
        return 0;
    }

    ContextManagerItem* item = &ctx->items[i];
    /* Protection against recursion if the
        user has passed himself as a parameter.*/
    if (_ArrayFastSearh(items, item->hint, size) < 0) {
        if (FT_UNLIKELY(!item->validator)) {
            PyObject* tp = PyType_Check(ctx->model) ? ctx->model : NULL;
            item->validator = ParseHint(item->hint, tp);
            if (FT_UNLIKELY(!item->validator)) {
                return -1;
            }
        }
        *validator = item->validator;
        return 1;
    }
    return 0;
}

ContextManager*
_ContextManager_New(PyObject* model,
                    ContextManagerCall call,
                    ContextManagerFromJson from_json)
{
    return context_new(0, model, NULL, call, from_json);
}

int
_ParseFrostValidate(PyObject* const* args,
                    Py_ssize_t nargs,
                    PyObject** val,
                    ContextManager** ctx)
{
    if (FT_UNLIKELY(!PyCheck_ArgsCnt(
          "__frost_validate__", PyVectorcall_NARGS(nargs), 2))) {
        return -1;
    }

    ContextManager* context = (ContextManager*)args[1];
    if (FT_UNLIKELY(!ContextManager_Check(context))) {
        PyErr_Format(PyExc_TypeError,
                     "__frost_validate__() argument 2 must "
                     "be ContextManager, not %.100s",
                     Py_TYPE(context)->tp_name);
        return -1;
    }

    *val = args[0];
    *ctx = context;
    return 0;
}

static inline PyObject*
context_call_frost_validate(ContextManager* self, PyObject* obj)
{
    if (FT_UNLIKELY(!self->validate_call)) {
        return PyErr_Format(PyExc_TypeError,
                            "'%.100s' object is not callable",
                            Py_TYPE(self)->tp_name);
    }
    return self->validate_call(self, &obj, 1 | CTX_FROST_VALIDATE_CALL, NULL);
}

inline Py_ssize_t
Ctx_NARGS(Py_ssize_t nargs, int* frost_validate)
{
    *frost_validate = (nargs & CTX_FROST_VALIDATE_CALL) != 0;
    return nargs & ~(PY_VECTORCALL_ARGUMENTS_OFFSET | CTX_FROST_VALIDATE_CALL);
}

ContextManager*
_ContextManager_CreateByOld(ContextManager* self, ContextManager* ctx)
{
    Py_ssize_t size = CTX_NUM_ITEMS(self);
    ContextManager* new_ctx = context_new(
      size, self->model, self->gtypes, self->validate_call, self->from_json);
    if (FT_UNLIKELY(!new_ctx)) {
        return new_ctx;
    }

    Py_ssize_t array_size = ctx->gtypes ? PyTuple_GET_SIZE(ctx->gtypes) : 0;
    PyObject* const* array = ctx->gtypes ? TUPLE_ITEMS(ctx->gtypes) : NULL;
    for (Py_ssize_t i = 0; i != size; i++) {
        Py_ssize_t j = _ArrayFastSearh(array, self->items[i].hint, array_size);
        if (FT_UNLIKELY(j < 0)) {
            new_ctx->items[i].hint = Py_XNewRef(self->items[i].hint);
            continue;
        }
        ContextManagerItem item = ctx->items[j];
        new_ctx->items[i] = item;
        Py_INCREF(item.hint);
        Py_XINCREF(item.validator);
    }
    return new_ctx;
}

PyObject*
_ContextManager_FrostValidate(ContextManager* self,
                              PyObject* val,
                              ContextManager* ctx)
{
    ContextManager* new_ctx = _ContextManager_CreateByOld(self, ctx);
    if (FT_UNLIKELY(!new_ctx)) {
        return NULL;
    }

    PyObject* res = context_call_frost_validate(new_ctx, val);
    Py_DECREF(new_ctx);
    return res;
}

static PyObject*
context_frost_validate(ContextManager* self,
                       PyObject* const* args,
                       Py_ssize_t nargs)
{
    PyObject* val;
    ContextManager* ctx;
    if (FT_UNLIKELY(_ParseFrostValidate(args, nargs, &val, &ctx) < 0)) {
        return NULL;
    }
    return _ContextManager_FrostValidate(self, val, ctx);
}

static PyObject*
context_construct(ContextManager* self,
                  PyObject* const* args,
                  Py_ssize_t nargs,
                  PyObject* kwnames)
{
    if (FT_UNLIKELY(!PyType_Check(self->model) ||
                    !MetaValid_IS_SUBCLASS(self->model))) {
        return ATTRIBUT_ERROR(self, "construct");
    }

    PyObject* res =
      _ValidModel_Construct((PyTypeObject*)self->model, args, nargs, kwnames);
    if (res && Py_IS_TYPE(res, (PyTypeObject*)self->model)) {
        Py_INCREF(self);
        _CAST(ValidModel*, res)->ctx = self;
    }
    return res;
}

static PyObject*
context_from_json(ContextManager* self,
                  PyObject** args,
                  Py_ssize_t nargs,
                  PyObject* kwnames)
{
    if (FT_UNLIKELY(!self->validate_call)) {
        ATTRIBUT_ERROR(self, ".from_json")
        return NULL;
    }

    if (FT_UNLIKELY(
          !PyCheck_ArgsCnt(".from_json", PyVectorcall_NARGS(nargs), 1))) {
        return NULL;
    }
    return self->from_json(self, *args, args + 1, kwnames);
}

static PyObject*
context_manager_subscript(ContextManager* self, PyObject* key)
{
    TypeAdapter* res;
    int r = _ContextManager_Get_TTypeAdapter(key, self, &res);

    if (FT_UNLIKELY(r < 0)) {
        return NULL;
    }

    if (FT_LIKELY(r)) {
        return Py_NewRef(res);
    }

    PyErr_SetObject(PyExc_KeyError, key);
    return NULL;
}

static PyObject*
get_args(ContextManager* self, UNUSED void* _)
{
    Py_ssize_t size = CTX_NUM_ITEMS(self);
    PyObject* res = PyTuple_New(size);
    if (FT_LIKELY(res)) {
        for (Py_ssize_t i = 0; i != size; i++) {
            PyTuple_SET_ITEM(res, i, Py_NewRef(self->items[i].hint));
        }
    }
    return res;
}

static PyObject*
get_self(ContextManager* self, UNUSED void* _)
{
    return Py_NewRef(self);
}

static PyMethodDef context_methods[] = {
    { "__frost_validate__",
      PY_METHOD_CAST(context_frost_validate),
      METH_FASTCALL,
      NULL },
    { "construct",
      PY_METHOD_CAST(context_construct),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "json_schema", PY_METHOD_CAST(Schema_JsonSchema), METH_NOARGS, NULL },
    { "from_attributes",
      PY_METHOD_CAST(context_call_frost_validate),
      METH_O,
      NULL },
    { "from_json",
      PY_METHOD_CAST(context_from_json),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "from_db_row", PY_METHOD_CAST(Object_FromDbRow), METH_FASTCALL, NULL },
    { NULL }
};

static PyMemberDef context_manager_members[] = {
    { "__gtypes__",
      T_OBJECT,
      offsetof(ContextManager, gtypes),
      READONLY,
      NULL },
    { "__origin__", T_OBJECT, offsetof(ContextManager, model), READONLY, NULL },
    { NULL },
};

static PyGetSetDef context_manager_getsets[] = {
    { "__args__", PY_GETTER_CAST(get_args), NULL, NULL, NULL },
    { "__context__", PY_GETTER_CAST(get_self), NULL, NULL, NULL },
    { NULL },
};

static PyMappingMethods сontext_manager_as_mapping = {
    .mp_subscript = (binaryfunc)context_manager_subscript,
};

PyTypeObject ContextManager_Type = {
    PyVarObject_HEAD_INIT(0, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC | Py_TPFLAGS_HAVE_VECTORCALL,
    .tp_vectorcall_offset = offsetof(ContextManager, validate_call),
    .tp_basicsize = offsetof(ContextManager, items),
    .tp_traverse = (traverseproc)context_traverse,
    .tp_as_mapping = &сontext_manager_as_mapping,
    .tp_dealloc = (destructor)_Object_Dealloc,
    .tp_itemsize = sizeof(ContextManagerItem),
    .tp_name = "frost_typing.ContextManager",
    .tp_members = context_manager_members,
    .tp_getset = context_manager_getsets,
    .tp_clear = (inquiry)context_clear,
    .tp_repr = (reprfunc)context_repr,
    .tp_str = (reprfunc)context_repr,
    .tp_alloc = PyType_GenericAlloc,
    .tp_methods = context_methods,
    .tp_call = PyVectorcall_Call,
    .tp_free = PyObject_GC_Del,
};

int
context_setup(void)
{
    return PyType_Ready(&ContextManager_Type);
}

void
context_free(void)
{
}