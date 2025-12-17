#pragma once

/**
 * @file bin_header.h
 * @brief Интерфейс работы с заголовком образа ВПО (Firmware Image) и контроль целостности
 *
 * @note Чтобы в образе ВПО появился заголовок необходимо добавить секцию в скрипт компоновщика:
 * @code{.c}
    .header (READONLY):
    {
        . = ALIGN(4);
        KEEP(*(.header))
        . = ALIGN(4);
    } > FLASH

    PROVIDE(header_load_addr = ORIGIN(FLASH));
    PROVIDE(header_boot_addr = Reset_Handler);
    PROVIDE(header_firmware_size = LOADADDR(.data) + SIZEOF(.data) - header_load_addr);
 * @endcode
 *
 */

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

#define BIN_HEADER_BEGIN_MAGIC                              (0xD72E5F1A)
#define BIN_HEADER_END_MAGIC                                (0x48EF7EC5)
#define BIN_HEADER_MAJOR_VERSION                            (1)
#define BIN_HEADER_MINOR_VERSION                            (1)
#define BIN_HEADER_PATCH_VERSION                            (0)
#define BIN_HEADER_INVALID_VERSION                          (0xFF)
#define BIN_HEADER_NAMES_SIZE                               (32UL)
#define BIN_HEADER_SHA256_SIZE                              (32UL)

#pragma pack(push)
#pragma pack(4)

/**
 * @brief Структура для хранения семантической версии
 *
 */
typedef struct
{
    uint8_t major;          ///< Увеличивается при появлении ломающих (breaking) изменений
    uint8_t minor;          ///< Увеличивается при добавлении новой функциональности
    uint8_t patch;          ///< Увеличивается при внесении исправлений и прочих изменений
    uint8_t RES0[1];
} BIN_HEADER_Version_s;

static_assert(offsetof(BIN_HEADER_Version_s, major)     == 0x00, "");
static_assert(offsetof(BIN_HEADER_Version_s, minor)     == 0x01, "");
static_assert(offsetof(BIN_HEADER_Version_s, patch)     == 0x02, "");
static_assert(offsetof(BIN_HEADER_Version_s, RES0)      == 0x03, "");
static_assert(sizeof(BIN_HEADER_Version_s)              == 0x04, "");

/**
 * @brief Специальная информация о прошивке (резерв)
 *
 */
typedef struct
{
#if !defined(__x86_64__) && !defined(__i386__)
    uint32_t loadAddr;                      ///< Целевой адрес расположения ВПО
    uint32_t bootAddr;                      ///< Адрес загрузки ВПО
    uint32_t size;                          ///< Размер константной части ВПО
    uint8_t RES0[16];
#else
    uint8_t RES0[28];
#endif
    uint8_t hash[BIN_HEADER_SHA256_SIZE];   ///< SHA256 hash ВПО (header заполнен нулями)
    uint32_t crc;                           ///< Контрольная сумма IEEE 802.3
} BIN_HEADER_FwInfo_s;

#if !defined(__x86_64__) && !defined(__i386__)
static_assert(offsetof(BIN_HEADER_FwInfo_s, loadAddr)   == 0x00, "");
static_assert(offsetof(BIN_HEADER_FwInfo_s, bootAddr)   == 0x04, "");
static_assert(offsetof(BIN_HEADER_FwInfo_s, size)       == 0x08, "");
static_assert(offsetof(BIN_HEADER_FwInfo_s, RES0)       == 0x0C, "");
#else
static_assert(offsetof(BIN_HEADER_FwInfo_s, RES0)       == 0x00, "");
#endif
static_assert(offsetof(BIN_HEADER_FwInfo_s, hash)       == 0x1C, "");
static_assert(offsetof(BIN_HEADER_FwInfo_s, crc)        == 0x3C, "");
static_assert(sizeof(BIN_HEADER_FwInfo_s)               == 0x40, "");

/**
 * @brief Информация, полученная из состояния git репозитория
 *
 */
typedef struct
{
    char rev[16];                           ///< Ревизия - наименование последнего тега и часть хеша текущего коммита
    char date[BIN_HEADER_NAMES_SIZE];       ///< Дата и время коммита или дата и время сборки, если в проекте есть изменения
    uint8_t hash[20];                       ///< Полный хеш текущего коммита
} BIN_HEADER_GitInfo_s;

