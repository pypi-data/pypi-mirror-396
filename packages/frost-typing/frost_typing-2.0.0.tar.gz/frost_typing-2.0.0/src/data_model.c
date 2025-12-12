#include "data_model.h"
#include "context_manager.h"
#include "convector.h"
#include "diff.h"
#include "field.h"
#include "field_serializer.h"
#include "hash_table.h"
#include "json_schema.h"
#include "meta_valid_model.h"
#include "utils_common.h"
#include "valid_model.h"
#include "vector_dict.h"
#include "json/json.h"

inline int
_DataModel_Get(Schema* sc,
               PyObject** addr,
               PyObject* self,
               PyObject** res,
               int missing_ok)
{
    PyObject* val = *addr;
    if (FT_LIKELY(val)) {
        *res = Py_NewRef(val);
        return 1;
    }
    return _Schema_GetValue(sc, self, addr, res, missing_ok);
}

inline PyObject*
_DataModel_FastGet(Schema* sc, PyObject** addr, PyObject* self)
{
    PyObject* val = *addr;
    if (FT_LIKELY(val)) {
        Py_INCREF(val);
    } else {
        _Schema_GetValue(sc, self, addr, &val, 0);
    }
    return val;
}

static inline void*
data_model_alloc(PyTypeObject* tp, UNUSED Py_ssize_t size)
{
    if (FT_LIKELY(Meta_IS_SUBCLASS(tp))) {
        return Object_New(void, tp);
    }
    return (void*)PyErr_Format(
      PyExc_TypeError, "%s is not initialized", tp->tp_name);
}

inline PyObject*
_DataModel_Alloc(PyTypeObject* tp)
{
    return (PyObject*)data_model_alloc(tp, 0);
}

static PyObject*
data_model_new(PyTypeObject* cls,
               UNUSED PyObject* args,
               UNUSED PyObject* kwargs)
{
    return data_model_alloc(cls, 0);
}

static inline void
data_model_raise_missing(const char* func_name, PyObject* names)
{
    UnicodeWriter_Create(writer, 32);
    if (FT_UNLIKELY(!writer)) {
        return;
    }

    Py_ssize_t cnt = PyList_GET_SIZE(names);
    _UNICODE_WRITE_STRING(writer, func_name, -1);
    _UNICODE_WRITE_STRING(writer, "() missing ", 11);

    _UNICODE_WRITE_SSIZE(writer, cnt);
    _UNICODE_WRITE_STRING(writer, " required positional arguments: ", 32);

    for (Py_ssize_t i = 0; i != cnt; i++) {
        if (i && UnicodeWriter_WriteASCIIString(writer, " and ", 5) < 0) {
            goto error;
        }

        _UNICODE_WRITE_CHAR(writer, '\'');
        PyObject* name = PyList_GET_ITEM(names, i);
        _UNICODE_WRITE_STR(writer, name);
        _UNICODE_WRITE_CHAR(writer, '\'');
    }

    PyObject* res = UnicodeWriter_Finish(writer);
    if (FT_LIKELY(res)) {
        PyErr_SetObject(PyExc_TypeError, res);
        Py_DECREF(res);
    }
    return;

error:
    UnicodeWriter_Discard(writer);
}

static inline void
data_model_missing(Schema** schemas,
                   Schema** end_schemas,
                   PyObject* arg,
                   const char* func_name)
{
    PyObject* names = PyList_New(0);
    if (FT_UNLIKELY(!names)) {
        return;
    }

    for (Schema* sc = *schemas; schemas != end_schemas; sc = *++schemas) {
        const uint32_t flags = sc->field->flags;
        if (FT_LIKELY(!IS_FIELD_INIT(flags) || IF_FIELD_DEFAULT(flags) ||
                      IF_FIELD_DEFAULT_FACTORY(flags))) {
            continue;
        }

        PyObject* name = SCHEMA_GET_NAME(sc);
        PyObject* val = arg ? _Object_Gettr(arg, name) : NULL;
        if (val) {
            Py_DECREF(val);
            continue;
        }

        if (FT_UNLIKELY(PyList_Append(names, name) < 0)) {
            Py_DECREF(names);
            return;
        }
    };

    data_model_raise_missing(func_name, names);
    Py_DECREF(names);
}

