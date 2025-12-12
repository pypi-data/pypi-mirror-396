#include "utils_common.h"
#include "json/json.h"

#define MAX_EXP 308
#define MIN_EXP -323

#define MAX_DOBULE_DIGIT (uint64_t)(10000000000000000)
#define MIN(a, b) (a < b ? a : b)
#define _CHAR_TO_INT(c) ((int)(c - '0'))
#define _CHAR_IS_NUM(c) (c >= '0' && c <= '9')

static double cache_pow[324] = { 0.0 };

static inline void
json_parse_raise_big_long(ReadBuffer* buffer)
{
    _JsonParse_RaiseFormat(buffer,
                           "number is big when parsed as integer"
                           ": line %zu column %zu (char '%c')");
}

static inline void
json_parse_raise_infinity(ReadBuffer* buffer)
{
    _JsonParse_RaiseFormat(buffer,
                           "number is infinity when parsed as double"
                           ": line %zu column %zu (char '%c')");
}

static inline double
fast_pow(int exp)
{
    double res = cache_pow[exp];
    if (FT_UNLIKELY(res == 0.0)) {
        res = pow(10.0, exp);
        cache_pow[exp] = res;
    }
    return res;
}

static inline double
create_dobule(uint64_t digit, int exp, int sign)
{
    if (exp < 0) {
        if (FT_UNLIKELY(exp < MIN_EXP)) {
            return NAN;
        }
        return ((double)digit / fast_pow(-exp)) * sign;
    }

    if (FT_UNLIKELY(exp > MAX_EXP)) {
        return NAN;
    }
    return ((double)digit * fast_pow(exp)) * sign;
}

static PyObject*
json_parse_e(char* start, ReadBuffer* buffer, uint64_t digit, int exp, int sign)
{
    const char* end = buffer->end_data;
    if (end - buffer->iter < 2) {
        return NULL;
    }

    int e_sign;
    int exponent = 0;
    char ch = *(++buffer->iter);
    if (ch == '-') {
        e_sign = -1;
    } else if (ch == '+') {
        e_sign = 1;
    } else if (_CHAR_IS_NUM(ch)) {
        e_sign = 1;
        buffer->iter--;
    } else {
        return NULL;
    }

    const char* st = buffer->iter++;
    for (; buffer->iter != end; buffer->iter++) {
        ch = *buffer->iter;
        if (_CHAR_IS_NUM(ch)) {
            exponent = exponent * 10 + _CHAR_TO_INT(ch);
            if (exponent > MAX_EXP) {
                goto error_infinity;
            }
        } else {
            break;
        }
    }

    if (!exponent && st == buffer->iter) {
        return NULL;
    }

    double d = create_dobule(digit, exp + (exponent * e_sign), sign);

    // check overflow
    if (FT_UNLIKELY(isinf(d))) {
        goto error_infinity;
    }
    return PyFloat_FromDouble(d);

error_infinity:
    buffer->iter = start;
    json_parse_raise_infinity(buffer);
    return NULL;
}

static PyObject*
json_parse_dobule(char* start, uint64_t digit, int sign, ReadBuffer* buffer)
{
    char ch;
    int exp = 0;
    int point = 0;
    const char* end = buffer->end_data;

    for (; buffer->iter != end; buffer->iter++) {
        ch = *buffer->iter;
        if (_CHAR_IS_NUM(ch)) {
            if (digit < MAX_DOBULE_DIGIT) {
                digit = digit * 10 + _CHAR_TO_INT(ch);
            } else {
                exp++;

                if (exp > MAX_EXP) {
                    goto error_infinity;
                }
            }
        } else if (ch == '.') {
            point = 1;
            buffer->iter++;
            break;
        } else if (ch == 'e' || ch == 'E') {
            return json_parse_e(start, buffer, digit, exp, sign);
        } else {
            // The integer is too large
            buffer->iter = start;
            json_parse_raise_big_long(buffer);
            return NULL;
        }
    }

    if (!point) {
        buffer->iter = start;
        json_parse_raise_big_long(buffer);
        return NULL;
    }

    for (; buffer->iter != end; buffer->iter++) {
        ch = *buffer->iter;
        if (_CHAR_IS_NUM(ch)) {
            if (digit < MAX_DOBULE_DIGIT) {
                digit = digit * 10 + _CHAR_TO_INT(ch);
            }

            exp--;
            if (exp < MIN_EXP) {
                goto error_infinity;
            }
        } else if (ch == 'e' || ch == 'E') {
            return json_parse_e(start, buffer, digit, exp, sign);
        } else {
            break;
        }
    }

    if (!exp) {
        return NULL;
    }

    double d = create_dobule(digit, exp, sign);

    // check overflow
    if (FT_UNLIKELY(isinf(d))) {
        goto error_infinity;
    }
    return PyFloat_FromDouble(d);

error_infinity:
    buffer->iter = start;
    json_parse_raise_infinity(buffer);
    return NULL;
}

PyObject*
JsonParse_Numeric(ReadBuffer* buffer)
{
    uint64_t interger = 0;
    char ch, *st, *end;
    int sign = 1;

    st = buffer->iter;
    if (*st == '-') {
        buffer->iter++;
        sign = -1;
        if (buffer->iter == buffer->end_data) {
            return NULL;
        }
    }

    end = MIN(buffer->end_data, buffer->iter + 19);
    for (; buffer->iter != end; buffer->iter++) {
        ch = *buffer->iter;
        if (FT_LIKELY(_CHAR_IS_NUM(ch))) {
            interger = interger * 10 + _CHAR_TO_INT(ch);
        } else if (FT_LIKELY(ch == '.')) {
            return json_parse_dobule(st, interger, sign, buffer);
        } else if (FT_LIKELY(ch == 'e' || ch == 'E')) {
            return json_parse_e(st, buffer, interger, 0, sign);
        } else {
            return PyLong_FromLongLong(((long long)interger) * sign);
        }
    }

    // checks overflow
    if (FT_UNLIKELY((interger > INT64_MAX) ||
                    (end != buffer->end_data && _CHAR_IS_NUM(*buffer->iter)))) {
        return json_parse_dobule(st, interger, sign, buffer);
    }
    return PyLong_FromLongLong(((long long)interger) * sign);
}