#include "bnn_model.h"

const uint16_t L0_WEIGHTS[64] = {
    1071, 16954, 14844, 45748, 50371, 38372, 23960, 63310, 27058, 63647, 63445, 2089, 55295, 27802, 59356, 50923, 50503, 360, 6445, 63484, 10481, 27281, 28379, 46429, 50992, 29556, 45932, 14834, 41509, 63299, 19459, 53171, 24732, 2081, 12654, 2107, 15355, 10415, 51163, 32808, 56407, 47292, 14663, 45358, 59389, 64967, 46460, 50507, 45324, 41509, 10729, 12358, 2187, 15359, 8440, 63319, 2610, 2219, 98, 31697, 12623, 50704, 31425, 21200
};

const int16_t L0_THRESHOLDS[64] = {
    -1921, -174, -182, -178, 12, -126, 587, 230, 326, 17, 209, -92, 287, 608, 178, 275, -122, -695, -187, 66, -115, 118, 711, -43, 25, -112, -537, 89, -528, -5, 148, 663, -174, -126, -594, -51, 31, 62, 301, -694, 192, 315, -70, -297, 247, 199, -426, -131, -694, -637, 1511, -601, -137, -253, -376, 10656, 330, 48, -525, 2, -399, 25, 77, -275
};

const uint32_t L1_WEIGHTS[64][2] = {
    {0x038FE6CAu, 0x9D7826FBu},
    {0x156B16EFu, 0x0ACC4517u},
    {0x03DC2EC6u, 0xECAA1FF3u},
    {0xC3CDDC50u, 0xBA113F77u},
    {0xDD23112Bu, 0x327DE904u},
    {0x116B17AFu, 0x00CE4413u},
    {0xA29ECE55u, 0xAD3217F3u},
    {0x62B52741u, 0xF01A3FF7u},
    {0x7432754Cu, 0x7942F734u},
    {0x62D6FE53u, 0xAD8693D3u},
    {0x5C295968u, 0x5455E508u},
    {0x150B132Bu, 0x1CC67944u},
    {0x7D219039u, 0x5BD5E004u},
    {0x0B8D0AD7u, 0x8E8F3CC8u},
    {0x229E2617u, 0xAD889EF3u},
    {0x42D62FD3u, 0xA54A3AFBu},
    {0x2022261Fu, 0xCCCC6596u},
    {0xE2DCAED7u, 0xA91A87F3u},
    {0x3F942072u, 0xE5FF984Cu},
    {0xBD29112Du, 0x56A9D124u},
    {0x439FEE57u, 0xAC121EFBu},
    {0xE296AE57u, 0xA40A16FBu},
    {0x429EEEC2u, 0xAD162EF3u},
    {0x8149832Bu, 0x86F769CAu},
    {0x076983A2u, 0x868760DAu},
    {0x0FED8E87u, 0x968520EDu},
    {0x42D6EF42u, 0xB8A0BAFFu},
    {0x3D69103Eu, 0x54B9CC04u},
    {0x5D2BD12Bu, 0x14FDD00Cu},
    {0xDD62593Au, 0x7365E30Cu},
    {0x3D2B9139u, 0x5AE5E00Cu},
    {0x42D6EFD1u, 0xA90E1EF3u},
    {0xC2D6BFD6u, 0xACB23A73u},
    {0x9D6B113Eu, 0x588BE924u},
    {0x3D2851BDu, 0x1EFB490Cu},
    {0x0D0B922Eu, 0x48ADF008u},
    {0x42DEAE46u, 0x8D8213F3u},
    {0x42D6E6C7u, 0xED5AB2FBu},
    {0x62B7DED2u, 0xAB28A7F3u},
    {0xC3DE2E56u, 0xAC8217F3u},
    {0x2F942126u, 0x65FE11C4u},
    {0xF07AF568u, 0x7118DA16u},
    {0x43DD2F52u, 0xA84A11F2u},
    {0xE3D4AEC3u, 0xED98BFFBu},
    {0x3D2191BDu, 0x53E5C804u},
    {0xFC21112Cu, 0x13F5C708u},
    {0x05499AABu, 0x869F605Fu},
    {0x056F86A3u, 0x86D748DEu},
    {0xBD21112Eu, 0x7655E10Cu},
    {0x82DEAFC6u, 0xAC921ADBu},
    {0x6284AEC1u, 0xCD82A3BBu},
    {0x1D291028u, 0x53C5E544u},
    {0x3E9EE540u, 0xFB889237u},
    {0xDD2B1038u, 0x5F5DE50Cu},
    {0x3D684139u, 0x5B3DE104u},
    {0x6294BEC7u, 0xA5821EFBu},
    {0x1D601129u, 0x1AE1490Cu},
    {0x1D2991ADu, 0x77E14D04u},
    {0x0BCD8AD3u, 0x96E53849u},
    {0x63D6AEC2u, 0xA882B2FBu},
    {0x25490B2Bu, 0x37EE6104u},
    {0x1D61113Fu, 0x5735E104u},
    {0xF472756Cu, 0x695AFA32u},
    {0x62F6F6D3u, 0x8D7436FBu}
};

