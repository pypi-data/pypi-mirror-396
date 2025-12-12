#include "Python.h"
#define PY_SSIZE_T_CLEAN

typedef struct ValidateContext ValidateContext;
typedef struct ContextManager ContextManager;
typedef struct TypeAdapter TypeAdapter;

typedef struct Handler
{
    PyObject_HEAD ContextManager* ctx;
    vectorcallfunc vectorcall;
    TypeAdapter* type_adapter;
    PyObject* cur_obj;
    PyObject* model;
    PyObject* data;
    uint32_t flags;
} Handler;

extern PyObject*
Handler_Create(ValidateContext* ctx, TypeAdapter* type_adapter);
extern int
handler_setup(void);
extern void
handler_free(void);