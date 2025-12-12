#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define HASH_TABLE_MASK(map) (Py_SIZE(map) - 1)

typedef struct HashEntry
{
    PyObject* key;
    Py_ssize_t offset;
} HashEntry;

typedef struct HashTable
{
    PyObject_VAR_HEAD HashEntry entries[1];
} HashTable;

extern PyTypeObject HashTableType;

extern HashTable*
HashTable_Create(PyObject* schema, int init);
extern Py_ssize_t
_HashTable_Get(HashTable* map, PyObject* string);
extern Py_ssize_t
HashTable_Get(HashTable* map, PyObject* string);
extern int
HashTable_CheckExtraKwnames(HashTable* map,
                            PyObject* schemas,
                            PyObject* kwnames,
                            const char* func_name);
extern int
HashTable_CheckExtraDict(HashTable* map,
                         PyObject* schemas,
                         PyObject* dict,
                         const char* func_name);
extern int
hash_table_setup(void);
extern void
hash_table_free(void);