const uint32_t L2_WEIGHTS[32][4] = {
    {0x62B4EFD5u, 0xCD1E12DAu, 0x1B27D460u, 0xB405AC70u},
    {0xF0327178u, 0x697AFFA5u, 0xEE0473A4u, 0x89F4B70Cu},
    {0x9D2B112Fu, 0x56176504u, 0xEC826B92u, 0xC3E84293u},
    {0x9D29902Fu, 0x12AD6405u, 0xF7892398u, 0xED6F43CBu},
    {0xF2966FC4u, 0xAD3692FAu, 0x917CD54Eu, 0x340AB860u},
    {0x9D6B1168u, 0x56C5C464u, 0xEEE87F9Fu, 0x6BDED69Bu},
    {0x9D21912Bu, 0x52376524u, 0xEEB82B9Bu, 0xEBCC029Fu},
    {0x0FCD8E93u, 0x96A5214Au, 0x81BE984Au, 0xEE2B3C51u},
    {0x0FAD8783u, 0xDEA5257Au, 0x00FF9E5Au, 0xEB3B58D1u},
    {0xF132756Cu, 0x6952DB95u, 0x7F2D2BB1u, 0x15E4027Eu},
    {0x7294E4D5u, 0xED12BEF3u, 0x311DC463u, 0x0D361965u},
    {0x1D29902Du, 0x1EFB692Cu, 0xE4C16795u, 0xEEC9A28Fu},
    {0xE3D52EC4u, 0xA11292F2u, 0x12358C41u, 0xB7352A20u},
    {0x0FED8E93u, 0x96AD24CCu, 0x80FA9807u, 0xEE6B18F3u},
    {0x9D4B913Bu, 0x53EDE10Cu, 0x7CD0378Eu, 0x73EA538Au},
    {0x1D29917Fu, 0x52CD4C64u, 0xE5E865AAu, 0x62F1D2DBu},
    {0x7032F16Cu, 0x695ADFA5u, 0x77E573F4u, 0x1D84A70Cu},
    {0x62D46CD5u, 0xED5A26DBu, 0x9874D040u, 0x1A34A834u},
    {0x9D19133Bu, 0x5EC16524u, 0x66C2258Bu, 0xEFCED7CBu},
    {0xF072756Cu, 0x6952D685u, 0x5E4371E4u, 0x10B4264Fu},
    {0x62D62EC4u, 0xE130BEF3u, 0x1117D840u, 0x1421F8B9u},
    {0x72B46564u, 0x64709BFBu, 0x122FC67Cu, 0xF4365870u},
    {0x0FCD8E93u, 0x9685284Au, 0xA19D881Bu, 0xF54B5AD3u},
    {0xC2DEEFD6u, 0xAD1616D3u, 0x113E8862u, 0x16300B34u},
    {0x9D23113Au, 0x120DE904u, 0xEFC12333u, 0xE9CA57CBu},
    {0x3D29113Au, 0x52F76DECu, 0xEFE02209u, 0xE9FC11DBu},
    {0x9D2B193Au, 0x14C5D024u, 0xCFD9279Cu, 0xEB4712DBu},
    {0x62D6EED4u, 0xED3A92DEu, 0x1904D0E4u, 0x51058A20u},
    {0x0F8D8A83u, 0x96A5247Au, 0x829A9A4Eu, 0xF30B3990u},
    {0x9D29D12Du, 0x529D492Cu, 0xE6C32BA8u, 0xE9CD76CBu},
    {0x62967CD4u, 0xAB78BFFBu, 0x001CC961u, 0x1A3ED970u},
    {0x72DE6ED5u, 0xAD1896FBu, 0x3307D8CEu, 0x961599B4u}
};

