#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "context_manager.h"
#include "handler.h"
#include "utils_common.h"
#include "validator/abc.h"
#include "validator/collection/validator_collection.h"
#include "validator/constraints/constraints.h"
#include "validator/field_validator.h"
#include "validator/py_typing.h"
#include "validator/valid_decoder.h"
#include "validator/validation_error.h"
#include "validator/validator_bool.h"
#include "validator/validator_date_time.h"
#include "validator/validator_literal.h"
#include "validator/validator_primitive.h"
#include "validator/validator_str.h"
#include "validator/validator_type_var.h"
#include "validator/validator_typed_dict.h"
#include "validator/validator_union.h"
#include "validator/validator_union_type.h"

#define TypeAdapter_Check(op) Py_IS_TYPE((op), &TypeAdapterType)
#define ValidateCtx_Create(ctx_, c_obj, d, m, f)                               \
    (ValidateContext)                                                          \
    {                                                                          \
        .ctx = ctx_, .cur_obj = (PyObject*)c_obj, .data = (PyObject*)d,        \
        .model = (PyObject*)m, .flags = f                                      \
    }

typedef struct TypeAdapter TypeAdapter;
typedef struct ContextManager ContextManager;

typedef struct ValidateContext
{
    ContextManager* ctx;
    PyObject* cur_obj;
    PyObject* model;
    PyObject* data;
    uint32_t flags;
} ValidateContext;

typedef PyObject* (*Converter)(TypeAdapter* validator,
                               ValidateContext* ctx,
                               PyObject* val);
typedef int (*Inspector)(TypeAdapter*, PyObject*);
typedef PyObject* (*TypeAdapterRepr)(TypeAdapter*);

struct TypeAdapter
{
    PyObject_HEAD PyObject* cls;
    PyObject* args;
    Converter conv;
    PyObject* ob_str;
    PyObject* err_msg;
    Inspector inspector;
    PyObject* tp_weaklist;
    TypeAdapterRepr ob_repr;
    JsonValidParser json_parser;
};

extern PyTypeObject TypeAdapterType;
extern PyObject* __frost_validate__;
extern PyObject*
TypeAdapter_Conversion(TypeAdapter*, ValidateContext* ctx, PyObject*);
extern TypeAdapter*
ParseHint(PyObject*, PyObject*);
extern TypeAdapter*
ParseHintAndName(PyObject*, PyObject*, PyObject*);
extern PyObject*
Not_Converter(TypeAdapter*, ValidateContext*, PyObject*);
extern PyObject*
TypeAdapter_Base_Repr(TypeAdapter*);
extern PyObject*
TypeAdapter_MapParseHintTuple(PyObject*, PyObject*);
extern int
Inspector_IsInstance(TypeAdapter*, PyObject*);
extern int
Inspector_IsInstanceTypeAdapter(TypeAdapter*, PyObject*);
extern int
Inspector_IsSubclass(TypeAdapter*, PyObject*);
extern int
Inspector_Any(TypeAdapter*, PyObject*);
extern int
Inspector_No(TypeAdapter*, PyObject*);
extern int
Inspector_IsType(TypeAdapter*, PyObject*);
extern TypeAdapter*
TypeAdapter_Create(PyObject* cls,
                   PyObject* args,
                   PyObject* ob_str,
                   TypeAdapterRepr ob_repr,
                   Converter conv,
                   Inspector inspector,
                   JsonValidParser json_parser);
extern int
validator_setup(void);
extern void
validator_free(void);