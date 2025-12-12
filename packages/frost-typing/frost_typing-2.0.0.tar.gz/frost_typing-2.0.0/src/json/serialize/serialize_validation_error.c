#include "convector.h"
#include "validator/validator.h"
#include "json/json.h"

static int
validation_error_as_json_nested(WriteBuffer* buff,
                                ValidationError* obj,
                                ConvParams* params)
{
    if (FT_UNLIKELY(!_Convector_Enter(params))) {
        return -1;
    }

    BUFFER_CONCAT_SIZE(buff, "{\"type\":", 8);
    if (FT_UNLIKELY(_PyObject_AsJson(buff, obj->type, params) < 0)) {
        return -1;
    }

    BUFFER_CONCAT_SIZE(buff, ",\"loc\":", 7);
    if (FT_UNLIKELY(_PyObject_AsJson(buff, obj->attrs, params) < 0)) {
        return -1;
    }

    BUFFER_CONCAT_SIZE(buff, ",\"input\":", 9);
    if (FT_UNLIKELY(_PyObject_AsJson(buff, obj->input_value, params) < 0)) {
        return -1;
    }

    BUFFER_CONCAT_SIZE(buff, ",\"msg\":", 7);
    if (FT_UNLIKELY(_PyObject_AsJson(buff, obj->msg, params) < 0)) {
        return -1;
    }

    buff->buffer[buff->size++] = '}';
    _Convector_Leave(params);
    return 0;
}

int
_ValidationError_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    ValidationError* self = (ValidationError*)obj;
    BUFFER_CONCAT_CHAR(buff, '[');
    for (;;) {
        if (FT_UNLIKELY(validation_error_as_json_nested(buff, self, params) <
                        0)) {
            return -1;
        }

        self = self->next;
        if (self) {
            buff->buffer[buff->size++] = ',';
        } else {
            break;
        }
    }

    buff->buffer[buff->size++] = ']';
    return 0;
}