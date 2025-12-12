#include "field.h"
#include "alias_generator.h"
#include "convector.h"
#include "stddef.h"
#include "stdint.h"
#include "utils_common.h"

#if defined(_MSC_VER)
#include <intrin.h>
#endif

#define _UNICODE_WRITE_ATTR(w, ch, f, s)                                       \
    if (ch(f->flags)) {                                                        \
        _UNICODE_WRITE_STRING(w, s "=True, ", _STRLEN(s) + 6);                 \
    } else {                                                                   \
        _UNICODE_WRITE_STRING(w, s "=False, ", _STRLEN(s) + 7);                \
    }
#define _UNICODE_WRITE_REPR_ATTR(o, w, f, s)                                   \
    if (field_repr_attr(o, w, f, s, _STRLEN(s)) < 0) {                         \
        goto error;                                                            \
    }

#define _GET_FLAG_BY_VALUE(v, f) (v == NULL || v == Py_True ? f : 0)
#define _GET_EXACT_FLAG_BY_VALUE(v, f) (v == Py_True ? f : 0)
#define _GET_DEF_FLAG_BY_VALUE(v, f) (v ? f : 0)

Field *DefaultField, *DefaultFieldPrivate, *DefaultFieldVFunc,
  *DefaultFieldVFuncNoInit, *DefaultFieldVFuncKwOnly,
  *DefaultFieldVFuncNoInitKwOnly, *VoidField, *DefaultConfig,
  *DefaultConfigValid;

static Field*
field_inheritance(Field* self,
                  Field* old,
                  int use_parent_attrs,
                  PyObject* serializer,
                  PyObject* ser_alias,
                  PyObject* alias);

static inline uint16_t
bit_cnt(uint32_t bits)
{
#if defined(__GNUC__) || defined(__clang__)
    return (uint16_t)__builtin_popcount(bits);
#elif defined(_MSC_VER)
    return (uint16_t)__popcnt(bits);
#else
    uint16_t cnt = 0;
    while (bits) {
        cnt++;
        bits &= (bits - 1);
    }
    return cnt;
#endif
}

static inline uint16_t
get_size_by_flags(uint32_t flags)
{
    return bit_cnt(flags & FIELD_VALUES);
}

inline uint16_t
_Field_Size(Field* self)
{
    return get_size_by_flags(self->flags);
}

static int
field_attr_pos_by_flag(uint32_t flags, uint32_t attr_flag)
{
    return (flags & attr_flag) ? bit_cnt(flags & (attr_flag - 1)) : -1;
}

inline PyObject*
_Field_GetAttr(Field* self, uint32_t flag)
{
    int pos = field_attr_pos_by_flag(self->flags, flag);
    return pos == -1 ? NULL : self->ob_item[pos];
}

static inline int
field_set_attr(Field* self, uint32_t flag, PyObject* val)
{
    if (val == NULL) {
        return -1;
    }

    int pos = field_attr_pos_by_flag(self->flags, flag);
    if (pos == -1) {
        return -1;
    }

    Py_XDECREF(self->ob_item[pos]);
    self->ob_item[pos] = Py_NewRef(val);
    return 0;
}

static void
config_dealloc(Field* self)
{
    int i = FIELD_SIZE(self);
    while (--i > -1) {
        Py_XDECREF(self->ob_item[i]);
    }
    Py_TYPE(self)->tp_free(self);
}

static Field*
field_create(PyTypeObject* tp, uint32_t flags, uint32_t def_flags)
{
    if (tp == &FieldType) {
        flags &= FIELD_FIELD;
        def_flags &= FIELD_FIELD;
    } else if (tp == &ConfigType) {
        flags &= FIELD_CONFIG;
        def_flags &= FIELD_CONFIG;
    }

    if (tp == &ConfigType) {
        if (DefaultConfig && DefaultConfig->flags == flags &&
            DefaultConfig->def_flags == def_flags) {
            Py_INCREF(DefaultConfig);
            return DefaultConfig;
        } else if (DefaultConfigValid && DefaultConfigValid->flags == flags &&
                   DefaultConfigValid->def_flags == def_flags) {
            Py_INCREF(DefaultConfigValid);
            return DefaultConfigValid;
        }
    } else if (tp == &FieldType && DefaultField &&
               DefaultField->flags == flags &&
               DefaultField->def_flags == def_flags) {
        Py_INCREF(DefaultField);
        return DefaultField;
    }

    Field* field = Object_NewVar(Field, tp, get_size_by_flags(flags));
    if (field) {
        field->flags = flags;
        field->def_flags = def_flags;
    }
    return field;
}

