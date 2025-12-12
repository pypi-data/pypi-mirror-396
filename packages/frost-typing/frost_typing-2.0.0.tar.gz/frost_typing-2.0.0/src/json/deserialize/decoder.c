#include "utils_common.h"
#include "json/json.h"

static PyObject*
json_parse_infinity(ReadBuffer*);
static PyObject*
json_parse_true(ReadBuffer*);
static PyObject*
json_parse_false(ReadBuffer*);
static PyObject*
json_parse_null(ReadBuffer*);
static PyObject*
json_parse_nan(ReadBuffer*);
static PyObject*
json_parse_array(ReadBuffer* buffer);
static PyObject*
json_parse_negative(ReadBuffer*);
static PyObject*
json_parse_dict(ReadBuffer*);
PyObject* JsonDecodeError;

PyObject*
_JsonParse_Continue(UNUSED ReadBuffer* buff)
{
    return NULL;
}

const _JsonParser _JsonParse_Router[256] = {
    ['I'] = json_parse_infinity,  ['t'] = json_parse_true,
    ['f'] = json_parse_false,     ['n'] = json_parse_null,
    ['N'] = json_parse_nan,       ['-'] = json_parse_negative,
    ['"'] = JsonParse_String,     ['['] = json_parse_array,
    ['{'] = json_parse_dict,      ['0'] = JsonParse_Numeric,
    ['1'] = JsonParse_Numeric,    ['2'] = JsonParse_Numeric,
    ['3'] = JsonParse_Numeric,    ['4'] = JsonParse_Numeric,
    ['5'] = JsonParse_Numeric,    ['6'] = JsonParse_Numeric,
    ['7'] = JsonParse_Numeric,    ['8'] = JsonParse_Numeric,
    ['9'] = JsonParse_Numeric,    ['\b'] = _JsonParse_Continue,
    ['\f'] = _JsonParse_Continue, ['\n'] = _JsonParse_Continue,
    ['\r'] = _JsonParse_Continue, ['\t'] = _JsonParse_Continue,
    [' '] = _JsonParse_Continue,
};

void
_JsonParse_RaiseFormat(ReadBuffer* buffer, const char* format)
{
    Py_ssize_t line, column;
    ReadBuffer_GetPos(buffer, &column, &line);
    char ch = buffer->iter[buffer->iter == buffer->end_data ? -1 : 0];
    PyErr_Format(JsonDecodeError, format, line, column, ch);
}

inline void
_JsonParse_Raise(ReadBuffer* buffer)
{
    _JsonParse_RaiseFormat(buffer,
                           "invalid literal: line %zu"
                           " column %zu (char '%c')");
}

static PyObject*
json_parse_dict(ReadBuffer* buffer)
{
    if (FT_UNLIKELY(_Decode_Enter(buffer) < 0)) {
        return NULL;
    }

    PyObject* dict = PyDict_New();
    if (!dict) {
        return NULL;
    }

    PyObject* key = NULL;
    uint8_t expect_key = 1;
    const char* end = buffer->end_data;
    Py_ssize_t cnt_sep = 0, dict_size = 0;

    for (buffer->iter++; buffer->iter != end; buffer->iter++) {
        unsigned char ch = (unsigned char)*buffer->iter;
        _JsonParser p = _JsonParse_Router[ch];
        if (p) {
            if (p == _JsonParse_Continue) {
                continue;
            }

            if (expect_key) {
                if (FT_UNLIKELY(key)) {
                    goto error;
                }

                key = JsonParse_StringKey(buffer);
                if (FT_UNLIKELY(!key)) {
                    goto error;
                }
            } else if (FT_UNLIKELY(!key)) {
                goto error;
            } else {
                PyObject* tmp = p(buffer);
                if (FT_UNLIKELY(!tmp)) {
                    goto error;
                }

                int r = Dict_SetItem_String(dict, key, tmp);
                Py_DECREF(key);
                Py_DECREF(tmp);
                dict_size++;
                key = NULL;
                if (FT_UNLIKELY(r < 0)) {
                    goto error;
                }
            }

            buffer->iter--;
            continue;
        }

        if (ch == ':') {
            if (FT_LIKELY(expect_key && key)) {
                expect_key = 0;
                continue;
            }
        } else if (ch == ',') {
            if (FT_LIKELY(!expect_key && !key && (++cnt_sep == dict_size))) {
                expect_key = 1;
                continue;
            }
        } else if (ch == '}') {
            if (FT_LIKELY(!key &&
                          ((expect_key && !cnt_sep && !dict_size) ||
                           (!expect_key && cnt_sep == (dict_size - 1))))) {
                buffer->iter++;
                _Decode_Leave(buffer);
                return dict;
            }
        }
        goto error;
    }

error:
    Py_XDECREF(key);
    Py_DECREF(dict);
    return NULL;
}

