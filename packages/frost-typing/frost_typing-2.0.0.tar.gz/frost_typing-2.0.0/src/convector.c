#include "convector.h"
#include "data_model.h"
#include "datetime.h"
#include "meta_model.h"
#include "structmember.h"
#include "validator/py_typing.h"
#include "validator/validator.h"
#include "json/serialize/serialize_date_time.h"

#define _GET_IND(o, m, sh) (((uintptr_t)o * m) >> sh) & TABLE_MASK
#define GET_IND(o) _GET_IND(o, MAGIC, SHIFT)
#define TABLE_MASK (TABLE_MAP_SIZE - 1)
#define TABLE_MAP_SIZE 32
#define MAX_NESTING 1024

typedef struct
{
    PyTypeObject* key;
    uint8_t value;
} PtrEntry;

static PtrEntry table[TABLE_MAP_SIZE] = { NULL };
static uintptr_t MAGIC;
static int SHIFT;

static inline void
init_lookup(PtrEntry* entries, int len)
{
    for (uint32_t m = 1; m != (1ULL << 31); m++) {
        for (uint8_t sh = 0; sh != TABLE_MAP_SIZE; sh++) {
            int ok = 1;
            char used[TABLE_MAP_SIZE] = { 0 };
            for (int i = 0; i != len; i++) {
                size_t k = _GET_IND(entries[i].key, m, sh);
                if (used[k]) {
                    ok = 0;
                    break;
                }
                used[k] = 1;
            }
            if (ok) {
                MAGIC = m;
                SHIFT = sh;
                for (int i = 0; i < TABLE_MAP_SIZE; i++) {
                    table[i].key = NULL;
                    table[i].value = 0;
                }
                for (int i = 0; i < len; i++) {
                    size_t k = _GET_IND(entries[i].key, m, sh);
                    table[k] = entries[i];
                }
                return;
            }
        }
    }
}

inline int
_Convector_Enter(ConvParams* params)
{
    if (FT_LIKELY(++(params->nested) < MAX_NESTING)) {
        return 1;
    }
    PyErr_SetString(PyExc_RecursionError, "maximum recursion depth exceeded");
    return 0;
}

inline void
_Convector_Leave(ConvParams* params)
{
    params->nested--;
}

static PyObject*
convector_const(PyObject* val, UNUSED ConvParams* params)
{
    return Py_NewRef(val);
}

static PyObject*
convector_decimal(PyObject* val, ConvParams* params)
{
    if (params->attr != __as_json__) {
        return Py_NewRef(val);
    }
    return PyObject_Str(val);
}

static PyObject*
convector_enum(PyObject* obj, ConvParams* params)
{
    if (params->attr != __as_json__) {
        return Py_NewRef(obj);
    }

    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return NULL;
    }

    PyObject* val = PyObject_GetAttr(obj, __value);
    if (FT_UNLIKELY(!val)) {
        return NULL;
    }

    PyObject* res = _Convector_ObjDecrefVal(val, params);
    _Convector_Leave(params);
    return res;
}

Py_ssize_t
_UUID_AsStr(unsigned char* out, PyObject* obj)
{
    PyObject* value = PyObject_GetAttr(obj, __int);
    if (FT_UNLIKELY(!value)) {
        return -1;
    }

    if (FT_UNLIKELY(!PyLong_Check(value))) {
        _RaiseInvalidType("int", "int", Py_TYPE(value)->tp_name);
        Py_DECREF(value);
        return -1;
    }

    unsigned char bytes[16] = { 0 };
    if (FT_UNLIKELY(PyLong_AsByteArray(value, bytes, 16, 0, 0) < 0)) {
        Py_DECREF(value);
        return -1;
    }

    static const char hex[] = "0123456789abcdef";
    *out++ = '"';
    for (uint8_t i = 0; i < 16; ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) {
            *out++ = '-';
        }

        *out++ = hex[bytes[i] >> 4];
        *out++ = hex[bytes[i] & 0xF];
    }
    *out++ = '"';

    Py_DECREF(value);
    return 38;
}

