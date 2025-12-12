typedef struct ReadBuffer
{
    PyObject* obj;
    uint16_t nesting_level;
    char* end_data;
    char* start;
    char* iter;
} ReadBuffer;

extern int
_Decode_Enter(ReadBuffer* buff);
extern void
_Decode_Leave(ReadBuffer* buff);
extern void
ReadBuffer_GetPos(ReadBuffer* buffer, Py_ssize_t* column, Py_ssize_t* line);
extern void
ReadBuffer_Free(ReadBuffer*);