# training a tokenizer model from scratch 

import os
import argparse
import regex as re
from collections import defaultdict

from functools import partial
from chunking import read_data_by_delimiter
from typing import Dict
from multiprocessing import Queue, Process


GPT_2_PATTERN = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

class Tokenizer:
    
    
    def __init__(self, * , dataset_path:str =None, file_path:str=None, vocab=None, special_tokens:list[bytes]=None, save_path:str = None, num_merges:int = 1000) -> None:
        """
        Initialize a Tokenizer instance.

        Args:
            dataset_path (str, optional): Path to a dataset for training or initializing the vocabulary.
            file_path (str, optional): Path to a file containing a pre-existing vocabulary.
            vocab (dict, optional): Pre-existing vocabulary mapping integers to byte tokens.
            special_tokens (list[bytes], optional): List of special tokens to be included in the vocabulary.
            save_path (str, optional): Path to save the trained tokenizer or vocabulary.
            num_merges (int, optional): Number of merge operations for tokenization (default is 1000).

        The Tokenizer supports three initialization methods, requiring at least one of
        dataset_path, vocab, or file_path to provide a vocabulary source.
        Utilizes a regex pattern based on the GPT-2 tokenizer for splitting tokens.
        """
        self.PATTERN = GPT_2_PATTERN
        self.word_bytes_freq_table = defaultdict(int) # word-bytes -> freq count
        self.special_tokens = special_tokens
        self.vocabulary = self._initialise_vocab()
        self.save_path = save_path
        self.cache = {}
        self.token_count = len(self.vocabulary)
        self.num_merges = num_merges

        if dataset_path:
            self.vocab = self.pretokenizer(dataset_path) 
        elif vocab:
            self.vocab = vocab
        elif file_path:
            self.vocab = self.load_vocab(file_path)
        else:
            raise ValueError('Requires either Dataset path, File path or Vocab one of those should be given')
        
        self.merges = list(self.vocab.values())


    def _initialise_vocab(self):
        idx = 0
        vocab = {}
        for token in self.special_tokens: 
            vocab[idx]=token # int -> bytes
            idx+=1 
        
        for i in range(256):
            vocab[idx] = bytes([i])
            idx+=1
        return vocab
         
        
    def _create_token_dictionary(self,text_chunk, queue):
        # create a token dictionary for reading data 
        partial_dict = defaultdict(int)
        text_decoded = text_chunk.decode('utf-8', errors='replace')

        if self.special_tokens:
            patterns = [re.escape(token.decode('utf-8')) for token in self.special_tokens]
            special_token_pattern = '|'.join(patterns)
        else:
            special_token_pattern = None


        if special_token_pattern:
            text_segments = re.split(special_token_pattern, text_decoded)
        else:
            text_segments = [text_decoded]

        for segment in text_segments:
            if not segment: continue
            
            words = re.findall(self.PATTERN, segment)
            for word in words:
                byte_word = tuple(bytes([b]) for b in word.encode('utf-8'))
                partial_dict[byte_word] += 1

        queue.put(partial_dict)


    def pretokenizer(self, file_path: str):
        queue = Queue()

        processes = []
        for text_chunk in read_data_by_delimiter(file_path):
            process = Process(target = self._create_token_dictionary, args = (text_chunk, queue))
            processes.append(process)

        for p in processes:
            print('starting process :',p)
            p.start()
        
        results = []
        for _ in processes:
            results.append(queue.get())

        for p in processes:
            p.join()

        for local in results:
            for key, count in local.items():
                self.word_bytes_freq_table[key] = self.word_bytes_freq_table.get(key, 0) + count
            
        return self.train()


    def train(self):
        num_merges = self.num_merges - len(self.vocabulary)
        for idx in range(num_merges):
            # word-bytes to char-pair bytes
            print(f'MERGING INDEX is : {idx}')
            char_bytes_freq_table = defaultdict(int) # (b' ', b't') : 100
            char_bytes_to_word_bytes = defaultdict(list) # (b' ', b't') : [b' the', b' tiger' .. etc]
            for word,freq in self.word_bytes_freq_table.items():
                for i in range(len(word)-1):
                    pair = (word[i], word[i+1])
                    char_bytes_to_word_bytes[pair] += [word]
                    char_bytes_freq_table[pair] += freq

            # find the most freq byte-pair 
            sorted_list = max(char_bytes_freq_table.items(), key = lambda  x:(x[1], x[0]))            
            most_frequent_pair, pair_freq = sorted_list[0] , sorted_list[1]

            if pair_freq ==1:
                break

            self.vocabulary[self.token_count] = most_frequent_pair[0] + most_frequent_pair[1]
            self.token_count += 1
            
            # update the word_bytes_freq_table  
            byteword_list = char_bytes_to_word_bytes[most_frequent_pair] # [(b'h' , b'e', b'l', b'l', b'o'), (b'y' , b'e', b'l', b'l', b'o', b'w')]
            
            for byteword in byteword_list: 
                earlier_freq = self.word_bytes_freq_table[byteword]
                update_byte_word = []
                idx =0
                while(idx<len(byteword)):
                    if idx+1 < len(byteword):
                        pair = (byteword[idx], byteword[idx+1])
                        if pair == most_frequent_pair:
                            update_byte_word.append(pair[0] + pair[1])
                            idx+=1
                        else:
                            update_byte_word.append(byteword[idx])
                    else:
                        update_byte_word.append(byteword[idx])
                    
                    idx+=1

                self.word_bytes_freq_table[tuple(update_byte_word)] += earlier_freq
                del self.word_bytes_freq_table[byteword]

        # save vocabulary ( lets save this as a string -> string ) as we can't store bytes in json
        self._save_vocab()

        return self.vocabulary


    def _save_vocab(self):
        # make key, values to string
        string_vocab = {}
        for k,v in self.vocabulary.items():
            string_vocab[str(k)] = str(v)

        import json 
        with open(self.save_path , 'w') as f:
            json.dump(string_vocab, f, indent = 2)


    def load_vocab(self, file_path:str):
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)

        vocab ={}
        for k,v in data.items():
            vocab[eval(k)] = eval(v)
        
        return vocab


    def _each_word_to_bytes(self, word:str) -> list[int]:
        # byte_list = [ch.encode('utf-8') for ch in word] # b'O' , b'n' , b'c' , b'e' ... (this leads to incresed token cost / less total no. of merges) 
        byte_list = [bytes([ch]) for ch in word.encode('utf-8')] # each word byte is considered as a seperate token in this   
        # character -> ’ <- this requires 3 bytes to be represented 
        self.rvocab = {v:k for k,v in self.vocab.items()}

        i =0 
        while i<len(byte_list)-1:
            pair = byte_list[i] + byte_list[i+1]
            if pair in self.merges:
                byte_list[i] = pair
                del byte_list[i+1]
                if i>0:
                    i-=1
            else:
                i+=1

        # final conversion of byte list to token 
        encoded=[]
        for byte in byte_list:
            try: # most of the words will be in this bpe vocab if some characters like é are not there then go to bpe fallback  
                encoded.append(self.rvocab[byte])
            except Exception as e:
                print(f'Found exception as {e}')
                encoded += [self.rvocab[bytes([i])] for i in byte] # but in my vocab this byte should have been present !! 
                # encoded += [i+1 for i in byte] # testing !
                
        del byte_list
        return encoded


    def encoder(self, text:str):
        text_list = re.findall(self.PATTERN, text)
        
        encoded = []
        for word in text_list:
            if word in self.cache:
                word_tokens = self.cache[word]
            else:
                word_tokens = self._each_word_to_bytes(word) 
                self.cache[word] = word_tokens
            
            encoded += word_tokens

        return encoded 


    def decoder(self, tokens:list[int]):
    
        byte_buffer = bytearray()
        for t in tokens:
            byte_buffer.extend(self.vocab[t])

        print('byte array is :', byte_buffer)
        return byte_buffer.decode('utf-8', errors='replace')

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train or load a tokenizer with optional arguments')

    default_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    default_test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test')
    
    default_training_file = os.path.join(default_data_path, 'TinyStoriesV2-GPT4-train.txt')
    # default_training_file = os.path.join(default_data_path, 'TinyStoriesV2-GPT4-valid.txt')
    default_save_path = os.path.join(default_test_path, 'vocab.json')

    parser.add_argument('--training_dataset', type=str, default=default_training_file,
                        help='Path to the training dataset (default: TinyStoriesV2-GPT4-train.txt)')
    parser.add_argument('--saving_path', type=str, default=default_save_path,
                        help='Where to save the trained vocab (default: vocab.json)')
    parser.add_argument('--num_merges', type=int, default=1000,
                        help='Number of merges to perform during BPE (default: 1000)')

    args = parser.parse_args()

    # tokenizer = Tokenizer(
    #     dataset_path=args.training_dataset,
    #     special_tokens=[b'<|endoftext|>'],
    #     save_path=args.saving_path,
    #     num_merges=args.num_merges,
    # )

    # sample for running this as a script : python train.py --training_dataset '' --saving_path '' --num_merges ''

    #load this 
    tokenizer = Tokenizer(file_path = default_save_path,special_tokens=[b'<|endoftext|>'])

    # Sanity check roundtrip
    # text = 'Hello World around us ! 你好世界'
    text = 'Hello World around us !'
    encoded_text = tokenizer.encoder(text)
    print(f'encoded text : {len(encoded_text)}')
    decoded_text = tokenizer.decoder(encoded_text)
    assert decoded_text == text, f'Decoded text is {decoded_text} , should have been : {text} '

