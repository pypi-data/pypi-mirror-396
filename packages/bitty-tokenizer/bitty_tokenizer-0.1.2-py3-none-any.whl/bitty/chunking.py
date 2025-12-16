# load the whole dataset and divide that into chunks use multiprocessing 
import os 
import sys 

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
valid_file_path = os.path.join(data_path,  'TinyStoriesV2-GPT4-valid.txt') #/TinyStoriesV2-GPT4-valid.txt'
training_file_path = os.path.join(data_path, 'TinyStoriesV2-GPT4-train.txt') #/TinyStoriesV2-GPT4-train.txt'


# cant read this big file to ram so we can use memmap for that 
def read_data_by_delimiter(data_file, delimiter:list[bytes] = [b'<|endoftext|>'], CHUNK_SIZE:int = None):
    
    if CHUNK_SIZE is None:
        CHUNK_SIZE = (10,200) # 8mb to 200mb and depending on no. of multiprocesses to use  

    total_file_size = os.path.getsize(data_file) // (1024*1024)
    print(f'Approximate file size is : {total_file_size} MB ')
    
    if total_file_size < 100:
        CHUNK_SIZE = CHUNK_SIZE[0]
    else:
        CHUNK_SIZE = CHUNK_SIZE[1]

    CHUNK_SIZE_BYTES  = CHUNK_SIZE * 1024 * 1024

    buffer = b''
    with open(data_file , 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE_BYTES)

            if not chunk:
                if buffer: 
                    yield buffer
                break 
            
            buffer += chunk

            last_idx = buffer.rfind(delimiter[0]) # assuming only one delimiter
            if last_idx != -1:
                data_to_yield = buffer[:last_idx]
                buffer = buffer[last_idx + len(delimiter[0]):]

                yield data_to_yield

    del buffer 

