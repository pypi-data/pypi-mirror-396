#include "data_model.h"
#include "field.h"
#include "hash_table.h"
#include "meta_valid_model.h"
#include "valid_model.h"
#include "validated_func.h"
#include "validator/validator.h"
#include "validator/validator_uuid.h"
#include "vector_dict.h"
#include "json/json.h"

typedef PyObject* (*create)(PyObject*);
typedef int (*append)(PyObject*, PyObject*);
typedef PyObject* (*parse_dt)(char*, Py_ssize_t, int);
typedef int (*parse_v_f)(PyObject* self,
                         ContextManager* ctx,
                         ReadBuffer* buff,
                         PyObject** res,
                         PyObject** args,
                         PyObject* kwnames);

static int
json_valid_raise(ReadBuffer* buff, PyObject* model)
{
    if (PyErr_Occurred()) {
        return ValidationError_RaiseInvalidJson(buff->obj, model);
    }

    Py_ssize_t line, column;
    ReadBuffer_GetPos(buff, &column, &line);
    char ch = buff->iter[buff->iter == buff->end_data ? -1 : 0];
    return ValidationError_RaiseFormat(
      "Invalid JSON: line %zu column %zu (char '%c')",
      NULL,
      __json_invalid_type,
      buff->obj,
      model,
      line,
      column,
      ch);
}

static int
json_valid_check_end(ReadBuffer* buff, PyObject* model)
{
    if (FT_UNLIKELY(_JsonParse_CheckEnd(buff) < 0)) {
        json_valid_raise(buff, model);
        return -1;
    }
    return 0;
}

static inline int
json_valid_validate_ind(TypeAdapter* vd,
                        PyObject* val,
                        ValidateContext* ctx,
                        Py_ssize_t ind,
                        PyObject** res,
                        ValidationError** err)
{
    *res = TypeAdapter_Conversion(vd, ctx, val);
    return *res ? 1
                : ValidationError_IndexCreate(ind, vd, val, ctx->model, err);
}

static inline int
json_parse_continue(unsigned char ch)
{
    return _JsonParse_Router[ch] == _JsonParse_Continue;
}