static int
data_model_universal_init(PyObject* self,
                          PyObject* const* args,
                          Py_ssize_t args_cnt,
                          PyObject* kw,
                          const char* f_name)
{
    PyTypeObject* tp = Py_TYPE(self);
    PyObject *name, *val, *const *args_end, **slots;

    args_end = args + args_cnt;
    slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(schema, tp, slots++)
    {
        const uint32_t flags = schema->field->flags;
        if (!IS_FIELD_INIT(flags)) {
            if (FT_UNLIKELY(_DataModel_SetDefault(schema->field, slots) < 0)) {
                return -1;
            }
            continue;
        }

        name = SCHEMA_GET_NAME(schema);
        val = kw ? _Object_Gettr(kw, name) : NULL;
        if ((args != args_end) && !IS_FIELD_KW_ONLY(flags)) {
            if (FT_UNLIKELY(val)) {
                Py_DECREF(val);
                PyErr_Format(PyExc_TypeError,
                             "%.100s() got multiple values for argument '%U'",
                             f_name,
                             name);
                return -1;
            }
            val = Py_NewRef(*args++);
        }

        if (val) {
            Py_XDECREF(*slots);
            *slots = val;
            continue;
        }

        int r = _DataModel_SetDefault(schema->field, slots);
        if (FT_UNLIKELY(r == -1)) {
            return -1;
        } else if (FT_UNLIKELY(!r)) {
            data_model_missing(__schema, __end_schema, kw, f_name);
            return -1;
        }
    }
    return 0;
}

static inline void
data_model_vec_missing(PyObject** slots, Schema** st, Schema** end)
{
    PyObject* names = PyList_New(0);
    if (FT_UNLIKELY(!names)) {
        return;
    }

    for (Schema* sc = *st; st != end; sc = *++st, slots++) {
        const uint32_t flags = sc->field->flags;
        if (FT_LIKELY(*slots || !IS_FIELD_INIT(flags) ||
                      IF_FIELD_DEFAULT(flags) ||
                      IF_FIELD_DEFAULT_FACTORY(flags))) {
            continue;
        }

        if (FT_UNLIKELY(PyList_Append(names, SCHEMA_GET_NAME(sc)) < 0)) {
            Py_DECREF(names);
            return;
        }
    }

    data_model_raise_missing("__init__", names);
    Py_DECREF(names);
}

static inline int
data_model_vec_set_args(PyObject* self,
                        PyObject* const* args,
                        Py_ssize_t nargsf)
{
    PyObject** slots = DATA_MODEL_GET_SLOTS(self);
    MetaModel* meta = (MetaModel*)Py_TYPE(self);
    Schema** schemas = (Schema**)TUPLE_ITEMS(meta->schemas);
    Py_ssize_t size = META_GET_SIZE(meta), i = 0;

    for (Py_ssize_t a_ind = 0; i != size && a_ind != nargsf; i++, slots++) {
        Schema* sc = schemas[i];
        if (FT_UNLIKELY(!IS_FIELD_INIT(sc->field->flags))) {
            if (FT_UNLIKELY(_DataModel_SetDefault(sc->field, slots) < 0)) {
                return -1;
            }
            continue;
        }

        if (FT_UNLIKELY(*slots)) {
            if (FT_LIKELY(IS_FIELD_KW_ONLY(sc->field->flags))) {
                continue;
            }

            PyErr_Format(PyExc_TypeError,
                         "__init__() got multiple values for argument'%U'",
                         SCHEMA_GET_NAME(sc));
            return -1;
        }

        Py_XDECREF(*slots);
        *slots = Py_NewRef(args[a_ind++]);
    }

    for (; i != size; i++, slots++) {
        if (FT_LIKELY(*slots)) {
            continue;
        }

        Field* field = schemas[i]->field;
        int r = _DataModel_SetDefault(field, slots);
        if (FT_UNLIKELY(r == -1)) {
            return -1;
        } else if (FT_UNLIKELY(!r && IS_FIELD_INIT(field->flags))) {
            data_model_vec_missing(slots, schemas + i, schemas + size);
            return -1;
        }
    }
    return 0;
}

