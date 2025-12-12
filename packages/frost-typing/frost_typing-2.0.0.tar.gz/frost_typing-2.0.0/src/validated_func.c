#include "validator/validator.h"

#include "convector.h"
#include "data_model.h"
#include "field.h"
#include "hash_table.h"
#include "json_schema.h"
#include "schema.h"
#include "stddef.h"
#include "structmember.h"
#include "valid_model.h"
#include "validated_func.h"
#include "vector_dict.h"
#include "json/json.h"

#define FUNC_GET_NAME(s) s->func->func_name
#define _FUNC_GET_NAME(s) _CAST(const char*, PyUnicode_DATA(FUNC_GET_NAME(s)))
#define _VD_FUNC_GET_ACNT(o) _FUNC_GET_ACNT(_CAST_FUNC_VALIDATOR(o)->func)
#define HAS_COROUTINE(f) ((FUNC_GET_FLAGS(f) & CO_COROUTINE) != 0)

typedef struct vd_args
{
    Py_ssize_t args_cnt;
    Py_ssize_t nargs;
    PyObject** stack;
    PyObject** args;
    PyObject* kw;
    ValidationError* err;
    ValidateContext* ctx;
} vd_args;

static int
args_kwargs_finish(ArgsKwargs* self);

static int
validated_func_is_init(ValidatedFunc* self)
{
    if (FT_LIKELY(self->func)) {
        return 1;
    }
    PyErr_Format(
      PyExc_TypeError, "%s is not initialized", Py_TYPE(self)->tp_name);
    return 0;
}

static PyObject*
validated_func_call_frost_validate(ContextManager* ctx,
                                   PyObject** args,
                                   Py_ssize_t nargs,
                                   PyObject* kwnames);

static PyObject*
validated_func_get(PyObject* self, PyObject* obj, UNUSED PyObject* type)
{
    if (!_CAST(ValidatedFunc*, self)->func) {
        return Py_NewRef(self);
    }

    if (obj == NULL || obj == Py_None) {
        return Py_NewRef(self);
    }
    return PyMethod_New(self, obj);
}

static int
validated_func_clear(ValidatedFunc* self)
{
    Py_CLEAR(self->map);
    Py_CLEAR(self->func);
    Py_CLEAR(self->gtypes);
    Py_CLEAR(self->schemas);
    Py_CLEAR(self->kwnames);
    Py_CLEAR(self->varnames);
    Py_CLEAR(self->head.ctx);
    Py_CLEAR(self->a_schema);
    Py_CLEAR(self->kw_schema);
    Py_CLEAR(self->r_validator);
    return 0;
}

static int
validated_func_traverse(ValidatedFunc* self, visitproc visit, void* arg)
{
    Py_VISIT(self->func);
    Py_VISIT(self->schemas);
    Py_VISIT(self->gtypes);
    Py_VISIT(self->kwnames);
    Py_VISIT(self->head.ctx);
    Py_VISIT(self->varnames);
    Py_VISIT(self->a_schema);
    Py_VISIT(self->kw_schema);
    Py_VISIT(self->r_validator);
    return 0;
}

static PyObject*
validated_func_repr(ValidatedFunc* self)
{
    if (!self->func) {
        return PyObject_Get__name__(Py_TYPE(self));
    }

    int r = Py_ReprEnter((PyObject*)self);
    if (r) {
        if (r > 0) {
            return PyUnicode_FromFormat("%U(...)", FUNC_GET_NAME(self));
        }
        return NULL;
    }

    Py_ssize_t size = VD_FUNC_GET_SIZE(self);
    Py_ssize_t argscnt = _VD_FUNC_GET_ACNT(self);

    UnicodeWriter_Create(writer, size * 5);
    if (FT_UNLIKELY(!writer)) {
        return NULL;
    }

    Schema** schemas = _VALID_FUNC_GET_SCHEMAS(self);

    _UNICODE_WRITE_STR(writer, FUNC_GET_NAME(self));
    _UNICODE_WRITE_CHAR(writer, '(');
    for (Py_ssize_t i = 0; i != size; ++i) {
        Schema* sc = schemas[i];
        if (i) {
            _UNICODE_WRITE_STRING(writer, ", ", 2);
        }

        if (FT_UNLIKELY(i == argscnt)) {
            if (self->a_schema) {
                _UNICODE_WRITE_CHAR(writer, '*');

                if (UnicodeWriter_WriteStr(
                      writer, self->a_schema->schema_base.name) < 0) {
                    goto error;
                }

                _UNICODE_WRITE_STRING(writer, ": ", 2);
                _UNICODE_WRITE(
                  writer, self->a_schema->validator, PyObject_Repr);
                _UNICODE_WRITE_STRING(writer, ", ", 2);
            } else {
                _UNICODE_WRITE_STRING(writer, "*, ", 3);
            }
        }

        if (UnicodeWriter_WriteStr(writer, sc->name) < 0) {
            goto error;
        }
        TypeAdapter* vd = _Schema_GET_VALIDATOR(sc);
        _UNICODE_WRITE_STRING(writer, ": ", 2);
        _UNICODE_WRITE(writer, vd, PyObject_Repr);
    }

    if (self->kw_schema) {
        _UNICODE_WRITE_STRING(writer, ", **", 4);
        if (UnicodeWriter_WriteStr(writer, self->kw_schema->schema_base.name) <
            0) {
            goto error;
        }

        _UNICODE_WRITE_STRING(writer, ": ", 2);
        _UNICODE_WRITE(writer, self->kw_schema->validator, PyObject_Repr);
    }

    _UNICODE_WRITE_STRING(writer, ") -> ", 5);
    _UNICODE_WRITE(writer, (PyObject*)self->r_validator, PyObject_Repr);

    Py_ReprLeave((PyObject*)self);
    return UnicodeWriter_Finish(writer);

error:
    UnicodeWriter_Discard(writer);
    Py_ReprLeave((PyObject*)self);
    return NULL;
}

