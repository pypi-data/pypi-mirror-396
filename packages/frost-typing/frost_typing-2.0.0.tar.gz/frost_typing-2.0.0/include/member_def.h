#define PY_SSIZE_T_CLEAN
#include "Python.h"

typedef struct MemberDef
{
    PyObject_HEAD Py_ssize_t offset;
} MemberDef;

extern PyTypeObject MemberDefType;

extern PyObject*
MemberDef_Create(Py_ssize_t offset);
extern int
member_def_setup(void);
extern void
member_def_free(void);