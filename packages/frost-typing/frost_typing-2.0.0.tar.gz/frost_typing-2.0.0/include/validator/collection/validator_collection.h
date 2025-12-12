#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "validator/collection/validator_dict.h"
#include "validator/collection/validator_list.h"
#include "validator/collection/validator_set.h"
#include "validator/collection/validator_tuple.h"

typedef struct ReadBuffer ReadBuffer;
typedef struct TypeAdapter TypeAdapter;
typedef struct ValidateContext ValidateContext;
typedef struct ValidationError ValidationError;

extern int
_TypeAdapter_CollectionConverterArr(TypeAdapter* self,
                                    ValidateContext* ctx,
                                    PyObject** arr,
                                    Py_ssize_t size,
                                    PyObject** res);
extern int
_TypeAdapter_CollectionConverterSet(TypeAdapter* self,
                                    ValidateContext* ctx,
                                    PyObject* set,
                                    PyObject** res);
extern int
TypeAdapter_CollectionCheckArgs(PyObject* type_args,
                                PyTypeObject* tp,
                                Py_ssize_t args_cnt);
extern TypeAdapter*
_TypeAdapter_NewCollection(PyObject* cls,
                           PyObject* args,
                           PyObject* (*conv)(TypeAdapter* validator,
                                             ValidateContext* ctx,
                                             PyObject* val),
                           int (*json_parser)(TypeAdapter* vd,
                                              ReadBuffer* buff,
                                              ValidateContext* ctx,
                                              PyObject** res));
extern PyObject*
_TypeAdapter_CollectionRepr(TypeAdapter*);
extern TypeAdapter*
TypeAdapter_CreateCollection(PyObject* hint, PyObject* tp, PyObject* origin);
extern int
validator_collection_setup(void);
extern void
validator_collection_free(void);