static inline int
validated_func_get_default(Schema* sc, vd_args* va, PyObject** res)
{
    int r = _DataModel_SetDefault(sc->field, res);
    if (r) {
        return r;
    }
    return ValidationError_CreateMissing(
      sc->name, va->ctx->data, va->ctx->model, &va->err);
}

static inline int
validate_args(Schema* sc, PyObject* val, PyObject** res, vd_args* va)
{
    TypeAdapter* vd = _Schema_GET_VALIDATOR(sc);
    *res = TypeAdapter_Conversion(vd, va->ctx, val);
    if (*res) {
        return 0;
    }
    return ValidationError_CREATE(sc->name, vd, val, va->ctx->model, &va->err);
}

static inline int
validate_decref_args(Schema* sc, PyObject* val, PyObject** res, vd_args* va)
{
    int r = validate_args(sc, val, res, va);
    Py_DECREF(val);
    return r;
}

static inline int
validate_args_getter(Schema* sc, PyObject* val, Py_ssize_t ind, vd_args* va)
{
    if (FT_LIKELY(val)) {
        return validate_decref_args(sc, val, va->stack + ind, va);
    }
    return validated_func_get_default(sc, va, va->stack + ind);
}

static Py_ssize_t
validated_func_args_stack(ValidatedFunc* self, vd_args* va, InitGetter getter)
{
    PyObject* val;
    Py_ssize_t j = 0, i = 0;
    Schema *sc, **schemas = _VALID_FUNC_GET_SCHEMAS(self);
    Py_ssize_t size = VD_FUNC_GET_SIZE(self) - HAS_VARKEYWORDS(self->func);

    for (; i < va->args_cnt && i < va->nargs && j != size; j++, i++) {
        sc = schemas[j];
        val = va->kw ? getter(va->kw, sc->name) : NULL;
        if (val) {
            Py_DECREF(val);
            PyErr_Format(PyExc_TypeError,
                         "%.100U() got multiple values for argument '%U'",
                         FUNC_GET_NAME(self),
                         sc->name);
            return -1;
        }

        if (FT_UNLIKELY(validate_args(sc, va->args[i], va->stack + i, va) <
                        0)) {
            return -1;
        }
    }

    for (; i < va->args_cnt && j != size; j++, i++) {
        sc = schemas[j];
        val = va->kw ? getter(va->kw, sc->name) : NULL;
        if (validate_args_getter(sc, val, i, va) < 0) {
            return -1;
        }
    }

    if (self->a_schema) {
        PyObject* name = self->a_schema->schema_base.name;
        TypeAdapter* vd = self->a_schema->validator;
        for (; i < va->nargs; i++) {
            PyObject* val = va->args[i];
            PyObject* tmp = TypeAdapter_Conversion(vd, va->ctx, val);
            if (!tmp) {
                if (FT_UNLIKELY(ValidationError_CreateAttrIdx(name,
                                                              i - va->args_cnt,
                                                              vd,
                                                              val,
                                                              va->ctx->model,
                                                              &va->err)) < 0) {
                    return -1;
                }
            }
            va->stack[i] = tmp;
        }
    }

    for (; j != size; j++, i++) {
        sc = schemas[j];
        val = va->kw ? getter(va->kw, sc->name) : NULL;
        if (FT_UNLIKELY(validate_args_getter(sc, val, i, va) < 0)) {
            return -1;
        }
    }
    return i;
}

static inline Py_ssize_t
validated_func_get_stack_size(ValidatedFunc* self,
                              Py_ssize_t nargs,
                              PyObject* kwnames)
{
    Py_ssize_t t_size = nargs;
    Py_ssize_t acnt = _VD_FUNC_GET_ACNT(self);
    t_size = Py_MAX(t_size, acnt);
    t_size += FUNC_GET_KWONLY_CNT(self->func);
    if (HAS_VARKEYWORDS(self->func) && kwnames) {
        t_size += Py_SIZE(kwnames);
    }
    return t_size;
}

static inline int
validated_func_get_kwnames(ValidatedFunc* self, vd_args* va, PyObject** kwnames)
{
    if (!va->kw || !HAS_VARKEYWORDS(self->func) || !VectorDict_Check(va->kw)) {
        *kwnames = Py_XNewRef(self->kwnames);
        return 0;
    }

    if (!self->kwnames) {
        *kwnames = Py_NewRef(va->kw);
        return 0;
    }

    PyObject* kwname = _CAST(_VectorDict*, va->kw)->kwnames;
    Py_ssize_t k_size = Py_SIZE(kwname);
    Py_ssize_t kw_knt = Py_SIZE(self->kwnames);
    PyObject* res = PyTuple_New(k_size + kw_knt);
    if (FT_UNLIKELY(!res)) {
        return -1;
    }

    for (Py_ssize_t i = 0; i != kw_knt; i++) {
        PyObject* val = PyTuple_GET_ITEM(self->kwnames, i);
        PyTuple_SET_ITEM(res, i, Py_NewRef(val));
    }

    for (Py_ssize_t i = 0; i != k_size; i++) {
        PyObject* val = PyTuple_GET_ITEM(kwname, i);
        if (_Tuple_GetName(self->kwnames, val) >= 0) {
            kw_knt--;
            continue;
        }
        PyTuple_SET_ITEM(res, kw_knt + i, Py_NewRef(val));
    }

    Py_SET_SIZE(res, k_size + kw_knt);
    *kwnames = res;
    return 0;
}

