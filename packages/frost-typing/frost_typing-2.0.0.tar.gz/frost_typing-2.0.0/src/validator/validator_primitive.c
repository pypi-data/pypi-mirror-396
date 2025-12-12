#include "field.h"
#include "limits.h"
#include "meta_valid_model.h"
#include "valid_model.h"
#include "validator/validator.h"
#include "validator/validator_uuid.h"

static PyObject* base_instan;

static PyObject*
converter_bytes(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (FT_UNLIKELY(ctx->flags & FIELD_STRICT)) {
        return NULL;
    }

    if (PyUnicode_Check(val)) {
        return PyUnicode_AsUTF8String(val);
    }

    if (PyByteArray_Check(val)) {
        return PyBytes_FromObject(val);
    }
    return NULL;
}

static PyObject*
converter_bytearray(UNUSED TypeAdapter* self,
                    ValidateContext* ctx,
                    PyObject* val)
{
    if (FT_UNLIKELY(ctx->flags & FIELD_STRICT)) {
        return NULL;
    }

    if (PyUnicode_Check(val)) {
        val = PyUnicode_AsUTF8String(val);
        if (val == NULL) {
            return NULL;
        }
        PyObject* res = PyByteArray_FromObject(val);
        Py_DECREF(val);
        return res;
    }
    if (PyBytes_Check(val)) {
        return PyByteArray_FromObject(val);
    }
    return NULL;
}

static PyObject*
converter_primitive(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (FT_UNLIKELY(ctx->flags & FIELD_STRICT)) {
        return NULL;
    }

    PyObject* res = PyObject_CallOneArg(self->cls, val);
    if (!res) {
        ValidationError_ExceptionHandling(ctx->model, val);
    }
    return res;
}

static PyObject*
converter_frost_validate(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    PyObject* res = PyObject_CallTwoArg(self->args, val, (PyObject*)ctx->ctx);
    if (!res) {
        ValidationError_ExceptionHandling(ctx->model, val);
    }
    return res;
}

static PyObject*
converter_frost_validate_valid_model(TypeAdapter* self,
                                     ValidateContext* ctx,
                                     PyObject* val)
{
    return _ValidModel_FrostValidate((PyTypeObject*)self->cls, val, ctx->ctx);
}

static PyObject*
converter_frost_validate_ctx_manager(TypeAdapter* self,
                                     ValidateContext* ctx,
                                     PyObject* val)
{
    return _ContextManager_FrostValidate(
      (ContextManager*)self->cls, val, ctx->ctx);
}

static PyObject*
converter_none(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (FT_UNLIKELY(ctx->flags & FIELD_STRICT)) {
        return NULL;
    }
    return EqString(val, "null", 4) == 1 ? Py_NewRef(Py_None) : NULL;
}

static PyObject*
converter_long(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (FT_UNLIKELY(ctx->flags & FIELD_STRICT)) {
        return NULL;
    }

    if (PyUnicode_Check(val)) {
        PyObject* res = PyLong_FromUnicodeObject(val, 10);
        if (!res) {
            PyErr_Clear();
        }
        return res;
    }

    if (PyBytes_Check(val) || PyByteArray_Check(val)) {
        const char* s;
        if (PyBytes_Check(val)) {
            s = PyBytes_AS_STRING(val);
        } else {
            s = PyByteArray_AS_STRING(val);
        }

        char* end = NULL;
        PyObject* res = PyLong_FromString(s, &end, 10);
        if (res && end == s + Py_SIZE(val)) {
            return res;
        }

        PyErr_Clear();
        Py_XDECREF(res);
        return NULL;
    }

    PyNumberMethods* m = Py_TYPE(val)->tp_as_number;
    if (m && m->nb_int) {
        PyObject* res = m->nb_int(val);
        if (res && PyLong_CheckExact(res)) {
            return res;
        }
        PyErr_Clear();
        Py_XDECREF(res);
        return NULL;
    }
    return NULL;
}

static PyObject*
converter_float_nested(UNUSED TypeAdapter* self,
                       ValidateContext* ctx,
                       PyObject* val)
{
    if (Py_IS_TYPE(val, &PyFloat_Type)) {
        return Py_NewRef(val);
    }

    if (FT_UNLIKELY(ctx->flags & FIELD_STRICT)) {
        return NULL;
    }

    if (PyUnicode_Check(val) || PyBytes_Check(val) || PyByteArray_Check(val)) {
        PyObject* res = PyFloat_FromString(val);
        if (FT_UNLIKELY(!res)) {
            PyErr_Clear();
        }
        return res;
    }

    PyNumberMethods* m = Py_TYPE(val)->tp_as_number;
    if (m && m->nb_float) {
        PyObject* res = m->nb_float(val);
        if (res && PyFloat_CheckExact(res)) {
            return res;
        }
        PyErr_Clear();
        Py_DECREF(res);
    }
    return NULL;
}

static inline PyObject*
float_check_allow_inf_nan(ValidateContext* ctx, PyObject* val)
{
    if (!(ctx->flags & FIELD_ALLOW_INF_NAN)) {
        double d = PyFloat_AS_DOUBLE(val);
        if (!isfinite(d)) {
            return NULL;
        }
    }
    return Py_NewRef(val);
}

