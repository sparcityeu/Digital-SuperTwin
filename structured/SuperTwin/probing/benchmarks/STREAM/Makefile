CC = gcc
CFLAGS = -O3 -fopenmp

FC = gfortran
FFLAGS = -O2 -fopenmp

all: stream_f.exe stream_c.exe stream.icc

stream_f.exe: stream.f mysecond.o
	$(CC) $(CFLAGS) -c mysecond.c
	$(FC) $(FFLAGS) -c stream.f
	$(FC) $(FFLAGS) stream.o mysecond.o -o stream_f.exe

stream_c.exe: stream.c
	$(CC) $(CFLAGS) stream.c -o stream_c.exe

clean:
	rm -f stream_f.exe stream_c.exe *.o

# an example of a more complex build line for the Intel icc compiler
stream.icc: stream.c
	icc -O3 -xCORE-AVX512 -ffreestanding -qopenmp -DSTREAM_ARRAY_SIZE=88000000 -DNTIMES=20 stream.c -o stream.omp.AVX512.80M.20x.icc
	#icc stream.c -O3 -DNTIMES=100 -DOFFSET=0 -DSTREAM_TYPE=double -DSTREAM_ARRAY_SIZE=268435456 -Wall -O3 -mcmodel=medium -qopenmp -shared-intel -qopt-streaming-stores always -xCORE-AVX512 -qopt-zmm-usage=high -o real_thing
