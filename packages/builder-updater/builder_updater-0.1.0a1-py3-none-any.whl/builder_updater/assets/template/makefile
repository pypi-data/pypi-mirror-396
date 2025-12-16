include build_scripts/global.mk
include project_configs/common.mk

# Список конфигураций сборки, получаемый из набора файлов, расположенных в папке "project_configs/build_configs"
BUILD_CONFIGS := $(basename $(notdir $(wildcard project_configs/build_configs/*.mk)))

# Если при вызове make не указана определенная конфигурация, то будет выбрана
# цель all и собраны все существующие конфигурации из списка BUILD_CONFIGS
all: $(BUILD_CONFIGS)
	@echo "Make ALL done"

# Стирает содержимое папки с артефактами сборки
clean:
	@echo "Cleaning"
	@$(RMD) $(G_OUTPUT_PATH)

# Шаблон, позволяющий автоматически создать набор целей для каждой конфигурации сборки
# Каждая цель вызывает отдельное выполнение утилиты make с целями сборки, описанными в файле "builder.mk"
%:
	@echo "----------------------------------------------------------------------------------------------------"
	@echo "Begin to build: $@"
	@make --no-print-directory -f build_scripts/builder.mk -j BC_NAME=$@
