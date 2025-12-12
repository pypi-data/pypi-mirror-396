#include "utils_common.h"
#include "json/json.h"

#if PY_MINOR_VERSION < 12
#define _PyLong_IsNegative(o) (Py_SIZE(o) < 0)
#define _PyLong_DigitCount(o) Py_ABS(Py_SIZE(o))
#define PyLong_GET_DIGIT(o) ((PyLongObject*)o)->ob_digit
#else
#define SIGN_MASK 3
#define SIGN_NEGATIVE 2
#define NON_SIZE_BITS 3

static inline int
_PyLong_IsNegative(const PyLongObject* op)
{
    return (op->long_value.lv_tag & SIGN_MASK) == SIGN_NEGATIVE;
}

static inline Py_ssize_t
_PyLong_DigitCount(const PyLongObject* op)
{
    return (Py_ssize_t)(op->long_value.lv_tag >> NON_SIZE_BITS);
}
#define PyLong_GET_DIGIT(o) ((PyLongObject*)o)->long_value.ob_digit
#endif

static const unsigned char DIGIT_TABLE[200] = {
    '0', '0', '0', '1', '0', '2', '0', '3', '0', '4', '0', '5', '0', '6', '0',
    '7', '0', '8', '0', '9', '1', '0', '1', '1', '1', '2', '1', '3', '1', '4',
    '1', '5', '1', '6', '1', '7', '1', '8', '1', '9', '2', '0', '2', '1', '2',
    '2', '2', '3', '2', '4', '2', '5', '2', '6', '2', '7', '2', '8', '2', '9',
    '3', '0', '3', '1', '3', '2', '3', '3', '3', '4', '3', '5', '3', '6', '3',
    '7', '3', '8', '3', '9', '4', '0', '4', '1', '4', '2', '4', '3', '4', '4',
    '4', '5', '4', '6', '4', '7', '4', '8', '4', '9', '5', '0', '5', '1', '5',
    '2', '5', '3', '5', '4', '5', '5', '5', '6', '5', '7', '5', '8', '5', '9',
    '6', '0', '6', '1', '6', '2', '6', '3', '6', '4', '6', '5', '6', '6', '6',
    '7', '6', '8', '6', '9', '7', '0', '7', '1', '7', '2', '7', '3', '7', '4',
    '7', '5', '7', '6', '7', '7', '7', '8', '7', '9', '8', '0', '8', '1', '8',
    '2', '8', '3', '8', '4', '8', '5', '8', '6', '8', '7', '8', '8', '8', '9',
    '9', '0', '9', '1', '9', '2', '9', '3', '9', '4', '9', '5', '9', '6', '9',
    '7', '9', '8', '9', '9'
};

static void
write_u32_8digits(uint32_t val, char* buf)
{
    uint32_t high_part, low_part, high_hundred, high_units, low_hundred,
      low_units;

    high_part = (uint32_t)(((uint64_t)val * 109951163) >> 40); /* val / 10000 */
    low_part = val - high_part * 10000;                        /* val % 10000 */

    high_hundred = (high_part * 5243) >> 19;     /* high_part / 100 */
    high_units = high_part - high_hundred * 100; /* high_part % 100 */

    low_hundred = (low_part * 5243) >> 19;    /* low_part / 100 */
    low_units = low_part - low_hundred * 100; /* low_part % 100 */

    memcpy(buf + 0, DIGIT_TABLE + high_hundred * 2, 2);
    memcpy(buf + 2, DIGIT_TABLE + high_units * 2, 2);
    memcpy(buf + 4, DIGIT_TABLE + low_hundred * 2, 2);
    memcpy(buf + 6, DIGIT_TABLE + low_units * 2, 2);
}

static inline void
write_u32_4digits(uint32_t val, char* buf)
{
    uint32_t hundreds, units;
    hundreds = (val * 5243) >> 19; /* val / 100 */
    units = val - hundreds * 100;  /* val % 100 */
    memcpy(buf + 0, DIGIT_TABLE + hundreds * 2, 2);
    memcpy(buf + 2, DIGIT_TABLE + units * 2, 2);
}

