#include "utils_common.h"
#include "json/json.h"

static int
write_buffer_write(WriteBuffer* buffer)
{
    if (!FT_UNLIKELY(buffer->size)) {
        return 1;
    }

    PyObject* bytes =
      PyBytes_FromStringAndSize((const char*)buffer->buffer, buffer->size);
    memset((void*)buffer->buffer, 0, buffer->size);
    buffer->size = 0;

    if (!FT_UNLIKELY(bytes)) {
        return 0;
    }

    PyObject* tmp = PyObject_CallOneArg(buffer->witer, bytes);
    Py_DECREF(bytes);
    if (FT_LIKELY(tmp)) {
        Py_DECREF(tmp);
        return 1;
    }
    return 0;
}

static inline Py_ssize_t
write_buffer_new_size(Py_ssize_t size, Py_ssize_t new_size)
{
    do {
        size <<= 2;
    } while (size < new_size);
    return size;
}

static int
write_buffer_resize(WriteBuffer* buffer, Py_ssize_t size)
{
    if (FT_UNLIKELY(buffer->witer && buffer->size)) {
        Py_ssize_t old_size = buffer->size;
        if (!write_buffer_write(buffer)) {
            return 0;
        }
        size -= old_size + 2;
        return WriteBuffer_Resize(buffer, size);
    }

    size = write_buffer_new_size(buffer->buffer_size, size);
    unsigned char* new_buffer = PyMem_Realloc(buffer->buffer, size);
    if (FT_UNLIKELY(!new_buffer)) {
        PyErr_NoMemory();
        return -1;
    }
    buffer->buffer_size = size;
    buffer->buffer = new_buffer;
    return 0;
}

inline int
WriteBuffer_Resize(WriteBuffer* buffer, Py_ssize_t size)
{
    size += 2; // For separators
    if (FT_LIKELY(buffer->buffer_size >= size)) {
        return 0;
    }
    return write_buffer_resize(buffer, size);
}

inline int
WriteBuffer_ConcatChar(WriteBuffer* buffer, char ch)
{
    if (FT_UNLIKELY(WriteBuffer_Resize(buffer, buffer->size + 1) < 0)) {
        return -1;
    }
    buffer->buffer[buffer->size++] = ch;
    return 0;
}

inline int
WriteBuffer_ConcatSize(WriteBuffer* buffer, char* data, Py_ssize_t size)
{
    Py_ssize_t new_size = buffer->size + size;
    if (FT_UNLIKELY(WriteBuffer_Resize(buffer, new_size) < 0)) {
        return -1;
    }
    memcpy(buffer->buffer + buffer->size, data, size);
    buffer->size = new_size;
    return 0;
}

inline void
WriteBuffer_Free(WriteBuffer* buffer)
{
    Py_CLEAR(buffer->witer);
    PyMem_Free(buffer->buffer);
}

PyObject*
WriteBuffer_Finish(WriteBuffer* buffer)
{
    PyObject* res = NULL;
    if (FT_LIKELY(!buffer->witer)) {
        res =
          PyBytes_FromStringAndSize((const char*)buffer->buffer, buffer->size);
    } else if (write_buffer_write(buffer)) {
        Py_INCREF(Py_None);
        res = Py_None;
    }

    WriteBuffer_Free(buffer);
    return res;
}

int
WriteBuffer_init(WriteBuffer* buffer, PyObject* writer)
{
    buffer->buffer = PyMem_Malloc(512);
    if (FT_UNLIKELY(!buffer->buffer)) {
        PyErr_NoMemory();
        return -1;
    }
    buffer->buffer_size = 512;
    buffer->witer = writer;
    buffer->size = 0;
    return 0;
}