static PyObject*
config_new(PyTypeObject* cls, PyObject* args, PyObject* kwargs)
{
    PyObject *init, *repr, *hash, *dict, *json, *kw_only, *comparison, *frozen,
      *frozen_type, *class_lookup, *strict, *fail_on_extra_init,
      *validate_private, *auto_alias, *gc, *alias_generator, *allow_inf_nan,
      *num_to_str, *title, *examples;
    init = repr = hash = dict = json = comparison = class_lookup = frozen =
      kw_only = strict = frozen_type = fail_on_extra_init = validate_private =
        auto_alias = gc = alias_generator = allow_inf_nan = num_to_str = title =
          examples = NULL;

    char* kwlist[] = { "init",
                       "repr",
                       "hash",
                       "dict",
                       "json",
                       "strict",
                       "kw_only",
                       "frozen",
                       "comparison",
                       "class_lookup",
                       "frozen_type",
                       "fail_on_extra_init",
                       "validate_private",
                       "auto_alias",
                       "allow_inf_nan",
                       "num_to_str",
                       "gc",
                       "alias_generator",
                       "title",
                       "examples",
                       NULL };
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "|O!O!O!O!O!O!O!O!O!O!"
                                     "O!O!O!O!O!O!O!OUO!:Config.__new__",
                                     kwlist,
                                     &PyBool_Type,
                                     &init,
                                     &PyBool_Type,
                                     &repr,
                                     &PyBool_Type,
                                     &hash,
                                     &PyBool_Type,
                                     &dict,
                                     &PyBool_Type,
                                     &json,
                                     &PyBool_Type,
                                     &strict,
                                     &PyBool_Type,
                                     &kw_only,
                                     &PyBool_Type,
                                     &frozen,
                                     &PyBool_Type,
                                     &comparison,
                                     &PyBool_Type,
                                     &class_lookup,
                                     &PyBool_Type,
                                     &frozen_type,
                                     &PyBool_Type,
                                     &fail_on_extra_init,
                                     &PyBool_Type,
                                     &validate_private,
                                     &PyBool_Type,
                                     &auto_alias,
                                     &PyBool_Type,
                                     &allow_inf_nan,
                                     &PyBool_Type,
                                     &num_to_str,
                                     &PyBool_Type,
                                     &gc,
                                     &alias_generator,
                                     &title,
                                     &PyList_Type,
                                     &examples)) {
        return NULL;
    }

    uint32_t flags = 0;
    uint32_t def_flags = 0;

    if (title) {
        flags |= FIELD_TITLE;
        def_flags |= FIELD_TITLE;
    }
    if (examples) {
        flags |= FIELD_EXAMPLES;
        def_flags |= FIELD_EXAMPLES;
    }
    if (alias_generator) {
        if (!AliasGenerator_Check(alias_generator) &&
            !PyCallable_Check(alias_generator)) {
            return _RaiseInvalidType("alias_generator",
                                     "callable or AliasGenerator",
                                     Py_TYPE(alias_generator)->tp_name);
        }
        flags |= FIELD_ALIAS_GENERATOR;
        def_flags |= FIELD_ALIAS_GENERATOR;
    }

    flags |= _GET_FLAG_BY_VALUE(init, FIELD_INIT);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(init, FIELD_INIT);

    flags |= _GET_FLAG_BY_VALUE(repr, FIELD_REPR);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(repr, FIELD_REPR);

    flags |= _GET_EXACT_FLAG_BY_VALUE(hash, FIELD_HASH);
    def_flags |= _GET_EXACT_FLAG_BY_VALUE(hash, FIELD_HASH);

    flags |= _GET_FLAG_BY_VALUE(dict, FIELD_DICT);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(dict, FIELD_DICT);

    flags |= _GET_FLAG_BY_VALUE(json, FIELD_JSON);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(json, FIELD_JSON);

    flags |= _GET_EXACT_FLAG_BY_VALUE(strict, FIELD_STRICT);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(strict, FIELD_STRICT);

    flags |= _GET_FLAG_BY_VALUE(comparison, FIELD_COMPARISON);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(comparison, FIELD_COMPARISON);

    flags |= _GET_EXACT_FLAG_BY_VALUE(kw_only, FIELD_KW_ONLY);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(kw_only, FIELD_KW_ONLY);

    flags |= _GET_EXACT_FLAG_BY_VALUE(frozen, FIELD_FROZEN);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(frozen, FIELD_FROZEN);

    flags |= _GET_EXACT_FLAG_BY_VALUE(frozen_type, FIELD_FROZEN_TYPE);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(frozen_type, FIELD_FROZEN_TYPE);

    flags |= _GET_FLAG_BY_VALUE(class_lookup, FIELD_CLASS_LOOKUP);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(class_lookup, FIELD_CLASS_LOOKUP);

    flags |= _GET_EXACT_FLAG_BY_VALUE(fail_on_extra_init, FAIL_ON_EXTRA_INIT);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(fail_on_extra_init, FAIL_ON_EXTRA_INIT);

    flags |= _GET_FLAG_BY_VALUE(validate_private, FIELD_VALIDATE_PRIVATE);
    def_flags |=
      _GET_DEF_FLAG_BY_VALUE(validate_private, FIELD_VALIDATE_PRIVATE);

    flags |= _GET_FLAG_BY_VALUE(auto_alias, FIELD_AUTO_ALIAS);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(auto_alias, FIELD_AUTO_ALIAS);

    flags |= _GET_FLAG_BY_VALUE(allow_inf_nan, FIELD_ALLOW_INF_NAN);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(allow_inf_nan, FIELD_ALLOW_INF_NAN);

    flags |= _GET_FLAG_BY_VALUE(gc, _FIELD_GC);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(gc, _FIELD_GC);

    flags |= _GET_EXACT_FLAG_BY_VALUE(num_to_str, FIELD_NUM_TO_STR);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(num_to_str, FIELD_NUM_TO_STR);

    Field* self = field_create(cls, flags, def_flags);
    if (self) {
        field_set_attr(self, FIELD_TITLE, title);
        field_set_attr(self, FIELD_EXAMPLES, examples);
        field_set_attr(self, FIELD_ALIAS_GENERATOR, alias_generator);
    }
    return (PyObject*)self;
}

