#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define DateTimeConstraints_AWARE ((uint64_t)1)
#define DateTimeConstraints_NAIVE ((uint64_t)1 << 1)
#define DateTimeConstraints_PAST ((uint64_t)1 << 2)
#define DateTimeConstraints_FUTURE ((uint64_t)1 << 3)

typedef struct TypeAdapter TypeAdapter;
typedef struct ValidateContext ValidateContext;

typedef struct DateTimeConstraints
{
    PyObject_HEAD uint64_t flags;
} DateTimeConstraints;

extern PyObject *AwareDatetime, // has a tz
  *NaiveDatetime,               // does not have a tz
  *PastDatetime,                // the past
  *FutureDatetime;              // the future

extern PyTypeObject DateTimeConstraintsType;
extern int
datetime_constraint_setup(void);
extern void
datetime_constraint_free(void);
extern PyObject*
DateTime_Converter(TypeAdapter*, ValidateContext*, PyObject*);