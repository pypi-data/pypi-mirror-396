#include "validator/validator.h"

PyTypeObject *PyUuidType = NULL, *DecimalType = NULL;
static PyObject *_eval_type, *py_typed_dict_meta, *pye_typed_dict_meta;
PyObject *PyTyping, *PyAnnotated, *PyModules, *PyAny, *PyAbc, *PyEnumType,
  *PySelf, *PyRequired, *PyNotRequired, *PyForwardRef, *Py_AnnotatedAlias,
  *PyTypeVar, *PyUnion, *PyLiteral, *PyGenericAlias, *_GenericAlias,
  *AbcCallable, *PyClassVar, *PySafeUUIDUnknown;

#if PY313_PLUS
PyObject* PyNoDefault = NULL;
#endif

/* ABC */
PyObject *AbcHashable, *AbcIterable, *AbcSequence, *AbcGenerator;

static PyObject*
get_global_by_type(PyObject* obj)
{
    if (!obj) {
        return PyEval_GetGlobals();
    }

    PyObject *module_name, *module, *globals;
    module_name = PyObject_GetAttr((PyObject*)obj, __module__);
    if (FT_UNLIKELY(!module_name)) {
        goto error;
    }

    module = PyDict_GetItemWithError(PyModules, module_name);
    Py_DECREF(module_name);
    if (FT_UNLIKELY(!module)) {
        goto error;
    }

    globals = PyModule_GetDict(module);
    if (FT_UNLIKELY(!globals)) {
        goto error;
    }
    return globals;
error:
    return PyErr_Format(FrostUserError,
                        "Failed to get the namespace of the '%.100s'",
                        ((PyTypeObject*)obj)->tp_name);
}

PyObject*
PyTyping_Eval(PyObject* code, PyTypeObject* tp)
{
    PyObject *globals, *locals, *co, *res;
    globals = get_global_by_type((PyObject*)tp);
    if (FT_UNLIKELY(!globals)) {
        return NULL;
    }

    locals = tp ? tp->tp_dict : PyEval_GetLocals();
    if (FT_UNLIKELY(!locals)) {
        return NULL;
    }

    const char* cmd = PyUnicode_AsUTF8(code);
    if (FT_UNLIKELY(!cmd)) {
        return PyErr_Format(
          PyExc_ValueError, "Failed to recognize '%.100U'", code);
    }

    co = Py_CompileString(cmd, "tmp", Py_eval_input);
    if (!co) {
        return PyErr_Format(
          PyExc_ValueError, "Failed to recognize '%.100U'", code);
    }

    res = PyEval_EvalCode(co, globals, locals);
    Py_DECREF(co);
    return res;
}

PyObject*
PyTyping_Get_RequiredKeys(PyObject* obj)
{
    PyObject* required_keys = PyObject_GetAttr(obj, __required_keys__);
    if (FT_UNLIKELY(!required_keys)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyFrozenSet_Check(required_keys))) {
        _RaiseInvalidType(
          "__required_keys__", "frozenset", Py_TYPE(required_keys)->tp_name);
        Py_DECREF(required_keys);
        return NULL;
    }
    return required_keys;
}

PyObject*
PyTyping_Get_Metadata(PyObject* obj)
{
    PyObject* metadata = PyObject_GetAttr(obj, __metadata__);
    if (FT_UNLIKELY(!metadata)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyTuple_Check(metadata))) {
        _RaiseInvalidType("__metadata__", "tuple", Py_TYPE(metadata)->tp_name);
        Py_DECREF(metadata);
        return NULL;
    }
    return metadata;
}

inline PyObject*
PyTyping_Get_Origin(PyObject* obj)
{
    return _Object_Gettr(obj, __origin__);
}

inline PyObject*
PyEvaluateIfNeeded(PyObject* obj, PyTypeObject* tp)
{
    if (PyUnicode_Check(obj)) {
        return PyTyping_Eval(obj, tp);
    }
    if (Py_IS_TYPE(obj, (PyTypeObject*)PyForwardRef)) {
        return PyTyping_Evaluate_Forward_Ref(obj, tp);
    }
    return Py_NewRef(obj);
}

