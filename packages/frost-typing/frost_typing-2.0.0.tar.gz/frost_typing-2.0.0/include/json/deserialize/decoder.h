extern PyObject* JsonDecodeError;

typedef struct ReadBuffer ReadBuffer;
typedef PyObject* (*_JsonParser)(ReadBuffer*);

extern const _JsonParser _JsonParse_Router[256];

extern PyObject*
JsonParse(PyObject*);
extern PyObject*
_JsonParse(ReadBuffer* buff);
extern PyObject*
_JsonParse_Continue(ReadBuffer*);
extern void
_JsonParse_Raise(ReadBuffer* buffer);
extern void
_JsonParse_RaiseFormat(ReadBuffer* buffer, const char* format);
extern int
JsonParse_GetBuffer(ReadBuffer* buff, PyObject* obj);
extern int
_JsonParse_CheckEnd(ReadBuffer* buff);
extern int
JsonParse_CheckEnd(ReadBuffer* buff);
extern int
decoder_setup(void);
extern void
decoder_free(void);