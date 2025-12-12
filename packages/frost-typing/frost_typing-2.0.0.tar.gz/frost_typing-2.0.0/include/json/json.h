#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "json/deserialize/decoder.h"
#include "json/deserialize/deserialize_string.h"
#include "json/deserialize/numeric.h"
#include "json/deserialize/read_buffer.h"
#include "json/serialize/encoder.h"
#include "json/serialize/serialize_array.h"
#include "json/serialize/serialize_date_time.h"
#include "json/serialize/serialize_dict.h"
#include "json/serialize/serialize_float.h"
#include "json/serialize/serialize_long.h"
#include "json/serialize/serialize_meta_model.h"
#include "json/serialize/serialize_string.h"
#include "json/serialize/serialize_validation_error.h"
#include "json/serialize/write_buffer.h"

extern int
json_setup(void);
extern void
json_free(void);