int
_ValidatedFunc_CallAndCheckResult(ValidatedFunc* self,
                                  PyObject** stack,
                                  Py_ssize_t stack_size,
                                  PyObject* kwnames,
                                  ValidateContext* ctx,
                                  PyObject** res)
{
    PyObject* func = (PyObject*)self->func;
    stack_size -= kwnames ? Py_SIZE(kwnames) : 0;
    PyObject* val = PyObject_Vectorcall(func, stack, stack_size, kwnames);
    if (FT_UNLIKELY(!val)) {
        return -1;
    }

    TypeAdapter* vd = self->r_validator;
    if (HAS_COROUTINE(self->func)) {
        *res = ValidatorIterable_CreateAsync(val, ctx, vd);
    } else {
        *res = TypeAdapter_Conversion(vd, ctx, val);
    }

    if (!*res) {
        int r = ValidationError_Raise(__return, vd, val, ctx->model);
        Py_DECREF(val);
        return r;
    }

    Py_DECREF(val);
    return 1;
}

static inline PyObject*
validated_func_call_and_check_result(ValidatedFunc* self,
                                     Py_ssize_t nargs,
                                     vd_args* va)
{
    PyObject* kwnames = NULL;
    if (validated_func_get_kwnames(self, va, &kwnames) < 0) {
        return NULL;
    }

    PyObject* res = NULL;
    _ValidatedFunc_CallAndCheckResult(
      self, va->stack, nargs, kwnames, va->ctx, &res);
    Py_XDECREF(kwnames);
    return res;
}

static inline int
validated_func_check_a_cnt(ValidatedFunc* self, vd_args* va)
{
    if (!IS_FAIL_ON_EXTRA_INIT(self->flags)) {
        return 1;
    }

    if (!HAS_VARARGS(self->func) &&
        !PyCheck_MaxArgs(_FUNC_GET_NAME(self), va->nargs, va->args_cnt)) {
        return 0;
    }

    if (!HAS_VARKEYWORDS(self->func) &&
        !HashTable_CheckExtraKwnames(
          self->map, self->schemas, va->kw, _FUNC_GET_NAME(self))) {
        return 0;
    }
    return 1;
}

static inline Py_ssize_t
validated_func_var_kwnames(ValidatedFunc* self, Py_ssize_t a_cnt, vd_args* va)
{
    if (!self->kw_schema || !va->kw) {
        return a_cnt;
    }

    Schema* sc = _CAST(Schema*, self->kw_schema);
    PyObject* kwname = _CAST(_VectorDict*, va->kw)->kwnames;
    Py_ssize_t kw_size = PyTuple_GET_SIZE(kwname);
    PyObject** kwnames = TUPLE_ITEMS(kwname);
    Py_ssize_t kw_ind = va->nargs;

    for (Py_ssize_t k = 0; k != kw_size; k++, kw_ind++) {
        if (_HashTable_Get(self->map, kwnames[k]) > -1) {
            continue;
        }

        if (FT_UNLIKELY(
              validate_args(sc, va->args[kw_ind], va->stack + a_cnt, va) < 0)) {
            return -1;
        }
        a_cnt++;
    }

    return a_cnt;
}

static PyObject*
validated_func_vector_call_ctx_nested(ValidatedFunc* self,
                                      ValidateContext* ctx,
                                      PyObject* kwnms,
                                      vd_args* va,
                                      InitGetter getter)
{
    PyObject* res = NULL;
    Py_ssize_t stack_size, a_cnt;

    stack_size = validated_func_get_stack_size(self, va->nargs, kwnms);
    va->stack = (PyObject**)Mem_New(stack_size * BASE_SIZE);
    if (FT_UNLIKELY(!va->stack)) {
        return NULL;
    }

    ctx->data =
      (PyObject*)_ArgsKwargs_Create(self, va->stack, va->nargs, kwnms);
    if (FT_UNLIKELY(!ctx->data)) {
        PyMem_Free(va->stack);
        return NULL;
    }

    a_cnt = validated_func_args_stack(self, va, getter);
    if (a_cnt < 0) {
        goto done;
    }

    if (kwnms) {
        a_cnt = validated_func_var_kwnames(self, a_cnt, va);
        if (a_cnt < 0) {
            goto done;
        }
    }

    if (va->err) {
        ValidationError_RaiseWithModel(va->err, ctx->model);
        va->err = NULL;
        goto done;
    }

    res = validated_func_call_and_check_result(self, a_cnt, va);

done:
    Py_XDECREF(va->err);
    _ArgsKwargs_Decref((ArgsKwargs*)ctx->data);
    _Stack_Decref(va->stack, stack_size);
    ctx->data = (PyObject*)self;
    return res;
}

static PyObject*
validated_func_vector_call_ctx(ValidatedFunc* self,
                               PyObject** args,
                               Py_ssize_t nargsf,
                               PyObject* kwnames,
                               ValidateContext* ctx)
{
    _VectorDict vd;
    PyObject* kw = NULL;
    if (kwnames) {
        vd = _VectorDict_Create(args, nargsf, kwnames);
        kw = (PyObject*)&vd;
    }

    vd_args va = {
        .nargs = PyVectorcall_NARGS(nargsf),
        .args_cnt = _VD_FUNC_GET_ACNT(self),
        .stack = NULL,
        .args = args,
        .err = NULL,
        .ctx = ctx,
        .kw = kw,
    };

    if (FT_UNLIKELY(!validated_func_check_a_cnt(self, &va))) {
        return NULL;
    }

    return validated_func_vector_call_ctx_nested(
      self, ctx, kwnames, &va, _VectorDict_Get);
}