static inline int
deserialize_array(ReadBuffer* buff,
                  PyObject* res,
                  TypeAdapter* vd,
                  ValidateContext* ctx,
                  append add)
{
    Py_ssize_t ind = 0;
    Py_ssize_t cnt_sep = 0;
    ValidationError* err = NULL;
    for (buff->iter++; buff->iter != buff->end_data; buff->iter++) {
        unsigned char ch = (unsigned char)*buff->iter;
        if (json_parse_continue(ch)) {
            continue;
        } else if (ch == ',') {
            if (++cnt_sep == ind) {
                continue;
            }
            goto error;
        } else if (ch == ']') {
            if (!(cnt_sep && ind) || cnt_sep == (ind - 1)) {
                buff->iter++;
                if (FT_UNLIKELY(err)) {
                    ValidationError_RaiseWithModel(err, ctx->model);
                    return 0;
                }
                return 1;
            }
            goto error;
        }

        PyObject* tmp = NULL;
        int r = vd->json_parser(vd, buff, ctx, &tmp);
        buff->iter--;
        if (r < 0) {
            goto error;
        } else if (!r) {
            if (FT_UNLIKELY(
                  _ValidationErrorSetNestedInd(ind, ctx->model, &err) < 0)) {
                goto error;
            }
            continue;
        }

        r = add(res, tmp);
        Py_DECREF(tmp);
        ind++;
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

error:
    Py_XDECREF(err);
    return -1;
}

static int
json_valid_parse_array(TypeAdapter* vd,
                       ReadBuffer* buff,
                       ValidateContext* ctx,
                       PyObject** res,
                       create new,
                       append add)
{
    if (*buff->iter != '[') {
        return _JsonValidParse(vd, buff, ctx, res);
    }

    if (FT_UNLIKELY(_Decode_Enter(buff) < 0)) {
        return -1;
    }

    *res = NULL;
    PyObject* arr = new(NULL);
    if (FT_UNLIKELY(!arr)) {
        return -1;
    }

    int r =
      deserialize_array(buff, arr, _CAST(TypeAdapter*, vd->args), ctx, add);
    _Decode_Leave(buff);
    if (r != 1) {
        Py_DECREF(arr);
        return r;
    }
    *res = arr;
    return 1;
}

static inline int
json_valid_by_schema_override(PyObject* schema,
                              PyObject** stack,
                              _VectorDict* kw,
                              ValidateContext* ctx,
                              ValidationError* err)
{
    _SchemaForeach(sc, schema, stack++)
    {
        PyObject* val = *stack;
        if (val) {
            // skipping err
            if (FT_LIKELY(val == _PySet_Dummy ||
                          !_IS_FIELD_DISCRIMINATOR(sc->field->flags))) {
                continue;
            }

            if (FT_UNLIKELY(
                  ValidSchema_ValidateInit(sc, val, stack, ctx, &err) < 0)) {
                goto error;
            }
            continue;
        }

        // override?
        if (kw) {
            PyObject* o = _VectorDict_Get((PyObject*)kw, SCHEMA_GET_NAME(sc));
            if (o) {
                if (FT_UNLIKELY(
                      ValidSchema_ValidateInit(sc, o, stack, ctx, &err) < 0)) {
                    goto error;
                }
                continue;
            }
        }

        int r = _DataModel_SetDefault(sc->field, stack);
        if (r) {
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            continue;
        }

        if (FT_UNLIKELY(!IS_FIELD_INIT(sc->field->flags) &&
                        ValidationError_CreateMissing(
                          SCHEMA_GET_NAME(sc), NULL, ctx->model, &err) < 0)) {
            goto error;
        }
    }

    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx->model);
        return 0;
    }
    return 1;

error:
    Py_XDECREF(err);
    return -1;
}

static int
skip_parse(ReadBuffer* buff)
{
    PyObject* skip = _JsonParse(buff);
    if (!skip) {
        return -1;
    }
    Py_DECREF(skip);
    return 0;
}

