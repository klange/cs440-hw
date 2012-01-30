.PHONY: all

all: solver

solver: solver.c list.o
	gcc -std=c99 -o solver solver.c list.o

list.o: list.c
	gcc -std=c99 -o list.o -c list.c
