all: Screenshot.o
	gcc -o screenshot.so Screenshot.o -shared -O3 -lX11 -fPIC

Screenshot.o: Screenshot.c
	gcc -c Screenshot.c