static int
json_valid_parse_by_schema(PyObject* schema,
                           PyObject** stack,
                           HashTable* map,
                           ReadBuffer* buff,
                           ValidateContext* ctx,
                           _VectorDict* kw)
{
    if (FT_UNLIKELY(_Decode_Enter(buff) < 0)) {
        return -1;
    }

    PyObject* key = NULL;
    uint8_t expect_key = 1;
    ValidationError* err = NULL;
    Py_ssize_t cnt_sep = 0, dict_size = 0;

    for (buff->iter++; buff->iter != buff->end_data; buff->iter++) {
        unsigned char ch = (unsigned char)*buff->iter;
        if (FT_UNLIKELY(json_parse_continue(ch))) {
            continue;
        }

        if (FT_UNLIKELY(ch == ':')) {
            if (FT_LIKELY(expect_key && key)) {
                expect_key = 0;
                continue;
            }
            goto error;
        }

        if (FT_UNLIKELY(ch == ',')) {
            if (FT_LIKELY(!expect_key && !key && (++cnt_sep == dict_size))) {
                expect_key = 1;
                continue;
            }
            goto error;
        }

        if (FT_UNLIKELY(ch == '}')) {
            if (FT_LIKELY(!key &&
                          ((expect_key && !cnt_sep && !dict_size) ||
                           (!expect_key && cnt_sep == (dict_size - 1))))) {
                buff->iter++;
                _Decode_Leave(buff);
                return json_valid_by_schema_override(
                  schema, stack, kw, ctx, err);
            }
            goto error;
        }

        if (expect_key) {
            if (FT_UNLIKELY(key)) {
                goto error;
            }

            key = JsonParse_StringKey(buff);
            if (FT_UNLIKELY(!key)) {
                goto error;
            }
            buff->iter--;
            continue;
        } else if (FT_UNLIKELY(!key)) {
            goto error;
        }

        dict_size++;
        const Py_ssize_t field_offset = _HashTable_Get(map, key);
        Py_DECREF(key);
        key = NULL;
        if (FT_UNLIKELY(field_offset < 0)) {
            if (FT_UNLIKELY(skip_parse(buff) < 0)) {
                goto error;
            }
            buff->iter--;
            continue;
        }

        Schema* sc = SCHEMA_BY_OFFSET(schema, field_offset);
        if (FT_UNLIKELY(!IS_FIELD_INIT(sc->field->flags))) {
            if (FT_UNLIKELY(skip_parse(buff) < 0)) {
                goto error;
            }
            buff->iter--;
            continue;
        }

        PyObject* field_val = NULL;
        PyObject* kw_val =
          kw ? _VectorDict_Get((PyObject*)kw, SCHEMA_GET_NAME(sc)) : NULL;
        if (FT_UNLIKELY(kw_val)) {
            if (skip_parse(buff) < 0) {
                Py_DECREF(kw_val);
                goto error;
            }

            if (FT_LIKELY(!_IS_FIELD_DISCRIMINATOR(sc->field->flags))) {
                int r =
                  ValidSchema_ValidateInit(sc, kw_val, &field_val, ctx, &err);
                Py_DECREF(kw_val);
                if (FT_UNLIKELY(r < 0)) {
                    goto error;
                }
            } else {
                field_val = kw_val;
            }
        } else {
            if (FT_UNLIKELY(_IS_FIELD_DISCRIMINATOR(sc->field->flags))) {
                field_val = _JsonParse(buff);
                if (FT_UNLIKELY(!field_val)) {
                    goto error;
                }
            } else {
                TypeAdapter* vd = _Schema_GET_VALIDATOR(sc);
                int res = vd->json_parser(vd, buff, ctx, &field_val);
                if (res < 0 ||
                    (!res &&
                     _ValidationErrorSetNested(
                       SCHEMA_GET_NAME(sc), NULL, ctx->model, &err) < 0)) {
                    goto error;
                }
            }
        }

        /* If, as a result of validation, field_val = NULL, a special value is
         * set to avoid raise missing. */
        if (FT_UNLIKELY(!field_val)) {
            field_val = Py_NewRef(_PySet_Dummy);
        }

        buff->iter--;
        *GET_ADDR(stack, field_offset) = field_val;
    }

error:
    Py_XDECREF(key);
    Py_XDECREF(err);
    return -1;
}

static inline int
json_valid_parse_valid_model_nested(PyObject* self,
                                    ReadBuffer* buff,
                                    PyObject** args,
                                    PyObject* kwnames)
{
    MetaModel* meta = _CAST_META(Py_TYPE(self));
    ValidateContext ctx = _VALID_MODEL_GET_CTX(self);
    PyObject** stack = DATA_MODEL_GET_SLOTS(self);

    _VectorDict vd;
    _VectorDict* kw = NULL;
    if (FT_UNLIKELY(kwnames)) {
        vd = _VectorDict_Create(args, 0, kwnames);
        kw = &vd;
    }

    return json_valid_parse_by_schema(
      meta->schemas, stack, meta->init_map, buff, &ctx, kw);
}

static inline int
json_valid_parse_validate_func_nested(ValidatedFunc* self,
                                      ValidateContext* ctx,
                                      PyObject** stack,
                                      ReadBuffer* buff,
                                      PyObject** args,
                                      PyObject* kwnames)
{
    _VectorDict vd;
    _VectorDict* kw = NULL;
    if (FT_UNLIKELY(kwnames)) {
        vd = _VectorDict_Create(args, 0, kwnames);
        kw = &vd;
    }

    return json_valid_parse_by_schema(
      self->schemas, stack, self->map, buff, ctx, kw);
}