static PyObject*
validated_func_vector_call(ValidatedFunc* self,
                           PyObject** args,
                           size_t nargsf,
                           PyObject* kwn)
{
    ContextManager* ctx = self->head.ctx;
    ValidateContext vctx = _ValidatedFunc_GetCtx(self, ctx);
    return validated_func_vector_call_ctx(self, args, nargsf, kwn, &vctx);
}

PyObject*
_ValidatedFunc_GetName(ValidatedFunc* self)
{
    if (!self->func) {
        return PyObject_Get__name__(Py_TYPE(self));
    }
    return Py_XNewRef(FUNC_GET_NAME(self));
}

static int
validated_func_set_kwnames(ValidatedFunc* self)
{
    Py_ssize_t kwonly = FUNC_GET_KWONLY_CNT(self->func);
    if (!kwonly) {
        return 0;
    }

    self->kwnames = PyTuple_New(kwonly);
    if (FT_UNLIKELY(!self->kwnames)) {
        return -1;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(self->schemas);
    for (Py_ssize_t j = 0; j < kwonly; ++j) {
        Schema* sc = (Schema*)PyTuple_GET_ITEM(self->schemas, size - j - 1);
        PyTuple_SET_ITEM(self->kwnames, j, Py_NewRef(sc->name));
    }
    return 0;
}

static inline PyObject*
validate_func_get_varnames(PyFunctionObject* func)
{
    PyObject* co_varnames =
      PyObject_GetAttrString(func->func_code, "co_varnames");
    if (FT_UNLIKELY(!co_varnames)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyTuple_Check(co_varnames))) {
        _RaiseInvalidType(
          "co_varnames", "tuple", Py_TYPE(co_varnames)->tp_name);
        Py_DECREF(co_varnames);
        return NULL;
    }
    return co_varnames;
}

static inline Py_ssize_t
validated_func_get_acnt(PyFunctionObject* func)
{
    return _FUNC_GET_ACNT(func) + FUNC_GET_KWONLY_CNT(func);
}

static inline int
validated_func_set_return_validator(ValidatedFunc* self, PyObject* annot)
{
    PyObject* r_hint = Dict_GetItemNoError(annot, __return);
    if (!r_hint) {
        r_hint = PyAny;
    }

    self->r_validator = ParseHint(r_hint, NULL);
    return self->r_validator ? 0 : -1;
}

static inline PyObject*
validate_get_args_default(PyFunctionObject* func, PyObject* co_varnames)
{
    PyObject* res = PyDict_New();
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (!func->func_defaults) {
        return res;
    }

    Py_ssize_t cnt = validated_func_get_acnt(func);
    Py_ssize_t defaults_cnt = PyTuple_GET_SIZE(func->func_defaults);
    Py_ssize_t st = cnt - defaults_cnt;
    for (Py_ssize_t i = st; i != cnt; i++) {
        PyObject* name = PyTuple_GET_ITEM(co_varnames, i);
        PyObject* val = PyTuple_GET_ITEM(func->func_defaults, i - st);
        if (FT_UNLIKELY(PyDict_SetItem(res, name, val) < 0)) {
            Py_DECREF(res);
            return NULL;
        }
    }
    return res;
}

