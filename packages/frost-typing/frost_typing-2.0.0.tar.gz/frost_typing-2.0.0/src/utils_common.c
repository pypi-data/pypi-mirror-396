#include "utils_common.h"
#include "stdio.h"

PyObject *__annotations__, *__sep_and__, *__slots__, *__post_init__, *__return,
  *__dict__, *__weakref__, *__default_factory, *__config__, *__as_dict__,
  *__copy__, *__as_json__, *VoidTuple, *VoidDict, *Long_Zero, *Long_One,
  *Long_Four, *__origin__, *__module__, *__required_keys__, *__instancecheck__,
  *__type_params__, *__metadata__, *__bound__, *VoidSet, *__constraints__,
  *__args__, *__reduce_ex__, *__reduce__, *__setstate__, *__exclude, *__include,
  *_value2member_map_, *__is_safe, *__int, *__new__, *__init__, *__isoformat,
  *__append, *__value, *__args, *__kwargs, *__write, *__read, *__utcoffset,
  *__description, *_missing_;

PyTypeObject* PyNone_Type;
typedef Py_hash_t (*hash_func)(const void*, Py_ssize_t);
hash_func get_hash_bytes;

static int
set_next(PySetObject* set, Py_ssize_t* pos, PyObject** val)
{
    Py_ssize_t i;
    Py_ssize_t mask;
    setentry* entry;

    i = *pos;
    mask = set->mask;
    entry = &set->table[i];
    while (i <= mask && (entry->key == NULL || entry->key == _PySet_Dummy)) {
        i++;
        entry++;
    }
    *pos = i + 1;
    if (i > mask) {
        return 0;
    }
    *val = entry->key;
    return 1;
}

inline int
_PySet_Next(PyObject* set, Py_ssize_t* pos, PyObject** val)
{
    return set_next((PySetObject*)set, pos, val);
}

inline PyObject*
ObjectIterNext(PyObject* obj)
{
    iternextfunc tp_iternext = Py_TYPE(obj)->tp_iternext;
    if (FT_LIKELY(tp_iternext)) {
        return tp_iternext(obj);
    }
    PyErr_BadArgument();
    return NULL;
}

int
_PyIter_GetNext(PyObject* iter, PyObject** item)
{
    *item = ObjectIterNext(iter);
    if (*item) {
        return 1;
    }

    PyObject* err_tp = PyErr_Occurred();
    if (!err_tp) {
        return 0;
    }

    if (PyErr_GivenExceptionMatches(err_tp, PyExc_StopIteration)) {
        PyErr_Clear();
        return 0;
    }
    return -1;
}

void
_Err_SetRaisedException(PyObject* ex)
{
#if PY312_PLUS
    PyErr_SetRaisedException(ex);
#else
    PyObject* exc_tb = PyException_GetTraceback(ex);
    PyErr_Restore(Py_NewRef(Py_TYPE(ex)), ex, exc_tb);
#endif
}

PyObject*
_Err_GetRaisedException(void)
{
#if PY312_PLUS
    return PyErr_GetRaisedException();
#else
    PyObject *exc_type, *exc_val, *exc_tb;
    PyErr_Fetch(&exc_type, &exc_val, &exc_tb);
    if (!exc_type) {
        return NULL;
    }

    PyErr_NormalizeException(&exc_type, &exc_val, &exc_tb);
    if (exc_tb) {
        PyException_SetTraceback(exc_val, exc_tb);
    }
    Py_XDECREF(exc_type);
    Py_XDECREF(exc_tb);
    return exc_val;
#endif
}

PyObject*
_StopIteration_GetObject(void)
{
    PyObject* exc_val = _Err_GetRaisedException();
    if (FT_UNLIKELY(!exc_val)) {
        return NULL;
    }

    if (!PyErr_GivenExceptionMatches(exc_val, PyExc_StopIteration)) {
        _Err_SetRaisedException(exc_val);
        return NULL;
    }

    PyObject* res = _CAST(PyStopIterationObject*, exc_val)->value;
    if (FT_UNLIKELY(!res)) {
        res = Py_None;
    }

    Py_INCREF(res);
    Py_DECREF(exc_val);
    return res;
}

