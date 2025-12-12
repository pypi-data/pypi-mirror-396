typedef struct WriteBuffer WriteBuffer;

typedef struct ConvParams ConvParams;
extern PyObject* JsonEncodeError;
extern PyObject*
PyObject_AsJson(PyObject* const* args,
                Py_ssize_t nargsf,
                PyObject* kwnames,
                int in_file);
extern int
_Uuid_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params);
extern int
_PyObject_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params);
extern int
_PyObject_AsJsonDecrefVal(WriteBuffer* buff, PyObject* obj, ConvParams* params);
extern int
encoder_setup(void);
extern void
encoder_free(void);