#include "convector.h"
#include "structmember.h"
#include "validator/validator.h"
#include "vector_dict.h"
#include "json/json.h"

PyObject *ValidationErrorType, *FrostUserError;
PyObject *__missing_type, *__msg_missing, *__msg, *__type, *__json_invalid_type,
  *__loc, *__input, *__invalid_json, *__value_error;

static int
validation_error_create_format(const char* msg,
                               PyObject* attr,
                               PyObject* err_type,
                               PyObject* val,
                               PyObject* model,
                               ValidationError** activ,
                               ...);

static int
validation_error_clear(ValidationError* self)
{
    Py_CLEAR(self->msg);
    Py_CLEAR(self->type);
    Py_CLEAR(self->next);
    Py_CLEAR(self->attrs);
    Py_CLEAR(self->model);
    Py_CLEAR(self->input_value);
    return Py_TYPE(self)->tp_base->tp_clear((PyObject*)self);
}

static int
validation_error_traverse(ValidationError* self, visitproc visit, void* arg)
{
    Py_VISIT(self->msg);
    Py_VISIT(self->type);
    Py_VISIT(self->next);
    Py_VISIT(self->attrs);
    Py_VISIT(self->model);
    Py_VISIT(self->input_value);
    return Py_TYPE(self)->tp_base->tp_traverse((PyObject*)self, visit, arg);
}

static ValidationError*
validation_error_from_data(PyObject* msg,
                           PyObject* attr,
                           PyObject* e_type,
                           PyObject* model,
                           PyObject* input_value)
{
    ValidationError* self;
    PyObject *attrs, *err_type;

    if (input_value) {
        Py_NewRef(input_value);
    } else {
        input_value = PyDict_New();
        if (FT_UNLIKELY(!input_value)) {
            return NULL;
        }
    }

    if (PyUnicode_CheckExact(e_type)) {
        err_type = Py_NewRef(e_type);
    } else {
        err_type = PyObject_Str(e_type);
        if (FT_UNLIKELY(!err_type)) {
            Py_DECREF(input_value);
            return NULL;
        }
    }

    attrs = PyList_New(attr ? 1 : 0);
    if (FT_UNLIKELY(!attrs)) {
        Py_DECREF(input_value);
        Py_DECREF(err_type);
        return NULL;
    }

    if (attr) {
        PyList_SET_ITEM(attrs, 0, Py_NewRef(attr));
    }

    self = Object_New(ValidationError, &_ValidationErrorType);
    if (FT_UNLIKELY(!self)) {
        Py_DECREF(input_value);
        Py_DECREF(err_type);
        Py_DECREF(attrs);
        return NULL;
    }

    self->attrs = attrs;
    self->type = err_type;
    self->msg = Py_NewRef(msg);
    self->model = Py_NewRef(model);
    self->input_value = input_value;
    _CAST(PyBaseExceptionObject*, self)->args = Py_NewRef(VoidTuple);
    return self;
}

static PyObject*
validation_error_new(PyTypeObject* cls, PyObject* args, PyObject* kwargs)
{
    PyObject *loc, *input_value, *type, *msg, *title, *next = NULL;
    char* kwlist[] = { "loc",   "input_value", "type", "msg",
                       "title", "next_error",  NULL };
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "O!OUUU|O!:ValidationError.__new__",
                                     kwlist,
                                     &PyList_Type,
                                     &loc,
                                     &input_value,
                                     &type,
                                     &msg,
                                     &title,
                                     cls,
                                     &next)) {
        return NULL;
    }

    ValidationError* self = Object_New(ValidationError, cls);
    if (FT_LIKELY(self)) {
        _CAST(PyBaseExceptionObject*, self)->args = Py_NewRef(args);
        self->next = (ValidationError*)Py_XNewRef(next);
        self->input_value = Py_NewRef(input_value);
        self->model = Py_NewRef(title);
        self->attrs = Py_NewRef(loc);
        self->type = Py_NewRef(type);
        self->msg = Py_NewRef(msg);
    }
    return (PyObject*)self;
}

