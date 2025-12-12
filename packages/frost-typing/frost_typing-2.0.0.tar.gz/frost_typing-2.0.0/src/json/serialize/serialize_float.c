// Copyright [2025] [Frostic]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// This file includes code from the Ryu project
// (https://github.com/ulfjack/ryu) originally licensed under the Apache
// License, Version 2.0.
// This file is based on code from the Ryu project but has been modified.

#include "math.h"
#include "utils_common.h"
#include "json/json.h"
#include "json/serialize/double_table.h"

#if defined(_MSC_VER) && defined(_M_X64)
#define UMUL128_DEFINED
#include "intrin.h"
#else
#include "stdint.h"
#endif

#define DOUBLE_POW5_INV_BITCOUNT 125
#define DOUBLE_POW5_BITCOUNT 125
#define MANTISSA_B 52
#define EXPONENT_B 11
#define MASK 1023

static const char DIGIT_TABLE[200] = {
    '0', '0', '0', '1', '0', '2', '0', '3', '0', '4', '0', '5', '0', '6', '0',
    '7', '0', '8', '0', '9', '1', '0', '1', '1', '1', '2', '1', '3', '1', '4',
    '1', '5', '1', '6', '1', '7', '1', '8', '1', '9', '2', '0', '2', '1', '2',
    '2', '2', '3', '2', '4', '2', '5', '2', '6', '2', '7', '2', '8', '2', '9',
    '3', '0', '3', '1', '3', '2', '3', '3', '3', '4', '3', '5', '3', '6', '3',
    '7', '3', '8', '3', '9', '4', '0', '4', '1', '4', '2', '4', '3', '4', '4',
    '4', '5', '4', '6', '4', '7', '4', '8', '4', '9', '5', '0', '5', '1', '5',
    '2', '5', '3', '5', '4', '5', '5', '5', '6', '5', '7', '5', '8', '5', '9',
    '6', '0', '6', '1', '6', '2', '6', '3', '6', '4', '6', '5', '6', '6', '6',
    '7', '6', '8', '6', '9', '7', '0', '7', '1', '7', '2', '7', '3', '7', '4',
    '7', '5', '7', '6', '7', '7', '7', '8', '7', '9', '8', '0', '8', '1', '8',
    '2', '8', '3', '8', '4', '8', '5', '8', '6', '8', '7', '8', '8', '8', '9',
    '9', '0', '9', '1', '9', '2', '9', '3', '9', '4', '9', '5', '9', '6', '9',
    '7', '9', '8', '9', '9'
};

static inline uint64_t
umul128(uint64_t a, uint64_t b, uint64_t* productHi)
{
#if defined(UMUL128_DEFINED)
    return _umul128(a, b, productHi);
#else
#if defined(__SIZEOF_INT128__)
    __uint128_t product = (__uint128_t)a * b;
    *productHi = product >> 64;
    return (uint64_t)product;
#elif UINTPTR_MAX == 0xFFFFFFFF
    uint32_t a_lo = (uint32_t)a, a_hi = a >> 32;
    uint32_t b_lo = (uint32_t)b, b_hi = b >> 32;

    uint64_t p0 = (uint64_t)a_lo * b_lo;
    uint64_t p1 = (uint64_t)a_hi * b_lo + (p0 >> 32);
    uint64_t p2 = (uint64_t)a_lo * b_hi + (uint32_t)p1;
    uint64_t p3 = (uint64_t)a_hi * b_hi + (p1 >> 32) + (p2 >> 32);
    *productHi = p3;
    return (p2 << 32) | (uint32_t)p0;
#else
#error "Unsupported platform: 128-bit multiplication is not available"
#endif
#endif
}

typedef struct floating_64
{
    uint64_t mantissa;
    int32_t exponent;
} floating_64;

static inline uint64_t
shiftright128(uint64_t lo, uint64_t hi, uint32_t dist)
{
    return (hi << (64 - dist)) | (lo >> dist);
}

static inline uint64_t
mulShift64(uint64_t m, const uint64_t* mul, int32_t j)
{
    // m is maximum 55 bits
    uint64_t high1;                             // 128
    uint64_t low1 = umul128(m, mul[1], &high1); // 64
    uint64_t high0;                             // 64
    umul128(m, mul[0], &high0);                 // 0
    uint64_t sum = high0 + low1;
    if (sum < high0) {
        ++high1; // overflow into high1
    }
    return shiftright128(sum, high1, j - 64);
}

