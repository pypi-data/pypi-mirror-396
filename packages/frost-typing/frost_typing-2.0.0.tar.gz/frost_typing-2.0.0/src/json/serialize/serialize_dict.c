#include "convector.h"
#include "utils_common.h"
#include "validator/py_typing.h"
#include "json/json.h"

static inline int
key_as_json(WriteBuffer* buff, PyObject* key, ConvParams* params)
{
    PyTypeObject* tp_key = Py_TYPE(key);
    if (tp_key->tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS) {
        return _Unicode_AsJson(buff, key, params);
    }

    if (tp_key->tp_flags & Py_TPFLAGS_LONG_SUBCLASS && tp_key != &PyBool_Type) {
        buff->buffer[buff->size++] = '"';
        if (_Long_AsJson(buff, key, params) < 0) {
            return -1;
        }
        buff->buffer[buff->size++] = '"';
        return 0;
    }

    if (tp_key == &PyFloat_Type || PyType_IsSubtype(tp_key, &PyFloat_Type)) {
        buff->buffer[buff->size++] = '"';
        if (_Float_AsJson(buff, key, params) < 0) {
            return -1;
        }
        buff->buffer[buff->size++] = '"';
        return 0;
    }

    if (tp_key == PyUuidType || PyType_IsSubtype(tp_key, PyUuidType)) {
        return _Uuid_AsJson(buff, key, params);
    }

    PyErr_Format(JsonEncodeError,
                 "Dict key must be a string, real"
                 ", or integer, or uuid, not '%.100s'",
                 tp_key->tp_name);
    return -1;
}

int
_Dict_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    if (!PyDict_GET_SIZE(obj)) {
        return WriteBuffer_ConcatSize(buff, "{}", 2);
    }

    if (FT_UNLIKELY(!_Convector_Enter(params) ||
                    WriteBuffer_ConcatChar(buff, '{') < 0)) {
        return -1;
    }

    Py_ssize_t pos = 0;
    PyObject *key, *val;
    while (PyDict_Next(obj, &pos, &key, &val)) {
        if (pos > 1) {
            buff->buffer[buff->size++] = ',';
        }

        if (FT_UNLIKELY(key_as_json(buff, key, params) < 0)) {
            return -1;
        }

        buff->buffer[buff->size++] = ':';
        if (FT_UNLIKELY(_PyObject_AsJson(buff, val, params) < 0)) {
            return -1;
        }
    }
    buff->buffer[buff->size++] = '}';
    _Convector_Leave(params);
    return 0;
}