static int
validation_error_repr_nested(ValidationError* self, UnicodeWriter* writer)
{
    PyTypeObject* tp = Py_TYPE(self);
    int r = Py_ReprEnter((PyObject*)self);
    if (r != 0) {
        if (r > 0) {
            _UNICODE_WRITE_STRING(writer, tp->tp_name, -1);
            return UnicodeWriter_WriteASCIIString(writer, "(...)", 5);
        }
        return -1;
    }

    PyObject* val;
    Py_ssize_t size = PyList_GET_SIZE(self->attrs);
    for (Py_ssize_t i = 0; i < size; i++) {
        if (i > 0 && size > 1) {
            _UNICODE_WRITE_CHAR(writer, '.');
        }

        val = PyList_GET_ITEM(self->attrs, i);
        if (PyUnicode_Check(val)) {
            _UNICODE_WRITE_STR(writer, val);
        } else {
            _UNICODE_WRITE(writer, val, PyObject_Str);
        }
    }

    if (size) {
        _UNICODE_WRITE_CHAR(writer, '\n');
    }

    _UNICODE_WRITE_STR(writer, self->msg);
    _UNICODE_WRITE_STRING(writer, " [type=", 7)
    _UNICODE_WRITE_STR(writer, self->type);
    _UNICODE_WRITE_STRING(writer, ", input_value=", 14)
    _UNICODE_WRITE(writer, self->input_value, PyObject_Repr)
    _UNICODE_WRITE_STRING(writer, ", input_type=", 13)
    _UNICODE_WRITE_STRING(writer, Py_TYPE(self->input_value)->tp_name, -1);
    _UNICODE_WRITE_CHAR(writer, ']');
    Py_ReprLeave((PyObject*)self);
    return 0;
error:
    return -1;
}

static Py_ssize_t
validation_error_count_error(ValidationError* self)
{
    Py_ssize_t cnt = 0;
    do {
        cnt += 1;
        self = self->next;
    } while (self);
    return cnt;
}

static PyObject*
validation_error_repr(ValidationError* self)
{
    UnicodeWriter_Create(writer, 64);
    if (!writer) {
        return NULL;
    }

    Py_ssize_t cnt = validation_error_count_error(self);
    _UNICODE_WRITE_SSIZE(writer, cnt);
    _UNICODE_WRITE_STRING(writer, " validation error for ", 22);
    if (_ContextManager_ReprModel(writer, self->model) < 0) {
        goto error;
    }
    _UNICODE_WRITE_CHAR(writer, '\n');

    do {
        if (validation_error_repr_nested(self, writer) < 0) {
            goto error;
        }

        self = self->next;
        if (self) {
            _UNICODE_WRITE_STRING(writer, "\n\n", 2);
        }
    } while (self);

    return UnicodeWriter_Finish(writer);

error:
    UnicodeWriter_Discard(writer);
    return NULL;
}

static PyObject*
validation_error_as_dict(ValidationError* self, ConvParams* params)
{
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(_PyDict_SetItem_Ascii(dict, __type, self->type) < 0)) {
        Py_DECREF(dict);
        return NULL;
    }

    if (FT_UNLIKELY(_PyDict_SetItem_Ascii(dict, __loc, self->attrs) < 0)) {
        Py_DECREF(dict);
        return NULL;
    }

    PyObject* input_value = _Convector_Obj(self->input_value, params);
    if (FT_UNLIKELY(!input_value)) {
        Py_DECREF(dict);
        return NULL;
    }
    if (FT_UNLIKELY(_PyDict_SetItemAsciiDecrefVal(dict, __input, input_value) <
                    0)) {
        Py_DECREF(dict);
        return NULL;
    }

    if (FT_UNLIKELY(_PyDict_SetItem_Ascii(dict, __msg, self->msg) < 0)) {
        Py_DECREF(dict);
        return NULL;
    }
    return dict;
}

static PyObject*
validation_error_as_list_nested(ValidationError* self, ConvParams* params)
{
    PyObject* list = PyList_New(0);
    if (FT_UNLIKELY(!list)) {
        return NULL;
    }

    do {
        if (FT_UNLIKELY(!_Convector_Enter(params))) {
            Py_DECREF(list);
            return NULL;
        }

        PyObject* dict = validation_error_as_dict(self, params);
        _Convector_Leave(params);

        if (FT_UNLIKELY(!dict)) {
            Py_DECREF(list);
            return NULL;
        }

        if (FT_UNLIKELY(_PyList_Append_Decref(list, dict) < 0)) {
            Py_DECREF(list);
            return NULL;
        }
        self = self->next;
    } while (self);
    return list;
}

static PyObject*
validation_error_as_list(ValidationError* self)
{
    ConvParams params = ConvParams_Create(__copy__);
    return validation_error_as_list_nested(self, &params);
}

