import os
import glob

import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_token_count(data_dir='../../data/all_annotated', model='gpt-3.5-turbo'):
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = 0
    for file in glob.glob(os.path.join(data_dir, '*.txt')):
        total_tokens += num_tokens_from_string(open(file).read(), encoding.name)

    print("Total number of tokens in all annotated text files: ", total_tokens)


if __name__ == '__main__':
    get_token_count()
