#include "config_test.h"

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//																					CREATE FP TEST
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void create_benchmark_flops(char * op, char * precision, int long long fp){
	
	int flops;
	char * assembly_op_flops_1, * assembly_op_flops_2;
	
	if(strcmp(op,"mad") == 0){
		select_ISA_flops(&flops, &assembly_op_flops_1, "mul", precision);	//Select FP operation based on the ISA
		select_ISA_flops(&flops, &assembly_op_flops_2, "add", precision);	//Select FP operation based on the ISA
	}else{
		select_ISA_flops(&flops, &assembly_op_flops_1,op, precision);	//Select FP operation based on the ISA
	}
		
	write_asm_fp (fp, op, flops, assembly_op_flops_1, assembly_op_flops_2, precision); 	//Write Assembly Code
	
	//Free auxiliary variables
	free(assembly_op_flops_1);
	if(strcmp(op,"mad") == 0) free(assembly_op_flops_2);
	
	system("make -f Test/Makefile_Benchmark");	
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//																					CREATE MEM TEST
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void create_benchmark_mem(int long long num_rep, int num_ld, int num_st, char * precision){
	
	char * assembly_op;
	int align, ops;
	
	select_ISA_mem(&align, &ops, &assembly_op, precision);   //Select memory operation based on the ISA

	write_asm_mem (num_rep, align, ops, num_ld, num_st, assembly_op, precision); //Write ASM code
		
	//Free auxiliary variables
	free(assembly_op);
	
	system("make -f Test/Makefile_Benchmark");
}