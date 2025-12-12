typedef struct ReadBuffer ReadBuffer;

extern const Py_UCS1 hex_table[256];
extern PyObject*
_JsonParse_CreateString(unsigned char* cur,
                        unsigned char* end,
                        Py_UCS4 max_char,
                        Py_ssize_t size,
                        int use_cache);
extern Py_ssize_t
_JsonParse_String(ReadBuffer* buffer,
                  Py_UCS4* max_char,
                  unsigned char** end_data);
extern PyObject*
JsonParse_String(ReadBuffer*);
extern PyObject*
JsonParse_StringKey(ReadBuffer* buffer);
extern void
_DeseralizeString_Intern(PyObject* ascii);
extern void
deserialize_string_free(void);