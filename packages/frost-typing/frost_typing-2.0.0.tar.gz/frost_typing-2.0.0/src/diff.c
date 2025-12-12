#include "diff.h"
#include "convector.h"
#include "meta_valid_model.h"
#include "utils_common.h"
#include "valid_model.h"

typedef int (*func_append)(PyObject*, PyObject*);

static inline PyObject*
get_by_key(PyObject* obj, PyObject* diff_key)
{
    if (PyDict_Check(obj)) {
        return PyObject_GetItem(obj, diff_key);
    }
    return PyObject_GetAttr(obj, diff_key);
}

static inline PyObject*
diff_copy(PyObject* val, uint32_t flags)
{
    return (flags & DIFF_COPY_VALUES) ? PyCopy(val) : Py_NewRef(val);
}

static PyObject*
diff_format(PyObject* self, PyObject* other, uint32_t flags)
{
    PyObject* dict = AsDict(self);
    if (FT_UNLIKELY(!dict)) {
        return NULL;
    }

    if (flags & DIFF_COPY_VALUES) {
        self = PyCopy(self);
        if (FT_UNLIKELY(!self)) {
            return NULL;
        }

        other = PyCopy(other);
        if (FT_UNLIKELY(!other)) {
            Py_DECREF(self);
            return NULL;
        }
    } else {
        Py_INCREF(self);
        Py_INCREF(other);
    }

    PyObject* res = PyTuple_Pack(2, self, other);
    Py_DECREF(self);
    Py_DECREF(other);
    return res;
}

static int
diff_collection(PyObject* removed, PyObject* append, PyObject** res)
{
    if (!removed && !append) {
        *res = NULL;
        return 0;
    }

    if (!removed) {
        removed = PyList_New(0);
        if (FT_UNLIKELY(!removed)) {
            goto error;
        }
    }

    if (!append) {
        append = PyList_New(0);
        if (FT_UNLIKELY(!append)) {
            goto error;
        }
    }

    *res = PyTuple_Pack(2, removed, append);
    Py_DECREF(removed);
    Py_DECREF(append);
    return *res ? 1 : -1;

error:
    Py_XDECREF(removed);
    Py_XDECREF(append);
    *res = NULL;
    return 0;
}

static int
diff_collection_diff_key(PyObject* removed,
                         PyObject* update,
                         PyObject* append,
                         PyObject** res)
{
    if (!removed && !update && !append) {
        *res = NULL;
        return 0;
    }

    if (!removed) {
        removed = PyList_New(0);
        if (FT_UNLIKELY(!removed)) {
            goto error;
        }
    }

    if (!update) {
        update = PyList_New(0);
        if (FT_UNLIKELY(!update)) {
            goto error;
        }
    }

    if (!append) {
        append = PyList_New(0);
        if (FT_UNLIKELY(!append)) {
            goto error;
        }
    }

    *res = PyTuple_Pack(3, removed, update, append);
    Py_DECREF(removed);
    Py_DECREF(append);
    Py_DECREF(update);
    return *res ? 1 : -1;

error:
    Py_XDECREF(removed);
    Py_XDECREF(append);
    Py_XDECREF(update);
    return -1;
}

static int
list_copy_append(PyObject* list, PyObject* items, uint32_t flags)
{
    PyObject* copy = diff_copy(items, flags);
    return copy ? _PyList_Append_Decref(list, copy) : -1;
}

static int
diff_list_append(PyObject** list, PyObject* items, uint32_t flags)
{
    PyObject* obj = *list;
    if (FT_UNLIKELY(!obj)) {
        obj = PyList_New(0);
        if (FT_UNLIKELY(!obj)) {
            return -1;
        }
        *list = obj;
    }
    return list_copy_append(obj, items, flags);
}

static int
diff_list_nested(PyObject* self,
                 PyObject* other,
                 uint32_t flags,
                 PyObject** res)
{
    PyObject* list = *res;
    ListForeach(val, self)
    {
        int r = PySequence_Contains(other, val);
        if (r) {
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            continue;
        }

        if (FT_UNLIKELY(diff_list_append(&list, val, flags) < 0)) {
            goto error;
        }
    }

    *res = list;
    return list ? 1 : 0;

error:
    *res = NULL;
    Py_XDECREF(list);
    return -1;
}