static int
data_model_init(PyObject* self, PyObject* args, PyObject* kw)
{
    MetaModel* m = _CAST_META(Py_TYPE(self));
    Py_ssize_t size = PyTuple_GET_SIZE(args);
    if (IS_FAIL_ON_EXTRA_INIT(m->config->flags) &&
        (!PyCheck_MaxArgs("__init__", size, m->args_only) ||
         !HashTable_CheckExtraDict(m->init_map, m->schemas, kw, "__init__"))) {
        return -1;
    }

    if (!kw) {
        return data_model_vec_set_args(self, TUPLE_ITEMS(args), size);
    }

    return data_model_universal_init(
      self, TUPLE_ITEMS(args), size, kw, "__init__");
}

static int
data_model_vec_init(PyObject* self,
                    PyObject* const* args,
                    size_t nargsf,
                    PyObject* kwnames)
{
    MetaModel* meta = _CAST_META(Py_TYPE(self));
    Py_ssize_t size = PyVectorcall_NARGS(nargsf);
    const int fail_on_extra_init = IS_FAIL_ON_EXTRA_INIT(meta->config->flags);

    if (fail_on_extra_init &&
        !PyCheck_MaxArgs("__init__", size, meta->args_only)) {
        return -1;
    }

    if (FT_UNLIKELY(kwnames && _Schema_VectorInitKw(DATA_MODEL_GET_SLOTS(self),
                                                    meta->init_map,
                                                    fail_on_extra_init,
                                                    args + size,
                                                    kwnames) < 0)) {
        return -1;
    }
    return data_model_vec_set_args(self, args, size);
}

static int
data_model_init_from_attributes(PyObject* self, PyObject* obj)
{
    return data_model_universal_init(self, NULL, 0, obj, "from_attributes");
}

static PyObject*
data_model_repr(PyObject* self)
{
    PyTypeObject* tp = Py_TYPE(self);
    int r = Py_ReprEnter(self);
    if (r) {
        return r > 0 ? PyUnicode_FromFormat("%.100s(...)", tp->tp_name) : NULL;
    }

    UnicodeWriter_Create(writer, 8);
    if (FT_UNLIKELY(!writer)) {
        return NULL;
    }

    if (MetaValid_IS_SUBCLASS(tp) && _CAST(ValidModel*, self)->ctx) {
        if (FT_UNLIKELY(_ContextManager_ReprModel(
                          writer, (PyObject*)_CAST(ValidModel*, self)->ctx) <
                        0)) {
            goto error;
        }
    } else {
        _UNICODE_WRITE_STRING(writer, tp->tp_name, -1);
    }

    int sep = 0;
    PyObject** slots = DATA_MODEL_GET_SLOTS(self);
    _UNICODE_WRITE_CHAR(writer, '(');
    SchemaForeach(sc, tp, slots++)
    {
        if (!IS_FIELD_REPR(sc->field->flags)) {
            continue;
        }

        if (FT_LIKELY(sep)) {
            _UNICODE_WRITE_STRING(writer, ", ", 2);
        } else {
            sep = 1;
        }

        _UNICODE_WRITE_STR(writer, sc->name);
        _UNICODE_WRITE_CHAR(writer, '=');

        PyObject* val = _DataModel_FastGet(sc, slots, self);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        int r = _UnicodeWriter_Write(writer, val, PyObject_Repr);
        Py_DECREF(val);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    _UNICODE_WRITE_CHAR(writer, ')');

    Py_ReprLeave(self);
    return UnicodeWriter_Finish(writer);

error:
    UnicodeWriter_Discard(writer);
    Py_ReprLeave(self);
    return NULL;
}

static Py_hash_t
data_model_hash(PyObject* self)
{
    if (FT_UNLIKELY(Py_EnterRecursiveCall(" hash"))) {
        return -1;
    }

    PyObject *val, **slots;
    PyTypeObject* tp = Py_TYPE(self);
    Py_hash_t acc = _PyHASH_XXPRIME_5;

    slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, tp, slots++)
    {
        if (!IS_FIELD_HASH(sc->field->flags)) {
            continue;
        }

        val = _DataModel_FastGet(sc, slots, self);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        Py_hash_t lane = PyObject_Hash(val);
        Py_DECREF(val);
        if (FT_UNLIKELY(lane == -1 && PyErr_Occurred())) {
            goto error;
        }

        acc += lane * _PyHASH_XXPRIME_2;
        acc = _PyHASH_XXROTATE(acc);
        acc *= _PyHASH_XXPRIME_1;
    }
    Py_LeaveRecursiveCall();

    acc += META_GET_SIZE(tp) ^ (_PyHASH_XXPRIME_5 ^ 3527539UL);
    if (FT_UNLIKELY(acc == (Py_hash_t)-1)) {
        return 1546275797;
    }

    return acc;

error:
    Py_LeaveRecursiveCall();
    return -1;
}

