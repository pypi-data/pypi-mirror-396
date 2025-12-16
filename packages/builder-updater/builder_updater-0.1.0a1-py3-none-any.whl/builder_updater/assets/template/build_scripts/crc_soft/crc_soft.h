#pragma once

#include <stddef.h>
#include <stdint.h>

#define CRC_SOFT_TABLE_LEN                                  (256UL)

/**
 * Name  : CRC-16 CCITT-false (CRC16/IBM-3740)
 * Poly  : 0x1021   x^16 + x^12 + x^5 + 1
 * Check : 0x29B1 ("123456789") init=0xFFFF xor=0x0000
 * MaxLen: 4095 байт (32767 бит)
*/
#define CRC_SOFT_CCITT_16_POLY          (0x1021)
#define CRC_SOFT_CCITT_16_INIT          (0xFFFF)
#define CRC_SOFT_CCITT_16_XOR           (0x0000)
extern const uint16_t CRC_SOFT_CCITT_16_Table[CRC_SOFT_TABLE_LEN];

/**
 * Name  : CRC-32 IEEE 802.3
 * Poly  : 0x04C11DB7    x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + x^11
 *                       + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1
 * Check : 0xCBF43926 ("123456789") init=0xFFFFFFFF xor=0xFFFFFFFF
 * MaxLen: 268 435 455 байт (2 147 483 647 бит) - обнаружение
           одинарных, двойных, пакетных и всех нечетных ошибок
*/
#define CRC_SOFT_IEEE_802_3_POLY        (0x04C11DB7)
#define CRC_SOFT_IEEE_802_3_INIT        (0xFFFFFFFF)
#define CRC_SOFT_IEEE_802_3_XOR         (0xFFFFFFFF)
extern const uint32_t CRC_SOFT_IEEE_802_3_Table[CRC_SOFT_TABLE_LEN];

/**
 * @brief Операция побитового отражения 8-битного значения
 *
 * @param val Отражаемое значение
 * @return Результат отражения
 */
uint8_t CRC_SOFT_Reflect8(uint8_t val);

/**
 * @brief Операция побитового отражения 16-битного значения
 *
 * @param val Отражаемое значение
 * @return Результат отражения
 */
uint16_t CRC_SOFT_Reflect16(uint16_t val);

/**
 * @brief Операция побитового отражения 32-битного значения
 *
 * @param val Отражаемое значение
 * @return Результат отражения
 */
uint32_t CRC_SOFT_Reflect32(uint32_t val);

/**
 * @brief Генератор таблицы для вычисления 16-битного CRC
 *
 * @param table Указатель на таблицу
 * @param poly Значение полинома
 */
void CRC_SOFT_GenTable16(uint16_t table[CRC_SOFT_TABLE_LEN], uint16_t poly);

/**
 * @brief Генератор таблицы для вычисления 32-битного CRC
 *
 * @param table Указатель на таблицу
 * @param poly Значение полинома
 */
void CRC_SOFT_GenTable32(uint32_t table[CRC_SOFT_TABLE_LEN], uint32_t poly);

/**
 * @brief Вычисление 16-битной CRC
 *
 * @note Позволяет вычислять CRC для любого полинома по предварительно сгенерированной таблице (см. CRC_SOFT_GenTable16),
 *       также позволяет вычислять CRC частями, передавая в параметр initCrc результат вычисления предыдущей части,
 *       после вычисления CRC для последней части необходимо выполнить XOR с итоговым результатом
 *
 * @param data Указатель на буфер с данными
 * @param size Размер буфера
 * @param initCrc Начальное значение CRC (или результат от предыдущей части данных)
 * @param table Указатель на таблицу
 * @return Результат вычисления
 */
uint16_t CRC_SOFT_CalcPartTable16(const void *data, size_t size, uint16_t initCrc, const uint16_t table[CRC_SOFT_TABLE_LEN]);

/**
 * @brief Вычисление 32-битной CRC
 *
 * @note Позволяет вычислять CRC для любого полинома по предварительно сгенерированной таблице (см. CRC_SOFT_GenTable32),
 *       также позволяет вычислять CRC частями, передавая в параметр initCrc результат вычисления предыдущей части,
 *       после вычисления CRC для последней части необходимо выполнить XOR с итоговым результатом
 *
 * @param data Указатель на буфер с данными
 * @param size Размер буфера
 * @param initCrc Начальное значение CRC (или результат от предыдущей части данных)
 * @param table Указатель на таблицу
 * @return Результат вычисления
 */
uint32_t CRC_SOFT_CalcPartTable32(const void *data, size_t size, uint32_t initCrc, const uint32_t table[CRC_SOFT_TABLE_LEN]);

/**
 * @brief Вычисление 16-битной CRC
 *
 * @note Позволяет вычислять CRC для любого полинома без использования таблиц,
 *       также позволяет вычислять CRC частями, передавая в параметр initCrc результат вычисления предыдущей части,
 *       после вычисления CRC для последней части необходимо выполнить XOR с итоговым результатом
 *
 * @param data Указатель на буфер с данными
 * @param size Размер буфера
 * @param initCrc Начальное значение CRC (или результат от предыдущей части данных)
 * @param poly Значение полинома
 * @return Результат вычисления
 */
uint16_t CRC_SOFT_CalcPart16(const void *data, size_t size, uint16_t initCrc, uint16_t poly);

/**
 * @brief Вычисление 32-битной CRC
 *
 * @note Позволяет вычислять CRC для любого полинома без использования таблиц,
 *       также позволяет вычислять CRC частями, передавая в параметр initCrc результат вычисления предыдущей части,
 *       после вычисления CRC для последней части необходимо выполнить XOR с итоговым результатом
 *
 * @param data Указатель на буфер с данными
 * @param size Размер буфера
 * @param initCrc Начальное значение CRC (или результат от предыдущей части данных)
 * @param poly Значение полинома
 * @return Результат вычисления
 */
uint32_t CRC_SOFT_CalcPart32(const void *data, size_t size, uint32_t initCrc, uint32_t poly);
