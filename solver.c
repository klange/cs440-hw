/* vim: tabstop=4 shiftwidth=4 noexpandtab
 *
 * Brute-Force SAT Solver
 */

#define _XOPEN_SOURCE 500
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "list.h"

#define LINE_WIDTH 4096

#define BITS_IN_SET 8
uint8_t * bit_sets = NULL;
uint64_t bit_sets_n = 0;
uint64_t variables  = 0;
uint64_t clause_n   = 0;
uint64_t collected  = 0;

list_t ** clauses;

uint8_t checkbit(uint64_t bit) {
	assert(bit < BITS_IN_SET * bit_sets_n && "Attempted to check an entirely invalid bit!");
	uint64_t set_id = bit / BITS_IN_SET;
	uint8_t offset = bit - set_id * BITS_IN_SET;
	uint8_t tmp = ((bit_sets[set_id] & (1 << offset)) > 0);

#if DEBUG
	fprintf(stderr,"bit %ld [%ld:%d] = %d [%x, %d]\n", bit, set_id, offset, tmp, bit_sets[set_id], 1 << offset);
#endif

	return tmp;
}

void setup_bitsets() {
	bit_sets_n = variables / BITS_IN_SET + 1;
	bit_sets = (uint8_t *)malloc(sizeof(uint64_t) * bit_sets_n);
}

void next_bitset(uint64_t i) {
	if (bit_sets[i] == 0xFF) {
		bit_sets[i] = 0;
		if (i + 1 == bit_sets_n) {
			printf("UNSATISFIABLE\n");
			exit(0);
		}
		next_bitset(i + 1);
	} else {
		bit_sets[i]++;
		if (i + 1 == bit_sets_n) {
			if (bit_sets[i] == (1 << variables)) {
				printf("UNSATISFIABLE\n");
				exit(0);
			}
		}
	}
}

uint8_t is_clause_true(uint64_t i) {
	list_t * clause = clauses[i];
	uint8_t yes = 0;

	foreach(node, clause) {
		int64_t var = (int64_t)node->value;
		if (var < 0) {
			yes |= (!checkbit(-var - 1));
		} else {
			yes |= (checkbit(var - 1));
		}
	}
	return yes;
}

uint8_t solved_with_bitset() {
	for (uint64_t i = 0; i < clause_n; ++i) {
		if (!is_clause_true(i)) {
			return 0;
		}
	}
	return 1;
}

int read_line() {
	char c = fgetc(stdin);
	switch (c) {
		case 'c':
			while (fgetc(stdin) != '\n');
			break;
		case 'p':
			/* Problem definition */
			{ 
				fgetc(stdin);
				while (fgetc(stdin) != ' ');
				char num[30];
				int offset = 0;
				char input;
				while ((input = fgetc(stdin)) != ' ') {
					num[offset] = input;
					offset++;
				}
				num[offset] = '\0';
				variables = atoi(num);
				offset = 0;
				while ((input = fgetc(stdin)) != '\n') {
					num[offset] = input;
					offset++;
				}
				num[offset] = '\0';
				clause_n = atoi(num);
				clauses  = malloc(sizeof(list_t *) * clause_n);
				setup_bitsets();
			}
			break;
		default:
			{
				assert(variables > 0);
				assert(clauses > 0);

				ungetc(c, stdin);

				clauses[collected] = list_create();
				char * line = malloc(LINE_WIDTH);
				fgets(line, LINE_WIDTH - 1, stdin);
				line[strlen(line) - 1] = '\0';

				char *p, *last;
				for ((p = strtok_r(line, " ", &last)); ;
						(p = strtok_r(NULL, " ", &last))) {
					int var = atoi(p);
					if (var == 0) break;
					uintptr_t x = var;
					list_insert(clauses[collected], (void *)x);
				}
				free(line);

				collected++;
				if (collected == clause_n) return 0;
			}
			break;
	}
	return 1;
}

int main(int argc, char * argv[]) {
	/* Read in file */
	while (read_line());

#if DEBUG
	for (uint32_t i = 0; i < clause_n; ++i) {
		list_t * clause = clauses[i];
		fprintf(stderr, "[clause #%d] ", (i + 1));
		foreach(node, clause) {
			fprintf(stderr, "%ld ", (uintptr_t)node->value);
		}
		fprintf(stderr, "\n");
	}

	fprintf(stderr, "%ld variables to check, which means %d combinations to bruteforce.\n", variables, 1 << variables);
#endif

	while (!solved_with_bitset()) {
		next_bitset(0);
	}

	/* We have found a working set. */
	for (uint64_t i = 0; i < variables; ++i) {
		if (checkbit(i)) {
			printf("%ld", i + 1);
		} else {
			printf("-%ld", i + 1);
		}
		if (i != variables - 1) {
			printf(" ");
		} else {
			printf("\n");
		}
	}

}
