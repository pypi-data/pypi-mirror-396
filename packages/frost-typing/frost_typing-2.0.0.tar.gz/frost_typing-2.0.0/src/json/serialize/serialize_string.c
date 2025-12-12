#include "utils_common.h"
#include "json/json.h"

static const char hex_digits[] = "0123456789ABCDEF";
static const unsigned char escape_table[256] = {
    [0x00] = 255, [0x01] = 255, [0x02] = 255,  [0x03] = 255, [0x04] = 255,
    [0x05] = 255, [0x06] = 255, [0x07] = 255,  [0x0b] = 255, [0x0e] = 255,
    [0x0f] = 255, [0x10] = 255, [0x11] = 255,  [0x12] = 255, [0x13] = 255,
    [0x14] = 255, [0x15] = 255, [0x16] = 255,  [0x17] = 255, [0x18] = 255,
    [0x19] = 255, [0x1a] = 255, [0x1b] = 255,  [0x1c] = 255, [0x1d] = 255,
    [0x1e] = 255, [0x1f] = 255, ['\\'] = '\\', ['"'] = '"',  ['\b'] = 'b',
    ['\f'] = 'f', ['\n'] = 'n', ['\r'] = 'r',  ['\t'] = 't', [0x7F] = 255,
};

static inline int
unicoda_as_json(WriteBuffer* buff, const unsigned char* data, Py_ssize_t length)
{
    Py_ssize_t total_size = buff->size + length + 2;
    if (FT_UNLIKELY(WriteBuffer_Resize(buff, total_size) < 0)) {
        return -1;
    }

    unsigned char* restrict s = buff->buffer + buff->size;
    const unsigned char* end_data = data + length;
    *s++ = '"';

    while (data != end_data) {
        unsigned char ch = *data++;
        unsigned char esc = escape_table[ch];
        if (FT_LIKELY(!esc)) {
            *s++ = ch;
        } else if (FT_LIKELY(esc != 255)) {
            total_size++;
            if (FT_UNLIKELY(WriteBuffer_Resize(buff, total_size) < 0)) {
                return -1;
            }
            *s++ = '\\';
            *s++ = esc;
        } else {
            total_size += 5;
            if (FT_UNLIKELY(WriteBuffer_Resize(buff, total_size) < 0)) {
                return -1;
            }
            s[0] = '\\';
            s[1] = 'u';
            s[2] = '0';
            s[3] = '0';
            s[4] = hex_digits[ch >> 4];
            s[5] = hex_digits[ch & 0xF];
            s += 6;
        }
    }

    *s++ = '"';
    buff->size = (s - buff->buffer);
    return 0;
}

static inline int
unicode_fast_as_json(WriteBuffer* buff,
                     const unsigned char* restrict data,
                     Py_ssize_t length)
{
    if (FT_UNLIKELY(WriteBuffer_Resize(buff, buff->size + length + 2) < 0)) {
        return -1;
    }

    unsigned char* restrict s = buff->buffer + buff->size;
    *s++ = '"';
    memcpy(s, data, length);
    s += length;
    *s++ = '"';

    buff->size += length + 2;
    return 0;
}

static inline const unsigned char*
unicode_str_and_size(PyObject* str, Py_ssize_t* size)
{
    if (FT_LIKELY(PyUnicode_IS_COMPACT_ASCII(str))) {
        *size = ((PyASCIIObject*)str)->length;
        return (unsigned char*)(((PyASCIIObject*)str) + 1);
    }

    const unsigned char* out =
      (const unsigned char*)(((PyCompactUnicodeObject*)str)->utf8);
    if (FT_LIKELY(out)) {
        *size = ((PyCompactUnicodeObject*)str)->utf8_length;
        return out;
    }
    return (const unsigned char*)PyUnicode_AsUTF8AndSize(str, size);
}

inline int
_Unicode_FastAsJson(WriteBuffer* buff, PyObject* obj)
{
    return unicode_fast_as_json(
      buff, PyUnicode_DATA(obj), PyUnicode_GET_LENGTH(obj));
}

int
_Bytes_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* _)
{
    Py_ssize_t length = PyBytes_GET_SIZE(obj);
    unsigned char* data = (unsigned char*)((PyBytesObject*)obj)->ob_sval;
    return unicoda_as_json(buff, data, length);
}

int
_BytesArray_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* _)
{
    Py_ssize_t length = PyByteArray_GET_SIZE(obj);
    unsigned char* data = (unsigned char*)((PyByteArrayObject*)obj)->ob_bytes;
    return unicoda_as_json(buff, data, length);
}

inline int
_Unicode_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* _)
{
    Py_ssize_t length;
    const unsigned char* data = unicode_str_and_size(obj, &length);
    if (FT_LIKELY(data)) {
        return unicoda_as_json(buff, data, length);
    }
    return -1;
}