static inline PyObject*
validate_get_default(PyFunctionObject* func, PyObject* co_varnames)
{
    PyObject* res = validate_get_args_default(func, co_varnames);
    PyObject* kwdefaults = func->func_kwdefaults;
    if (kwdefaults && PyDict_Update(res, kwdefaults) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static inline PyObject*
validate_func_get_hint(PyObject* annot, PyObject* name)
{
    PyObject* hint = Dict_GetItemNoError(annot, name);
    return hint ? hint : PyAny;
}

static inline ValidSchema*
create_schema_by_annot(PyObject* annot, PyObject* name)
{
    PyObject* hint = validate_func_get_hint(annot, name);
    return ValidSchema_Create(
      name, hint, DefaultFieldVFuncNoInit, NULL, NULL, DefaultConfigValid);
}

static inline PyObject*
validate_func_get_annot(ValidatedFunc* self,
                        PyObject* annot,
                        PyObject* co_varnames,
                        PyFunctionObject* func)
{
    PyObject* res = PyDict_New();
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    PyObject *name, *hint;
    Py_ssize_t cnt = validated_func_get_acnt(func);

    if (HAS_VARARGS(func)) {
        self->a_schema =
          create_schema_by_annot(annot, PyTuple_GET_ITEM(co_varnames, cnt));
        if (!self->a_schema) {
            goto error;
        }
    }

    if (HAS_VARKEYWORDS(func)) {
        self->kw_schema = create_schema_by_annot(
          annot, PyTuple_GET_ITEM(co_varnames, cnt + HAS_VARARGS(func)));
        if (!self->kw_schema) {
            goto error;
        }
    }

    for (Py_ssize_t i = 0; i != cnt; i++) {
        name = PyTuple_GET_ITEM(co_varnames, i);
        hint = validate_func_get_hint(annot, name);
        if (PyDict_SetItem(res, name, hint) < 0) {
            goto error;
        }
    }

    return res;

error:
    Py_DECREF(res);
    return NULL;
}

static inline int
validated_func_set_schema(ValidatedFunc* self, PyObject* annot)
{
    PyObject* varnames = validate_func_get_varnames(self->func);
    if (FT_UNLIKELY(!varnames)) {
        return -1;
    }

    PyObject* new_annot =
      validate_func_get_annot(self, annot, varnames, self->func);
    if (FT_UNLIKELY(!new_annot)) {
        Py_DECREF(varnames);
        return -1;
    }

    PyObject* defaults = validate_get_default(self->func, varnames);
    Py_DECREF(varnames);
    if (FT_UNLIKELY(!defaults)) {
        Py_DECREF(new_annot);
        return -1;
    }

    self->schemas = _ValidatedFunc_CreateSchema(new_annot,
                                                _FUNC_GET_ACNT(self->func) +
                                                  HAS_VARARGS(self->func),
                                                defaults);
    Py_DECREF(defaults);
    Py_DECREF(new_annot);
    return self->schemas ? 0 : -1;
}

static int
validated_func_parse_new_kw(PyObject* const* args,
                            PyObject* kwnames,
                            uint32_t* flags)
{
    *flags = FIELD_ALLOW_INF_NAN;
    if (!kwnames) {
        return 1;
    }

    PyObject* buff[4] = { NULL };
    static const char* const kwlist[] = {
        "fail_on_extra_init", "allow_inf_nan", "num_to_str", "strict", NULL
    };
    static _PyArg_Parser _parser = {
        .fname = "validated_func",
        .keywords = kwlist,
        .kwtuple = NULL,
    };

    if (!PyArg_UnpackKeywords(args,
                              0,
                              NULL,
                              kwnames,
                              &_parser,
                              0, /*minpos*/
                              0, /*maxpos*/
                              0, /*minkw*/
                              buff)) {
        return 0;
    }

    for (Py_ssize_t i = 0; i != 4; i++) {
        if (!_ValidateArg(buff[i], &PyBool_Type, kwlist[i])) {
            return 0;
        }
    }

    uint32_t f = buff[0] == Py_True ? FAIL_ON_EXTRA_INIT : 0;
    if (buff[1] != Py_False) {
        f |= FIELD_ALLOW_INF_NAN;
    }

    if (buff[2] == Py_True) {
        f |= FIELD_NUM_TO_STR;
    }

    if (buff[3] == Py_True) {
        f |= FIELD_STRICT;
    }

    *flags = f;
    return 1;
}

static int
validated_func_parse_new(PyObject* const* args,
                         size_t nargsf,
                         PyObject* kwnames,
                         PyFunctionObject** func,
                         uint32_t* flags)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    if (nargs == 1) {
        if (!_ValidateArg((PyObject*)*args, &PyFunction_Type, "func")) {
            return 0;
        }
        *func = (PyFunctionObject*)*args;
        return validated_func_parse_new_kw(args + 1, kwnames, flags);
    }

    if (FT_UNLIKELY(!PyCheck_ArgsCnt("validated_func", nargs, 0))) {
        return 0;
    }

    *func = NULL;
    return validated_func_parse_new_kw(args, kwnames, flags);
}

static PyObject*
validate_func_call_deferred_create(ValidatedFunc* self,
                                   PyObject** args,
                                   Py_ssize_t nargsf,
                                   PyObject* kwnames)
{
    PyFunctionObject* func = (PyFunctionObject*)_VectorCall_GetOneArg(
      "validated_func", args, nargsf, kwnames);
    if (FT_UNLIKELY(!func)) {
        return NULL;
    }

    if (FT_UNLIKELY(!_ValidateArg((PyObject*)func, &PyFunction_Type, "func"))) {
        return NULL;
    }
    return ValidatedFunc_Create(Py_TYPE(self), func, self->flags, self->gtypes);
}

static PyObject*
validate_func_deferred_create(PyTypeObject* cls,
                              uint32_t flags,
                              PyObject* gtypes)
{
    ValidatedFunc* self = (ValidatedFunc*)cls->tp_alloc(cls, 0);
    if (FT_LIKELY(self)) {
        self->flags = flags;
        self->gtypes = Py_XNewRef(gtypes);
        self->vectorcall = (vectorcallfunc)validate_func_call_deferred_create;
    }
    return (PyObject*)self;
}

static int
validated_func_create_varnames(ValidatedFunc* self)
{
    Py_ssize_t ind = 0, size = VD_FUNC_GET_SIZE(self);
    self->varnames = PyTuple_New(size);
    if (FT_UNLIKELY(!self->varnames)) {
        return -1;
    }

    _SchemaForeach(sc, self->schemas)
    {
        PyTuple_SET_ITEM(self->varnames, ind++, Py_NewRef(SCHEMA_GET_NAME(sc)));
    }
    return 0;
}

PyObject*
ValidatedFunc_Create(PyTypeObject* type,
                     PyFunctionObject* func,
                     uint32_t flags,
                     PyObject* gtypes)
{
    if (!func) {
        return validate_func_deferred_create(type, flags, gtypes);
    }

    PyObject* annot = PyFunction_GetAnnotations((PyObject*)func);
    if (FT_UNLIKELY(!annot)) {
        ATTRIBUT_ERROR(func, "__annotations__");
        return NULL;
    }

    ValidatedFunc* self = (ValidatedFunc*)type->tp_alloc(type, 0);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    self->flags = flags;
    self->func = (PyFunctionObject*)Py_NewRef(func);

    if (validated_func_set_return_validator(self, annot) < 0) {
        goto error;
    }

    if (validated_func_set_schema(self, annot) < 0) {
        goto error;
    }

    if (validated_func_set_kwnames(self) < 0) {
        goto error;
    }

    self->map = HashTable_Create(self->schemas, 1);
    if (!self->map) {
        goto error;
    }

    self->vectorcall = (vectorcallfunc)validated_func_vector_call;
    self->gtypes = gtypes ? Py_NewRef(gtypes)
                          : _Object_Gettr((PyObject*)func, __type_params__);
    self->head.ctx = ContextManager_CREATE(self);
    if (!self->head.ctx) {
        goto error;
    }

    if (validated_func_create_varnames(self) < 0) {
        goto error;
    }

    return (PyObject*)self;

error:
    Py_XDECREF(self);
    return NULL;
}

static PyObject*
validated_func_new(PyTypeObject* type,
                   PyObject* const* args,
                   size_t nargsf,
                   PyObject* kwnames)
{
    PyFunctionObject* func;
    uint32_t flags;
    if (!validated_func_parse_new(args, nargsf, kwnames, &func, &flags)) {
        return NULL;
    }
    return ValidatedFunc_Create(type, func, flags, NULL);
}

static PyObject*
validated_func_from_json(ValidatedFunc* self,
                         PyObject** args,
                         size_t nargs,
                         PyObject* kwnames)
{
    if (!validated_func_is_init(self)) {
        return NULL;
    }

    Py_ssize_t cnt = PyVectorcall_NARGS(nargs);
    if (!PyCheck_ArgsCnt(".from_json", cnt, 1)) {
        return NULL;
    }

    PyObject* obj = (PyObject*)*args;
    ContextManager* ctx = self->head.ctx;
    return JsonValidParse_ValidatedFunc(self, obj, ctx, args + 1, kwnames);
}

static PyObject*
sequence_set_key(ContextManager* ctx,
                 PyObject** args,
                 Py_ssize_t nargsf,
                 PyObject* kwnames)
{
    int ft;
    uint32_t flags;
    PyFunctionObject* func;
    nargsf = Ctx_NARGS(nargsf, &ft);
    if (!validated_func_parse_new(args, nargsf, kwnames, &func, &flags)) {
        return NULL;
    }

    PyTypeObject* cls = _CAST(PyTypeObject*, ctx->model);
    return ValidatedFunc_Create(cls, func, flags, ctx->gtypes);
}

inline ValidateContext
_ValidatedFunc_GetCtx(ValidatedFunc* self, ContextManager* ctx)
{
    return ValidateCtx_Create(
      ctx, self, self, ctx, self->flags & _VALIDATE_FLAGS);
}

static PyObject*
validated_func_from_attributes_nested(ValidatedFunc* self,
                                      PyObject* obj,
                                      ValidateContext* vctx)
{
    vd_args va = {
        .args_cnt = _VD_FUNC_GET_ACNT(self),
        .stack = NULL,
        .ctx = vctx,
        .args = NULL,
        .err = NULL,
        .nargs = 0,
        .kw = obj,
    };
    return validated_func_vector_call_ctx_nested(
      self,
      vctx,
      self->varnames,
      &va,
      PyDict_Check(obj) ? _Dict_GetAscii : _Object_Gettr);
}

static PyObject*
validated_func_from_attributes(ValidatedFunc* self, PyObject* obj)
{
    ValidateContext vctx = _ValidatedFunc_GetCtx(self, self->head.ctx);
    return validated_func_from_attributes_nested(self, obj, &vctx);
}

static PyObject*
validated_func_from_subscript(PyTypeObject* cls, PyObject* key)
{
    PyObject* gtypes;
    if (PyTuple_Check(key)) {
        gtypes = Py_NewRef(key);
    } else {
        gtypes = PyTuple_Pack(1, key);
        if (!gtypes) {
            return NULL;
        }
    }
    PyObject* res = (PyObject*)_ContextManager_CreateGetItem(
      (PyObject*)cls, gtypes, key, sequence_set_key, NULL);
    Py_DECREF(gtypes);
    return res;
}

static inline PyObject*
validated_func_call_frost_validate(ContextManager* ctx,
                                   PyObject** args,
                                   Py_ssize_t nargs,
                                   PyObject* kwnames)
{
    int ft;
    nargs = Ctx_NARGS(nargs, &ft);
    ValidatedFunc* self = _CAST(ValidatedFunc*, ctx->model);
    ValidateContext vctx = _ValidatedFunc_GetCtx(self, ctx);
    if (ft) {
        return validated_func_from_attributes_nested(self, *args, &vctx);
    }
    return validated_func_vector_call_ctx(self, args, nargs, kwnames, &vctx);
}

static PyObject*
validated_func_ctx_from_json(ContextManager* ctx,
                             PyObject* obj,
                             PyObject** args,
                             PyObject* kwnames)
{
    ValidatedFunc* self = _CAST(ValidatedFunc*, ctx->model);
    return JsonValidParse_ValidatedFunc(self, obj, ctx, args, kwnames);
}

static PyObject*
validated_func_get_item(ValidatedFunc* self, PyObject* key)
{
    if (FT_UNLIKELY(!validated_func_is_init(self))) {
        return NULL;
    }

    return _ContextManager_CreateGetItem((PyObject*)self,
                                         self->gtypes,
                                         key,
                                         validated_func_call_frost_validate,
                                         validated_func_ctx_from_json);
}

static PyObject*
validated_func_json_schema(ValidatedFunc* self)
{
    return validated_func_is_init(self) ? Schema_JsonSchema((PyObject*)self)
                                        : NULL;
}

static PyObject*
get_flag(ValidatedFunc* self, uint32_t flags)
{
    return Py_NewRef((self->flags & flags) ? Py_True : Py_False);
}

static PyMappingMethods validated_func_map_methods = {
    .mp_subscript = (binaryfunc)validated_func_get_item,
};

static PyGetSetDef validated_func_getsets[] = {
    { "fail_on_extra_init",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FAIL_ON_EXTRA_INIT) },
    { "allow_inf_nan",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_ALLOW_INF_NAN) },
    { "num_to_str",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_NUM_TO_STR) },
    { "strict", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_STRICT) },
    { NULL },
};