inline PyObject*
_ValidationError_AsList(PyObject* self, ConvParams* params)
{
    return validation_error_as_list_nested((ValidationError*)self, params);
}

static PyObject*
validation_error_as_json(PyObject* self)
{
    return PyObject_AsJson(&self, 1, NULL, 0);
}

static PyObject*
get_title(ValidationError* self, UNUSED void* _)
{
    if (PyType_Check(self->model)) {
        return PyObject_Get__name__(_CAST(PyTypeObject*, self->model));
    }
    return PyObject_Str(self->model);
}

static PyMethodDef validation_error_methods[] = {
    { "errors", PY_METHOD_CAST(validation_error_as_list), METH_NOARGS, NULL },
    { "as_json", PY_METHOD_CAST(validation_error_as_json), METH_NOARGS, NULL },
    { NULL }
};

static PyMemberDef validation_error_members[] = {
    { "msg", T_OBJECT, offsetof(ValidationError, msg), READONLY, NULL },
    { "loc", T_OBJECT, offsetof(ValidationError, attrs), READONLY, NULL },
    { "type", T_OBJECT, offsetof(ValidationError, type), READONLY, NULL },
    { "next_error", T_OBJECT, offsetof(ValidationError, next), READONLY, NULL },
    { "input_value",
      T_OBJECT,
      offsetof(ValidationError, input_value),
      READONLY,
      NULL },
    { NULL }
};

static PyGetSetDef validation_error_getsets[] = {
    { "title", PY_GETTER_CAST(get_title), NULL, NULL, NULL },
    { NULL }
};

PyTypeObject _ValidationErrorType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags =
      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASE_EXC_SUBCLASS | Py_TPFLAGS_HAVE_GC,
    .tp_traverse = (traverseproc)validation_error_traverse,
    .tp_clear = (inquiry)validation_error_clear,
    .tp_repr = (reprfunc)validation_error_repr,
    .tp_str = (reprfunc)validation_error_repr,
    .tp_dealloc = (destructor)_Object_Dealloc,
    .tp_name = "frost_typing.ValidationError",
    .tp_basicsize = sizeof(ValidationError),
    .tp_methods = validation_error_methods,
    .tp_members = validation_error_members,
    .tp_getset = validation_error_getsets,
    .tp_new = validation_error_new,
    .tp_free = PyObject_GC_Del,
};

static int
validation_error_get_activ(PyObject** res)
{
    PyObject* ex = _Err_GetRaisedException();
    if (!ex) {
        *res = NULL;
        return 0;
    }

    if (PyErr_GivenExceptionMatches(ex, ValidationErrorType)) {
        *res = ex;
        return 1;
    }

    if (PyErr_GivenExceptionMatches(ex, PyExc_ValueError)) {
        *res = ex;
        return 2;
    }

    *res = NULL;
    _Err_SetRaisedException(ex);
    return -1;
}

static void
validation_error_set_nested(ValidationError* self, ValidationError** activ)
{
    ValidationError* current = *activ;
    if (current) {
        while (current->next) {
            current = current->next;
        }
        current->next = self;
    } else {
        *activ = self;
    }
}

static inline int
validation_error_set_nested_attr(ValidationError* self, PyObject* attr)
{
    if (!attr) {
        return 0;
    }

    while (self) {
        if (PyList_Insert(self->attrs, 0, attr) < 0) {
            return -1;
        }
        self = self->next;
    }
    return 0;
}

int
_ValidationErrorSetNested(PyObject* attr,
                          PyObject* val,
                          PyObject* model,
                          ValidationError** err)
{
    ValidationError* activ;
    int r = validation_error_get_activ((PyObject**)&activ);
    if (r < 0) {
        return -1;
    }
    if (!r) {
        return 0;
    }

    if (r == 2) {
        int r = validation_error_create_format(
          "Value error, %S", attr, __value_error, val, model, err, activ);
        Py_DECREF(activ);
        return r < 0 ? r : 1;
    }

    if (validation_error_set_nested_attr(activ, attr) < 0) {
        Py_DECREF(activ);
        return -1;
    }
    validation_error_set_nested(activ, err);
    return 1;
}

inline int
_ValidationErrorSetNestedInd(Py_ssize_t ind,
                             PyObject* model,
                             ValidationError** err)
{
    PyObject* attr = PyLong_FromSsize_t(ind);
    if (!attr) {
        return -1;
    }
    int r = _ValidationErrorSetNested(attr, NULL, model, err);
    Py_DECREF(attr);
    return r;
}

