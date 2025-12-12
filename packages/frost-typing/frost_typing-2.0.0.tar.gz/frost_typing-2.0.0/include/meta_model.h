#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "schema.h"

#define TPFLAGS_META_SUBCLASS (1UL << 16)

#define _CAST_META(o) _CAST(MetaModel*, o)
#define META_GET_SIZE(m) Py_SIZE(_CAST_META(m)->schemas)
#define META_MODEL_GET_OFFSET(tp) _CAST_META(tp)->slot_offset
#define META_GET_SCHEMA(m, i)                                                  \
    ((Schema*)PyTuple_GET_ITEM(_CAST_META(m)->schemas, i))

#define META_GET_SCHEMA_BY_OFFSET(m, o)                                        \
    SCHEMA_BY_OFFSET(_CAST_META(m)->schemas, o)

#define Meta_IS_SUBCLASS(tp)                                                   \
    (_CAST(PyTypeObject*, tp)->tp_flags & TPFLAGS_META_SUBCLASS)
#define Meta_Check(op) Meta_IS_SUBCLASS(Py_TYPE(op))
#define Meta_CheckExact(op) Py_IS_TYPE((op), &MetaModelType)

#define _META_GET_SCHEMAS(m) ((Schema**)TUPLE_ITEMS(_CAST_META(m)->schemas))
#define SchemaForeach(s, m, ...)                                               \
    for (Schema** __##schema = _META_GET_SCHEMAS(m),                           \
                  ** __end_##schema = __##schema + META_GET_SIZE(m),           \
                  *s = *__##schema;                                            \
         __##schema != __end_##schema;                                         \
         s = *++__##schema, ##__VA_ARGS__)

typedef struct HashTable HashTable;
typedef int (*vectorcall_init)(PyObject* self,
                               PyObject* const* args,
                               size_t nargsf,
                               PyObject* kwnames);

typedef struct MetaModel
{
    PyHeapTypeObject head;
    HashTable* attr_map;
    HashTable* init_map;
    vectorcall_init vec_init;
    Py_ssize_t slot_offset;
    Py_ssize_t args_only;
    PyObject* schemas;
    Field* config;
    PyObject* __copy__;
    PyObject* __as_dict__;
    PyObject* __as_json__;
    PyObject* __post_init__;
} MetaModel;

extern PyTypeObject MetaModelType;
extern int
_MetaModel_CallPostInit(PyObject* self);
extern int
meta_model_setup(void);
extern void
meta_model_free(void);
extern int
_MetaModel_SetFunc(MetaModel* self,
                   PyObject* name,
                   unsigned long check_flags,
                   Py_ssize_t offset);
extern PyObject*
_MetaModel_Vectorcall(MetaModel* cls,
                      PyObject* const* args,
                      size_t nargsf,
                      PyObject* kwnames);
extern MetaModel*
MetaModel_New(PyTypeObject*, PyObject*, PyObject*, SchemaCreate);