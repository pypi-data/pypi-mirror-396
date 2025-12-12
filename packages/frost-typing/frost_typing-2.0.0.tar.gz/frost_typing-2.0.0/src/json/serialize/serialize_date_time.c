#include "utils_common.h"
#include "json/json.h"

#include "datetime.h"

#define INT_TO_CHAR(v) ((char)((v) + '0'))
#define _DateTime_HAS_TZINFO(o) (((_PyDateTime_BaseTZInfo*)o)->hastzinfo)
#define DateTime_DATE_GET_TZINFO(o)                                            \
    (_DateTime_HAS_TZINFO((o)) ? ((PyDateTime_DateTime*)(o))->tzinfo : NULL)

static void
write_buffer_date(WriteBuffer* buff, int year, int month, int day)
{
    unsigned char* s = buff->buffer + buff->size;
    for (int divisor = 1000; divisor > 0; divisor /= 10) {
        *s++ = INT_TO_CHAR(year / divisor % 10);
    }
    *s++ = '-';
    *s++ = INT_TO_CHAR(month / 10);
    *s++ = INT_TO_CHAR(month % 10);
    *s++ = '-';
    *s++ = INT_TO_CHAR(day / 10);
    *s++ = INT_TO_CHAR(day % 10);
    buff->size += 10;
}

static void
write_buffer_time(WriteBuffer* buff,
                  int hour,
                  int minute,
                  int second,
                  int microsecond)
{
    unsigned char* st = buff->buffer + buff->size;
    unsigned char* s = st;

    *s++ = INT_TO_CHAR(hour / 10);
    *s++ = INT_TO_CHAR(hour % 10);

    *s++ = ':';
    *s++ = INT_TO_CHAR(minute / 10);
    *s++ = INT_TO_CHAR(minute % 10);

    if (second || microsecond) {
        *s++ = ':';
        *s++ = INT_TO_CHAR(second / 10);
        *s++ = INT_TO_CHAR(second % 10);
    }
    if (microsecond) {
        *s++ = ':';
        for (int div = 100000; div > 0; div /= 10) {
            *s++ = INT_TO_CHAR(microsecond / div % 10);
        }
    }
    buff->size += s - st;
}

static PyObject*
tzinfo_get_offset(PyObject* tzinfo)
{
    PyObject* offset = PyObject_CallMethodOneArg(tzinfo, __utcoffset, Py_None);
    if (offset == Py_None || offset == NULL) {
        return offset;
    }

    if (FT_LIKELY(PyDelta_Check(offset))) {
        PyDateTime_Delta* dt = (PyDateTime_Delta*)offset;
        if ((dt->days == -1 && dt->seconds == 0 && dt->microseconds < 1) ||
            dt->days < -1 || dt->days >= 1) {
            Py_DECREF(offset);
            return PyErr_Format(PyExc_ValueError,
                                "offset must be a timedelta"
                                " strictly between -timedelta(hour=24) and"
                                " timedelta(hour=24).");
        }
        return offset;
    }

    PyErr_Format(PyExc_TypeError,
                 "tzinfo.utcoffset() must return None or "
                 "timedelta, not '%.200s'",
                 Py_TYPE(offset)->tp_name);
    Py_DECREF(offset);
    return NULL;
}

static int
format_tzoffset(WriteBuffer* buff, PyObject* tzinfo)
{
    PyObject* offset;
    offset = tzinfo_get_offset(tzinfo);
    if (FT_UNLIKELY(!offset)) {
        return -1;
    }

    if (offset == Py_None) {
        int r = WriteBuffer_ConcatSize(buff, "+00:00", 5);
        Py_DECREF(offset);
        return r;
    }

    PyDateTime_Delta* dt = (PyDateTime_Delta*)offset;
    int hour, minute, second = dt->seconds;
    if (PyDateTime_DELTA_GET_DAYS(offset) < 0) {
        buff->buffer[buff->size++] = '-';
        second = 86400 - second;
    } else {
        buff->buffer[buff->size++] = '+';
        minute = second / 60;
    }
    minute = second / 60;
    hour = minute / 60;
    // second %= 60;
    minute %= 60;
    write_buffer_time(buff, hour, minute, 0, 0);
    Py_DECREF(offset);
    return 0;
}

static inline unsigned char*
int_to_str(unsigned char* p, int value)
{
    unsigned char tmp[10];
    int i = 0;

    if (value == 0) {
        *p++ = '0';
        return p;
    }

    while (value > 0) {
        tmp[i++] = '0' + (value % 10);
        value /= 10;
    }

    while (i--) {
        *p++ = tmp[i];
    }
    return p;
}