static PyObject*
convector_uuid(PyObject* obj, ConvParams* params)
{
    if (params->attr != __as_json__) {
        return Py_NewRef(obj);
    }

    PyObject* str = PyUnicode_New(38, 126);
    if (FT_UNLIKELY(str && _UUID_AsStr(PyUnicode_DATA(str), obj) < 0)) {
        Py_DECREF(str);
        return NULL;
    }
    return str;
}

static PyObject*
convector_date_and_time(PyObject* val, ConvParams* params)
{
    if (params->attr == __as_json__) {
        return PyObject_CallMethodNoArgs(val, __isoformat);
    }
    return Py_NewRef(val);
}

static PyObject*
convector_time_delta(PyObject* val, ConvParams* params)
{
    if (params->attr != __as_json__) {
        return Py_NewRef(val);
    }

    unsigned char buff[26];
    Py_ssize_t size = _TimeDelta_AsISO(val, buff);
    PyObject* res = PyUnicode_New(size, 100);
    if (FT_LIKELY(res)) {
        memcpy(PyUnicode_DATA(res), buff, size);
    }
    return res;
}

static PyObject*
convector_bytes(PyObject* val, ConvParams* params)
{
    if (params->attr == __as_json__) {
        return PyUnicode_FromEncodedObject(val, NULL, NULL);
    }
    return Py_NewRef(val);
}

static PyObject*
convector_dict(PyObject* dict, ConvParams* params)
{
    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return NULL;
    }

    PyObject* res = PyDict_New();
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    Py_ssize_t pos = 0;
    PyObject *key, *val;
    while (PyDict_Next(dict, &pos, &key, &val)) {
        key = _Convector_Obj(key, params);
        if (FT_UNLIKELY(!key)) {
            goto error;
        }

        val = _Convector_Obj(val, params);
        if (FT_UNLIKELY(!val)) {
            Py_DECREF(key);
            goto error;
        }

        int r = PyDict_SetItem(res, key, val);
        Py_DECREF(val);
        Py_DECREF(key);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    _Convector_Leave(params);
    return res;

error:
    Py_DECREF(res);
    return NULL;
}

static inline int
convector_array(PyObject* restrict* arr,
                Py_ssize_t size,
                PyObject** res,
                ConvParams* params)
{
    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return -1;
    }

    for (Py_ssize_t i = 0; i != size; i++) {
        res[i] = _Convector_Obj(arr[i], params);
        if (FT_UNLIKELY(!res[i])) {
            return -1;
        }
    }

    _Convector_Leave(params);
    return 0;
}

static PyObject*
convector_tuple(PyObject* tuple, ConvParams* params)
{
    PyObject *res, **items;
    Py_ssize_t size = PyTuple_GET_SIZE(tuple);
    const int is_list = params->attr == __as_json__;

    res = is_list ? PyList_New(size) : PyTuple_New(size);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    items = is_list ? LIST_ITEMS(res) : TUPLE_ITEMS(res);
    if (FT_UNLIKELY(convector_array(TUPLE_ITEMS(tuple), size, items, params) <
                    0)) {
        Py_DECREF(res);
        return NULL;
    }

    return res;
}

