#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define FIELD_FULL UINT32_MAX

#define FIELD_SIZE(o) _Field_Size(((Field*)o))

#define FIELD_ALIAS ((uint32_t)1)
#define FIELD_TITLE ((uint32_t)1 << 1)
#define FIELD_DEFAULT ((uint32_t)1 << 2)
#define FIELD_EXAMPLES ((uint32_t)1 << 3)
#define FIELD_DEFAULT_FACTORY ((uint32_t)1 << 4)
#define FIELD_SERIALIZATION_ALIAS ((uint32_t)1 << 5)
#define FIELD_JSON_SCHEMA_EXTRA ((uint32_t)1 << 6)
#define FIELD_ALIAS_GENERATOR ((uint32_t)1 << 7)
#define FAIL_ON_EXTRA_INIT ((uint32_t)1 << 8)
#define FIELD_DESCRIPTION ((uint32_t)1 << 9)

#define _FIELD_SERIALIZER ((uint32_t)1 << 10)
#define _FIELD_COMPUTED_FIELD ((uint32_t)1 << 11)
#define FIELD_DIFF_KEY ((uint32_t)1 << 12)

#define FIELD_VALUES                                                           \
    (FIELD_DIFF_KEY | FIELD_ALIAS | FIELD_TITLE | FIELD_DEFAULT |              \
     FIELD_EXAMPLES | FIELD_DEFAULT_FACTORY | FIELD_SERIALIZATION_ALIAS |      \
     FIELD_JSON_SCHEMA_EXTRA | _FIELD_COMPUTED_FIELD | _FIELD_SERIALIZER |     \
     FIELD_ALIAS_GENERATOR | FIELD_DESCRIPTION)

#define _FIELD_GC ((uint32_t)1 << 13)
#define _FIELD_DISCRIMINATOR ((uint32_t)1 << 14)

#define FIELD_INIT ((uint32_t)1 << 15)
#define FIELD_REPR ((uint32_t)1 << 16)
#define FIELD_HASH ((uint32_t)1 << 17)
#define FIELD_DICT ((uint32_t)1 << 18)
#define FIELD_JSON ((uint32_t)1 << 19)
#define FIELD_COMPARISON ((uint32_t)1 << 20)
#define FIELD_CLASS_LOOKUP ((uint32_t)1 << 21)
#define FIELD_AUTO_ALIAS ((uint32_t)1 << 22)

#define FIELD_NUM_TO_STR ((uint32_t)1 << 23)
#define FIELD_ALLOW_INF_NAN ((uint32_t)1 << 24)

#define FIELD_DEFAULTS                                                         \
    (FIELD_INIT | FIELD_REPR | FIELD_DICT | FIELD_JSON | FIELD_COMPARISON |    \
     FIELD_CLASS_LOOKUP | FIELD_AUTO_ALIAS)
#define CONFIG_DEFAULTS                                                        \
    (FIELD_DEFAULTS | FIELD_ALLOW_INF_NAN | FAIL_ON_EXTRA_INIT | _FIELD_GC)

#define CONFIG_DEFAULTS_VALID                                                  \
    ((CONFIG_DEFAULTS & ~FAIL_ON_EXTRA_INIT) | FIELD_KW_ONLY)

#define FIELD_KW_ONLY ((uint32_t)1 << 25)
#define FIELD_FROZEN ((uint32_t)1 << 26)
#define FIELD_FROZEN_TYPE ((uint32_t)1 << 27)
#define _FIELD_CONST_DEFAULT ((uint32_t)1 << 28)

#define FIELD_STRICT ((uint32_t)1 << 29)
#define FIELD_VALIDATE_PRIVATE ((uint32_t)1 << 30)

#define FIELD_FIELD                                                            \
    (_FIELD_DISCRIMINATOR | _FIELD_CONST_DEFAULT | _FIELD_SERIALIZER |         \
     _FIELD_COMPUTED_FIELD | FIELD_DIFF_KEY | FIELD_DEFAULT | FIELD_INIT |     \
     FIELD_REPR | FIELD_HASH | FIELD_DICT | FIELD_JSON | FIELD_KW_ONLY |       \
     FIELD_FROZEN | FIELD_COMPARISON | FIELD_CLASS_LOOKUP |                    \
     FIELD_FROZEN_TYPE | FIELD_AUTO_ALIAS | FIELD_ALIAS | FIELD_TITLE |        \
     FIELD_EXAMPLES | FIELD_SERIALIZATION_ALIAS | FIELD_DEFAULT_FACTORY |      \
     FIELD_JSON_SCHEMA_EXTRA | FIELD_DESCRIPTION)

#define FIELD_CONFIG                                                           \
    (FAIL_ON_EXTRA_INIT | _FIELD_GC | FIELD_INIT | FIELD_REPR | FIELD_HASH |   \
     FIELD_DICT | FIELD_JSON | FIELD_STRICT | FIELD_KW_ONLY | FIELD_FROZEN |   \
     FIELD_COMPARISON | FIELD_CLASS_LOOKUP | FIELD_FROZEN_TYPE |               \
     FIELD_VALIDATE_PRIVATE | FIELD_AUTO_ALIAS | FIELD_ALLOW_INF_NAN |         \
     FIELD_NUM_TO_STR | FIELD_ALIAS_GENERATOR | FIELD_TITLE | FIELD_EXAMPLES)

