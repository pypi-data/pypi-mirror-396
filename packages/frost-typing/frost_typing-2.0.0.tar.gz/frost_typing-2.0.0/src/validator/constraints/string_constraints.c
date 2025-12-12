#include "validator/validator.h"

#include "structmember.h"

#ifndef T_BOOL
#define T_BOOL Py_T_BOOL
#endif

static PyObject *_re_compile, *__string_pattern_mismatch, *__not_printable_err,
  *__not_ascii_err;
PyObject *__string_too_short, *__string_too_long, *__string_not_printable,
  *__string_not_ascii;

static PyObject*
string_constraint_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    Py_ssize_t min_length, max_length;
    PyObject* pattern_string = NULL;
    PyObject* pattern;
    int strip_whitespace, to_upper, to_lower, is_printable, is_ascii;
    strip_whitespace = to_upper = to_lower = is_printable = is_ascii = 0;
    min_length = max_length = -1;
    pattern = NULL;

    char* kwlist[] = { "strip_whitespace", "to_upper",   "to_lower",
                       "min_length",       "max_length", "pattern",
                       "is_printable",     "is_ascii",   NULL };
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "|pppnnUpp:StringConstraints.__new__",
                                     kwlist,
                                     &strip_whitespace,
                                     &to_upper,
                                     &to_lower,
                                     &min_length,
                                     &max_length,
                                     &pattern_string,
                                     &is_printable,
                                     &is_ascii)) {
        return NULL;
    }

    if (to_upper && to_lower) {
        PyErr_SetString(PyExc_ValueError,
                        "to_upper and to_lower conflict with each other");
        return NULL;
    }

    if (pattern_string != NULL) {
        PyObject* tmp = PyObject_CallOneArg(_re_compile, pattern_string);
        if (FT_UNLIKELY(!tmp)) {
            return NULL;
        }

        pattern = PyObject_GetAttrString(tmp, "match");
        Py_DECREF(tmp);
        if (FT_UNLIKELY(!pattern)) {
            return NULL;
        }
    }
    StringConstraints* self = (StringConstraints*)type->tp_alloc(type, 0);
    if (FT_UNLIKELY(!self)) {
        return NULL;
    }

    self->pattern_string = Py_XNewRef(pattern_string);
    self->strip_whitespace = (char)strip_whitespace;
    self->pattern = (PyMethodObject*)pattern;
    self->is_printable = (char)is_printable;
    self->to_upper = (char)to_upper;
    self->to_lower = (char)to_lower;
    self->is_ascii = (char)is_ascii;
    self->base.min_length = min_length;
    self->base.max_length = max_length;
    return (PyObject*)self;
}

static PyObject*
string_constraint_repr(StringConstraints* self)
{
    return PyUnicode_FromFormat("StringConstraints(strip_whitespace=%S, "
                                "to_upper=%S, to_lower=%S, "
                                "min_length=%zd, max_length=%zd, "
                                "pattern=%R, is_printable=%S, is_ascii=%S)",
                                self->strip_whitespace ? Py_True : Py_False,
                                self->to_upper ? Py_True : Py_False,
                                self->to_lower ? Py_True : Py_False,
                                self->base.min_length,
                                self->base.max_length,
                                self->pattern_string ? self->pattern_string
                                                     : Py_None,
                                self->is_printable ? Py_True : Py_False,
                                self->is_ascii ? Py_True : Py_False);
}

static void
string_constraint_dealloc(StringConstraints* self)
{
    Py_XDECREF(self->pattern_string);
    Py_XDECREF(self->pattern);
    Py_TYPE(self)->tp_free(self);
}

static inline int
eq_string_constraint(StringConstraints* self, StringConstraints* other)
{
    if (Py_TYPE(self) != Py_TYPE(other)) {
        return 0;
    }

    int r = Object_EqualAllowNull((PyObject*)self->pattern,
                                  (PyObject*)other->pattern);
    if (FT_UNLIKELY(r < 0)) {
        return r;
    }
    return r && self->strip_whitespace == other->strip_whitespace &&
           self->is_printable == other->is_printable &&
           self->to_upper == other->to_upper &&
           self->to_lower == other->to_lower &&
           self->is_ascii == other->is_ascii &&
           self->base.min_length == other->base.min_length &&
           self->base.max_length == other->base.max_length;
}