static int
json_valid_parse_validate_func(ValidatedFunc* self,
                               ContextManager* ctx,
                               ReadBuffer* buff,
                               PyObject** res,
                               PyObject** args,
                               PyObject* kwnames)
{
    Py_ssize_t stack_size = VD_FUNC_GET_SIZE(self);
    PyObject** stack = (PyObject**)Mem_New(stack_size * BASE_SIZE);
    if (FT_UNLIKELY(!stack)) {
        return -1;
    }

    ArgsKwargs* data = _ArgsKwargs_Create(self, stack, 0, self->varnames);
    if (FT_UNLIKELY(!data)) {
        PyMem_Free(stack);
        return -1;
    }

    ValidateContext vctx = _ValidatedFunc_GetCtx(self, ctx);
    vctx.data = (PyObject*)data;

    int r = json_valid_parse_validate_func_nested(
      self, &vctx, stack, buff, args, kwnames);
    if (FT_UNLIKELY(r != 1)) {
        _ArgsKwargs_Decref(data);
        _Stack_Decref(stack, stack_size);
        return r;
    }

    r = _ValidatedFunc_CallAndCheckResult(
      self, stack, stack_size, self->kwnames, &vctx, res);
    _ArgsKwargs_Decref(data);
    _Stack_Decref(stack, stack_size);
    return r;
}

static int
json_valid_parse_dict_nested(TypeAdapter* vd,
                             ReadBuffer* buff,
                             ValidateContext* ctx,
                             PyObject* dict)
{
    if (FT_UNLIKELY(_Decode_Enter(buff) < 0)) {
        return -1;
    }

    uint8_t expect_key = 1;
    ValidationError* err = NULL;
    Py_ssize_t cnt_sep = 0, dict_size = 0;
    PyObject *key = NULL, *val = NULL;
    TypeAdapter* vd_key = (TypeAdapter*)PyTuple_GET_ITEM(vd->args, 0);
    TypeAdapter* vd_val = (TypeAdapter*)PyTuple_GET_ITEM(vd->args, 1);

    for (buff->iter++; buff->iter != buff->end_data; buff->iter++) {
        unsigned char ch = (unsigned char)*buff->iter;
        if (json_parse_continue(ch)) {
            continue;
        }

        if (ch == ':') {
            if (FT_LIKELY(expect_key && key)) {
                expect_key = 0;
                continue;
            }
            goto error;
        }

        if (ch == ',') {
            if (FT_LIKELY(!expect_key && !key && (++cnt_sep == dict_size))) {
                expect_key = 1;
                continue;
            }
            goto error;
        }

        if (ch == '}') {
            if (FT_LIKELY(!key &&
                          ((expect_key && !cnt_sep && !dict_size) ||
                           (!expect_key && cnt_sep == (dict_size - 1))))) {
                buff->iter++;
                _Decode_Leave(buff);
                if (FT_UNLIKELY(err)) {
                    ValidationError_RaiseWithModel(err, ctx->model);
                    return 0;
                }
                return 1;
            }
            goto error;
        }

        if (expect_key) {
            if (FT_UNLIKELY(key)) {
                goto error;
            }

            PyObject* tmp = JsonParse_StringKey(buff);
            if (FT_UNLIKELY(!tmp)) {
                goto error;
            }

            buff->iter--;
            key = TypeAdapter_Conversion(vd_key, ctx, tmp);
            if (!key) {
                if (FT_UNLIKELY(ValidationError_IndexCreate(
                                  dict_size, vd_key, tmp, ctx->model, &err) <
                                0)) {
                    Py_DECREF(tmp);
                    goto error;
                }
                key = Py_NewRef(_PySet_Dummy);
            }
            Py_DECREF(tmp);
            continue;
        } else if (FT_UNLIKELY(!key)) {
            goto error;
        }

        int r = vd_val->json_parser(vd_val, buff, ctx, &val);
        buff->iter--;
        dict_size++;

        if (FT_UNLIKELY(r < 0)) {
            goto error;
        } else if (FT_UNLIKELY(!r)) {
            if (FT_UNLIKELY(_ValidationErrorSetNestedInd(
                              dict_size - 1, ctx->model, &err) < 0)) {
                goto error;
            }
            Py_XDECREF(key);
            key = NULL;
            continue;
        }

        if (FT_UNLIKELY(key == _PySet_Dummy || !val)) {
            Py_XDECREF(key);
            Py_XDECREF(val);
            key = NULL;
            continue;
        }

        r = PyDict_SetItemDecrefVal(dict, key, val);
        Py_DECREF(key);
        key = NULL;
        if (FT_UNLIKELY(r < 0)) {
            return -1;
        }
    }

error:
    Py_XDECREF(key);
    Py_XDECREF(err);
    return -1;
}