static inline uint64_t
mulShiftAll64(uint64_t m,
              const uint64_t* mul,
              int32_t j,
              uint64_t* vp,
              uint64_t* vm,
              uint32_t mmShift)
{
    *vp = mulShift64(4 * m + 2, mul, j);
    *vm = mulShift64(4 * m - 1 - mmShift, mul, j);
    return mulShift64(4 * m, mul, j);
}

static inline uint32_t
pow5Factor(uint64_t value)
{
    // 5 * m_inv_5 = 1 (mod 2^64)
    uint64_t m_inv_5 = 14757395258967641293u;
    //{ n | n = 0 (mod 2^64) } = 2^64 / 5
    uint64_t n_div_5 = 3689348814741910323u;
    uint32_t count = 0;
    for (;;) {
        value *= m_inv_5;
        if (value > n_div_5) {
            break;
        }
        ++count;
    }
    return count;
}

static inline int
multipleOfPowerOf5(uint64_t value, uint32_t p)
{
    return pow5Factor(value) >= p;
}

static inline uint32_t
decimalLength17(uint64_t m)
{
    if (m >= 10000000000000000L) {
        return 17;
    } else if (m >= 1000000000000000L) {
        return 16;
    } else if (m >= 100000000000000L) {
        return 15;
    } else if (m >= 10000000000000L) {
        return 14;
    } else if (m >= 1000000000000L) {
        return 13;
    } else if (m >= 100000000000L) {
        return 12;
    } else if (m >= 10000000000L) {
        return 11;
    } else if (m >= 1000000000L) {
        return 10;
    } else if (m >= 100000000L) {
        return 9;
    } else if (m >= 10000000L) {
        return 8;
    } else if (m >= 1000000L) {
        return 7;
    } else if (m >= 100000L) {
        return 6;
    } else if (m >= 10000L) {
        return 5;
    } else if (m >= 1000L) {
        return 4;
    } else if (m >= 100L) {
        return 3;
    } else if (m >= 10L) {
        return 2;
    } else {
        return 1;
    }
}

static inline uint64_t
umulh(uint64_t a, uint64_t b)
{
    uint64_t hi;
    umul128(a, b, &hi);
    return hi;
}

static inline int
multipleOfPowerOf2(uint64_t value, uint32_t p)
{
    return (value & ((1ull << p) - 1)) == 0;
}

static inline uint64_t
div5(uint64_t x)
{
    return umulh(x, 0xCCCCCCCCCCCCCCCDu) >> 2;
}

static inline uint64_t
div10(uint64_t x)
{
    return umulh(x, 0xCCCCCCCCCCCCCCCDu) >> 3;
}

static inline uint64_t
div100(uint64_t x)
{
    return umulh(x >> 2, 0x28F5C28F5C28F5C3u) >> 2;
}

static inline uint64_t
div1e8(uint64_t x)
{
    return umulh(x, 0xABCC77118461CEFDu) >> 26;
}

static inline int32_t
pow5bits(int32_t e)
{
    return (int32_t)(((((uint32_t)e) * 1217359) >> 19) + 1);
}

static inline uint32_t
log10Pow2(int32_t e)
{
    return (((uint32_t)e) * 78913) >> 18;
}

static inline uint32_t
log10Pow5(int32_t e)
{
    return (((uint32_t)e) * 732923) >> 20;
}

