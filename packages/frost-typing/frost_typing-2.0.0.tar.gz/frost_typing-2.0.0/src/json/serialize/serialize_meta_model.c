#include "convector.h"
#include "data_model.h"
#include "field.h"
#include "field_serializer.h"
#include "meta_model.h"
#include "utils_common.h"
#include "json/json.h"

static int
meta_model_as_json_call_override(WriteBuffer* buff,
                                 PyObject* obj,
                                 ConvParams* params,
                                 PyObject* as_json)
{
    if (!as_json) {
        PyErr_Format(PyExc_TypeError,
                     "'%.100s' object has no '%U' method",
                     Py_TYPE(obj)->tp_name,
                     __as_json__);
        return -1;
    }

    PyObject* json = _Сonvector_СallFunc(as_json, obj, params);
    return json ? _PyObject_AsJsonDecrefVal(buff, json, params) : -1;
}

static int
meta_model_as_json(WriteBuffer* buff,
                   PyObject* obj,
                   ConvParams* params,
                   PyObject* include,
                   PyObject* exclude)
{
    PyTypeObject* tp = Py_TYPE(obj);
    PyObject* as_json = _CAST_META(tp)->__as_json__;
    if (FT_UNLIKELY(as_json != DataModelType.__as_json__)) {
        return meta_model_as_json_call_override(buff, obj, params, as_json);
    }

    if (FT_UNLIKELY(!_Convector_Enter(params) ||
                    WriteBuffer_ConcatChar(buff, '{') < 0)) {
        return -1;
    }

    uint8_t sep = 0;
    PyObject *val, **slots = DATA_MODEL_GET_SLOTS(obj);

    SchemaForeach(sc, tp, slots++)
    {
        if (FT_UNLIKELY(!IS_FIELD_JSON(sc->field->flags))) {
            continue;
        }

        if (FT_UNLIKELY(exclude)) {
            int r = PySet_Contains(exclude, sc->name);
            if (r < 0) {
                return -1;
            }
            if (r) {
                continue;
            }
        }

        if (FT_UNLIKELY(include)) {
            int r = PySet_Contains(include, sc->name);
            if (r < 0) {
                return -1;
            }
            if (!r) {
                continue;
            }
        }

        int r = _DataModel_Get(sc, slots, obj, &val, params->exclude_unset);
        if (FT_UNLIKELY(r < 0)) {
            return -1;
        } else if (FT_UNLIKELY(!r)) {
            continue;
        } else if (FT_UNLIKELY(params->exclude_none && val == Py_None)) {
            Py_DECREF(val);
            continue;
        }

        if (FT_LIKELY(sep)) {
            buff->buffer[buff->size++] = ',';
        } else {
            sep = 1;
        }

        if (FT_UNLIKELY(params->by_alias &&
                        IF_FIELD_CHECK(sc->field, FIELD_SERIALIZATION_ALIAS))) {
            PyObject* name = Field_GET_SERIALIZATION_ALIAS(sc->field);
            if (FT_UNLIKELY(_Unicode_AsJson(buff, name, params) < 0)) {
                Py_DECREF(val);
                return -1;
            }
        } else if (FT_UNLIKELY(_Unicode_FastAsJson(buff, sc->name) < 0)) {
            Py_DECREF(val);
            return -1;
        }

        buff->buffer[buff->size++] = ':';

        if (FT_UNLIKELY(params->custom_ser &&
                        IF_FIELD_CHECK(sc->field, _FIELD_SERIALIZER))) {
            PyObject* tmp = _FieldSerializer_Call(sc->field, obj, val, params);
            Py_DECREF(val);
            if (!tmp) {
                return -1;
            }
            val = tmp;
        }

        if (FT_UNLIKELY(_PyObject_AsJsonDecrefVal(buff, val, params) < 0)) {
            return -1;
        }
    }

    buff->buffer[buff->size++] = '}';
    _Convector_Leave(params);
    return 0;
}

int
_MetaModel_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    return meta_model_as_json(buff, obj, params, NULL, NULL);
}

PyObject*
_MetaModel_AsJsonCall(PyObject* obj,
                      PyObject* const* args,
                      Py_ssize_t nargsf,
                      PyObject* kwnames)
{
    if (FT_UNLIKELY(
          !PyCheck_ArgsCnt("as_json", PyVectorcall_NARGS(nargsf), 0))) {
        return NULL;
    }

    WriteBuffer buff;
    PyObject* argsbuf[8] = { NULL };
    ConvParams params = ConvParams_Create(__as_json__);
    if (!kwnames) {
        goto done;
    }

    static const char* const kwlist[] = {
        "include",       "exclude",      "by_alias",
        "exclude_unset", "exclude_none", "use_custom",
        "str_unknown",   "context",      NULL,
    };
    static _PyArg_Parser _parser = {
        .keywords = kwlist,
        .fname = "as_json",
        .kwtuple = NULL,
    };

    if (FT_UNLIKELY(!PyArg_UnpackKeywords(args,
                                          0,
                                          NULL,
                                          kwnames,
                                          &_parser,
                                          0, /*minpos*/
                                          0, /*maxpos*/
                                          0, /*minkw*/
                                          argsbuf))) {
        return NULL;
    }

    for (Py_ssize_t i = 2; i != 7; i++) {
        if (FT_UNLIKELY(!_ValidateArg(argsbuf[i], &PyBool_Type, kwlist[i]))) {
            return NULL;
        }
    }

    if (FT_UNLIKELY(_Convector_ValidateInclude(argsbuf, argsbuf + 1) < 0)) {
        return NULL;
    }

    params.by_alias = argsbuf[2] != Py_False;
    params.exclude_unset = argsbuf[3] == Py_True;
    params.exclude_none = argsbuf[4] == Py_True;
    params.custom_ser = argsbuf[5] != Py_False;
    params.str_unknown = argsbuf[6] == Py_True;
    params.context = argsbuf[7];

done:
    if (FT_UNLIKELY(WriteBuffer_init(&buff, NULL) < 0)) {
        return NULL;
    }

    if (FT_UNLIKELY(meta_model_as_json(
                      &buff, obj, &params, argsbuf[0], argsbuf[1]) < 0)) {
        WriteBuffer_Free(&buff);
        _ConvParams_Free(&params);
        return NULL;
    }

    PyObject* res = WriteBuffer_Finish(&buff);
    _ConvParams_Free(&params);
    return res;
}