static PyObject*
field_new(PyTypeObject* cls, PyObject* args, PyObject* kwargs)
{
    PyObject *default_value, *init, *repr, *hash, *dict, *json, *kw_only,
      *comparison, *frozen, *frozen_type, *class_lookup, *alias, *title,
      *examples, *serialization_alias, *default_factory, *json_schema_extra,
      *auto_alias, *diff_key, *description;
    default_value = default_factory = alias = title = examples = NULL;
    init = repr = hash = dict = json = comparison = class_lookup = NULL;
    serialization_alias = frozen = kw_only = frozen_type = json_schema_extra =
      auto_alias = diff_key = description = NULL;

    char* kwlist[] = { "default",
                       "init",
                       "repr",
                       "hash",
                       "dict",
                       "json",
                       "kw_only",
                       "frozen",
                       "comparison",
                       "class_lookup",
                       "frozen_type",
                       "auto_alias",
                       "alias",
                       "title",
                       "examples",
                       "serialization_alias",
                       "default_factory",
                       "json_schema_extra",
                       "diff_key",
                       "description",
                       NULL };

    if (!PyArg_ParseTupleAndKeywords(
          args,
          kwargs,
          "|OO!O!O!O!O!O!O!O!O!O!O!UUO!UOO!UU:Field.__new__",
          kwlist,
          &default_value,
          &PyBool_Type,
          &init,
          &PyBool_Type,
          &repr,
          &PyBool_Type,
          &hash,
          &PyBool_Type,
          &dict,
          &PyBool_Type,
          &json,
          &PyBool_Type,
          &kw_only,
          &PyBool_Type,
          &frozen,
          &PyBool_Type,
          &comparison,
          &PyBool_Type,
          &class_lookup,
          &PyBool_Type,
          &frozen_type,
          &PyBool_Type,
          &auto_alias,
          &alias,
          &title,
          &PyList_Type,
          &examples,
          &serialization_alias,
          &default_factory,
          &PyDict_Type,
          &json_schema_extra,
          &diff_key,
          &description)) {
        return NULL;
    }

    uint32_t flags = 0;
    uint32_t def_flags = 0;

    if (default_value) {
        flags |= FIELD_DEFAULT;
        def_flags |= FIELD_DEFAULT;
        if (Convector_IsConstVal(default_value)) {
            flags |= _FIELD_CONST_DEFAULT;
            def_flags |= _FIELD_CONST_DEFAULT;
        }
    }
    if (alias) {
        if (!CheckValidityOfAttribute(alias)) {
            return NULL;
        }
        flags |= FIELD_ALIAS;
        def_flags |= FIELD_ALIAS;
    }
    if (title) {
        flags |= FIELD_TITLE;
        def_flags |= FIELD_TITLE;
    }
    if (examples) {
        flags |= FIELD_EXAMPLES;
        def_flags |= FIELD_EXAMPLES;
    }
    if (serialization_alias) {
        flags |= FIELD_SERIALIZATION_ALIAS;
        def_flags |= FIELD_SERIALIZATION_ALIAS;
    }
    if (default_factory) {
        flags |= FIELD_DEFAULT_FACTORY;
        def_flags |= FIELD_DEFAULT_FACTORY;
        if (!PyCallable_Check(default_factory)) {
            return _RaiseInvalidType(
              "default_factory", "callable", Py_TYPE(default_factory)->tp_name);
        }
    }
    if (json_schema_extra) {
        flags |= FIELD_JSON_SCHEMA_EXTRA;
        def_flags |= FIELD_JSON_SCHEMA_EXTRA;
    }

    if (diff_key) {
        flags |= FIELD_DIFF_KEY;
        def_flags |= FIELD_DIFF_KEY;
    }

    if (description) {
        flags |= FIELD_DESCRIPTION;
        def_flags |= FIELD_DESCRIPTION;
    }

    flags |= _GET_FLAG_BY_VALUE(init, FIELD_INIT);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(init, FIELD_INIT);

    flags |= _GET_FLAG_BY_VALUE(repr, FIELD_REPR);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(repr, FIELD_REPR);

    flags |= _GET_EXACT_FLAG_BY_VALUE(hash, FIELD_HASH);
    def_flags |= _GET_EXACT_FLAG_BY_VALUE(hash, FIELD_HASH);

    flags |= _GET_FLAG_BY_VALUE(dict, FIELD_DICT);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(dict, FIELD_DICT);

    flags |= _GET_FLAG_BY_VALUE(json, FIELD_JSON);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(json, FIELD_JSON);

    flags |= _GET_FLAG_BY_VALUE(comparison, FIELD_COMPARISON);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(comparison, FIELD_COMPARISON);

    flags |= _GET_EXACT_FLAG_BY_VALUE(kw_only, FIELD_KW_ONLY);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(kw_only, FIELD_KW_ONLY);

    flags |= _GET_EXACT_FLAG_BY_VALUE(frozen, FIELD_FROZEN);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(frozen, FIELD_FROZEN);

    flags |= _GET_EXACT_FLAG_BY_VALUE(frozen_type, FIELD_FROZEN_TYPE);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(frozen_type, FIELD_FROZEN_TYPE);

    flags |= _GET_FLAG_BY_VALUE(class_lookup, FIELD_CLASS_LOOKUP);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(class_lookup, FIELD_CLASS_LOOKUP);

    flags |= _GET_FLAG_BY_VALUE(auto_alias, FIELD_AUTO_ALIAS);
    def_flags |= _GET_DEF_FLAG_BY_VALUE(auto_alias, FIELD_AUTO_ALIAS);

    Field* self = field_create(cls, flags, def_flags);
    if (self) {
        field_set_attr(self, FIELD_ALIAS, alias);
        field_set_attr(self, FIELD_TITLE, title);
        field_set_attr(self, FIELD_DIFF_KEY, diff_key);
        field_set_attr(self, FIELD_EXAMPLES, examples);
        field_set_attr(self, FIELD_DEFAULT, default_value);
        field_set_attr(self, FIELD_DESCRIPTION, description);
        field_set_attr(self, FIELD_DEFAULT_FACTORY, default_factory);
        field_set_attr(self, FIELD_JSON_SCHEMA_EXTRA, json_schema_extra);
        field_set_attr(self, FIELD_SERIALIZATION_ALIAS, serialization_alias);
    }

    return (PyObject*)self;
}

