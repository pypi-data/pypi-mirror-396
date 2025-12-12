#include "computed_field.h"
#include "convector.h"
#include "data_model.h"
#include "field.h"
#include "field_serializer.h"
#include "hash_table.h"
#include "json_schema.h"
#include "meta_model.h"
#include "stddef.h"
#include "structmember.h"
#include "valid_model.h"
#include "validated_func.h"
#include "validator/discriminator.h"
#include "validator/validator.h"

static Schema*
schema_create(PyTypeObject* cls,
              PyObject* name,
              PyObject* type,
              Field* field,
              PyObject* value,
              PyObject* tp,
              Field* config)
{
    PyUnicode_InternInPlace(&name);
    PyObject* serializer = tp ? FieldSerializer_RegisteredPop(tp, name) : NULL;
    if (!serializer) {
        serializer = Field_GET_SERIALIZER(field);
    }

    field = _Field_SetConfig(field, config, name, serializer);
    Py_XDECREF(serializer);
    if (!field) {
        return NULL;
    }

    Schema* self = (Schema*)cls->tp_alloc(cls, 0);
    if (!self) {
        return NULL;
    }
    self->field = field;
    self->name = Py_NewRef(name);
    self->type = Py_NewRef(type);
    self->value = Py_XNewRef(value);
    return self;
}

Schema*
Schema_Create(PyObject* name,
              PyObject* type,
              Field* field,
              PyObject* value,
              PyObject* tp,
              Field* config)
{
    return schema_create(&SchemaType, name, type, field, value, tp, config);
}

static inline int
is_validate(Field* config, PyObject* name)
{
    return !Unicode_IsPrivate(name) ||
           IF_FIELD_CHECK(config, FIELD_VALIDATE_PRIVATE);
}

static inline int
valid_schema_set_discriminator(ValidSchema* self)
{
    if (!_TypeAdapter_СontainsDiscriminator(self->validator)) {
        return 0;
    }

    Field* new_field = _Field_SetDiscriminator(self->schema_base.field);
    if (FT_UNLIKELY(!new_field)) {
        return -1;
    }
    Py_DECREF(self->schema_base.field);
    self->schema_base.field = new_field;
    return 0;
}

static int
valid_schema_set_validator(ValidSchema* self, Field* config, PyObject* tp)
{
    PyObject* hint = is_validate(config, self->schema_base.name)
                       ? self->schema_base.type
                       : PyAny;
    self->validator = ParseHintAndName(hint, tp, self->schema_base.name);
    return self->validator ? valid_schema_set_discriminator(self) : -1;
}

ValidSchema*
ValidSchema_Create(PyObject* name,
                   PyObject* type,
                   Field* field,
                   PyObject* value,
                   PyObject* tp,
                   Field* config)
{
    ValidSchema* schema = (ValidSchema*)schema_create(
      &ValidSchemaType, name, type, field, value, tp, config);
    if (!schema) {
        return NULL;
    }
    if (valid_schema_set_validator(schema, config, tp) < 0) {
        Py_DECREF(schema);
        return NULL;
    }
    return schema;
}

Schema*
Schema_Copy(Schema* self,
            Field* field,
            PyObject* value,
            PyObject* tp,
            Field* config)
{
    Schema* schema = schema_create(
      Py_TYPE(self), self->name, self->type, field, value, tp, config);
    if (!schema) {
        return NULL;
    }

    if (!Py_IS_TYPE(schema, &ValidSchemaType)) {
        return schema;
    }

    if (!Py_IS_TYPE(self, &ValidSchemaType)) {
        if (valid_schema_set_validator((ValidSchema*)schema, config, tp) < 0) {
            Py_DECREF(schema);
            return NULL;
        }
        return schema;
    }

    TypeAdapter* vd = _TypeAdapter_Create_FieldValidator(
      _CAST_VALID_SCHEMA(self)->validator, tp, self->name);
    if (!vd) {
        Py_DECREF(schema);
        return NULL;
    }
    _CAST_VALID_SCHEMA(schema)->validator = vd;
    return schema;
}

static void
schema_dealloc(Schema* self)
{
    Py_DECREF(self->name);
    Py_DECREF(self->type);
    Py_DECREF(self->field);
    Py_XDECREF(self->value);
    Py_TYPE(self)->tp_free(self);
}

static void
valid_schema_dealloc(ValidSchema* self)
{
    Py_XDECREF(self->validator);
    schema_dealloc((Schema*)self);
}

