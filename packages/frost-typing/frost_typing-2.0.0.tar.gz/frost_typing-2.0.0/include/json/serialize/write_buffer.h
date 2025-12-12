#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define BUFFER_CONCAT_CHAR(b, c)                                               \
    if (FT_UNLIKELY(WriteBuffer_ConcatChar(b, c) < 0)) {                       \
        return -1;                                                             \
    }

#define BUFFER_CONCAT_SIZE(b, d, s)                                            \
    if (FT_UNLIKELY(WriteBuffer_ConcatSize(b, d, s) < 0)) {                    \
        return -1;                                                             \
    }

typedef struct WriteBuffer
{
    Py_ssize_t buffer_size;
    Py_ssize_t size;
    PyObject* witer;
    unsigned char* buffer;
} WriteBuffer;

extern int
WriteBuffer_ConcatChar(WriteBuffer*, char);
extern int
WriteBuffer_Resize(WriteBuffer*, Py_ssize_t);
extern int
WriteBuffer_ConcatSize(WriteBuffer*, char*, Py_ssize_t);
extern void
WriteBuffer_Free(WriteBuffer*);
extern PyObject*
WriteBuffer_Finish(WriteBuffer* buffer);
extern int
WriteBuffer_init(WriteBuffer* buffer, PyObject* writer);