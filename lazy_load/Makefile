all:
	clang++ --target=wasm32 -nostdlib -O3 -c a.cpp -o /tmp/a.o
	clang++ --target=wasm32 -nostdlib -O3 -c b.cpp -o /tmp/b.o
	wasm-ld --no-entry --export-all --lto-O3 --allow-undefined --import-memory /tmp/a.o -o a.wasm
	wasm-ld --no-entry --export-all --lto-O3 --allow-undefined --import-memory /tmp/b.o -o b.wasm

GENERATED_DIR := generated
SRC_FILES := $(wildcard $(GENERATED_DIR)/*.cpp)
OBJ_FILES := $(patsubst $(GENERATED_DIR)/%.cpp,$(GENERATED_DIR)/%.wasm.o,$(SRC_FILES))
OUT_FILES := $(patsubst $(GENERATED_DIR)/%.cpp,$(GENERATED_DIR)/%.wasm,$(SRC_FILES))

.PHONY: generated generated_files

generate: $(OUT_FILES)

generate_combined: $(OBJ_FILES)
	wasm-ld --no-entry --export-all --lto-O3 --allow-undefined --import-memory -o f_all.wasm $^

$(GENERATED_DIR)/%.wasm: $(GENERATED_DIR)/%.cpp  $(GENERATED_DIR)/%.wasm.o
	wasm-ld --no-entry --export-all --lto-O3 --allow-undefined --import-memory $@.o -o $@

$(GENERATED_DIR)/%.wasm.o: $(GENERATED_DIR)/%.cpp
	clang++ --target=wasm32 -nostdlib -O3 -c $< -o $@