static PyObject*
data_model_richcompare(PyObject* self, PyObject* other, int op)
{
    if (FT_UNLIKELY(op != Py_EQ && op != Py_NE)) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    PyTypeObject* tp = Py_TYPE(self);
    if (FT_UNLIKELY(!Py_IS_TYPE(other, tp))) {
        return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
    }

    PyObject **slots, **o_slots, *val, *o_val;
    o_slots = DATA_MODEL_GET_SLOTS(other);
    slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, tp, slots++, o_slots++)
    {
        if (FT_UNLIKELY(!IS_FIELD_COMPARISON(sc->field->flags))) {
            continue;
        }

        val = _DataModel_FastGet(sc, slots, self);
        if (FT_UNLIKELY(!val)) {
            return NULL;
        }

        o_val = _DataModel_FastGet(sc, o_slots, other);
        if (FT_UNLIKELY(!o_val)) {
            Py_DECREF(val);
            return NULL;
        }

        int r = PyObject_RichCompareBool(val, o_val, Py_EQ);
        Py_DECREF(val);
        Py_DECREF(o_val);
        if (FT_UNLIKELY(r < 0)) {
            return NULL;
        }
        if (!r) {
            return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
        }
    }
    return Py_NewRef(op == Py_EQ ? Py_True : Py_False);
}

static PyObject*
data_model__as_dict__nested(PyObject* self,
                            ConvParams* params,
                            PyObject* include,
                            PyObject* exclude,
                            uint32_t exclude_flag)
{
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(!dict)) {
        return NULL;
    }

    PyTypeObject* tp = Py_TYPE(self);
    PyObject** slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, tp, slots++)
    {
        if (FT_UNLIKELY(!IF_FIELD_CHECK(sc->field, exclude_flag))) {
            continue;
        }

        if (FT_UNLIKELY(exclude)) {
            int r = PySet_Contains(exclude, sc->name);
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            if (r) {
                continue;
            }
        }

        if (FT_UNLIKELY(include)) {
            int r = PySet_Contains(include, sc->name);
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            if (!r) {
                continue;
            }
        }

        PyObject* val;
        int r = _DataModel_Get(sc, slots, self, &val, params->exclude_unset);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        } else if (FT_UNLIKELY(!r ||
                               (params->exclude_none && val == Py_None))) {
            Py_XDECREF(val);
            continue;
        }

        if (FT_UNLIKELY(params->custom_ser &&
                        IF_FIELD_CHECK(sc->field, _FIELD_SERIALIZER))) {
            PyObject* tmp = _FieldSerializer_Call(sc->field, self, val, params);
            Py_DECREF(val);
            if (FT_UNLIKELY(!tmp)) {
                goto error;
            }
            val = tmp;
        }

        val = _Convector_ObjDecrefVal(val, params);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        PyObject* name = SCHEMA_GET_SNAME(params->by_alias, sc);
        if (FT_UNLIKELY(PyDict_SetItemStringDecrefVal(dict, name, val) < 0)) {
            goto error;
        }
    }

    return dict;

error:
    Py_DECREF(dict);
    return NULL;
}

static int
data_model_parse_ser_info(PyObject* const* args,
                          Py_ssize_t nargs,
                          PyObject* method_name,
                          ConvParams* params)
{
    Py_ssize_t args_cnt = PyVectorcall_NARGS(nargs);
    if (FT_UNLIKELY(!PyCheck_MaxArgs(
          (const char* const)PyUnicode_DATA(method_name), nargs, 1))) {
        return -1;
    }

    if (args_cnt == 1) {
        SerializationInfo* info = (SerializationInfo*)*args;
        PyTypeObject* tp_info = Py_TYPE(info);
        if (FT_UNLIKELY(!PyType_IsSubtype(tp_info, &SerializationInfo_Type))) {
            _RaiseInvalidType(
              "info", SerializationInfo_Type.tp_name, Py_TYPE(info)->tp_name);
            return -1;
        }

        params->serialization_info = Py_NewRef(info);
        params->attr = method_name;
        params->by_alias = info->by_alias;
        params->context = info->context;
        params->custom_ser = info->custom_ser;
        params->exclude_none = info->exclude_none;
        params->exclude_unset = info->exclude_unset;
        params->str_unknown = 0;
        params->nested = 0;
    } else {
        *params = ConvParams_Create(method_name);
    }

    return 0;
}

