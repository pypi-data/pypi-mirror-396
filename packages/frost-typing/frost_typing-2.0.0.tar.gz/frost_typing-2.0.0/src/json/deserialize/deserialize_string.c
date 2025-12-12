#include "utils_common.h"
#include "json/json.h"

#define MAX_UNICODE 0x10ffff
#define STRING_CACHE_MAX_LENGTH 32
#define CACHE_SIZE ((uint32_t)2048)
#define CACHE_MASK (CACHE_SIZE - 1)
#define MASK (uint32_t)(0x5bd1e995)
#define MIN_MISSING ((int8_t)-10)

static const Py_UCS1 escape_table[256] = {
    ['\\'] = '\\', ['"'] = '"',  ['b'] = '\b', ['f'] = '\f',
    ['n'] = '\n',  ['r'] = '\r', ['t'] = '\t'
};

static PyObject* cache_str[CACHE_SIZE] = { NULL };
static int8_t used_cache_str[CACHE_SIZE] = { 0 };

const Py_UCS1 hex_table[256] = {
    [0x00] = 255, [0x01] = 255, [0x02] = 255, [0x03] = 255, [0x04] = 255,
    [0x05] = 255, [0x06] = 255, [0x07] = 255, [0x08] = 255, [0x09] = 255,
    [0x0A] = 255, [0x0B] = 255, [0x0C] = 255, [0x0D] = 255, [0x0E] = 255,
    [0x0F] = 255, [0x10] = 255, [0x11] = 255, [0x12] = 255, [0x13] = 255,
    [0x14] = 255, [0x15] = 255, [0x16] = 255, [0x17] = 255, [0x18] = 255,
    [0x19] = 255, [0x1A] = 255, [0x1B] = 255, [0x1C] = 255, [0x1D] = 255,
    [0x1E] = 255, [0x1F] = 255, [' '] = 255,  ['!'] = 255,  ['"'] = 255,
    ['#'] = 255,  ['$'] = 255,  ['%'] = 255,  ['&'] = 255,  ['\''] = 255,
    ['('] = 255,  [')'] = 255,  ['*'] = 255,  ['+'] = 255,  [','] = 255,
    ['-'] = 255,  ['.'] = 255,  ['/'] = 255,  ['0'] = 0,    ['1'] = 1,
    ['2'] = 2,    ['3'] = 3,    ['4'] = 4,    ['5'] = 5,    ['6'] = 6,
    ['7'] = 7,    ['8'] = 8,    ['9'] = 9,    [':'] = 255,  [';'] = 255,
    ['<'] = 255,  ['='] = 255,  ['>'] = 255,  ['?'] = 255,  ['@'] = 255,
    ['A'] = 10,   ['B'] = 11,   ['C'] = 12,   ['D'] = 13,   ['E'] = 14,
    ['F'] = 15,   ['G'] = 255,  ['H'] = 255,  ['I'] = 255,  ['J'] = 255,
    ['K'] = 255,  ['L'] = 255,  ['M'] = 255,  ['N'] = 255,  ['O'] = 255,
    ['P'] = 255,  ['Q'] = 255,  ['R'] = 255,  ['S'] = 255,  ['T'] = 255,
    ['U'] = 255,  ['V'] = 255,  ['W'] = 255,  ['X'] = 255,  ['Y'] = 255,
    ['Z'] = 255,  ['['] = 255,  ['\\'] = 255, [']'] = 255,  ['^'] = 255,
    ['_'] = 255,  ['`'] = 255,  ['a'] = 10,   ['b'] = 11,   ['c'] = 12,
    ['d'] = 13,   ['e'] = 14,   ['f'] = 15,   ['g'] = 255,  ['h'] = 255,
    ['i'] = 255,  ['j'] = 255,  ['k'] = 255,  ['l'] = 255,  ['m'] = 255,
    ['n'] = 255,  ['o'] = 255,  ['p'] = 255,  ['q'] = 255,  ['r'] = 255,
    ['s'] = 255,  ['t'] = 255,  ['u'] = 255,  ['v'] = 255,  ['w'] = 255,
    ['x'] = 255,  ['y'] = 255,  ['z'] = 255,  ['{'] = 255,  ['|'] = 255,
    ['}'] = 255,  ['~'] = 255,  [0x7F] = 255, [0x80] = 255, [0x81] = 255,
    [0x82] = 255, [0x83] = 255, [0x84] = 255, [0x85] = 255, [0x86] = 255,
    [0x87] = 255, [0x88] = 255, [0x89] = 255, [0x8A] = 255, [0x8B] = 255,
    [0x8C] = 255, [0x8D] = 255, [0x8E] = 255, [0x8F] = 255, [0x90] = 255,
    [0x91] = 255, [0x92] = 255, [0x93] = 255, [0x94] = 255, [0x95] = 255,
    [0x96] = 255, [0x97] = 255, [0x98] = 255, [0x99] = 255, [0x9A] = 255,
    [0x9B] = 255, [0x9C] = 255, [0x9D] = 255, [0x9E] = 255, [0x9F] = 255,
    [0xA0] = 255, [0xFF] = 255
};

