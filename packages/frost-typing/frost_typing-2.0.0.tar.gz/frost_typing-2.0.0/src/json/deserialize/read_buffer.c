#include "json/json.h"

#define RECURSION_LIMIT 1024

inline int
_Decode_Enter(ReadBuffer* buff)
{
    if (++(buff->nesting_level) < RECURSION_LIMIT) {
        return 0;
    }
    PyErr_SetString(PyExc_RecursionError,
                    "maximum recursion depth exceeded"
                    " while decoding a JSON object");
    return -1;
}

inline void
_Decode_Leave(ReadBuffer* buff)
{
    buff->nesting_level--;
}

void
ReadBuffer_GetPos(ReadBuffer* buffer, Py_ssize_t* column, Py_ssize_t* line)
{
    Py_ssize_t c = 0;
    Py_ssize_t l = 1;
    char* st = buffer->start;
    while (st < buffer->iter) {
        char ch = *st++;
        if (ch != '\n') {
            c++;
        } else {
            l++;
            c = 0;
        }
    }
    *column = c;
    *line = l;
}

void
ReadBuffer_Free(ReadBuffer* buff)
{
    Py_CLEAR(buff->obj);
}
