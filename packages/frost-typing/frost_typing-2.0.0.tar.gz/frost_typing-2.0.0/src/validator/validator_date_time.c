#include "field.h"
#include "validator/validator.h"

#include "datetime.h"

#define PyTime_FromTimeAndTZ(hour, minute, second, usecond, tz)                \
    PyDateTimeAPI->Time_FromTime(                                              \
      hour, minute, second, usecond, tz, PyDateTimeAPI->TimeType)

#define PyDateTime_FromDateAndTimeAndTZ(                                       \
  year, month, day, hour, min, sec, usec, tz)                                  \
    PyDateTimeAPI->DateTime_FromDateAndTime(                                   \
      year, month, day, hour, min, sec, usec, tz, PyDateTimeAPI->DateTimeType)

#define _CACHE_SIZE 48
static PyObject* tz_cache[_CACHE_SIZE] = { NULL };

#define TD_Y (uint8_t)(1)
#define TD_M (uint8_t)(1 << 1)
#define TD_D (uint8_t)(1 << 2)
#define TD_T (uint8_t)(1 << 3)
#define TD_H (uint8_t)(1 << 4)
#define TD_MIN (uint8_t)(1 << 5)
#define TD_S (uint8_t)(1 << 6)

const int SECONDS_PER_DAY = 86400;
const int SECONDS_PER_HOUR = 3600;
const int SECONDS_PER_MINUTE = 60;

TypeAdapter *TypeAdapterTime, *TypeAdapterDate, *TypeAdapterDateTime,
  *TypeAdapterTimeDelta;

