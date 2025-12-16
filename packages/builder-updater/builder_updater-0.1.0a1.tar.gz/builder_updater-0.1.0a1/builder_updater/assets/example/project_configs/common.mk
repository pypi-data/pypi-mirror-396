include build_scripts/global.mk
# Параметры проекта, общие для всех конфигураций сборки

# Выбор компиляции
GCC     := $(ENV_GCC_PATH)gcc
G++     := $(ENV_GCC_PATH)g++
SIZE    := $(ENV_GCC_PATH)size
OBJDUMP := $(ENV_GCC_PATH)objdump
OBJCOPY := $(ENV_GCC_PATH)objcopy

# Название проекта
PRJ_NAME := example_project

# Расширение исполняемого файла (.elf, .exe,  и др.)
ifeq ($(OS),Windows_NT)
	PRJ_OUT_EXTENSION := .exe
else
	PRJ_OUT_EXTENSION :=
endif

# Флаги компиляции
PRJ_CFLAGS := \
-O2 \
-Werror \
-D"ELOF(a)=(sizeof(a)/sizeof(a)[0])" \
-D"INDOF(el,arr)=((((uintptr_t)el)-((uintptr_t)arr))/sizeof((arr)[0]))" \
-D"RUN_TEST(TestExpr,flag)={bool testOk = (TestExpr); flag = flag && testOk; printf(\"$(PCT)-32s - $(PCT)s\r\n\", \#TestExpr, testOk ? \"OK\" : \"FAIL\");}" \
-D"END_TEST(flag)={printf(\"$(PCT)-32s - $(PCT)s\r\n\", \"Total result\", flag ? \"OK\" : \"FAIL\");}" \

# Флаги линкера
PRJ_LFLAGS := \

# Дефайны
PRJ_DEFINES := \
PRJ_DEFINE_EXAMPLE=1 \

# Пути к заголовочным файлам
PRJ_INC_PATHS := \
build_scripts/bin_header \
build_scripts/crc_soft \

# Пути к файлам с исходным кодом
PRJ_SRC_PATHS := \
build_scripts/bin_header \
build_scripts/crc_soft \
src \

# Пути к скомпилированным библиотекам
PRJ_LIB_PATHS := \

# Наименования библиотек
PRJ_LIBRARIES := \

# LD-скрипт
PRJ_LINKER_SCRIPT := \

PRJ_GCC_DEF := \

# Прочие файлы, при изменении которых необходимо перезапускать сборку
PRJ_OTHER_DEPS := \