static int
diff_list(PyObject* self, PyObject* other, uint32_t flags, PyObject** res)
{
    PyObject* removed = NULL;
    PyObject* append = NULL;
    if (FT_UNLIKELY(diff_list_nested(self, other, flags, &removed) < 0 ||
                    diff_list_nested(other, self, flags, &append) < 0)) {
        Py_XDECREF(removed);
        Py_XDECREF(append);
        return -1;
    }
    return diff_collection(removed, append, res);
}

static PyObject*
diff_set_create_dict_by_key(PyObject* set, PyObject* diff_key)
{
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(!dict)) {
        return NULL;
    }

    SetForeach(item, set)
    {
        PyObject* key = get_by_key(item, diff_key);
        if (FT_UNLIKELY(!key)) {
            goto error;
        }

        int r = PyDict_SetItem(dict, key, item);
        Py_DECREF(key);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    return dict;
error:
    Py_DECREF(dict);
    return NULL;
}

static PyObject*
diff_list_create_dict_by_key(PyObject* list, PyObject* diff_key)
{
    PyObject* dict = PyDict_New();
    if (FT_UNLIKELY(!dict)) {
        return NULL;
    }

    ListForeach(item, list)
    {
        PyObject* key = get_by_key(item, diff_key);
        if (FT_UNLIKELY(!key)) {
            goto error;
        }

        int r = PyDict_SetItem(dict, key, item);
        Py_DECREF(key);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
    }

    return dict;
error:
    Py_DECREF(dict);
    return NULL;
}

static int
diff_obj_by_key(PyObject* self,
                PyObject* other,
                uint32_t flags,
                PyObject* diff_key,
                PyObject* obj_id,
                PyObject** res)
{
    PyObject* diff = NULL;
    int r = _Diff_Obj(self, other, flags, &diff);
    if (r != 1) {
        *res = NULL;
        return r;
    }

    if (FT_UNLIKELY(!PyDict_Check(diff))) {
        _RaiseInvalidType("diff", "dict", Py_TYPE(diff)->tp_name);
        goto error;
    }

    if (FT_UNLIKELY(PyDict_SetItem(diff, diff_key, obj_id) < 0)) {
        goto error;
    }

    *res = diff;
    return 1;

error:
    Py_DECREF(diff);
    *res = NULL;
    return -1;
}

static int
diff_by_key_append(PyObject** append,
                   PyObject** update,
                   PyObject* dict_keys,
                   PyObject* val,
                   PyObject* diff_key,
                   uint32_t flags)
{
    PyObject* obj_id = get_by_key(val, diff_key);
    if (FT_UNLIKELY(!obj_id)) {
        return -1;
    }

    PyObject* old = Dict_GetItemNoError(dict_keys, obj_id);
    if (!old) {
        Py_DECREF(obj_id);
        return diff_list_append(append, val, flags);
    }

    PyObject* diff = NULL;
    int r = diff_obj_by_key(old, val, flags, diff_key, obj_id, &diff);
    Py_DECREF(obj_id);
    if (r != 1) {
        return r;
    }

    r = diff_list_append(update, diff, flags);
    Py_DECREF(diff);
    return r;
}

static int
diff_by_key_removed(PyObject** list,
                    PyObject* dict_keys,
                    PyObject* val,
                    PyObject* diff_key,
                    uint32_t flags)
{
    PyObject* obj_id = get_by_key(val, diff_key);
    if (FT_UNLIKELY(!obj_id)) {
        return -1;
    }

    int r = PyDict_Contains(dict_keys, obj_id);
    Py_DECREF(obj_id);
    if (r) {
        return r;
    }
    return diff_list_append(list, val, flags);
}

