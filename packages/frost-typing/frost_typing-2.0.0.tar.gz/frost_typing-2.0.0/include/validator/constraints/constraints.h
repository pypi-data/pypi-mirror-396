#include "comparison_constraints.h"
#include "datetime_constraints.h"
#include "string_constraints.h"

typedef struct TypeAdapter TypeAdapter;
extern int
IsConstraints(PyObject*);
extern TypeAdapter*
TypeAdapter_Create_Constraints(TypeAdapter*, PyObject*);
extern int
constraints_setup(void);
extern void
constraints_free(void);