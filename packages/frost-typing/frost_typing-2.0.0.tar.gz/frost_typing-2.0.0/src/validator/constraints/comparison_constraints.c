#include "validator/validator.h"

#include "structmember.h"

#define _ConComparison_ITEMS(con)                                              \
    GET_ADDR(con, offsetof(ComparisonConstraints, gt))

#define _ConComparisonForeach(v, con, ...)                                     \
    for (PyObject** __##v = _ConComparison_ITEMS(con),                         \
                    ** __end_##v =                                             \
                      GET_ADDR(__##v,                                          \
                               sizeof(ComparisonConstraints) -                 \
                                 offsetof(ComparisonConstraints, gt)),         \
                    *v = *__##v;                                               \
         __##v != __end_##v;                                                   \
         v = *++__##v, ##__VA_ARGS__)

static PyObject *__greater_than, *__greater_than_equal, *__less_than,
  *__less_than_equal;

static PyObject*
comparison_constraints_repr(ComparisonConstraints* self)
{
    return PyUnicode_FromFormat("ComparisonConstraints(gt=%.100R, "
                                "ge=%.100R, lt=%.100R, le=%.100R)",
                                self->gt ? self->gt : Py_None,
                                self->ge ? self->ge : Py_None,
                                self->lt ? self->lt : Py_None,
                                self->le ? self->le : Py_None);
}

static PyObject*
comparison_constraints_new(PyTypeObject* type, PyObject* args, PyObject* kwargs)
{
    PyObject *gt, *ge, *lt, *le;
    gt = ge = lt = le = NULL;
    char* kwlist[] = { "gt", "ge", "lt", "le", NULL };
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "|OOOO:ComparisonConstraints.__new__",
                                     kwlist,
                                     &gt,
                                     &ge,
                                     &lt,
                                     &le)) {
        return NULL;
    }
    PyObject* self = type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    ComparisonConstraints* this = (ComparisonConstraints*)self;
    this->gt = Py_XNewRef(gt);
    this->ge = Py_XNewRef(ge);
    this->lt = Py_XNewRef(lt);
    this->le = Py_XNewRef(le);
    return self;
}

static void
comparison_constraints_dealloc(ComparisonConstraints* self)
{
    Py_XDECREF(self->gt);
    Py_XDECREF(self->ge);
    Py_XDECREF(self->lt);
    Py_XDECREF(self->le);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
comparison_constraints_richcompare(PyObject* self, PyObject* other, int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    if (Py_TYPE(self) != Py_TYPE(other)) {
        return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
    }

    PyObject** o = _ConComparison_ITEMS(other);
    _ConComparisonForeach(val, self, o++)
    {
        int r = Object_EqualAllowNull(val, *o);
        if (FT_UNLIKELY(r < 0)) {
            return NULL;
        }
        if (!r) {
            return Py_NewRef(op == Py_EQ ? Py_False : Py_True);
        }
    }
    return Py_NewRef(op == Py_EQ ? Py_True : Py_False);
}

static PyMemberDef comparison_constraints_members[] = {
    { "gt", T_OBJECT, offsetof(ComparisonConstraints, gt), READONLY, NULL },
    { "ge", T_OBJECT, offsetof(ComparisonConstraints, ge), READONLY, NULL },
    { "lt", T_OBJECT, offsetof(ComparisonConstraints, lt), READONLY, NULL },
    { "le", T_OBJECT, offsetof(ComparisonConstraints, le), READONLY, NULL },
    { NULL }
};

PyTypeObject ComparisonConstraintsType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_basicsize = sizeof(ComparisonConstraints),
    .tp_richcompare = (richcmpfunc)comparison_constraints_richcompare,
    .tp_dealloc = (destructor)comparison_constraints_dealloc,
    .tp_repr = (reprfunc)comparison_constraints_repr,
    .tp_name = "frost_typing.ComparisonConstraints",
    .tp_members = comparison_constraints_members,
    .tp_new = comparison_constraints_new,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

PyObject*
ComparisonConstraints_Converter(TypeAdapter* validator,
                                ValidateContext* ctx,
                                PyObject* val)
{
    val = TypeAdapter_Conversion((TypeAdapter*)validator->cls, ctx, val);
    if (!val) {
        return NULL;
    }

    int r;
    ComparisonConstraints* con = (ComparisonConstraints*)validator->args;
    if (con->gt) {
        r = PyObject_RichCompareBool(val, con->gt, Py_GT);
        if (r != 1) {
            ValidationError_RaiseFormat("Input should be greater than %R",
                                        NULL,
                                        __greater_than,
                                        val,
                                        ctx->model,
                                        con->gt);
            goto error;
        }
    }
    if (con->ge) {
        r = PyObject_RichCompareBool(val, con->ge, Py_GE);
        if (r != 1) {
            ValidationError_RaiseFormat("Input should be greater "
                                        "than or equal to %R",
                                        NULL,
                                        __greater_than_equal,
                                        val,
                                        ctx->model,
                                        con->ge);
            goto error;
        }
    }
    if (con->lt) {
        r = PyObject_RichCompareBool(val, con->lt, Py_LT);
        if (r != 1) {
            ValidationError_RaiseFormat("Input should be less than %R",
                                        NULL,
                                        __less_than,
                                        val,
                                        ctx->model,
                                        con->lt);
            goto error;
        }
    }
    if (con->le) {
        r = PyObject_RichCompareBool(val, con->le, Py_LE);
        if (r != 1) {
            ValidationError_RaiseFormat("Input should be less "
                                        "than or equal to %R",
                                        NULL,
                                        __less_than_equal,
                                        val,
                                        ctx->model,
                                        con->le);
            goto error;
        }
    }
    return val;

error:
    Py_DECREF(val);
    return NULL;
}

int
comparison_constraint_setup(void)
{
    CREATE_VAR_INTERN___STING(greater_than);
    CREATE_VAR_INTERN___STING(greater_than_equal);
    CREATE_VAR_INTERN___STING(less_than_equal);
    CREATE_VAR_INTERN___STING(less_than);
    return PyType_Ready(&ComparisonConstraintsType);
}

void
comparison_constraint_free(void)
{
    Py_DECREF(__greater_than);
    Py_DECREF(__greater_than_equal);
}