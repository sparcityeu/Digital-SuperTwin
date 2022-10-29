//Operands Selection
void select_ISA_flops(int * flop, char ** assembly_op, char * operation, char * precision);
void select_ISA_mem(int * align, int * ops, char ** assembly_op, char * precision);

//Create Benchmarks
void create_benchmark_flops(char * op, char * precision, int long long fp);
void create_benchmark_mem(int long long num_rep, int num_ld, int num_st, char * precision);

//Write Assembly Codes
void write_asm_fp (int long long fp, char * op, int flops, char * assembly_op_flops_1, char * assembly_op_flops_2, char * precision);
void write_asm_mem (int long long num_rep, int align, int ops, int num_ld, int num_st, char * assembly_op, char * precision);

//Params calculation
int long long flops_math(int long long fp);
int long long mem_math (int long long num_rep, int num_ld, int num_st, int * num_aux);
