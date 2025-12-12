#include "convector.h"
#include "data_model.h"
#include "datetime.h"
#include "math.h"
#include "meta_model.h"
#include "stdint.h"
#include "validator/validator.h"
#include "json/json.h"

typedef int (*ConverterFunc)(WriteBuffer*, PyObject*, ConvParams*);
PyObject* JsonEncodeError;

static int
py_enum_as_json(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    PyObject* value = PyObject_GetAttr(obj, __value);
    return value ? _PyObject_AsJsonDecrefVal(buff, value, params) : -1;
}

int
_Uuid_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* params)
{
    if (FT_UNLIKELY(WriteBuffer_Resize(buff, buff->size + 38) < 0)) {
        return -1;
    }

    Py_ssize_t size = _UUID_AsStr(buff->buffer + buff->size, obj);
    if (FT_LIKELY(size != -1)) {
        buff->size += size;
        return 0;
    }
    return -1;
}

static int
py_bool_as_json(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* params)
{
    if (obj == Py_True) {
        return WriteBuffer_ConcatSize(buff, "true", 4);
    }
    return WriteBuffer_ConcatSize(buff, "false", 5);
}

static int
py_none_as_json(WriteBuffer* buff,
                UNUSED PyObject* obj,
                UNUSED ConvParams* params)
{
    return WriteBuffer_ConcatSize(buff, "null", 4);
}

static int
call_as_json(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    PyObject* res = _Convector_CallMethod(obj, params);
    return res ? _PyObject_AsJsonDecrefVal(buff, res, params) : -1;
}

static int
any_as_str_json(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return -1;
    }

    PyObject* op = PyObject_Str(obj);
    int r = op ? _PyObject_AsJsonDecrefVal(buff, op, params) : -1;
    _Convector_Leave(params);
    return r;
}

static int
missing_as_json(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    if (FT_LIKELY(params->str_unknown)) {
        return any_as_str_json(buff, obj, params);
    }

    PyErr_Format(JsonEncodeError,
                 "'%.100s' object has no '%U' method",
                 Py_TYPE(obj)->tp_name,
                 __as_json__);
    return -1;
}

static const ConverterFunc convector_object[CONVECTOR_SIZE] = {
    [_VALIDATION_ERR_POS] = _ValidationError_AsJson,
    [_TIME_DELTA_POS] = _TimeDelta_AsJson,
    [_BYTES_ARR_POS] = _BytesArray_AsJson,
    [_DATA_MODEL_POS] = _MetaModel_AsJson,
    [_DATE_TIME_POS] = _Datetime_AsJson,
    [_DECIMAL_POS] = any_as_str_json,
    [_MISSING_POS] = missing_as_json,
    [_ENUM_POS] = py_enum_as_json,
    [_BOOL_POS] = py_bool_as_json,
    [_NONE_POS] = py_none_as_json,
    [_FLOAT_POS] = _Float_AsJson,
    [_BYTES_POS] = _Bytes_AsJson,
    [_TUPLE_POS] = _Tuple_AsJson,
    [_STR_POS] = _Unicode_AsJson,
    [_DATE_POS] = _Date_AsJson,
    [_UUID_POS] = _Uuid_AsJson,
    [_TIME_POS] = _Time_AsJson,
    [_DICT_POS] = _Dict_AsJson,
    [_LIST_POS] = _List_AsJson,
    [_CALL_POS] = call_as_json,
    [_INT_POS] = _Long_AsJson,
    [_SET_POS] = _Set_AsJson,
};

inline int
_PyObject_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    const uint8_t ind = _Conv_Get(obj, __as_json__, 1);
    return convector_object[ind](buff, obj, params);
}

inline int
_PyObject_AsJsonDecrefVal(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    int r = _PyObject_AsJson(buff, obj, params);
    Py_DECREF(obj);
    return r;
}

PyObject*
PyObject_AsJson(PyObject* const* args,
                Py_ssize_t nargsf,
                PyObject* kwnames,
                int in_file)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    if (!PyCheck_ArgsCnt("dumps", nargs, 1 + in_file)) {
        return NULL;
    }

    WriteBuffer buff;
    PyObject *obj = (PyObject*)*args, *writer = NULL;
    if (in_file) {
        writer = PyObject_GetAttr((PyObject*)args[1], __write);
        if (!writer) {
            return NULL;
        }
    }

    ConvParams params = ConvParams_Create(__as_json__);
    if (!kwnames) {
        goto done;
    }

    PyObject* argsbuf[6] = { NULL };
    static const char* const kwlist[] = {
        "by_alias",    "exclude_unset", "exclude_none", "use_custom",
        "str_unknown", "context",       NULL,
    };

    static _PyArg_Parser _parser = {
        .keywords = kwlist,
        .fname = "dumps",
        .kwtuple = NULL,
    };

    args += 1 + in_file;
    nargs -= 1 - in_file;
    if (FT_UNLIKELY(!PyArg_UnpackKeywords(args,
                                          nargs,
                                          NULL,
                                          kwnames,
                                          &_parser,
                                          0, /*minpos*/
                                          0, /*maxpos*/
                                          0, /*minkw*/
                                          argsbuf))) {
        return NULL;
    }

    for (Py_ssize_t i = 0; i != 5; i++) {
        if (FT_UNLIKELY(!_ValidateArg(argsbuf[i], &PyBool_Type, kwlist[i]))) {
            return NULL;
        }
    }

    params.by_alias = argsbuf[0] != Py_False;
    params.exclude_unset = argsbuf[1] == Py_True;
    params.exclude_none = argsbuf[2] == Py_True;
    params.custom_ser = argsbuf[3] != Py_False;
    params.str_unknown = argsbuf[4] == Py_True;
    params.context = argsbuf[5];

done:
    if (FT_UNLIKELY(WriteBuffer_init(&buff, writer) < 0)) {
        Py_XDECREF(writer);
        return NULL;
    }

    if (FT_UNLIKELY(_PyObject_AsJson(&buff, obj, &params) < 0)) {
        _ConvParams_Free(&params);
        WriteBuffer_Free(&buff);
        return NULL;
    }

    PyObject* res = WriteBuffer_Finish(&buff);
    _ConvParams_Free(&params);
    return res;
}

int
encoder_setup(void)
{
    if (json_date_time_setup() < 0) {
        return -1;
    }

    PyDateTime_IMPORT;
    if (PyDateTimeAPI == NULL) {
        return -1;
    }

    JsonEncodeError =
      PyErr_NewException("frost_typing.JsonEncodeError", NULL, NULL);
    if (JsonEncodeError == NULL) {
        return -1;
    }
    return 0;
}

void
encoder_free(void)
{
    json_date_time_free();
}