static PyMethodDef validated_func_methods[] = {
    { "from_attributes",
      PY_METHOD_CAST(validated_func_from_attributes),
      METH_O,
      NULL },
    { "__class_getitem__",
      PY_METHOD_CAST(validated_func_from_subscript),
      METH_CLASS | METH_O | METH_COEXIST,
      NULL },
    { "json_schema",
      PY_METHOD_CAST(validated_func_json_schema),
      METH_NOARGS,
      NULL },
    { "from_json",
      PY_METHOD_CAST(validated_func_from_json),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "from_db_row", PY_METHOD_CAST(Object_FromDbRow), METH_FASTCALL, NULL },
    { NULL }
};

static PyMemberDef validated_func_members[] = {
    { "__func__", T_OBJECT, offsetof(ValidatedFunc, func), READONLY, NULL },
    { "__schemas__",
      T_OBJECT,
      offsetof(ValidatedFunc, schemas),
      READONLY,
      NULL },
    { NULL }
};

PyTypeObject ValidatedFuncType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL | Py_TPFLAGS_HAVE_GC,
    .tp_vectorcall_offset = offsetof(ValidatedFunc, vectorcall),
    .tp_traverse = (traverseproc)validated_func_traverse,
    .tp_vectorcall = (vectorcallfunc)validated_func_new,
    .tp_descr_get = (descrgetfunc)validated_func_get,
    .tp_as_mapping = &validated_func_map_methods,
    .tp_str = (reprfunc)_ValidatedFunc_GetName,
    .tp_dealloc = (destructor)_Object_Dealloc,
    .tp_clear = (inquiry)validated_func_clear,
    .tp_repr = (reprfunc)validated_func_repr,
    .tp_name = "frost_typing.validated_func",
    .tp_basicsize = sizeof(ValidatedFunc),
    .tp_methods = validated_func_methods,
    .tp_members = validated_func_members,
    .tp_getset = validated_func_getsets,
    .tp_alloc = PyType_GenericAlloc,
    .tp_call = PyVectorcall_Call,
    .tp_free = PyObject_GC_Del,
};

