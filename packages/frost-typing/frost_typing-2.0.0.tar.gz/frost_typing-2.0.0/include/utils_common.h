#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define PY310_PLUS (PY_VERSION_HEX >= 0x030a0000)
#define PY311_PLUS (PY_VERSION_HEX >= 0x030b0000)
#define PY312_PLUS (PY_VERSION_HEX >= 0x030c0000)
#define PY313_PLUS (PY_VERSION_HEX >= 0x030d0000)
#define PY314_PLUS (PY_VERSION_HEX >= 0x030e0000)

#if defined(__has_builtin)
#if __has_builtin(__builtin_expect)
#define FT_LIKELY(x) __builtin_expect(!!(x), 1)
#define FT_UNLIKELY(x) __builtin_expect(!!(x), 0)
#else
#define FT_LIKELY(x) (x)
#define FT_UNLIKELY(x) (x)
#endif
#elif defined(__GNUC__) || defined(__clang__)
#define FT_LIKELY(x) __builtin_expect(!!(x), 1)
#define FT_UNLIKELY(x) __builtin_expect(!!(x), 0)
#else
#define FT_LIKELY(x) (x)
#define FT_UNLIKELY(x) (x)
#endif

#if defined(USED_JSON_SCHEMA) && (USED_JSON_SCHEMA == 1)
#define _USED_JSON_SCHEMA 1
#else
#define _USED_JSON_SCHEMA 0
#endif

#ifdef __GNUC__
#define UNUSED __attribute__((unused))
#elif defined(_MSC_VER)
#define UNUSED __pragma(warning(suppress : 4100))
#else
#define UNUSED
#endif

#define _CAST(tp, o) ((tp)(o))
#define _VOID_CAST(tp, o) _CAST(tp, _CAST(void (*)(void), o))
#define PY_METHOD_CAST(f) _VOID_CAST(PyCFunction, f)
#define PY_GETTER_CAST(f) _VOID_CAST(getter, f)
#define _STRLEN(s) (sizeof(s) / sizeof(s[0]))
#define SIZE_OBJ ((Py_ssize_t)sizeof(PyObject))
#define BASE_SIZE ((Py_ssize_t)sizeof(PyObject*))

#define TUPLE_ITEMS(o) (_CAST(PyTupleObject*, o)->ob_item)
#define LIST_ITEMS(o) (_CAST(PyListObject*, o)->ob_item)
#define LIST_CAPACITY(x) (_CAST(PyListObject*, x)->allocated)
#define TYPE_SIZE(tp) (_CAST(PyTypeObject*, tp)->tp_basicsize)
#define GET_ADDR(obj, o) (_CAST(PyObject**, _CAST(char*, obj) + o))
#define GET_OBJ(obj, o) (*_CAST(PyObject**, _CAST(char*, obj) + o))
#define SET_OBJ(obj, o, v) *_CAST(PyObject**, _CAST(char*, obj) + o) = v
#define _AnySetType_Check(tp)                                                  \
    (tp == &PySet_Type || tp == &PyFrozenSet_Type ||                           \
     PyType_IsSubtype(tp, &PySet_Type) ||                                      \
     PyType_IsSubtype(tp, &PyFrozenSet_Type))

#define _FUNC_GET_ACNT(f)                                                      \
    (_CAST(PyCodeObject*, _CAST(PyFunctionObject*, f)->func_code)->co_argcount)

#if SIZEOF_Py_hash_t > 4
#define _PyHASH_XXPRIME_1 ((Py_hash_t)11400714785074694791ULL)
#define _PyHASH_XXPRIME_2 ((Py_hash_t)14029467366897019727ULL)
#define _PyHASH_XXPRIME_5 ((Py_hash_t)2870177450012600261ULL)
#define _PyHASH_XXROTATE(x) ((x << 31) | (x >> 33)) /* Rotate left 31 bits */
#else
#define _PyHASH_XXPRIME_1 ((Py_hash_t)2654435761UL)
#define _PyHASH_XXPRIME_2 ((Py_hash_t)2246822519UL)
#define _PyHASH_XXPRIME_5 ((Py_hash_t)374761393UL)
#define _PyHASH_XXROTATE(x) ((x << 13) | (x >> 19)) /* Rotate left 13 bits */
#endif

