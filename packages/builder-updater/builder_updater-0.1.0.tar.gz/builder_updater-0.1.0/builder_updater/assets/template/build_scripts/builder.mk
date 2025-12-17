include build_scripts/global.mk
include project_configs/build_configs/$(BC_NAME).mk
include project_configs/common.mk

#----------------------------------------------------------------------------------------------------------------------

# Путь к артефактам текущей конфигурации сборки
OUTPUT_PATH := $(G_OUTPUT_PATH)/$(BC_NAME)/

# Наименования артефактов текущей конфигурации сборки
OUT := $(OUTPUT_PATH)$(PRJ_NAME)_$(BC_NAME)$(PRJ_OUT_EXTENSION)
RAW := $(OUTPUT_PATH)$(PRJ_NAME)_$(BC_NAME).raw
MAP := $(OUTPUT_PATH)$(PRJ_NAME)_$(BC_NAME).map
LSS := $(OUTPUT_PATH)$(PRJ_NAME)_$(BC_NAME).lss
BIN := $(OUTPUT_PATH)$(PRJ_NAME)_$(BC_NAME).bin
PRS := $(OUTPUT_PATH)$(PRJ_NAME)_$(BC_NAME).txt

# Функция генерации списка файлов с рекурсивным поиском по переданому
# списку путей $1 и фильтрацией по регулярному выражению $2
rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

# Пути к файлам с исходным кодом
SRC_PATHS := $(PRJ_SRC_PATHS) $(BC_SRC_PATHS)

# Списки файлов с исходным кодом (c++, c, asm)
CPP_SRC := $(call rwildcard, $(SRC_PATHS), *.cpp) $(filter %.cpp, $(SRC_PATHS))
C_SRC   := $(call rwildcard, $(SRC_PATHS), *.c) $(filter %.c, $(SRC_PATHS))
S_SRC   := $(call rwildcard, $(SRC_PATHS), *.s *.S) $(filter %.s %.S, $(SRC_PATHS))

# Списки объектных файлов (c++, c, asm)
CPP_OBJ := $(addprefix $(OUTPUT_PATH), $(CPP_SRC:.cpp=.o))
C_OBJ   := $(addprefix $(OUTPUT_PATH), $(C_SRC:.c=.o))
S_OBJ   := $(addprefix $(OUTPUT_PATH), $(S_SRC:.s=.o))
S_OBJ   := $(S_OBJ:.S=.o)

# LD скрипт из конфигурации приоритетнее, чем из общих настроек проекта
ifneq ($(BC_LINKER_SCRIPT), )
LINKER_SCRIPT := $(BC_LINKER_SCRIPT)
else
LINKER_SCRIPT := $(PRJ_LINKER_SCRIPT)
endif

# Формирует параметры цели сборки и флаги компоновщика, если LD скрипт задан
ifneq ($(LINKER_SCRIPT), )
LDS := $(addprefix $(OUTPUT_PATH), $(LINKER_SCRIPT))
LDS_DEP := $(LDS:.ld=.d)
LDS_FLAGS := -T $(LDS)
endif

# Список всех объектных файлов
ALL_OBJ := $(CPP_OBJ) $(C_OBJ) $(S_OBJ)

# Список файлов с информацией о зависимостях исходных и заголовочных файлов
DEPENDS := $(ALL_OBJ:.o=.d) $(LDS_DEP)

# Подключаемые библиотеки
LIBS := $(addprefix -l, $(PRJ_LIBRARIES) $(BC_LIBRARIES))

# Дополнительные скрипты
GCC_MAP_PARSER := build_scripts/post_build/gcc_map_parser.py
MODIFY_HEADER := build_scripts/post_build/modify_header.py

# Список файлов при изменении которых необходимо перезапускать сборку всего проекта
OTHER_DEPS := \
$(PRJ_OTHER_DEPS) \
$(BC_OTHER_DEPS) \
$(G_ENV_FILE) \
project_configs/common.mk \
project_configs/build_configs/$(BC_NAME).mk \
build_scripts/builder.mk \
build_scripts/global.mk \
makefile \

#----------------------------------------------------------------------------------------------------------------------

# Флаги компиляции С файлов
GCC_CFLAGS := \
-D"BUILDER_PRJ_NAME=\"$(PRJ_NAME)\"" \
-D"BUILDER_BC_NAME=\"$(BC_NAME)\"" \
$(addprefix -D, $(PRJ_DEFINES) $(BC_DEFINES)) \
$(addprefix -I, $(PRJ_INC_PATHS) $(BC_INC_PATHS)) \
$(addprefix -L, $(PRJ_LIB_PATHS) $(BC_LIB_PATHS)) \
-MMD -MP \
-ffunction-sections -fdata-sections \
-g -fms-extensions -static -static-libgcc -static-libstdc++ \
-Wall -Wextra -Wshadow -Wredundant-decls -Wno-unused-result \
$(PRJ_CFLAGS) $(BC_CFLAGS) \
-pipe $(PRJ_GCC_DEF) \

