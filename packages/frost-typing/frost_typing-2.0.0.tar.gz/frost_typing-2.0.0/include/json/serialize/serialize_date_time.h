typedef struct WriteBuffer WriteBuffer;

extern Py_ssize_t
_TimeDelta_AsISO(PyObject* timedelta, unsigned char* buff);
extern int
_Date_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_Datetime_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_Time_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_TimeDelta_AsJson(WriteBuffer* buff, PyObject* timedelta, ConvParams* params);
extern int
json_date_time_setup(void);
extern void
json_date_time_free(void);