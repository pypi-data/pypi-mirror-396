#include "Python.h"
#include "meta_model.h"
#define PY_SSIZE_T_CLEAN

#define TPFLAGS_META_VALID_SUBCLASS (1UL << 21)
#define MetaValid_IS_SUBCLASS(tp)                                              \
    (_CAST(PyTypeObject*, tp)->tp_flags & TPFLAGS_META_VALID_SUBCLASS)
#define MetaValid_Check(op) MetaValid_IS_SUBCLASS(Py_TYPE(op))
#define MetaValid_CheckExact(op) Py_IS_TYPE((op), &MetaValidModelType)

typedef struct ContextManager ContextManager;

typedef struct MetaValidModel
{
    MetaModel head;
    PyObject* gtypes;
    ContextManager* ctx;
    PyObject* __frost_validate__;
} MetaValidModel;

extern PyTypeObject MetaValidModelType;
extern int
meta_valid_model_setup(void);
extern void
meta_valid_model_free(void);