static int
json_valid_parse_valid_model(PyTypeObject* tp,
                             ContextManager* ctx,
                             ReadBuffer* buff,
                             PyObject** res,
                             PyObject** args,
                             PyObject* kwnames)
{
    *res = NULL;
    if (*buff->iter != '{') {
        return json_valid_raise(buff, (PyObject*)ctx);
    }

    PyObject* self = _DataModel_Alloc(tp);
    if (FT_UNLIKELY(!self)) {
        return -1;
    }

    _ValidModel_SetCtx(self, ctx);
    int r = json_valid_parse_valid_model_nested(self, buff, args, kwnames);
    if (FT_LIKELY(r == 1 && _MetaModel_CallPostInit(self) >= 0)) {
        *res = self;
        return 1;
    }

    Py_DECREF(self);
    *res = NULL;
    return r;
}

static PyObject*
json_valid_parse(TypeAdapter* self, ReadBuffer* buff, ValidateContext* ctx)
{
    PyObject* res = NULL;
    self->json_parser(self, buff, ctx, &res);
    if (!res) {
        json_valid_raise(buff, ctx->model);
        return NULL;
    }

    if (json_valid_check_end(buff, ctx->model) < 0) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static int
json_valid_parse_handler_str(TypeAdapter* vd,
                             ValidateContext* ctx,
                             char* st,
                             char* end_dat,
                             Py_UCS4 max_char,
                             Py_ssize_t size)
{
    PyErr_Clear();
    PyObject* input = _JsonParse_CreateString(
      (unsigned char*)st, (unsigned char*)end_dat, max_char, size, 0);
    if (FT_UNLIKELY(!input)) {
        return -1;
    }

    int r = ValidationError_Raise(NULL, vd, input, ctx->model);
    Py_DECREF(input);
    return r;
}

static int
json_valid_parse_date_and_time(TypeAdapter* vd,
                               ReadBuffer* buff,
                               ValidateContext* ctx,
                               PyObject** res,
                               parse_dt parser)
{
    if (*buff->iter != '"') {
        return _JsonValidParse(vd, buff, ctx, res);
    }

    Py_UCS4 max_ch;
    char *end_dat, *st = buff->iter + 1;
    Py_ssize_t str_size =
      _JsonParse_String(buff, &max_ch, (unsigned char**)(&end_dat));
    if (FT_UNLIKELY(str_size < 0)) {
        return -1;
    }

    *res = parser(st, _CAST(Py_ssize_t, end_dat - st), 0);
    if (*res) {
        return 1;
    }

    return json_valid_parse_handler_str(vd, ctx, st, end_dat, max_ch, str_size);
}

int
_JsonValidParse_Date(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res)
{
    return json_valid_parse_date_and_time(
      vd, buff, ctx, res, _DateTime_ParseDateFromBuff);
}

int
_JsonValidParse_Time(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res)
{
    return json_valid_parse_date_and_time(
      vd, buff, ctx, res, _DateTime_ParseTimeFromBuff);
}

int
_JsonValidParse_UUID(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res)
{
    if (FT_UNLIKELY(*buff->iter != '"')) {
        return _JsonValidParse(vd, buff, ctx, res);
    }

    Py_UCS4 max_ch;
    char *end_dat, *st = buff->iter + 1;
    Py_ssize_t str_size =
      _JsonParse_String(buff, &max_ch, (unsigned char**)(&end_dat));
    if (str_size < 0) {
        return -1;
    }

    *res = _Parse_UUID(vd, st, _CAST(Py_ssize_t, end_dat - st));
    if (*res) {
        return 1;
    }

    return json_valid_parse_handler_str(vd, ctx, st, end_dat, max_ch, str_size);
}

int
_JsonValidParse_DateTime(TypeAdapter* vd,
                         ReadBuffer* buff,
                         ValidateContext* ctx,
                         PyObject** res)
{
    return json_valid_parse_date_and_time(
      vd, buff, ctx, res, _DateTime_ParseDateTimeFromBuff);
}

int
_JsonValidParse_TimeDelta(TypeAdapter* vd,
                          ReadBuffer* buff,
                          ValidateContext* ctx,
                          PyObject** res)
{
    return json_valid_parse_date_and_time(
      vd, buff, ctx, res, _DateTime_ParseTimeDeltaFromBuff);
}

int
_JsonValidParse_Dict(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res)
{
    if (*buff->iter != '{') {
        return _JsonValidParse(vd, buff, ctx, res);
    }

    *res = NULL;
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(!dict)) {
        return -1;
    }

    int r = json_valid_parse_dict_nested(vd, buff, ctx, dict);
    if (r != 1) {
        Py_DECREF(dict);
        return r;
    }

    *res = dict;
    return 1;
}