static PyObject*
convector_list(PyObject* list, ConvParams* params)
{
    Py_ssize_t size = PyList_GET_SIZE(list);
    PyObject* res = PyList_New(size);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (FT_UNLIKELY(convector_array(
                      LIST_ITEMS(list), size, LIST_ITEMS(res), params) < 0)) {
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

static PyObject*
convector_set_as_list(PyObject* set, ConvParams* params)
{
    PyObject* res = PyList_New(PySet_GET_SIZE(set));
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    Py_ssize_t i = 0;
    PyObject *val, **items = LIST_ITEMS(res);
    SetForeach(item, set)
    {
        val = _Convector_Obj(item, params);
        if (FT_UNLIKELY(!val)) {
            Py_DECREF(res);
            return NULL;
        }
        items[i++] = val;
    }

    _Convector_Leave(params);
    return res;
}

static PyObject*
convector_any_set(PyObject* set, ConvParams* params)
{
    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return NULL;
    }

    if (params->attr != __copy__) {
        return convector_set_as_list(set, params);
    }

    PyObject* res =
      Py_IS_TYPE(set, &PySet_Type) ? PySet_New(NULL) : PyFrozenSet_New(NULL);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    SetForeach(item, set)
    {
        PyObject* val = _Convector_Obj(item, params);
        if (FT_UNLIKELY(!val || PySet_Add(res, val) < 0)) {
            Py_DECREF(res);
            Py_XDECREF(val);
            return NULL;
        }
        Py_DECREF(val);
    }

    _Convector_Leave(params);
    return res;
}

static PyObject*
convector_data_model(PyObject* data_model, ConvParams* params)
{
    return params->attr == __copy__
             ? _DataModel_CallCopy(data_model)
             : _DataModel_AsDict(data_model, params, NULL, NULL);
}

static PyObject*
convector_validation_error(PyObject* val, ConvParams* params)
{
    return params->attr == __copy__ ? Py_NewRef(val)
                                    : _ValidationError_AsList(val, params);
}

static uint8_t
conv_get_sub(PyObject* val, PyObject* attr, int sub_check)
{
    if (PyObject_HasAttr(val, attr)) {
        return _CALL_POS;
    }

    PyTypeObject* tp = Py_TYPE(val);
    if (Py_IS_TYPE(tp, Py_TYPE(PyEnumType))) {
        return _ENUM_POS;
    }

    if (FT_UNLIKELY(!sub_check)) {
        return _MISSING_POS;
    }

    switch (tp->tp_flags &
            (Py_TPFLAGS_LONG_SUBCLASS | Py_TPFLAGS_UNICODE_SUBCLASS |
             Py_TPFLAGS_BYTES_SUBCLASS | Py_TPFLAGS_TUPLE_SUBCLASS |
             Py_TPFLAGS_LIST_SUBCLASS | Py_TPFLAGS_DICT_SUBCLASS)) {
        case Py_TPFLAGS_LONG_SUBCLASS:
            return _INT_POS;
        case Py_TPFLAGS_UNICODE_SUBCLASS:
            return _STR_POS;
        case Py_TPFLAGS_BYTES_SUBCLASS:
            return _BYTES_POS;
        case Py_TPFLAGS_TUPLE_SUBCLASS:
            return _TUPLE_POS;
        case Py_TPFLAGS_LIST_SUBCLASS:
            return _LIST_POS;
        case Py_TPFLAGS_DICT_SUBCLASS:
            return _DICT_POS;
    }

    if (PyType_IsSubtype(tp, PyUuidType)) {
        return _UUID_POS;
    }
    if (PyType_IsSubtype(tp, &PyFloat_Type)) {
        return _FLOAT_POS;
    }
    if (PyType_IsSubtype(tp, &PySet_Type) ||
        PyType_IsSubtype(tp, &PyFrozenSet_Type)) {
        return _SET_POS;
    }
    if (PyType_IsSubtype(tp, &PyByteArray_Type)) {
        return _BYTES_ARR_POS;
    }
    if (PyType_IsSubtype(tp, PyDateTimeAPI->DateType)) {
        return _DATE_POS;
    }
    if (PyType_IsSubtype(tp, PyDateTimeAPI->TimeType)) {
        return _TIME_POS;
    }
    if (PyType_IsSubtype(tp, PyDateTimeAPI->DateTimeType)) {
        return _DATE_TIME_POS;
    }
    if (PyType_IsSubtype(tp, PyDateTimeAPI->DeltaType)) {
        return _TIME_DELTA_POS;
    }
    if (DecimalType && PyType_IsSubtype(tp, DecimalType)) {
        return _DECIMAL_POS;
    }
    return _MISSING_POS;
}

inline uint8_t
_Conv_Get(PyObject* val, PyObject* attr, int sub_check)
{
    PyTypeObject* tp = Py_TYPE(val);
    Py_ssize_t i = GET_IND(tp);
    if (FT_LIKELY((table[i].key == tp))) {
        return table[i].value;
    }

    if (Meta_IS_SUBCLASS(tp)) {
        return _DATA_MODEL_POS;
    }
    return conv_get_sub(val, attr, sub_check);
}

int
Convector_IsConstVal(PyObject* val)
{
    switch (_Conv_Get(val, __copy__, 0)) {
        case _UUID_POS:
        case _BYTES_POS:
        case _DATE_TIME_POS:
        case _TIME_POS:
        case _DATE_POS:
        case _FLOAT_POS:
        case _STR_POS:
        case _INT_POS:
        case _NONE_POS:
        case _DECIMAL_POS:
            return 1;
        default:
            return 0;
    }
}

int
_Convector_ValidateInclude(PyObject** include, PyObject** exclude)
{
    PyObject *inc = *include, *exc = *exclude;

    if (!inc || inc == Py_None) {
        *include = NULL;
    } else if (!Py_IS_TYPE(inc, &PySet_Type)) {
        PyErr_Format(PyExc_ValueError,
                     "The parameter 'include' should be set or None, but "
                     "received '%.100s'",
                     Py_TYPE(inc)->tp_name);
        return -1;
    }

    if (!exc || exc == Py_None) {
        *exclude = NULL;
    } else if (!Py_IS_TYPE(exc, &PySet_Type)) {
        PyErr_Format(PyExc_ValueError,
                     "The parameter 'exclude' should be set or None, but "
                     "received '%.100s'",
                     Py_TYPE(exc)->tp_name);
        return -1;
    }
    return 0;
}

PyObject*
_Сonvector_СallFunc(PyObject* call, PyObject* val, ConvParams* params)
{
    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return NULL;
    }

    PyObject* res;
    if (PyFunction_Check(call) && _FUNC_GET_ACNT(call) == 2) {
        PyObject* info = _ConvParams_GetSerializationInfo(params);
        res = info ? PyObject_CallTwoArg(call, val, info) : NULL;
    } else {
        res = PyObject_CallOneArg(call, val);
    }

    _Convector_Leave(params);
    return res;
}