static int
field_repr_attr(Field* self,
                UnicodeWriter* writer,
                uint32_t flag,
                const char* name,
                Py_ssize_t size_name)
{
    _UNICODE_WRITE_STRING(writer, name, size_name);
    PyObject* attr = _Field_GetAttr(self, flag);
    _UNICODE_WRITE(writer, attr ? attr : Py_None, PyObject_Repr);
    return 0;
error:
    return -1;
}

static int
config_repr_attr(Field* self, UnicodeWriter* writer)
{
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_INIT, self, "init");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_REPR, self, "repr");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_HASH, self, "hash");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_DICT, self, "dict");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_JSON, self, "json");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_KW_ONLY, self, "kw_only");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_FROZEN, self, "frozen");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_COMPARISON, self, "comparison");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_CLASS_LOOKUP, self, "class_lookup");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_FROZEN_TYPE, self, "frozen_type");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_AUTO_ALIAS, self, "auto_alias");
    _UNICODE_WRITE_REPR_ATTR(self, writer, FIELD_TITLE, "title=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(self, writer, FIELD_EXAMPLES, "examples=");
    return 0;
error:
    return -1;
}

static PyObject*
config_repr(Field* self)
{
    UnicodeWriter_Create(writer, 160);
    if (!writer) {
        return NULL;
    }

    _UNICODE_WRITE_STRING(writer, Py_TYPE(self)->tp_name, -1);
    _UNICODE_WRITE_CHAR(writer, '(');
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_STRICT, self, "strict");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_NUM_TO_STR, self, "num_to_str");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_ALLOW_INF_NAN, self, "allow_inf_nan");
    _UNICODE_WRITE_ATTR(writer, IS_FIELD_GC, self, "gc");
    _UNICODE_WRITE_REPR_ATTR(
      self, writer, FIELD_ALIAS_GENERATOR, "alias_generator=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);

    _UNICODE_WRITE_ATTR(
      writer, IS_FAIL_ON_EXTRA_INIT, self, "fail_on_extra_init");
    _UNICODE_WRITE_ATTR(
      writer, IS_FIELD_VALIDATE_PRIVATE, self, "validate_private");
    if (config_repr_attr(self, writer) < 0) {
        goto error;
    }
    _UNICODE_WRITE_CHAR(writer, ')');
    return UnicodeWriter_Finish(writer);
error:
    UnicodeWriter_Discard(writer);
    return NULL;
}