static PyObject*
converter_float(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    PyObject* res = converter_float_nested(self, ctx, val);
    if (!res) {
        return NULL;
    }

    val = float_check_allow_inf_nan(ctx, res);
    Py_DECREF(res);
    return val;
}

static PyObject*
converter_enum(TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (FT_UNLIKELY((ctx->flags & FIELD_STRICT))) {
        return NULL;
    }

    PyObject* res = PyObject_CheckHashable(val)
                      ? PyDict_GetItemWithError(self->args, val)
                      : NULL;
    if (FT_LIKELY(res)) {
        return Py_NewRef(res);
    }

    PyErr_Clear();
    res = PyObject_CallMethodOneArg(self->cls, _missing_, val);
    if (FT_LIKELY(res && Py_IS_TYPE(res, (PyTypeObject*)self->cls))) {
        return res;
    }

    Py_XDECREF(res);
    return NULL;
}

static inline TypeAdapter*
validator_create_enum(PyObject* hint)
{
    PyObject* args = PyTyping_Get__value2member_map_(hint);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }
    TypeAdapter* res = TypeAdapter_Create(hint,
                                          args,
                                          NULL,
                                          TypeAdapter_Base_Repr,
                                          converter_enum,
                                          Inspector_IsType,
                                          NULL);
    Py_DECREF(args);
    return res;
}

static inline TypeAdapter*
validator_create_frost_validate(PyObject* hint)
{
    PyObject* args = PyObject_GetAttr(hint, __frost_validate__);
    if (FT_UNLIKELY(!args)) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyCallable_Check(args))) {
        _RaiseInvalidType(
          "__frost_validate__", "callable", Py_TYPE(args)->tp_name);
        Py_DECREF(args);
        return NULL;
    }

    TypeAdapter* res = TypeAdapter_Create(hint,
                                          args,
                                          NULL,
                                          TypeAdapter_Base_Repr,
                                          converter_frost_validate,
                                          Inspector_No,
                                          NULL);
    Py_DECREF(args);
    return res;
}

static inline Inspector
type_adapter_get_incp(PyObject* hint)
{
    if (!PyType_Check(hint)) {
        return Inspector_IsInstance;
    }

    PyObject* tmp = _Object_Gettr((PyObject*)Py_TYPE(hint), __instancecheck__);
    if (!tmp) {
        return Inspector_IsInstance;
    }

    Inspector incp =
      base_instan == tmp ? Inspector_IsType : Inspector_IsInstance;
    Py_DECREF(tmp);
    return incp;
}

TypeAdapter*
TypeAdapter_Create_Primitive(PyObject* hint)
{
    if (((PyTypeObject*)hint) == &PyUnicode_Type) {
        return TypeAdapter_Create_Str(hint);
    } else if (((PyTypeObject*)hint) == &PyBool_Type) {
        return TypeAdapter_Create_Bool(hint);
    } else if (((PyTypeObject*)hint) == PyNone_Type) {
        return TypeAdapter_Create(hint,
                                  NULL,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  converter_none,
                                  Inspector_IsType,
                                  NULL);
    } else if (ContextManager_Check(hint)) {
        return TypeAdapter_Create(hint,
                                  NULL,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  converter_frost_validate_ctx_manager,
                                  Inspector_No,
                                  _JsonValidParse_ContextManager);
    } else if (PyType_Check(hint) && MetaValid_IS_SUBCLASS(hint) &&
               ValidModelType.__frost_validate__ ==
                 _CAST(MetaValidModel*, hint)->__frost_validate__) {
        return TypeAdapter_Create(hint,
                                  NULL,
                                  NULL,
                                  TypeAdapter_Base_Repr,
                                  converter_frost_validate_valid_model,
                                  Inspector_No,
                                  _JsonValidParse_ValidModel);
    } else if (PyObject_HasAttr(hint, __frost_validate__)) {
        return validator_create_frost_validate(hint);
    } else if (PyType_Check(hint)) {
        if (PyType_IsSubtype((PyTypeObject*)hint, (PyTypeObject*)PyEnumType)) {
            return validator_create_enum(hint);
        }
        if (PyType_IsSubtype((PyTypeObject*)hint, PyUuidType)) {
            return TypeAdapter_Create_Uuid(hint);
        }
    }

    Converter conv;
    Inspector insp = Inspector_IsType;
    PyTypeObject* type = (PyTypeObject*)hint;

    if (type == &PyBytes_Type) {
        conv = converter_bytes;
    } else if (type == &PyByteArray_Type) {
        conv = converter_bytearray;
    } else if (type == &PyFloat_Type) {
        conv = converter_float;
        insp = Inspector_No;
    } else if (type == &PyLong_Type) {
        conv = converter_long;
    } else {
        insp = type_adapter_get_incp(hint);
        conv = converter_primitive;
    }

    return TypeAdapter_Create(
      hint, NULL, NULL, TypeAdapter_Base_Repr, conv, insp, NULL);
}

int
validator_primitive_setup(void)
{
    base_instan = PyObject_GetAttr((PyObject*)&PyType_Type, __instancecheck__);
    if (!base_instan) {
        return -1;
    }
    if (validator_uuid_setup() < 0) {
        return -1;
    }
    return date_time_setup();
}

void
validator_primitive_free(void)
{
    Py_DECREF(base_instan);
    validator_uuid_free();
    date_time_free();
}