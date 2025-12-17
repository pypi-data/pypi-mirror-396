__global__ void fast_hash_ver1_cuda_kernel(
  int *mask,        
  float *vector,    
  int *Dmat,        
  int *hash_code,   
  int batch_size,
  int num_vector,
  int vector_dim,
  int num_part,
  int num_hash_f,
  int hash_code_len
);
__global__ void lsh_cumulation_ver1_step1_cuda_kernel(
  int *key_mask,           
  int *key_hash_code,      
  float *value,            
  float *hashtable_value,  
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_key,
  int value_dim,
  int offset_warp
);
__global__ void lsh_cumulation_ver1_step2_cuda_kernel(
  int *query_mask,         
  int *query_hash_code,    
  float *hashtable_value,  
  float *cumulation_value, 
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_query,
  int value_dim,
  int offset_warp
);
__global__ void lsh_weighted_cumulation_ver1_step1_cuda_kernel(
  int *key_mask,            
  int *key_hash_code,       
  float *key_weight,        
  float *value,             
  float *hashtable_value,   
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_key,
  int value_dim,
  int weight_dim,
  int offset_warp,
  int weight_idx
);
__global__ void lsh_weighted_cumulation_ver1_step2_cuda_kernel(
  int *query_mask,          
  int *query_hash_code,     
  float *query_weight,      
  float *hashtable_value,   
  float *cumulation_value,  
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_query,
  int value_dim,
  int weight_dim,
  int offset_warp,
  int weight_idx
);
__global__ void count_sort_step1_cuda_kernel(
  int *key_mask,         
  int *key_hash_code,    
  int *count_sort_table, 
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_key
);
__global__ void count_sort_step2_cuda_kernel(
  int *count_sort_table,  
  int batch_size,
  int num_hash_f,
  int hashtable_capacity
);
__global__ void count_sort_step3_cuda_kernel(
  int *key_mask,          
  int *key_hash_code,     
  int *count_sort_table,  
  int *key_sorted_idxes,  
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_key
);
__global__ void extract_query_info_cuda_kernel(
  int *query_mask,       
  int *query_hash_code,  
  int *count_sort_table, 
  int *query_info,       
  int batch_size,
  int num_hash_f,
  int hashtable_capacity,
  int num_query
);
__global__ void lsh_weighted_cumulation_ver2_step2_cuda_kernel(
  int *query_mask,         
  int *query_info,         
  int *key_sorted_idxes,   
  float *query_weight,     
  float *key_weight,       
  float *value,            
  float *cumulation_value, 
  int batch_size,
  int num_hash_f,
  int num_query,
  int num_key,
  int value_dim,
  int weight_dim
);
__global__ void lsh_weighted_cumulation_ver3_step2_cuda_kernel(
  int *query_sorted_idxes,   
  int *key_mask,             
  int *key_info,             
  float *query_weight,       
  float *key_weight,         
  float *value,              
  float *cumulation_value,   
  int batch_size,
  int num_hash_f,
  int num_query,
  int num_key,
  int value_dim,
  int weight_dim
);
__global__ void lsh_weighted_cumulation_ver4_step2_cuda_kernel(
  int *query_sorted_idxes,   
  int *key_mask,             
  int *key_info,             
  float *query_weight,       
  float *key_weight,         
  float *value,              
  float *cumulation_value,   
  int batch_size,
  int num_hash_f,
  int num_query,
  int num_key,
  int value_dim,
  int weight_dim
);