static PyObject*
field_repr(Field* self)
{
    UnicodeWriter_Create(writer, 160);
    if (!writer) {
        return NULL;
    }

    _UNICODE_WRITE_STRING(writer, Py_TYPE(self)->tp_name, -1);
    _UNICODE_WRITE_STRING(writer, "(default=", 9);
    if (IS_FIELD_DEFAULT(self->flags)) {
        _UNICODE_WRITE(
          writer, _Field_GetAttr(self, FIELD_DEFAULT), PyObject_Repr);
        _UNICODE_WRITE_STRING(writer, ", ", 2);
    } else {
        _UNICODE_WRITE_STRING(writer, "NULL, ", 6);
    }

    if (config_repr_attr(self, writer) < 0) {
        goto error;
    }

    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(self, writer, FIELD_DIFF_KEY, "diff_key=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(self, writer, FIELD_DESCRIPTION, "description=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(self, writer, FIELD_ALIAS, "alias=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(
      self, writer, FIELD_SERIALIZATION_ALIAS, "serialization_alias=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(
      self, writer, FIELD_DEFAULT_FACTORY, "default_factory=");
    _UNICODE_WRITE_STRING(writer, ", ", 2);
    _UNICODE_WRITE_REPR_ATTR(
      self, writer, FIELD_JSON_SCHEMA_EXTRA, "json_schema_extra=");
    _UNICODE_WRITE_CHAR(writer, ')');
    return UnicodeWriter_Finish(writer);
error:
    UnicodeWriter_Discard(writer);
    return NULL;
}

static PyObject*
config_richcompare(Field* self, PyObject* o, int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    if (Py_TYPE(self) != Py_TYPE(o)) {
        return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
    }

    Field* other = (Field*)o;
    if (self->flags != other->flags) {
        return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
    }

    Py_ssize_t size = FIELD_SIZE(self);
    for (uint16_t i = 0; i != size; i++) {
        int r =
          PyObject_RichCompareBool(self->ob_item[i], other->ob_item[i], Py_EQ);
        if (r < 0) {
            return NULL;
        }

        if (!r) {
            return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
        }
    }
    return Py_NewRef(op == Py_EQ ? Py_True : Py_False);
}

static Py_hash_t
config_hash(Field* self)
{
    Py_hash_t acc = self->flags * _PyHASH_XXPRIME_2;
    for (uint16_t i = 0; i < FIELD_SIZE(self); i++) {
        Py_hash_t lane = PyObject_Hash(self->ob_item[i]);
        if (lane == -1) {
            PyErr_Clear();
            continue;
        }
        acc += lane * _PyHASH_XXPRIME_2;
        acc = _PyHASH_XXROTATE(acc);
        acc *= _PyHASH_XXPRIME_1;
    }
    acc += FIELD_SIZE(self) ^ (_PyHASH_XXPRIME_5 ^ 3527539UL);
    return acc;
}

static PyObject*
get_flag(Field* self, uint32_t flags)
{
    return Py_NewRef(IF_FIELD_CHECK(self, flags) ? Py_True : Py_False);
}

static PyObject*
get_attr(Field* self, uint32_t flag)
{
    PyObject* res = _Field_GetAttr(self, flag);
    return Py_NewRef(res ? res : Py_None);
}

static PyObject*
get_default(Field* self, UNUSED void* d)
{
    PyObject* res = _Field_GetAttr(self, FIELD_DEFAULT);
    return res ? Py_NewRef(res) : ATTRIBUT_ERROR(self, "default");
}

static PyObject*
config___sizeof__(PyObject* self)
{
    Py_ssize_t size = Py_TYPE(self)->tp_basicsize +
                      Py_TYPE(self)->tp_itemsize * FIELD_SIZE(self);
    return PyLong_FromSsize_t(size);
}

static PyObject*
config_update(Field* self, Field* other)
{
    if (!PyType_IsSubtype(Py_TYPE(self), Py_TYPE(other))) {
        return PyErr_Format(
          PyExc_TypeError,
          "Argument 0 should be '%.100s', but '%.100s' is received",
          Py_TYPE(self)->tp_name,
          Py_TYPE(other)->tp_name);
    }
    return (PyObject*)field_inheritance(other, self, 1, NULL, NULL, NULL);
}

static PyMethodDef config_methods[] = {
    { "__sizeof__", PY_METHOD_CAST(config___sizeof__), METH_NOARGS, NULL },
    { "update", PY_METHOD_CAST(config_update), METH_O, NULL },
    { NULL }
};

static PyGetSetDef config_getsets[] = {
    { "init", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_INIT) },
    { "repr", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_REPR) },
    { "hash", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_HASH) },
    { "dict", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_DICT) },
    { "json", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_JSON) },
    { "kw_only", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_KW_ONLY) },
    { "frozen", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_FROZEN) },
    { "comparison",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_COMPARISON) },
    { "validate_private",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(intptr_t)(FIELD_VALIDATE_PRIVATE) },
    { "fail_on_extra_init",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(intptr_t)(FAIL_ON_EXTRA_INIT) },
    { "class_lookup",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_CLASS_LOOKUP) },
    { "num_to_str",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_NUM_TO_STR) },
    { "gc", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(_FIELD_GC) },
    { "allow_inf_nan",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_ALLOW_INF_NAN) },
    { "frozen_type",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_FROZEN_TYPE) },
    { "strict", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_STRICT) },
    { "auto_alias",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_AUTO_ALIAS) },
    { "title", PY_GETTER_CAST(get_attr), NULL, NULL, (void*)(FIELD_TITLE) },
    { "examples",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_EXAMPLES) },
    { "serialization_alias",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_SERIALIZATION_ALIAS) },
    { "alias_generator",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_ALIAS_GENERATOR) },

    { NULL }
};

