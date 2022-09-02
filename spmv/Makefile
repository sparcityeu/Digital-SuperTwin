all:
	g++ -o rcm order.cc -std=c++17 -fopenmp -DREORDER -DRCM
	g++ -o random order.cc -std=c++17 -fopenmp -DREORDER -DRCM -DRANDOM
	g++ -o degree order.cc -std=c++17 -fopenmp -DREORDER -DDEGREE
	g++ -o none order.cc -std=c++17 -fopenmp -DNONE
