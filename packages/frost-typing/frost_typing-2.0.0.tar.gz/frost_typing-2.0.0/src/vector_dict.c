#include "vector_dict.h"
#include "utils_common.h"

inline void
_VectorDictDealloc(_VectorDict* self)
{
    Py_CLEAR(self->_dict);
}

PyTypeObject _VectorDictType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)_VectorDictDealloc,
    .tp_name = "frost_typing.VectorDict",
    .tp_basicsize = sizeof(_VectorDict),
};

inline _VectorDict
_VectorDict_Create(PyObject* const* args, size_t nargsf, PyObject* kwnames)
{
    _VectorDict vd = (_VectorDict){ .ob_base.ob_type = &_VectorDictType,
                                    .args = args + PyVectorcall_NARGS(nargsf),
                                    .kwnames = kwnames,
                                    ._dict = NULL };
    Py_SET_REFCNT(&vd, 1);
    return vd;
}

inline PyObject*
_VectorDict_Get(PyObject* self, PyObject* string)
{
    _VectorDict* this = (_VectorDict*)self;
    Py_ssize_t i = _Tuple_GetName(this->kwnames, string);
    return i < 0 ? NULL : Py_NewRef(this->args[i]);
}

PyObject*
_VectorDict_GetDict(_VectorDict* self)
{
    if (self->_dict) {
        return self->_dict;
    }

    self->_dict = _Dict_FromKwnames((PyObject**)self->args, self->kwnames);
    return self->_dict;
}

int
vector_dict_setup(void)
{
    return PyType_Ready(&_VectorDictType);
}

void
vector_dict_free(void)
{
}