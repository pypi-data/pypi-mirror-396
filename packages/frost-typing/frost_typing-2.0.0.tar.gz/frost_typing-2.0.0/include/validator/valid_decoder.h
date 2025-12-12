#define PY_SSIZE_T_CLEAN
#include "Python.h"

typedef struct ReadBuffer ReadBuffer;
typedef struct TypeAdapter TypeAdapter;
typedef struct ValidatedFunc ValidatedFunc;
typedef struct ValidateContext ValidateContext;

typedef int (*JsonValidParser)(TypeAdapter* vd,
                               ReadBuffer* buff,
                               ValidateContext* ctx,
                               PyObject** res);

extern int
_JsonValidParse(TypeAdapter* vd,
                ReadBuffer* buff,
                ValidateContext* ctx,
                PyObject** res);
extern int
_JsonValidParse_AnySet(TypeAdapter* vd,
                       ReadBuffer* buff,
                       ValidateContext* ctx,
                       PyObject** res);
extern int
_JsonValidParse_List(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res);
extern int
_JsonValidParse_Tuple(TypeAdapter* vd,
                      ReadBuffer* buff,
                      ValidateContext* ctx,
                      PyObject** res);
extern int
_JsonValidParse_TupleFixSize(TypeAdapter* vd,
                             ReadBuffer* buff,
                             ValidateContext* ctx,
                             PyObject** res);
extern int
_JsonValidParse_ValidModel(TypeAdapter* vd,
                           ReadBuffer* buff,
                           ValidateContext* ctx,
                           PyObject** res);
extern int
_JsonValidParse_Dict(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res);
extern int
_JsonValidParse_ContextManager(TypeAdapter* vd,
                               ReadBuffer* buff,
                               ValidateContext* ctx,
                               PyObject** res);
extern int
_JsonValidParse_Date(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res);
extern int
_JsonValidParse_Time(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res);
extern int
_JsonValidParse_DateTime(TypeAdapter* vd,
                         ReadBuffer* buff,
                         ValidateContext* ctx,
                         PyObject** res);
extern int
_JsonValidParse_TimeDelta(TypeAdapter* vd,
                          ReadBuffer* buff,
                          ValidateContext* ctx,
                          PyObject** res);
int
_JsonValidParse_TypeVar(TypeAdapter* vd,
                        ReadBuffer* buff,
                        ValidateContext* ctx,
                        PyObject** res);
extern int
_JsonValidParse_UUID(TypeAdapter* vd,
                     ReadBuffer* buff,
                     ValidateContext* ctx,
                     PyObject** res);
extern int
_JsonValidParse(TypeAdapter* vd,
                ReadBuffer* buff,
                ValidateContext* ctx,
                PyObject** res);
extern PyObject*
JsonValidParse(TypeAdapter* self, PyObject* obj, ValidateContext* ctx);
extern PyObject*
JsonValidParse_ValidModel(PyTypeObject* tp,
                          PyObject* obj,
                          ContextManager* ctx,
                          PyObject** args,
                          PyObject* kwnames);
extern PyObject*
JsonValidParse_ValidatedFunc(ValidatedFunc* self,
                             PyObject* obj,
                             ContextManager* ctx,
                             PyObject** args,
                             PyObject* kwnames);