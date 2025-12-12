#include "json_schema.h"
#include "computed_field.h"
#include "convector.h"
#include "field.h"
#include "field_serializer.h"
#include "meta_valid_model.h"
#include "valid_model.h"
#include "validated_func.h"
#include "validator/validator.h"

#if _USED_JSON_SCHEMA
static PyObject *__type, *__title, *__object, *__required, *__properties,
  *__items, *__default, *__integer, *__boolean, *__number, *__string,
  *__uniqueItems, *__array, *__time, *__date, *__date_time, *__enum, *__anyOf,
  *__additionalProperties, *__ge, *__gt, *__le, *__lt, *__minLength, *___null,
  *__maxLength, *__pattern, *___defs, *___ref, *__allOf, *__examples,
  *__readOnly, *__format, *__binary, *__uuid;

typedef struct Compiller
{
    Py_ssize_t nesting_level;
    ContextManager* ctx;
    PyObject* defs;
    int use_defs;
} Compiller;

typedef PyObject* (*ObjectParser)(Compiller*, PyObject*, PyObject*);
#define RECURSION_LIMIT 3000

static int
compiller_enter(Compiller* compiller)
{
    if (compiller->nesting_level++ > RECURSION_LIMIT) {
        PyErr_SetString(PyExc_RecursionError,
                        "maximum recursion depth exceeded"
                        " while encoding a JSON object");
        return -1;
    }
    return 0;
}

static inline void
compiller_leave(Compiller* compiller)
{
    compiller->nesting_level--;
}

#endif

#if _USED_JSON_SCHEMA
static PyObject*
schema_json(Compiller* compiller, PyObject* hint, PyObject* title);
static int
schema_json_by_schemas(Compiller* compiller,
                       PyObject* schemas,
                       PyObject* properties,
                       PyObject* required);

