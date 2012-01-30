.PHONY: all

all: solver

solver: solver.c list.o
	gcc -std=c99 -g -o solver solver.c list.o

list.o: list.c
	gcc -std=c99 -g -o list.o -c list.c
