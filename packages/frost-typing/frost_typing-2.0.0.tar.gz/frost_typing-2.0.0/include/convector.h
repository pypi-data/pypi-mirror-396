#define PY_SSIZE_T_CLEAN
#include "Python.h"
#define CONVECTOR_SIZE 22

typedef struct ConvParams ConvParams;

#define _MISSING_POS 0
#define _CALL_POS 1
#define _DATA_MODEL_POS 2
#define _BOOL_POS 3
#define _INT_POS 4
#define _STR_POS 5
#define _SET_POS 6
#define _LIST_POS 7
#define _DICT_POS 8
#define _NONE_POS 9
#define _FLOAT_POS 10
#define _TUPLE_POS 11
#define _BYTES_POS 12
#define _BYTES_ARR_POS 13
#define _DATE_POS 14
#define _TIME_POS 15
#define _ENUM_POS 16
#define _UUID_POS 17
#define _DATE_TIME_POS 18
#define _VALIDATION_ERR_POS 19
#define _TIME_DELTA_POS 20
#define _DECIMAL_POS 21

typedef PyObject* (*ObjectConverter)(PyObject* val, ConvParams* params);
#define ConvParams_Create(attribute)                                           \
    (ConvParams)                                                               \
    {                                                                          \
        .by_alias = 1, .exclude_unset = 0, .exclude_none = 0,                  \
        .attr = attribute, .nested = 0, .custom_ser = 1, .str_unknown = 0,     \
        .context = NULL, .serialization_info = NULL                            \
    }

typedef struct ConvParams
{
    PyObject* serialization_info;
    PyObject* context;
    PyObject* attr;
    uint16_t nested;
    unsigned char exclude_unset : 1;
    unsigned char exclude_none : 1;
    unsigned char str_unknown : 1;
    unsigned char custom_ser : 1;
    unsigned char by_alias : 1;
} ConvParams;

typedef struct SerializationInfo
{
    PyObject_HEAD PyObject* context;
    unsigned char exclude_unset;
    unsigned char exclude_none;
    unsigned char custom_ser;
    unsigned char by_alias;

} SerializationInfo;

extern PyTypeObject SerializationInfo_Type;

extern PyObject*
AsDict(PyObject* obj);
extern PyObject*
PyCopy(PyObject* obj);
extern Py_ssize_t
_UUID_AsStr(unsigned char* out, PyObject* value);
extern PyObject*
_Convector_Obj(PyObject* val, ConvParams* params);
extern PyObject*
_Convector_ObjDecrefVal(PyObject* val, ConvParams* params);
extern int
_Convector_ValidateInclude(PyObject** include, PyObject** exclude);
extern uint8_t
_Conv_Get(PyObject* val, PyObject* attr, int sub_check);
extern int
Convector_IsConstVal(PyObject* val);
extern int
_Convector_Enter(ConvParams* params);
extern void
_Convector_Leave(ConvParams* params);
extern PyObject*
_ConvParams_GetSerializationInfo(ConvParams* params);
extern void
_ConvParams_Free(ConvParams* params);
extern PyObject*
_Convector_CallMethod(PyObject* val, ConvParams* params);
extern PyObject*
_Сonvector_СallFunc(PyObject* call, PyObject* val, ConvParams* params);
extern int
convector_setup(void);
extern void
convector_free(void);