PyObject*
_GetAwaitableIter(PyObject* obj)
{
    PyTypeObject* tp = Py_TYPE(obj);
    if (FT_LIKELY(tp->tp_as_async && tp->tp_as_async->am_await)) {
        PyObject* res = tp->tp_as_async->am_await(obj);
        if (FT_UNLIKELY(res && !PyIter_Check(res))) {
            PyErr_Format(PyExc_TypeError,
                         "%s.__await__() must return an iterator, not %s",
                         tp->tp_name,
                         Py_TYPE(res)->tp_name);
            Py_CLEAR(res);
        }
        return res;
    }

    PyErr_Format(
      PyExc_TypeError, "'%.100s' object can't be awaited", tp->tp_name);
    return NULL;
}

int
_UnicodeWriter_WriteSsize(UnicodeWriter* writer, Py_ssize_t digit)
{
    char buffer_digit[21];
    int size_cnt = sprintf(buffer_digit, "%zu", digit);
    return UnicodeWriter_WriteASCIIString(writer, buffer_digit, size_cnt);
}

int
_UnicodeWriter_Write(UnicodeWriter* writer,
                     PyObject* obj,
                     ConverterObject to_str)
{
    PyObject* s = to_str(obj);
    if (FT_UNLIKELY(!s)) {
        return -1;
    }
    int r = UnicodeWriter_WriteStr(writer, s);
    Py_DECREF(s);
    return r;
}

inline int
Unicode_IsPrivate(PyObject* unicode)
{
    return PyUnicode_GET_LENGTH(unicode) &&
           PyUnicode_READ_CHAR(unicode, 0) == (Py_UCS4)'_';
}

int
CheckValidityOfAttribute(PyObject* name)
{
    if (PyUnicode_Check(name) && PyUnicode_IS_ASCII(name) &&
        PyUnicode_IsIdentifier(name)) {
        // Calculate the hash for caching
        _Hash_String(name);
        return 1;
    }
    PyErr_Format(PyExc_ValueError, "Invalid attribute: '%S'", name);
    return 0;
}

inline int
PyCheck_MaxArgs(const char* const func_name,
                Py_ssize_t args_cnt,
                Py_ssize_t max_arg_cnt)
{
    if (FT_UNLIKELY(args_cnt > max_arg_cnt)) {
        PyErr_Format(PyExc_TypeError,
                     "%s() takes %zu positional argument but %zu were given",
                     func_name,
                     max_arg_cnt,
                     args_cnt);
        return 0;
    }
    return 1;
}

inline int
PyCheck_ArgsCnt(const char* msg,
                Py_ssize_t args_cnt,
                Py_ssize_t expected_arg_cnt)
{
    if (FT_LIKELY(args_cnt == expected_arg_cnt)) {
        return 1;
    }

    PyErr_Format(PyExc_TypeError,
                 "%s() takes %zu positional argument but %zu were given",
                 msg,
                 expected_arg_cnt,
                 args_cnt);
    return 0;
}

inline int
_PyList_Append_Decref(PyObject* list, PyObject* val)
{
    Py_ssize_t size = Py_SIZE(list);
    if (FT_LIKELY((LIST_CAPACITY(list) > size))) {
        PyList_SET_ITEM(list, size, val);
        Py_SET_SIZE(list, ++size);
        return 0;
    }
    int r = PyList_Append(list, val);
    Py_DECREF(val);
    return r;
}

inline int
_PyDict_SetItemAsciiDecrefVal(PyObject* mp, PyObject* str, PyObject* item)
{
    int r = _PyDict_SetItem_Ascii(mp, str, item);
    Py_DECREF(item);
    return r;
}

inline int
PyDict_SetItemStringDecrefVal(PyObject* mp, PyObject* str, PyObject* item)
{
    int r = Dict_SetItem_String(mp, str, item);
    Py_DECREF(item);
    return r;
}

