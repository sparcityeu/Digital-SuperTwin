COMPILER = gcc
FLAGS = -g -Wall -Wextra -O2

ifeq ($(isa),sse)
	FLAGS += -DSSE
else ifeq ($(isa),avx)
	FLAGS += -DAVX
else ifeq ($(isa),avx512)
	FLAGS += -DAVX512
else
	FLAGS += -DSCALAR
endif

Bench:
	$(COMPILER) $(FLAGS) Bench.c select_op.c create_bench.c write_asm.c calc_param.c -o Bench -lm

clean:
	rm -f Bench
