#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define DATA_MODEL_GET_SLOTS(o)                                                \
    _CAST(PyObject**, (char*)o + META_MODEL_GET_OFFSET(Py_TYPE(o)))

typedef PyObject* (*InitGetter)(PyObject*, PyObject*);

typedef struct MetaModel MetaModel;
typedef struct Field Field;
typedef struct ConvParams ConvParams;
typedef PyObject* (*ObjectConverter)(PyObject* val, ConvParams* params);

#define DataModelForeach(s, o, ...)                                            \
    for (PyObject** s = DATA_MODEL_GET_SLOTS(o),                               \
                    ** __end_##s = s + META_GET_SIZE(Py_TYPE(o));              \
         s != __end_##s;                                                       \
         s++, ##__VA_ARGS__)

typedef struct Schema Schema;

extern MetaModel DataModelType;

extern void
data_model_free(void);
extern int
data_model_setup(void);
extern int
_DataModel_SetDefault(Field*, PyObject**);
extern PyObject*
_DataModel_AsDict(PyObject* self,
                  ConvParams* params,
                  PyObject* include,
                  PyObject* exclude);
extern PyObject*
_DataModel_CallCopy(PyObject* self);
extern PyObject*
_DataModel_Copy(PyObject* self);
extern int
_DataModel_Get(Schema* sc,
               PyObject** addr,
               PyObject* self,
               PyObject** res,
               int missing_ok);
extern PyObject*
_DataModel_FastGet(Schema* sc, PyObject** addr, PyObject* self);
extern PyObject*
_DataModel_Alloc(PyTypeObject* tp);
extern int
_DataModel_Traverse(PyObject* self, visitproc visit, void* arg);