inline int
PyDict_SetItemDecrefVal(PyObject* mp, PyObject* key, PyObject* item)
{
    int r = PyDict_SetItem(mp, key, item);
    Py_DECREF(item);
    return r;
}

int
PyDict_SetItemWithTransform(PyObject* mp,
                            PyObject* key,
                            PyObject* item,
                            PyObject* (*call)(PyObject*))
{
    PyObject* tmp = call(item);
    if (!tmp) {
        return -1;
    }
    return PyDict_SetItemDecrefVal(mp, key, tmp);
}

PyObject*
_Dict_GetAscii(PyObject* dict, PyObject* name)
{
    return Py_XNewRef(_PyDict_GetItem_Ascii(dict, name));
}

PyObject*
Dict_GetItemNoError(PyObject* mp, PyObject* key)
{
    PyObject* res = PyDict_GetItemWithError(mp, key);
    if (!res) {
        PyErr_Clear();
    }
    return res;
}

inline Py_ssize_t
_ArrayFastSearh(PyObject* const* array, PyObject* key, Py_ssize_t size)
{
    for (Py_ssize_t i = 0; i != size; ++i) {
        if (array[i] == key) {
            return i;
        }
    }
    return -1;
}

int
EqString(PyObject* str_bytes, char* const str, Py_ssize_t size)
{
    if (PyUnicode_Check(str_bytes)) {
        return PyUnicode_KIND(str_bytes) == 1 &&
               PyUnicode_GET_LENGTH(str_bytes) == size &&
               !memcmp(PyUnicode_DATA(str_bytes), str, size);
    }
    if (PyBytes_Check(str_bytes)) {
        return PyBytes_GET_SIZE(str_bytes) == size &&
               !memcmp(_CAST(PyBytesObject*, str_bytes)->ob_sval, str, size);
    }
    if (PyByteArray_Check(str_bytes)) {
        return PyByteArray_GET_SIZE(str_bytes) == size &&
               !memcmp(
                 _CAST(PyByteArrayObject*, str_bytes)->ob_bytes, str, size);
    }
    return -1;
}

inline int
PyObject_CheckHashable(PyObject* obj)
{
    hashfunc tp_hash = Py_TYPE(obj)->tp_hash;
    return tp_hash && tp_hash != PyObject_HashNotImplemented;
}

inline int
PyObject_CheckIter(PyObject* obj)
{
    return Py_TYPE(obj)->tp_iter || PySequence_Check(obj);
}

inline PyObject*
_RaiseInvalidReturnType(const char* msg,
                        const char* expected_tp,
                        const char* received_tp)
{
    return PyErr_Format(PyExc_TypeError,
                        "%s should return %.100s, not '%.100s'",
                        msg,
                        expected_tp,
                        received_tp);
}

inline PyObject*
_RaiseInvalidType(const char* attr,
                  const char* expected_tp,
                  const char* received_tp)
{
    return PyErr_Format(PyExc_TypeError,
                        "Argument '%s' must be a %.100s, not '%.100s'",
                        attr,
                        expected_tp,
                        received_tp);
}

inline Py_hash_t
_Hash_String(PyObject* str)
{
    Py_hash_t x = _CAST(PyASCIIObject*, str)->hash;
    if (x != -1) {
        return x;
    }
    x = _PyHashBytes(PyUnicode_DATA(str),
                     PyUnicode_GET_LENGTH(str) * PyUnicode_KIND(str));
    _CAST(PyASCIIObject*, str)->hash = x;
    return x;
}

PyObject*
_PyObject_Get_Func(PyObject* func, const char* attr)
{
    if (Py_IS_TYPE(func, &PyFunction_Type)) {
        return Py_NewRef(func);
    }
    if (Py_IS_TYPE(func, &PyClassMethod_Type)) {
        func = PyObject_GetAttrString(func, "__func__");
        if (func) {
            PyObject* tmp = _PyObject_Get_Func(func, attr);
            Py_DECREF(func);
            return tmp;
        }
        return func;
    }

    return _RaiseInvalidType(
      attr, "function or classmethod", Py_TYPE(func)->tp_name);
}