static PyObject*
string_constraint_richcompare(StringConstraints* self,
                              StringConstraints* other,
                              int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    int r = eq_string_constraint(self, other);
    if (FT_UNLIKELY(r < 0)) {
        return NULL;
    }

    if (r) {
        return Py_NewRef(op == Py_EQ ? Py_True : Py_False);
    }
    return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
}

static PyMemberDef string_constraint_members[] = {
    { "pattern",
      T_OBJECT,
      offsetof(StringConstraints, pattern_string),
      READONLY,
      NULL },
    { "strip_whitespace",
      T_BOOL,
      offsetof(StringConstraints, strip_whitespace),
      READONLY,
      NULL },
    { "to_upper",
      T_BOOL,
      offsetof(StringConstraints, to_upper),
      READONLY,
      NULL },
    { "to_lower",
      T_BOOL,
      offsetof(StringConstraints, to_lower),
      READONLY,
      NULL },
    { "is_printable",
      T_BOOL,
      offsetof(StringConstraints, is_printable),
      READONLY,
      NULL },
    { "is_ascii",
      T_BOOL,
      offsetof(StringConstraints, is_ascii),
      READONLY,
      NULL },
    { NULL }
};

PyTypeObject StringConstraintsType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_dealloc =
      (destructor)string_constraint_dealloc,
    .tp_richcompare = (richcmpfunc)string_constraint_richcompare,
    .tp_name = "frost_typing.StringConstraints",
    .tp_repr = (reprfunc)string_constraint_repr,
    .tp_basicsize = sizeof(StringConstraints),
    .tp_members = string_constraint_members,
    .tp_new = string_constraint_new,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

int
string_constraint_setup(void)
{
    CREATE_VAR_INTERN___STING(string_too_long);
    CREATE_VAR_INTERN___STING(string_not_ascii);
    CREATE_VAR_INTERN___STING(string_too_short);
    CREATE_VAR_INTERN___STING(string_not_printable);
    CREATE_VAR_INTERN___STING(string_pattern_mismatch);

    __not_ascii_err =
      PyUnicode_InternFromString("String must contain only ASCII characters");
    if (FT_UNLIKELY(!__not_ascii_err)) {
        return -1;
    }

    __not_printable_err =
      PyUnicode_InternFromString("String contains non-printable characters");
    if (FT_UNLIKELY(!__not_printable_err)) {
        return -1;
    }

    PyObject* re = PyImport_ImportModule("re");
    if (FT_UNLIKELY(!re)) {
        return -1;
    }

    _re_compile = PyObject_GetAttrString(re, "compile");
    Py_DECREF(re);
    if (FT_UNLIKELY(!_re_compile)) {
        return -1;
    }

    StringConstraintsType.tp_base = &SequenceConstraintsType;
    SequenceConstraintsType.tp_flags |= Py_TPFLAGS_BASETYPE;
    int r = PyType_Ready(&StringConstraintsType);
    SequenceConstraintsType.tp_flags &= ~Py_TPFLAGS_BASETYPE;
    return r;
}

void
string_constraint_free(void)
{
    Py_DECREF(_re_compile);
    Py_DECREF(__not_ascii_err);
    Py_DECREF(__string_too_long);
    Py_DECREF(__string_too_short);
    Py_DECREF(__string_not_ascii);
    Py_DECREF(__not_printable_err);
    Py_DECREF(__string_not_printable);
    Py_DECREF(__string_pattern_mismatch);
}

static inline int
unicode_map(int kind,
            const void* data,
            const void* res,
            Py_ssize_t length,
            int is_lower)
{
    Py_ssize_t i;
    for (i = 0; i < length; i++) {
        Py_UCS4 c = PyUnicode_READ(kind, data, i);
        c = is_lower ? _PyUnicode_ToLowercase(c) : _PyUnicode_ToUppercase(c);
        PyUnicode_WRITE(kind, res, i, c);
    }
    return 0;
}

