#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define VectorDict_Check(o) Py_IS_TYPE(o, &_VectorDictType)

typedef struct _VectorDict
{
    PyObject_HEAD PyObject* const* args;
    PyObject* kwnames;
    PyObject* _dict;
} _VectorDict;

extern PyTypeObject _VectorDictType;

extern _VectorDict
_VectorDict_Create(PyObject* const* args, size_t nargsf, PyObject* kwnames);
extern PyObject*
_VectorDict_GetDict(_VectorDict* self);
extern PyObject*
_VectorDict_Get(PyObject* self, PyObject* name);
extern void
_VectorDictDealloc(_VectorDict* self);
extern int
vector_dict_setup(void);
extern void
vector_dict_free(void);