PyTypeObject ConfigType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_richcompare = (richcmpfunc)config_richcompare,
    .tp_basicsize = sizeof(Field) - BASE_SIZE,
    .tp_dealloc = (destructor)config_dealloc,
    .tp_repr = (reprfunc)config_repr,
    .tp_name = "frost_typing.Config",
    .tp_hash = (hashfunc)config_hash,
    .tp_methods = config_methods,
    .tp_getset = config_getsets,
    .tp_itemsize = BASE_SIZE,
    .tp_new = config_new,
};

static PyGetSetDef field_getsets[] = {
    { "init", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_INIT) },
    { "repr", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_REPR) },
    { "hash", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_HASH) },
    { "dict", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_DICT) },
    { "json", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_JSON) },
    { "kw_only", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_KW_ONLY) },
    { "frozen", PY_GETTER_CAST(get_flag), NULL, NULL, (void*)(FIELD_FROZEN) },
    { "comparison",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_COMPARISON) },
    { "class_lookup",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_CLASS_LOOKUP) },
    { "frozen_type",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_FROZEN_TYPE) },
    { "auto_alias",
      PY_GETTER_CAST(get_flag),
      NULL,
      NULL,
      (void*)(FIELD_AUTO_ALIAS) },
    { "diff_key",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_DIFF_KEY) },
    { "description",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_DESCRIPTION) },
    { "title", PY_GETTER_CAST(get_attr), NULL, NULL, (void*)(FIELD_TITLE) },
    { "examples",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_EXAMPLES) },
    { "serialization_alias",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_SERIALIZATION_ALIAS) },
    { "alias", PY_GETTER_CAST(get_attr), NULL, NULL, (void*)(FIELD_ALIAS) },
    { "default",
      PY_GETTER_CAST(get_default),
      NULL,
      NULL,
      (void*)(FIELD_DEFAULT) },
    { "default_factory",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_DEFAULT_FACTORY) },
    { "json_schema_extra",
      PY_GETTER_CAST(get_attr),
      NULL,
      NULL,
      (void*)(FIELD_JSON_SCHEMA_EXTRA) },
    { NULL }
};

PyTypeObject FieldType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_richcompare = (richcmpfunc)config_richcompare,
    .tp_basicsize = sizeof(Field) - BASE_SIZE,
    .tp_dealloc = (destructor)config_dealloc,
    .tp_repr = (reprfunc)field_repr,
    .tp_name = "frost_typing.Field",
    .tp_hash = (hashfunc)config_hash,
    .tp_methods = config_methods,
    .tp_getset = field_getsets,
    .tp_itemsize = BASE_SIZE,
    .tp_new = field_new,
};

Field*
Field_Create(uint32_t flags, uint32_t def_flags)
{
    return field_create(&FieldType, flags, def_flags);
}

Field*
_Field_CreateValidatedFunc(PyObject* dflt, int kw_only)
{
    if (!dflt) {
        if (!kw_only) {
            return (Field*)Py_NewRef(DefaultFieldVFunc);
        }
        return (Field*)Py_NewRef(DefaultFieldVFuncKwOnly);
    }

    uint32_t flags = FIELD_DEFAULTS | FIELD_DEFAULT;
    if (kw_only) {
        flags |= FIELD_KW_ONLY;
    }

    Field* self = field_create(&FieldType, flags, FIELD_FULL);
    if (self) {
        field_set_attr(self, FIELD_DEFAULT, dflt);
    }
    return self;
}

