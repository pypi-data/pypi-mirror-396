#define PY_SSIZE_T_CLEAN
#include "Python.h"

extern PyTypeObject *PyUuidType, *DecimalType;
extern PyObject *PyTyping, *PyAnnotated, *PyModules, *PyAny, *PyAbc,
  *PyEnumType, *PySelf, *PyRequired, *PyNotRequired, *PyForwardRef,
  *Py_AnnotatedAlias, *PyTypeVar, *PyUnion, *PyLiteral, *PyGenericAlias,
  *_GenericAlias, *PyClassVar, *PySafeUUIDUnknown;

#if (PY_VERSION_HEX >= 0x030d0000) // PY313_PLUS
extern PyObject* PyNoDefault;
#endif

/* ABC */
extern PyObject *AbcCallable, *AbcHashable, *AbcIterable, *AbcSequence,
  *AbcGenerator;

extern int
typing_setup(void);
extern void
typing_free(void);
extern int
PyTyping_Is_TypedDict(PyObject*);
extern PyObject*
PyTyping_Get_Args(PyObject*);
extern PyObject*
PyTyping_Get_Bound(PyObject*);
extern PyObject*
PyTyping_Get_Origin(PyObject*);
extern PyObject*
PyTyping_Get_Metadata(PyObject*);
extern PyObject*
PyTyping_Get_Constraints(PyObject*);
extern PyObject*
PyTyping_Get_RequiredKeys(PyObject*);
extern PyObject*
PyTyping_Get__value2member_map_(PyObject* obj);
extern PyObject*
PyTyping_Eval(PyObject*, PyTypeObject*);
extern PyObject*
PyEvaluateIfNeeded(PyObject* obj, PyTypeObject* tp);
extern PyObject*
PyTyping_Evaluate_Forward_Ref(PyObject*, PyTypeObject*);
extern PyObject*
PyTyping_AnnotatedGetItem(PyObject* hint, PyObject* key);
extern PyObject*
PyTypedDict_Getannotations(PyObject* hint);
extern int
PyTyping_Is_Value(PyObject*, const char*);
extern int
PyTyping_Is_Origin(PyObject*, PyObject*);
