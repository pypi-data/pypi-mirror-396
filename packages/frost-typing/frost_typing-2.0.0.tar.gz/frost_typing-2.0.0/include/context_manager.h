#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define CTX_FROST_VALIDATE_CALL ((size_t)1 << (8 * sizeof(size_t) - 2))
#define CTX_NUM_ITEMS(c) Py_SIZE(c)
#define ContextManager_Check(o) (Py_TYPE(o) == &ContextManager_Type)
#define ContextManager_CREATE(m) _ContextManager_New((PyObject*)m, NULL, NULL)

typedef struct ValidateContext ValidateContext;
typedef struct ContextManager ContextManager;
typedef struct MetaValidModel MetaValidModel;
typedef struct ValidModel ValidModel;
typedef struct TypeAdapter TypeAdapter;

#if (PY_VERSION_HEX >= 0x030e0000)
#define UnicodeWriter PyUnicodeWriter
#else
#define UnicodeWriter _PyUnicodeWriter
#endif

typedef PyObject* (*ContextManagerFromJson)(ContextManager* ctx,
                                            PyObject* obj,
                                            PyObject** args,
                                            PyObject* kwnames);

typedef PyObject* (*ContextManagerCall)(ContextManager* ctx,
                                        PyObject** args,
                                        Py_ssize_t nargsf,
                                        PyObject* kwanames);

typedef struct ContextManagerItem
{
    TypeAdapter* validator;
    PyObject* hint;
} ContextManagerItem;

struct ContextManager
{
    PyObject_VAR_HEAD PyObject* model;
    PyObject* gtypes;
    ContextManagerFromJson from_json;
    ContextManagerCall validate_call;
    ContextManagerItem items[1];
};

extern PyTypeObject ContextManager_Type;
extern Py_ssize_t
Ctx_NARGS(Py_ssize_t nargs, int* frost_validate);
extern int
_ParseFrostValidate(PyObject* const*, Py_ssize_t, PyObject**, ContextManager**);
extern PyObject*
_ContextManager_Get_THint(PyObject* cls, ContextManager* ctx);
extern int
_ContextManager_Get_TTypeAdapter(PyObject* cls,
                                 ContextManager* ctx,
                                 TypeAdapter** validator);
extern ContextManager*
_ContextManager_CreateByOld(ContextManager* self, ContextManager* ctx);
extern PyObject*
_ContextManager_CreateGetItem(PyObject* model,
                              PyObject* gtypes,
                              PyObject* key,
                              ContextManagerCall call,
                              ContextManagerFromJson from_json);
extern ContextManager*
_ContextManager_New(PyObject* model,
                    ContextManagerCall call,
                    ContextManagerFromJson from_json);
extern int
_ContextManager_ReprModel(UnicodeWriter* writer, PyObject* model);
extern PyObject*
_ContextManager_FrostValidate(ContextManager* self,
                              PyObject* val,
                              ContextManager* ctx);
extern int
context_setup(void);
extern void
context_free(void);