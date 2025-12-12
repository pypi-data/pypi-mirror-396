#define PY_SSIZE_T_CLEAN
#include "Python.h"

typedef struct ValidateContext ValidateContext;
typedef struct ContextManager ContextManager;
typedef struct TypeAdapter TypeAdapter;

typedef struct ValidatorIterable
{
    PyObject_HEAD PyObject* iterator;
    TypeAdapter* validator;
    ContextManager* ctx;
    uint32_t flags;
} ValidatorIterable;

extern PyTypeObject ValidatorIterableType;
extern TypeAdapter *TypeAdapter_AbcHashable, *TypeAdapter_AbcCallable;

extern PyObject*
ValidatorIterable_Create(PyObject* iterable,
                         ValidateContext* ctx,
                         TypeAdapter* validator);
extern PyObject*
ValidatorIterable_CreateAsync(PyObject* coroutine,
                              ValidateContext* ctx,
                              TypeAdapter* validator);
extern TypeAdapter*
_TypeAdapter_CreateIterable(PyObject* cls, PyObject* tp, PyObject* args);
extern TypeAdapter*
_TypeAdapter_CreateGenerator(PyObject* tp, PyObject* args);
extern TypeAdapter*
_TypeAdapter_CreateSequence(PyObject* tp, PyObject* args);
extern int
abc_setup(void);
extern void
abc_free(void);