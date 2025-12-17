#define WARP_SIZE 32
#define FULL_MASK 0xffffffff
#define OPTIMAL_THREADS 256
__global__ void index_max_cuda_kernel(
  float *index_vals,       
  int   *indices,        
  float *max_vals,        
  float *max_vals_scatter,   
  long batch_size,
  long A_num_block,
  long B_num_block,
  long num_block
);
__global__ void mm_to_sparse_cuda_kernel(
  float *dense_A,   
  float *dense_B,   
  int   *indices,   
  float *sparse_C,  
  long batch_size,
  long A_num_block,
  long B_num_block,
  long dim,
  long num_block
);
__global__ void sparse_dense_mm_cuda_kernel(
  float *sparse_A,  
  int   *indices,   
  float *dense_B,   
  float *dense_C,   
  long batch_size,
  long A_num_block,
  long B_num_block,
  long dim,
  long num_block
);
__global__ void reduce_sum_cuda_kernel(
  float *sparse_A,  
  int   *indices,   
  float *dense_C,   
  long batch_size,
  long A_num_block,
  long B_num_block,
  long num_block
);
__global__ void scatter_cuda_kernel(
  float *dense_A,   
  int   *indices,   
  float *sparse_C,  
  long batch_size,
  long A_num_block,
  long B_num_block,
  long num_block
);