static inline floating_64
d2d(uint64_t mantissa, uint32_t exponent)
{
    int32_t e2;
    uint64_t m2;
    if (exponent == 0) {
        // We subtract 2 so that the bounds computation has 2 additional bits.
        e2 = 1 - MASK - MANTISSA_B - 2;
        m2 = mantissa;
    } else {
        e2 = (int32_t)exponent - MASK - MANTISSA_B - 2;
        m2 = (1ull << MANTISSA_B) | mantissa;
    }
    int even = (m2 & 1) == 0;
    int acceptBounds = even;
    // Step 2: Determine the interval of valid decimal representations.
    uint64_t mv = 4 * m2;
    // Implicit bool -> int conversion. True is 1, 0 is 0.
    uint32_t mmShift = mantissa != 0 || exponent <= 1;
    // We would compute mp and mm like this:
    // uint64_t mp = 4 * m2 + 2;
    // uint64_t mm = mv - 1 - mmShift;

    // Step 3: Convert to a decimal power base using 128-bit arithmetic.
    uint64_t vr, vp, vm;
    int32_t e10;
    int vmIsTrailingZeros = 0;
    int vrIsTrailingZeros = 0;
    if (e2 >= 0) {
        // I tried special-casing q == 0, but there was no effect on
        // performance. This expression is slightly faster than max(0,
        // log10Pow2(e2) - 1).
        uint32_t q = log10Pow2(e2) - (e2 > 3);
        e10 = (int32_t)q;
        int32_t k = DOUBLE_POW5_INV_BITCOUNT + pow5bits((int32_t)q) - 1;
        int32_t i = -e2 + (int32_t)q + k;
        vr = mulShiftAll64(m2, DOUBLE_POW5_INV_SPLIT[q], i, &vp, &vm, mmShift);
        if (q <= 21) {
            // This should use q <= 22, but I think 21 is also safe. Smaller
            // values may still be safe, but it's more difficult to reason about
            // them. Only one of mp, mv, and mm can be a multiple of 5, if any.
            uint32_t mvMod5 = ((uint32_t)mv) - 5 * ((uint32_t)div5(mv));
            if (mvMod5 == 0) {
                vrIsTrailingZeros = multipleOfPowerOf5(mv, q);
            } else if (acceptBounds) {
                // Same as min(e2 + (~mm & 1), pow5Factor(mm)) >= q
                // <=> e2 + (~mm & 1) >= q && pow5Factor(mm) >= q
                // <=> 1 && pow5Factor(mm) >= q, since e2 >= q.
                vmIsTrailingZeros = multipleOfPowerOf5(mv - 1 - mmShift, q);
            } else {
                // Same as min(e2 + 1, pow5Factor(mp)) >= q.
                vp -= multipleOfPowerOf5(mv + 2, q);
            }
        }
    } else {
        // This expression is slightly faster than max(0, log10Pow5(-e2) - 1).
        uint32_t q = log10Pow5(-e2) - (-e2 > 1);
        e10 = (int32_t)q + e2;
        int32_t i = -e2 - (int32_t)q;
        int32_t k = pow5bits(i) - DOUBLE_POW5_BITCOUNT;
        int32_t j = (int32_t)q - k;
        vr = mulShiftAll64(m2, DOUBLE_POW5_SPLIT[i], j, &vp, &vm, mmShift);
        if (q <= 1) {
            // {vr,vp,vm} is trailing zeros if {mv,mp,mm} has at least q
            // trailing 0 bits. mv = 4 * m2, so it always has at least two
            // trailing 0 bits.
            vrIsTrailingZeros = 1;
            if (acceptBounds) {
                // mm = mv - 1 - mmShift, so it has 1 trailing 0 bit iff mmShift
                // == 1.
                vmIsTrailingZeros = mmShift == 1;
            } else {
                // mp = mv + 2, so it always has at least one trailing 0 bit.
                --vp;
            }
        } else if (q < 63) {
            // We want to know if the full product has at least q trailing
            // zeros. We need to compute min(p2(mv), p5(mv) - e2) >= q
            // <=> p2(mv) >= q && p5(mv) - e2 >= q
            // <=> p2(mv) >= q (because -e2 >= q)
            vrIsTrailingZeros = multipleOfPowerOf2(mv, q);
        }
    }

    // Step 4: Find the shortest decimal representation in the interval of valid
    // representations.
    int32_t removed = 0;
    uint8_t lastRemovedDigit = 0;
    uint64_t output;
    // On average, we remove ~2 digits.
    if (vmIsTrailingZeros || vrIsTrailingZeros) {
        // General case, which happens rarely (~0.7%).
        for (;;) {
            uint64_t vpDiv10 = div10(vp);
            uint64_t vmDiv10 = div10(vm);
            if (vpDiv10 <= vmDiv10) {
                break;
            }
            uint32_t vmMod10 = ((uint32_t)vm) - 10 * ((uint32_t)vmDiv10);
            uint64_t vrDiv10 = div10(vr);
            uint32_t vrMod10 = ((uint32_t)vr) - 10 * ((uint32_t)vrDiv10);
            vmIsTrailingZeros &= vmMod10 == 0;
            vrIsTrailingZeros &= lastRemovedDigit == 0;
            lastRemovedDigit = (uint8_t)vrMod10;
            vr = vrDiv10;
            vp = vpDiv10;
            vm = vmDiv10;
            ++removed;
        }
        if (vmIsTrailingZeros) {
            for (;;) {
                uint64_t vmDiv10 = div10(vm);
                uint32_t vmMod10 = ((uint32_t)vm) - 10 * ((uint32_t)vmDiv10);
                if (vmMod10 != 0) {
                    break;
                }
                uint64_t vpDiv10 = div10(vp);
                uint64_t vrDiv10 = div10(vr);
                uint32_t vrMod10 = ((uint32_t)vr) - 10 * ((uint32_t)vrDiv10);
                vrIsTrailingZeros &= lastRemovedDigit == 0;
                lastRemovedDigit = (uint8_t)vrMod10;
                vr = vrDiv10;
                vp = vpDiv10;
                vm = vmDiv10;
                ++removed;
            }
        }
        if (vrIsTrailingZeros && lastRemovedDigit == 5 && vr % 2 == 0) {
            // Round even if the exact number is .....50..0.
            lastRemovedDigit = 4;
        }
        // We need to take vr + 1 if vr is outside bounds or we need to round
        // up.
        output = vr + ((vr == vm && (!acceptBounds || !vmIsTrailingZeros)) ||
                       lastRemovedDigit >= 5);
    } else {
        // Specialized for the common case (~99.3%). Percentages below are
        // relative to this.
        int roundUp = 0;
        uint64_t vpDiv100 = div100(vp);
        uint64_t vmDiv100 = div100(vm);
        if (vpDiv100 >
            vmDiv100) { // Optimization: remove two digits at a time (~86.2%).
            uint64_t vrDiv100 = div100(vr);
            uint32_t vrMod100 = ((uint32_t)vr) - 100 * ((uint32_t)vrDiv100);
            roundUp = vrMod100 >= 50;
            vr = vrDiv100;
            vp = vpDiv100;
            vm = vmDiv100;
            removed += 2;
        }
        // Loop iterations below (approximately), without optimization above:
        // 0: 0.03%, 1: 13.8%, 2: 70.6%, 3: 14.0%, 4: 1.40%, 5: 0.14%, 6+: 0.02%
        // Loop iterations below (approximately), with optimization above:
        // 0: 70.6%, 1: 27.8%, 2: 1.40%, 3: 0.14%, 4+: 0.02%
        for (;;) {
            uint64_t vpDiv10 = div10(vp);
            uint64_t vmDiv10 = div10(vm);
            if (vpDiv10 <= vmDiv10) {
                break;
            }
            uint64_t vrDiv10 = div10(vr);
            uint32_t vrMod10 = ((uint32_t)vr) - 10 * ((uint32_t)vrDiv10);
            roundUp = vrMod10 >= 5;
            vr = vrDiv10;
            vp = vpDiv10;
            vm = vmDiv10;
            ++removed;
        }
        // We need to take vr + 1 if vr is outside bounds or we need to round
        // up.
        output = vr + (vr == vm || roundUp);
    }
    int32_t exp = e10 + removed;

    floating_64 fd;
    fd.exponent = exp;
    fd.mantissa = output;
    return fd;
}