PyObject*
_Convector_CallMethod(PyObject* val, ConvParams* params)
{
    PyObject* res;
    if (FT_LIKELY(params->attr != __copy__)) {
        PyObject* call =
          PyObject_GetAttr((PyObject*)Py_TYPE(val), params->attr);
        if (FT_UNLIKELY(!call)) {
            return NULL;
        }

        res = _Сonvector_СallFunc(call, val, params);
        Py_DECREF(call);
    } else {
        if (FT_UNLIKELY(!_Convector_Enter(params))) {
            return NULL;
        }

        res = PyObject_CallMethodNoArgs(val, params->attr);
        _Convector_Leave(params);
    }
    return res;
}

static inline int
setstate_set_dict(PyObject* self, PyObject* state)
{
    PyObject** addr_dict = _PyObject_GetDictPtr(self);
    if (!addr_dict) {
        return 0;
    }

    if (*addr_dict) {
        return PyDict_Update(*addr_dict, state);
    }

    if (PyDict_CheckExact(state)) {
        *addr_dict = Py_NewRef(state);
        return 0;
    }

    *addr_dict = PyObject_CallOneArg((PyObject*)&PyDict_Type, state);
    return *addr_dict ? 0 : -1;
}

static inline int
setstate_update_slots(PyObject* self, PyObject* slotstate)
{
    slotstate = PyObject_Call((PyObject*)&PyDict_Type, slotstate, NULL);
    if (FT_UNLIKELY(!slotstate)) {
        return -1;
    }

    Py_ssize_t pos = 0;
    PyObject *name, *val;
    while (PyDict_Next(slotstate, &pos, &name, &val)) {
        if (FT_UNLIKELY(PyObject_GenericSetAttr(self, name, val) < 0)) {
            Py_DECREF(slotstate);
            return -1;
        }
    }
    Py_DECREF(slotstate);
    return 0;
}

