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

typedef struct
{
    uint32_t poly;
    uint32_t init;
    uint32_t xor;
    bool refIn;
    bool refOut;
    uint32_t checkCrc;
    const void *checkTable;
} CrcParams_s;

static const CrcParams_s crc8ParamsCases[] = {
    {CRC_SOFT_CCITT_8_POLY, CRC_SOFT_CCITT_8_INIT, CRC_SOFT_CCITT_8_XOR, CRC_SOFT_CCITT_8_REFIN, CRC_SOFT_CCITT_8_REFOUT, 0xF4, CRC_SOFT_CCITT_8_Table},
    {0x1D, 0xFF, 0xFF, false, false, 0x4B, NULL}, // CRC-8-SAE-J1850
    {0x31, 0x00, 0x00, true,  true,  0xA1, NULL}, // CRC-8-MAXIM
    {0x07, 0x00, 0x55, false, false, 0xA1, NULL}, // CRC-8-ITU
    {0x07, 0xFF, 0x00, true,  true,  0xD0, NULL}, // CRC-8-ROHC
};

static const CrcParams_s crc16ParamsCases[] = {
    {CRC_SOFT_CCITT_16_POLY, CRC_SOFT_CCITT_16_INIT, CRC_SOFT_CCITT_16_XOR, CRC_SOFT_CCITT_16_REFIN, CRC_SOFT_CCITT_16_REFOUT, 0x29B1, CRC_SOFT_CCITT_16_Table},
    {0x8005, 0x0000, 0x0000, true,  true,  0xBB3D, NULL}, // CRC-16-ARC
    {0x8005, 0xFFFF, 0x0000, true,  true,  0x4B37, NULL}, // CRC-16-MODBUS
    {0x8005, 0xFFFF, 0xFFFF, true,  true,  0xB4C8, NULL}, // CRC-16-USB
    {0x1021, 0xFFFF, 0xFFFF, false, false, 0xD64E, NULL}, // CRC-16-GENIBUS
};

static const CrcParams_s crc32ParamsCases[] = {
    {CRC_SOFT_IEEE_802_3_POLY, CRC_SOFT_IEEE_802_3_INIT, CRC_SOFT_IEEE_802_3_XOR, CRC_SOFT_IEEE_802_3_REFIN, CRC_SOFT_IEEE_802_3_REFOUT, 0xCBF43926, CRC_SOFT_IEEE_802_3_Table},
    {0x04C11DB7, 0xFFFFFFFF, 0x00000000, false, false, 0x0376E6E7, NULL}, // CRC-32-MPEG-2
    {0x04C11DB7, 0xFFFFFFFF, 0xFFFFFFFF, false, false, 0xFC891918, NULL}, // CRC-32-BZIP2
    {0x1EDC6F41, 0xFFFFFFFF, 0xFFFFFFFF, true,  true,  0xE3069283, NULL}, // CRC-32C
    {0xA833982B, 0xFFFFFFFF, 0xFFFFFFFF, true,  true,  0x87315576, NULL}, // CRC-32D
    {0x04C11DB7, 0x00000000, 0xFFFFFFFF, false, true,  0x765E7680, NULL}, // CRC-32-POSIX
    {0xF4ACFB13, 0xFFFFFFFF, 0xFFFFFFFF, true,  false, 0x1697D06A, NULL}, // CRC-32-AUTOSAR
};

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

static bool Crc8Test(void)
{
    bool res = true;
    const char checkStr[] = "123456789";
    for (size_t i = 0; i < ELOF(crc8ParamsCases); i++)
    {
        const CrcParams_s *param = &crc8ParamsCases[i];
        uint8_t crc8;
        crc8 = CRC_SOFT_CalcPart8(checkStr, 4, param->init, param->refIn, param->poly);
        crc8 = CRC_SOFT_CalcPart8(checkStr + 4, 5, crc8, param->refIn, param->poly);
        crc8 = crc8 ^ param->xor;
        res = res && (crc8 == param->checkCrc);
    }
    return res;
}