PyObject*
PyTyping_Get_Bound(PyObject* obj)
{
    PyObject* bound = PyObject_GetAttr(obj, __bound__);
    if (FT_UNLIKELY(!bound)) {
        return NULL;
    }

    PyObject* res = PyEvaluateIfNeeded(bound, NULL);
    Py_DECREF(bound);
    if (!res) {
        return NULL;
    }

    if (res != Py_None && !PyType_Check(res)) {
        _RaiseInvalidType("bound", "type", Py_TYPE(res)->tp_name);
        Py_DECREF(res);
        return NULL;
    }
    return res;
}

PyObject*
PyTyping_Get_Constraints(PyObject* obj)
{
    PyObject* constr = PyObject_GetAttr(obj, __constraints__);
    if (FT_UNLIKELY(!constr)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyTuple_Check(constr))) {
        _RaiseInvalidType("__constraints__", "type", Py_TYPE(constr)->tp_name);
        Py_DECREF(constr);
        return NULL;
    }

    Py_ssize_t size = PyTuple_GET_SIZE(constr);
    PyObject* res = PyTuple_New(size);
    for (Py_ssize_t i = 0; i != size; i++) {
        PyObject* tmp = PyEvaluateIfNeeded(PyTuple_GET_ITEM(constr, i), NULL);
        if (!tmp) {
            Py_DECREF(res);
            return NULL;
        }
        PyTuple_SET_ITEM(res, i, tmp);
    }
    return res;
}

inline int
PyTyping_Is_TypedDict(PyObject* hint)
{
    return Py_IS_TYPE(hint, (PyTypeObject*)py_typed_dict_meta) ||
           Py_IS_TYPE(hint, (PyTypeObject*)pye_typed_dict_meta);
}

int
PyTyping_Is_Origin(PyObject* hint, PyObject* tp)
{
    PyObject* origin = PyTyping_Get_Origin(hint);
    if (!origin) {
        return 0;
    }

    int res = origin == tp;
    Py_DECREF(origin);
    return res;
}

PyObject*
PyTyping_Evaluate_Forward_Ref(PyObject* hint, PyTypeObject* tp)
{
    PyObject *locals, *globals;
    globals = get_global_by_type((PyObject*)tp);
    if (FT_UNLIKELY(!globals)) {
        return NULL;
    }

    locals = tp ? tp->tp_dict : PyEval_GetLocals();
    if (FT_UNLIKELY(!locals)) {
        return NULL;
    }

    PyObject* call_args[5] = { NULL, hint, globals, locals, VoidSet };
    return PyObject_Vectorcall(
      _eval_type, call_args + 1, 4 | PY_VECTORCALL_ARGUMENTS_OFFSET, NULL);
}

PyObject*
PyTyping_Get__value2member_map_(PyObject* obj)
{
    PyObject* res = PyObject_GetAttr(obj, _value2member_map_);
    if (FT_UNLIKELY(res && !PyDict_Check(res))) {
        _RaiseInvalidType("_value2member_map_", "dict", Py_TYPE(res)->tp_name);
        Py_DECREF(res);
        return NULL;
    }

    return res;
}

PyObject*
PyTyping_Get_Args(PyObject* obj)
{
    PyObject* val = PyObject_GetAttr(obj, __args__);
    if (FT_UNLIKELY(val && !PyTuple_CheckExact(val))) {
        PyErr_Format(PyExc_TypeError, "%.100S.__args__ must be a tuple", obj);
        Py_DECREF(val);
        return NULL;
    }
    return val;
}

PyObject*
PyTyping_AnnotatedGetItem(PyObject* hint, PyObject* key)
{
    PyObject* args = PyTuple_Pack(2, hint, key);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }
    PyObject* res = PyObject_GetItem(PyAnnotated, args);
    Py_DECREF(args);
    return res;
}

