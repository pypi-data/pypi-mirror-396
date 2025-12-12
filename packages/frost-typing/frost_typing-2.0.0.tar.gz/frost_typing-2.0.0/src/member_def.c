#include "member_def.h"
#include "data_model.h"
#include "field.h"
#include "meta_valid_model.h"
#include "valid_model.h"
#include "validator/validator.h"

#define CACHE_SIZE 10

static PyObject* cache[CACHE_SIZE] = { NULL };

static inline int
member_def_check(Py_ssize_t offset, PyTypeObject* tp)
{
    if (FT_UNLIKELY(!PyType_Check(tp) || !Meta_IS_SUBCLASS(tp) ||
                    tp->tp_basicsize <= offset ||
                    _CAST_META(tp)->slot_offset > offset)) {
        PyErr_SetString(PyExc_TypeError, "Invalid member descriptor");
        return 0;
    }
    return 1;
}

static PyObject*
member_def_descr_get(MemberDef* self, PyObject* obj, MetaModel* type)
{
    const Py_ssize_t offset = self->offset;
    MetaModel* meta = (MetaModel*)obj ? (MetaModel*)Py_TYPE(obj) : type;
    if (FT_UNLIKELY(!member_def_check(offset, (PyTypeObject*)meta))) {
        return NULL;
    }

    Schema* sc = META_GET_SCHEMA_BY_OFFSET(meta, offset - meta->slot_offset);
    if (FT_LIKELY(obj)) {
        PyObject** addr = GET_ADDR(obj, offset);
        return _DataModel_FastGet(sc, addr, obj);
    }

    if (FT_LIKELY(sc->value)) {
        return Py_NewRef(sc->value);
    }
    return PyErr_Format(PyExc_AttributeError,
                        "type object '%.100s' has no attribute '%.100U'",
                        _CAST(PyTypeObject*, meta)->tp_name,
                        sc->name);
}

static int
member_def_descr_set(MemberDef* self, PyObject* obj, PyObject* val)
{
    MetaModel* meta = (MetaModel*)Py_TYPE(obj);
    const Py_ssize_t offset = self->offset;
    if (FT_UNLIKELY(!member_def_check(offset, (PyTypeObject*)meta))) {
        return -1;
    }

    Schema* sc = META_GET_SCHEMA_BY_OFFSET(meta, offset - meta->slot_offset);
    const uint32_t flags = sc->field->flags;
    if (FT_UNLIKELY((flags & FIELD_FROZEN) ||
                    (val && (flags & _FIELD_COMPUTED_FIELD)))) {
        PyErr_Format(PyExc_AttributeError,
                     "'%.100s' object attribute '%U' is read-only",
                     _CAST(PyTypeObject*, meta)->tp_name,
                     sc->name);
        return -1;
    }

    PyObject** addr = GET_ADDR(obj, offset);
    PyObject* old = *addr;
    if (FT_LIKELY(val)) {
        if (MetaValid_IS_SUBCLASS(meta)) {
            PyObject* tmp;
            ValidateContext ctx = _VALID_MODEL_GET_CTX(obj);
            tmp = TypeAdapter_Conversion(_Schema_GET_VALIDATOR(sc), &ctx, val);
            if (!tmp) {
                ValidationError_Raise(
                  sc->name, _Schema_GET_VALIDATOR(sc), val, (PyObject*)meta);
                return -1;
            }

            Py_XDECREF(old);
            *addr = tmp;
        } else {
            Py_XDECREF(old);
            *addr = Py_NewRef(val);
        }
        return 0;
    }

    if (FT_UNLIKELY(!old)) {
        RETURN_ATTRIBUT_ERROR(self, sc->name, -1);
    }

    Py_DECREF(old);
    *addr = NULL;
    return 0;
}

PyTypeObject MemberDefType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_descr_get = (descrgetfunc)member_def_descr_get,
    .tp_descr_set = (descrsetfunc)member_def_descr_set,
    .tp_dealloc = (destructor)_Object_Dealloc,
    .tp_name = "frost_typing.MemberDef",
    .tp_basicsize = sizeof(MemberDef),
};

PyObject*
MemberDef_Create(Py_ssize_t offset)
{
    const Py_ssize_t ind = (offset / BASE_SIZE) - 2;
    PyObject* res = ind >= CACHE_SIZE ? NULL : cache[ind];
    if (!res) {
        res = Object_New(PyObject, &MemberDefType);
        if (FT_UNLIKELY(!res)) {
            return NULL;
        }

        _CAST(MemberDef*, res)->offset = offset;
        if (ind >= CACHE_SIZE) {
            return res;
        }
        cache[ind] = res;
    }

    return Py_NewRef(res);
}

int
member_def_setup(void)
{
    return PyType_Ready(&MemberDefType);
}

void
member_def_free(void)
{
    for (Py_ssize_t i = 0; i != CACHE_SIZE; i++) {
        Py_CLEAR(cache[i]);
    }
}