PyObject*
json_parse_array(ReadBuffer* buffer)
{
    if (FT_UNLIKELY(_Decode_Enter(buffer) < 0)) {
        return NULL;
    }

    PyObject* list = PyList_New(0);
    if (FT_UNLIKELY(!list)) {
        return NULL;
    }

    Py_ssize_t cnt_sep = 0;
    const char* end = buffer->end_data;
    for (buffer->iter++; buffer->iter != end; buffer->iter++) {
        unsigned char ch = (unsigned char)*buffer->iter;
        _JsonParser p = _JsonParse_Router[ch];
        if (p) {
            if (p == _JsonParse_Continue) {
                continue;
            }

            PyObject* tmp = p(buffer);
            if (FT_UNLIKELY(!tmp || _PyList_Append_Decref(list, tmp) < 0)) {
                goto error;
            }
            buffer->iter--;
            continue;
        }

        const Py_ssize_t size = Py_SIZE(list);
        if (ch == ',') {
            if (FT_LIKELY(++cnt_sep == size)) {
                continue;
            }
        } else if (ch == ']') {
            if (FT_LIKELY(!(cnt_sep && size) || cnt_sep == (size - 1))) {
                buffer->iter++;
                _Decode_Leave(buffer);
                return list;
            }
        }
        goto error;
    }

error:
    Py_DECREF(list);
    return NULL;
}

static inline int
json_parse_pattern(ReadBuffer* buff,
                   const char* pattern,
                   Py_ssize_t pattern_size)
{
    if (FT_UNLIKELY(((buff->end_data - buff->iter) < pattern_size) ||
                    memcmp(buff->iter, pattern, pattern_size))) {
        return 0;
    }
    buff->iter += pattern_size;
    return 1;
}

static PyObject*
json_parse_null(ReadBuffer* buff)
{
    return json_parse_pattern(buff, "null", 4) ? Py_NewRef(Py_None) : NULL;
}

static PyObject*
json_parse_true(ReadBuffer* buff)
{
    return json_parse_pattern(buff, "true", 4) ? Py_NewRef(Py_True) : NULL;
}

static PyObject*
json_parse_false(ReadBuffer* buff)
{
    return json_parse_pattern(buff, "false", 5) ? Py_NewRef(Py_False) : NULL;
}

static PyObject*
json_parse_nan(ReadBuffer* buff)
{
    return json_parse_pattern(buff, "NaN", 3) ? PyFloat_FromDouble(NAN) : NULL;
}

static PyObject*
json_parse_infinity(ReadBuffer* buff)
{
    return json_parse_pattern(buff, "Infinity", 8)
             ? PyFloat_FromDouble(INFINITY)
             : NULL;
}

static PyObject*
json_parse_n_infinity(ReadBuffer* buff)
{
    return json_parse_pattern(buff, "-Infinity", 9)
             ? PyFloat_FromDouble(-INFINITY)
             : NULL;
}

static PyObject*
json_parse_negative(ReadBuffer* buff)
{
    char* next = buff->iter + 1;
    if (FT_UNLIKELY(next != buff->end_data && *next == 'I')) {
        return json_parse_n_infinity(buff);
    }
    return JsonParse_Numeric(buff);
}