static bool Crc8TableTest(void)
{
    bool res = true;
    static uint8_t tableCrc8[CRC_SOFT_TABLE_LEN];
    const char checkStr[] = "123456789";
    for (size_t i = 0; i < ELOF(crc8ParamsCases); i++)
    {
        const CrcParams_s *param = &crc8ParamsCases[i];
        CRC_SOFT_GenTable8(tableCrc8, param->refIn, param->poly);
        uint8_t crc8;
        crc8 = CRC_SOFT_CalcPartTable8(checkStr, 4, param->init, param->refIn, tableCrc8);
        crc8 = CRC_SOFT_CalcPartTable8(checkStr + 4, 5, crc8, param->refIn, tableCrc8);
        crc8 = crc8 ^ param->xor;
        res = res && (crc8 == param->checkCrc);
        if (param->checkTable != NULL)
        {
            res = res && (memcmp(tableCrc8, param->checkTable, sizeof(tableCrc8)) == 0);
        }
    }
    return res;
}

static bool Crc16Test(void)
{
    bool res = true;
    const char checkStr[] = "123456789";
    for (size_t i = 0; i < ELOF(crc16ParamsCases); i++)
    {
        const CrcParams_s *param = &crc16ParamsCases[i];
        uint16_t crc16;
        crc16 = CRC_SOFT_CalcPart16(checkStr, 4, param->init, param->refIn, param->poly);
        crc16 = CRC_SOFT_CalcPart16(checkStr + 4, 5, crc16, param->refIn, param->poly);
        crc16 = crc16 ^ param->xor;
        res = res && (crc16 == param->checkCrc);
    }
    return res;
}

static bool Crc16TableTest(void)
{
    bool res = true;
    static uint16_t tableCrc16[CRC_SOFT_TABLE_LEN];
    const char checkStr[] = "123456789";
    for (size_t i = 0; i < ELOF(crc16ParamsCases); i++)
    {
        const CrcParams_s *param = &crc16ParamsCases[i];
        CRC_SOFT_GenTable16(tableCrc16, param->refIn, param->poly);
        uint16_t crc16;
        crc16 = CRC_SOFT_CalcPartTable16(checkStr, 4, param->init, param->refIn, tableCrc16);
        crc16 = CRC_SOFT_CalcPartTable16(checkStr + 4, 5, crc16, param->refIn, tableCrc16);
        crc16 = crc16 ^ param->xor;
        res = res && (crc16 == param->checkCrc);
        if (param->checkTable != NULL)
        {
            res = res && (memcmp(tableCrc16, param->checkTable, sizeof(tableCrc16)) == 0);
        }
    }
    return res;
}

static bool Crc32Test(void)
{
    bool res = true;
    const char checkStr[] = "123456789";
    for (size_t i = 0; i < ELOF(crc32ParamsCases); i++)
    {
        const CrcParams_s *param = &crc32ParamsCases[i];
        uint32_t crc32;
        crc32 = CRC_SOFT_CalcPart32(checkStr, 3, param->init, param->refIn, param->poly);
        crc32 = CRC_SOFT_CalcPart32(checkStr + 3, 6, crc32, param->refIn, param->poly);
        crc32 = crc32 ^ param->xor;
        res = res && (crc32 == param->checkCrc);
    }
    return res;
}

static bool Crc32TableTest(void)
{
    bool res = true;
    static uint32_t tableCrc32[CRC_SOFT_TABLE_LEN];
    const char checkStr[] = "123456789";
    for (size_t i = 0; i < ELOF(crc32ParamsCases); i++)
    {
        const CrcParams_s *param = &crc32ParamsCases[i];
        CRC_SOFT_GenTable32(tableCrc32, param->refIn, param->poly);
        uint32_t crc32;
        crc32 = CRC_SOFT_CalcPartTable32(checkStr, 3, param->init, param->refIn, tableCrc32);
        crc32 = CRC_SOFT_CalcPartTable32(checkStr + 3, 6, crc32, param->refIn, tableCrc32);
        crc32 = crc32 ^ param->xor;
        res = res && (crc32 == param->checkCrc);
        if (param->checkTable != NULL)
        {
            res = res && (memcmp(tableCrc32, param->checkTable, sizeof(tableCrc32)) == 0);
        }
    }
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
    RUN_TEST(Crc8Test(), status);
    RUN_TEST(Crc8TableTest(), status);
    RUN_TEST(Crc16Test(), status);
    RUN_TEST(Crc16TableTest(), status);
    RUN_TEST(Crc32Test(), status);
    RUN_TEST(Crc32TableTest(), status);
    END_TEST(status);

    return status ? 0 : 1;
}