static inline void
unicode_strip_whitespace(int kind,
                         Py_ssize_t length,
                         const void* data,
                         Py_ssize_t* st_ind,
                         Py_ssize_t* end_ind)
{
    Py_ssize_t st_i = 0, end_i = length, i = 0;
    for (; i < length; i++) {
        Py_UCS4 ch = PyUnicode_READ(kind, data, i);
        if (ch != ' ') {
            break;
        }
        st_i++;
    }

    for (Py_ssize_t j = length - 1; j > i; j--) {
        Py_UCS4 ch = PyUnicode_READ(kind, data, j);
        if (ch != ' ') {
            break;
        }
        end_i--;
    }
    *st_ind = st_i;
    *end_ind = end_i;
}

static inline int
scheckis_printable(void* data, int kind, Py_ssize_t length)
{
    for (Py_ssize_t i = 0; i != length; i++) {
        if (!Py_UNICODE_ISPRINTABLE(PyUnicode_READ(kind, data, i))) {
            return 0;
        }
    }
    return 1;
}

static inline PyObject*
str_trim_and_to_case(StringConstraints* con,
                     PyObject* str,
                     ValidateContext* ctx)
{
    if (con->is_ascii && !PyUnicode_IS_ASCII(str)) {
        _ValidationError_Raise(
          __not_ascii_err, NULL, __string_not_ascii, str, ctx->model);
        return NULL;
    }

    if (!con->to_lower && !con->to_upper && !con->strip_whitespace &&
        !con->is_printable) {
        return Py_NewRef(str);
    }

    int kind = PyUnicode_KIND(str);
    void* data = PyUnicode_DATA(str);
    Py_ssize_t length = PyUnicode_GET_LENGTH(str);
    if (con->strip_whitespace) {
        Py_ssize_t st_ind, end_ind;
        unicode_strip_whitespace(kind, length, data, &st_ind, &end_ind);
        if (st_ind != 0 || end_ind != length) {
            data = ((char*)data) + st_ind * kind;
            length = end_ind - st_ind;
        } else if (!con->to_lower && !con->to_upper) {
            if (con->is_printable && !scheckis_printable(data, kind, length)) {
                _ValidationError_Raise(__not_printable_err,
                                       NULL,
                                       __string_not_printable,
                                       str,
                                       ctx->model);
                return NULL;
            }
            return Py_NewRef(str);
        }
    }

    if (con->is_printable && !scheckis_printable(data, kind, length)) {
        _ValidationError_Raise(
          __not_printable_err, NULL, __string_not_printable, str, ctx->model);
        return NULL;
    }

    PyObject* res = PyUnicode_New(length, PyUnicode_MAX_CHAR_VALUE(str));
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    if (con->to_lower || con->to_upper) {
        unicode_map(kind, data, PyUnicode_DATA(res), length, con->to_lower);
    } else {
        memcpy(PyUnicode_DATA(res), data, length * kind);
    }
    return res;
}

PyObject*
StringConstraints_Converter(TypeAdapter* self,
                            ValidateContext* ctx,
                            PyObject* val)
{
    PyObject* tmp = TypeAdapter_Conversion((TypeAdapter*)self->cls, ctx, val);
    if (!tmp) {
        return NULL;
    }

    if (!PyUnicode_Check(tmp)) {
        Py_DECREF(tmp);
        return NULL;
    }

    StringConstraints* con = (StringConstraints*)self->args;
    PyObject* str = str_trim_and_to_case(con, tmp, ctx);
    Py_DECREF(tmp);
    if (!str) {
        return NULL;
    }

    if (_SequenceConstraints_CheckSize(self, ctx, str) < 0) {
        goto error;
    }

    if (con->pattern) {
        PyObject* pattern = PyObject_CallOneArg((PyObject*)con->pattern, str);
        if (!pattern) {
            goto error;
        }
        if (pattern == Py_None) {
            ValidationError_RaiseFormat("String should match pattern '%U'",
                                        NULL,
                                        __string_pattern_mismatch,
                                        str,
                                        ctx->model,
                                        con->pattern_string);
            Py_DECREF(pattern);
            goto error;
        }
        Py_DECREF(pattern);
    }

    val = TypeAdapter_Conversion((TypeAdapter*)self->cls, ctx, str);
    Py_DECREF(str);
    return val;

error:
    Py_DECREF(str);
    return NULL;
}