static int
args_kwargs_clear(ArgsKwargs* self)
{
    Py_CLEAR(self->args_tuple);
    Py_CLEAR(self->kwargs);
    Py_CLEAR(self->model);
    return 0;
}

static int
args_kwargs_traverse(ArgsKwargs* self, visitproc visit, void* arg)
{
    Py_VISIT(self->args_tuple);
    Py_VISIT(self->kwargs);
    Py_VISIT(self->model);
    return 0;
}

ArgsKwargs*
_ArgsKwargs_Create(ValidatedFunc* model,
                   PyObject** args,
                   Py_ssize_t nargs,
                   PyObject* kwnames)
{
    ArgsKwargs* self = Object_New(ArgsKwargs, &ArgsKwargsType);
    if (self) {
        self->model = (ValidatedFunc*)Py_NewRef(model);
        self->nargs = PyVectorcall_NARGS(nargs);
        self->kwnames = kwnames;
        self->args = args;
    }
    return self;
}

inline void
_ArgsKwargs_Decref(ArgsKwargs* self)
{
    if (Py_REFCNT(self) != 1) {
        args_kwargs_finish(self);
    }
    Py_DECREF(self);
}

int
args_kwargs_finish(ArgsKwargs* self)
{
    if (self->args_tuple) {
        return 0;
    }

    self->args_tuple = PyTuple_New(self->nargs);
    if (!self->args_tuple) {
        return -1;
    }

    Py_ssize_t real_size = 0;
    for (Py_ssize_t i = 0; i != self->nargs; i++) {
        PyObject* val = self->args[i];
        if (!val) {
            continue;
        }

        real_size++;
        PyTuple_SET_ITEM(self->args_tuple, i, Py_NewRef(val));
    }

    if (real_size != self->nargs &&
        _PyTuple_Resize(&self->args_tuple, real_size) < 0) {
        self->nargs = 0;
        self->args = NULL;
        self->kwnames = NULL;
        return -1;
    }

    if (!self->kwnames) {
        goto done;
    }

    self->kwargs = PyDict_New();
    if (!self->kwargs) {
        return -1;
    }

    for (Py_ssize_t i = 0; i != Py_SIZE(self->kwnames); i++) {
        PyObject* val = self->args[self->nargs + i];
        if (!val) {
            continue;
        }
        PyObject* name = PyTuple_GET_ITEM(self->kwnames, i);
        if (Dict_SetItem_String(self->kwargs, name, val) < 0) {
            return -1;
        }
    }

done:
    self->nargs = 0;
    self->args = NULL;
    self->kwnames = NULL;
    return 0;
}

static int
args_kwargs_getattro_nested(ArgsKwargs* self, PyObject* string, PyObject** res)
{
    if (!self->args) {
        return 0;
    }

    /* try to get in kwargs */
    Py_ssize_t ind = _Tuple_GetName(self->kwnames, string);
    if (ind != -1) {
        *res = Py_XNewRef(self->args[self->nargs + ind]);
        if (*res) {
            return 1;
        }
    }

    /* try to get in **args */
    Py_ssize_t offset = _HashTable_Get(self->model->map, string);
    if (offset < 0) {
        return 0;
    }

    ind = offset / BASE_SIZE;
    if (ind >= self->nargs) {
        return 0;
    }

    *res = Py_XNewRef(self->args[ind]);
    if (*res) {
        return 1;
    }

    Schema* sc = SCHEMA_BY_OFFSET(self->model->schemas, offset);
    return _DataModel_SetDefault(sc->field, res);
}

