#include "module.h"
#include "alias_generator.h"
#include "computed_field.h"
#include "convector.h"
#include "data_model.h"
#include "diff.h"
#include "field.h"
#include "field_serializer.h"
#include "hash_table.h"
#include "json_schema.h"
#include "member_def.h"
#include "meta_valid_model.h"
#include "valid_model.h"
#include "validated_func.h"
#include "validator/discriminator.h"
#include "validator/validator.h"
#include "vector_dict.h"
#include "weakref_cache.h"
#include "json/json.h"

#define PYMODULE_ADD_TYPE(m, tp)                                               \
    if (PyModule_AddType(m, (PyTypeObject*)tp) < 0) {                          \
        return NULL;                                                           \
    }

static PyObject*
copy(UNUSED PyObject* self, PyObject* obj)
{
    return PyCopy(obj);
}

static PyObject*
dumps(UNUSED PyObject* self,
      PyObject* const* args,
      Py_ssize_t nargsf,
      PyObject* kwnames)
{
    return PyObject_AsJson(args, nargsf, kwnames, 0);
}

static PyObject*
dump(UNUSED PyObject* self,
     PyObject* const* args,
     Py_ssize_t nargsf,
     PyObject* kwnames)
{
    return PyObject_AsJson(args, nargsf, kwnames, 1);
}

static PyObject*
loads(UNUSED PyObject* self, PyObject* obj)
{
    return JsonParse(obj);
}

static PyObject*
load(UNUSED PyObject* self, PyObject* fp)
{
    PyObject* obj = PyObject_CallMethodNoArgs(fp, __read);
    if (FT_UNLIKELY(!obj)) {
        return NULL;
    }

    PyObject* res = JsonParse(obj);
    Py_DECREF(obj);
    return res;
}

static PyObject*
as_dict(UNUSED PyObject* self,
        PyObject* const* args,
        Py_ssize_t nargsf,
        PyObject* kwnames)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    if (FT_UNLIKELY(!PyCheck_ArgsCnt("as_dict", nargs, 1))) {
        return NULL;
    }

    PyObject *res = NULL, *obj = (PyObject*)*args;
    ConvParams params = ConvParams_Create(__as_dict__);
    if (!kwnames) {
        goto done;
    }

    PyObject* argsbuf[6] = { NULL };
    static const char* const kwlist[] = {
        "as_json", "by_alias", "exclude_unset", "exclude_none", "use_custom",
        "context", NULL,
    };

    static _PyArg_Parser _parser = {
        .keywords = kwlist,
        .fname = "as_dict",
        .kwtuple = NULL,
    };

    args++;
    nargs--;
    if (!PyArg_UnpackKeywords(args,
                              nargs,
                              NULL,
                              kwnames,
                              &_parser,
                              0, /*minpos*/
                              0, /*maxpos*/
                              0, /*minkw*/
                              argsbuf)) {
        return NULL;
    }
    for (Py_ssize_t i = 0; i != 5; i++) {
        if (!_ValidateArg(argsbuf[i], &PyBool_Type, kwlist[i])) {
            return NULL;
        }
    }

    if (argsbuf[0] == Py_True) {
        params.attr = __as_json__;
    }
    params.by_alias = argsbuf[1] != Py_False;
    params.exclude_unset = argsbuf[2] == Py_True;
    params.exclude_none = argsbuf[3] == Py_True;
    params.custom_ser = argsbuf[4] != Py_False;
    params.context = argsbuf[5];

done:
    res = _Convector_Obj(obj, &params);
    _ConvParams_Free(&params);
    return res;
}

static PyObject*
parse_date(UNUSED PyObject* self, PyObject* obj)
{
    return DateTime_ParseDate(obj);
}

static PyObject*
parse_time(UNUSED PyObject* self, PyObject* obj)
{
    return DateTime_ParseTime(obj);
}

static PyObject*
parse_datetime(UNUSED PyObject* self, PyObject* obj)
{
    return DateTime_ParseDateTime(obj);
}

static PyObject*
parse_timedelta(UNUSED PyObject* self, PyObject* obj)
{
    return DateTime_ParseTimeDelta(obj);
}

static PyObject*
json_schema(UNUSED PyObject* self, PyObject* obj)
{
    return Schema_JsonSchema(obj);
}

