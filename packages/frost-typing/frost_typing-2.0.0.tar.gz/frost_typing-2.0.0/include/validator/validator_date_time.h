#define PY_SSIZE_T_CLEAN
#include "Python.h"

extern TypeAdapter *TypeAdapterTime, *TypeAdapterDate, *TypeAdapterDateTime,
  *TypeAdapterTimeDelta;

extern int
date_time_setup(void);
extern void
date_time_free(void);
extern PyObject*
DateTime_ParseDate(PyObject*);
extern PyObject*
DateTime_ParseTime(PyObject*);
extern PyObject*
DateTime_ParseDateTime(PyObject*);
extern PyObject*
DateTime_ParseTimeDelta(PyObject*);
extern int
DateTime_Is_DateType(PyTypeObject*);
extern int
DateTime_Is_TimeType(PyTypeObject*);
extern int
DateTime_Is_DateTimeType(PyTypeObject*);
extern int
DateTime_Is_TimeDeltaType(PyTypeObject*);
extern PyObject*
_DateTime_ParseDateFromBuff(char* buf, Py_ssize_t length, int raise_err);
extern PyObject*
_DateTime_ParseTimeFromBuff(char* buf, Py_ssize_t length, int raise_err);
extern PyObject*
_DateTime_ParseDateTimeFromBuff(char* buf, Py_ssize_t length, int raise_err);
extern PyObject*
_DateTime_ParseTimeDeltaFromBuff(char* buf, Py_ssize_t length, int raise_err);