static inline int
to_chars(floating_64 v, int sign, WriteBuffer* buf)
{
    // Step 5: Print the decimal representation.
    int index = 0;
    unsigned char* result = buf->buffer + buf->size;
    if (sign) {
        result[index++] = '-';
    }

    uint64_t output = v.mantissa;
    uint32_t olength = decimalLength17(output);

    uint32_t i = 0;
    // We prefer 32-bit operations, even on 64-bit platforms.
    // We have at most 17 digits, and uint32_t can store 9 digits.
    // If output doesn't fit into uint32_t, we cut off 8 digits,
    // so the rest will fit into uint32_t.
    if ((output >> 32) != 0) {
        // Expensive 64-bit division.
        uint64_t q = div1e8(output);
        uint32_t output2 = ((uint32_t)output) - 100000000 * ((uint32_t)q);
        output = q;

        uint32_t c = output2 % 10000;
        output2 /= 10000;
        uint32_t d = output2 % 10000;
        uint32_t c0 = (c % 100) << 1;
        uint32_t c1 = (c / 100) << 1;
        uint32_t d0 = (d % 100) << 1;
        uint32_t d1 = (d / 100) << 1;
        memcpy(result + index + olength - 1, DIGIT_TABLE + c0, 2);
        memcpy(result + index + olength - 3, DIGIT_TABLE + c1, 2);
        memcpy(result + index + olength - 5, DIGIT_TABLE + d0, 2);
        memcpy(result + index + olength - 7, DIGIT_TABLE + d1, 2);
        i += 8;
    }
    uint32_t output2 = (uint32_t)output;
    while (output2 >= 10000) {
        uint32_t c = output2 % 10000;
        output2 /= 10000;
        uint32_t c0 = (c % 100) << 1;
        uint32_t c1 = (c / 100) << 1;
        memcpy(result + index + olength - i - 1, DIGIT_TABLE + c0, 2);
        memcpy(result + index + olength - i - 3, DIGIT_TABLE + c1, 2);
        i += 4;
    }
    if (output2 >= 100) {
        uint32_t c = (output2 % 100) << 1;
        output2 /= 100;
        memcpy(result + index + olength - i - 1, DIGIT_TABLE + c, 2);
        i += 2;
    }
    if (output2 >= 10) {
        uint32_t c = output2 << 1;
        // We can't use memcpy here: the decimal dot goes between these two
        // digits.
        result[index + olength - i] = DIGIT_TABLE[c + 1];
        result[index] = DIGIT_TABLE[c];
    } else {
        result[index] = (char)('0' + output2);
    }

    if (olength > 1) {
        result[index + 1] = '.';
        index += olength + 1;
    } else {
        ++index;
    }

    int32_t exp = v.exponent + (int32_t)olength - 1;
    if (!exp) {
        buf->size += index;
        return 0;
    }

    result[index++] = 'e';
    if (exp < 0) {
        result[index++] = '-';
        exp = -exp;
    }

    if (exp >= 100) {
        int32_t c = exp % 10;
        memcpy(result + index, DIGIT_TABLE + 2 * (exp / 10), 2);
        result[index + 2] = (char)('0' + c);
        index += 3;
    } else if (exp >= 10) {
        memcpy(result + index, DIGIT_TABLE + 2 * exp, 2);
        index += 2;
    } else {
        result[index++] = (char)('0' + exp);
    }

    buf->size += index;
    return 0;
}