static PyObject*
schema_json_base(PyObject* type, PyObject* title)
{
    PyObject* dict = PyDict_New();
    if (dict == NULL) {
        return NULL;
    }

    if (_PyDict_SetItem_Ascii(dict, __type, type) < 0) {
        Py_DECREF(dict);
        return NULL;
    }

    if (title && _PyDict_SetItem_Ascii(dict, __title, title) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
schema_json_base_object(PyObject** required,
                        PyObject** properties,
                        PyObject* title)
{
    PyObject *req, *prop, *dict;
    dict = schema_json_base(__object, title);
    if (dict == NULL) {
        return NULL;
    }

    req = PyList_New(0);
    if (req == NULL) {
        goto error;
    }

    if (_PyDict_SetItemAsciiDecrefVal(dict, __required, req) < 0) {
        goto error;
    }

    prop = PyDict_New();
    if (properties == NULL) {
        goto error;
    }

    if (_PyDict_SetItemAsciiDecrefVal(dict, __properties, prop) < 0) {
        goto error;
    }

    *required = req;
    *properties = prop;
    return dict;
error:
    *required = NULL;
    *properties = NULL;
    Py_DECREF(dict);
    return NULL;
}

static PyObject*
schema_json_base_sequence(PyObject** items, PyObject* title)
{
    PyObject *dict, *tmp;
    dict = schema_json_base(__array, title);
    if (dict == NULL) {
        return NULL;
    }

    tmp = PyDict_New();
    *items = tmp;
    if (tmp == NULL) {
        Py_DECREF(dict);
        return NULL;
    }

    if (_PyDict_SetItemAsciiDecrefVal(dict, __items, tmp) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
schema_json_unicode(Compiller* compiller, PyObject* obj, PyObject* title)
{
    PyObject* hint = PyTyping_Eval(obj, NULL);
    if (hint == NULL) {
        return NULL;
    }
    PyObject* res = schema_json(compiller, hint, title);
    Py_DECREF(hint);
    return res;
}

static PyObject*
schema_json_set_allOf(PyObject* dict)
{
    int r = PyDict_Contains(dict, ___ref);
    if (r < 0) {
        return NULL;
    }
    if (!r) {
        return Py_NewRef(dict);
    }

    PyObject* list = PyList_New(1);
    if (!list) {
        return NULL;
    }

    PyList_SET_ITEM(list, 0, Py_NewRef(dict));
    PyObject* tmp = PyDict_New();
    if (!tmp) {
        Py_DECREF(list);
        return NULL;
    }

    if (_PyDict_SetItemAsciiDecrefVal(tmp, __allOf, list) < 0) {
        return NULL;
    }
    return tmp;
}

static PyObject*
schema_json_schema(Compiller* compiller,
                   PyObject* type,
                   PyObject* name,
                   PyObject* value,
                   Field* field)
{
    PyObject *dict, *title;
    if (IF_FIELD_CHECK(field, FIELD_TITLE)) {
        title = Py_NewRef(_Field_GetAttr(field, FIELD_TITLE));
    } else {
        title = PyObject_CallMethodNoArgs(name, __title);
        if (!title) {
            return NULL;
        }
    }

    dict = schema_json(compiller, type, title);
    Py_DECREF(title);
    if (dict == NULL) {
        return NULL;
    }

    // There are no additional fields
    if (!value && IS_FIELD_INIT(field->flags) &&
        !(field->flags & (FIELD_TITLE | FIELD_EXAMPLES |
                          FIELD_JSON_SCHEMA_EXTRA | FIELD_DESCRIPTION))) {
        return dict;
    }

    PyObject* tmp = schema_json_set_allOf(dict);
    Py_DECREF(dict);
    if (!tmp) {
        return NULL;
    }
    dict = tmp;

    // Set the header only if it is redefined
    if (IF_FIELD_CHECK(field, FIELD_TITLE)) {
        if (!PyDict_SetDefault(
              dict, __title, _Field_GetAttr(field, FIELD_TITLE))) {
            goto error;
        }
    }

    if (IF_FIELD_DESCRIPTION(field, FIELD_DESCRIPTION)) {
        if (_PyDict_SetItem_Ascii(
              dict, __description, _Field_GetAttr(field, FIELD_DESCRIPTION)) <
            0) {
            goto error;
        }
    }

    if (IF_FIELD_CHECK(field, FIELD_EXAMPLES)) {
        if (_PyDict_SetItem_Ascii(
              dict, __examples, _Field_GetAttr(field, FIELD_EXAMPLES)) < 0) {
            goto error;
        }
    }

    if (value && _PyDict_SetItem_Ascii(dict, __default, value) < 0) {
        goto error;
    }

    if (!IS_FIELD_INIT(field->flags) &&
        _PyDict_SetItem_Ascii(dict, __readOnly, Py_True) < 0) {
        goto error;
    }

    PyObject* extra = Field_GET_JSON_SCHEMA_EXTRA(field);
    if (extra && PyDict_Update(dict, extra) < 0) {
        goto error;
    }

    return dict;
error:
    Py_DECREF(dict);
    return NULL;
}

static PyObject*
schema_json_typed_dict_nested(Compiller* compiller,
                              PyObject* obj,
                              PyObject* title)
{
    PyObject *r_keys, *annot, *dict, *required, *properties;
    annot = PyTypedDict_Getannotations(obj);
    if (!annot) {
        return NULL;
    }

    r_keys = PyTyping_Get_RequiredKeys(obj);
    if (!r_keys) {
        Py_DECREF(annot);
        return NULL;
    }

    dict = schema_json_base_object(&required, &properties, title);
    if (!dict) {
        goto error;
    }

    Py_ssize_t pos = 0;
    PyObject *name, *hint, *nested_dict;
    while (PyDict_Next(annot, &pos, &name, &hint)) {
        nested_dict =
          schema_json_schema(compiller, hint, name, NULL, DefaultField);
        if (!nested_dict) {
            goto error;
        }
        if (PyDict_SetItemDecrefVal(properties, name, nested_dict) < 0) {
            goto error;
        }

        int r = PySet_Contains(r_keys, name);
        if (r < 0) {
            goto error;
        }

        if (r && PyList_Append(required, name) < 0) {
            goto error;
        }
    }

    Py_DECREF(r_keys);
    Py_DECREF(annot);

    if (!PyList_GET_SIZE(required)) {
        if (PyDict_DelItem(dict, __required) < 0) {
            goto error;
        }
    }
    return dict;
error:
    Py_DECREF(annot);
    Py_DECREF(r_keys);
    Py_XDECREF(dict);
    return NULL;
}

static PyObject*
schema_json_validated_func_nested(Compiller* compiller,
                                  ValidatedFunc* obj,
                                  PyObject* title)
{
    PyObject *required, *properties, *dict;

    title = _ValidatedFunc_GetName(obj);
    if (!title) {
        return NULL;
    }

    dict = schema_json_base_object(&required, &properties, title);
    Py_DECREF(title);
    if (dict == NULL) {
        return NULL;
    }

    if (schema_json_by_schemas(compiller, obj->schemas, properties, required) <
        0) {
        goto error;
    }

    if (!PyList_GET_SIZE(required)) {
        if (PyDict_DelItem(dict, __required) < 0) {
            goto error;
        }
    }

    return dict;
error:
    Py_DECREF(dict);
    return NULL;
}

static inline PyObject*
object_create_ref(PyObject* title)
{
    return PyUnicode_FromFormat("#/$defs/%S", title, NULL);
}

static inline PyObject*
object_create_ref_dict(PyObject* ref)
{
    PyObject* dict;
    dict = PyDict_New();
    if (!dict) {
        return NULL;
    }
    if (_PyDict_SetItem_Ascii(dict, ___ref, ref) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
schema_json_object_nested(Compiller* compiller,
                          PyObject* obj,
                          ObjectParser parser,
                          PyObject* name,
                          PyObject* ref)
{
    PyObject* dict;
    if (compiller->defs) {
        int r = PyDict_Contains(compiller->defs, ref);
        if (r) {
            return r < 0 ? NULL : object_create_ref_dict(ref);
        }
    }

    int use_defs = compiller->use_defs;
    if (!use_defs) {
        compiller->use_defs = 1;
    }

    dict = parser(compiller, obj, name);
    if (!dict) {
        return NULL;
    }

    if (!PyDict_SetDefault(dict, __title, name)) {
        Py_DECREF(dict);
        return NULL;
    }

    if (!use_defs) {
        return dict;
    }

    if (!compiller->defs) {
        compiller->defs = PyDict_New();
        if (!compiller->defs) {
            Py_DECREF(dict);
            return NULL;
        }
    }

    if (PyDict_SetItemDecrefVal(compiller->defs, name, dict) < 0) {
        return NULL;
    }

    dict = object_create_ref_dict(ref);
    return dict;
}

static PyObject*
schema_json_object(Compiller* compiller,
                   PyObject* obj,
                   UNUSED PyObject* title,
                   ObjectParser parser)
{

    PyObject *res, *ref, *name;
    if (PyType_Check(obj)) {
        name = PyObject_Get__name__(_CAST(PyTypeObject*, obj));
    } else {
        name = PyObject_Repr(obj);
    }

    if (!name) {
        return NULL;
    }

    ref = object_create_ref(name);
    if (!ref) {
        Py_DECREF(name);
        return NULL;
    }
    res = schema_json_object_nested(compiller, obj, parser, name, ref);
    Py_DECREF(name);
    Py_DECREF(ref);
    return res;
}

static inline PyObject*
enum_get_member_names(PyObject* obj)
{
    PyObject* member_names = PyTyping_Get__value2member_map_(obj);
    if (!member_names) {
        return NULL;
    }

    PyObject* res = PyDict_Keys(member_names);
    Py_DECREF(member_names);
    return res;
}

static PyObject*
schema_json_enum_nested(Compiller* compiller, PyObject* obj, PyObject* title)
{
    PyObject *member_names, *type, *dict;
    type = PyObject_GetAttrString(obj, "_member_type_");
    if (type == NULL) {
        return NULL;
    }

    dict = schema_json(compiller, type, title);
    Py_DECREF(type);
    if (dict == NULL) {
        return NULL;
    }

    member_names = enum_get_member_names(obj);
    if (member_names == NULL) {
        goto error;
    }

    if (_PyDict_SetItemAsciiDecrefVal(dict, __enum, member_names) < 0) {
        goto error;
    }
    return dict;
error:
    Py_DECREF(dict);
    return NULL;
}

static int
schema_json_comppartion(PyObject* dict, ComparisonConstraints* con)
{
    if (con->ge &&
        PyDict_SetItemWithTransform(dict, __ge, con->ge, AsDict) < 0) {
        return -1;
    }
    if (con->gt &&
        PyDict_SetItemWithTransform(dict, __gt, con->gt, AsDict) < 0) {
        return -1;
    }
    if (con->le &&
        PyDict_SetItemWithTransform(dict, __le, con->le, AsDict) < 0) {
        return -1;
    }
    if (con->lt &&
        PyDict_SetItemWithTransform(dict, __lt, con->lt, AsDict) < 0) {
        return -1;
    }
    return 0;
}

static int
schema_json_sequence_constraints(PyObject* dict, SequenceConstraints* con)
{
    if (con->max_length != -1) {
        PyObject* tmp = PyLong_FromSsize_t(con->max_length);
        if (tmp == NULL) {
            return -1;
        }
        if (_PyDict_SetItemAsciiDecrefVal(dict, __maxLength, tmp) < 0) {
            return -1;
        }
    }
    if (con->min_length != -1) {
        PyObject* tmp = PyLong_FromSsize_t(con->min_length);
        if (tmp == NULL) {
            return -1;
        }
        if (_PyDict_SetItemAsciiDecrefVal(dict, __minLength, tmp) < 0) {
            return -1;
        }
    }
    return 0;
}

static int
schema_json_string(PyObject* dict, StringConstraints* con)
{
    if (schema_json_sequence_constraints(dict, (SequenceConstraints*)con) < 0) {
        return -1;
    }

    if (con->pattern_string) {
        return _PyDict_SetItem_Ascii(dict, __pattern, con->pattern_string);
    }
    return 0;
}

static int
schema_json_annotated_nested(PyObject* dict, PyObject* obj, PyObject* title)
{
    PyObject* metadata = PyTyping_Get_Metadata(obj);
    if (!metadata) {
        return -1;
    }

    TupleForeach(val, metadata)
    {
        if (ComparisonConstraints_CheckExact(val)) {
            if (schema_json_comppartion(dict, (ComparisonConstraints*)val) <
                0) {
                goto error;
            }
            continue;
        }
        if (StringConstraints_CheckExact(val)) {
            if (schema_json_string(dict, (StringConstraints*)val) < 0) {
                goto error;
            }
            continue;
        }
        if (SequenceConstraints_CheckExact(val)) {
            if (schema_json_sequence_constraints(
                  dict, (SequenceConstraints*)val) < 0) {
                goto error;
            }
            continue;
        }
        if (Py_IS_TYPE(val, (PyTypeObject*)Py_AnnotatedAlias)) {
            if (schema_json_annotated_nested(dict, val, title) < 0) {
                goto error;
            }
        }
    }

    Py_DECREF(metadata);
    return 0;
error:
    Py_DECREF(metadata);
    return -1;
}

static PyObject*
schema_json_annotated(Compiller* compiller, PyObject* obj, PyObject* title)
{
    PyObject *origin, *dict;
    origin = PyTyping_Get_Origin(obj);
    if (!origin) {
        RETURN_ATTRIBUT_ERROR(obj, __origin__, NULL);
    }

    dict = schema_json(compiller, origin, title);
    Py_DECREF(origin);
    if (dict == NULL) {
        return NULL;
    }

    if (schema_json_annotated_nested(dict, obj, title) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
schema_json_uuid(PyObject* title)
{
    PyObject* dict = schema_json_base(__string, title);
    if (dict && _PyDict_SetItem_Ascii(dict, __format, __uuid) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
schema_json_union(Compiller* compiller, PyObject* obj, PyObject* title)
{
    PyObject *args, *anyOf, *dict;
    Py_ssize_t size;

    args = PyTyping_Get_Args(obj);
    if (args == NULL) {
        return NULL;
    }

    dict = PyDict_New();
    if (dict == NULL) {
        Py_DECREF(args);
        return NULL;
    }

    size = PyTuple_GET_SIZE(args);
    anyOf = PyList_New(size);
    if (anyOf == NULL) {
        goto error;
    }

    if (_PyDict_SetItemAsciiDecrefVal(dict, __anyOf, anyOf) < 0) {
        goto error;
    }

    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject* nested_dict =
          schema_json(compiller, PyTuple_GET_ITEM(args, i), title);
        if (nested_dict == NULL) {
            goto error;
        }
        PyList_SET_ITEM(anyOf, i, nested_dict);
    }

    Py_DECREF(args);
    return dict;
error:
    Py_DECREF(args);
    Py_DECREF(dict);
    return NULL;
}

static PyObject*
schema_json_literal(PyObject* obj)
{
    PyObject* dict = PyDict_New();
    if (dict == NULL) {
        return NULL;
    }
    PyObject* args = PyTyping_Get_Args(obj);
    if (args == NULL) {
        return NULL;
    }
    if (_PyDict_SetItemAsciiDecrefVal(dict, __enum, args) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
schema_json_type_var(Compiller* compiller, PyObject* obj, PyObject* title)
{
    if (compiller->ctx) {
        PyObject* hint = _ContextManager_Get_THint(obj, compiller->ctx);
        if (hint) {
            return schema_json(compiller, hint, title);
        }
    }

    PyObject *bound, *constraints, *dict;
    Py_ssize_t constraints_size;

    bound = PyTyping_Get_Bound(obj);
    if (bound == NULL) {
        return NULL;
    }
    if (bound != Py_None) {
        PyObject* res = Schema_JsonSchema(bound);
        Py_DECREF(bound);
        return res;
    }
    Py_DECREF(bound);

    dict = PyDict_New();
    if (dict == NULL) {
        return NULL;
    }
    constraints = PyTyping_Get_Constraints(obj);
    if (constraints == NULL) {
        Py_DECREF(dict);
        return NULL;
    }

    constraints_size = PyTuple_GET_SIZE(constraints);
    if (constraints_size) {
        PyObject *nested_dict, *anyOf, *val;
        anyOf = PyList_New(constraints_size);
        if (anyOf == NULL) {
            goto error;
        }

        if (_PyDict_SetItemAsciiDecrefVal(dict, __anyOf, anyOf) < 0) {
            goto error;
        }

        for (Py_ssize_t i = 0; i < constraints_size; i++) {
            val = PyTuple_GET_ITEM(constraints, i);
            nested_dict = schema_json(compiller, val, title);
            if (nested_dict == NULL) {
                goto error;
            }
            PyList_SET_ITEM(anyOf, i, nested_dict);
        }
    }
    return dict;
error:
    Py_DECREF(constraints);
    Py_DECREF(dict);
    return NULL;
}

static inline PyObject*
schema_json_forward_ref(Compiller* compiller, PyObject* obj, PyObject* title)
{
    PyObject* hint = PyTyping_Evaluate_Forward_Ref(obj, NULL);
    if (hint == NULL) {
        return NULL;
    }

    PyObject* res = schema_json(compiller, hint, title);
    Py_DECREF(hint);
    return res;
}

static inline PyObject*
schema_json_required(Compiller* compiller, PyObject* hint, PyObject* title)
{
    PyObject *res, *type_args = PyTyping_Get_Args(hint);
    if (!type_args) {
        return NULL;
    }

    if (PyTuple_GET_SIZE(type_args) != 1) {
        PyErr_Format(PyExc_ValueError,
                     "%.100S accepts only a single type. Got %.100S",
                     hint,
                     type_args);
        Py_DECREF(type_args);
        return NULL;
    }

    res = schema_json(compiller, PyTuple_GET_ITEM(type_args, 0), title);
    Py_DECREF(type_args);
    return res;
}

static PyObject*
schema_json_sequence(Compiller* compiller,
                     PyObject* obj,
                     PyObject* title,
                     PyObject* origin)
{
    PyObject *args, *dict_nested, *dict = NULL;
    if (!PyType_Check(origin)) {
        return _RaiseInvalidType(
          "__origin__", "type", Py_TYPE(origin)->tp_name);
    }

    args = PyTyping_Get_Args(obj);
    if (args == NULL) {
        return NULL;
    }
    int eq =
      PyType_FastSubclass((PyTypeObject*)origin, Py_TPFLAGS_DICT_SUBCLASS);
    if (eq) {
        if (PyTuple_GET_SIZE(args) != 2) {
            PyErr_SetString(
              PyExc_ValueError,
              "Expected mapping to have exactly 2 sequence parameters");
            goto error;
        }

        dict = schema_json_base(__object, title);
        if (dict == NULL) {
            goto error;
        }

        dict_nested = schema_json(compiller, PyTuple_GET_ITEM(args, 1), NULL);
        Py_DECREF(args);
        if (!dict_nested) {
            Py_DECREF(dict);
            return NULL;
        }

        if (_PyDict_SetItemAsciiDecrefVal(
              dict, __additionalProperties, dict_nested) < 0) {
            Py_DECREF(dict);
            return NULL;
        }
        return dict;
    }

    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_Format(PyExc_ValueError,
                     "Only Generic Ones with 1 argument are supported, but "
                     "received '%.100S'",
                     obj);
        goto error;
    }

    dict = schema_json(compiller, origin, title);
    if (dict == NULL) {
        goto error;
    }

    dict_nested = schema_json(compiller, PyTuple_GET_ITEM(args, 0), NULL);
    if (dict_nested == NULL) {
        goto error;
    }

    int r = _PyDict_SetItem_Ascii(dict, __items, dict_nested);
    Py_DECREF(dict_nested);
    Py_DECREF(args);
    if (r < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
error:
    Py_XDECREF(dict);
    Py_DECREF(args);
    return NULL;
}

int
schema_json_by_schemas(Compiller* compiller,
                       PyObject* schemas,
                       PyObject* properties,
                       PyObject* required)
{
    _SchemaForeach(schema, schemas)
    {
        PyObject* name = SCHEMA_GET_NAME(schema);
        if (Unicode_IsPrivate(name)) {
            continue;
        }

        if (PyUnicode_Check(schema->type)) {
            PyObject* hint = PyTyping_Eval(schema->type, NULL);
            if (!hint) {
                return -1;
            }
            Py_DECREF(schema->type);
            schema->type = hint;
        }

        PyObject* nested_dict =
          schema_json_schema(compiller,
                             schema->type,
                             name,
                             _Field_GetAttr(schema->field, FIELD_DEFAULT),
                             schema->field);
        if (!nested_dict) {
            return -1;
        }

        if (PyDict_SetItemDecrefVal(properties, name, nested_dict) < 0) {
            return -1;
        }

        if (!IS_FIELD_DEFAULT(schema->field->flags)) {
            if (PyList_Append(required, name) < 0) {
                return -1;
            }
        }
    }
    return 0;
}

static PyObject*
schema_json_meta_mode_nested(Compiller* compiller,
                             MetaModel* meta,
                             PyObject* title)
{
    PyObject *required, *properties, *dict;
    if (IF_FIELD_CHECK(meta->config, FIELD_TITLE)) {
        title = _Field_GetAttr(meta->config, FIELD_TITLE);
    }

    dict = schema_json_base_object(&required, &properties, title);
    if (dict == NULL) {
        return NULL;
    }

    if (IF_FIELD_CHECK(meta->config, FIELD_EXAMPLES)) {
        if (_PyDict_SetItem_Ascii(
              dict, __examples, _Field_GetAttr(meta->config, FIELD_EXAMPLES)) <
            0) {
            goto error;
        }
    }

    if (schema_json_by_schemas(compiller, meta->schemas, properties, required) <
        0) {
        goto error;
    }

    if (!PyList_GET_SIZE(required)) {
        if (PyDict_DelItem(dict, __required) < 0) {
            goto error;
        }
    }
    return dict;

error:
    Py_DECREF(dict);
    return NULL;
}

static PyObject*
schema_json_enum(Compiller* compiller, PyObject* obj, PyObject* title)
{
    ContextManager* ctx = compiller->ctx;
    compiller->ctx = NULL;
    PyObject* res =
      schema_json_object(compiller, obj, title, schema_json_enum_nested);
    compiller->ctx = ctx;
    return res;
}

static PyObject*
schema_json_validated_func(Compiller* compiller, PyObject* obj, PyObject* title)
{
    ContextManager* ctx = compiller->ctx;
    compiller->ctx = NULL;
    PyObject* res = schema_json_object(
      compiller, obj, title, (ObjectParser)schema_json_validated_func_nested);
    compiller->ctx = ctx;
    return res;
}

static PyObject*
schema_json_typed_dict(Compiller* compiller, PyObject* obj, PyObject* title)
{
    ContextManager* ctx = compiller->ctx;
    compiller->ctx = NULL;
    PyObject* res =
      schema_json_object(compiller, obj, title, schema_json_typed_dict_nested);
    compiller->ctx = ctx;
    return res;
}

static PyObject*
schema_json_meta_mode(Compiller* compiller, PyObject* obj, PyObject* title)
{
    ContextManager* ctx = compiller->ctx;
    compiller->ctx = NULL;
    PyObject* res = schema_json_object(
      compiller, obj, title, (ObjectParser)schema_json_meta_mode_nested);
    compiller->ctx = ctx;
    return res;
}

static PyObject*
schema_json_context_manager_nested(Compiller* compiller,
                                   ContextManager* ctx,
                                   PyObject* title)
{
    if (ValidatedFunc_Check(ctx->model)) {
        return schema_json_validated_func_nested(
          compiller, (ValidatedFunc*)ctx->model, title);
    }
    return schema_json_meta_mode_nested(
      compiller, (MetaModel*)ctx->model, title);
}

static PyObject*
schema_json_context_manager(Compiller* compiller,
                            ContextManager* ctx,
                            PyObject* title)
{
    ContextManager* old_ctx = compiller->ctx;
    if (old_ctx) {
        ctx = _ContextManager_CreateByOld(ctx, old_ctx);
        if (!ctx) {
            return NULL;
        }
    }

    compiller->ctx = ctx;
    PyObject* res =
      schema_json_object(compiller,
                         (PyObject*)ctx,
                         title,
                         (ObjectParser)schema_json_context_manager_nested);
    compiller->ctx = old_ctx;
    if (old_ctx) {
        Py_DECREF(ctx);
    }
    return res;
}

static PyObject*
schema_json_bytes(PyObject* title)
{
    PyObject* dict = schema_json_base(__string, title);
    if (dict) {
        if (_PyDict_SetItem_Ascii(dict, __format, __binary) < 0) {
            Py_DECREF(dict);
            return NULL;
        }
    }
    return dict;
}

static PyObject*
_schema_json(Compiller* compiller, PyObject* hint, PyObject* title)
{
    if (hint == (PyObject*)&PyBaseObject_Type || hint == PyAny ||
        hint == Py_Ellipsis) {
        return PyDict_New();
    }

    if (PyType_Check(hint)) {
        PyTypeObject* tp = (PyTypeObject*)hint;
        if (_CAST(PyTypeObject*, hint) == PyNone_Type) {
            return schema_json_base(___null, title);
        } else if (PyType_IsSubtype(tp, (PyTypeObject*)PyEnumType)) {
            return schema_json_enum(compiller, hint, title);
        } else if (DateTime_Is_DateType((PyTypeObject*)hint)) {
            return schema_json_base(__date, title);
        } else if (DateTime_Is_TimeType((PyTypeObject*)hint)) {
            return schema_json_base(__time, title);
        } else if (DateTime_Is_DateTimeType((PyTypeObject*)hint)) {
            return schema_json_base(__date_time, title);
        } else if (PyTyping_Is_TypedDict(hint)) {
            return schema_json_typed_dict(compiller, hint, title);
        } else if (PyType_FastSubclass((PyTypeObject*)hint,
                                       Py_TPFLAGS_DICT_SUBCLASS)) {
            return schema_json_base(__object, title);
        } else if (PyType_IsSubtype(tp, &PyBool_Type)) {
            return schema_json_base(__boolean, title);
        } else if (PyType_IsSubtype(tp, &PyLong_Type)) {
            return schema_json_base(__integer, title);
        } else if (PyType_IsSubtype(tp, &PyFloat_Type)) {
            return schema_json_base(__number, title);
        } else if (PyType_FastSubclass((PyTypeObject*)hint,
                                       Py_TPFLAGS_UNICODE_SUBCLASS)) {
            return schema_json_base(__string, title);
        } else if (PyType_IsSubtype(tp, &PyList_Type) ||
                   PyType_IsSubtype(tp, &PyTuple_Type)) {
            PyObject* items;
            return schema_json_base_sequence(&items, title);
        } else if (PyType_IsSubtype(tp, &PySet_Type) ||
                   PyType_IsSubtype(tp, &PyFrozenSet_Type)) {
            PyObject *dict, *items;
            dict = schema_json_base_sequence(&items, title);
            if (dict == NULL) {
                return NULL;
            }
            if (_PyDict_SetItem_Ascii(dict, __uniqueItems, Py_True) < 0) {
                Py_DECREF(dict);
                return NULL;
            }
            return dict;
        } else if (PyType_IsSubtype(tp, &PyBytes_Type) ||
                   PyType_IsSubtype(tp, &PyByteArray_Type)) {
            return schema_json_bytes(title);
        } else if (Meta_IS_SUBCLASS(hint)) {
            return schema_json_meta_mode(compiller, hint, title);
        } else if (PyType_IsSubtype(tp, PyUuidType)) {
            return schema_json_uuid(title);
        }
    } else if (PyUnicode_Check(hint)) {
        return schema_json_unicode(compiller, hint, title);
    } else if (ValidatedFunc_Check(hint)) {
        return schema_json_validated_func(compiller, hint, title);
    } else if (ContextManager_Check(hint)) {
        return schema_json_context_manager(
          compiller, (ContextManager*)hint, title);
    } else if (Py_IS_TYPE(hint, (PyTypeObject*)Py_AnnotatedAlias)) {
        return schema_json_annotated(compiller, hint, title);
    } else if (Py_IS_TYPE(hint, (PyTypeObject*)PyTypeVar)) {
        return schema_json_type_var(compiller, hint, title);
    } else if (Py_IS_TYPE(hint, (PyTypeObject*)PyForwardRef)) {
        return schema_json_forward_ref(compiller, hint, title);
    } else {
        PyObject* origin = PyTyping_Get_Origin(hint);
        if (origin) {
            if (origin == PyUnion) {
                Py_DECREF(origin);
                return schema_json_union(compiller, hint, title);
            } else if (origin == PyLiteral) {
                Py_DECREF(origin);
                return schema_json_literal(hint);
            } else if (origin == PyRequired || origin == PyNotRequired) {
                Py_DECREF(origin);
                return schema_json_required(compiller, hint, title);
            } else if (Py_IS_TYPE(hint, (PyTypeObject*)PyGenericAlias) ||
                       Py_IS_TYPE(hint, (PyTypeObject*)_GenericAlias)) {
                PyObject* res =
                  schema_json_sequence(compiller, hint, title, origin);
                Py_DECREF(origin);
                return res;
            }
            Py_DECREF(origin);
        }
    }
    return PyErr_Format(
      PyExc_ValueError, "It is impossible to recognize '%R'", hint);
}

static PyObject*
schema_json(Compiller* compiller, PyObject* hint, PyObject* title)
{
    if (compiller_enter(compiller) < 0) {
        return NULL;
    }
    PyObject* res = _schema_json(compiller, hint, title);
    compiller_leave(compiller);
    return res;
}

#endif

PyObject*
Schema_JsonSchema(UNUSED PyObject* hint)
{
#if _USED_JSON_SCHEMA
    Compiller compiller = {
        .defs = NULL, .use_defs = 0, .ctx = NULL, .nesting_level = 0
    };

    PyObject* dict = schema_json(&compiller, hint, NULL);
    if (!dict || !compiller.use_defs || !compiller.defs) {
        return dict;
    }

    if (_PyDict_SetItemAsciiDecrefVal(dict, ___defs, compiller.defs) < 0) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
#else
    PyErr_SetString(PyExc_NotImplementedError,
                    "This version is compiled without JSON Schema support");
    return NULL;
#endif
}

int
json_schema_setup(void)
{
#if _USED_JSON_SCHEMA
    CREATE_VAR_INTERN___STING(type);
    CREATE_VAR_INTERN___STING(object);
    CREATE_VAR_INTERN___STING(ge);
    CREATE_VAR_INTERN___STING(gt);
    CREATE_VAR_INTERN___STING(le);
    CREATE_VAR_INTERN___STING(lt);
    CREATE_VAR_INTERN___STING(enum);
    CREATE_VAR_INTERN___STING(number);
    // CREATE_VAR_INTERN___STING(null);
    CREATE_VAR_INTERN___STING(uuid);
    CREATE_VAR_INTERN___STING(date)
    CREATE_VAR_INTERN___STING(time)
    CREATE_VAR_INTERN___STING(allOf)
    CREATE_VAR_INTERN___STING(items)
    CREATE_VAR_INTERN___STING(array)
    CREATE_VAR_INTERN___STING(title)
    CREATE_VAR_INTERN___STING(anyOf)
    CREATE_VAR_INTERN___STING(string)
    CREATE_VAR_INTERN___STING(format)
    CREATE_VAR_INTERN___STING(binary)
    CREATE_VAR_INTERN___STING(default)
    CREATE_VAR_INTERN___STING(integer)
    CREATE_VAR_INTERN___STING(boolean)
    CREATE_VAR_INTERN___STING(pattern)
    CREATE_VAR_INTERN___STING(required)
    CREATE_VAR_INTERN___STING(examples)
    CREATE_VAR_INTERN___STING(readOnly)
    CREATE_VAR_INTERN___STING(minLength)
    CREATE_VAR_INTERN___STING(maxLength)
    CREATE_VAR_INTERN___STING(properties)
    CREATE_VAR_INTERN___STING(uniqueItems)
    CREATE_VAR_INTERN___STING(additionalProperties)

    ___null = PyUnicode_InternFromString("null");
    if (___null == NULL) {
        return -1;
    }

    ___ref = PyUnicode_InternFromString("$ref");
    if (___ref == NULL) {
        return -1;
    }

    ___defs = PyUnicode_InternFromString("$defs");
    if (___defs == NULL) {
        return -1;
    }

    __date_time = PyUnicode_InternFromString("date-time");
    if (__date_time == NULL) {
        return -1;
    }
#endif
    return 0;
}

void
json_schema_free(void)
{
#if _USED_JSON_SCHEMA
    Py_DECREF(__ge);
    Py_DECREF(__gt);
    Py_DECREF(__le);
    Py_DECREF(__lt);
    Py_DECREF(__uuid);
    Py_DECREF(___ref);
    Py_DECREF(__enum);
    Py_DECREF(__type);
    Py_DECREF(__date);
    Py_DECREF(__time);
    Py_DECREF(__allOf);
    Py_DECREF(___defs);
    Py_DECREF(__title);
    Py_DECREF(__items);
    Py_DECREF(___null);
    Py_DECREF(__array);
    Py_DECREF(__anyOf);
    Py_DECREF(__format);
    Py_DECREF(__binary);
    Py_DECREF(__object);
    Py_DECREF(__number);
    Py_DECREF(__string);
    Py_DECREF(__integer);
    Py_DECREF(__boolean);
    Py_DECREF(__default);
    Py_DECREF(__pattern);
    Py_DECREF(__readOnly);
    Py_DECREF(__examples);
    Py_DECREF(__date_time);
    Py_DECREF(__required);
    Py_DECREF(__minLength);
    Py_DECREF(__maxLength);
    Py_DECREF(__properties);
    Py_DECREF(__uniqueItems);
    Py_DECREF(__additionalProperties);
#endif
}