// std
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// builder
#include <crc_soft.h>
#include <bin_header.h>

const uint32_t header_load_addr;
const uint32_t header_boot_addr;
const uint32_t header_firmware_size;

static bool ReflectTest(void)
{
    bool res = true;

    const struct {
        uint32_t value;
        uint32_t reflect;
    } reflectCases [] = {
        {.value = 0x00000000, .reflect = 0x00000000},
        {.value = 0xFFFFFFFF, .reflect = 0xFFFFFFFF},
        {.value = 0x00000001, .reflect = 0x80000000},
        {.value = 0x00F000F0, .reflect = 0x0F000F00},
        {.value = 0x0F0F0F0F, .reflect = 0xF0F0F0F0},
        {.value = 0xAAAAAAAA, .reflect = 0x55555555},
        {.value = 0x12345678, .reflect = 0x1E6A2C48},
        {.value = 0x80000000, .reflect = 0x00000001},
        {.value = 0x1E2D3C4B, .reflect = 0xD23CB478},
        {.value = 0x1234BEEF, .reflect = 0xF77D2C48},
        {.value = 0x1E2DC0FF, .reflect = 0xFF03B478},
        {.value = 0x3C3C1357, .reflect = 0xEAC83C3C},
        {.value = 0x7E812468, .reflect = 0x1624817E},
    };

    for (size_t i = 0; i < ELOF(reflectCases); i++)
    {
        const uint16_t reflect8 = CRC_SOFT_Reflect8(reflectCases[i].value);
        res = res && (reflect8 == (reflectCases[i].reflect >> 24));

        const uint16_t reflect16 = CRC_SOFT_Reflect16(reflectCases[i].value);
        res = res && (reflect16 == (reflectCases[i].reflect >> 16));

        const uint32_t reflect32 = CRC_SOFT_Reflect32(reflectCases[i].value);
        res = res && (reflect32 == reflectCases[i].reflect);
    }
    return res;
}

static bool CrcTable16Test(void)
{
    bool res = true;
    static uint16_t tableCrc16[CRC_SOFT_TABLE_LEN];
    const char checkStr[] = "123456789";
    CRC_SOFT_GenTable16(tableCrc16, CRC_SOFT_CCITT_16_POLY);
    uint16_t crc16 = CRC_SOFT_CCITT_16_INIT;
    crc16 = CRC_SOFT_CalcPartTable16(checkStr, 4, crc16, tableCrc16);
    crc16 = CRC_SOFT_CalcPartTable16(checkStr + 4, 5, crc16, tableCrc16);
    crc16 = crc16 ^ CRC_SOFT_CCITT_16_XOR;
    res = res && (crc16 == 0x29B1);
    res = res && (memcmp(tableCrc16, CRC_SOFT_CCITT_16_Table, sizeof(tableCrc16)) == 0);
    return res;
}

static bool CrcTable32Test(void)
{
    bool res = true;
    static uint32_t tableCrc32[CRC_SOFT_TABLE_LEN];
    const char checkStr[] = "123456789";
    CRC_SOFT_GenTable32(tableCrc32, CRC_SOFT_IEEE_802_3_POLY);
    uint32_t crc32 = CRC_SOFT_IEEE_802_3_INIT;
    crc32 = CRC_SOFT_CalcPartTable32(checkStr, 3, crc32, tableCrc32);
    crc32 = CRC_SOFT_CalcPartTable32(checkStr + 3, 6, crc32, tableCrc32);
    crc32 = crc32 ^ CRC_SOFT_IEEE_802_3_XOR;
    res = res && (crc32 == 0xCBF43926);
    res = res && (memcmp(tableCrc32, CRC_SOFT_IEEE_802_3_Table, sizeof(tableCrc32)) == 0);
    return res;
}

static bool Crc16Test(void)
{
    bool res = true;
    const char checkStr[] = "123456789";
    uint16_t crc16 = CRC_SOFT_CCITT_16_INIT;
    crc16 = CRC_SOFT_CalcPart16(checkStr, 4, crc16, CRC_SOFT_CCITT_16_POLY);
    crc16 = CRC_SOFT_CalcPart16(checkStr + 4, 5, crc16, CRC_SOFT_CCITT_16_POLY);
    crc16 = crc16 ^ CRC_SOFT_CCITT_16_XOR;
    res = res && (crc16 == 0x29B1);
    return res;
}

static bool Crc32Test(void)
{
    bool res = true;
    const char checkStr[] = "123456789";
    uint32_t crc32 = CRC_SOFT_IEEE_802_3_INIT;
    crc32 = CRC_SOFT_CalcPart32(checkStr, 3, crc32, CRC_SOFT_IEEE_802_3_POLY);
    crc32 = CRC_SOFT_CalcPart32(checkStr + 3, 6, crc32, CRC_SOFT_IEEE_802_3_POLY);
    crc32 = crc32 ^ CRC_SOFT_IEEE_802_3_XOR;
    res = res && (crc32 == 0xCBF43926);
    return res;
}

int main(int argc, char * argv[])
{
    (void)argc;
    (void)argv;
    bool status = true;

    const BIN_HEADER_s *header = BIN_HEADER_GetHeader();
    BIN_HEADER_Print(header);
    BIN_HEADER_PrintShort(header);
    BIN_HEADER_CheckInit();

    RUN_TEST(BIN_HEADER_CheckHeader(header), status);
    RUN_TEST(PRJ_DEFINE_EXAMPLE == 1, status);
    RUN_TEST(BC_DEFINE_EXAMPLE == 1, status);
    RUN_TEST(ReflectTest(), status);
    RUN_TEST(CrcTable16Test(), status);
    RUN_TEST(CrcTable32Test(), status);
    RUN_TEST(Crc16Test(), status);
    RUN_TEST(Crc32Test(), status);
    END_TEST(status);

    return status ? 0 : 1;
}