static PyObject*
schema_repr(Schema* self)
{
    return PyUnicode_FromFormat("%.100s(name='%S', type=%S, field=%S)",
                                Py_TYPE(self)->tp_name,
                                self->name,
                                self->type,
                                self->field);
}

static PyObject*
valid_schema_repr(ValidSchema* self)
{
    return PyUnicode_FromFormat(
      "%.100s(name='%S', type=%S, field=%S, validator=%S)",
      Py_TYPE(self)->tp_name,
      self->schema_base.name,
      self->schema_base.type,
      self->schema_base.field,
      self->validator);
}

static PyMemberDef schema_members[] = {
    { "name", T_OBJECT, offsetof(Schema, name), READONLY, NULL },
    { "type", T_OBJECT, offsetof(Schema, type), READONLY, NULL },
    { "field", T_OBJECT, offsetof(Schema, field), READONLY, NULL },
    { NULL }
};

PyTypeObject SchemaType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)schema_dealloc,
    .tp_name = "frost_typing.Schema",
    .tp_repr = (reprfunc)schema_repr,
    .tp_basicsize = sizeof(Schema),
    .tp_members = schema_members,
};

static PyMemberDef valid_schema_members[] = {
    { "validator", T_OBJECT, offsetof(ValidSchema, validator), READONLY, NULL },
    { NULL }
};

PyTypeObject ValidSchemaType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)valid_schema_dealloc,
    .tp_repr = (reprfunc)valid_schema_repr,
    .tp_name = "frost_typing.ValidSchema",
    .tp_basicsize = sizeof(ValidSchema),
    .tp_members = valid_schema_members,
    .tp_base = &SchemaType,
};

int
_Schema_GetValue(Schema* self,
                 PyObject* obj,
                 PyObject** addr,
                 PyObject** res,
                 int missing_ok)
{
    Field* field = self->field;
    if (FT_UNLIKELY(IF_FIELD_CHECK(field, _FIELD_COMPUTED_FIELD))) {
        ComputedField* cf = Field_GET_FIELD_COMPUTED_FIELD(field);
        if (FT_UNLIKELY(Py_EnterRecursiveCall(" __getattribute__"))) {
            *res = NULL;
            return -1;
        }

        PyObject* tmp = PyObject_CallOneArg((PyObject*)cf, obj);
        Py_LeaveRecursiveCall();
        if (FT_UNLIKELY(!tmp)) {
            *res = NULL;
            return -1;
        }

        if (cf->cache) {
            Py_XDECREF(*addr);
            *addr = Py_NewRef(tmp);
        }
        *res = tmp;
        return 1;
    }

    if (IF_FIELD_CHECK(field, FIELD_CLASS_LOOKUP)) {
        PyObject* tmp = self->value;
        if (FT_LIKELY(tmp)) {
            *res = Py_NewRef(tmp);
            return 1;
        }
    }

    *res = NULL;
    if (FT_LIKELY(missing_ok)) {
        return 0;
    }
    RETURN_ATTRIBUT_ERROR(obj, self->name, -1);
}

static inline Field*
field_inheritance(Field* activ, Field* new)
{
    if (!activ) {
        Py_INCREF(new);
        return new;
    }

    Field* res = Field_Inheritance(new, activ);
    Py_DECREF(activ);
    return res;
}

static int
get_field_in_annotated(PyObject* hint, Field** res)
{
    if (!Py_IS_TYPE(hint, (PyTypeObject*)Py_AnnotatedAlias)) {
        *res = NULL;
        return 0;
    }

    Field* activ = NULL;
    PyObject* metadata = PyTyping_Get_Metadata(hint);
    if (!metadata) {
        goto error;
    }

    TupleForeach(field, metadata)
    {
        if (Field_Check(field)) {
            activ = field_inheritance(activ, _CAST_FIELD(field));
            if (!activ) {
                goto error;
            }
        } else if (Py_IS_TYPE(field, (PyTypeObject*)Py_AnnotatedAlias)) {
            Field* tmp;
            int r = get_field_in_annotated(field, &tmp);
            if (r < 0) {
                Py_XDECREF(activ);
                goto error;
            } else if (r) {
                activ = field_inheritance(activ, tmp);
                if (!activ) {
                    goto error;
                }
            }
        }
    }

    *res = activ;
    Py_DECREF(metadata);
    return activ ? 1 : 0;

error:
    *res = NULL;
    Py_XDECREF(metadata);
    return -1;
}

