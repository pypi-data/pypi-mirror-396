#include "validator/validator_uuid.h"
#include "field.h"
#include "validator/validator.h"
#include "json/deserialize/deserialize_string.h"

static PyObject* max_uuid;

static PyObject*
create_uuid(PyTypeObject* tp, PyObject* integer)
{
    PyObject* uuid = tp->tp_new(tp, VoidTuple, NULL);
    if (FT_UNLIKELY(!uuid)) {
        return NULL;
    }

    if (FT_UNLIKELY(
          PyObject_GenericSetAttr(uuid, __int, integer) < 0 ||
          PyObject_GenericSetAttr(uuid, __is_safe, PySafeUUIDUnknown) < 0)) {
        Py_DECREF(uuid);
        return NULL;
    }
    return uuid;
}

static PyObject*
parse_unicode_nested(unsigned char* data, Py_ssize_t size)
{
    if (size < 32) {
        return NULL;
    }

    char buffer[33] = { 0 };
    unsigned char* end = data + size;
    if (*data == '{') {
        data++;
    }
    if (end[-1] == '}') {
        end--;
    }

    if (!memcmp(data, "urn:", 4)) {
        data += 4;
    }

    if (!memcmp(data, "uuid:", 5)) {
        data += 5;
    }

    Py_ssize_t count = 0;
    while (data != end) {
        const unsigned char ch = *data++;
        if (ch == '-') {
            continue;
        }
        if (hex_table[ch] == 255 || count == 32) {
            return NULL;
        }

        buffer[count++] = ch;
    }

    return count == 32 ? PyLong_FromString(buffer, NULL, 16) : NULL;
}

static inline PyObject*
parse_unicode(PyObject* unicode)
{
    if (PyUnicode_KIND(unicode) != PyUnicode_1BYTE_KIND) {
        return NULL;
    }

    Py_ssize_t size = PyUnicode_GET_LENGTH(unicode);
    return parse_unicode_nested((unsigned char*)PyUnicode_DATA(unicode), size);
}

static int
check_int_uuid(PyObject* integer)
{
    return PyObject_RichCompareBool(Long_Zero, integer, Py_LE) == 1 &&
           PyObject_RichCompareBool(integer, max_uuid, Py_LT) == 1;
}

PyObject*
_Parse_UUID(TypeAdapter* self, char* buff, Py_ssize_t size)
{
    PyObject* integer = parse_unicode_nested((unsigned char*)buff, size);
    if (!integer) {
        return NULL;
    }

    if (!check_int_uuid(integer)) {
        Py_DECREF(integer);
        return NULL;
    }

    PyObject* res = create_uuid((PyTypeObject*)self->cls, integer);
    Py_DECREF(integer);
    return res;
}

static PyObject*
converter_uuid(TypeAdapter* self, ValidateContext* ctx, PyObject* uuid)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    PyObject* integer = NULL;
    if (PyUnicode_Check(uuid)) {
        integer = parse_unicode(uuid);
    } else if (PyBytes_Check(uuid) && Py_SIZE(uuid) == 16) {
        integer = _PyLong_FromByteArray(
          (unsigned char*)PyBytes_AS_STRING(uuid), 16, 0, 0);
    }
    if (!integer) {
        return NULL;
    }

    if (!check_int_uuid(integer)) {
        Py_DECREF(integer);
        return NULL;
    }

    PyObject* res = create_uuid((PyTypeObject*)self->cls, integer);
    Py_DECREF(integer);
    return res;
}

inline TypeAdapter*
TypeAdapter_Create_Uuid(PyObject* hint)
{
    return TypeAdapter_Create(hint,
                              NULL,
                              NULL,
                              TypeAdapter_Base_Repr,
                              converter_uuid,
                              PyObject_HasAttr(hint, __instancecheck__)
                                ? Inspector_IsType
                                : Inspector_IsInstance,
                              _JsonValidParse_UUID);
}

int
validator_uuid_setup(void)
{
    max_uuid = PyLong_FromString("80000000000000000000000000", NULL, 32);
    return max_uuid ? 0 : -1;
}

void
validator_uuid_free(void)
{
    Py_DECREF(max_uuid);
}