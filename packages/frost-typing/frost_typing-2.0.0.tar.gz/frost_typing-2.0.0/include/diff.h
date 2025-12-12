#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define WITH_DIFF_REVERT (uint32_t)(1)

#define DIFF_SKIP_NONE (uint32_t)(1)
#define DIFF_COPY_VALUES (uint32_t)(1 << 1)

extern int
_Diff_Obj(PyObject* self, PyObject* other, uint32_t flags, PyObject** res);
extern int
_Diff_ObjByKey(PyObject* self,
               PyObject* other,
               uint32_t flags,
               PyObject* key,
               PyObject** res);
extern PyObject*
WithDiff_Update(PyObject* self, PyObject* val, uint32_t flags);
extern PyObject*
WithDiff_UpdateByDiffKey(PyObject* self,
                         PyObject* val,
                         uint32_t flags,
                         PyObject* diff_key);