static inline int
set_state(PyObject* self, PyObject* state, ConvParams* params)
{
    PyObject* copy = _Convector_Obj(state, params);
    if (!copy) {
        return -1;
    }

    PyObject* func = _Object_Gettr(self, __setstate__);
    if (func) {
        PyObject* tmp = PyObject_CallOneArg(func, copy);
        Py_DECREF(copy);
        return tmp ? 0 : -1;
    }

    PyObject* slotstate = Py_None;
    if (PyTuple_Check(copy) && PyTuple_GET_SIZE(copy) == 2) {
        state = PyTuple_GET_ITEM(copy, 0);
        slotstate = PyTuple_GET_ITEM(copy, 1);
    } else {
        state = copy;
    }

    if (state != Py_None && setstate_set_dict(self, state) < 0) {
        Py_DECREF(copy);
        return -1;
    }

    if (slotstate != Py_None && setstate_update_slots(self, slotstate) < 0) {
        Py_DECREF(copy);
        return -1;
    }

    Py_DECREF(copy);
    return 0;
}

static inline int
set_listiter(PyObject* self, PyObject* listiter, ConvParams* params)
{
    PyObject* iter = PyObject_GetIter(listiter);
    if (!iter) {
        return -1;
    }

    for (;;) {
        PyObject* item;
        int r = _PyIter_GetNext(iter, &item);
        if (!r) {
            break;
        } else if (r < 0) {
            goto error;
        }

        PyObject* val = _Convector_ObjDecrefVal(item, params);
        if (FT_UNLIKELY(!val)) {
            goto error;
        }

        PyObject* tmp = PyObject_CallMethodOneArg(self, __append, val);
        Py_DECREF(val);
        if (FT_UNLIKELY(!tmp)) {
            goto error;
        }
    }

    Py_DECREF(iter);
    return 0;

error:
    Py_DECREF(iter);
    return -1;
}

static inline int
set_dictiter(PyObject* self, PyObject* dictiter, ConvParams* params)
{
    PyObject* dict = PyObject_CallOneArg((PyObject*)&PyDict_Type, dictiter);
    if (FT_UNLIKELY(!dict)) {
        return -1;
    }

    Py_ssize_t pos = 0;
    PyObject *key, *val;
    while (PyDict_Next(dict, &pos, &key, &val)) {
        key = _Convector_Obj(key, params);
        if (FT_UNLIKELY(!key)) {
            goto error;
        }

        val = _Convector_Obj(val, params);
        if (FT_UNLIKELY(!val)) {
            Py_DECREF(key);
            goto error;
        }

        int r = PyObject_SetItem(self, key, val);
        Py_DECREF(key);
        Py_DECREF(val);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }
    return 0;

error:
    Py_DECREF(dict);
    return -1;
}

static inline PyObject*
reconstruct(PyObject* rv, ConvParams* params)
{
    if (!PyTuple_Check(rv)) {
        return _RaiseInvalidReturnType(
          "__reduce_ex__", "tuple", Py_TYPE(rv)->tp_name);
    }

    Py_ssize_t size = PyTuple_GET_SIZE(rv);
    PyObject *res, *func, *args;
    func = PyTuple_GET_ITEM(rv, 0);
    args = PyTuple_GET_ITEM(rv, 1);
    if (!PyTuple_Check(args)) {
        return _RaiseInvalidType("args", "tuple", Py_TYPE(args)->tp_name);
    }

    res = PyObject_Vectorcall(
      func, TUPLE_ITEMS(args), PyTuple_GET_SIZE(args), NULL);
    if (!res) {
        return NULL;
    }

    if (size > 2) {
        PyObject* state = PyTuple_GET_ITEM(rv, 2);
        if (state != Py_None && set_state(res, state, params) < 0) {
            goto error;
        }
    }

    if (size > 3) {
        PyObject* listiter = PyTuple_GET_ITEM(rv, 3);
        if (listiter != Py_None && set_listiter(res, listiter, params) < 0) {
            goto error;
        }
    }

    if (size > 4) {
        PyObject* dictiter = PyTuple_GET_ITEM(rv, 4);
        if (dictiter != Py_None && set_dictiter(res, dictiter, params) < 0) {
            goto error;
        }
    }

    return res;

error:
    Py_DECREF(res);
    return NULL;
}