static const uint8_t ascii_safe_table[256] = {
    [0x0] = 1,  [0x1] = 1,  [0x2] = 1,  [0x3] = 1,  [0x4] = 1,  [0x5] = 1,
    [0x6] = 1,  [0x7] = 1,  [0x8] = 1,  [0x9] = 1,  [0x10] = 1, [0x11] = 1,
    [0x12] = 1, [0x13] = 1, [0x14] = 1, [0x15] = 1, [0x16] = 1, [0x17] = 1,
    [0x18] = 1, [0x19] = 1, [0x20] = 1, [0x21] = 1, [0x23] = 1, [0x24] = 1,
    [0x25] = 1, [0x26] = 1, [0x27] = 1, [0x28] = 1, [0x29] = 1, [0x2A] = 1,
    [0x2B] = 1, [0x2C] = 1, [0x2D] = 1, [0x2E] = 1, [0x2F] = 1, [0x30] = 1,
    [0x31] = 1, [0x32] = 1, [0x33] = 1, [0x34] = 1, [0x35] = 1, [0x36] = 1,
    [0x37] = 1, [0x38] = 1, [0x39] = 1, [0x3A] = 1, [0x3B] = 1, [0x3C] = 1,
    [0x3D] = 1, [0x3E] = 1, [0x3F] = 1, [0x40] = 1, [0x41] = 1, [0x42] = 1,
    [0x43] = 1, [0x44] = 1, [0x45] = 1, [0x46] = 1, [0x47] = 1, [0x48] = 1,
    [0x49] = 1, [0x4A] = 1, [0x4B] = 1, [0x4C] = 1, [0x4D] = 1, [0x4E] = 1,
    [0x4F] = 1, [0x50] = 1, [0x51] = 1, [0x52] = 1, [0x53] = 1, [0x54] = 1,
    [0x55] = 1, [0x56] = 1, [0x57] = 1, [0x58] = 1, [0x59] = 1, [0x5A] = 1,
    [0x5B] = 1, [0x5D] = 1, [0x5E] = 1, [0x5F] = 1, [0x60] = 1, [0x61] = 1,
    [0x62] = 1, [0x63] = 1, [0x64] = 1, [0x65] = 1, [0x66] = 1, [0x67] = 1,
    [0x68] = 1, [0x69] = 1, [0x6A] = 1, [0x6B] = 1, [0x6C] = 1, [0x6D] = 1,
    [0x6E] = 1, [0x6F] = 1, [0x70] = 1, [0x71] = 1, [0x72] = 1, [0x73] = 1,
    [0x74] = 1, [0x75] = 1, [0x76] = 1, [0x77] = 1, [0x78] = 1, [0x79] = 1,
    [0x7A] = 1, [0x7B] = 1, [0x7C] = 1, [0x7D] = 1, [0x7E] = 1, [0x7F] = 1,
};

static inline PyObject*
unicode_from_ascii(const char* str, Py_ssize_t size)
{
    PyObject* res = PyUnicode_New(size, 127);
    if (FT_LIKELY(res)) {
        memcpy((((PyASCIIObject*)res) + 1), str, size);
    }
    return res;
}

static inline void
use_cache(uint32_t index)
{
    uint8_t used = used_cache_str[index];
    if (used != (INT8_MAX - 1)) {
        used_cache_str[index] = used + 1;
    }
}