static int
diff_list_by_key(PyObject* self,
                 PyObject* other,
                 uint32_t flags,
                 PyObject* diff_key,
                 PyObject** res)
{
    PyObject *rm = NULL, *add = NULL, *upd = NULL;
    PyObject* old_dict = diff_list_create_dict_by_key(self, diff_key);
    if (FT_UNLIKELY(!old_dict)) {
        return -1;
    }

    PyObject* new_dict = diff_list_create_dict_by_key(other, diff_key);
    if (FT_UNLIKELY(!new_dict)) {
        Py_DECREF(old_dict);
        return -1;
    }

    ListForeach(new_val, other)
    {
        if (FT_UNLIKELY(diff_by_key_append(
                          &add, &upd, old_dict, new_val, diff_key, flags) <
                        0)) {
            goto error;
        }
    }

    ListForeach(old_val, self)
    {
        if (FT_UNLIKELY(diff_by_key_removed(
                          &rm, new_dict, old_val, diff_key, flags) < 0)) {
            goto error;
        }
    }

    Py_DECREF(old_dict);
    Py_DECREF(new_dict);
    return diff_collection_diff_key(rm, upd, add, res);

error:
    Py_DECREF(old_dict);
    Py_DECREF(new_dict);
    Py_XDECREF(add);
    Py_XDECREF(upd);
    Py_XDECREF(rm);
    *res = NULL;
    return -1;
}

static int
diff_any_set_by_key(PyObject* self,
                    PyObject* other,
                    uint32_t flags,
                    PyObject* diff_key,
                    PyObject** res)
{
    PyObject *rm = NULL, *add = NULL, *upd = NULL;
    PyObject* old_dict = diff_set_create_dict_by_key(self, diff_key);
    if (FT_UNLIKELY(!old_dict)) {
        return -1;
    }

    PyObject* new_dict = diff_set_create_dict_by_key(other, diff_key);
    if (FT_UNLIKELY(!new_dict)) {
        Py_DECREF(old_dict);
        return -1;
    }

    SetForeach(new_val, other)
    {
        if (FT_UNLIKELY(diff_by_key_append(
                          &add, &upd, old_dict, new_val, diff_key, flags) <
                        0)) {
            goto error;
        }
    }

    SetForeach(old_val, self)
    {
        if (FT_UNLIKELY(diff_by_key_removed(
                          &rm, new_dict, old_val, diff_key, flags) < 0)) {
            goto error;
        }
    }

    Py_DECREF(old_dict);
    Py_DECREF(new_dict);
    return diff_collection_diff_key(rm, upd, add, res);

error:
    Py_DECREF(old_dict);
    Py_DECREF(new_dict);
    Py_XDECREF(add);
    Py_XDECREF(upd);
    Py_XDECREF(rm);
    *res = NULL;
    return -1;
}

static int
diff_any_set_nested(PyObject* self,
                    PyObject* other,
                    uint32_t flags,
                    PyObject** res)
{
    PyObject* list = NULL;
    SetForeach(val, self)
    {
        int r = PySet_Contains(other, val);
        if (FT_UNLIKELY(r < 0)) {
            goto error;
        }
        if (r) {
            continue;
        }

        if (FT_UNLIKELY(!list)) {
            list = PyList_New(0);
            if (FT_UNLIKELY(!list)) {
                goto error;
            }
        }

        if (FT_UNLIKELY(list_copy_append(list, val, flags) < 0)) {
            goto error;
        }
    }

    *res = list;
    return list ? 1 : 0;

error:
    *res = NULL;
    Py_XDECREF(list);
    return -1;
}

static int
diff_any_set(PyObject* self, PyObject* other, uint32_t flags, PyObject** res)
{
    PyObject* removed = NULL;
    PyObject* append = NULL;
    if (FT_UNLIKELY(diff_any_set_nested(self, other, flags, &removed) < 0 ||
                    diff_any_set_nested(other, self, flags, &append) < 0)) {
        Py_XDECREF(*res);
        *res = NULL;
        return -1;
    }
    return diff_collection(removed, append, res);
}

static int
diff_dict_nested(PyObject* self,
                 PyObject* other,
                 uint32_t flags,
                 PyObject** res,
                 int reversed)
{
    PyObject *copy, *key, *val, *o_val, *dict = *res;
    Py_ssize_t pos = 0;
    int r;
    while (PyDict_Next(self, &pos, &key, &val)) {
        o_val = Dict_GetItemNoError(other, key);
        if (o_val) {
            if (reversed) {
                r = _Diff_Obj(o_val, val, flags, &copy);
            } else {
                r = _Diff_Obj(val, o_val, flags, &copy);
            }
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            if (!r) {
                continue;
            }
        } else {
            if (reversed) {
                copy = diff_format(Py_None, val, flags);
            } else {
                copy = diff_format(val, Py_None, flags);
            }

            if (FT_UNLIKELY(!copy)) {
                goto error;
            }
        }

        if (FT_UNLIKELY(!dict)) {
            dict = PyDict_New();
            if (FT_UNLIKELY(!dict)) {
                Py_DECREF(copy);
                goto error;
            }
        }

        if (FT_UNLIKELY(PyDict_SetItemDecrefVal(dict, key, copy) < 0)) {
            goto error;
        }
    }

    *res = dict;
    return dict ? 1 : 0;

error:
    *res = NULL;
    Py_XDECREF(dict);
    return -1;
}