static PyObject*
data_model__as_dict__(PyObject* self, PyObject* const* args, Py_ssize_t nargs)
{
    ConvParams params;
    if (data_model_parse_ser_info(args, nargs, __as_dict__, &params)) {
        return NULL;
    }

    PyObject* res =
      data_model__as_dict__nested(self, &params, NULL, NULL, FIELD_DICT);
    _ConvParams_Free(&params);
    return res;
}

static PyObject*
data_model_as_dict(PyObject* self,
                   PyObject* const* args,
                   Py_ssize_t nargsf,
                   PyObject* kwnames)
{
    PyObject *res = NULL, *argsbuf[8] = { NULL };
    ConvParams params = ConvParams_Create(__as_dict__);
    nargsf = PyVectorcall_NARGS(nargsf);
    if (FT_LIKELY(!kwnames && !nargsf)) {
        goto done;
    }

    static const char* const kwlist[] = {
        "as_json",      "include",    "exclude", "by_alias", "exclude_unset",
        "exclude_none", "use_custom", "context", NULL,
    };
    static _PyArg_Parser _parser = {
        .keywords = kwlist,
        .fname = "as_dict",
        .kwtuple = NULL,
    };

    if (FT_UNLIKELY(!PyArg_UnpackKeywords(args,
                                          nargsf,
                                          NULL,
                                          kwnames,
                                          &_parser,
                                          0, /*minpos*/
                                          0, /*maxpos*/
                                          0, /*minkw*/
                                          argsbuf))) {
        return NULL;
    }

    if (FT_UNLIKELY(!_ValidateArg(argsbuf[0], &PyBool_Type, kwlist[0]))) {
        return NULL;
    }

    if (FT_UNLIKELY(_Convector_ValidateInclude(argsbuf + 1, argsbuf + 2) < 0)) {
        return NULL;
    }

    for (Py_ssize_t i = 3; i != 7; i++) {
        if (FT_UNLIKELY(!_ValidateArg(argsbuf[i], &PyBool_Type, kwlist[i]))) {
            return NULL;
        }
    }

    if (argsbuf[0] == Py_True) {
        params.attr = __as_json__;
    }

    params.by_alias = argsbuf[3] != Py_False;
    params.exclude_unset = argsbuf[4] == Py_True;
    params.exclude_none = argsbuf[5] == Py_True;
    params.custom_ser = argsbuf[6] != Py_False;
    params.context = argsbuf[7];

done:
    res = _DataModel_AsDict(self, &params, argsbuf[1], argsbuf[2]);
    _ConvParams_Free(&params);
    return res;
}

