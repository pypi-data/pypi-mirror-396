G_REAL_PATH     := $(realpath .)
G_OUTPUT_PATH   := output
G_ENV_FILE      := env.mk

ifneq ($(wildcard $(G_ENV_FILE)), $(G_ENV_FILE))
    G_ENV_FILE := build_scripts/env_default.mk
endif

include $(G_ENV_FILE)

ifeq ($(OS),Windows_NT)
    path=$(subst /,\,$1)
    RM      := $(ENV_BUSYBOX_PATH) rm -rf
    RMD     := $(ENV_BUSYBOX_PATH) rm -rf
    MKD     := $(ENV_BUSYBOX_PATH) mkdir -p
    CP      := $(ENV_BUSYBOX_PATH) cp
    PCT     := %%
else
    path=$(subst \,/,$1)
    RM      := rm -rf
    RMD     := rm -rf
    MKD     := mkdir -p
    CP      := cp
    PCT     := %
endif