int
_PyObject_Get_ReturnHinst(PyObject* obj, PyObject** res)
{
    if (PyType_Check(obj)) {
        *res = Py_NewRef(obj);
        return 1;
    }

    if (PyFunction_Check(obj)) {
        PyObject* annot = PyFunction_GetAnnotations(obj);
        if (!annot) {
            *res = NULL;
            return 0;
        }

        *res = Py_XNewRef(_PyDict_GetItem_Ascii(annot, __return));
        return *res ? 1 : 0;
    }

    if (Py_IS_TYPE(obj, &PyClassMethod_Type)) {
        PyObject* tmp = PyObject_GetAttrString(obj, "__func__");
        if (FT_UNLIKELY(!tmp)) {
            *res = NULL;
            return -1;
        }
        int r = _PyObject_Get_ReturnHinst(tmp, res);
        Py_DECREF(tmp);
        return r;
    }

    *res = NULL;
    return 0;
}

inline Py_hash_t
_PyHashBytes(const void* data, Py_ssize_t size)
{
    return get_hash_bytes(data, size);
}

inline int
Object_EqualAllowNull(PyObject* self, PyObject* other)
{
    if (self && other) {
        return PyObject_RichCompareBool(self, other, Py_EQ);
    }
    return self == other;
}

PyObject*
_Object_Gettr(PyObject* obj, PyObject* name)
{
    if (FT_UNLIKELY(!PyUnicode_Check(name))) {
        return NULL;
    }

    PyObject* res;
    if (PyDict_Check(obj)) {
        res = _Dict_GetAscii(obj, name);
    } else if (Py_TYPE(obj)->tp_getattro == PyObject_GenericGetAttr) {
        res = _PyObject_GenericGetAttrWithDict(obj, name, NULL, 1);
    } else {
        res = PyObject_GetAttr(obj, name);
    }

    if (FT_UNLIKELY(!res)) {
        PyErr_Clear();
    }
    return res;
}

PyObject*
PyObject_Get_annotations(PyObject* obj)
{
    PyObject* annot = PyObject_GetAttr(obj, __annotations__);
    if (!annot) {
        return NULL;
    }

    if (!PyDict_Check(annot)) {
        _RaiseInvalidType("__annotations__", "dict", Py_TYPE(annot)->tp_name);
        Py_DECREF(annot);
        return NULL;
    }

    return annot;
}

inline int
_ValidateArg(PyObject* obj, PyTypeObject* tp, const char* name)
{
    if (FT_LIKELY(!obj || Py_IS_TYPE(obj, tp))) {
        return 1;
    }
    _RaiseInvalidType(name, tp->tp_name, Py_TYPE(obj)->tp_name);
    return 0;
}

PyObject*
_VectorCall_GetOneArg(char* const msg,
                      PyObject* const* args,
                      size_t nargsf,
                      PyObject* kwnames)
{
    if (FT_UNLIKELY(kwnames && PyTuple_GET_SIZE(kwnames))) {
        return PyErr_Format(
          PyExc_TypeError, "%s() takes no keyword arguments", msg);
    }

    if (FT_UNLIKELY(!PyCheck_ArgsCnt(msg, PyVectorcall_NARGS(nargsf), 1))) {
        return NULL;
    }
    return (PyObject*)*args;
}

int
_Dict_MergeKwnames(PyObject* dict, PyObject* const* args, PyObject* kwnames)
{
    if (!kwnames) {
        return 0;
    }

    TupleForeach(name, kwnames, args++)
    {
        if (FT_UNLIKELY(Dict_SetItem_String(dict, name, *args) < 0)) {
            return -1;
        }
    }
    return 0;
}