static int
diff_dict(PyObject* self, PyObject* other, uint32_t flags, PyObject** res)
{
    if (FT_UNLIKELY(diff_dict_nested(self, other, flags, res, 0) < 0 ||
                    diff_dict_nested(other, self, flags, res, 1) < 0)) {
        Py_XDECREF(*res);
        return -1;
    }
    return *res ? 1 : 0;
}

int
_Diff_ObjByKey(PyObject* self,
               PyObject* other,
               uint32_t flags,
               PyObject* key,
               PyObject** res)
{
    *res = NULL;
    if (flags & DIFF_SKIP_NONE && other == Py_None) {
        return 0;
    } else if (!Py_IS_TYPE(other, Py_TYPE(self))) {
        return _Diff_Obj(self, other, flags, res);
    } else if (PyList_Check(self)) {
        return diff_list_by_key(self, other, flags, key, res);
    } else if (PySet_Check(self)) {
        return diff_any_set_by_key(self, other, flags, key, res);
    }

    _RaiseInvalidType("diff_key_val", "list or set", Py_TYPE(self)->tp_name);
    return -1;
}

int
_Diff_Obj(PyObject* self, PyObject* other, uint32_t flags, PyObject** res)
{
    *res = NULL;
    if (flags & DIFF_SKIP_NONE && other == Py_None) {
        return 0;
    }

    if (Py_IS_TYPE(other, Py_TYPE(self))) {
        if (PyList_Check(self)) {
            return diff_list(self, other, flags, res);
        } else if (PyDict_Check(self)) {
            return diff_dict(self, other, flags, res);
        } else if (MetaValid_Check(self)) {
            return _ValidModel_Diff(self, other, flags, res);
        } else if (PySet_Check(self)) {
            return diff_any_set(self, other, flags, res);
        }
    }

    int r = PyObject_RichCompareBool(self, other, Py_EQ);
    if (r) {
        return r < 0 ? -1 : 0;
    }

    *res = diff_format(self, other, flags);
    return *res ? 1 : -1;
}

static int
with_diff_array_add(PyObject* add, PyObject* res, func_append append)
{
    ListForeach(val, add)
    {
        if (FT_UNLIKELY(append(res, val) < 0)) {
            return -1;
        }
    }
    return 0;
}

static PyObject*
with_diff_list(PyObject* self, PyObject* rm, PyObject* add)
{
    PyObject* res = PyList_New(0);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    ListForeach(val, self)
    {
        int r = PySequence_Contains(rm, val);
        if (r) {
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            continue;
        }

        if (FT_UNLIKELY(PyList_Append(res, val) < 0)) {
            goto error;
        }
    }

    if (FT_LIKELY(with_diff_array_add(add, res, PyList_Append) >= 0)) {
        return res;
    }
error:
    Py_DECREF(res);
    return NULL;
}

static PyObject*
with_diff_any_set(PyObject* self, PyObject* rm, PyObject* add)
{
    PyObject* res = PySet_New(NULL);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    SetForeach(val, self)
    {
        int r = PySequence_Contains(rm, val);
        if (r) {
            if (FT_UNLIKELY(r < 0)) {
                goto error;
            }
            continue;
        }

        if (FT_UNLIKELY(PySet_Add(res, val) < 0)) {
            goto error;
        }
    }

    if (FT_LIKELY(with_diff_array_add(add, res, PySet_Add) >= 0)) {
        return res;
    }

error:
    Py_DECREF(res);
    return NULL;
}

