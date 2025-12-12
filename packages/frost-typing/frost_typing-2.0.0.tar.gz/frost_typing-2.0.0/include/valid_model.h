#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define _VALID_MODEL_GET_CTX(s) _ValidModel_GetCtx((ValidModel*)s)

typedef struct HashTable HashTable;
typedef struct ContextManager ContextManager;
typedef struct MetaValidModel MetaValidModel;
typedef struct ValidationError ValidationError;
typedef struct ValidateContext ValidateContext;

typedef struct ValidModel
{
    PyObject_HEAD ContextManager* ctx;
} ValidModel;

extern MetaValidModel ValidModelType;
extern PyObject*
_ValidModel_CtxFromJson(ContextManager* ctx,
                        PyObject* obj,
                        PyObject** args,
                        PyObject* kwnames);
extern PyObject*
_ValidModel_CtxCall(ContextManager* ctx,
                    PyObject** args,
                    Py_ssize_t nargsf,
                    PyObject* kwnames);
extern void
_ValidModel_SetCtx(PyObject* self, ContextManager* ctx);
extern ValidateContext
_ValidModel_GetCtx(ValidModel* self);
extern PyObject*
_ValidModel_WithDiff(PyObject* self, PyObject* kwargs, uint32_t flags);
extern PyObject*
_ValidModel_Construct(PyTypeObject* cls,
                      PyObject* const* args,
                      Py_ssize_t nargs,
                      PyObject* kwnames);
extern PyObject*
_ValidModel_FrostValidate(PyTypeObject* cls,
                          PyObject* val,
                          ContextManager* ctx);
extern int
_ValidModel_Diff(PyObject* self,
                 PyObject* other,
                 uint32_t flags,
                 PyObject** res);
extern int
_ValidModel_Update(PyObject* self,
                   PyObject** args,
                   PyObject* kwnames,
                   ValidateContext* ctx,
                   ValidationError** err);
extern int
valid_model_setup(void);
extern void
valid_model_free(void);