inline PyObject*
_JsonParse(ReadBuffer* buff)
{
    for (; buff->iter != buff->end_data; buff->iter++) {
        _JsonParser p = _JsonParse_Router[(unsigned char)*buff->iter];
        if (p == _JsonParse_Continue) {
            continue;
        }
        if (p) {
            return p(buff);
        }
        return NULL;
    }
    return NULL;
}

static int
json_parse_get_buffer(ReadBuffer* buff, PyObject* obj)
{
    buff->nesting_level = 0;
    char* s;

    if (PyBytes_Check(obj)) {
        s = PyBytes_AS_STRING(obj);
        buff->start = s;
        buff->iter = s;
        buff->end_data = s + Py_SIZE(obj);
        buff->obj = Py_NewRef(obj);
        return 0;
    }

    if (PyUnicode_Check(obj)) {
        PyObject* bytes = PyUnicode_EncodeFSDefault(obj);
        if (!bytes) {
            return -1;
        }
        s = PyBytes_AS_STRING(bytes);
        buff->start = s;
        buff->iter = s;
        buff->end_data = s + Py_SIZE(bytes);
        buff->obj = bytes;
        return 0;
    }
    if (PyByteArray_Check(obj)) {
        s = PyByteArray_AS_STRING(obj);
        buff->start = s;
        buff->iter = s;
        buff->end_data = s + Py_SIZE(obj);
        buff->obj = Py_NewRef(obj);
        return 0;
    }
    _RaiseInvalidType(
      "0", "string, a bytes-like object", Py_TYPE(obj)->tp_name);
    return -1;
}

static int
json_parse_skip(ReadBuffer* buff)
{
    for (; buff->iter != buff->end_data; buff->iter++) {
        _JsonParser p = _JsonParse_Router[(unsigned char)*buff->iter];
        if (p == _JsonParse_Continue) {
            continue;
        }

        if (FT_LIKELY(p)) {
            return 1;
        }

        break;
    }

    _JsonParse_Raise(buff);
    return 0;
}

int
JsonParse_GetBuffer(ReadBuffer* buff, PyObject* obj)
{
    if (FT_UNLIKELY(json_parse_get_buffer(buff, obj) < 0)) {
        return -1;
    }

    if (FT_UNLIKELY(buff->iter == buff->end_data)) {
        PyErr_Format(JsonDecodeError,
                     "Expecting value: line 1 column 1 (char 0)");
        return -1;
    }

    if (FT_UNLIKELY(!json_parse_skip(buff))) {
        ReadBuffer_Free(buff);
        return -1;
    }
    return 0;
}

inline int
_JsonParse_CheckEnd(ReadBuffer* buff)
{
    // Check that all characters at the end are not significant
    for (; buff->iter < buff->end_data; buff->iter++) {
        if (_JsonParse_Router[(unsigned char)*buff->iter] !=
            _JsonParse_Continue) {
            return -1;
        }
    }
    return 0;
}

int
JsonParse_CheckEnd(ReadBuffer* buff)
{
    if (FT_UNLIKELY(_JsonParse_CheckEnd(buff) < 0)) {
        _JsonParse_Raise(buff);
        return -1;
    }
    return 0;
}

static inline PyObject*
json_parse(ReadBuffer* buff)
{
    PyObject* tmp = _JsonParse(buff);
    if (!tmp) {
        if (!PyErr_Occurred()) {
            _JsonParse_Raise(buff);
        }
        return NULL;
    }

    if (FT_UNLIKELY(JsonParse_CheckEnd(buff) < 0)) {
        Py_DECREF(tmp);
        return NULL;
    }
    return tmp;
}

PyObject*
JsonParse(PyObject* obj)
{
    ReadBuffer buff;
    if (FT_UNLIKELY(JsonParse_GetBuffer(&buff, obj) < 0)) {
        return NULL;
    }

    PyObject* res = json_parse(&buff);
    ReadBuffer_Free(&buff);
    return res;
}

int
decoder_setup(void)
{
    JsonDecodeError =
      PyErr_NewException("frost_typing.JsonDecodeError", NULL, NULL);
    return JsonDecodeError ? 0 : -1;
}

void
decoder_free(void)
{
    Py_DECREF(JsonDecodeError);
    deserialize_string_free();
}