static PyObject*
args_kwargs_getattro(PyObject* self, PyObject* string)
{
    if (PyUnicode_Check(string)) {
        PyObject* res = NULL;
        if (args_kwargs_getattro_nested((ArgsKwargs*)self, string, &res)) {
            return res;
        }
    }
    return PyObject_GenericGetAttr((PyObject*)self, string);
}

static PyObject*
args_kwargs_new(PyTypeObject* tp, PyObject* args, PyObject* kwargs)
{
    PyObject *args_tuple, *kw = Py_None;
    char* kwlist[] = { "args", "kwargs", NULL };
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "O!|O:ArgsKwargs.__new__",
                                     kwlist,
                                     &PyTuple_Type,
                                     &args_tuple,
                                     &kw)) {
        return NULL;
    }

    if (kw != Py_None && !PyDict_Check(kw)) {
        _RaiseInvalidType("kwargs", "dict or None", Py_TYPE(kw)->tp_name);
        return NULL;
    }

    ArgsKwargs* self = Object_New(ArgsKwargs, tp);
    if (self) {
        self->args_tuple = Py_NewRef(args_tuple);
        self->kwargs = kw == Py_None ? NULL : Py_NewRef(kw);
    }
    return (PyObject*)self;
}

static int
asrgs_kwargs_eq_kwargs(PyObject* self_kwargs, PyObject* other_kwargs)
{
    if (self_kwargs && other_kwargs) {
        return PyObject_RichCompareBool(self_kwargs, other_kwargs, Py_EQ);
    }
    if (self_kwargs == other_kwargs) {
        return 1;
    }
    return 0;
}

static PyObject*
args_kwargs_richcompare(ArgsKwargs* self, ArgsKwargs* other, int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    if (Py_TYPE(other) != Py_TYPE(self)) {
        return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
    }

    if (args_kwargs_finish(self) < 0 || args_kwargs_finish(other) < 0) {
        return NULL;
    }

    int r =
      PyObject_RichCompareBool(self->args_tuple, other->args_tuple, Py_EQ);
    if (r < 0) {
        return NULL;
    }

    if (!r) {
        return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
    }

    r = asrgs_kwargs_eq_kwargs(self->kwargs, other->kwargs);
    if (r < 0) {
        return NULL;
    }

    if (op == Py_NE) {
        r = !r;
    }
    return Py_NewRef(r ? Py_True : Py_False);
}

static PyObject*
args_kwargs_repr(ArgsKwargs* self)
{
    if (args_kwargs_finish(self) < 0) {
        return NULL;
    }
    if (self->kwargs) {
        return PyUnicode_FromFormat(
          "ArgsKwargs(args=%R, kwargs=%R)", self->args_tuple, self->kwargs);
    }
    return PyUnicode_FromFormat("ArgsKwargs(args=%R)", self->args_tuple);
}

static PyObject*
args_kwargs_as_dict(ArgsKwargs* self)
{
    if (args_kwargs_finish(self) < 0) {
        return NULL;
    }

    PyObject* res = PyDict_New();
    if (!res) {
        return NULL;
    }

    if (Dict_SetItem_String(res, __args, self->args_tuple) < 0) {
        Py_DECREF(res);
        return NULL;
    }

    if (Dict_SetItem_String(res, __kwargs, self->kwargs) < 0) {
        Py_DECREF(res);
        return NULL;
    }

    return res;
}

static PyObject*
args_kwargs_get(ArgsKwargs* self, Py_ssize_t offset)
{
    if (args_kwargs_finish(self) < 0) {
        return NULL;
    }
    PyObject* res = GET_OBJ(self, offset);
    return Py_NewRef(res ? res : Py_None);
}

static PyMethodDef args_kwargs_methods[] = {
    { "__as_json__", PY_METHOD_CAST(args_kwargs_repr), METH_NOARGS, NULL },
    { "__as_dict__", PY_METHOD_CAST(args_kwargs_as_dict), METH_NOARGS, NULL },
    { "__copy__", PY_METHOD_CAST(PyObject_SelfIter), METH_NOARGS, NULL },
    { NULL }
};

static PyGetSetDef args_kwargs_getsets[] = {
    { "args",
      PY_GETTER_CAST(args_kwargs_get),
      NULL,
      NULL,
      (void*)(offsetof(ArgsKwargs, args_tuple)) },
    { "kwargs",
      PY_GETTER_CAST(args_kwargs_get),
      NULL,
      NULL,
      (void*)(offsetof(ArgsKwargs, kwargs)) },
    { NULL }
};

PyTypeObject ArgsKwargsType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_richcompare = (richcmpfunc)args_kwargs_richcompare,
    .tp_traverse = (traverseproc)args_kwargs_traverse,
    .tp_dealloc = (destructor)_Object_Dealloc,
    .tp_clear = (inquiry)args_kwargs_clear,
    .tp_repr = (reprfunc)args_kwargs_repr,
    .tp_name = "frost_typing.ArgsKwargs",
    .tp_getattro = args_kwargs_getattro,
    .tp_basicsize = sizeof(ArgsKwargs),
    .tp_methods = args_kwargs_methods,
    .tp_getset = args_kwargs_getsets,
    .tp_free = PyObject_GC_Del,
    .tp_new = args_kwargs_new,
};

int
validated_func_setup(void)
{
    if (PyType_Ready(&ArgsKwargsType) < 0) {
        return -1;
    }
    return PyType_Ready(&ValidatedFuncType);
}

void
validated_func_free(void)
{
}