Py_ssize_t
_Tuple_GetName(PyObject* tuple, PyObject* string)
{
    if (!tuple) {
        return -1;
    }

    PyObject** names = TUPLE_ITEMS(tuple);
    Py_ssize_t size = PyTuple_GET_SIZE(tuple);
    for (Py_ssize_t i = 0; i != size; i++) {
        if (names[i] == string) {
            return i;
        }
    }

    Py_hash_t hash = _Hash_String(string);
    Py_ssize_t key_len = PyUnicode_GET_LENGTH(string);

    for (Py_ssize_t i = 0; i != size; i++) {
        PyObject* name = names[i];
        if ((key_len == PyUnicode_GET_LENGTH(name) &&
             _Hash_String(name) == hash &&
             !memcmp(PyUnicode_DATA(name), PyUnicode_DATA(string), key_len))) {
            return i;
        }
    }
    return -1;
}

PyObject*
_VectorCall_GetFuncArg(char* const msg,
                       PyObject* const* args,
                       size_t nargsf,
                       PyObject* kwnames)
{
    PyObject* func = _VectorCall_GetOneArg(msg, args, nargsf, kwnames);
    return func ? _PyObject_Get_Func(func, "func") : func;
}

PyObject*
_VectorCall_GetCallable(char* const msg,
                        PyObject* const* args,
                        size_t nargsf,
                        PyObject* kwnames)
{
    PyObject* callable = _VectorCall_GetOneArg(msg, args, nargsf, kwnames);
    if (FT_UNLIKELY(!callable)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyCallable_Check(callable))) {
        return _RaiseInvalidType(msg, "Callable", Py_TYPE(callable)->tp_name);
    }

    return callable;
}

inline PyObject*
PyObject_Get__name__(PyTypeObject* tp)
{
    if (tp->tp_flags & Py_TPFLAGS_HEAPTYPE) {
        return Py_NewRef(_CAST(PyHeapTypeObject*, tp)->ht_name);
    }
    return PyUnicode_FromString(_PyType_Name(tp));
}

inline void
_Stack_Decref(PyObject** stack, Py_ssize_t size)
{
    for (Py_ssize_t i = 0; i < size; ++i) {
        Py_XDECREF(stack[i]);
    }
    PyMem_Free((void*)stack);
}

inline void*
Mem_New(Py_ssize_t size)
{
    void* res = PyMem_Malloc(size);
    if (FT_LIKELY(res)) {
        memset(res, '\0', size);
    } else {
        PyErr_NoMemory();
    }
    return res;
}

void*
_Object_New(PyTypeObject* tp)
{
    void* obj;
    if (tp->tp_flags & Py_TPFLAGS_HAVE_GC) {
        obj = PyObject_GC_New(void*, tp);
    } else {
        obj = PyObject_New(void*, tp);
    }

    if (FT_LIKELY(obj)) {
        memset(_CAST(char*, obj) + SIZE_OBJ, '\0', tp->tp_basicsize - SIZE_OBJ);
        if (tp->tp_flags & Py_TPFLAGS_HAVE_GC) {
            PyObject_GC_Track(obj);
        }
    }
    return obj;
}

void*
_Object_NewVar(PyTypeObject* tp, Py_ssize_t nitems)
{
    void* obj;
    if (tp->tp_flags & Py_TPFLAGS_HAVE_GC) {
        obj = PyObject_GC_NewVar(void, tp, nitems);
    } else {
        obj = PyObject_NewVar(void, tp, nitems);
    }

    if (FT_LIKELY(obj)) {
        const Py_ssize_t size =
          (tp->tp_basicsize - sizeof(PyVarObject)) + (nitems * tp->tp_itemsize);
        memset(_CAST(char*, obj) + sizeof(PyVarObject), 0, size);
        if (tp->tp_flags & Py_TPFLAGS_HAVE_GC) {
            PyObject_GC_Track(obj);
        }
    }
    return obj;
}

void
_Object_Dealloc(PyObject* self)
{
    PyTypeObject* tp = Py_TYPE(self);
    if (tp->tp_flags & Py_TPFLAGS_HAVE_GC) {
        PyObject_GC_UnTrack(self);
        Py_TRASHCAN_BEGIN(self, _Object_Dealloc);
        if (FT_LIKELY(tp->tp_clear)) {
            tp->tp_clear(self);
        }
        tp->tp_free(self);
        Py_TRASHCAN_END;
    } else {
        if (FT_LIKELY(tp->tp_clear)) {
            tp->tp_clear(self);
        }
        tp->tp_free(self);
    }
}