Py_ssize_t
_TimeDelta_AsISO(PyObject* timedelta, unsigned char* buff)
{
    int days = PyDateTime_DELTA_GET_DAYS(timedelta);
    int secs = PyDateTime_DELTA_GET_SECONDS(timedelta);
    int usec = PyDateTime_DELTA_GET_MICROSECONDS(timedelta);

    int64_t total_second = (_CAST(int64_t, days) * 86400) + secs;
    int negative = total_second < 0;
    if (negative) {
        total_second = -total_second;
    }

    days = (int)(total_second / 86400);
    secs = (int)(total_second % 86400);

    if (negative && usec > 0) {
        usec = 1000000 - usec;
        secs--;
    } else if (usec < 0) {
        negative = 1;
        usec = -usec;
    }

    unsigned char* p = buff;
    if (negative) {
        *p++ = '-';
    }

    *p++ = 'P';
    if (days) {
        p = int_to_str(p, days);
        *p++ = 'D';
    }

    if (!(secs || usec)) {
        if (!days) {
            *p++ = '0';
            *p++ = 'D';
        }
        return (Py_ssize_t)(p - buff);
    }

    *p++ = 'T';
    if (secs || usec) {
        p = int_to_str(p, secs);
        if (usec) {
            *p++ = '.';
            int digits[6] = {
                (usec / 100000) % 10, (usec / 10000) % 10, (usec / 1000) % 10,
                (usec / 100) % 10,    (usec / 10) % 10,    usec % 10,
            };
            for (int i = 0; i < 6; i++) {
                *p++ = '0' + digits[i];
            }
        }
        *p++ = 'S';
    }

    return (Py_ssize_t)(p - buff);
}

int
_Date_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* params)
{
    if (FT_UNLIKELY(WriteBuffer_Resize(buff, buff->size + 12) < 0)) {
        return -1;
    }

    buff->buffer[buff->size++] = '"';
    int year = PyDateTime_GET_YEAR(obj);
    unsigned char month = PyDateTime_GET_MONTH(obj);
    unsigned char day = PyDateTime_GET_DAY(obj);
    write_buffer_date(buff, year, month, day);
    buff->buffer[buff->size++] = '"';
    return 0;
}

int
_Time_AsJson(WriteBuffer* buff, PyObject* obj, UNUSED ConvParams* params)
{
    PyObject* tzinfo = DateTime_DATE_GET_TZINFO(obj);
    if (tzinfo && !PyTZInfo_Check(tzinfo)) {
        PyObject* tmp = PyObject_CallMethodNoArgs(obj, __isoformat);
        return tmp ? _PyObject_AsJsonDecrefVal(buff, tmp, params) : -1;
    }

    const Py_ssize_t n_size = buff->size + (tzinfo ? 33 : 17);
    if (FT_UNLIKELY(WriteBuffer_Resize(buff, n_size) < 0)) {
        return -1;
    }

    buff->buffer[buff->size++] = '"';
    unsigned char hour = PyDateTime_TIME_GET_HOUR(obj);
    unsigned char minute = PyDateTime_TIME_GET_MINUTE(obj);
    unsigned char second = PyDateTime_TIME_GET_SECOND(obj);
    int microsecond = PyDateTime_TIME_GET_MICROSECOND(obj);
    write_buffer_time(buff, hour, minute, second, microsecond);
    if (tzinfo) {
        if (format_tzoffset(buff, tzinfo) < 0) {
            return -1;
        }
    }
    buff->buffer[buff->size++] = '"';
    return 0;
}

int
_Datetime_AsJson(WriteBuffer* buff, PyObject* obj, ConvParams* params)
{
    PyObject* tzinfo = DateTime_DATE_GET_TZINFO(obj);
    if (tzinfo && !PyTZInfo_Check(tzinfo)) {
        PyObject* tmp = PyObject_CallMethodNoArgs(obj, __isoformat);
        return tmp ? _PyObject_AsJsonDecrefVal(buff, tmp, params) : -1;
    }

    const Py_ssize_t n_size = buff->size + (tzinfo ? 44 : 28);
    if (FT_UNLIKELY(WriteBuffer_Resize(buff, n_size) < 0)) {
        return -1;
    }

    buff->buffer[buff->size++] = '"';
    int year = PyDateTime_GET_YEAR(obj);
    unsigned char month = PyDateTime_GET_MONTH(obj);
    unsigned char day = PyDateTime_GET_DAY(obj);
    write_buffer_date(buff, year, month, day);

    buff->buffer[buff->size++] = 'T';

    int hour = PyDateTime_DATE_GET_HOUR(obj);
    int minute = PyDateTime_DATE_GET_MINUTE(obj);
    int second = PyDateTime_DATE_GET_SECOND(obj);
    int microsecond = PyDateTime_DATE_GET_MICROSECOND(obj);
    write_buffer_time(buff, hour, minute, second, microsecond);
    if (tzinfo) {
        if (FT_UNLIKELY(format_tzoffset(buff, tzinfo) < 0)) {
            return -1;
        }
    }
    buff->buffer[buff->size++] = '"';
    return 0;
}

int
_TimeDelta_AsJson(WriteBuffer* buff,
                  PyObject* timedelta,
                  UNUSED ConvParams* params)
{
    Py_ssize_t new_size = buff->size + 28;
    if (WriteBuffer_Resize(buff, new_size) < 0) {
        return -1;
    }

    unsigned char* cur = buff->buffer + buff->size;
    *cur++ = '"';
    buff->size += _TimeDelta_AsISO(timedelta, cur) + 1;
    buff->buffer[buff->size++] = '"';
    return 0;
}

int
json_date_time_setup(void)
{
    PyDateTime_IMPORT;
    return PyDateTimeAPI ? 0 : -1;
}

void
json_date_time_free(void)
{
}