const uint16_t L1_THRESHOLDS[64] = {
    28, 41, 30, 28, 25, 43, 30, 7, 29, 37, 38, 34, 23, 37, 48, 18, 32, 64, 31, 51, 17, 42, 25, 32, 29, 35, 25, 53, 38, 33, 37, 44, 52, 59, 31, 23, 26, 36, 37, 18, 30, 32, 35, 28, 34, 48, 34, 31, 54, 29, 0, 39, 32, 35, 64, 26, 35, 19, 35, 27, 32, 0, 30, 31
};

const uint16_t L2_THRESHOLDS[32] = {
    56, 58, 78, 77, 63, 66, 43, 70, 67, 61, 58, 68, 71, 67, 58, 64, 59, 81, 59, 63, 59, 63, 72, 63, 73, 67, 123, 54, 70, 61, 50, 70
};

const uint32_t OUT_WEIGHTS[5] = {0xF3E67C70u, 0xAD428AFAu, 0xB34FCC61u, 0x6F3069A5u, 0x399D4F3Fu};
const uint16_t OUT_THRESHOLD = 81;


static inline uint8_t bit_at(const uint32_t *w, int words, int nbits, int j)
{
    // Exporter writes each row as one big-endian-looking hexadecimal
    // integer: feature 0 is the MSB of the first 32-bit word.
    (void)words;
    (void)nbits;
    const int word = j / 32;
    const int bit_in_word = 31 - (j % 32);
    return (uint8_t)((w[word] >> bit_in_word) & 1u);
}

static inline uint8_t bit_at16(uint16_t w, int j)
{
    return (uint8_t)((w >> (15 - j)) & 1u);
}

void bnn_forward_q8(const uint8_t x_q8[BNN_INPUTS],
                    uint8_t l0[BNN_L0_OUT],
                    uint8_t l1[BNN_L1_OUT],
                    uint8_t l2[BNN_L2_OUT],
                    uint8_t *out)
{
    // Layer 0: signed sum of +/- uint8 inputs.
    for (int n = 0; n < BNN_L0_OUT; ++n) {
        int32_t acc = 0;
        for (int j = 0; j < BNN_INPUTS; ++j) {
            acc += bit_at16(L0_WEIGHTS[n], j) ? (int32_t)x_q8[j]
                                             : -(int32_t)x_q8[j];
        }
        l0[n] = (acc >= (int32_t)L0_THRESHOLDS[n]) ? 1 : 0;
    }

    // Layer 1: input is l0 only, 64 bits.
    for (int n = 0; n < BNN_L1_OUT; ++n) {
        uint32_t pc = 0;
        for (int j = 0; j < BNN_L0_OUT; ++j) {
            uint8_t wb = bit_at(L1_WEIGHTS[n], 2, 64, j);
            pc += (wb == l0[j]);
        }
        l1[n] = (pc >= L1_THRESHOLDS[n]) ? 1 : 0;
    }

    // Layer 2: dense concatenation [l0 | l1] = 128 bits.
    for (int n = 0; n < BNN_L2_OUT; ++n) {
        uint32_t pc = 0;
        for (int j = 0; j < 128; ++j) {
            uint8_t xb = (j < 64) ? l0[j] : l1[j - 64];
            uint8_t wb = bit_at(L2_WEIGHTS[n], 4, 128, j);
            pc += (wb == xb);
        }
        l2[n] = (pc >= L2_THRESHOLDS[n]) ? 1 : 0;
    }

    // Output: dense concatenation [l0 | l1 | l2] = 160 bits.
    uint32_t pc = 0;
    for (int j = 0; j < 160; ++j) {
        uint8_t xb;
        if (j < 64) xb = l0[j];
        else if (j < 128) xb = l1[j - 64];
        else xb = l2[j - 128];

        uint8_t wb = bit_at(OUT_WEIGHTS, 5, 160, j);
        pc += (wb == xb);
    }
    *out = (pc >= OUT_THRESHOLD) ? 1 : 0;
}

uint8_t bnn_predict_q8(const uint8_t x_q8[BNN_INPUTS])
{
    uint8_t l0[BNN_L0_OUT];
    uint8_t l1[BNN_L1_OUT];
    uint8_t l2[BNN_L2_OUT];
    uint8_t out;
    bnn_forward_q8(x_q8, l0, l1, l2, &out);
    return out;
}