static inline PyObject*
with_diff_set(PyObject* set, PyObject* rm, PyObject* add)
{
    PyObject* res = PySet_New(set);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    ListForeach(val, rm)
    {
        if (FT_UNLIKELY(PySet_Discard(res, val) < 0)) {
            goto error;
        }
    }

    ListForeach(val, add)
    {
        if (FT_UNLIKELY(PySet_Add(res, val) < 0)) {
            goto error;
        }
    }

    return res;

error:
    Py_DECREF(res);
    return NULL;
}

static int
with_diff_by_key_rm_upd(PyObject* res,
                        PyObject* val,
                        PyObject* dict_rm,
                        PyObject* dict_update,
                        uint32_t flags,
                        PyObject* diff_key,
                        func_append append)
{
    PyObject* obj_id = get_by_key(val, diff_key);
    if (!obj_id) {
        return -1;
    }

    int r = PyDict_Contains(dict_rm, obj_id);
    if (r) {
        Py_DECREF(obj_id);
        return r;
    }

    PyObject* update_val = Dict_GetItemNoError(dict_update, obj_id);
    Py_DECREF(obj_id);
    if (!update_val) {
        return append(res, val);
    }

    // update
    PyObject* new_val = WithDiff_Update(val, update_val, flags);
    if (FT_UNLIKELY(!new_val)) {
        return -1;
    }

    r = append(res, new_val);
    Py_DECREF(new_val);
    return r;
}

static PyObject*
create_diff_dicts_by_key(PyObject* rm,
                         PyObject* update,
                         PyObject* key,
                         PyObject** out_updated_dict)
{
    PyObject* dict_rm = diff_list_create_dict_by_key(rm, key);
    if (FT_UNLIKELY(!dict_rm)) {
        return NULL;
    }

    PyObject* dict_update = diff_list_create_dict_by_key(update, key);
    if (FT_UNLIKELY(!dict_update)) {
        Py_DECREF(dict_rm);
        return NULL;
    }

    *out_updated_dict = dict_update;
    return dict_rm;
}

static PyObject*
with_diff_list_by_key(PyObject* self,
                      PyObject* rm,
                      PyObject* update,
                      PyObject* add,
                      uint32_t flags,
                      PyObject* key)
{
    PyObject *dict_upd, *dict_rm, *res = PyList_New(0);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    dict_rm = create_diff_dicts_by_key(rm, update, key, &dict_upd);
    if (FT_UNLIKELY(!dict_rm)) {
        Py_DECREF(res);
        return NULL;
    }

    ListForeach(val, self)
    {
        if (FT_UNLIKELY(
              with_diff_by_key_rm_upd(
                res, val, dict_rm, dict_upd, flags, key, PyList_Append) < 0)) {
            goto error;
        }
    }

    ListForeach(val, add)
    {
        if (FT_UNLIKELY(PyList_Append(res, val) < 0)) {
            goto error;
        }
    }

    Py_DECREF(dict_rm);
    Py_DECREF(dict_upd);
    return res;

error:
    Py_XDECREF(dict_rm);
    Py_XDECREF(dict_upd);
    Py_DECREF(res);
    return NULL;
}

static inline PyObject*
with_diff_set_by_key(PyObject* self,
                     PyObject* rm,
                     PyObject* update,
                     PyObject* add,
                     uint32_t flags,
                     PyObject* key)
{
    PyObject *dict_upd, *dict_rm, *res = PySet_New(NULL);
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    dict_rm = create_diff_dicts_by_key(rm, update, key, &dict_upd);
    if (FT_UNLIKELY(!dict_rm)) {
        Py_DECREF(res);
        return NULL;
    }

    SetForeach(val, self)
    {
        if (FT_UNLIKELY(with_diff_by_key_rm_upd(
                          res, val, dict_rm, dict_upd, flags, key, PySet_Add) <
                        0)) {
            goto error;
        }
    }

    ListForeach(val, add)
    {
        if (FT_UNLIKELY(PySet_Add(res, val) < 0)) {
            goto error;
        }
    }

    Py_DECREF(dict_rm);
    Py_DECREF(dict_upd);
    return res;

error:
    Py_XDECREF(dict_rm);
    Py_XDECREF(dict_upd);
    Py_DECREF(res);
    return NULL;
}