static PyObject*
field(UNUSED PyObject* self,
      PyObject* const* args,
      Py_ssize_t nargsf,
      PyObject* kwnames)
{
    if (!PyCheck_ArgsCnt("field", PyVectorcall_NARGS(nargsf), 1)) {
        return NULL;
    }

    PyObject* type = (PyObject*)*args;
    PyObject* field =
      PyObject_Vectorcall((PyObject*)&FieldType, args + 1, 0, kwnames);
    if (FT_UNLIKELY(!field)) {
        return NULL;
    }

    PyObject* res = PyTyping_AnnotatedGetItem(type, field);
    Py_DECREF(field);
    return res;
}

static PyObject*
create_con(PyTypeObject* type_con,
           PyObject* const* args,
           Py_ssize_t nargsf,
           PyObject* kwnames,
           const char* func_name)
{
    if (!PyCheck_ArgsCnt(func_name, PyVectorcall_NARGS(nargsf), 1)) {
        return NULL;
    }

    PyObject* type = (PyObject*)*args;
    PyObject* con =
      PyObject_Vectorcall((PyObject*)type_con, args + 1, 0, kwnames);
    if (FT_UNLIKELY(!con)) {
        return NULL;
    }

    PyObject* res = PyTyping_AnnotatedGetItem(type, con);
    Py_DECREF(con);
    return res;
}

static PyObject*
con_sequence(UNUSED PyObject* self,
             PyObject* const* args,
             Py_ssize_t nargsf,
             PyObject* kwnames)
{
    return create_con(
      &SequenceConstraintsType, args, nargsf, kwnames, "con_sequence");
}

static PyObject*
con_string(UNUSED PyObject* self,
           PyObject* const* args,
           Py_ssize_t nargsf,
           PyObject* kwnames)
{
    return create_con(
      &StringConstraintsType, args, nargsf, kwnames, "con_string");
}

static PyObject*
con_comparison(UNUSED PyObject* self,
               PyObject* const* args,
               Py_ssize_t nargsf,
               PyObject* kwnames)
{
    return create_con(
      &ComparisonConstraintsType, args, nargsf, kwnames, "con_comparison");
}