static inline int
is_leap_year(int year)
{
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

static inline int
days_in_month(int month, int year)
{
    if (month == 1) {
        return is_leap_year(year) ? 29 : 28;
    }
    return month & 1 ? 30 : 31;
}

static void
time_from_timestamp(int64_t seconds, int* restrict time)
{
    int64_t seconds_in_day = seconds % SECONDS_PER_DAY;
    if (seconds_in_day < 0) {
        seconds_in_day += SECONDS_PER_DAY;
    }

    time[0] = (int)(seconds_in_day / SECONDS_PER_HOUR);
    seconds_in_day %= SECONDS_PER_HOUR;
    time[1] = (int)(seconds_in_day / SECONDS_PER_MINUTE);
    time[2] = (int)(seconds_in_day % SECONDS_PER_MINUTE);
}

static int64_t
date_from_timestamp(int64_t timestamp, int* restrict date)
{
    int64_t seconds_in_day = timestamp % SECONDS_PER_DAY;
    int64_t days = timestamp / SECONDS_PER_DAY;

    int year = 1970;
    while (1) {
        int y_days = is_leap_year(year) ? 366 : 365;
        if (days >= y_days) {
            days -= y_days;
            year += 1;
        } else {
            break;
        }
    }

    int d, month = 0;
    while (days >= (d = days_in_month(month, year))) {
        days -= d;
        month++;
    }

    date[0] = year;
    date[1] = month + 1;
    date[2] = (int)days + 1;
    return seconds_in_day;
}

static PyObject*
timestamp_to_date(int64_t timestamp)
{
    if (timestamp < 0) {
        return NULL;
    }

    int date[3] = { 0 };
    if (date_from_timestamp(timestamp, date) != 0) {
        return NULL;
    }
    return PyDate_FromDate(date[0], date[1], date[2]);
}

static PyObject*
timestamp_to_time(int64_t timestamp, double frac)
{
    if (timestamp < 0 || timestamp >= 86400) {
        return NULL;
    }

    int time[3] = { 0 };
    time_from_timestamp(timestamp, time);
    return PyTime_FromTimeAndTZ(time[0],
                                time[1],
                                time[2],
                                (int)(frac * 1000000.0 + 0.5),
                                PyDateTimeAPI->TimeZone_UTC);
}

static PyObject*
timestamp_to_datetime(int64_t timestamp, double frac)
{
    if (timestamp < 0) {
        return NULL;
    }

    int dt[6] = { 0 };
    timestamp = date_from_timestamp(timestamp, dt);
    time_from_timestamp(timestamp, dt + 3);
    return PyDateTime_FromDateAndTimeAndTZ(dt[0],
                                           dt[1],
                                           dt[2],
                                           dt[3],
                                           dt[4],
                                           dt[5],
                                           (int)(frac * 1000000.0 + 0.5),
                                           PyDateTimeAPI->TimeZone_UTC);
}

PyObject*
creat_tz_info(int sign, int hout, int minute)
{
    PyObject *tz_info, *delta, *tz_name;
    int tz_minute = sign * (hout * 60 + minute);
    if (tz_minute == 0) {
        return Py_NewRef(PyDateTimeAPI->TimeZone_UTC);
    }

    int is_cache = (tz_minute + 720) % 30 == 0;
    if (is_cache) {
        tz_info = tz_cache[(tz_minute + 720) / 30];
        if (tz_info != NULL) {
            return Py_NewRef(tz_info);
        }
    }

    delta = PyDelta_FromDSU(0, tz_minute * 60, 0);
    if (delta == NULL) {
        return NULL;
    }

    tz_name = PyUnicode_FromFormat(
      "UTC%c%02u:%02u", sign == -1 ? '-' : '+', hout, minute);
    if (tz_name == NULL) {
        return NULL;
    }
    tz_info = PyTimeZone_FromOffsetAndName(delta, tz_name);
    Py_DECREF(tz_name);
    Py_DECREF(delta);
    if (is_cache) {
        tz_cache[(tz_minute + 720) / 30] = Py_NewRef(tz_info);
    }
    return tz_info;
}

static void
week_to_date(int* restrict date)
{
    int year = date[0], week = date[1], day = date[2];
    int first_day_of_year = (1 + 5 * ((year - 1) % 4) + 4 * ((year - 1) % 100) +
                             6 * ((year - 1) % 400)) %
                            7;
    int offset = (first_day_of_year == 0) ? 6 : (first_day_of_year - 1);
    int days_passed = (week - 1) * 7 + (day - 1) - offset;
    if (days_passed < 0) {
        year--;
        days_passed += is_leap_year(year) ? 366 : 365;
    }

    int d, month = 1;
    while (days_passed >= (d = days_in_month(month, year))) {
        days_passed -= d;
        month++;
    }
    date[0] = year;
    date[1] = month;
    date[2] = days_passed;
}

static Py_ssize_t
get_buffer(PyObject* obj, char** buf, int raise_err)
{
    PyTypeObject* tp = Py_TYPE(obj);
    if (tp == &PyUnicode_Type) {
        int kind = PyUnicode_KIND(obj);
        void* d = PyUnicode_DATA(obj);
        Py_ssize_t length = PyUnicode_GET_LENGTH(obj);
        if (kind == 1) {
            *buf = d;
            return length;
        }
        if (raise_err) {
            PyErr_Format(PyExc_ValueError, "Invalid isoformat string '%s'", d);
        }
        return -1;
    }
    if (tp == &PyBytes_Type) {
        *buf = _CAST(PyBytesObject*, obj)->ob_sval;
        return PyBytes_GET_SIZE(obj);
    }
    if (tp == &PyByteArray_Type) {
        *buf = _CAST(PyByteArrayObject*, obj)->ob_bytes;
        return PyByteArray_GET_SIZE(obj);
    }

    if (raise_err) {
        PyErr_Format(PyExc_TypeError,
                     "Argument must be string, or a"
                     " bytes-like object, not '%s'",
                     tp->tp_name);
    }
    return -1;
}

static int
parse_date(const char* restrict buf,
           int length,
           int* restrict res,
           int* restrict last_ind)
{
    int st_section = 0, section_i = 0, w = 0;

    for (int ind = 0; ind < length; ++ind) {
        unsigned char ch = (unsigned char)buf[ind];
        if (ch >= '0' && ch <= '9') {
            if (section_i == 0) {
                if (ind - st_section == 4) {
                    st_section = ind;
                    ++section_i;
                }
            } else if (section_i == 1) {
                if (ind - st_section == 2) {
                    st_section = ind;
                    ++section_i;
                }
            }
            res[section_i] = res[section_i] * 10 + (ch - '0');
            continue;
        }
        if (ch == 'W' && !w) {
            if (section_i <= 1) {
                st_section = ind + 1;
                w = 1;
                section_i = 1;
                continue;
            }
        }

        if ((section_i == 0 && ind > 4) ||
            (section_i == 1 && ind - st_section > (3 + w))) {
            if (*last_ind) {
                *last_ind = ind;
                if (w) {
                    week_to_date(res);
                }
                return 0;
            }
            return -1;
        }

        if (res[section_i] == 0) {
            return -1;
        }

        st_section = ind + 1;
        if (ch != '-' || buf[ind - 1] == '-' || ++section_i > 2) {
            if (*last_ind) {
                *last_ind = ind;
                if (w) {
                    if (section_i == 1 && !res[2]) {
                        res[2] = 1;
                    }
                    week_to_date(res);
                }
                return 0;
            }
            return -1;
        }
    }

    if (buf[length - 1] == '-') {
        return -1;
    }

    if (section_i == 1) {
        res[++section_i] = 1;
    }

    if (w) {
        week_to_date(res);
    }

    return 0;
}

static int
pow_degree(int degree)
{
    switch (degree) {
        case 0:
        case 6:
            return 1;
        case 1:
            return 10;
        case 2:
            return 100;
        case 3:
            return 1000;
        case 4:
            return 10000;
        case 5:
            return 100000;
        default:
            return -1;
    }
}

static int
parse_time(const char* restrict buf,
           int length,
           int* restrict res,
           int* restrict sign)
{
    int digit, st_section = 0, section_i = 0;

    for (int ind = 0; ind < length; ++ind) {
        char ch = buf[ind];

        if (ch >= '0' && ch <= '9') {
            if (section_i < 3 || section_i == 4) {
                if (ind - st_section == 2) {
                    section_i++;
                    st_section = ind;
                }
            }
            res[section_i] = res[section_i] * 10 + (ch - '0');
            continue;
        }

        if (st_section == ind) {
            return -1;
        }

        switch (ch) {
            case 'Z':
            case 'z':
                if (section_i < 1 || *sign) {
                    return -1;
                }
                if (ind + 1 != length) {
                    return -1;
                }
                digit = pow_degree(6 - (ind - st_section));
                if (digit < 0) {
                    return -1;
                }
                res[3] *= digit;
                *sign = 1;
                return 0;
            case '-':
            case '+':
                if (section_i < 1 || *sign) {
                    return -1;
                }
                *sign = (ch == '+') ? 1 : -1;
                digit = pow_degree(6 - (ind - st_section));
                if (digit < 0) {
                    return -1;
                }
                res[3] *= digit;
                st_section = ind + 1;
                section_i = 4;
                break;

            case ':':
                if (section_i > 1 && section_i < 4) {
                    return -1;
                }
                st_section = ind + 1;
                if (++section_i == 6) {
                    return -1;
                }
                break;

            case '.':
            case ',':
                if (section_i != 2) {
                    return -1;
                }
                st_section = ind + 1;
                if (++section_i == 6) {
                    return -1;
                }
                break;

            default:
                return -1;
        }
    }

    if (!(*sign) && section_i == 3) {
        digit = pow_degree(6 - (length - st_section));
        if (digit < 0) {
            return -1;
        }
        res[3] *= digit;
    }

    return 0;
}

PyObject*
_DateTime_ParseDateFromBuff(char* buf, Py_ssize_t length, int raise_err)
{
    int writer[3] = { 0 };
    int last_ind = 0;
    if (length > 10 || length < 5 ||
        parse_date(buf, (int)length, writer, &last_ind) < 0) {
        goto error;
    }

    PyObject* res = PyDate_FromDate(writer[0], writer[1], writer[2]);
    if (res) {
        return res;
    }

error:
    if (raise_err) {
        return PyErr_Format(
          PyExc_ValueError, "Invalid isoformat string '%s'", buf);
    }
    return NULL;
}

static PyObject*
date_time_parse_date(PyObject* obj, int raise_err)
{
    char* buff;
    Py_ssize_t size = get_buffer(obj, &buff, raise_err);
    return size < 0 ? NULL : _DateTime_ParseDateFromBuff(buff, size, raise_err);
}

PyObject*
DateTime_ParseDate(PyObject* obj)
{
    return date_time_parse_date(obj, 1);
}

PyObject*
_DateTime_ParseTimeFromBuff(char* buf, Py_ssize_t length, int raise_err)
{
    int sign = 0;
    int writer[6] = { 0 };
    PyObject *tz_info, *time;
    if (length < 3 || length > 21 ||
        parse_time(buf, (int)length, writer, &sign) < 0) {
        goto error;
    }

    if (sign) {
        tz_info = creat_tz_info(sign, writer[4], writer[5]);
        if (!tz_info) {
            return NULL;
        }
    } else {
        tz_info = Py_NewRef(Py_None);
    }
    time =
      PyTime_FromTimeAndTZ(writer[0], writer[1], writer[2], writer[3], tz_info);
    Py_DECREF(tz_info);
    if (time) {
        return time;
    }

error:
    if (raise_err) {
        return PyErr_Format(
          PyExc_ValueError, "Invalid isoformat string '%s'", buf);
    }
    return NULL;
}

static PyObject*
date_time_parse_time(PyObject* obj, int raise_err)
{
    char* buff;
    Py_ssize_t size = get_buffer(obj, &buff, raise_err);
    return size < 0 ? NULL : _DateTime_ParseTimeFromBuff(buff, size, raise_err);
}

PyObject*
DateTime_ParseTime(PyObject* obj)
{
    return date_time_parse_time(obj, 1);
}

PyObject*
_DateTime_ParseDateTimeFromBuff(char* buf, Py_ssize_t length, int raise_err)
{
    if (length < 5 || length > 32) {
        goto error;
    }

    int last_ind = -1;
    int date[3] = { 0 };
    if (parse_date(buf, (int)length, date, &last_ind) < 0) {
        goto error;
    }

    if (last_ind == -1 || last_ind == length) {
        PyObject* res =
          PyDateTime_FromDateAndTime(date[0], date[1], date[2], 0, 0, 0, 0);
        if (res) {
            return res;
        }
        goto error;
    }

    char ch = buf[last_ind++];
    if ((ch != ' ' && ch != 'T') || last_ind == length) {
        goto error;
    }

    int sign = 0;
    int time[6] = { 0 };
    length -= last_ind;
    if (parse_time(buf + last_ind, (int)length, time, &sign) < 0) {
        goto error;
    }

    PyObject* tz_info = sign ? creat_tz_info(sign, time[4], time[5]) : Py_None;
    if (!tz_info) {
        return NULL;
    }

    PyObject* dt = PyDateTime_FromDateAndTimeAndTZ(
      date[0], date[1], date[2], time[0], time[1], time[2], time[3], tz_info);

    if (sign) {
        Py_DECREF(tz_info);
    }

    if (dt) {
        return dt;
    }

error:
    if (raise_err) {
        return PyErr_Format(
          PyExc_ValueError, "Invalid isoformat string '%s'", buf);
    }
    return NULL;
}

static PyObject*
date_time_parse_date_time(PyObject* obj, int raise_err)
{
    char* buff;
    Py_ssize_t size = get_buffer(obj, &buff, raise_err);
    return size < 0 ? NULL
                    : _DateTime_ParseDateTimeFromBuff(buff, size, raise_err);
}

PyObject*
_DateTime_ParseTimeDeltaFromBuff(char* buf, Py_ssize_t length, int raise_err)
{
#define CHECK_FLAG(f)                                                          \
    if (flags >= f || flags & f) {                                             \
        goto error;                                                            \
    }                                                                          \
    flags |= f;

    int is_sign = 0;
    unsigned char ch = (unsigned char)*buf;
    if (length < 3) {
        goto error;
    }

    if (ch == '-' || ch == '+') {
        ch = (unsigned char)buf[1];
        is_sign = 1;
    }

    if (ch != 'P') {
        goto error;
    }

    int tmp = 0, year = 0, month = 0, days = 0, hours = 0, minutes = 0,
        seconds = 0, useconds = 0, is_negativ = *buf == '-' ? 1 : 0;
    Py_ssize_t st_usec = 0;
    uint8_t flags = 0;

    for (Py_ssize_t ind = 1 + is_sign; ind != length; ++ind) {
        ch = (unsigned char)buf[ind];
        if (ch >= '0' && ch <= '9') {
            tmp = tmp * 10 + (ch - '0');
            continue;
        } else if (ch == 'T') {
            CHECK_FLAG(TD_T);
            continue;
        } else if (ch == 'Y') {
            CHECK_FLAG(TD_Y);
            year = tmp;
            tmp = 0;
            continue;
        } else if (ch == 'M') {
            if (flags & TD_T) {
                CHECK_FLAG(TD_MIN);
                minutes = tmp;
            } else {
                CHECK_FLAG(TD_M);
                month = tmp;
            }
            tmp = 0;
            continue;
        } else if (ch == 'D') {
            CHECK_FLAG(TD_D);
            days = tmp;
            tmp = 0;
            continue;
        }

        if (!(flags & TD_T)) {
            goto error;
        }

        if (ch == 'H') {
            CHECK_FLAG(TD_H);
            hours = tmp;
        } else if (ch == 'S') {
            CHECK_FLAG(TD_S);

            if (st_usec) {
                /* 7 considering the `S` */
                int digit = pow_degree(7 - (int)(ind - st_usec));
                if (digit < 0) {
                    goto error;
                }

                useconds = tmp * digit;
            } else {
                seconds = tmp;
            }
        } else if (ch == '.') {
            if (st_usec || !ind) {
                goto error;
            }
            st_usec = ind;
            seconds = tmp;
        } else {
            goto error;
        }
        tmp = 0;
    }

    days += year * 365 + month * 30;
    seconds += hours * 3600 + minutes * 60;
    if (is_negativ) {
        useconds = -useconds;
        seconds = -seconds;
        days = -days;
    }

    PyObject* res = PyDelta_FromDSU(days, seconds, useconds);
    if (res) {
        return res;
    }

error:
    if (raise_err) {
        return PyErr_Format(
          PyExc_ValueError, "Invalid isoformat string '%s'", buf);
    }
    return NULL;
}

static PyObject*
date_time_parse_delta(PyObject* obj, int raise_err)
{
    char* buff;
    Py_ssize_t size = get_buffer(obj, &buff, raise_err);
    return size < 0 ? NULL
                    : _DateTime_ParseTimeDeltaFromBuff(buff, size, raise_err);
}

PyObject*
DateTime_ParseDateTime(PyObject* obj)
{
    return date_time_parse_date_time(obj, 1);
}

PyObject*
DateTime_ParseTimeDelta(PyObject* obj)
{
    return date_time_parse_delta(obj, 1);
}

static PyObject*
converter_time(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    PyObject* res;
    if (PyLong_Check(val) && !PyBool_Check(val)) {
        res = timestamp_to_time(PyLong_AsLongLong(val), 0.0);
    } else if (PyFloat_Check(val)) {
        double d = PyFloat_AS_DOUBLE(val);
        if (!isfinite(d)) {
            return NULL;
        }
        int64_t l = (int64_t)d;
        res = timestamp_to_time(l, d - (double)l);
    } else {
        res = date_time_parse_time(val, 0);
    }

    if (!res) {
        PyErr_Clear();
    }
    return res;
}

static PyObject*
converter_date(UNUSED TypeAdapter* self, ValidateContext* ctx, PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    PyObject* res;
    if (PyLong_Check(val) && !PyBool_Check(val)) {
        res = timestamp_to_date(PyLong_AsLongLong(val));
    } else if (PyFloat_Check(val)) {
        double d = PyFloat_AS_DOUBLE(val);
        int64_t l = (int64_t)d;
        if (!isfinite(d) || ((double)l != d)) {
            return NULL;
        }
        res = timestamp_to_date(l);
    } else {
        res = date_time_parse_date(val, 0);
    }

    if (!res) {
        PyErr_Clear();
    }
    return res;
}

static PyObject*
converter_datetime(UNUSED TypeAdapter* self,
                   ValidateContext* ctx,
                   PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    PyObject* res;
    if (PyLong_Check(val) && !PyBool_Check(val)) {
        res = timestamp_to_datetime(PyLong_AsLongLong(val), 0.0);
    } else if (PyFloat_Check(val)) {
        double d = PyFloat_AS_DOUBLE(val);
        if (!isfinite(d)) {
            return NULL;
        }
        int64_t l = (int64_t)d;
        res = timestamp_to_datetime(l, d - (double)l);
    } else {
        res = date_time_parse_date_time(val, 0);
    }
    if (!res) {
        PyErr_Clear();
    }
    return res;
}

static inline PyObject*
timestamp_to_timedelta(int64_t timestamp, double frac)
{
    if (timestamp < 0) {
        return NULL;
    }

    int days = (int)(timestamp / SECONDS_PER_DAY);
    int seconds = (int)(timestamp % SECONDS_PER_DAY);
    return PyDelta_FromDSU(days, seconds, (int)(frac * 1000000.0 + 0.5));
}

static PyObject*
converter_timedelta(UNUSED TypeAdapter* self,
                    ValidateContext* ctx,
                    PyObject* val)
{
    if (ctx->flags & FIELD_STRICT) {
        return NULL;
    }

    PyObject* res;
    if (PyLong_Check(val) && !PyBool_Check(val)) {
        res = timestamp_to_timedelta(PyLong_AsLongLong(val), 0.0);
    } else if (PyFloat_Check(val)) {
        double d = PyFloat_AS_DOUBLE(val);
        if (!isfinite(d)) {
            return NULL;
        }
        int64_t l = (int64_t)d;
        res = timestamp_to_timedelta(l, d - (double)l);
    } else {
        res = date_time_parse_delta(val, 0);
    }

    if (!res) {
        PyErr_Clear();
    }
    return res;
}

inline int
DateTime_Is_DateType(PyTypeObject* tp)
{
    return tp == PyDateTimeAPI->DateType;
}

inline int
DateTime_Is_TimeType(PyTypeObject* tp)
{
    return tp == PyDateTimeAPI->TimeType;
}

inline int
DateTime_Is_DateTimeType(PyTypeObject* tp)
{
    return tp == PyDateTimeAPI->DateTimeType;
}

inline int
DateTime_Is_TimeDeltaType(PyTypeObject* tp)
{
    return tp == PyDateTimeAPI->DeltaType;
}

int
date_time_setup(void)
{
    PyDateTime_IMPORT;
    if (!PyDateTimeAPI) {
        return -1;
    }

#define TYPEADAPTER_CREATE_DT(name, h, conv, ins, from_json)                   \
    name = TypeAdapter_Create(                                                 \
      (PyObject*)h, NULL, NULL, TypeAdapter_Base_Repr, conv, ins, from_json);  \
    if (!name) {                                                               \
        return -1;                                                             \
    }

    TYPEADAPTER_CREATE_DT(TypeAdapterTime,
                          PyDateTimeAPI->TimeType,
                          converter_time,
                          Inspector_IsType,
                          _JsonValidParse_Time);

    TYPEADAPTER_CREATE_DT(TypeAdapterDate,
                          PyDateTimeAPI->DateType,
                          converter_date,
                          Inspector_IsType,
                          _JsonValidParse_Date);

    TYPEADAPTER_CREATE_DT(TypeAdapterDateTime,
                          PyDateTimeAPI->DateTimeType,
                          converter_datetime,
                          Inspector_IsType,
                          _JsonValidParse_DateTime);

    TYPEADAPTER_CREATE_DT(TypeAdapterTimeDelta,
                          PyDateTimeAPI->DateTimeType,
                          converter_timedelta,
                          Inspector_IsType,
                          _JsonValidParse_TimeDelta);

#undef TYPEADAPTER_CREATE_DT
    return 0;
}

void
date_time_free(void)
{
    Py_DECREF(TypeAdapterTime);
    Py_DECREF(TypeAdapterDate);
    Py_DECREF(TypeAdapterDateTime);
    Py_DECREF(TypeAdapterTimeDelta);

    for (Py_ssize_t i = 0; i < _CACHE_SIZE; i++) {
        Py_CLEAR(tz_cache[i]);
    }
}