#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif





#include <linux/unistd.h>
#include <unistd.h> 
#include <sys/resource.h>
#include <sys/time.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include <sched.h>
#include <stdint.h>
#include <pthread.h>
#include <mm_malloc.h>
#include <math.h>
#include <stdbool.h>

#include "test_params.h" 

#define NUM_RUNS 1024
//#define NUM_RUNS 100
//#define NUM_RUNS 10
#define EXPECTED_TIME 100000000  //in ns
extern uint64_t clktest(uint64_t iterations) __attribute((sysv_abi));

void sleep0(){
	sched_yield();
}

void set_process_priority_high(){
	setpriority(PRIO_PROCESS, 0, PRIO_MIN);
}

void set_process_priority_normal(){
	setpriority(PRIO_PROCESS, 0, 0);
}

pid_t get_thread_id()
{
	return syscall(__NR_gettid);
}

int long long median(int n, int long long x[]){
	int long long temp;
	int i, j;
	int long long val;

	int long long * x_aux = (int long long *)malloc(n*sizeof(int long long));

	for(i = 0; i < n; i++){
		x_aux[i] = x[i];
	}

	for(i=0; i<n-1; i++){
		for(j=i+1; j<n; j++){
			if(x_aux[j] < x_aux[i]){
				temp = x_aux[i];
				x_aux[i] = x_aux[j];
				x_aux[j] = temp;
			}
		}
	}
	if(n%2==0){
		val = ((x_aux[n/2] + x_aux[n/2 - 1]) / 2);
	}else{
		val = x_aux[n/2];
	}
	free(x_aux);
	return val;
}

static  inline void serialize(){
	asm volatile ( "xorl %%eax, %%eax \n cpuid " : : : "%eax","%ebx","%ecx","%edx" );
}

static  inline long long read_tsc_start(){
	uint64_t d;
	uint64_t a;
	asm __volatile__ (
		"lfence;"
		"rdtsc;"
		"movq %%rdx, %0;"
		"movq %%rax, %1;"
		: "=r" (d), "=r" (a)
		:
		: "%rax", "%rbx","%rcx", "%rdx"
	);

	return ((long long)d << 32 | a);
}

static inline long long read_tsc_end(){
	uint64_t d;
	uint64_t a;
	asm __volatile__ (
        "rdtscp;"
		"movq %%rdx, %0;"
		"movq %%rax, %1;"
		"lfence;"
		: "=r" (d), "=r" (a)
		:
		: "%rax", "%rbx","%rcx", "%rdx"
	);

	return ((long long)d << 32 | a);
}

pthread_attr_t attr;
pthread_barrier_t bar;
pthread_mutex_t mutexsum;

int long long num_rep_max;

int tsc_cycle_counting = 1;
int measure_freq = 1;


int long long ** cycles_s, ** cycles_e;

uint64_t ** time_test_total;

float freq_real = 0;
float freq_nominal = 0;

struct pthread_args{
    int tid;
    float freq;
};