static Schema*
create_schema_from_annot(PyTypeObject* tp,
                         PyObject* name,
                         PyObject* hint,
                         PyObject* value,
                         Field* default_field,
                         Field* config,
                         SchemaCreate schema_create)
{
    Field* field;
    int r = get_field_in_annotated(hint, &field);
    if (r < 0) {
        return NULL;
    } else if (!r) {
        field = Unicode_IsPrivate(name) ? DefaultFieldPrivate : default_field;
        Py_INCREF(field);
    }

    Schema* res =
      schema_create(name, hint, field, value, (PyObject*)tp, config);
    Py_DECREF(field);
    return res;
}

static inline Schema*
copy_existing_schema(PyTypeObject* tp,
                     Schema* old,
                     PyObject* value,
                     Field* config)
{
    Field* field;
    int r = get_field_in_annotated(old->type, &field);
    if (r < 0) {
        return NULL;
    } else if (!r) {
        field = _CAST_FIELD(Py_NewRef(old->field));
    }

    Schema* res = Schema_Copy(
      old, field, value ? value : old->value, (PyObject*)tp, config);
    Py_DECREF(field);
    return res;
}

Py_ssize_t
Schema_GetArgsCnt(PyObject* schemas)
{
    Py_ssize_t cnt = 0;
    _SchemaForeach(sc, schemas)
    {
        cnt += !IS_FIELD_KW_ONLY(sc->field->flags);
    }
    return cnt;
}

static inline PyObject*
schema_create_list_old(PyObject* base_schemas,
                       SchemaCreate create_fn,
                       PyObject* annotations,
                       MetaModel* meta,
                       Field* field,
                       Field* config,
                       PyObject* defaults)
{
    PyObject* res = PyList_New(0);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    PyTypeObject* tp = (PyTypeObject*)meta;
    Schema* sc;

    _SchemaForeach(old_sc, base_schemas)
    {
        PyObject* hint = _PyDict_GetItem_Ascii(annotations, old_sc->name);
        PyObject* value = _PyDict_GetItem_Ascii(defaults, old_sc->name);

        if (hint) {
            if (PyDict_DelItem(annotations, old_sc->name) < 0) {
                goto error;
            }
            sc = create_schema_from_annot(
              tp, old_sc->name, hint, value, field, config, create_fn);
        } else {
            sc = copy_existing_schema(tp, old_sc, value, config);
        }

        if (!sc || _PyList_Append_Decref(res, (PyObject*)sc) < 0) {
            goto error;
        }
    }
    return res;

error:
    Py_DECREF(res);
    return NULL;
}

static Schema*
schema_search(PyObject* self, PyObject* name)
{
    _SchemaForeach(sc, self)
    {
        if (sc->name == name) {
            return sc;
        }
    }
    return NULL;
}

PyObject*
Schema_Concat(PyObject* self, PyObject* other)
{
    PyObject* list = PyList_New(0);
    if (!list) {
        return NULL;
    }

    _SchemaForeach(sc, self)
    {
        Schema* override = schema_search(other, sc->name);
        if (override) {
            sc = override;
        }

        if (PyList_Append(list, (PyObject*)sc) < 0) {
            Py_DECREF(list);
            return NULL;
        }
    }

    _SchemaForeach(sc, other)
    {
        Schema* override = schema_search(self, sc->name);
        if (override) {
            continue;
        }

        if (PyList_Append(list, (PyObject*)sc) < 0) {
            Py_DECREF(list);
            return NULL;
        }
    }

    PyObject* res = PySequence_Tuple(list);
    Py_DECREF(list);
    return res;
}

PyObject*
Schema_CreateTuple(PyObject* base_schemas,
                   SchemaCreate create_fn,
                   PyObject* annotations,
                   MetaModel* meta,
                   Field* field,
                   Field* config,
                   PyObject* defaults)
{
    PyObject* list = schema_create_list_old(
      base_schemas, create_fn, annotations, meta, field, config, defaults);
    if (FT_UNLIKELY(!list)) {
        return NULL;
    }

    Py_ssize_t pos = 0;
    PyObject *key, *hint;
    while (PyDict_Next(annotations, &pos, &key, &hint)) {
        if (FT_UNLIKELY(!CheckValidityOfAttribute(key))) {
            goto error;
        }

        PyObject* value = Dict_GetItemNoError(defaults, key);
        Schema* sc = create_schema_from_annot(
          (PyTypeObject*)meta, key, hint, value, field, config, create_fn);
        if (FT_UNLIKELY(!sc ||
                        _PyList_Append_Decref(list, (PyObject*)sc) < 0)) {
            goto error;
        }
    }

    PyObject* res = PySequence_Tuple(list);
    Py_DECREF(list);
    return res;

error:
    Py_DECREF(list);
    return NULL;
}

