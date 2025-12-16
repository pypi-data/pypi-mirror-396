include build_scripts/global.mk
# Параметры проекта, общие для всех конфигураций сборки

# Выбор компиляции
GCC     := $(ENV_GCC_PATH)gcc
G++     := $(ENV_GCC_PATH)g++
SIZE    := $(ENV_GCC_PATH)size
OBJDUMP := $(ENV_GCC_PATH)objdump
OBJCOPY := $(ENV_GCC_PATH)objcopy

# Название проекта
PRJ_NAME := project_name

# Расширение исполняемого файла (.elf, .exe,  и др.)
PRJ_OUT_EXTENSION :=

# Флаги компиляции
PRJ_CFLAGS := \

# Флаги линкера
PRJ_LFLAGS := \

# Дефайны
PRJ_DEFINES := \

# Пути к заголовочным файлам
PRJ_INC_PATHS := \

# Пути к файлам с исходным кодом
PRJ_SRC_PATHS := \

# Пути к скомпилированным библиотекам
PRJ_LIB_PATHS := \

# Наименования библиотек
PRJ_LIBRARIES := \

# LD-скрипт
PRJ_LINKER_SCRIPT := \

PRJ_GCC_DEF := \

# Прочие файлы, при изменении которых необходимо перезапускать сборку
PRJ_OTHER_DEPS := \