void * benchmark_test(void *t_args){

	int i;
	int long long num_reps_t;
	int long long expected_time = EXPECTED_TIME;

    struct pthread_args *args = t_args;

	uint64_t iterationsHigh = 8e9;
	float nominalClockSpeed = 0, clockSpeedGhzmax = 0;

	long tid = (long)args->tid;
    freq_real = args->freq;


	volatile long long tsc_s;
	volatile long long tsc_e;
	
	#if defined (MEM) || defined (DIV)
		PRECISION * test_var = (PRECISION*)_mm_malloc(NUM_REP*OPS*(NUM_LD+NUM_ST)*sizeof(PRECISION),ALIGN);
		for(i=0; i< NUM_REP*OPS*(NUM_LD+NUM_ST); i++){
			test_var[i] = 1;
		}
	#endif 

	//fprintf(stderr, "NUM_REP: %d, OPS: %d, NUM_LD+NUM_ST: %d\n", NUM_REP, OPS, (NUM_LD+NUM_ST));

	if (measure_freq == 1){
		//CLOCK SPEED MEASURING
		for (int i=0; i<10; i++){

			serialize();
			
			pthread_barrier_wait(&bar);
			
			sleep0();
			
			serialize();

			struct timeval startTv, endTv;

			gettimeofday(&startTv, NULL);
			tsc_s = read_tsc_start();
			clktest(iterationsHigh);
			tsc_e = read_tsc_end();
			gettimeofday(&endTv, NULL);

			uint64_t test_time_diff_ms = 1000 * (endTv.tv_sec - startTv.tv_sec) + ((endTv.tv_usec - startTv.tv_usec) / 1000);
			float latency = 1e6 * (float)test_time_diff_ms / (float)iterationsHigh;
			float clockspeedGhzaux = 1 / latency;


			float nominalClockSpeedaux = (float) ((tsc_e-tsc_s)/((float) (test_time_diff_ms * 1000000)));

			pthread_mutex_lock (&mutexsum);
			
			if(clockSpeedGhzmax < clockspeedGhzaux){
				clockSpeedGhzmax = clockspeedGhzaux;
			}

			if(nominalClockSpeed < nominalClockSpeedaux){
				nominalClockSpeed = nominalClockSpeedaux;
			}
				
			pthread_mutex_unlock (&mutexsum);

			freq_real = clockSpeedGhzmax;
			freq_nominal = nominalClockSpeed;

			serialize();

			pthread_barrier_wait(&bar);

			sleep0();

			serialize();

		}

		//fprintf(stderr, "\nMAX RECORDED FREQUENCY: %f GHz\n", freq_real);
		//fprintf(stderr, "NOMINAL RECORDED FREQUENCY: %f GHz\n", freq_nominal);

	}
	
	pthread_barrier_wait(&bar);
	
	serialize();
	
	tsc_s = read_tsc_start(); 
	
	//CALCULATE NUMBER ITERATIONS FOR TEST CODE TO EXECUTE THE EXPECTED TIME
	#if defined (MEM) || defined (DIV)
		test_function(test_var,NUM_RUNS*3);
    #else
		test_function(NUM_RUNS*3);
	#endif

	tsc_e = read_tsc_end();
	
    
	if(FP_INST >= 131072){
		expected_time = 100000000;  
	} 

	int long long number_rep_aux = (int long long) ceil( (double) expected_time*freq_real*NUM_RUNS*3/(tsc_e-tsc_s));
	
	pthread_mutex_lock (&mutexsum);
	
	if(num_rep_max < number_rep_aux){
		num_rep_max = number_rep_aux;
	}
		
	pthread_mutex_unlock (&mutexsum);

	num_reps_t = num_rep_max;

	serialize();
	
	pthread_barrier_wait(&bar);
	
	sleep0();

	serialize();

	//MICROBENCHMARK LOOP
	for(i=0;i<NUM_RUNS;i++){
		
		serialize();
		
		pthread_barrier_wait(&bar);
		
		sleep0();
		
		serialize();


		tsc_s = read_tsc_start(); 

		
		#if defined (MEM) || defined (DIV) 
			test_function(test_var, num_reps_t);
		#else
			test_function(num_reps_t);
		#endif

        tsc_e = read_tsc_end(); 
		
		serialize();
		
		cycles_s[tid][i] = tsc_s;
		cycles_e[tid][i] = tsc_e;
		
		serialize();
		
		pthread_barrier_wait(&bar);

        sleep0();

	}
	
	serialize();
	
	#if defined (MEM) || defined (DIV)
		_mm_free(test_var);
	#endif
	
	pthread_exit(NULL);
}


void input_parser(int n_args, char*args[], int* num_threads, bool* interleaved, float* freq){
    
    int i;
    
    for(i = 0; i < n_args; i++){
        if(strcmp(args[i], "-threads") == 0){
            (*num_threads) = atoi(args[i+1]);
        } 
        if(strcmp(args[i], "-freq") == 0){
            (*freq) = atof(args[i+1]);
        }
		if(strcmp(args[i], "-measure_freq") == 0){
			if (strcmp(args[i+1], "0") == 0){
				measure_freq = 1;
			} else if (strcmp(args[i+1], "1") == 0)
			{
				measure_freq = 0;
			}
		}
        if(strcmp(args[i], "--interleaved") == 0){
            (*interleaved) = 1;
        }
        if(strcmp(args[i], "-h") == 0 || strcmp(args[i], "--help") == 0){
            printf("Usage: ./test -threads <num_threads> -freq <nominal_freq> -measure_freq [0, 1]  [--interleaved]\n");
            printf("Default Values:\n");
            printf("num_threads = 1\n");
            printf("nominal_freq = 1.0\n");
			printf("measure_freq = 0\n");
            printf("Use --interleaved for systems with several NUMA domains where the cores domain is interleaved (core 0 - node 0; core 1 - node 1; core 2 - node 0 ...)\n");
        }   
    }
}


