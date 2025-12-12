#include "stddef.h"
#include "validator/validator.h"

static PyTypeObject HandlerType;

static void
handler_dealloc(Handler* self)
{
    Py_DECREF(self->ctx);
    Py_DECREF(self->data);
    Py_DECREF(self->model);
    Py_DECREF(self->cur_obj);
    Py_DECREF(self->type_adapter);
    Py_TYPE(self)->tp_free(self);
}

static PyObject*
handler_vector_call(Handler* self,
                    PyObject* const* args,
                    Py_ssize_t nargs,
                    PyObject* kwn)
{
    PyObject* val = _VectorCall_GetOneArg("Handler.__call__", args, nargs, kwn);
    if (FT_LIKELY(val)) {
        ValidateContext ctx = ValidateCtx_Create(
          self->ctx, self->cur_obj, self->data, self->model, self->flags);
        return TypeAdapter_Conversion(self->type_adapter, &ctx, val);
    }
    return NULL;
}

PyObject*
Handler_Create(ValidateContext* ctx, TypeAdapter* type_adapter)
{
    Handler* self = Object_New(Handler, &HandlerType);
    if (FT_LIKELY(self)) {
        self->flags = ctx->flags;
        self->data = Py_NewRef(ctx->data);
        self->model = Py_NewRef(ctx->model);
        self->cur_obj = Py_NewRef(ctx->cur_obj);
        self->ctx = (ContextManager*)Py_NewRef(ctx->ctx);
        self->vectorcall = (vectorcallfunc)handler_vector_call;
        self->type_adapter = (TypeAdapter*)Py_NewRef(type_adapter);
    }
    return (PyObject*)self;
}

static PyTypeObject HandlerType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_vectorcall_offset = offsetof(Handler, vectorcall),
    .tp_dealloc = (destructor)handler_dealloc,
    .tp_name = "frost_typing.Handler",
    .tp_basicsize = sizeof(Handler),
};

int
handler_setup(void)
{
    return PyType_Ready(&HandlerType);
}

void
handler_free(void)
{
}