static PyMethodDef frost_typing_methods[] = {
    { "copy", PY_METHOD_CAST(copy), METH_O, NULL },
    { "dump", PY_METHOD_CAST(dump), METH_FASTCALL | METH_KEYWORDS, NULL },
    { "load", PY_METHOD_CAST(load), METH_O, NULL },
    { "dumps", PY_METHOD_CAST(dumps), METH_FASTCALL | METH_KEYWORDS, NULL },
    { "loads", PY_METHOD_CAST(loads), METH_O, NULL },
    { "as_dict", PY_METHOD_CAST(as_dict), METH_FASTCALL | METH_KEYWORDS, NULL },
    { "parse_date", PY_METHOD_CAST(parse_date), METH_O, NULL },
    { "parse_time", PY_METHOD_CAST(parse_time), METH_O, NULL },
    { "json_schema", PY_METHOD_CAST(json_schema), METH_O, NULL },
    { "parse_datetime", PY_METHOD_CAST(parse_datetime), METH_O, NULL },
    { "parse_timedelta", PY_METHOD_CAST(parse_timedelta), METH_O, NULL },
    { "field", PY_METHOD_CAST(field), METH_FASTCALL | METH_KEYWORDS, NULL },
    { "con_sequence",
      PY_METHOD_CAST(con_sequence),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "con_string",
      PY_METHOD_CAST(con_string),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { "con_comparison",
      PY_METHOD_CAST(con_comparison),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { NULL },
};

static void
frost_typing_free(UNUSED void* self)
{
    discriminator_free();
    computed_field_free();
    schema_free();
    json_free();
    field_validator_free();
    field_serializer_free();
    typing_free();
    validation_error_free();
    field_free();
    utils_common_free();
    meta_model_free();
    data_model_free();
    validator_free();
    validated_func_free();
    constraints_free();
    meta_valid_model_free();
    valid_model_free();
    convector_free();
    context_free();
    weakref_cache_free();
    alias_generator_free();
    json_schema_free();
    vector_dict_free();
    hash_table_free();
    member_def_free();
}

static int
frost_typing_setup(void)
{
    if (discriminator_setup() < 0 || utils_common_setup() < 0 ||
        weakref_cache_setup() < 0 || context_setup() < 0 ||
        field_validator_setup() < 0 || field_serializer_setup() < 0 ||
        typing_setup() < 0 || validation_error_setup() < 0 ||
        field_setup() < 0 || schema_setup() < 0 || meta_model_setup() < 0 ||
        data_model_setup() < 0 || validator_setup() < 0 ||
        validated_func_setup() < 0 || constraints_setup() < 0 ||
        meta_valid_model_setup() < 0 || valid_model_setup() < 0 ||
        convector_setup() < 0 || json_setup() < 0 ||
        computed_field_setup() < 0 || alias_generator_setup() < 0 ||
        json_schema_setup() || vector_dict_setup() < 0 ||
        hash_table_setup() < 0 || member_def_setup() < 0) {
        return -1;
    }
    return 0;
}

static PyModuleDef frost_typing = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_methods = frost_typing_methods,
    .m_free = frost_typing_free,
    .m_name = "frost_typing",
    .m_doc = NULL,
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_frost_typing(void)
{
    PyObject* m;
    if (frost_typing_setup() < 0) {
        return NULL;
    }
    m = PyModule_Create(&frost_typing);
    if (m == NULL) {
        return NULL;
    }
    PYMODULE_ADD_TYPE(m, &MetaModelType);
    PYMODULE_ADD_TYPE(m, &MetaValidModelType);
    PYMODULE_ADD_TYPE(m, &DataModelType);
    PYMODULE_ADD_TYPE(m, &FieldType);
    PYMODULE_ADD_TYPE(m, &ConfigType);
    PYMODULE_ADD_TYPE(m, &ValidModelType);
    PYMODULE_ADD_TYPE(m, ValidationErrorType);
    PYMODULE_ADD_TYPE(m, JsonEncodeError);
    PYMODULE_ADD_TYPE(m, JsonDecodeError);
    PYMODULE_ADD_TYPE(m, FrostUserError);
    PYMODULE_ADD_TYPE(m, &ComparisonConstraintsType);
    PYMODULE_ADD_TYPE(m, &SequenceConstraintsType);
    PYMODULE_ADD_TYPE(m, &SerializationInfo_Type);
    PYMODULE_ADD_TYPE(m, &StringConstraintsType);
    PYMODULE_ADD_TYPE(m, &ValidatedFuncType);
    PYMODULE_ADD_TYPE(m, &TypeAdapterType);
    PYMODULE_ADD_TYPE(m, &FieldValidatorType);
    PYMODULE_ADD_TYPE(m, &FieldSerializerType);
    PYMODULE_ADD_TYPE(m, &ComputedFieldType);
    PYMODULE_ADD_TYPE(m, &ContextManager_Type);
    PYMODULE_ADD_TYPE(m, &AliasGeneratorType);
    PYMODULE_ADD_TYPE(m, &DiscriminatorType);
    PYMODULE_ADD_TYPE(m, &ValidSchemaType);
    PYMODULE_ADD_TYPE(m, &ArgsKwargsType);
    PYMODULE_ADD_TYPE(m, &SchemaType);

    if (PyModule_AddObject(m, "AwareDatetime", AwareDatetime) < 0) {
        return NULL;
    }
    if (PyModule_AddObject(m, "NaiveDatetime", NaiveDatetime) < 0) {
        return NULL;
    }
    if (PyModule_AddObject(m, "PastDatetime", PastDatetime) < 0) {
        return NULL;
    }
    if (PyModule_AddObject(m, "FutureDatetime", FutureDatetime) < 0) {
        return NULL;
    }

#if _USED_JSON_SCHEMA
    PyObject* has_json_schema = Py_True;
#else
    PyObject* has_json_schema = Py_False;
#endif

#if PY310_PLUS
    if (PyModule_AddObjectRef(m, "HAS_JSON_SCHEMA", has_json_schema) < 0) {
        return NULL;
    }
#else
    if (PyModule_AddObject(m, "HAS_JSON_SCHEMA", Py_NewRef(has_json_schema)) <
        0) {
        return NULL;
    }
#endif

    return m;
}