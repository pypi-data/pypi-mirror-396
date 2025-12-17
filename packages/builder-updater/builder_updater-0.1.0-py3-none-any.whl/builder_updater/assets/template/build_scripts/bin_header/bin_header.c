// std
#include <stdio.h>
#include <inttypes.h>

// builder
#include <crc_soft.h>
#include "bin_header.h"

extern uint32_t header_load_addr;
extern uint32_t header_boot_addr;
extern uint32_t header_firmware_size;

#if (BIN_HEADER_CRC_TABLE_EN == 1)
static uint32_t crc32Table[CRC_SOFT_TABLE_LEN];
#define CALC_CRC32(buf_, size_, crc_) CRC_SOFT_CalcPartTable32(buf_, size_, crc_, CRC_SOFT_IEEE_802_3_REFIN, crc32Table);
#else
#define CALC_CRC32(buf_, size_, crc_) CRC_SOFT_CalcPart32(buf_, size_, crc_, CRC_SOFT_IEEE_802_3_REFIN, CRC_SOFT_IEEE_802_3_POLY);
#endif

static const BIN_HEADER_s __attribute__((section(".header"))) binHeader =
{
    .beginMagic = BIN_HEADER_BEGIN_MAGIC,
    .hdrVer.major = BIN_HEADER_MAJOR_VERSION,
    .hdrVer.minor = BIN_HEADER_MINOR_VERSION,
    .hdrVer.patch = BIN_HEADER_PATCH_VERSION,
    .fwVer.major = BIN_HEADER_INVALID_VERSION,
    .fwVer.minor = BIN_HEADER_INVALID_VERSION,
    .fwVer.patch = BIN_HEADER_INVALID_VERSION,
    .prjName = BUILDER_PRJ_NAME,
    .bcName = BUILDER_BC_NAME,
#if !defined(__x86_64__) && !defined(__i386__)
    .fwInfo.loadAddr = (uintptr_t)&header_load_addr,
    .fwInfo.bootAddr = (uintptr_t)&header_boot_addr,
    .fwInfo.size = (uintptr_t)&header_firmware_size,
#endif
    .fwInfo.hash = {0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
                    0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
                    0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
                    0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE, 0xEE},
    .fwInfo.crc = 0x00000000,
    .gitInfo.rev = "empty",
    .gitInfo.date = "empty",
    .gitInfo.hash = {0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
                     0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
                     0xEE, 0xEE, 0xEE, 0xEE, 0xEE,
                     0xEE, 0xEE, 0xEE, 0xEE, 0xEE},
    .endMagic = BIN_HEADER_END_MAGIC,
    .crc = 0x00000000
};

const BIN_HEADER_s * BIN_HEADER_GetHeader(void)
{
    return &binHeader;
}

void BIN_HEADER_Print(const BIN_HEADER_s *header)
{
    printf("\r\n------------------------------------------------------------\r\n");
    printf("Header ver:     %u.%u.%u\r\n", header->hdrVer.major, header->hdrVer.minor, header->hdrVer.patch);
    printf("Firmware ver:   %u.%u.%u\r\n", header->fwVer.major, header->fwVer.minor, header->fwVer.patch);
    printf("Project:        %.*s\r\n", (int)sizeof(header->prjName), header->prjName);
    printf("Build config:   %.*s\r\n", (int)sizeof(header->bcName), header->bcName);
#if !defined(__x86_64__) && !defined(__i386__)
    printf("Fw load addr:   0x%08" PRIX32 "\r\n", header->fwInfo.loadAddr);
    printf("Fw boot addr:   0x%08" PRIX32 "\r\n", header->fwInfo.bootAddr);
    printf("Fw size:        0x%08" PRIX32 " (%" PRIu32 " B)\r\n", header->fwInfo.size, header->fwInfo.size);
#endif
    printf("Fw SHA256:      ");
    for (uint8_t i = 0; i < sizeof(header->fwInfo.hash); i++)
    {
        if ((i & 0x0F) == 0 && (i != 0))
        {
            printf("\r\n                ");
        }
        printf("%02X", header->fwInfo.hash[i]);
    }
    printf("\r\n");
    printf("Git rev:        %.*s\r\n", (int)sizeof(header->gitInfo.rev), header->gitInfo.rev);
    printf("Git date:       %.*s\r\n", (int)sizeof(header->gitInfo.date), header->gitInfo.date);
    printf("Git hash:       ");
    for (uint8_t i = 0; i < sizeof(header->gitInfo.hash); i++)
    {
        printf("%02X", header->gitInfo.hash[i]);
    }
    printf("\r\n");
    printf("Firmware CRC:   0x%08" PRIX32 "\r\n", header->fwInfo.crc);
    printf("Header CRC:     0x%08" PRIX32 "\r\n", header->crc);
    printf("------------------------------------------------------------\r\n\r\n");
}

