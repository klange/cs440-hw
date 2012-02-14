.PHONY: all clean

all: sat
clean:
	-rm sat list.o

sat: solver.c list.o
	gcc -std=c99 -g -O3 -o sat solver.c list.o

list.o: list.c
	gcc -std=c99 -g -O3 -o list.o -c list.c
