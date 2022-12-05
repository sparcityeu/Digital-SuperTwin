CC = gcc
CFLAGS = -O3 -fopenmp

FC = gfortran
FFLAGS = -O2 -fopenmp

all: stream_gcc stream_avx stream_avx2 stream_avx512

stream_gcc: stream.c
	$(CC) $(CFLAGS) stream.c -o stream_c

clean:
	rm -f stream_f.exe stream_c.exe *.o


# an example of a more complex build line for the Intel icc compiler
stream_avx: stream.c
	icx stream.c -O3 -DNTIMES=100 -DOFFSET=0 -DSTREAM_TYPE=double -DSTREAM_ARRAY_SIZE=268435456 -Wall -O3 -mcmodel=medium -qopenmp -shared-intel -xAVX -o stream_avx

stream_avx2: stream.c
	icx stream.c -O3 -DNTIMES=100 -DOFFSET=0 -DSTREAM_TYPE=double -DSTREAM_ARRAY_SIZE=268435456 -Wall -O3 -mcmodel=medium -qopenmp -shared-intel -xCORE-AVX2 -o stream_avx2

stream_avx512: stream.c
	icx stream.c -O3 -DNTIMES=100 -DOFFSET=0 -DSTREAM_TYPE=double -DSTREAM_ARRAY_SIZE=268435456 -Wall -O3 -mcmodel=medium -qopenmp -shared-intel -xCORE-AVX512 -qopt-zmm-usage=high -o stream_avx512