static inline int
missing_cache(uint32_t index)
{
    int8_t used = used_cache_str[index];
    if (used != MIN_MISSING) {
        used_cache_str[index] = used - 1;
        return 0;
    }
    return 1;
}

static inline uint32_t
to_u32(const unsigned char* p)
{
    uint32_t out;
    memcpy(&out, p, sizeof(out));
    return out;
}

static inline uint32_t
fast_hash_str(const unsigned char* str, Py_ssize_t size)
{
    uint32_t hash = (uint32_t)size;

    while (size >= 4) {
        uint32_t k = to_u32(str);
        k *= MASK;
        k ^= k >> 24;
        k *= MASK;
        hash *= MASK;
        hash ^= k;
        str += 4;
        size -= 4;
    }

    switch (size) {
        case 3:
            hash ^= str[2] << 16;
            hash ^= str[1] << 8;
            hash ^= str[0];
            hash *= MASK;
            break;
        case 2:
            hash ^= str[1] << 8;
            hash ^= str[0];
            hash *= MASK;
            break;
        case 1:
            hash ^= str[0];
            hash *= MASK;
            break;
        default:
            break;
    }

    hash ^= hash >> 13;
    hash *= MASK;
    hash ^= hash >> 15;
    return hash;
}

static PyObject*
cache_get(unsigned char* str, Py_ssize_t size)
{
    if (size > STRING_CACHE_MAX_LENGTH || size < 2) {
        return unicode_from_ascii((char*)str, size);
    }

    uint32_t index = fast_hash_str(str, size) & CACHE_MASK;
    PyObject* cache = cache_str[index];
    if (cache && PyUnicode_GET_LENGTH(cache) == size &&
        !memcmp(PyUnicode_DATA(cache), str, size)) {
        use_cache(index);
        return Py_NewRef(cache);
    }

    PyObject* res = unicode_from_ascii((char*)str, size);
    if (FT_LIKELY(res)) {
        if (!cache) {
            cache_str[index] = Py_NewRef(res);
        } else if (missing_cache(index)) {
            Py_DECREF(cache_str[index]);
            cache_str[index] = Py_NewRef(res);
            used_cache_str[index] = 0;
        }
    }
    return res;
}

static inline int
decode_unicode(unsigned char** cursor, const unsigned char* end, Py_UCS4* res)
{
    unsigned char* cur = *cursor;
    if (end - cur < 4) {
        return -1;
    }

    Py_UCS1 d0 = hex_table[cur[0]];
    Py_UCS1 d1 = hex_table[cur[1]];
    Py_UCS1 d2 = hex_table[cur[2]];
    Py_UCS1 d3 = hex_table[cur[3]];
    if ((d0 | d1 | d2 | d3) == 255) {
        return -1;
    }

    *res = (d0 << 12) | (d1 << 8) | (d2 << 4) | d3;
    // must stay on the last character
    *cursor += 3;
    return 0;
}

static inline void
filling_string_1(Py_UCS1* data, unsigned char* cur, unsigned char* end)
{
    int slash = 0;

    Py_UCS1 ch;
    for (; cur != end; cur++) {
        ch = *cur;
        if (!slash) {
            if (ch == '\\') {
                slash = 1;
                continue;
            }
            *data++ = ch;
            continue;
        }

        slash = 0;
        Py_UCS1 esc = escape_table[ch];
        if (esc) {
            *data++ = esc;
        } else if (ch == 'u') {
            cur++;
            Py_UCS4 u_ch = 0;
            decode_unicode(&cur, end, &u_ch);
            *data++ = (Py_UCS1)u_ch;
        }
    }
}

