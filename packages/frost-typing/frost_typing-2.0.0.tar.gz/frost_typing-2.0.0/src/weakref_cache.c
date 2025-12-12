#include "weakref_cache.h"
#include "utils_common.h"

#define Weakref_GET_OBJECT(ref)                                                \
    (Py_REFCNT(((PyWeakReference*)(ref))->wr_object) > 0                       \
       ? ((PyWeakReference*)(ref))->wr_object                                  \
       : NULL)

inline void
WeakrefCache_SetItem(PyObject* self, PyObject* key, PyObject* val)
{
    if (FT_UNLIKELY(!PyObject_CheckHashable(key) ||
                    !PyType_SUPPORTS_WEAKREFS(Py_TYPE(val)))) {
        return;
    }

    PyObject* method = PyMethod_New(self, key);
    if (FT_UNLIKELY(!method)) {
        goto done;
    }

    PyObject* ref = PyWeakref_NewRef(val, method);
    Py_DECREF(method);
    if (FT_UNLIKELY(!ref)) {
        goto done;
    }

    if (PyDict_SetItemDecrefVal(self, key, ref) < 0) {
        goto done;
    }

    return;
done:
    PyErr_Clear();
}

inline PyObject*
WeakrefCache_GetItem(PyObject* self, PyObject* key)
{
    PyObject* ref = Dict_GetItemNoError(self, key);
    return ref ? Weakref_GET_OBJECT(ref) : NULL;
}

static PyObject*
weakref_cache_call(PyObject* self, PyObject* args, UNUSED PyObject* kw)
{
    if (PyTuple_GET_SIZE(args) != 2) {
        Py_RETURN_NONE;
    }
    if (FT_UNLIKELY(PyDict_DelItem(self, PyTuple_GET_ITEM(args, 0)) < 0)) {
        PyErr_Clear();
    }
    Py_RETURN_NONE;
}

PyTypeObject WeakrefCacheType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_name = "frost_typing.WeakrefCacheType",
    .tp_call = weakref_cache_call,
};

int
weakref_cache_setup(void)
{
    WeakrefCacheType.tp_base = &PyDict_Type;
    return PyType_Ready(&WeakrefCacheType);
}

void
weakref_cache_free(void)
{
}