static inline int
validated_kwnames(PyObject* kwnames)
{
    if (FT_UNLIKELY(!_ValidateArg(kwnames, &PyTuple_Type, "kwnames"))) {
        return 0;
    }

    TupleForeach(name, kwnames)
    {
        if (FT_UNLIKELY(!PyUnicode_Check(name))) {
            PyErr_SetString(PyExc_TypeError, "keywords must be strings");
            return 0;
        }
    }
    return 1;
}

PyObject*
Object_FromDbRow(PyObject* callable, PyObject** args, size_t nargsf)
{
    PyObject *kwnames, *arg, **buff;
    if (!PyCheck_ArgsCnt(".from_db_row", PyVectorcall_NARGS(nargsf), 2)) {
        return NULL;
    }

    kwnames = args[0];
    if (FT_UNLIKELY(!validated_kwnames(kwnames))) {
        return NULL;
    }

    arg = args[1];
    if (PyTuple_Check(arg)) {
        Py_INCREF(arg);
        buff = TUPLE_ITEMS(arg);
    } else if (PyList_Check(arg)) {
        Py_INCREF(arg);
        buff = LIST_ITEMS(arg);
    } else {
        arg = PySequence_List(arg);
        if (!arg) {
            return NULL;
        }
        buff = LIST_ITEMS(arg);
    }

    if (!PyCheck_ArgsCnt(".from_db_row", Py_SIZE(arg), Py_SIZE(kwnames))) {
        Py_DECREF(args);
        return NULL;
    }

    PyObject* res = PyObject_Vectorcall((PyObject*)callable, buff, 0, kwnames);
    Py_DECREF(args);
    return res;
}

inline PyObject*
PyObject_CallTwoArg(PyObject* call, PyObject* one, PyObject* two)
{
    PyObject* const args[3] = { NULL, one, two };
    return PyObject_Vectorcall(
      call, args + 1, 2 | PY_VECTORCALL_ARGUMENTS_OFFSET, NULL);
}

inline PyObject*
PyObject_CallThreeArg(PyObject* call,
                      PyObject* one,
                      PyObject* two,
                      PyObject* three)
{
    PyObject* const args[4] = { NULL, one, two, three };
    return PyObject_Vectorcall(
      call, args + 1, 3 | PY_VECTORCALL_ARGUMENTS_OFFSET, NULL);
}

PyObject*
_Dict_FromKwnames(PyObject* const* args, PyObject* kwnames)
{
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(!dict || !kwnames)) {
        return dict;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(kwnames);
    PyObject** names = TUPLE_ITEMS(kwnames);
    for (Py_ssize_t i = 0; i != size; i++) {
        if (FT_UNLIKELY(Dict_SetItem_String(dict, names[i], args[i]) < 0)) {
            Py_DECREF(dict);
            return NULL;
        }
    }

    return dict;
}