int
_JsonValidParse_AnySet(TypeAdapter* vd,
                       ReadBuffer* buff,
                       ValidateContext* ctx,
                       PyObject** res)
{
    return json_valid_parse_array(
      vd,
      buff,
      ctx,
      res,
      vd->cls == (PyObject*)&PySet_Type ? PySet_New : PyFrozenSet_New,
      PySet_Add);
}

int
_JsonValidParse_List(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res)
{
    return json_valid_parse_array(
      vd, buff, ctx, res, _VOID_CAST(create, PyList_New), PyList_Append);
}

int
_JsonValidParse_Tuple(TypeAdapter* vd,
                      ReadBuffer* buff,
                      ValidateContext* ctx,
                      PyObject** res)
{
    PyObject* list;
    int r = _JsonValidParse_List(vd, buff, ctx, &list);
    if (r != 1) {
        return r;
    }

    *res = PyList_AsTuple(list);
    Py_DECREF(list);
    return *res ? 1 : -1;
}

int
_JsonValidParse_TupleFixSize(TypeAdapter* vd,
                             ReadBuffer* buff,
                             ValidateContext* ctx,
                             PyObject** res)
{
    if (FT_UNLIKELY(*(buff->iter - 1) != '[')) {
        return _JsonValidParse(vd, buff, ctx, res);
    }

    *res = NULL;
    PyObject* val = _JsonParse(buff);
    if (FT_UNLIKELY(!val)) {
        return -1;
    }

    *res = TypeAdapter_Conversion(vd, ctx, val);
    Py_DECREF(val);
    return *res ? 1 : -1;
}

int
_JsonValidParse_ValidModel(TypeAdapter* vd,
                           ReadBuffer* buff,
                           UNUSED ValidateContext* ctx,
                           PyObject** res)
{
    PyTypeObject* tp = _CAST(PyTypeObject*, vd->cls);
    return json_valid_parse_valid_model(
      tp, _CAST(MetaValidModel*, tp)->ctx, buff, res, NULL, NULL);
}

int
_JsonValidParse_TypeVar(TypeAdapter* vd,
                        ReadBuffer* buff,
                        ValidateContext* ctx,
                        PyObject** res)
{
    TypeAdapter* actual;
    int r = _ContextManager_Get_TTypeAdapter(vd->cls, ctx->ctx, &actual);
    if (r == 1) {
        return actual->json_parser(actual, buff, ctx, res);
    }
    return _JsonValidParse(vd, buff, ctx, res);
}

