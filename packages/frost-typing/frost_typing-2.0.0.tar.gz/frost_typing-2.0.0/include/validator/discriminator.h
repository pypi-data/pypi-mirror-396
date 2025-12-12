#define PY_SSIZE_T_CLEAN
#include "Python.h"

#define Discriminator_Check(v) Py_IS_TYPE(v, &DiscriminatorType)

typedef struct TypeAdapter TypeAdapter;
typedef struct Discriminator
{
    PyObject_HEAD PyObject* discriminator;
    PyObject* raise_on_missing;
    PyObject* mapping;
} Discriminator;

extern PyTypeObject DiscriminatorType;
extern TypeAdapter*
TypeAdapter_Create_Discriminator(TypeAdapter* validator,
                                 Discriminator* discriminator,
                                 PyObject* tp);
extern int
_TypeAdapter_СontainsDiscriminator(TypeAdapter* self);
extern int
discriminator_setup(void);
extern void
discriminator_free(void);
