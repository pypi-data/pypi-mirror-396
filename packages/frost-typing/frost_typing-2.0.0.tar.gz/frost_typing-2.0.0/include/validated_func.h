#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define ArgsKwargs_Check(op) Py_IS_TYPE(op, &ArgsKwargsType)
#define ValidatedFunc_Check(op) Py_IS_TYPE(op, &ValidatedFuncType)
#define _CAST_FUNC_VALIDATOR(o) _CAST(ValidatedFunc*, o)
#define _VALID_FUNC_GET_SCHEMAS(o)                                             \
    ((Schema**)TUPLE_ITEMS(_CAST_FUNC_VALIDATOR(o)->schemas))

#define VD_FUNC_GET_SIZE(o) PyTuple_GET_SIZE(_CAST_FUNC_VALIDATOR(o)->schemas)

#define FUNC_GET_KWONLY_CNT(f)                                                 \
    ((_CAST(PyCodeObject*, _CAST(PyFunctionObject*, f)->func_code)             \
        ->co_kwonlyargcount))
#define FUNC_GET_FLAGS(f)                                                      \
    (_CAST(PyCodeObject*, _CAST(PyFunctionObject*, f)->func_code)->co_flags)

#define HAS_COROUTINE(f) ((FUNC_GET_FLAGS(f) & CO_COROUTINE) != 0)
#define HAS_VARARGS(f) ((FUNC_GET_FLAGS(f) & CO_VARARGS) != 0)
#define HAS_VARKEYWORDS(f) ((FUNC_GET_FLAGS(f) & CO_VARKEYWORDS) != 0)

typedef struct ValidSchema ValidSchema;
typedef struct HashTable HashTable;
typedef struct ValidModel ValidModel;
typedef struct TypeAdapter TypeAdapter;
typedef struct ContextManager ContextManager;

typedef struct ValidatedFunc
{
    ValidModel head;
    uint32_t flags;
    HashTable* map;
    PyObject* gtypes;
    PyObject* kwnames;
    PyObject* schemas;
    PyObject* varnames;
    ValidSchema* a_schema;
    ValidSchema* kw_schema;
    PyFunctionObject* func;
    TypeAdapter* r_validator;
    vectorcallfunc vectorcall;
} ValidatedFunc;

typedef struct ArgsKwargs
{
    PyObject_HEAD struct ValidatedFunc* model;
    PyObject** args;
    Py_ssize_t nargs;
    PyObject* kwnames;
    PyObject* kwargs;
    PyObject* args_tuple;
} ArgsKwargs;

extern PyTypeObject ValidatedFuncType, ArgsKwargsType;
extern int
validated_func_setup(void);
extern void
validated_func_free(void);
extern PyObject*
_ValidatedFunc_GetName(ValidatedFunc* self);
extern PyObject*
ValidatedFunc_Create(PyTypeObject*,
                     PyFunctionObject*,
                     uint32_t flags,
                     PyObject* gtypes);
extern int
_ValidatedFunc_CallAndCheckResult(ValidatedFunc* self,
                                  PyObject** stack,
                                  Py_ssize_t stack_size,
                                  PyObject* kwnames,
                                  ValidateContext* ctx,
                                  PyObject** res);
extern ArgsKwargs*
_ArgsKwargs_Create(ValidatedFunc* model,
                   PyObject** args,
                   Py_ssize_t nargs,
                   PyObject* kwnames);
extern void
_ArgsKwargs_Decref(ArgsKwargs* self);
extern ValidateContext
_ValidatedFunc_GetCtx(ValidatedFunc* self, ContextManager* ctx);