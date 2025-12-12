typedef struct WriteBuffer WriteBuffer;

extern int
_Unicode_FastAsJson(WriteBuffer*, PyObject*);
extern int
_Unicode_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_BytesArray_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_Bytes_AsJson(WriteBuffer*, PyObject*, ConvParams* params);