PyObject*
PyTypedDict_Getannotations(PyObject* hint)
{
    PyObject* res = PyDict_New();
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    PyObject* mro = _CAST(PyTypeObject*, hint)->tp_mro;
    Py_ssize_t ind = PyTuple_GET_SIZE(mro) - 1;

    while (ind != -1) {
        PyObject* base = PyTuple_GET_ITEM(mro, ind--);
        if (!PyTyping_Is_TypedDict(base)) {
            continue;
        }

        PyObject* annot = PyObject_Get_annotations(hint);
        if (!annot) {
            Py_DECREF(res);
            return NULL;
        }

        int r = PyDict_Merge(res, annot, 0);
        Py_DECREF(annot);
        if (r < 0) {
            Py_DECREF(res);
            return NULL;
        }
    }
    return res;
}

int
typing_setup(void)
{
#define _IMPORT(prefix, m, name, r)                                            \
    prefix##name = PyObject_GetAttrString(m, #name);                           \
    if (FT_UNLIKELY(!prefix##name)) {                                          \
        r                                                                      \
    }

#define IMPORT_TYPING(name) _IMPORT(Py, PyTyping, name, return -1;)
#define OPTIONAL_IMPORT_TYPING(name) _IMPORT(Py, PyTyping, name, PyErr_Clear();)
#define IMPORT_ABC(name) _IMPORT(Abc, PyAbc, name, return -1;)

    PyObject* m_enum = PyImport_ImportModule("enum");
    if (!m_enum) {
        return -1;
    }

    PyEnumType = PyObject_GetAttrString(m_enum, "Enum");
    Py_DECREF(m_enum);
    if (!PyEnumType) {
        return -1;
    }

    PyAbc = PyImport_ImportModule("collections.abc");
    if (!PyAbc) {
        return -1;
    }

    PyObject* sys = PyImport_ImportModule("sys");
    if (!sys) {
        return -1;
    }

    PyModules = PyObject_GetAttrString(sys, "modules");
    Py_DECREF(sys);
    if (!PyModules) {
        return -1;
    }

    PyTyping = PyImport_ImportModule("typing");
    if (!PyTyping) {
        return -1;
    }

    IMPORT_TYPING(Any);
    IMPORT_TYPING(Union);
    IMPORT_TYPING(TypeVar);
    IMPORT_TYPING(Literal);
    IMPORT_TYPING(ClassVar);
    IMPORT_TYPING(Annotated);
    IMPORT_TYPING(Annotated);
    IMPORT_TYPING(ForwardRef);
    IMPORT_TYPING(GenericAlias);
    IMPORT_TYPING(_AnnotatedAlias);
#if PY313_PLUS
    IMPORT_TYPING(NoDefault)
#endif
    OPTIONAL_IMPORT_TYPING(NotRequired);
    OPTIONAL_IMPORT_TYPING(Required);
    OPTIONAL_IMPORT_TYPING(Self);

    IMPORT_ABC(Generator);
    IMPORT_ABC(Callable);
    IMPORT_ABC(Hashable);
    IMPORT_ABC(Sequence);
    IMPORT_ABC(Iterable);

    py_typed_dict_meta = PyObject_GetAttrString(PyTyping, "_TypedDictMeta");
    if ((!py_typed_dict_meta)) {
        PyErr_Clear();
    }

    _GenericAlias = PyObject_GetAttrString(PyTyping, "_GenericAlias");
    if (!_GenericAlias) {
        return -1;
    }

    _eval_type = PyObject_GetAttrString(PyTyping, "_eval_type");
    if (!_eval_type) {
        return -1;
    }

    PyObject* uuid_module = PyImport_ImportModule("uuid");
    if (!uuid_module) {
        return -1;
    }

    PyObject* tmp = PyObject_GetAttrString(uuid_module, "SafeUUID");
    if (!tmp) {
        Py_DECREF(uuid_module);
        return -1;
    }

    PySafeUUIDUnknown = PyObject_GetAttrString(tmp, "unknown");
    Py_DECREF(tmp);
    if (!PySafeUUIDUnknown) {
        Py_DECREF(uuid_module);
        return -1;
    }

    PyUuidType = (PyTypeObject*)PyObject_GetAttrString(uuid_module, "UUID");
    Py_DECREF(uuid_module);
    if (!PyUuidType) {
        return -1;
    }

    PyObject* decimal_module = PyImport_ImportModule("decimal");
    if (!decimal_module) {
        PyErr_Clear();
    } else {
        DecimalType =
          (PyTypeObject*)PyObject_GetAttrString(decimal_module, "Decimal");
        Py_DECREF(decimal_module);
        if (!DecimalType) {
            return -1;
        }

        if (!PyType_Check(DecimalType)) {
            _RaiseInvalidType("Decimal", "type", Py_TYPE(DecimalType)->tp_name);
            return -1;
        }
    }

    if (!PyType_Check(PyEnumType)) {
        _RaiseInvalidType("Enum", "type", Py_TYPE(PyEnumType)->tp_name);
        return -1;
    }

    if (!PyDict_Check(PyModules)) {
        _RaiseInvalidType("modules", "dict", Py_TYPE(PyModules)->tp_name);
        return -1;
    }

    if (!PyType_Check(AbcGenerator)) {
        _RaiseInvalidType("Generator", "type", Py_TYPE(AbcGenerator)->tp_name);
        return -1;
    }

    if (!PyType_Check(AbcIterable)) {
        _RaiseInvalidType("Iterable", "type", Py_TYPE(AbcIterable)->tp_name);
        return -1;
    }

    if (!PyType_Check(AbcSequence)) {
        _RaiseInvalidType("AbcSequence", "type", Py_TYPE(AbcSequence)->tp_name);
        return -1;
    }

    if (!PyType_Check(AbcGenerator)) {
        _RaiseInvalidType(
          "AbcGenerator", "type", Py_TYPE(AbcGenerator)->tp_name);
        return -1;
    }

    if (!PyType_Check(PyUuidType)) {
        _RaiseInvalidType("UUID", "type", Py_TYPE(PyUuidType)->tp_name);
        return -1;
    }

    PyObject* typing_extensions = PyImport_ImportModule("typing_extensions");
    if (typing_extensions) {
        pye_typed_dict_meta =
          PyObject_GetAttrString(typing_extensions, "_TypedDictMeta");
        Py_DECREF(typing_extensions);
        if (!pye_typed_dict_meta) {
            return -1;
        }

        if (!PyType_Check(pye_typed_dict_meta)) {
            _RaiseInvalidType(
              "_TypedDictMeta", "type", Py_TYPE(pye_typed_dict_meta)->tp_name);
            return -1;
        }
    } else {
        pye_typed_dict_meta = NULL;
        PyErr_Clear();
    }

    return 0;

#undef _IMPORT
#undef IMPORT_ABC
#undef IMPORT_TYPING
}

void
typing_free(void)
{
    Py_DECREF(PyAbc);
    Py_DECREF(PyAny);
    Py_XDECREF(PySelf);
    Py_DECREF(PyUnion);
    Py_DECREF(PyTyping);
    Py_DECREF(PyLiteral);
    Py_DECREF(PyTypeVar);
    Py_DECREF(PyModules);
    Py_DECREF(_eval_type);
    Py_DECREF(PyUuidType);
    Py_DECREF(PyClassVar);
    Py_DECREF(PyEnumType);
    Py_DECREF(AbcCallable);
    Py_XDECREF(PyRequired);
    Py_DECREF(PyAnnotated);
    Py_DECREF(PyForwardRef);
    Py_DECREF(_GenericAlias);
    Py_XDECREF(PyNotRequired);
    Py_DECREF(PyGenericAlias);
    Py_DECREF(Py_AnnotatedAlias);
    Py_XDECREF(PySafeUUIDUnknown);
    Py_XDECREF(py_typed_dict_meta);
    Py_XDECREF(pye_typed_dict_meta);
    Py_DECREF(AbcGenerator);
    Py_DECREF(AbcHashable);
    Py_DECREF(AbcIterable);
    Py_DECREF(AbcSequence);
#if PY313_PLUS
    Py_DECREF(PyNoDefault);
#endif
}