int
_JsonValidParse(TypeAdapter* vd,
                ReadBuffer* buff,
                ValidateContext* ctx,
                PyObject** res)
{
    PyObject* tmp = _JsonParse(buff);
    if (!tmp) {
        return -1;
    }

    *res = TypeAdapter_Conversion(vd, ctx, tmp);
    if (!*res) {
        int r = ValidationError_Raise(NULL, vd, tmp, ctx->model);
        Py_DECREF(tmp);
        return r;
    }

    Py_DECREF(tmp);
    return 1;
}

PyObject*
JsonValidParse(TypeAdapter* self, PyObject* obj, ValidateContext* ctx)
{
    ReadBuffer buff;
    if (FT_UNLIKELY(JsonParse_GetBuffer(&buff, obj) < 0)) {
        ValidationError_RaiseInvalidJson(obj, ctx->model);
        return NULL;
    }

    PyObject* res = json_valid_parse(self, &buff, ctx);
    if (FT_UNLIKELY(!res)) {
        json_valid_raise(&buff, ctx->model);
    }
    ReadBuffer_Free(&buff);
    return res;
}

int
_JsonValidParse_ContextManager(TypeAdapter* vd,
                               ReadBuffer* buff,
                               ValidateContext* ctx,
                               PyObject** res)
{
    ContextManager* self = (ContextManager*)vd->cls;
    ContextManager* new_ctx = _ContextManager_CreateByOld(self, ctx->ctx);
    if (FT_UNLIKELY(!new_ctx)) {
        return -1;
    }

    int r;
    if (PyType_Check(new_ctx->model) && MetaValid_IS_SUBCLASS(new_ctx->model)) {
        r = json_valid_parse_valid_model(
          (PyTypeObject*)new_ctx->model, new_ctx, buff, res, NULL, NULL);
    } else if (ValidatedFunc_Check(new_ctx->model)) {
        r = json_valid_parse_validate_func(
          (ValidatedFunc*)new_ctx->model, new_ctx, buff, res, NULL, NULL);
    } else {
        r = _JsonValidParse(vd, buff, ctx, res);
    }
    Py_DECREF(new_ctx);
    return r;
}

static PyObject*
json_valida_parse_valid_nester(PyObject* self,
                               PyObject* obj,
                               ContextManager* ctx,
                               PyObject** args,
                               PyObject* kwnames,
                               parse_v_f parser)
{
    ReadBuffer buff;
    if (FT_UNLIKELY(JsonParse_GetBuffer(&buff, obj) < 0)) {
        ValidationError_RaiseInvalidJson(obj, (PyObject*)ctx);
        return NULL;
    }

    PyObject* res = NULL;
    parser(self, ctx, &buff, &res, args, kwnames);
    if (FT_UNLIKELY(!res)) {
        json_valid_raise(&buff, (PyObject*)ctx);
    } else if (FT_UNLIKELY(json_valid_check_end(&buff, (PyObject*)ctx) < 0)) {
        Py_CLEAR(res);
    }

    ReadBuffer_Free(&buff);
    return res;
}

inline PyObject*
JsonValidParse_ValidModel(PyTypeObject* tp,
                          PyObject* obj,
                          ContextManager* ctx,
                          PyObject** args,
                          PyObject* kwnames)
{
    return json_valida_parse_valid_nester(
      (PyObject*)tp,
      obj,
      ctx,
      args,
      kwnames,
      (parse_v_f)json_valid_parse_valid_model);
}

inline PyObject*
JsonValidParse_ValidatedFunc(ValidatedFunc* self,
                             PyObject* obj,
                             ContextManager* ctx,
                             PyObject** args,
                             PyObject* kwnames)
{
    return json_valida_parse_valid_nester(
      (PyObject*)self,
      obj,
      ctx,
      args,
      kwnames,
      (parse_v_f)json_valid_parse_validate_func);
}