static int
validation_error_create(PyObject* msg,
                        PyObject* attr,
                        PyObject* err_type,
                        PyObject* val,
                        PyObject* model,
                        ValidationError** err)
{
    int r = _ValidationErrorSetNested(attr, val, model, err);
    if (r) {
        return r < 0 ? r : 0;
    }

    ValidationError* self;
    self = validation_error_from_data(msg, attr, err_type, model, val);
    if (!self) {
        return -1;
    }
    validation_error_set_nested(self, err);
    return 0;
}

static int
validation_error_create_formatv(const char* msg,
                                PyObject* attr,
                                PyObject* err_type,
                                PyObject* val,
                                PyObject* model,
                                ValidationError** err,
                                va_list vargs)
{
    int r = _ValidationErrorSetNested(attr, val, model, err);
    if (r) {
        return r < 0 ? r : 0;
    }

    PyObject* s = PyUnicode_FromFormatV(msg, vargs);
    if (!s) {
        return -1;
    }

    ValidationError* self =
      validation_error_from_data(s, attr, err_type, model, val);
    Py_DECREF(s);
    if (!self) {
        return -1;
    }
    validation_error_set_nested(self, err);
    return 0;
}

static int
validation_error_create_format(const char* msg,
                               PyObject* attr,
                               PyObject* err_type,
                               PyObject* val,
                               PyObject* model,
                               ValidationError** activ,
                               ...)
{
    va_list vargs;
    va_start(vargs, activ);
    int r = validation_error_create_formatv(
      msg, attr, err_type, val, model, activ, vargs);
    va_end(vargs);
    return r;
}

int
_ValidationError_Raise(PyObject* msg,
                       PyObject* attr,
                       PyObject* err_type,
                       PyObject* val,
                       PyObject* model)
{
    ValidationError* err = NULL;
    int r = validation_error_create(msg, attr, err_type, val, model, &err);
    if (FT_UNLIKELY(r < 0)) {
        return -1;
    }
    _Err_SetRaisedException((PyObject*)err);
    return 0;
}

int
ValidationError_RaiseFormat(const char* msg,
                            PyObject* attr,
                            PyObject* err_type,
                            PyObject* val,
                            PyObject* model,
                            ...)
{
    va_list vargs;
    ValidationError* err = NULL;
    va_start(vargs, model);
    int r = validation_error_create_formatv(
      msg, attr, err_type, val, model, &err, vargs);
    va_end(vargs);
    if (FT_UNLIKELY(r < 0)) {
        return -1;
    }

    _Err_SetRaisedException((PyObject*)err);
    return 0;
}

int
ValidationError_RaiseInvalidJson(PyObject* val, PyObject* model)
{
    PyObject* ex = _Err_GetRaisedException();
    if (!ex) {
        return _ValidationError_Raise(
          __invalid_json, NULL, __json_invalid_type, val, model);
    }

    if (!PyErr_GivenExceptionMatches(ex, JsonDecodeError)) {
        _Err_SetRaisedException(ex);
        return -1;
    }

    int r = ValidationError_RaiseFormat(
      "Invalid JSON: %S", NULL, __json_invalid_type, val, model, ex);
    Py_XDECREF(ex);
    return r;
}

inline int
ValidationError_Raise(PyObject* attr,
                      TypeAdapter* hint,
                      PyObject* val,
                      PyObject* model)
{
    return _ValidationError_Raise(
      hint->err_msg, attr, (PyObject*)hint, val, model);
}

inline int
ValidationError_Create(PyObject* attr,
                       TypeAdapter* hint,
                       PyObject* val,
                       PyObject* model,
                       ValidationError** activ)
{
    return validation_error_create(
      hint->err_msg, attr, (PyObject*)hint, val, model, activ);
}

inline int
ValidationError_CreateAttrIdx(PyObject* attr,
                              Py_ssize_t ind,
                              TypeAdapter* hint,
                              PyObject* val,
                              PyObject* model,
                              ValidationError** activ)
{
    if (ValidationError_RaiseIndex(ind, hint, val, model) < 0) {
        return -1;
    }
    return ValidationError_Create(attr, hint, val, model, activ);
}

