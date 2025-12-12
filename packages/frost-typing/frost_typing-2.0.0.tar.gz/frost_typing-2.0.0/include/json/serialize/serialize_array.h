typedef struct WriteBuffer WriteBuffer;

extern int
_List_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_Tuple_AsJson(WriteBuffer*, PyObject*, ConvParams* params);
extern int
_Set_AsJson(WriteBuffer*, PyObject*, ConvParams* params);