#define IF_FIELD_CHECK(field, f) (field->flags & f)
#define IS_FIELD_DEFAULT(f) (f & FIELD_DEFAULT)
#define IS_FIELD_INIT(f) (f & FIELD_INIT)
#define IS_FIELD_REPR(f) (f & FIELD_REPR)
#define IS_FIELD_HASH(f) (f & FIELD_HASH)
#define IS_FIELD_DICT(f) (f & FIELD_DICT)
#define IS_FIELD_JSON(f) (f & FIELD_JSON)
#define IS_FIELD_ALIAS(f) (f & FIELD_ALIAS)
#define IS_FIELD_FROZEN(f) (f & FIELD_FROZEN)
#define IS_FIELD_KW_ONLY(f) (f & FIELD_KW_ONLY)
#define IF_FIELD_DEFAULT(f) (f & FIELD_DEFAULT)
#define IS_FIELD_DIFF_KEY(f) (f & FIELD_DIFF_KEY)
#define IS_FIELD_COMPARISON(f) (f & FIELD_COMPARISON)
#define IS_FIELD_AUTO_ALIAS(f) (f & FIELD_AUTO_ALIAS)
#define IS_FIELD_DESCRIPTION(f) (f & FIELD_DESCRIPTION)
#define IS_FIELD_FROZEN_TYPE(f) (f & FIELD_FROZEN_TYPE)
#define IS_FIELD_CLASS_LOOKUP(f) (f & FIELD_CLASS_LOOKUP)
#define IS_FAIL_ON_EXTRA_INIT(f) ((f & FAIL_ON_EXTRA_INIT) != 0)
#define _IS_FIELD_DISCRIMINATOR(f) (f & _FIELD_DISCRIMINATOR)
#define IF_FIELD_DEFAULT_FACTORY(f) (f & FIELD_DEFAULT_FACTORY)
#define IS_FIELD_ALIAS_GENERATOR(f) (f & FIELD_ALIAS_GENERATOR)
#define IS_FIELD_VALIDATE_PRIVATE(f) (f & FIELD_VALIDATE_PRIVATE)

// Config only
#define _VALIDATE_FLAGS (FIELD_ALLOW_INF_NAN | FIELD_NUM_TO_STR | FIELD_STRICT)
#define IS_FIELD_GC(f) (f & _FIELD_GC)
#define IS_FIELD_ALLOW_INF_NAN(f) (f & FIELD_ALLOW_INF_NAN)
#define IS_FIELD_NUM_TO_STR(f) (f & FIELD_NUM_TO_STR)
#define IS_FIELD_STRICT(f) (f & FIELD_STRICT)

#define _CAST_FIELD(o) _CAST(Field*, o)

#define Field_GET_SERIALIZATION_ALIAS(f)                                       \
    _Field_GetAttr(f, FIELD_SERIALIZATION_ALIAS)
#define Field_GET_DIFF_KEY(f) _Field_GetAttr(f, FIELD_DIFF_KEY)
#define Field_GET_ALIAS(f) _Field_GetAttr(f, FIELD_ALIAS)
#define Field_GET_SERIALIZER(f) _Field_GetAttr(f, _FIELD_SERIALIZER)
#define Field_GET_DEFAULT_FACTORY(f) _Field_GetAttr(f, FIELD_DEFAULT_FACTORY)
#define Field_GET_FIELD_COMPUTED_FIELD(f)                                      \
    ((ComputedField*)_Field_GetAttr(f, _FIELD_COMPUTED_FIELD))
#define Field_GET_JSON_SCHEMA_EXTRA(f)                                         \
    _Field_GetAttr(f, FIELD_JSON_SCHEMA_EXTRA)
#define FIELD_GET_ALIAS_GENERATOR(f) _Field_GetAttr(f, FIELD_ALIAS_GENERATOR)

#define Field_Check(op) PyType_IsSubtype(Py_TYPE(op), &FieldType)
#define Config_Check(op) PyType_IsSubtype(Py_TYPE(op), &ConfigType)
#define Config_CheckExact(op) Py_IS_TYPE((op), &ConfigType)

#define _CTX_CONFIG_GET_FLAGS(config) IF_FIELD_CHECK(config, _VALIDATE_FLAGS)

typedef struct Field
{
    PyObject_HEAD uint32_t flags;
    uint32_t def_flags;
    PyObject* ob_item[1];
} Field;

extern Field *DefaultField, *DefaultFieldPrivate, *DefaultFieldVFunc,
  *DefaultFieldVFuncNoInit, *DefaultFieldVFuncKwOnly,
  *DefaultFieldVFuncNoInitKwOnly, *VoidField, *DefaultConfig,
  *DefaultConfigValid;
extern PyTypeObject ConfigType;
extern PyTypeObject FieldType;
extern uint16_t
_Field_Size(Field*);
extern Field*
Field_Create(uint32_t, uint32_t);
extern Field*
Field_Inheritance(Field* self, Field* old);
extern Field*
Config_Inheritance(Field* self, Field* old);
extern Field*
_Field_CreateValidatedFunc(PyObject* dflt, int kw_only);
extern Field*
_Field_SetConfig(Field* self,
                 Field* config,
                 PyObject* name,
                 PyObject* serializer);
extern PyObject*
_Field_GetAttr(Field*, uint32_t);
extern Field*
_Field_CreateComputed(uint32_t, Field*, PyObject*);
extern Field*
_Field_SetDiscriminator(Field* self);
extern int
field_setup(void);
extern void
field_free(void);