int
utils_common_setup(void)
{
    VoidSet = PyFrozenSet_New(NULL);
    if (!VoidSet) {
        return -1;
    }

    PyNone_Type = Py_TYPE(Py_None);
    CREATE_VAR_INTERN_STING(__new__)
    CREATE_VAR_INTERN_STING(__init__)
    CREATE_VAR_INTERN_STING(__copy__)
    CREATE_VAR_INTERN_STING(__dict__)
    CREATE_VAR_INTERN_STING(__args__)
    CREATE_VAR_INTERN_STING(_missing_);
    CREATE_VAR_INTERN_STING(__bound__)
    CREATE_VAR_INTERN_STING(__slots__)
    CREATE_VAR_INTERN_STING(__config__)
    CREATE_VAR_INTERN_STING(__origin__)
    CREATE_VAR_INTERN_STING(__module__)
    CREATE_VAR_INTERN_STING(__reduce__)
    CREATE_VAR_INTERN_STING(__as_json__)
    CREATE_VAR_INTERN_STING(__weakref__)
    CREATE_VAR_INTERN_STING(__as_dict__)
    CREATE_VAR_INTERN_STING(__metadata__)
    CREATE_VAR_INTERN_STING(__setstate__)
    CREATE_VAR_INTERN_STING(__reduce_ex__)
    CREATE_VAR_INTERN_STING(__post_init__)
    CREATE_VAR_INTERN_STING(__annotations__)
    CREATE_VAR_INTERN_STING(__constraints__)
    CREATE_VAR_INTERN_STING(__type_params__)
    CREATE_VAR_INTERN_STING(__required_keys__)
    CREATE_VAR_INTERN_STING(__instancecheck__)
    CREATE_VAR_INTERN_STING(_value2member_map_)
    CREATE_VAR_INTERN___STING(default_factory)
    CREATE_VAR_INTERN___STING(description)
    CREATE_VAR_INTERN___STING(isoformat)
    CREATE_VAR_INTERN___STING(utcoffset)
    CREATE_VAR_INTERN___STING(is_safe)
    CREATE_VAR_INTERN___STING(return)
    CREATE_VAR_INTERN___STING(append)
    CREATE_VAR_INTERN___STING(exclude)
    CREATE_VAR_INTERN___STING(include)
    CREATE_VAR_INTERN___STING(kwargs)
    CREATE_VAR_INTERN___STING(write)
    CREATE_VAR_INTERN___STING(value)
    CREATE_VAR_INTERN___STING(read)
    CREATE_VAR_INTERN___STING(args)
    CREATE_VAR_INTERN___STING(int)

    get_hash_bytes = PyHash_GetFuncDef()->hash;
    Long_Zero = PyLong_FromSsize_t(0);
    if (!Long_Zero) {
        return -1;
    }

    Long_One = PyLong_FromSsize_t(1);
    if (!Long_One) {
        return -1;
    }

    Long_Four = PyLong_FromSsize_t(4);
    if (!Long_Four) {
        return -1;
    }

    VoidTuple = PyTuple_New(0);
    if (!VoidTuple) {
        return -1;
    }

    VoidDict = _PyDict_NewPresized(0);
    if (!VoidDict) {
        return -1;
    }

    __sep_and__ = PyUnicode_InternFromString("' and '");
    if (!__sep_and__) {
        return -1;
    }
    return 0;
}

void
utils_common_free(void)
{
    Py_DECREF(VoidSet);
    Py_DECREF(VoidDict);
    Py_DECREF(__int);
    Py_DECREF(__new__);
    Py_DECREF(__init__);
    Py_DECREF(__copy__);
    Py_DECREF(__dict__);
    Py_DECREF(__return);
    Py_DECREF(_missing_);
    Py_DECREF(__is_safe);
    Py_DECREF(__slots__);
    Py_DECREF(Long_Zero);
    Py_DECREF(Long_One);
    Py_DECREF(Long_Four);
    Py_DECREF(VoidTuple);
    Py_DECREF(__config__);
    Py_DECREF(__as_dict__);
    Py_DECREF(__weakref__);
    Py_DECREF(__sep_and__);
    Py_DECREF(__as_json__);
    Py_DECREF(__utcoffset);
    Py_DECREF(__post_init__);
    Py_DECREF(__annotations__);
    Py_DECREF(__type_params__);
    Py_DECREF(__instancecheck__);
    Py_DECREF(__default_factory);
    Py_DECREF(_value2member_map_);
    Py_DECREF(__required_keys__);
    Py_DECREF(__constraints__);
    Py_DECREF(__reduce_ex__);
    Py_DECREF(__description);
    Py_DECREF(__setstate__);
    Py_DECREF(__metadata__);
    Py_DECREF(__isoformat);
    Py_DECREF(__reduce__);
    Py_DECREF(__origin__);
    Py_DECREF(__module__);
    Py_DECREF(__args__);
    Py_DECREF(__bound__);
    Py_DECREF(__exclude);
    Py_DECREF(__include);
    Py_DECREF(__append);
    Py_DECREF(__kwargs);
    Py_DECREF(__value);
    Py_DECREF(__write);
    Py_DECREF(__read);
    Py_DECREF(__args);
}