inline int
ValidationError_CreateMissing(PyObject* attr,
                              PyObject* val,
                              PyObject* model,
                              ValidationError** activ)
{
    return validation_error_create(
      __msg_missing, attr, __missing_type, val, model, activ);
}

inline int
ValidationError_RaiseIndex(Py_ssize_t ind,
                           TypeAdapter* hint,
                           PyObject* val,
                           PyObject* model)
{
    PyObject* index = PyLong_FromSsize_t(ind);
    if (FT_UNLIKELY(!index)) {
        return -1;
    }
    int r = ValidationError_Raise(index, hint, val, model);
    Py_DECREF(index);
    return r;
}

inline int
ValidationError_IndexCreate(Py_ssize_t ind,
                            TypeAdapter* hint,
                            PyObject* val,
                            PyObject* model,
                            ValidationError** activ)
{
    PyObject* index = PyLong_FromSsize_t(ind);
    if (FT_UNLIKELY(!index)) {
        return -1;
    }
    int r = ValidationError_Create(index, hint, val, model, activ);
    Py_DECREF(index);
    return r;
}

int
ValidationError_RaiseModelType(PyObject* model, PyObject* val)
{
    PyErr_Clear();
    PyObject* err_type;
    if (PyType_Check(model)) {
        err_type = PyObject_Get__name__(_CAST(PyTypeObject*, model));
    } else {
        err_type = PyObject_Str(model);
    }

    if (FT_UNLIKELY(!err_type)) {
        return -1;
    }

    int r = ValidationError_RaiseFormat(
      "Input should be a valid %U", Long_Zero, err_type, val, model, err_type);
    Py_DECREF(err_type);
    return r;
}

void
ValidationError_RaiseWithModel(ValidationError* err, PyObject* model)
{
    ValidationError* self = err;
    do {
        Py_DECREF(err->model);
        err->model = Py_NewRef(model);
        err = err->next;
    } while (err);

    _Err_SetRaisedException((PyObject*)self);
}

int
ValidationError_ExceptionHandling(PyObject* model, PyObject* val)
{
    PyObject* ex = _Err_GetRaisedException();
    if (!ex) {
        return 0;
    }

    if (PyErr_GivenExceptionMatches(ex, ValidationErrorType)) {
        _Err_SetRaisedException(ex);
        return 0;
    }

    if (PyErr_GivenExceptionMatches(ex, FrostUserError)) {
        _Err_SetRaisedException(ex);
        return -1;
    }

    if (!PyErr_GivenExceptionMatches(ex, PyExc_ValueError)) {
        Py_DECREF(ex);
        return -1;
    }

    int r = ValidationError_RaiseFormat(
      "Value error, %S", NULL, __value_error, val, model, ex);
    Py_DECREF(ex);
    return r;
}

int
validation_error_setup(void)
{
    CREATE_VAR_INTERN___STING(loc);
    CREATE_VAR_INTERN___STING(msg);
    CREATE_VAR_INTERN___STING(type);
    CREATE_VAR_INTERN___STING(input);
    CREATE_VAR_INTERN___STING(value_error);

    __invalid_json = PyUnicode_InternFromString("Invalid JSON");
    if (__invalid_json == NULL) {
        return -1;
    }

    __msg_missing = PyUnicode_InternFromString("Field required");
    if (__msg_missing == NULL) {
        return -1;
    }

    __missing_type = PyUnicode_InternFromString("missing");
    if (__missing_type == NULL) {
        return -1;
    }

    __json_invalid_type = PyUnicode_InternFromString("json_invalid");
    if (__json_invalid_type == NULL) {
        return -1;
    }

    _ValidationErrorType.tp_base = (PyTypeObject*)PyExc_Exception;
    if (PyType_Ready(&_ValidationErrorType) < 0) {
        return -1;
    }

    FrostUserError =
      PyErr_NewException("frost_typing.FrostUserError", PyExc_TypeError, NULL);
    if (!FrostUserError) {
        return -1;
    }

    _ValidationErrorType.tp_init = NULL;
    ValidationErrorType = Py_NewRef((PyObject*)&_ValidationErrorType);
    return 0;
}

void
validation_error_free(void)
{
    Py_DECREF(__loc);
    Py_DECREF(__msg);
    Py_DECREF(__type);
    Py_DECREF(__input);
    Py_DECREF(__value_error);
    Py_DECREF(__msg_missing);
    Py_DECREF(__json_invalid_type);
    Py_DECREF(ValidationErrorType);
    Py_DECREF(__missing_type);
}