#include "validator/validator.h"

#include "datetime.h"

static PyObject *__AwareDatetime, *__NaiveDatetime, *__PastDatetime,
  *__FutureDatetime, *__timezone_aware, *__timezone_naive, *__past, *__now,
  *__future;
PyObject* AwareDatetime;  // has a tz
PyObject* NaiveDatetime;  // does not have a tz
PyObject* PastDatetime;   // the past
PyObject* FutureDatetime; // the future

static PyObject*
datetime_constraints_repr(DateTimeConstraints* self)
{
    switch (self->flags) {
        case DateTimeConstraints_AWARE:
            return Py_NewRef(__AwareDatetime);
        case DateTimeConstraints_NAIVE:
            return Py_NewRef(__NaiveDatetime);
        case DateTimeConstraints_PAST:
            return Py_NewRef(__PastDatetime);
        default:
            return Py_NewRef(__FutureDatetime);
    }
}

static PyObject*
datetime_constraints_richcompare(PyObject* self, PyObject* other, int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    if (self == other) {
        return Py_NewRef(op == Py_EQ ? Py_True : Py_False);
    }
    return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
}

static Py_hash_t
datetime_constraints_hash(PyObject* self)
{
    return (Py_hash_t)self;
}

PyTypeObject DateTimeConstraintsType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "frost_typing.DateTimeConstraints",
    .tp_richcompare = (richcmpfunc)datetime_constraints_richcompare,
    .tp_repr = (reprfunc)datetime_constraints_repr,
    .tp_hash = (hashfunc)datetime_constraints_hash,
    .tp_basicsize = sizeof(DateTimeConstraints),
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

int
datetime_constraint_setup(void)
{
    if (PyType_Ready(&DateTimeConstraintsType) < 0) {
        return -1;
    }

    PyDateTime_IMPORT;
    if (FT_UNLIKELY(!PyDateTimeAPI)) {
        return -1;
    }

    AwareDatetime = _PyObject_New(&DateTimeConstraintsType);
    if (FT_UNLIKELY(!AwareDatetime)) {
        return -1;
    }

    NaiveDatetime = _PyObject_New(&DateTimeConstraintsType);
    if (FT_UNLIKELY(!AwareDatetime)) {
        return -1;
    }

    PastDatetime = _PyObject_New(&DateTimeConstraintsType);
    if (FT_UNLIKELY(!AwareDatetime)) {
        return -1;
    }

    FutureDatetime = _PyObject_New(&DateTimeConstraintsType);
    if (FT_UNLIKELY(!AwareDatetime)) {
        return -1;
    }

    _CAST(DateTimeConstraints*, AwareDatetime)->flags =
      DateTimeConstraints_AWARE;
    _CAST(DateTimeConstraints*, NaiveDatetime)->flags =
      DateTimeConstraints_NAIVE;
    _CAST(DateTimeConstraints*, PastDatetime)->flags = DateTimeConstraints_PAST;
    _CAST(DateTimeConstraints*, FutureDatetime)->flags =
      DateTimeConstraints_FUTURE;

    CREATE_VAR_INTERN___STING(AwareDatetime);
    CREATE_VAR_INTERN___STING(NaiveDatetime);
    CREATE_VAR_INTERN___STING(PastDatetime);
    CREATE_VAR_INTERN___STING(FutureDatetime);
    CREATE_VAR_INTERN___STING(timezone_aware);
    CREATE_VAR_INTERN___STING(timezone_naive);
    CREATE_VAR_INTERN___STING(future);
    CREATE_VAR_INTERN___STING(past);
    CREATE_VAR_INTERN___STING(now);
    return 0;
}

void
datetime_constraint_free(void)
{
    Py_DECREF(AwareDatetime);
    Py_DECREF(NaiveDatetime);
    Py_DECREF(PastDatetime);
    Py_DECREF(FutureDatetime);
    Py_DECREF(__AwareDatetime);
    Py_DECREF(__NaiveDatetime);
    Py_DECREF(__PastDatetime);
    Py_DECREF(__FutureDatetime);
    Py_DECREF(__timezone_aware);
    Py_DECREF(__timezone_naive);
    Py_DECREF(__future);
    Py_DECREF(__past);
    Py_DECREF(__now);
}

static PyObject*
datetime_get_tz(PyObject* dt)
{
    if (_CAST(_PyDateTime_BaseTime*, dt)->hastzinfo) {
        PyObject* tz = _CAST(PyDateTime_DateTime*, dt)->tzinfo;
        return !tz ? Py_None : tz;
    }
    return Py_None;
}

static int
datetime_check_current(PyObject* dt, int flag)
{
    PyObject* tz = datetime_get_tz(dt);
    PyObject* now = PyObject_CallMethodOneArg(
      (PyObject*)PyDateTimeAPI->DateTimeType, __now, tz);
    if (!now) {
        return 0;
    }

    int r = PyObject_RichCompareBool(now, dt, flag);
    Py_DECREF(now);
    return r == 1;
}

PyObject*
DateTime_Converter(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    PyObject* res = TypeAdapter_Conversion((TypeAdapter*)self->cls, ctx, val);
    if (!res) {
        return NULL;
    }

    if (PyObject_TypeCheck(Py_TYPE(res), PyDateTimeAPI->DateTimeType)) {
        Py_DECREF(res);
        return NULL;
    }

    DateTimeConstraints* con = (DateTimeConstraints*)self->args;
    switch (con->flags) {
        case DateTimeConstraints_AWARE:
            if (datetime_get_tz(res) != Py_None) {
                return res;
            }

            ValidationError_RaiseFormat("Input should have timezone info",
                                        NULL,
                                        __timezone_aware,
                                        val,
                                        ctx->model);
            Py_DECREF(res);
            return NULL;

        case DateTimeConstraints_NAIVE:
            if (datetime_get_tz(res) == Py_None) {
                return res;
            }

            ValidationError_RaiseFormat("Input should not have timezone info",
                                        NULL,
                                        __timezone_naive,
                                        val,
                                        ctx->model);
            Py_DECREF(res);
            return NULL;

        case DateTimeConstraints_PAST:
            if (datetime_check_current(res, Py_GT)) {
                return res;
            }

            ValidationError_RaiseFormat(
              "Input should be in the past", NULL, __past, val, ctx->model);
            Py_DECREF(res);
            return NULL;

        default:
            if (datetime_check_current(res, Py_LT)) {
                return res;
            }

            ValidationError_RaiseFormat(
              "Input should be in the future", NULL, __future, val, ctx->model);
            Py_DECREF(res);
            return NULL;
    }
}