int
_Float_AsJson(WriteBuffer* buf, PyObject* obj, UNUSED ConvParams* _)
{
    if (WriteBuffer_Resize(buf, buf->size + 25) < 0) {
        return -1;
    }

    double f;
    int sign;
    uint32_t exponent;
    uint64_t mantissa, bits = 0;
    f = PyFloat_AS_DOUBLE(obj);
    memcpy(&bits, &f, sizeof(double));

    sign = ((bits >> (MANTISSA_B + EXPONENT_B)) & 1) != 0;
    mantissa = bits & ((1ull << MANTISSA_B) - 1);
    exponent = (uint32_t)((bits >> MANTISSA_B) & ((1u << EXPONENT_B) - 1));
    if (FT_UNLIKELY(exponent == ((1u << EXPONENT_B) - 1u) ||
                    (exponent == 0 && mantissa == 0))) {
        if (mantissa) {
            return WriteBuffer_ConcatSize(buf, "NaN", 3);
        }
        if (sign) {
            BUFFER_CONCAT_CHAR(buf, '-');
        }
        if (exponent) {
            return WriteBuffer_ConcatSize(buf, "Infinity", 8);
        }
        return WriteBuffer_ConcatSize(buf, "0.0", 3);
    }

    return to_chars(d2d(mantissa, exponent), sign, buf);
}