static void
field_inheritance_items(Field* self, Field* root, Field* other)
{
    uint32_t flags = self->flags & FIELD_VALUES;
    while (flags) {
        uint32_t bit = flags & (~flags + 1);
        PyObject* val = _Field_GetAttr(root, bit);
        if (!val && other) {
            val = _Field_GetAttr(other, bit);
        }
        field_set_attr(self, bit, val);
        flags ^= bit;
    }
}

Field*
field_inheritance(Field* self,
                  Field* old,
                  int use_parent_attrs,
                  PyObject* serializer,
                  PyObject* ser_alias,
                  PyObject* alias)

{
    if (self->flags == old->flags && self->def_flags == old->def_flags &&
        !serializer && !ser_alias && !alias) {
        Py_INCREF(self);
        return self;
    }

    uint32_t new_flags, new_def_flags;
    if (use_parent_attrs) {
        new_flags = (self->flags & self->def_flags) |
                    (old->flags & old->def_flags & ~self->def_flags) |
                    (self->flags & ~self->def_flags & ~old->def_flags);
    } else {
        new_flags =
          (self->flags & self->def_flags) |
          (old->flags & old->def_flags & ~self->def_flags & ~FIELD_VALUES) |
          (self->flags & ~self->def_flags & ~old->def_flags);
    }

    new_def_flags = self->def_flags | old->def_flags;
    if (alias) {
        new_flags |= FIELD_ALIAS;
        new_def_flags |= FIELD_ALIAS;
    }

    if (ser_alias) {
        new_flags |= FIELD_SERIALIZATION_ALIAS;
        new_def_flags |= FIELD_SERIALIZATION_ALIAS;
    }

    if (serializer) {
        new_flags |= _FIELD_SERIALIZER;
        new_def_flags |= _FIELD_SERIALIZER;
    }

    Field* new_field = field_create(Py_TYPE(self), new_flags, new_def_flags);
    if (new_field) {
        field_inheritance_items(new_field, self, use_parent_attrs ? old : NULL);
        field_set_attr(new_field, FIELD_ALIAS, alias);
        field_set_attr(new_field, _FIELD_SERIALIZER, serializer);
        field_set_attr(new_field, FIELD_SERIALIZATION_ALIAS, ser_alias);
    }
    return new_field;
}

inline Field*
Config_Inheritance(Field* self, Field* old)
{
    return field_inheritance(self, old, 1, NULL, NULL, NULL);
}

inline Field*
Field_Inheritance(Field* self, Field* old)
{
    return field_inheritance(self, old, 1, NULL, NULL, NULL);
}

static void
field_copy_attr(Field* self, Field* old)
{
    uint32_t flags_val = self->flags & FIELD_VALUES;
    uint32_t bit = flags_val;
    while (bit) {
        if (flags_val & bit) {
            PyObject* val = _Field_GetAttr(old, bit);
            if (val) {
                field_set_attr(self, bit, val);
            }
        }
        bit >>= 1;
    }
}
Field*
_Field_CreateComputed(uint32_t flags, Field* old, PyObject* call)
{
    Field* self = Field_Create(flags | _FIELD_COMPUTED_FIELD, FIELD_FULL);
    if (!self) {
        return NULL;
    }

    field_copy_attr(self, old);
    field_set_attr(self, _FIELD_COMPUTED_FIELD, call);
    return self;
}

Field*
_Field_SetDiscriminator(Field* self)
{
    if (Py_REFCNT(self) == 1) {
        self->flags |= _FIELD_DISCRIMINATOR;
        self->def_flags |= _FIELD_DISCRIMINATOR;
        return (Field*)Py_NewRef(self);
    }

    Field* res = Field_Create(self->flags | _FIELD_DISCRIMINATOR,
                              self->def_flags | _FIELD_DISCRIMINATOR);
    if (res) {
        field_copy_attr(res, self);
    }
    return res;
}

static int
validate_alias(PyObject* alias, PyObject* ser_alias)
{
    if (alias) {
        if (!CheckValidityOfAttribute(alias)) {
            return 0;
        }
        _Hash_String(alias);
    }

    if (ser_alias) {
        if (!PyUnicode_Check(ser_alias)) {
            _RaiseInvalidType(
              "serialization_alias", "str", Py_TYPE(ser_alias)->tp_name);
            return 0;
        }
        _Hash_String(ser_alias);
    }
    return 1;
}

