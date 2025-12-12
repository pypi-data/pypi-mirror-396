#include "hash_table.h"
#include "field.h"
#include "schema.h"
#include "utils_common.h"
#include "json/json.h"

#define OVERSIZE 1.5
#define OFFSET 1
#define SCHEMAS_HAS_INIT(sc, o)                                                \
    IS_FIELD_INIT(SCHEMA_BY_OFFSET(sc, o)->field->flags)

static void
hash_table_dealloc(HashTable* self)
{
    Py_ssize_t size = Py_SIZE(self);
    for (Py_ssize_t i = 0; i != size; i++) {
        Py_XDECREF(self->entries[i].key);
    }
    Py_TYPE(self)->tp_free(self);
}

static inline HashTable*
hash_table_alloc(Py_ssize_t len)
{
    if (FT_UNLIKELY(len > PY_SSIZE_T_MAX / OVERSIZE)) {
        PyErr_NoMemory();
        return NULL;
    }

    Py_ssize_t size = 1;
    while (size < (len * OVERSIZE)) {
        size <<= 1;
    }

    return Object_NewVar(HashTable, &HashTableType, size);
}

HashTable*
HashTable_Create(PyObject* schema, int init)
{
    Py_ssize_t size = PyTuple_GET_SIZE(schema);
    HashTable* map = hash_table_alloc(size);
    if (FT_UNLIKELY(!map)) {
        return NULL;
    }

    Py_ssize_t mask = HASH_TABLE_MASK(map);
    for (Py_ssize_t i = 0; i != size; i++) {
        Schema* sc = _CAST(Schema*, PyTuple_GET_ITEM(schema, i));
        if (init && !IS_FIELD_INIT(sc->field->flags)) {
            continue;
        }

        PyObject* key = (init && IS_FIELD_ALIAS(sc->field->flags))
                          ? Field_GET_ALIAS(sc->field)
                          : sc->name;

        Py_hash_t hash = _Hash_String(key);
        Py_ssize_t j = hash & mask;

        while (map->entries[j].key) {
            j = (j + OFFSET) & mask;
        }

        _DeseralizeString_Intern(key);
        map->entries[j].key = Py_NewRef(key);
        map->entries[j].offset = i * BASE_SIZE;
    }

    return map;
}

Py_ssize_t
_HashTable_Get(HashTable* map, PyObject* string)
{
    if (FT_UNLIKELY(!map)) {
        return -1;
    }

    const Py_ssize_t key_len = PyUnicode_GET_LENGTH(string);
    const void* key_data = PyUnicode_DATA(string);
    const Py_ssize_t mask = HASH_TABLE_MASK(map);
    const Py_hash_t hash = _Hash_String(string);
    const HashEntry* entries = map->entries;
    Py_ssize_t i = hash & mask;

    for (;;) {
        PyObject* k = entries[i].key;
        if (!k) {
            return -1;
        }

        if (FT_LIKELY((k == string) ||
                      (_CAST(PyASCIIObject*, k)->hash == hash &&
                       PyUnicode_GET_LENGTH(k) == key_len &&
                       !memcmp(PyUnicode_DATA(k), key_data, key_len)))) {
            return entries[i].offset;
        }

        i = (i + OFFSET) & mask;
    }
}

inline Py_ssize_t
HashTable_Get(HashTable* map, PyObject* string)
{
    return PyUnicode_Check(string) ? _HashTable_Get(map, string) : -2;
}

static inline int
hash_table_check_extra(HashTable* map,
                       PyObject* schemas,
                       PyObject* name,
                       const char* func_name)
{
    const Py_ssize_t offset = _HashTable_Get(map, name);
    if (offset != -1 && SCHEMAS_HAS_INIT(schemas, offset)) {
        return 1;
    }
    PyErr_Format(PyExc_TypeError,
                 "%s() got an unexpected keyword argument '%U'",
                 func_name,
                 name);
    return 0;
}

int
HashTable_CheckExtraKwnames(HashTable* map,
                            PyObject* schemas,
                            PyObject* kwnames,
                            const char* func_name)
{
    if (!map || !kwnames) {
        return 1;
    }

    TupleForeach(name, kwnames)
    {
        if (!hash_table_check_extra(map, schemas, name, func_name)) {
            return 0;
        }
    }
    return 1;
}

int
HashTable_CheckExtraDict(HashTable* map,
                         PyObject* schemas,
                         PyObject* dict,
                         const char* func_name)
{
    if (!map || !dict) {
        return 1;
    }

    Py_ssize_t pos = 0;
    PyObject *name, *_;
    while (PyDict_Next(dict, &pos, &name, &_)) {
        if (!hash_table_check_extra(map, schemas, name, func_name)) {
            return 0;
        }
    }
    return 1;
}

PyTypeObject HashTableType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_basicsize = sizeof(HashTable) - sizeof(HashEntry),
    .tp_dealloc = (destructor)hash_table_dealloc,
    .tp_name = "frost_typing.HashTable",
    .tp_itemsize = sizeof(HashEntry),
};

int
hash_table_setup(void)
{
    return PyType_Ready(&HashTableType);
}

void
hash_table_free(void)
{
}