static PyObject*
convector_handle_missing(PyObject* val, ConvParams* params)
{
    if (params->attr != __copy__) {
        goto error;
    }

    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return NULL;
    }

    // try to pickle
    PyObject *rv, *reductor = _Object_Gettr(val, __reduce_ex__);
    if (reductor) {
        rv = PyObject_CallOneArg(reductor, Long_Four);
        Py_DECREF(reductor);
    } else {
        reductor = _Object_Gettr(val, __reduce__);
        if (!reductor) {
            goto error;
        }
        rv = PyObject_CallNoArgs(reductor);
        Py_DECREF(reductor);
    }

    if (!rv || PyUnicode_CheckExact(rv)) {
        return rv;
    }

    PyObject* res = reconstruct(rv, params);
    _Convector_Leave(params);
    Py_DECREF(rv);
    return res;

error:
    return PyErr_Format(PyExc_TypeError,
                        "'%.100s' object has no '%U' method",
                        Py_TYPE(val)->tp_name,
                        params->attr);
}

static const ObjectConverter convector_object[CONVECTOR_SIZE] = {
    [_MISSING_POS] = convector_handle_missing,
    [_CALL_POS] = _Convector_CallMethod,
    [_DECIMAL_POS] = convector_decimal,
    [_INT_POS] = convector_const,
    [_STR_POS] = convector_const,
    [_LIST_POS] = convector_list,
    [_DICT_POS] = convector_dict,
    [_ENUM_POS] = convector_enum,
    [_UUID_POS] = convector_uuid,
    [_BOOL_POS] = convector_const,
    [_NONE_POS] = convector_const,
    [_SET_POS] = convector_any_set,
    [_FLOAT_POS] = convector_const,
    [_BYTES_POS] = convector_bytes,
    [_TUPLE_POS] = convector_tuple,
    [_BYTES_ARR_POS] = convector_bytes,
    [_DATE_POS] = convector_date_and_time,
    [_TIME_POS] = convector_date_and_time,
    [_DATA_MODEL_POS] = convector_data_model,
    [_TIME_DELTA_POS] = convector_time_delta,
    [_DATE_TIME_POS] = convector_date_and_time,
    [_VALIDATION_ERR_POS] = convector_validation_error,
};

inline PyObject*
_Convector_Obj(PyObject* restrict val, ConvParams* params)
{
    register uint8_t ind =
      _Conv_Get(val, params->attr, params->attr == __as_json__);
    return convector_object[ind](val, params);
}

inline PyObject*
_Convector_ObjDecrefVal(PyObject* val, ConvParams* params)
{
    PyObject* res = _Convector_Obj(val, params);
    Py_DECREF(val);
    return res;
}

inline PyObject*
PyCopy(PyObject* obj)
{
    ConvParams conv_params = ConvParams_Create(__copy__);
    PyObject* res = _Convector_Obj(obj, &conv_params);
    _ConvParams_Free(&conv_params);
    return res;
}

inline PyObject*
AsDict(PyObject* obj)
{
    ConvParams conv_params = ConvParams_Create(__as_dict__);
    PyObject* res = _Convector_Obj(obj, &conv_params);
    _ConvParams_Free(&conv_params);
    return res;
}

inline void
_ConvParams_Free(ConvParams* params)
{
    Py_CLEAR(params->serialization_info);
}

PyObject*
_ConvParams_GetSerializationInfo(ConvParams* params)
{
    if (FT_LIKELY(params->serialization_info)) {
        return params->serialization_info;
    }

    SerializationInfo* self =
      Object_New(SerializationInfo, &SerializationInfo_Type);
    if (FT_LIKELY(self)) {
        params->serialization_info = (PyObject*)self;
        self->context = Py_XNewRef(params->context);
        self->exclude_unset = params->exclude_unset;
        self->exclude_none = params->exclude_none;
        self->custom_ser = params->custom_ser;
        self->by_alias = params->by_alias;
    }

    // borrow ref
    return (PyObject*)self;
}

