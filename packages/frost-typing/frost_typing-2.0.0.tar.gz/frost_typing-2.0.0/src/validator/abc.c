#include "field.h"
#include "validator/validator.h"

#define ASYNC ((uint32_t)1 << 31)

static PyObject *__send, *__throw, *__close;

TypeAdapter *TypeAdapter_AbcHashable, *TypeAdapter_AbcCallable;

static int
validator_iterable_traverse(ValidatorIterable* self, visitproc visit, void* arg)
{
    Py_VISIT(self->validator);
    Py_VISIT(self->iterator);
    Py_VISIT(self->ctx);
    return 0;
}

static int
validator_iterable_clear(ValidatorIterable* self)
{
    Py_CLEAR(self->validator);
    Py_CLEAR(self->iterator);
    Py_CLEAR(self->ctx);
    return 0;
}

static PyObject*
validator_iterable_repr(ValidatorIterable* self)
{
    return PyUnicode_FromFormat(
      "%s[%.100S]", Py_TYPE(self)->tp_name, self->validator);
}

static PyObject*
validator_iterable_validate(ValidatorIterable* self, PyObject* val)
{
    ValidateContext vctx =
      ValidateCtx_Create(self->ctx, self, self, Py_TYPE(self), self->flags);
    PyObject* res = TypeAdapter_Conversion(self->validator, &vctx, val);
    if (!res) {
        ValidationError_Raise(
          NULL, self->validator, val, (PyObject*)Py_TYPE(self));
    }
    return res;
}

static PyObject*
validator_iterable_next_no_validator(ValidatorIterable* self)
{
    PyObject* item = ObjectIterNext(self->iterator);
    if (item) {
        return item;
    }

    PyObject* val = _StopIteration_GetObject();
    if (!val) {
        return NULL;
    }

    PyObject* res = validator_iterable_validate(self, val);
    Py_DECREF(val);
    if (FT_LIKELY(res)) {
        PyErr_SetObject(PyExc_StopIteration, res);
        Py_DECREF(res);
    }
    return NULL;
}

static PyObject*
validator_iterable_next_iter(ValidatorIterable* self)
{
    PyObject* item;
    int r = _PyIter_GetNext(self->iterator, &item);
    if (r != 1) {
        return NULL;
    }

    PyObject* res = validator_iterable_validate(self, item);
    Py_DECREF(item);
    return res;
}

static PyObject*
validator_iterable_next(ValidatorIterable* self)
{
    if (self->flags | ASYNC) {
        return validator_iterable_next_no_validator(self);
    }
    return validator_iterable_next_iter(self);
}

static PyObject*
validator_iterable_send(ValidatorIterable* self, PyObject* args)
{
    PyObject* res = PyObject_CallMethodOneArg(self->iterator, __send, args);
    if (!res && self->flags | ASYNC) {
        PyObject* item = _StopIteration_GetObject();
        if (item) {
            res = validator_iterable_validate(self, item);
            Py_DECREF(item);
            if (FT_LIKELY(res)) {
                PyErr_SetObject(PyExc_StopIteration, res);
                Py_DECREF(res);
            }
            return NULL;
        }
    }
    return res;
}

static PyObject*
validator_iterable_throw(ValidatorIterable* self,
                         PyObject* const* args,
                         Py_ssize_t nargs,
                         PyObject* kwnames)
{
    PyObject* func = PyObject_GetAttr(self->iterator, __throw);
    if (FT_UNLIKELY(!func)) {
        return NULL;
    }
    PyObject* res = PyObject_Vectorcall(func, args, nargs, kwnames);
    Py_DECREF(func);
    return res;
}

static PyObject*
validator_iterable_close(ValidatorIterable* self)
{
    return PyObject_CallMethodNoArgs(self->iterator, __close);
}

static PyAsyncMethods validator_iterable_async_methods = {
    .am_await = PyObject_SelfIter,
};

static PyMethodDef validator_iterable_methods[] = {
    { "send", PY_METHOD_CAST(validator_iterable_send), METH_O, NULL },
    { "close", PY_METHOD_CAST(validator_iterable_close), METH_NOARGS, NULL },
    { "throw",
      PY_METHOD_CAST(validator_iterable_throw),
      METH_FASTCALL | METH_KEYWORDS,
      NULL },
    { NULL },
};

PyTypeObject ValidatorIterableType = {
    .tp_traverse = (traverseproc)validator_iterable_traverse,
    .tp_iternext = (iternextfunc)validator_iterable_next,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
    .tp_as_async = &validator_iterable_async_methods,
    .tp_clear = (inquiry)validator_iterable_clear,
    .tp_repr = (reprfunc)validator_iterable_repr,
    .tp_name = "frost_typing.ValidatorIterable",
    .tp_dealloc = (destructor)_Object_Dealloc,
    .tp_methods = validator_iterable_methods,
    .tp_basicsize = sizeof(ValidatorIterable),
    .tp_iter = PyObject_SelfIter,
    .tp_free = PyObject_GC_Del,
};