static inline int
field_get_auto_alias(Field* self, Field* config)
{
    if (IS_FIELD_AUTO_ALIAS(self->def_flags)) {
        return IS_FIELD_AUTO_ALIAS(self->flags) != 0;
    }
    if (IS_FIELD_AUTO_ALIAS(config->def_flags)) {
        return IS_FIELD_AUTO_ALIAS(config->flags) != 0;
    }
    return IS_FIELD_AUTO_ALIAS(self->flags) != 0;
}

static inline int
field_create_alias(Field* field,
                   Field* config,
                   PyObject* alias_gnrt,
                   PyObject* name,
                   PyObject** alias,
                   PyObject** ser_alias)
{
    int auto_alias = field_get_auto_alias(field, config);
    if (!alias_gnrt || !auto_alias) {
        return 0;
    }

    int want_alias = !IF_FIELD_CHECK(field, FIELD_ALIAS);
    int want_ser_alias = !IF_FIELD_CHECK(field, FIELD_SERIALIZATION_ALIAS);
    if (AliasGenerator_Check(alias_gnrt)) {
        return AliasGenerator_CreateAlias((AliasGenerator*)alias_gnrt,
                                          name,
                                          want_alias ? alias : NULL,
                                          want_ser_alias ? ser_alias : NULL);
    }

    if (want_alias) {
        *alias = PyObject_CallOneArg(alias_gnrt, name);
        if (!*alias) {
            return -1;
        }
    }

    if (want_ser_alias) {
        *ser_alias = PyObject_CallOneArg(alias_gnrt, name);
        if (!*ser_alias) {
            Py_XDECREF(*alias);
            return -1;
        }
    }
    return 0;
}

inline Field*
_Field_SetConfig(Field* self,
                 Field* config,
                 PyObject* name,
                 PyObject* serializer)
{
    PyObject *alias = NULL, *ser_alias = NULL;
    PyObject* alias_gnrt = FIELD_GET_ALIAS_GENERATOR(config);
    if (field_create_alias(self, config, alias_gnrt, name, &alias, &ser_alias) <
        0) {
        return NULL;
    }

    if (!validate_alias(alias, ser_alias)) {
        Py_XDECREF(ser_alias);
        Py_XDECREF(alias);
        return NULL;
    }
    Field* res =
      field_inheritance(self, config, 0, serializer, ser_alias, alias);
    Py_XDECREF(ser_alias);
    Py_XDECREF(alias);
    return res;
}

void
field_free(void)
{
    Py_DECREF(DefaultField);
    Py_DECREF(DefaultConfig);
    Py_DECREF(DefaultFieldVFunc);
    Py_DECREF(DefaultFieldVFuncNoInit);
    Py_DECREF(DefaultFieldVFuncKwOnly);
    Py_DECREF(DefaultFieldVFuncNoInitKwOnly);
    Py_DECREF(DefaultConfigValid);
    Py_DECREF(DefaultFieldPrivate);
}

int
field_setup(void)
{
    if (PyType_Ready(&ConfigType) < 0 || PyType_Ready(&FieldType) < 0) {
        return -1;
    }

    DefaultField = Field_Create(FIELD_DEFAULTS, 0);
    if (DefaultField == NULL) {
        return -1;
    }

    VoidField = Field_Create(FIELD_FROZEN | FIELD_FROZEN_TYPE, FIELD_FULL);
    if (!VoidField) {
        return -1;
    }

    DefaultFieldVFunc = Field_Create(FIELD_DEFAULTS, FIELD_FULL);
    if (!DefaultFieldVFunc) {
        return -1;
    }

    DefaultFieldVFuncNoInit =
      Field_Create(FIELD_DEFAULTS & ~FIELD_INIT, FIELD_FULL);
    if (!DefaultFieldVFuncNoInit) {
        return -1;
    }

    DefaultFieldVFuncKwOnly =
      Field_Create(FIELD_DEFAULTS | FIELD_KW_ONLY, FIELD_FULL);
    if (!DefaultFieldVFuncKwOnly) {
        return -1;
    }

    DefaultFieldVFuncNoInitKwOnly =
      Field_Create((FIELD_DEFAULTS | FIELD_KW_ONLY) & ~FIELD_INIT, FIELD_FULL);
    if (!DefaultFieldVFuncNoInitKwOnly) {
        return -1;
    }

    DefaultFieldPrivate = Field_Create(0, 0);
    if (!DefaultFieldPrivate) {
        return -1;
    }

    DefaultConfig = field_create(&ConfigType, CONFIG_DEFAULTS, 0);
    if (!DefaultConfig) {
        return -1;
    }

    DefaultConfigValid =
      field_create(&ConfigType, CONFIG_DEFAULTS_VALID, FAIL_ON_EXTRA_INIT);
    if (!DefaultConfigValid) {
        return -1;
    }
    return 0;
}
