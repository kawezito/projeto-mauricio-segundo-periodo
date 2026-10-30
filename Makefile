# Makefile para o Sistema de Farmacia Desktop (C + GTK)

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -Iinclude $(shell pkg-config --cflags gtk+-3.0)
LIBS = $(shell pkg-config --libs gtk+-3.0) -lsqlite3

SRC_DIR = src
OBJ_DIR = build
BIN_DIR = bin
TARGET = $(BIN_DIR)/farmacia_app

# Lista de arquivos-fonte
SRCS = $(wildcard $(SRC_DIR)/*.c) \
       $(wildcard $(SRC_DIR)/models/*.c) \
       $(wildcard $(SRC_DIR)/repositories/*.c) \
       $(wildcard $(SRC_DIR)/services/*.c) \
       $(wildcard $(SRC_DIR)/ui/*.c)

OBJS = $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRCS))

all: directories $(TARGET)

$(TARGET): $(OBJS)
	@mkdir -p $(BIN_DIR)
	$(CC) $(OBJS) -o $@ $(LIBS)
	@echo "Compilação concluída com sucesso: $(TARGET)"

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

directories:
	@mkdir -p $(BIN_DIR) $(OBJ_DIR) data

run: all
	./$(TARGET)

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)
	@echo "Arquivos temporários e binários removidos."

.PHONY: all run clean directories