static inline void
filling_string_2(Py_UCS2* data, unsigned char* cur, unsigned char* end)
{
    int slash = 0;
    Py_UCS2 ch;

    for (; cur != end; cur++) {
        ch = *cur;
        if (!slash) {
            if (ch == '\\') {
                slash = 1;
                continue;
            }

            Py_UCS2 c = 0;
            if ((ch & 0x80) == 0) {
                c = ch;
            } else if ((ch & 0xE0) == 0xC0) {
                c = ((ch & 0x1F) << 6);
                c |= (*++cur & 0x3F);
            } else if ((ch & 0xF0) == 0xE0) {
                c = ((ch & 0x0F) << 12);
                c |= ((*++cur & 0x3F) << 6);
                c |= (*++cur & 0x3F);
            }
            *data++ = c;
            continue;
        }
        slash = 0;
        Py_UCS1 esc = escape_table[ch];
        if (esc) {
            *data++ = esc;
        } else if (ch == 'u') {
            cur++;
            Py_UCS4 u_ch = 0;
            decode_unicode(&cur, end, &u_ch);
            *data++ = (Py_UCS2)u_ch;
        }
    }
}

static inline void
filling_string_4(Py_UCS4* data, unsigned char* cur, unsigned char* end)
{
    int slash = 0;
    Py_UCS1 ch;

    for (; cur != end; cur++) {
        ch = *cur;
        if (!slash) {
            if (ch == '\\') {
                slash = 1;
                continue;
            }

            Py_UCS4 c;
            if ((ch & 0x80) == 0) {
                c = ch;
            } else if ((ch & 0xE0) == 0xC0) {
                c = ((ch & 0x1F) << 6);
                c |= (*++cur & 0x3F);
            } else if ((ch & 0xF0) == 0xE0) {
                c = ((ch & 0x0F) << 12);
                c |= ((*++cur & 0x3F) << 6);
                c |= (*++cur & 0x3F);
            } else {
                c = ((ch & 0x07) << 18);
                c |= ((*++cur & 0x3F) << 12);
                c |= ((*++cur & 0x3F) << 6);
                c |= (*++cur & 0x3F);
            }

            *data++ = c;
            continue;
        }
        slash = 0;
        Py_UCS1 esc = escape_table[ch];
        if (esc) {
            *data++ = esc;
        } else if (ch == 'u') {
            cur++;
            Py_UCS4 u_ch = 0;
            decode_unicode(&cur, end, &u_ch);
            if (Py_UNICODE_IS_HIGH_SURROGATE(u_ch) && (cur + 5) < end &&
                *(cur + 1) == '\\' && *(cur + 2) == 'u') {
                cur += 3;
                Py_UCS4 u_ch2 = 0;
                decode_unicode(&cur, end, &u_ch2);
                if (Py_UNICODE_IS_LOW_SURROGATE(u_ch2)) {
                    *data++ = Py_UNICODE_JOIN_SURROGATES(u_ch, u_ch2);
                } else {
                    *data++ = u_ch;
                    *data++ = u_ch2;
                }
            } else {
                *data++ = u_ch;
            }
        }
    }
}

PyObject*
_JsonParse_CreateString(unsigned char* cur,
                        unsigned char* end,
                        Py_UCS4 max_char,
                        Py_ssize_t size,
                        int use_cache)
{
    if (max_char < 128 && (end - cur) == size) {
        return use_cache ? cache_get(cur, size)
                         : unicode_from_ascii((char*)cur, size);
    }

    PyObject* res = PyUnicode_New(size, max_char);
    if (!res) {
        return NULL;
    }

    void* data = PyUnicode_DATA(res);
    if (max_char < 256) {
        filling_string_1(data, cur, end);
    } else if (max_char < 65536) {
        filling_string_2(data, cur, end);
    } else {
        if (max_char > MAX_UNICODE) {
            Py_DECREF(res);
            PyErr_SetString(PyExc_SystemError, "invalid maximum character");
            return NULL;
        }
        filling_string_4(data, cur, end);
    }
    return res;
}