#define TupleForeach(v, tuple, ...)                                            \
    for (PyObject** __##v = TUPLE_ITEMS(tuple),                                \
                    ** __end_##v = __##v + Py_SIZE(tuple),                     \
                    *v = *__##v;                                               \
         __##v != __end_##v;                                                   \
         v = *++__##v, ##__VA_ARGS__)

#define ListForeach(v, list, ...)                                              \
    for (PyObject** __##v = LIST_ITEMS(list),                                  \
                    ** __end_##v = __##v + Py_SIZE(list),                      \
                    *v = __##v ? *__##v : NULL;                                \
         __##v != __end_##v;                                                   \
         v = *++__##v, ##__VA_ARGS__)

#define SetForeach(v, set, ...)                                                \
    for (PyObject * v, *__pos_##v = 0;                                         \
         _PySet_Next(set, _CAST(Py_ssize_t*, &__pos_##v), &v);                 \
         ##__VA_ARGS__)

#if !PY310_PLUS
static inline PyObject*
_Py_NewRef(PyObject* o)
{
    Py_INCREF(o);
    return o;
}

static inline PyObject*
_Py_XNewRef(PyObject* o)
{
    Py_XINCREF(o);
    return o;
}
#define Py_NewRef(o) _Py_NewRef(_CAST(PyObject*, o))
#define Py_XNewRef(o) _Py_XNewRef(_CAST(PyObject*, o))
#endif

#define CREATE_VAR_INTERN___STING(v)                                           \
    __##v = PyUnicode_InternFromString(#v);                                    \
    if (FT_UNLIKELY(!__##v)) {                                                 \
        return -1;                                                             \
    }

#define CREATE_VAR_INTERN_STING(v)                                             \
    v = PyUnicode_InternFromString(#v);                                        \
    if (FT_UNLIKELY(!v)) {                                                     \
        return -1;                                                             \
    }

#if PY314_PLUS

#define UnicodeWriter PyUnicodeWriter
#define UnicodeWriter_Create(writer, min_l)                                    \
    PyUnicodeWriter* writer = PyUnicodeWriter_Create(min_l);

#define UnicodeWriter_WriteASCIIString PyUnicodeWriter_WriteASCII
#define UnicodeWriter_WriteChar PyUnicodeWriter_WriteChar
#define UnicodeWriter_WriteStr PyUnicodeWriter_WriteStr
#define UnicodeWriter_Discard PyUnicodeWriter_Discard
#define UnicodeWriter_Finish PyUnicodeWriter_Finish

#else

#define UnicodeWriter _PyUnicodeWriter
#define UnicodeWriter_Create(writer, min_l)                                    \
    _PyUnicodeWriter __writer;                                                 \
    _PyUnicodeWriter_Init(&__writer);                                          \
    __writer.overallocate = 1;                                                 \
    __writer.min_length = min_l;                                               \
    _PyUnicodeWriter* writer = &__writer;

#define UnicodeWriter_WriteASCIIString _PyUnicodeWriter_WriteASCIIString
#define UnicodeWriter_WriteChar _PyUnicodeWriter_WriteChar
#define UnicodeWriter_WriteStr _PyUnicodeWriter_WriteStr
#define UnicodeWriter_Discard _PyUnicodeWriter_Dealloc
#define UnicodeWriter_Finish _PyUnicodeWriter_Finish
#endif

/*UNICODE*/
#define _UNICODE_WRITE_STRING(w, s, i)                                         \
    if (FT_UNLIKELY(UnicodeWriter_WriteASCIIString(w, s, i) < 0)) {            \
        goto error;                                                            \
    }

#define _UNICODE_WRITE_STR(w, s)                                               \
    if (FT_UNLIKELY(UnicodeWriter_WriteStr(w, s) < 0)) {                       \
        goto error;                                                            \
    }

#define _UNICODE_WRITE_CHAR(w, s)                                              \
    if (FT_UNLIKELY(UnicodeWriter_WriteChar(w, s) < 0)) {                      \
        goto error;                                                            \
    }

#define _UNICODE_WRITE(w, o, f)                                                \
    if (FT_UNLIKELY(_UnicodeWriter_Write(w, (PyObject*)(o), f) < 0)) {         \
        goto error;                                                            \
    }

#define _UNICODE_WRITE_SSIZE(w, d)                                             \
    if (FT_UNLIKELY(_UnicodeWriter_WriteSsize(w, d) < 0)) {                    \
        goto error;                                                            \
    }

#define ATTRIBUT_ERROR(o, name)                                                \
    PyErr_Format(PyExc_AttributeError,                                         \
                 "'%.100s' object has no attribute '%s'",                      \
                 Py_TYPE(o)->tp_name,                                          \
                 name);

#define RETURN_ATTRIBUT_ERROR(o, name, r)                                      \
    PyErr_Format(PyExc_AttributeError,                                         \
                 "'%.100s' object has no attribute '%.100U'",                  \
                 Py_TYPE(o)->tp_name,                                          \
                 name);                                                        \
    return r;

#if PY313_PLUS
#define Py_BUILD_CORE 1
#include "internal/pycore_modsupport.h"
#undef Py_BUILD_CORE

#if PY314_PLUS
#define PyArg_UnpackKeywords(                                                  \
  args, nargs, kwargs, kwnames, parser, minpos, maxpos, minkw, buf)            \
    _PyArg_UnpackKeywords(                                                     \
      args, nargs, kwargs, kwnames, parser, minpos, maxpos, minkw, 0, buf)
#else
#define PyArg_UnpackKeywords _PyArg_UnpackKeywords
#endif

#else
#define PyArg_UnpackKeywords _PyArg_UnpackKeywords
#endif

#if PY313_PLUS
#define Py_BUILD_CORE 1
#include "internal/pycore_modsupport.h"
#include "internal/pycore_setobject.h"
#undef Py_BUILD_CORE
extern int
_PyDict_SetItem_KnownHash_LockHeld(PyObject* mp,
                                   PyObject* key,
                                   PyObject* value,
                                   Py_hash_t hash);
#define PyDict_SetItem_KnownHash _PyDict_SetItem_KnownHash_LockHeld
#define PyLong_AsByteArray(v, bytes, n, little_endian, is_signed)              \
    _PyLong_AsByteArray((PyLongObject*)v, bytes, n, little_endian, is_signed, 1)

#else
#define PyLong_AsByteArray(v, bytes, n, little_endian, is_signed)              \
    _PyLong_AsByteArray((PyLongObject*)v, bytes, n, little_endian, is_signed)
#define PyDict_SetItem_KnownHash _PyDict_SetItem_KnownHash
#endif

#define _PyDict_GetItem_Ascii(d, n)                                            \
    _PyDict_GetItem_KnownHash(d, n, _CAST(PyASCIIObject*, n)->hash)

#define _Dict_GetItem_String(d, k)                                             \
    _PyDict_GetItem_KnownHash(d, k, _Hash_String(k))

#define _PyDict_SetItem_Ascii(d, n, v)                                         \
    PyDict_SetItem_KnownHash(d, n, v, _CAST(PyASCIIObject*, n)->hash)

#define Dict_SetItem_String(d, k, v)                                           \
    PyDict_SetItem_KnownHash(d, k, v, _Hash_String(k))

#define Object_NewVar(type, t, s) _CAST(type*, _Object_NewVar(t, s))
#define Object_New(type, t) _CAST(type*, _Object_New(t))

typedef PyObject* (*ConverterObject)(PyObject*);

extern PyTypeObject* PyNone_Type;
extern PyObject *__annotations__, *__sep_and__, *__slots__, *__post_init__,
  *__return, *__dict__, *__weakref__, *__default_factory, *__config__,
  *__as_dict__, *__copy__, *__as_json__, *VoidTuple, *VoidDict, *Long_Zero,
  *Long_One, *Long_Four, *__origin__, *__module__, *__required_keys__,
  *__instancecheck__, *__type_params__, *__metadata__, *__bound__, *VoidSet,
  *__constraints__, *__args__, *__reduce_ex__, *__reduce__, *__setstate__,
  *__exclude, *__include, *_value2member_map_, *__is_safe, *__int, *__new__,
  *__init__, *__isoformat, *__append, *__value, *__args, *__kwargs, *__write,
  *__read, *__utcoffset, *__description, *_missing_;

extern int
_UnicodeWriter_WriteSsize(UnicodeWriter*, Py_ssize_t);
extern int
_UnicodeWriter_Write(UnicodeWriter*, PyObject*, PyObject* (*to_str)(PyObject*));
extern int
_PyList_Append_Decref(PyObject* list, PyObject* val);
extern int
PyDict_SetItemDecrefVal(PyObject*, PyObject*, PyObject*);
extern int
PyDict_SetItemStringDecrefVal(PyObject* mp, PyObject* str, PyObject* val);
extern int
_PyDict_SetItemAsciiDecrefVal(PyObject* mp, PyObject* str, PyObject* val);
extern int
PyDict_SetItemWithTransform(PyObject*,
                            PyObject*,
                            PyObject*,
                            PyObject* (*call)(PyObject*));
extern PyObject*
_RaiseInvalidReturnType(const char* msg,
                        const char* expected_tp,
                        const char* received_tp);
extern PyObject*
_RaiseInvalidType(const char* attr,
                  const char* expected_tp,
                  const char* received_tp);
extern int
EqString(PyObject* str_bytes, char* const str, Py_ssize_t size);
extern int
CheckValidityOfAttribute(PyObject*);
extern int
PyCheck_MaxArgs(const char* const func_name,
                Py_ssize_t args_cnt,
                Py_ssize_t max_arg_cnt);
extern int
PyCheck_ArgsCnt(const char* msg,
                Py_ssize_t args_cnt,
                Py_ssize_t expected_arg_cnt);
extern int
Unicode_IsPrivate(PyObject* unicode);
extern int
_ValidateArg(PyObject* obj, PyTypeObject* tp, const char* name);
extern Py_ssize_t
_Tuple_GetName(PyObject* tuple, PyObject* string);
extern PyObject*
_VectorCall_GetFuncArg(char* const msg,
                       PyObject* const* args,
                       size_t nargsf,
                       PyObject* kwnames);
extern PyObject*
_VectorCall_GetCallable(char* const msg,
                        PyObject* const* args,
                        size_t nargsf,
                        PyObject* kwnames);
extern Py_hash_t
_PyHashBytes(const void*, Py_ssize_t);
extern Py_ssize_t
_ArrayFastSearh(PyObject* const* array, PyObject* key, Py_ssize_t size);
extern PyObject*
_VectorCall_GetOneArg(char* const msg,
                      PyObject* const* args,
                      size_t nargsf,
                      PyObject* kwnames);
extern PyObject*
_PyObject_Get_Func(PyObject* func, const char* attr);
extern int
_PyObject_Get_ReturnHinst(PyObject* obj, PyObject** res);
extern PyObject*
_Object_Gettr(PyObject* obj, PyObject* name);
extern PyObject*
_Dict_GetAscii(PyObject* dict, PyObject* name);
extern PyObject*
Dict_GetItemNoError(PyObject* mp, PyObject* key);
extern int
Object_EqualAllowNull(PyObject* self, PyObject* other);
extern Py_hash_t
_Hash_String(PyObject* str);
extern int
_Dict_MergeKwnames(PyObject* dict, PyObject* const* args, PyObject* kwnames);
extern int
_PySet_Next(PyObject* set, Py_ssize_t* pos, PyObject** val);
extern PyObject*
ObjectIterNext(PyObject* obj);
extern int
_PyIter_GetNext(PyObject* iter, PyObject** item);
extern PyObject*
_Err_GetRaisedException(void);
extern void
_Err_SetRaisedException(PyObject* ex);
extern PyObject*
_StopIteration_GetObject(void);
extern PyObject*
_GetAwaitableIter(PyObject* obj);
extern int
PyObject_CheckHashable(PyObject* obj);
extern int
PyObject_CheckIter(PyObject* obj);
extern PyObject*
PyObject_Get_annotations(PyObject* obj);
extern PyObject*
PyObject_Get__name__(PyTypeObject* tp);
extern void
_Stack_Decref(PyObject** stack, Py_ssize_t size);
extern void*
Mem_New(Py_ssize_t size);
extern void*
_Object_NewVar(PyTypeObject* tp, Py_ssize_t size);
extern void*
_Object_New(PyTypeObject* tp);
extern void
_Object_Dealloc(PyObject* self);
extern PyObject*
PyObject_CallTwoArg(PyObject* call, PyObject* one, PyObject* two);
extern PyObject*
PyObject_CallThreeArg(PyObject* call,
                      PyObject* one,
                      PyObject* two,
                      PyObject* three);
extern PyObject*
Object_FromDbRow(PyObject* callable, PyObject** args, size_t nargsf);
extern PyObject*
_Dict_FromKwnames(PyObject* const* args, PyObject* kwnames);
extern int
utils_common_setup(void);
extern void
utils_common_free(void);