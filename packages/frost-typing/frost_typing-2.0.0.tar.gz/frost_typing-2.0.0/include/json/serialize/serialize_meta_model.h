typedef struct WriteBuffer WriteBuffer;

extern int
_MetaModel_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern PyObject*
_MetaModel_AsJsonCall(PyObject* obj,
                      PyObject* const* args,
                      Py_ssize_t nargsf,
                      PyObject* kwnames);