void BIN_HEADER_PrintShort(const BIN_HEADER_s *header)
{
    printf("Ver:    HDR %u.%u.%u  FW %u.%u.%u\r\n",
        header->hdrVer.major, header->hdrVer.minor, header->hdrVer.patch,
        header->fwVer.major, header->fwVer.minor, header->fwVer.patch);
#if !defined(__x86_64__) && !defined(__i386__)
    printf("Load:   0x%08" PRIX32 "\r\n", header->fwInfo.loadAddr);
    printf("Boot:   0x%08" PRIX32 "\r\n", header->fwInfo.bootAddr);
    printf("Size:   %" PRIu32 " B\r\n", header->fwInfo.size);
#endif
    printf("Rev:    %.*s\r\n", (int)sizeof(header->gitInfo.rev), header->gitInfo.rev);
    printf("Date:   %.*s\r\n", (int)sizeof(header->gitInfo.date), header->gitInfo.date);
    printf("CRC:    HDR 0x%08" PRIX32 "  FW 0x%08" PRIX32 "\r\n", header->crc, header->fwInfo.crc);
    printf("\r\n");
}

void BIN_HEADER_CheckInit(void)
{
#if (BIN_HEADER_CRC_TABLE_EN == 1)
    CRC_SOFT_GenTable32(crc32Table, CRC_SOFT_IEEE_802_3_REFIN, CRC_SOFT_IEEE_802_3_POLY);
#endif
}

bool BIN_HEADER_CheckHeader(const BIN_HEADER_s *header)
{
    bool res = (header != NULL) && (header->beginMagic == BIN_HEADER_BEGIN_MAGIC) && (header->endMagic == BIN_HEADER_END_MAGIC);

    if (res)
    {
        uint32_t calcCrc = CRC_SOFT_IEEE_802_3_INIT;
        const uint32_t dummy = 0x00000000;
        calcCrc = CALC_CRC32((const void*)header, sizeof(BIN_HEADER_s) - 4, calcCrc);
        calcCrc = CALC_CRC32(&dummy, sizeof(dummy), calcCrc);
        calcCrc = calcCrc ^ CRC_SOFT_IEEE_802_3_XOR;
        res = (calcCrc == header->crc);
    }

    return res;
}

#if !defined(__x86_64__) && !defined(__i386__)
bool BIN_HEADER_CheckFirmware(const BIN_HEADER_s *header, const void *firmware)
{
    const uintptr_t fwStart = (uintptr_t)firmware;
    const uintptr_t hdrStart = (uintptr_t)header;
    const size_t hdrSize = sizeof(BIN_HEADER_s);
    size_t fwSize = 0;

    bool res = (header != NULL) && (firmware != NULL);

    if (res)
    {
        res = BIN_HEADER_CheckHeader(header);
    }

    if (res)
    {
        fwSize = header->fwInfo.size;
        res = (fwStart <= hdrStart) && ((hdrStart + hdrSize) <= (fwStart + fwSize));
    }

    if (res)
    {
        uint32_t calcCrc = CRC_SOFT_IEEE_802_3_INIT;
        calcCrc = CALC_CRC32(firmware, hdrStart - fwStart, calcCrc);

        const uint32_t dummy = 0x00000000;
        for (size_t i = 0; i < hdrSize / sizeof(dummy); i++)
        {
            calcCrc = CALC_CRC32(&dummy, sizeof(dummy), calcCrc);
        }

        calcCrc = CALC_CRC32((void*)(hdrStart + hdrSize), fwSize - ((hdrStart - fwStart) + hdrSize), calcCrc);
        calcCrc = calcCrc ^ CRC_SOFT_IEEE_802_3_XOR;
        res = (calcCrc == header->fwInfo.crc);
    }

    return res;
}
#endif
