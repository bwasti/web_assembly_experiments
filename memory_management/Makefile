all:
	clang++ --target=wasm32 -nostdlib -Oz -c demo.cpp -o /tmp/demo.o
	clang --target=wasm32 -nostdlib -Oz -c malloc.c -o /tmp/malloc.o
	wasm-ld --no-entry --export-all --lto-O3 --allow-undefined --import-memory /tmp/malloc.o /tmp/demo.o -o demo.wasm