# Флаги компиляции С++ файлов
G++_CFLAGS := \
$(LDS_FLAGS) \
-std=c++17 \
$(GCC_CFLAGS) \

# Флаги линкера
G++_LFLAGS := \
-ggdb -Wl,-Map=$(MAP),--no-warn-rwx-segment \
$(PRJ_LFLAGS) $(BC_LFLAGS) \

#----------------------------------------------------------------------------------------------------------------------

# Главная цель сборки, реквизиты которой - набор главных артефактов сборки
all: compile_version $(OUT) $(BIN) $(LSS) $(COMPILE_COMMANDS_PATH) $(PRS)
	@echo "Building done: $(BC_NAME)"

$(PRS): $(OUT) $(GCC_MAP_PARSER)
	@echo "Generate: $@"
	@$(ENV_PYTHON_PATH) $(GCC_MAP_PARSER) -p $< -l $@ -z -s -m -f \
	.isr_vector .init .fini .preinit_array init_array .fini_array .text .data .sdata .rodata .rela .data .bss

# Цель для сборки файлов, необходимых в VS Code (не выполняется, если COMPILE_COMMANDS_PATH пусто)
$(COMPILE_COMMANDS_PATH): $(OUT)
# Т.к. в режиме -n выполнение цели all не достигается, то и рекурсивного вызова make не происходит
	@echo "Generate: $@"
	@$(ENV_PYTHON_PATH) -m compiledb -n -o $@ make -f build_scripts/builder.mk -j 8

# Цель для создания bin файла из elf/exe файла
$(BIN): $(OUT)
	@echo "Generate: $@"
	@$(OBJCOPY) -O binary $< $@

# Цель для создания lss файла из elf/exe файла
$(LSS): $(OUT)
	@echo "Generate: $@"
	@$(OBJDUMP) -h -S $< > $@

# Цель для линковки "сырого" elf/exe файла до добавления информации в заголовок
$(RAW): $(ALL_OBJ) $(LDS)
	@echo "Linking: $@"
	@$(G++) $(G++_CFLAGS) $(G++_LFLAGS) -o $@ $(ALL_OBJ) $(LIBS)
	@$(SIZE) $@

# Добавление информации в заголовок исполняемого файла
$(OUT): $(RAW) $(MODIFY_HEADER)
	@$(CP) $(RAW) $(OUT)
	@$(ENV_PYTHON_PATH) $(MODIFY_HEADER) -p $@ -d $(OBJDUMP) -c $(OBJCOPY)

# Цель для препроцессинга LD скрипта
$(LDS): $(LINKER_SCRIPT) $(OTHER_DEPS)
	@echo "Generate: $@"
	@$(MKD) $(dir $@)
	@$(GCC) $(GCC_CFLAGS) -MF $(LDS_DEP) -MQ $@ -E -x c $< > $@

# Включаем файлы с зависимостями для отслеживания изменений в заголовочных файлах
-include $(DEPENDS)

# Шаблон для компиляции всех C++ файлов
$(OUTPUT_PATH)%.o: %.cpp $(OTHER_DEPS)
	@echo "Compile: $<"
	@$(MKD) $(dir $@)
	@$(G++) $(G++_CFLAGS) -c -o $@ $<

# Шаблон для компиляции всех C файлов
$(OUTPUT_PATH)%.o: %.c $(OTHER_DEPS)
	@echo "Compile: $<"
	@$(MKD) $(dir $@)
	@$(GCC) $(GCC_CFLAGS) -c -o $@ $<

# Шаблон для компиляции ASM файлов .S
$(OUTPUT_PATH)%.o: %.S $(OTHER_DEPS)
	@echo "Compile: $<"
	@$(MKD) $(dir $@)
	@$(GCC) $(GCC_CFLAGS) -c -o $@ $<

# Шаблон для компиляции ASM файлов .s
$(OUTPUT_PATH)%.o: %.s $(OTHER_DEPS)
	@echo "Compile: $<"
	@$(MKD) $(dir $@)
	@$(GCC) $(GCC_CFLAGS) -c -o $@ $<

compile_version:
	@echo "Using: $(GCC) $(shell $(GCC) -dumpversion)"

.PHONY: $(OUT)