Py_ssize_t
_JsonParse_String(ReadBuffer* buffer,
                  Py_UCS4* max_char,
                  unsigned char** end_data)
{
    unsigned char* cur = (unsigned char*)++buffer->iter;
    const unsigned char* end = (unsigned char*)buffer->end_data;
    const unsigned char* st = cur;

    while (FT_LIKELY(cur != end && ascii_safe_table[*cur])) {
        cur++;
    }

    Py_ssize_t size = cur - st;

    if (FT_LIKELY(cur != end && *cur == '"')) {
        buffer->iter = (char*)cur + 1;
        *max_char = '\x7f';
        *end_data = cur;
        return size;
    }

    Py_UCS4 max_ch = '\0';
    uint8_t slash = 0;

    for (; cur != end; cur++) {
        Py_UCS1 ch = *cur;
        if (FT_LIKELY(!slash)) {
            if (FT_UNLIKELY(ch == '\\')) {
                slash = 1;
                continue;
            }

            if (ch == '"') {
                buffer->iter = (char*)cur + 1;
                *max_char = max_ch;
                *end_data = cur;
                return size;
            }

            Py_UCS4 c;
            if ((ch & 0x80) == 0) {
                c = ch;
            } else if ((ch & 0xE0) == 0xC0 && (cur + 1 < end)) {
                c = ((ch & 0x1F) << 6) | (cur[1] & 0x3F);
                cur += 1;
            } else if ((ch & 0xF0) == 0xE0 && (cur + 2 < end)) {
                c = ((ch & 0x0F) << 12) | ((cur[1] & 0x3F) << 6) |
                    (cur[2] & 0x3F);
                cur += 2;
            } else if ((ch & 0xF8) == 0xF0 && (cur + 3 < end)) {
                c = ((ch & 0x07) << 18) | ((cur[1] & 0x3F) << 12) |
                    ((cur[2] & 0x3F) << 6) | (cur[3] & 0x3F);
                cur += 3;
            } else {
                goto error;
            }

            if (c > max_ch) {
                max_ch = c;
            }
            size++;
            continue;
        }

        slash = 0;
        if (FT_LIKELY(escape_table[ch])) {
            size++;
        } else if (FT_LIKELY(ch == 'u')) {
            cur++;
            Py_UCS4 u_ch = 0;
            if (decode_unicode(&cur, end, &u_ch) < 0) {
                goto error;
            }
            if (Py_UNICODE_IS_HIGH_SURROGATE(u_ch) && (cur + 5) < end &&
                *(cur + 1) == '\\' && *(cur + 2) == 'u') {
                cur += 3;
                Py_UCS4 u_ch2 = 0;
                if (decode_unicode(&cur, end, &u_ch2) < 0) {
                    goto error;
                }
                if (Py_UNICODE_IS_LOW_SURROGATE(u_ch2)) {
                    u_ch = Py_UNICODE_JOIN_SURROGATES(u_ch, u_ch2);
                } else {
                    size++;
                    if (u_ch2 > max_ch) {
                        max_ch = u_ch2;
                    }
                }
            }
            size++;
            if (u_ch > max_ch) {
                max_ch = u_ch;
            }
        } else {
            goto error;
        }
    }

error:
    if (FT_UNLIKELY(cur == end)) {
        cur--;
    }

    buffer->iter = (char*)cur;
    return -1;
}

static inline PyObject*
json_parse_string(ReadBuffer* buffer, int use_cahche)
{
    Py_UCS4 max_char = '\0';
    unsigned char *end, *st = (unsigned char*)buffer->iter + 1;
    Py_ssize_t size = _JsonParse_String(buffer, &max_char, &end);

    if (FT_UNLIKELY(size < 0)) {
        return NULL;
    }
    return _JsonParse_CreateString(st, end, max_char, size, use_cahche);
}

inline PyObject*
JsonParse_String(ReadBuffer* buffer)
{
    return json_parse_string(buffer, 0);
}

inline PyObject*
JsonParse_StringKey(ReadBuffer* buffer)
{
    return *buffer->iter == '"' ? json_parse_string(buffer, 1) : NULL;
}

void
_DeseralizeString_Intern(PyObject* ascii)
{
    Py_ssize_t size = PyUnicode_GET_LENGTH(ascii);
    if (!PyUnicode_IS_ASCII(ascii) || size > STRING_CACHE_MAX_LENGTH ||
        size < 2) {
        return;
    }

    const unsigned char* data = (const unsigned char*)PyUnicode_DATA(ascii);
    uint32_t index = fast_hash_str(data, size) & CACHE_MASK;
    PyObject* cache = cache_str[index];
    if (!cache) {
        cache_str[index] = Py_NewRef(ascii);
    }
}

void
deserialize_string_free(void)
{
    for (uint32_t i = 0; i != CACHE_SIZE; i++) {
        Py_CLEAR(cache_str[i]);
    }
}