int main(int argc, char*argv[]){

    int num_threads = 1;
    bool interleaved = 0;
    freq_real = 1.0;

    input_parser(argc, argv, &num_threads, &interleaved, &freq_real);

    int i, j;
	num_rep_max = 0;

	
	int rc;
	pthread_t threads[num_threads];
	void * status;
	cpu_set_t cpus;

    struct pthread_args *t_args = malloc(num_threads*sizeof(struct pthread_args));


	cycles_s = (int long long **)malloc(num_threads*sizeof(int long long *));
	cycles_e = (int long long **)malloc(num_threads*sizeof(int long long *));
	for(i = 0; i < num_threads; i++){
		cycles_s[i] = (int long long *)malloc(NUM_RUNS*sizeof(int long long));
		cycles_e[i] = (int long long *)malloc(NUM_RUNS*sizeof(int long long));
	}
	set_process_priority_high();
	pthread_barrier_init(&bar, NULL, num_threads);
	
    if(interleaved){
        for(i = 0; i < num_threads; i++){
            t_args[i].tid = i;
            t_args[i].freq = freq_real;
            CPU_ZERO(&cpus);
            if(i < 18) CPU_SET(i*2, &cpus);
            if(i >= 18) CPU_SET((i-18)*2+1, &cpus);
            pthread_attr_setaffinity_np(&attr, sizeof(cpu_set_t), &cpus);
            rc = pthread_create(&threads[i], &attr, benchmark_test,(void *) &t_args[i]);
            if (rc){
                printf("ERROR; return code from pthread_create() is %d\n", rc);
                exit(-1);
            }
        }
    }else{
        for(i = 0; i < num_threads; i++){
            t_args[i].tid = i;
            t_args[i].freq = freq_real;
            CPU_ZERO(&cpus);
            CPU_SET(i, &cpus);
            pthread_attr_setaffinity_np(&attr, sizeof(cpu_set_t), &cpus);
            rc = pthread_create(&threads[i], &attr, benchmark_test,(void *) &t_args[i]);
            if (rc){
                printf("ERROR; return code from pthread_create() is %d\n", rc);
                exit(-1);
            }
        }
    }

	
	for(i = 0; i < num_threads; i++){
		rc = pthread_join(threads[i], &status);
		if (rc){
			printf("ERROR; return code from pthread_join() is %d\n", rc);
			exit(-1);
		}
	}
	
	pthread_barrier_destroy(&bar);
	pthread_mutex_destroy(&mutexsum);
	
	set_process_priority_normal();

	
	//PARSE RESULTS
	int long long * min_cycles_start = calloc(NUM_RUNS,sizeof(int long long));
	int long long * max_cycles_end = calloc(NUM_RUNS,sizeof(int long long));

	for(i=0;i<NUM_RUNS;i++){
		min_cycles_start[i] = cycles_s[0][i];
		max_cycles_end[i] = cycles_e[0][i];
		for(j=1;j<num_threads;j++){
			if(cycles_s[j][i] < min_cycles_start[i]) min_cycles_start[i] = cycles_s[j][i];
			if(cycles_e[j][i] > max_cycles_end[i]) max_cycles_end[i] = cycles_e[j][i];
		}
		max_cycles_end[i] = max_cycles_end[i] - min_cycles_start[i];
	}

	printf("%f, %lld, %f, %f",(float)median(NUM_RUNS,max_cycles_end), num_rep_max, freq_real, freq_nominal);

	//FREE ALL VARIABLES
	for(i=0;i<num_threads;i++){
		free(cycles_s[i]);
		free(cycles_e[i]);
	}

	free(min_cycles_start);
	free(max_cycles_end);

	free(cycles_s);
	free(cycles_e);

	return 0;
}