static inline int
with_diff_get_rm_add(PyObject* self,
                     PyObject** rm,
                     PyObject** add,
                     uint32_t flags)
{
    PyObject** items;
    if (PyTuple_Check(self)) {
        items = TUPLE_ITEMS(self);
    } else if (PyList_Check(self)) {
        items = LIST_ITEMS(self);
    } else {
        return 0;
    }

    if (Py_SIZE(self) != 2) {
        return 0;
    }

    if (flags & WITH_DIFF_REVERT) {
        *rm = items[1];
        *add = items[0];
    } else {
        *rm = items[0];
        *add = items[1];
    }
    return 1;
}

static inline int
with_diff_by_key_get_rm_upd_add(PyObject* self,
                                PyObject** rm,
                                PyObject** upd,
                                PyObject** add,
                                uint32_t flags)
{

    PyObject** items;
    if (PyTuple_Check(self)) {
        items = TUPLE_ITEMS(self);
    } else if (PyList_Check(self)) {
        items = LIST_ITEMS(self);
    } else {
        _RaiseInvalidType("diff", "tuple or list", Py_TYPE(self)->tp_name);
        return 0;
    }

    if (!PyCheck_ArgsCnt("with_diff_by_key", Py_SIZE(self), 3)) {
        return 0;
    }

    *upd = items[1];
    if (flags & WITH_DIFF_REVERT) {
        *rm = items[2];
        *add = items[0];
    } else {
        *rm = items[0];
        *add = items[2];
    }
    return 1;
}

static inline PyObject*
with_diff_dict(PyObject* self, PyObject* dict, uint32_t flags)
{
    PyObject* res = PyDict_New();
    if (FT_UNLIKELY(!res)) {
        return NULL;
    }

    Py_ssize_t pos = 0;
    PyObject *key, *val, *tmp;
    while (PyDict_Next(self, &pos, &key, &val)) {
        PyObject* diff = Dict_GetItemNoError(dict, key);
        if (!diff) {
            if (FT_UNLIKELY(PyDict_SetItem(res, key, val) < 0)) {
                goto error;
            }
            continue;
        }

        tmp = WithDiff_Update(val, diff, flags);
        if (FT_UNLIKELY(!tmp || PyDict_SetItemDecrefVal(res, key, tmp) < 0)) {
            goto error;
        }
    }

    return res;

error:
    Py_DECREF(res);
    return NULL;
}

PyObject*
WithDiff_Update(PyObject* self, PyObject* val, uint32_t flags)
{
    if (PyDict_Check(val)) {
        if (MetaValid_Check(self)) {
            return _ValidModel_WithDiff(self, val, flags);
        } else if (PyDict_Check(self)) {
            return with_diff_dict(self, val, flags);
        }
    }

    PyObject *rm, *add;
    if (!with_diff_get_rm_add(val, &rm, &add, flags)) {
        return Py_NewRef(val);
    }

    if (PyList_Check(rm) && PyList_Check(add)) {
        if (PyList_Check(self)) {
            return with_diff_list(self, rm, add);
        } else if (PySet_Check(self)) {
            return with_diff_any_set(self, rm, add);
        }
    }
    return Py_NewRef(add);
}

PyObject*
WithDiff_UpdateByDiffKey(PyObject* self,
                         PyObject* val,
                         uint32_t flags,
                         PyObject* diff_key)
{
    PyObject *rm, *update, *add;
    if (FT_UNLIKELY(
          !with_diff_by_key_get_rm_upd_add(val, &rm, &update, &add, flags))) {
        return NULL;
    }

    if (FT_UNLIKELY(!PyList_Check(rm))) {
        return _RaiseInvalidType("rm_list", "list", Py_TYPE(rm)->tp_name);
    }

    if (FT_UNLIKELY(!PyList_Check(update))) {
        return _RaiseInvalidType(
          "update_list", "list", Py_TYPE(update)->tp_name);
    }

    if (!PyList_Check(add)) {
        return _RaiseInvalidType("add_list", "list", Py_TYPE(add)->tp_name);
    }

    if (PyList_Check(self)) {
        return with_diff_list_by_key(self, rm, update, add, flags, diff_key);
    }

    if (PySet_Check(self)) {
        return with_diff_set_by_key(self, rm, update, add, flags, diff_key);
    }

    return _RaiseInvalidType("obj", "list or set", Py_TYPE(self)->tp_name);
}
