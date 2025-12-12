#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define _Schema_GET_VALIDATOR(s) _CAST(ValidSchema*, s)->validator
#define SCHEMA_BY_OFFSET(s, o) _CAST(Schema*, GET_OBJ(TUPLE_ITEMS(s), o))
#define SCHEMA_GET_SNAME(a, s)                                                 \
    (a && IF_FIELD_CHECK(s->field, FIELD_SERIALIZATION_ALIAS))                 \
      ? Field_GET_SERIALIZATION_ALIAS(s->field)                                \
      : s->name

#define SCHEMA_GET_NAME(s)                                                     \
    !IF_FIELD_CHECK(s->field, FIELD_ALIAS) ? s->name : Field_GET_ALIAS(s->field)

#define _CAST_VALID_SCHEMA(s) _CAST(ValidSchema*, s)

#define _SchemaForeach(s, schemas, ...)                                        \
    for (Schema** __##schema = (Schema**)TUPLE_ITEMS(schemas),                 \
                  ** __end_##schema = __##schema + PyTuple_GET_SIZE(schemas),  \
                  *s = *__##schema;                                            \
         __##schema != __end_##schema;                                         \
         s = *++__##schema, ##__VA_ARGS__)

#define ValidSchema_ValidateInit(sc, val, addr, ctx, err)                      \
    _ValidSchema_ValidateInit(_CAST(ValidSchema*, sc), val, addr, ctx, err)

typedef struct ValidateContext ValidateContext;
typedef struct ValidationError ValidationError;
typedef struct HashTable HashTable;
typedef struct MetaModel MetaModel;
typedef struct Field Field;

typedef struct Schema
{
    PyObject_HEAD Field* field;
    PyObject* name;
    PyObject* type;
    PyObject* value;
} Schema;

typedef struct TypeAdapter TypeAdapter;
typedef struct ValidSchema
{
    Schema schema_base;
    TypeAdapter* validator;
} ValidSchema;

typedef Schema* (*SchemaCreate)(PyObject* name,
                                PyObject* type,
                                Field* field,
                                PyObject* value,
                                PyObject* tp,
                                Field* config);

extern PyTypeObject SchemaType, ValidSchemaType;
extern Schema*
Schema_Create(PyObject* name,
              PyObject* type,
              Field* field,
              PyObject* value,
              PyObject* tp,
              Field* config);
extern ValidSchema*
ValidSchema_Create(PyObject* name,
                   PyObject* type,
                   Field* field,
                   PyObject* value,
                   PyObject* tp,
                   Field* config);
PyObject*
_ValidatedFunc_CreateSchema(PyObject* annot,
                            Py_ssize_t acnt,
                            PyObject* defaults);
extern Schema*
Schema_Copy(Schema* self,
            Field* field,
            PyObject* value,
            PyObject* tp,
            Field* config);
extern Py_ssize_t
Schema_GetArgsCnt(PyObject* schemas);
extern PyObject*
Schema_Concat(PyObject* self, PyObject* other);
extern PyObject*
Schema_CreateTuple(PyObject* base_schemas,
                   SchemaCreate create_fn,
                   PyObject* annotations,
                   MetaModel* meta,
                   Field* field,
                   Field* config,
                   PyObject* defaults);
extern int
_Schema_GetValue(Schema* self,
                 PyObject* obj,
                 PyObject** addr,
                 PyObject** res,
                 int missing_ok);
extern int
_ValidSchema_ValidateInit(ValidSchema* sc,
                          PyObject* val,
                          PyObject* restrict* addr,
                          ValidateContext* restrict ctx,
                          ValidationError** restrict err);
extern int
_Schema_VecInitFinish(PyObject* schemas,
                      PyObject** stack,
                      ValidateContext* ctx,
                      PyObject* const* args,
                      PyObject* kwnames);
extern int
_Schema_VectorInitKw(PyObject** stack,
                     HashTable* map,
                     int fail_on_extra_init,
                     PyObject* const* args,
                     PyObject* kwnames);
extern int
schema_setup(void);
extern void
schema_free(void);