static void
serialization_info_dealloc(SerializationInfo* self)
{
    Py_XDECREF(self->context);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
serialization_info_new(PyTypeObject* cls, PyObject* args, PyObject* kwargs)
{
    PyObject* context = NULL;
    char* kwlist[] = { "context",    "exclude_unset", "exclude_none",
                       "use_custom", "by_alias",      NULL };
    int exclude_unset = 0, exclude_none = 0, use_custom = 1, by_alias = 1;
    if (FT_UNLIKELY(
          !PyArg_ParseTupleAndKeywords(args,
                                       kwargs,
                                       "|Opppp:SerializationInfo.__new__",
                                       kwlist,
                                       &context,
                                       &exclude_unset,
                                       &exclude_none,
                                       &use_custom,
                                       &by_alias))) {
        return NULL;
    }

    SerializationInfo* self = Object_New(SerializationInfo, cls);
    if (FT_LIKELY(self)) {
        self->context = Py_XNewRef(context);
        self->exclude_unset = exclude_unset;
        self->exclude_none = exclude_none;
        self->custom_ser = use_custom;
        self->by_alias = by_alias;
    }
    return (PyObject*)self;
}

static PyObject*
serialization_info_repr(SerializationInfo* self)
{
    return PyUnicode_FromFormat(
      "SerializationInfo(context=%R, exclude_unset=%R, exclude_none=%R, "
      "use_custom=%R, by_alias=%R)",
      self->context,
      self->exclude_unset ? Py_True : Py_False,
      self->exclude_none ? Py_True : Py_False,
      self->custom_ser ? Py_True : Py_False,
      self->by_alias ? Py_True : Py_False);
}

static PyMemberDef serialization_info_members[] = {
    { "exclude_unset",
      T_BOOL,
      offsetof(SerializationInfo, exclude_unset),
      READONLY,
      NULL },
    { "exclude_none",
      T_BOOL,
      offsetof(SerializationInfo, exclude_none),
      READONLY,
      NULL },
    { "by_alias",
      T_BOOL,
      offsetof(SerializationInfo, by_alias),
      READONLY,
      NULL },
    { "use_custom",
      T_BOOL,
      offsetof(SerializationInfo, custom_ser),
      READONLY,
      NULL },
    { "context",
      T_OBJECT,
      offsetof(SerializationInfo, context),
      READONLY,
      NULL },
    { NULL }
};

PyTypeObject SerializationInfo_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_dealloc = (destructor)serialization_info_dealloc,
    .tp_repr = (reprfunc)serialization_info_repr,
    .tp_name = "frost_typing.SerializationInfo",
    .tp_basicsize = sizeof(SerializationInfo),
    .tp_new = (newfunc)serialization_info_new,
    .tp_members = serialization_info_members,
};

int
convector_setup(void)
{
    PyDateTime_IMPORT;
    if (!PyDateTimeAPI || PyType_Ready(&SerializationInfo_Type) < 0) {
        return -1;
    }

    PtrEntry entries[19] = {
        { &PySet_Type, _SET_POS },
        { &PyLong_Type, _INT_POS },
        { PyNone_Type, _NONE_POS },
        { &PyBool_Type, _BOOL_POS },
        { &PyList_Type, _LIST_POS },
        { &PyDict_Type, _DICT_POS },
        { &PyUnicode_Type, _STR_POS },
        { &PyTuple_Type, _TUPLE_POS },
        { &PyFloat_Type, _FLOAT_POS },
        { &PyBytes_Type, _BYTES_POS },
        { &PyFrozenSet_Type, _SET_POS },
        { &PyByteArray_Type, _BYTES_ARR_POS },
        { PyDateTimeAPI->DateType, _DATE_POS },
        { PyDateTimeAPI->TimeType, _TIME_POS },
        { PyDateTimeAPI->DeltaType, _TIME_DELTA_POS },
        { &_ValidationErrorType, _VALIDATION_ERR_POS },
        { PyDateTimeAPI->DateTimeType, _DATE_TIME_POS },
        { PyUuidType, _UUID_POS },
        { DecimalType, _DECIMAL_POS },
    };

    init_lookup(entries, (sizeof(entries) / sizeof(PtrEntry)) - !DecimalType);
    return 0;
}

void
convector_free(void)
{
}