static Py_ssize_t
write_u32_low_8digits(uint32_t val, char* buf)
{
    uint32_t hundreds, tens, ones, remainder, high_part, low_part, leading_zero;

    if (val < 100) { /* 1-2 digits */
        leading_zero = val < 10;
        memcpy(buf, DIGIT_TABLE + val * 2 + leading_zero, 2);
        return 2 - leading_zero;
    }

    if (val < 10000) { /* 3-4 digits */
        hundreds = (val * 5243) >> 19;
        tens = val - hundreds * 100;
        leading_zero = hundreds < 10;
        memcpy(buf + 0, DIGIT_TABLE + hundreds * 2 + leading_zero, 2);
        buf -= leading_zero;
        memcpy(buf + 2, DIGIT_TABLE + tens * 2, 2);
        return 4 - leading_zero;
    }

    if (val < 1000000) { /* 5-6 digits */
        high_part =
          (uint32_t)(((uint64_t)val * 429497) >> 32); /* val / 10000 */
        remainder = val - high_part * 10000;          /* val % 10000 */
        tens = (remainder * 5243) >> 19;
        ones = remainder - tens * 100;
        leading_zero = high_part < 10;
        memcpy(buf + 0, DIGIT_TABLE + high_part * 2 + leading_zero, 2);
        buf -= leading_zero;
        memcpy(buf + 2, DIGIT_TABLE + tens * 2, 2);
        memcpy(buf + 4, DIGIT_TABLE + ones * 2, 2);
        return 6 - leading_zero;
    }

    high_part = (uint32_t)(((uint64_t)val * 109951163) >> 40); /* val / 10000 */
    low_part = val - high_part * 10000;                        /* val % 10000 */
    hundreds = (high_part * 5243) >> 19;
    tens = high_part - hundreds * 100;
    ones = (low_part * 5243) >> 19;
    remainder = low_part - ones * 100;
    leading_zero = hundreds < 10;
    memcpy(buf + 0, DIGIT_TABLE + hundreds * 2 + leading_zero, 2);
    buf -= leading_zero;
    memcpy(buf + 2, DIGIT_TABLE + tens * 2, 2);
    memcpy(buf + 4, DIGIT_TABLE + ones * 2, 2);
    memcpy(buf + 6, DIGIT_TABLE + remainder * 2, 2);
    return 8 - leading_zero;
}

static inline Py_ssize_t
write_u64_high_8digits(uint32_t val, char* buf)
{
    uint32_t hundreds, tens, ones, remainder, high_part, low_part, leading_zero;

    if (val < 1000000) { /* 5-6 digits */
        high_part =
          (uint32_t)(((uint64_t)val * 429497) >> 32); /* val / 10000 */
        remainder = val - high_part * 10000;
        tens = (remainder * 5243) >> 19;
        ones = remainder - tens * 100;
        leading_zero = high_part < 10;
        memcpy(buf, DIGIT_TABLE + high_part * 2 + leading_zero, 2);
        buf -= leading_zero;
        memcpy(buf + 2, DIGIT_TABLE + tens * 2, 2);
        memcpy(buf + 4, DIGIT_TABLE + ones * 2, 2);
        return 6 - leading_zero;
    }

    /* 7-8 digits */
    high_part = (uint32_t)(((uint64_t)val * 109951163) >> 40); /* val / 10000 */
    low_part = val - high_part * 10000;
    hundreds = (high_part * 5243) >> 19;
    tens = high_part - hundreds * 100;
    ones = (low_part * 5243) >> 19;
    remainder = low_part - ones * 100;
    leading_zero = hundreds < 10;
    memcpy(buf + 0, DIGIT_TABLE + hundreds * 2 + leading_zero, 2);
    buf -= leading_zero;
    memcpy(buf + 2, DIGIT_TABLE + tens * 2, 2);
    memcpy(buf + 4, DIGIT_TABLE + ones * 2, 2);
    memcpy(buf + 6, DIGIT_TABLE + remainder * 2, 2);
    return 8 - leading_zero;
}

static inline Py_ssize_t
write_u64(uint64_t val, char* buf)
{
    uint64_t tmp, high64;
    uint32_t mid32, low32;

    if (val < 100000000) { /* 1-8 digits */
        return write_u32_low_8digits((uint32_t)val, buf);
    }

    if (val < (uint64_t)100000000 * 100000000) { /* 9-16 digits */
        high64 = val / 100000000;
        low32 = (uint32_t)(val - high64 * 100000000);
        Py_ssize_t size = write_u32_low_8digits((uint32_t)high64, buf);
        write_u32_8digits(low32, buf + size);
        return size + 8;
    }

    tmp = val / 100000000;
    low32 = (uint32_t)(val - tmp * 100000000);
    high64 = (uint32_t)(tmp / 10000);
    mid32 = (uint32_t)(tmp - high64 * 10000);

    Py_ssize_t size = write_u64_high_8digits((uint32_t)high64, buf);
    char* cur = buf + size;
    write_u32_4digits(mid32, cur);
    write_u32_8digits(low32, cur + 4);
    return size + 12;
}

int
_Long_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* params)
{
    uint64_t val;
    const int is_neg = _PyLong_IsNegative((PyLongObject*)obj);
    Py_ssize_t size_a = _PyLong_DigitCount((PyLongObject*)obj);
    if (size_a < 2) {
        if (FT_UNLIKELY(!size_a)) {
            return WriteBuffer_ConcatChar(buff, '0');
        }

        val = PyLong_GET_DIGIT(obj)[0];
    } else {
        if (FT_UNLIKELY(PyLong_AsByteArray(
                          obj, (unsigned char*)&val, 8, 1, is_neg) < 0)) {
            PyErr_SetString(JsonEncodeError, "Integer exceeds 64-bit range");
            return -1;
        }

        if (is_neg) {
            val &= 0xfffffffffffffffful;
        }
    }

    if (FT_UNLIKELY(WriteBuffer_Resize(buff, buff->size + 21) < 0)) {
        return -1;
    }

    char* restrict p = (char*)buff->buffer + buff->size;
    if (is_neg) {
        *p++ = '-';
    }
    buff->size += write_u64(val, p) + is_neg;
    return 0;
}