PyObject*
_ValidatedFunc_CreateSchema(PyObject* annot,
                            Py_ssize_t acnt,
                            PyObject* defaults)
{
    PyObject* res = PyTuple_New(PyDict_GET_SIZE(annot));
    PyObject *name, *hint;
    Py_ssize_t pos = 0, i = 0;
    while (PyDict_Next(annot, &pos, &name, &hint)) {
        if (FT_UNLIKELY(!CheckValidityOfAttribute(name))) {
            goto error;
        }

        PyObject* dflt = Dict_GetItemNoError(defaults, name);
        Field* field = _Field_CreateValidatedFunc(dflt, i >= acnt);
        if (!field) {
            goto error;
        }

        PyObject* sc = (PyObject*)ValidSchema_Create(
          name, hint, field, NULL, NULL, DefaultConfigValid);
        if (!sc) {
            goto error;
        }

        PyTuple_SET_ITEM(res, i++, sc);
    }
    return res;

error:
    Py_DECREF(res);
    return NULL;
}

int
_ValidSchema_ValidateInit(ValidSchema* sc,
                          PyObject* val,
                          PyObject* restrict* addr,
                          ValidateContext* restrict ctx,
                          ValidationError** restrict err)
{
    PyObject* tmp = TypeAdapter_Conversion(sc->validator, ctx, val);
    if (tmp) {
        Py_XDECREF(*addr);
        *addr = tmp;
        return 1;
    }
    return ValidationError_Create(
      SCHEMA_GET_NAME(_CAST(Schema*, sc)), sc->validator, val, ctx->model, err);
}

int
schema_setup(void)
{
    SchemaType.tp_flags |= Py_TPFLAGS_BASETYPE;
    if (FT_UNLIKELY(PyType_Ready(&SchemaType) < 0)) {
        return -1;
    }

    if (FT_UNLIKELY(PyType_Ready(&ValidSchemaType) < 0)) {
        return -1;
    }

    SchemaType.tp_flags ^= Py_TPFLAGS_BASETYPE;
    return 0;
}

inline int
_Schema_VecInitFinish(PyObject* schemas,
                      PyObject** stack,
                      ValidateContext* ctx,
                      PyObject* const* args,
                      PyObject* kwnames)
{
    ValidationError* err = NULL;
    PyObject* kwargs = NULL;

    _SchemaForeach(sc, schemas, stack++)
    {
        PyObject* tmp = *stack;
        if (FT_LIKELY(tmp)) {
            if (FT_UNLIKELY(
                  ValidSchema_ValidateInit(sc, tmp, stack, ctx, &err) < 0)) {
                goto error;
            }
            continue;
        }

        int r = _DataModel_SetDefault(sc->field, stack);
        if (FT_LIKELY(r)) {
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            continue;
        }

        if (FT_UNLIKELY(!IS_FIELD_INIT(sc->field->flags))) {
            continue;
        }

        if (FT_UNLIKELY(!kwargs)) {
            kwargs = _Dict_FromKwnames(args, kwnames);
            if (FT_UNLIKELY(!kwargs)) {
                goto error;
            }
        }

        if (FT_UNLIKELY(ValidationError_CreateMissing(
                          SCHEMA_GET_NAME(sc), kwargs, ctx->model, &err) < 0)) {
            goto error;
        }
    }

    Py_XDECREF(kwargs);
    if (FT_UNLIKELY(err)) {
        ValidationError_RaiseWithModel(err, ctx->model);
        return -1;
    }
    return 0;

error:
    Py_XDECREF(kwargs);
    Py_XDECREF(err);
    return -1;
}

inline int
_Schema_VectorInitKw(PyObject** stack,
                     HashTable* map,
                     int fail_on_extra_init,
                     PyObject* const* args,
                     PyObject* kwnames)
{
    TupleForeach(name, kwnames, args++)
    {
        const Py_ssize_t offset = _HashTable_Get(map, name);
        if (FT_LIKELY(offset != -1)) {
            PyObject** addr = GET_ADDR(stack, offset);
            Py_XDECREF(*addr);
            *addr = Py_NewRef(*args);
        } else if (FT_UNLIKELY(fail_on_extra_init)) {
            PyErr_Format(PyExc_TypeError,
                         "__init__() got an unexpected keyword argument '%U'",
                         name);
            return -1;
        }
    }
    return 0;
}

void
schema_free(void)
{
}