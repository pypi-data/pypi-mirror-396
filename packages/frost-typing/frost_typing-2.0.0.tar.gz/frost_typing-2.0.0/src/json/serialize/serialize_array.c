#include "convector.h"
#include "utils_common.h"
#include "json/json.h"

static inline int
array_as_json(WriteBuffer* buff,
              PyObject** data_ptr,
              Py_ssize_t length,
              ConvParams* params)
{
    if (FT_UNLIKELY(!length)) {
        return WriteBuffer_ConcatSize(buff, "[]", 2);
    }

    if (FT_UNLIKELY(!_Convector_Enter(params) ||
                    WriteBuffer_ConcatChar(buff, '[') < 0)) {
        return -1;
    }

    if (FT_UNLIKELY(_PyObject_AsJson(buff, *data_ptr, params) < 0)) {
        return -1;
    }

    for (Py_ssize_t i = 1; i != length; i++) {
        buff->buffer[buff->size++] = ',';
        if (FT_UNLIKELY(_PyObject_AsJson(buff, data_ptr[i], params) < 0)) {
            return -1;
        }
    }

    buff->buffer[buff->size++] = ']';
    _Convector_Leave(params);
    return 0;
}

int
_Set_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    if (FT_UNLIKELY(!PySet_GET_SIZE(obj))) {
        return WriteBuffer_ConcatSize(buff, "[]", 2);
    }

    if (FT_UNLIKELY(!_Convector_Enter(params) ||
                    WriteBuffer_ConcatChar(buff, '[') < 0)) {
        return -1;
    }

    PyObject* item;
    Py_ssize_t pos = 0;
    _PySet_Next(obj, &pos, &item);
    if (FT_UNLIKELY(_PyObject_AsJson(buff, item, params) < 0)) {
        return -1;
    }

    while (_PySet_Next(obj, &pos, &item)) {
        buff->buffer[buff->size++] = ',';
        if (FT_UNLIKELY(_PyObject_AsJson(buff, item, params) < 0)) {
            return -1;
        }
    }

    buff->buffer[buff->size++] = ']';
    _Convector_Leave(params);
    return 0;
}

int
_Tuple_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    return array_as_json(buff, TUPLE_ITEMS(obj), PyTuple_GET_SIZE(obj), params);
}

int
_List_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    return array_as_json(buff, LIST_ITEMS(obj), PyList_GET_SIZE(obj), params);
}