PyObject*
_DataModel_AsDict(PyObject* self,
                  ConvParams* params,
                  PyObject* include,
                  PyObject* exclude)
{
    PyTypeObject* tp = Py_TYPE(self);
    PyObject* as_dict = _CAST_META(tp)->__as_dict__;
    if (FT_LIKELY(as_dict == DataModelType.__as_dict__)) {
        return data_model__as_dict__nested(
          self,
          params,
          include,
          exclude,
          params->attr == __as_dict__ ? FIELD_DICT : FIELD_JSON);
    }

    if (FT_UNLIKELY(!as_dict)) {
        return PyErr_Format(PyExc_TypeError,
                            "'%.100s' object has no '%U' method",
                            tp->tp_name,
                            __as_dict__);
    }

    PyObject* res = _Сonvector_СallFunc(as_dict, self, params);
    if (FT_UNLIKELY(res && !PyDict_Check(res))) {
        _RaiseInvalidReturnType("__as_dict__", "dict", Py_TYPE(res)->tp_name);
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

PyObject*
_DataModel_Copy(PyObject* self)
{
    PyTypeObject* tp = Py_TYPE(self);
    PyObject *duplicate, **c_slots;
    ConvParams conv_params = ConvParams_Create(__copy__);
    duplicate = _DataModel_Alloc(tp);
    if (FT_UNLIKELY(!duplicate)) {
        return NULL;
    }

    if (MetaValid_IS_SUBCLASS(tp)) {
        Py_XINCREF(_CAST(ValidModel*, self)->ctx);
        _CAST(ValidModel*, duplicate)->ctx = _CAST(ValidModel*, self)->ctx;
    }

    c_slots = DATA_MODEL_GET_SLOTS(duplicate);
    DataModelForeach(slots, self, c_slots++)
    {
        PyObject* val = *slots;
        if (FT_UNLIKELY(!val)) {
            continue;
        }

        val = _Convector_Obj(val, &conv_params);
        if (FT_UNLIKELY(!val)) {
            Py_DECREF(duplicate);
            return NULL;
        }
        *c_slots = val;
    }

    if (tp->tp_dictoffset) {
        PyObject **addr_dict, *copy_dict;
        addr_dict = _PyObject_GetDictPtr(self);
        if (!addr_dict || !*addr_dict) {
            return duplicate;
        }

        copy_dict = _Convector_Obj(*addr_dict, &conv_params);
        if (FT_UNLIKELY(!copy_dict)) {
            Py_DECREF(duplicate);
            return NULL;
        }

        addr_dict = _PyObject_GetDictPtr(duplicate);
        Py_XDECREF(*addr_dict);
        *addr_dict = copy_dict;
    }
    return duplicate;
}

PyObject*
_DataModel_CallCopy(PyObject* self)
{
    PyTypeObject* tp = Py_TYPE(self);
    PyObject* copy = _CAST_META(tp)->__copy__;
    if (FT_LIKELY(copy == DataModelType.__copy__)) {
        return _DataModel_Copy(self);
    }

    if (!copy) {
        return PyErr_Format(PyExc_TypeError,
                            "'%.100s' object has no '%U' method",
                            tp->tp_name,
                            __copy__);
    }

    PyObject* res = PyObject_CallOneArg(copy, self);
    if (FT_UNLIKELY(res && !Py_IS_TYPE(res, tp))) {
        _RaiseInvalidReturnType("__copy__", tp->tp_name, Py_TYPE(res)->tp_name);
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
data_model_copy(PyObject* self,
                PyObject** args,
                size_t nargsf,
                PyObject* kwnames)
{
    if (!PyCheck_ArgsCnt("copy", PyVectorcall_NARGS(nargsf), 0)) {
        return NULL;
    }

    PyObject* res = _DataModel_CallCopy(self);
    if (FT_LIKELY(!res || !kwnames)) {
        return res;
    }

    MetaModel* meta = _CAST_META(Py_TYPE(res));
    HashTable* map = meta->attr_map;
    PyObject** stack = GET_ADDR(res, meta->slot_offset);
    TupleForeach(name, kwnames, args++)
    {
        const Py_ssize_t offset = _HashTable_Get(map, name);
        if (FT_UNLIKELY(offset < 0)) {
            continue;
        }

        PyObject** addr = GET_ADDR(stack, offset);
        Py_XDECREF(*addr);
        *addr = Py_NewRef(*args);
    }
    return res;
}

static PyObject*
data_model_from_attributes(PyTypeObject* cls, PyObject* obj)
{
    PyObject* self = _DataModel_Alloc(cls);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    if (data_model_init_from_attributes(self, obj) < 0 ||
        _MetaModel_CallPostInit(self) < 0) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

static PyObject*
data_model_from_json(PyTypeObject* cls,
                     PyObject* const* args,
                     size_t nargs,
                     PyObject* kwnames)
{
    Py_ssize_t cnt = PyVectorcall_NARGS(nargs);
    if (FT_UNLIKELY(!PyCheck_ArgsCnt(".from_json", cnt, 1))) {
        return NULL;
    }

    PyObject* dict = JsonParse((PyObject*)*args);
    if (FT_UNLIKELY(!dict)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyDict_Check(dict))) {
        PyErr_SetString(PyExc_TypeError, "JSON must be dict");
        Py_DECREF(dict);
        return NULL;
    }

    if (FT_UNLIKELY(_Dict_MergeKwnames(dict, args + cnt, kwnames) < 0)) {
        Py_DECREF(dict);
        return NULL;
    }

    PyObject* res = data_model_from_attributes(cls, dict);
    Py_DECREF(dict);
    return res;
}

static int
data_model_clear(PyObject* self)
{
    PyTypeObject* tp = Py_TYPE(self);
    if (PyType_SUPPORTS_WEAKREFS(tp)) {
        PyObject_ClearWeakRefs(self);
    }

    DataModelForeach(slots, self)
    {
        Py_CLEAR(*slots);
    }

    if (tp->tp_dictoffset) {
        PyObject** addr_dict = _PyObject_GetDictPtr(self);
        Py_CLEAR(*addr_dict);
    }
    return 0;
}

int
_DataModel_Traverse(PyObject* self, visitproc visit, void* arg)
{
    DataModelForeach(slots, self)
    {
        Py_VISIT(*slots);
    }

    if (Py_TYPE(self)->tp_dictoffset) {
        PyObject** addr_dict = _PyObject_GetDictPtr(self);
        Py_VISIT(*addr_dict);
    }
    return 0;
}

static PyObject*
data_model__as_json__(PyObject* self, PyObject* const* args, Py_ssize_t nargs)
{
    ConvParams params;
    if (data_model_parse_ser_info(args, nargs, __as_json__, &params)) {
        return NULL;
    }

    PyObject* res =
      data_model__as_dict__nested(self, &params, NULL, NULL, FIELD_JSON);
    _ConvParams_Free(&params);
    return res;
}

static PyObject*
data_model_get_item(PyObject* self, PyObject* name)
{
    MetaModel* meta = _CAST_META(Py_TYPE(self));
    const Py_ssize_t offset = HashTable_Get(meta->attr_map, name);
    if (offset < 0) {
        PyErr_SetObject(PyExc_KeyError, name);
        return NULL;
    }

    PyObject *val, **addr = GET_ADDR(self, meta->slot_offset + offset);
    Schema* sc = META_GET_SCHEMA_BY_OFFSET(meta, offset);
    int r = _DataModel_Get(sc, addr, self, &val, 1);
    if (FT_UNLIKELY(r < 0)) {
        return NULL;
    } else if (FT_UNLIKELY(!r)) {
        PyErr_SetObject(PyExc_KeyError, name);
        return NULL;
    }
    return val;
}

static PyObject*
data_model_keys(MetaModel* cls)
{
    PyObject* res = PyList_New(META_GET_SIZE(cls));
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    Py_ssize_t i = 0;
    SchemaForeach(sc, cls)
    {
        if (FT_LIKELY(IS_FIELD_DICT(sc->field->flags))) {
            PyList_SET_ITEM(res, i++, Py_NewRef(sc->name));
        }
    }

    Py_SET_SIZE(res, i);
    return res;
}

static PyObject*
data_model__setstate__(PyObject* self, PyObject* state)
{
    if (!PyDict_Check(state)) {
        return _RaiseInvalidType("state", "dict", Py_TYPE(state)->tp_name);
    }

    PyObject** slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, Py_TYPE(self), slots++)
    {
        PyObject* val = _Dict_GetAscii(state, SCHEMA_GET_NAME(sc));
        if (!val) {
            continue;
        }
        Py_XDECREF(*slots);
        *slots = Py_NewRef(val);
    }
    Py_RETURN_NONE;
}

static PyObject*
data_model__getstate__(PyObject* self)
{
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(!dict)) {
        return NULL;
    }

    PyObject** slots = DATA_MODEL_GET_SLOTS(self);
    SchemaForeach(sc, Py_TYPE(self), slots++)
    {
        PyObject* val = _DataModel_FastGet(sc, slots, self);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        if (FT_UNLIKELY(_PyDict_SetItemAsciiDecrefVal(
                          dict, SCHEMA_GET_NAME(sc), val) < 0)) {
            goto error;
        }
    }

    return dict;

error:
    Py_DECREF(dict);
    return NULL;
}

static PyMethodDef data_model_methods[] = {
    { "keys", PY_METHOD_CAST(data_model_keys), METH_CLASS | METH_NOARGS, NULL },
    { "from_attributes",
      PY_METHOD_CAST(data_model_from_attributes),
      METH_CLASS | METH_O,
      NULL },
    { "from_json",
      PY_METHOD_CAST(data_model_from_json),
      METH_CLASS | METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "as_dict",
      PY_METHOD_CAST(data_model_as_dict),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "__setstate__", PY_METHOD_CAST(data_model__setstate__), METH_O, NULL },
    { "__getstate__",
      PY_METHOD_CAST(data_model__getstate__),
      METH_NOARGS,
      NULL },
    { "__as_dict__",
      PY_METHOD_CAST(data_model__as_dict__),
      METH_FASTCALL,
      NULL },
    { "__as_json__",
      PY_METHOD_CAST(data_model__as_json__),
      METH_FASTCALL,
      NULL },
    { "as_json",
      PY_METHOD_CAST(_MetaModel_AsJsonCall),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "__copy__", PY_METHOD_CAST(_DataModel_Copy), METH_NOARGS, NULL },
    { "copy",
      PY_METHOD_CAST(data_model_copy),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "json_schema",
      PY_METHOD_CAST(Schema_JsonSchema),
      METH_CLASS | METH_NOARGS,
      NULL },
    { "from_db_row",
      PY_METHOD_CAST(Object_FromDbRow),
      METH_CLASS | METH_FASTCALL,
      NULL },
    { NULL }
};

PyMappingMethods data_model_as_mapping = {
    .mp_subscript = data_model_get_item,
};

MetaModel DataModelType = {
    .vec_init = data_model_vec_init,
    .slot_offset = SIZE_OBJ,
    .head = {
        .ht_type = {
            PyVarObject_HEAD_INIT((PyTypeObject*)&MetaModelType,
                                                 0)
            .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE |
            Py_TPFLAGS_HAVE_GC | TPFLAGS_META_SUBCLASS |
            Py_TPFLAGS_HAVE_VECTORCALL,
            .tp_vectorcall = (vectorcallfunc)_MetaModel_Vectorcall,
            .tp_richcompare = data_model_richcompare,
            .tp_as_mapping = &data_model_as_mapping,
            .tp_alloc = (allocfunc)data_model_alloc,
            .tp_name = "frost_typing.DataModel",
            .tp_traverse = _DataModel_Traverse,
            .tp_methods = data_model_methods,
            .tp_dealloc = _Object_Dealloc,
            .tp_clear = data_model_clear,
            .tp_init = data_model_init,
            .tp_repr = data_model_repr,
            .tp_free = PyObject_GC_Del,
            .tp_hash = data_model_hash,
            .tp_new = data_model_new,
        },
    },
};

int
_DataModel_SetDefault(Field* field, PyObject** res)
{
    PyObject* val;
    if (IF_FIELD_CHECK(field, FIELD_DEFAULT_FACTORY)) {
        val = PyObject_CallNoArgs(Field_GET_DEFAULT_FACTORY(field));
    } else {
        val = _Field_GetAttr(field, FIELD_DEFAULT);
        if (!val) {
            return 0;
        }

        val = IF_FIELD_CHECK(field, _FIELD_CONST_DEFAULT) ? Py_NewRef(val)
                                                          : PyCopy(val);
    }

    if (!val) {
        return -1;
    }
    Py_XDECREF(*res);
    *res = val;
    return 1;
}

void
data_model_free(void)
{
}

int
data_model_setup(void)
{
    DataModelType.config = (Field*)Py_NewRef((PyObject*)DefaultConfig);
    DataModelType.schemas = Py_NewRef(VoidTuple);
    Py_SET_TYPE(&DataModelType, &MetaModelType);
    if (PyType_Ready((PyTypeObject*)&DataModelType) < 0) {
        return -1;
    }

    Py_INCREF(&MetaModelType);
    Py_SET_TYPE(&DataModelType, &MetaModelType);

    PyObject* dict = DataModelType.head.ht_type.tp_dict;
    DataModelType.__copy__ = _Dict_GetAscii(dict, __copy__);
    if (!DataModelType.__copy__) {
        return -1;
    }

    DataModelType.__as_dict__ = _Dict_GetAscii(dict, __as_dict__);
    if (!DataModelType.__as_dict__) {
        return -1;
    }

    DataModelType.__as_json__ = _Dict_GetAscii(dict, __as_json__);
    if (!DataModelType.__as_json__) {
        return -1;
    }
    return 0;
}