static_assert(offsetof(BIN_HEADER_GitInfo_s, rev)       == 0x00, "");
static_assert(offsetof(BIN_HEADER_GitInfo_s, date)      == 0x10, "");
static_assert(offsetof(BIN_HEADER_GitInfo_s, hash)      == 0x30, "");
static_assert(sizeof(BIN_HEADER_GitInfo_s)              == 0x44, "");

/**
 * @brief Полное описание заголовка
 *
 */
typedef volatile struct
{
    uint32_t beginMagic;                        ///< Начальное магическое число заголовка
    BIN_HEADER_Version_s hdrVer;                ///< Семантическая версия заголовка
    BIN_HEADER_Version_s fwVer;                 ///< Семантическая версия ВПО (формируется из тега git репозитория)
    uint8_t RES1[4];
    char prjName[BIN_HEADER_NAMES_SIZE];        ///< Наименование проекта
    char bcName[BIN_HEADER_NAMES_SIZE];         ///< Наименование конфигурации сборки
    BIN_HEADER_FwInfo_s fwInfo;                 ///< Специальная информация о прошивке (резерв)
    uint8_t RES2[16];
    BIN_HEADER_GitInfo_s gitInfo;               ///< Информация, полученная из состояния git репозитория
    uint8_t RES3[20];
    uint32_t endMagic;                          ///< Завершающее магическое число
    uint32_t crc;                               ///< Контрольная сумма IEEE 802.3 для заголовка
} BIN_HEADER_s;

static_assert(offsetof(BIN_HEADER_s, beginMagic)        == 0x0000, "");
static_assert(offsetof(BIN_HEADER_s, hdrVer)            == 0x0004, "");
static_assert(offsetof(BIN_HEADER_s, fwVer)             == 0x0008, "");
static_assert(offsetof(BIN_HEADER_s, prjName)           == 0x0010, "");
static_assert(offsetof(BIN_HEADER_s, bcName)            == 0x0030, "");
static_assert(offsetof(BIN_HEADER_s, fwInfo)            == 0x0050, "");
static_assert(offsetof(BIN_HEADER_s, gitInfo)           == 0x00A0, "");
static_assert(offsetof(BIN_HEADER_s, endMagic)          == 0x00F8, "");
static_assert(offsetof(BIN_HEADER_s, crc)               == 0x00FC, "");
static_assert(sizeof(BIN_HEADER_s)                      == 0x0100, "");
static_assert(sizeof(BIN_HEADER_s) % sizeof(uint32_t)   == 0, "");

#pragma pack(pop)

/**
 * @brief Возвращает указатель на заголовок
 *
 * @return Указатель на заголовок
 */
const BIN_HEADER_s * BIN_HEADER_GetHeader(void);

/**
 * @brief Выводит информацию о заголовке через стандартный вывод
 *
 * @param header Указатель на заголовок
 */
void BIN_HEADER_Print(const BIN_HEADER_s *header);

/**
 * @brief Выводит сокращенную информацию о заголовке через стандартный вывод
 *
 * @param header Указатель на заголовок
 */
void BIN_HEADER_PrintShort(const BIN_HEADER_s *header);

/**
 * @brief Инициализация таблиц для операций BIN_HEADER_Check..
 *
 * @warning Генерирует таблицу для вычисления CRC, необходимо вызвать один раз
 *          перед вызовами функций BIN_HEADER_CheckHeader и BIN_HEADER_CheckFirmware
 *
 */
void BIN_HEADER_CheckInit(void);

/**
 * @brief Проверяет заголовок по CRC
 *
 * @param header Указатель на заголовок
 * @retval true: Заголовок валидный
 * @retval false: Заголовок НЕвалидный
 */
bool BIN_HEADER_CheckHeader(const BIN_HEADER_s *header);

#if !defined(__x86_64__) && !defined(__i386__)
/**
 * @brief Проверяет ВПО по CRC
 *
 * @warning Указатель на заголовок должен находится внутри ВПО, передаваемого по указателю firmware
 *
 * @param header Указатель на заголовок
 * @param firmware Указатель на ВПО
 * @retval true: Заголовок валидный
 * @retval false: Заголовок НЕвалидный
 */
bool BIN_HEADER_CheckFirmware(const BIN_HEADER_s *header, const void *firmware);
#endif