static PyObject*
validator_iterable_create(PyObject* iterator,
                          ContextManager* ctx,
                          TypeAdapter* validator,
                          uint32_t flags)
{
    ValidatorIterable* self =
      Object_New(ValidatorIterable, &ValidatorIterableType);
    if (FT_LIKELY(self)) {
        self->validator = (TypeAdapter*)Py_NewRef(validator);
        self->ctx = (ContextManager*)Py_NewRef(ctx);
        self->iterator = Py_NewRef(iterator);
        self->flags = flags;
    }
    return (PyObject*)self;
}

PyObject*
ValidatorIterable_Create(PyObject* iterable,
                         ValidateContext* ctx,
                         TypeAdapter* validator)
{
    if (!PyObject_CheckIter(iterable)) {
        return NULL;
    }

    PyObject* iterator = PyObject_GetIter(iterable);
    if (FT_UNLIKELY(!iterator)) {
        return NULL;
    }

    PyObject* self =
      validator_iterable_create(iterator, ctx->ctx, validator, ctx->flags);
    Py_DECREF(iterator);
    return self;
}

PyObject*
ValidatorIterable_CreateAsync(PyObject* coroutine,
                              ValidateContext* ctx,
                              TypeAdapter* validator)
{
    PyObject* iterator = _GetAwaitableIter(coroutine);
    if (!iterator) {
        return NULL;
    }

    PyObject* self = validator_iterable_create(
      iterator, ctx->ctx, validator, ctx->flags | ASYNC);
    Py_DECREF(iterator);
    return self;
}

static int
hashable_inspector(UNUSED TypeAdapter* self, PyObject* val)
{
    return PyObject_CheckHashable(val);
}

static int
callable_inspector(UNUSED TypeAdapter* self, PyObject* val)
{
    return PyCallable_Check(val);
}

static int
iterable_inspector(UNUSED TypeAdapter* self, PyObject* val)
{
    return PyObject_CheckIter(val);
}

static PyObject*
iterable_convector(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    return ValidatorIterable_Create(val, ctx, (TypeAdapter*)self->args);
}

static int
sequence_inspector(UNUSED TypeAdapter* self, PyObject* val)
{
    PySequenceMethods* tp_as_sequence = Py_TYPE(val)->tp_as_sequence;
    return tp_as_sequence && tp_as_sequence->sq_length &&
           tp_as_sequence->sq_item;
}

static TypeAdapter*
type_adapter_create_iterable(PyObject* hint, PyObject* tp, PyObject* args)
{
    if (!args) {
        return TypeAdapter_Create(hint,
                                  NULL,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  Not_Converter,
                                  iterable_inspector,
                                  NULL);
    }

    PyObject* vd = (PyObject*)ParseHint(PyTuple_GET_ITEM(args, 0), tp);
    if (!vd) {
        return NULL;
    }

    TypeAdapter* res = _TypeAdapter_NewCollection(
      hint, vd, iterable_convector, _JsonValidParse_List);
    Py_DECREF(vd);
    return res;
}

TypeAdapter*
_TypeAdapter_CreateIterable(PyObject* cls, PyObject* tp, PyObject* args)
{
    if (args && !TypeAdapter_CollectionCheckArgs(args, (PyTypeObject*)cls, 1)) {
        return NULL;
    }
    return type_adapter_create_iterable(cls, tp, args);
}

TypeAdapter*
_TypeAdapter_CreateGenerator(PyObject* tp, PyObject* args)
{
    if (args && !TypeAdapter_CollectionCheckArgs(
                  args, (PyTypeObject*)AbcGenerator, 3)) {
        return NULL;
    }
    return type_adapter_create_iterable(AbcGenerator, tp, args);
}

TypeAdapter*
_TypeAdapter_CreateSequence(PyObject* tp, PyObject* args)
{
    if (!args) {
        return TypeAdapter_Create(AbcSequence,
                                  NULL,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  Not_Converter,
                                  sequence_inspector,
                                  NULL);
    }
    return _TypeAdapter_Create_List(AbcSequence, args, tp);
}

int
abc_setup(void)
{
#define TYPE_ADAPTER_ABC(h, conv, ins)                                         \
    TypeAdapter_##h = TypeAdapter_Create(                                      \
      h, NULL, NULL, TypeAdapter_Base_Repr, conv, ins, NULL);                  \
    if (FT_UNLIKELY(!TypeAdapter_##h)) {                                       \
        return -1;                                                             \
    }

    if (PyType_Ready(&ValidatorIterableType) < 0) {
        return -1;
    }

    CREATE_VAR_INTERN___STING(send);
    CREATE_VAR_INTERN___STING(throw);
    CREATE_VAR_INTERN___STING(close);

    TYPE_ADAPTER_ABC(AbcCallable, Not_Converter, callable_inspector);
    TYPE_ADAPTER_ABC(AbcHashable, Not_Converter, hashable_inspector);

#undef TYPE_ADAPTER_ABC
    return 0;
}

void
abc_free(void)
{
    Py_DECREF(__send);
    Py_DECREF(__throw);
    Py_DECREF(__close);
    Py_DECREF(TypeAdapter_AbcCallable);
    Py_DECREF(TypeAdapter_AbcHashable);
}