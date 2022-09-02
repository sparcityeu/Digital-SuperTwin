#include <iostream>
#include <set>

#include <sparsebase/format/format.h>
#include <sparsebase/object/object.h>
#include <sparsebase/preprocess/preprocess.h>
#include <sparsebase/utils/io/reader.h>

#include <omp.h>
#include <algorithm>


using namespace std;
using namespace sparsebase;

using vertex_type = unsigned int;
using edge_type = unsigned int;
using value_type = unsigned int;

int main(int argc, char *argv[]) {

  std::string A_filename = argv[1];
  context::CPUContext cpu_context;
  
  utils::io::MTXReader<unsigned long long, unsigned long long, double> A_reader(A_filename, true);
  //utils::io::MTXReader<unsigned long long, unsigned long long, double> b_reader(A_filename, true);

  format::CSR<unsigned long long, unsigned long long, double> * csr =  A_reader.ReadCSR();
  


#ifdef REORDER

#ifdef DEGREE
  bool ascending = false;
  preprocess::DegreeReorder<unsigned long long, unsigned long long, double> reorderer(ascending);
  unsigned long long* new_order = reorderer.GetReorder(csr, {&cpu_context});
#endif

#ifdef RCM
  preprocess::RCMReorder<unsigned long long, unsigned long long, double> reorderer;
  //unsigned long long* new_order = reorderer.GetReorder(csr, {&cpu_context});
  unsigned long long* new_order = reorderer.GetReorder(csr, {&cpu_context});

#ifdef RANDOM
  std::random_shuffle(new_order, new_order + csr->get_dimensions()[0]);
#endif
#endif



  // Transform object takes the reordering as an argument
  preprocess::Transform<unsigned long long, unsigned long long, double> transform(new_order);
  // The transformer will use `new_order` to restructure `csr`
  format::Format* format = transform.GetTransformation(csr, {&cpu_context});
  // The abstract `Format` pointer is cast into a `CSR` pointer
  format::CSR<unsigned long long, unsigned long long, double>* new_csr = 
    format->As<format::CSR<unsigned long long, unsigned long long, double>>();

#endif

#ifdef NONE
  format::CSR<unsigned long long, unsigned long long, double> * new_csr =  csr;
#endif

  //Don't forget to seed the random ordering
  
  
  unsigned long long* a_row_ptr = new_csr->get_row_ptr();
  unsigned long long* a_col = new_csr->get_col();
  double *a_val = new_csr->get_vals();

  //cout << "dim0: " << csr->get_dimensions()[0] << endl;
  //cout << "dim1: " << csr->get_dimensions()[1] << endl;

  int nov = csr->get_dimensions()[0];
  double out[nov];
  double in[nov]; //init

  for(int i = 0; i < nov; i++){
    in[i] = 1;
  }

  double start = omp_get_wtime();
  for(int k = 0; k < 10000; k++){
    for(int i = 0; i < nov; i++){
      double tmp = 0;
      for(int j = a_row_ptr[i]; j < a_row_ptr[i+1]; j++){
	tmp += a_val[j] * in[a_col[j]];
      }
      out[i] = tmp;
    }
    for(int i = 0; i < nov; i++){                               
      in[i] = out[i];
    }
  }
  double end = omp_get_wtime();
  cout << "Time: " << end - start << endl;
  
  return 0;
}
