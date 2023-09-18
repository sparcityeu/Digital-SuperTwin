#include "config_test.h"

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//																					WRITE FP TEST
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void write_asm_fp (int long long fp, char * op, int flops, char * assembly_op_flops_1, char * assembly_op_flops_2, char * precision){
	
	int i, j;
	FILE * file,*file_header;
	int long long iter;
	j = 0;
		
	file_header =  fopen("Test/test_params.h", "w");
	file = file_header;
	
	//Specific test data
	if(strcmp(op,"div") == 0){
		fprintf(file_header,"#define DIV 1\n");
		fprintf(file_header,"#define NUM_LD 1\n");
		fprintf(file_header,"#define NUM_ST 0\n");
		fprintf(file_header,"#define OPS %d\n",flops);
		fprintf(file_header,"#define NUM_REP 1\n");
		if(strcmp(precision, "dp") == 0){
			fprintf(file_header,"#define PRECISION double\n");
			fprintf(file_header,"#define ALIGN %d\n", (int) DP_ALIGN);
		}else{
			fprintf(file_header,"#define PRECISION float\n");
			fprintf(file_header,"#define ALIGN %d\n", (int) SP_ALIGN);
		}
	}

	fprintf(file_header,"#define FP_INST %lld\n",fp);
	
	iter = flops_math(fp); //Calculate necessary iterations
	
	//Creating Test Function
	if(strcmp(op,"div") == 0){
		fprintf(file,"static inline __attribute__((always_inline)) void test_function(PRECISION * test_var, int long long num_rep_max){\n");
	}else{
		fprintf(file,"static inline __attribute__((always_inline)) void test_function(int long long num_rep_max){\n");
	}
	
	fprintf(file,"\t__asm__ __volatile__ (\n");
	fprintf(file,"\t\t\"movq %%0, %%%%r8\\n\\t\\t\"\n");
	if(strcmp(op,"div") == 0){
		fprintf(file,"\t\t\"movq %%1, %%%%rax\\n\\t\\t\"\n");
		if(strcmp(precision, "dp") == 0){
			fprintf(file,"\t\t\"%s (%%%%rax), %%%%%s0\\n\\t\\t\"\n", DP_MEM, REGISTER);	
		}else{
			fprintf(file,"\t\t\"%s (%%%%rax), %%%%%s0\\n\\t\\t\"\n", SP_MEM, REGISTER);	
		}
	}
	fprintf(file,"\t\t\"Loop2_%%=:\\n\\t\\t\"\n");
	if(iter > 1){
		fprintf(file,"\t\t\"movl $%lld, %%%%edi\\n\\t\\t\"\n",iter);
		fprintf(file,"\t\t\"Loop1_%%=:\\n\\t\\t\"\n");
		for(i = 0; i < BASE_LOOP_SIZE; i++){
			if(i % NUM_REGISTER == 0){
				j = 0;
			}
			#if defined(AVX) || defined(AVX512) || defined(AVX2) || !defined(SSE)
				if(strcmp(op,"div") == 0){
					fprintf(file,"\t\t\"%s %%%%%s0, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, REGISTER, j, REGISTER, j);
				}else if(strcmp(op,"mad") == 0){
					if(j  >= NUM_REGISTER){
						j = 0;
					}
					fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j, REGISTER, j);
					j++;
					if(j  >= NUM_REGISTER){
						j = 0;
					}
					fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_2, REGISTER, j, REGISTER, j, REGISTER, j);
				}else{	
					fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j, REGISTER, j);
				}	
			#else
				if(strcmp(op,"div") == 0){
					fprintf(file,"\t\t\"%s %%%%%s0, %%%%%s%d;\"\n", assembly_op_flops_1, REGISTER, REGISTER, j);
				}else if(strcmp(op,"mad") == 0){
					if(j  >= NUM_REGISTER){
						j = 0;
					}
					fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d;\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j);
					j++;
					if(j  >= NUM_REGISTER){
						j = 0;
					}
					fprintf(file,"\t\t\"%s %%%%%st%d, %%%%%s%d;\"\n", assembly_op_flops_2, REGISTER, j, REGISTER, j);
				}else if(strcmp(op,"FMA") == 0){
					fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j, REGISTER, j);
				}else{
					fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d;\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j);
				}	
			#endif
			j++;
			fp -= iter;
		}	
		fprintf(file,"\t\t\"subl $1, %%%%edi\\n\\t\\t\"\n");
		fprintf(file,"\t\t\"jnz Loop1_%%=\\n\\t\\t\"\n");
	}
	
	for(i = 0; i < fp; i++){
		if(i % 16 == 0){
			j = 0;
		}
		#if defined (AVX512) || defined (AVX) || defined (AVX2)
			if(strcmp(op,"div") == 0){
				fprintf(file,"\t\t\"%s %%%%%s0, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, REGISTER, j, REGISTER, j);
			}else if(strcmp(op,"mad") == 0){
				if(j  >= NUM_REGISTER){
					j = 0;
				}
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j, REGISTER, j);
				j++;
				if(j  >= NUM_REGISTER){
					j = 0;
				}
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_2, REGISTER, j, REGISTER, j, REGISTER, j);
			}else{	
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j, REGISTER, j);
			}	
		#else
			if(strcmp(op,"div") == 0){
				fprintf(file,"\t\t\"%s %%%%%s0, %%%%%s%d;\"\n", assembly_op_flops_1, REGISTER, REGISTER, j);
			}else if(strcmp(op,"mad") == 0){
				if(j  >= NUM_REGISTER){
					j = 0;
				}
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d;\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j);
				j++;
				if(j  >= NUM_REGISTER){
					j = 0;
				}
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d;\"\n", assembly_op_flops_2, REGISTER, j, REGISTER, j);
			}else if(strcmp(op,"FMA") == 0){
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d, %%%%%s%d\\n\\t\\t\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j, REGISTER, j);	
			}else{
				fprintf(file,"\t\t\"%s %%%%%s%d, %%%%%s%d;\"\n", assembly_op_flops_1, REGISTER, j, REGISTER, j);
			}	
		#endif
		j++;
	}
	
	fprintf(file,"\t\t\"sub $1, %%%%r8\\n\\t\\t\"\n");
	fprintf(file,"\t\t\"jnz Loop2_%%=\\n\\t\\t\"\n");
	
	//End Test Function
	if(strcmp(op,"div") == 0){
		fprintf(file,"\t\t:\n\t\t:\"r\"(num_rep_max),\"r\" (test_var)\n\t\t:\"%%rax\",\"%%rdi\","COBLERED"\n\t);\n");
	}else{
		fprintf(file,"\t\t:\n\t\t:\"r\"(num_rep_max)\n\t\t:\"%%rax\",\"%%rdi\","COBLERED"\n\t);\n");
	}
	
	fprintf(file,"}\n\n");
	
	//fclose(file);
	fclose(file_header);
}



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//																					WRITE MEM TEST
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void write_asm_mem (int long long num_rep, int align, int ops, int num_ld, int num_st, char * assembly_op, char * precision){
	
	int offset = 0;
	int aux = num_rep;
	int i, j = 0, k;
	FILE * file, * file_header;
	int num_aux;
	int long long iter;
	
	file_header =  fopen("Test/test_params.h", "w");
	file = file_header;
	
	//Specific Test Data
	fprintf(file_header,"#define MEM 1\n");	
	fprintf(file_header,"#define NUM_LD %d\n",num_ld);
	fprintf(file_header,"#define NUM_ST %d\n",num_st);
	fprintf(file_header,"#define OPS %d\n",ops);
	fprintf(file_header,"#define NUM_REP %lld\n",num_rep);
	if(strcmp(precision, "dp") == 0){
			fprintf(file_header,"#define PRECISION double\n");
	}else{
			fprintf(file_header,"#define PRECISION float\n");
	}
	fprintf(file_header,"#define ALIGN %d\n\n", align);
	fprintf(file_header,"#define FP_INST 1\n\n");
	
	iter = mem_math (num_rep, num_ld, num_st,&num_aux); //Calculate number of iterations
	
	//Create Test Function
	fprintf(file,"static inline __attribute__((always_inline)) void test_function(PRECISION * test_var, int long long num_reps_t){\n");
	
	fprintf(file,"\t__asm__ __volatile__ (\n");
	fprintf(file,"\t\t\"movq %%0, %%%%r8\\n\\t\\t\"\n");
	fprintf(file,"\t\t\"Loop2_%%=:\\n\\t\\t\"\n");
	fprintf(file,"\t\t\"movq %%1, %%%%rax\\n\\t\\t\"\n");
	if(iter > 1){
		fprintf(file,"\t\t\"movq $%lld, %%%%rdi\\n\\t\\t\"\n",iter);
		fprintf(file,"\t\t\"Loop1_%%=:\\n\\t\\t\"\n");

		
		for(i = 0; i < num_aux; i++){
				for(k = 0;k < num_ld;k++){
					if(j  >= NUM_REGISTER){
						j = 0;
					}
					fprintf(file,"\t\t\"%s %d(%%%%rax), %%%%%s%d\\n\\t\\t\"\n", assembly_op, offset, REGISTER,j);
					j++;
					offset += align;
				}
				for(k = 0;k < num_st;k++){
					if(j  >= NUM_REGISTER){
						j = 0;
					}
					fprintf(file,"\t\t\"%s %%%%%s%d, %d(%%%%rax)\\n\\t\\t\"\n", assembly_op, REGISTER, j, offset);
					j++;
					offset += align;
				}
				aux -= iter;
		}	
	
		fprintf(file,"\t\t\"addq $%d, %%%%rax\\n\\t\\t\"\n",offset);
		fprintf(file,"\t\t\"subq $1, %%%%rdi\\n\\t\\t\"\n");
		fprintf(file,"\t\t\"jnz Loop1_%%=\\n\\t\\t\"\n");
	}
	
	num_rep = aux;
	offset = 0;
	
	for(i = 0; i < num_rep; i++){
		for(k = 0;k < num_ld;k++){
			if(j  >= NUM_REGISTER){
				j = 0;
			}
			fprintf(file,"\t\t\"%s %d(%%%%rax), %%%%%s%d\\n\\t\\t\"\n", assembly_op, offset, REGISTER,j);
			j++;
			offset += align;
			
		}
		for(k = 0;k < num_st;k++){
			if(j  >= NUM_REGISTER){
				j = 0;
			}
			fprintf(file,"\t\t\"%s %%%%%s%d, %d(%%%%rax)\\n\\t\\t\"\n", assembly_op, REGISTER, j, offset);
			j++;
			offset += align;
		}
	}
	fprintf(file,"\t\t\"subq $1, %%%%r8\\n\\t\\t\"\n");
	fprintf(file,"\t\t\"jnz Loop2_%%=\\n\\t\\t\"\n");
	
	
	//End Test Function
	fprintf(file,"\t\t:\n\t\t:\"r\"(num_reps_t),\"r\" (test_var)\n\t\t:\"%%rax\",\"%%rdi\",\"%%r8\","COBLERED"\n\t);\n");
	
	fprintf(file,"}\n\n");
	
	fclose(file_header);
}	
