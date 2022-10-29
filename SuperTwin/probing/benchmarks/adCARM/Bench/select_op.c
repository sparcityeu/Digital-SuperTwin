#include "config_test.h"

void select_ISA_flops(int * flop, char ** assembly_op, char * operation, char * precision){
	size_t len;
	if(strcmp(precision, "dp") == 0){
		*flop = DP_OPS;
		if(strcmp(operation, "div") == 0){
			len = strlen(DP_DIV);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op, DP_DIV);
		}	
		if(strcmp(operation, "add") == 0){
			len = strlen(DP_ADD);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op, DP_ADD);
		}		
		if(strcmp(operation, "mul") == 0){ 
			len = strlen(DP_MUL);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op, DP_MUL);  
		}
		if(strcmp(operation, "fma") == 0){
			len = strlen(DP_FMA);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op, DP_FMA);  
		}
	}else{
		*flop = SP_OPS;		
		if(strcmp(operation, "div") == 0){
			len = strlen(SP_DIV);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op,SP_DIV);
		}
		if(strcmp(operation, "add") == 0){
			size_t len = strlen(SP_ADD);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op,SP_ADD);
		}
		if(strcmp(operation, "mul") == 0){
			len = strlen(SP_MUL);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op,SP_MUL);
		}
		if(strcmp(operation, "fma") == 0){
			len = strlen(SP_FMA);
			*assembly_op = (char *) malloc(len+1);
			strcpy(*assembly_op,SP_FMA);	
		}

	}
}

void select_ISA_mem(int * align, int * ops, char ** assembly_op, char * precision){
	size_t len;
	if(strcmp(precision, "dp") == 0){
		*ops = DP_OPS;
		*align = DP_ALIGN;
		len = strlen(DP_MEM);
		*assembly_op = (char *) malloc(len+1);
		strcpy(*assembly_op,DP_MEM);
	}else{
		*ops = SP_OPS;
		*align = SP_ALIGN;
		len = strlen(SP_MEM);
		*assembly_op = (char *) malloc(len+1);
		strcpy(*assembly_op, SP_MEM);	
	}                                
}