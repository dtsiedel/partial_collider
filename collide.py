import argparse
import hashlib
import io
import pathlib


def buffer_of(s: str):
    return io.BytesIO(str.encode(s, encoding='utf-8')).getbuffer()

def hash_file(path: pathlib.Path, hasher) -> str:
    BUF_SIZE = 65536
    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target_file', type=str, help='The target file')
    parser.add_argument('payload_file', type=str, help='The payload file')

    parser.add_argument('--max_iterations', type=int, default=1000000, help='Maximum number of iterations (default: 1 million)')
    parser.add_argument('--hash_type', type=str, choices=['md5', 'sha1', 'sha256'], default='md5', help='Hash type (options: md5, sha1, sha256)')
    parser.add_argument('--num_match', type=int, default=3, help='How many chars to match')
    args = parser.parse_args()

    if args.hash_type == 'md5':
        hash_func = hashlib.md5
    elif args.hash_type == 'sha1':
        hash_func = hashlib.sha1
    elif args.hash_type == 'sha256':
        hash_func = hashlib.sha256
    else:
        print(f'Invalid hash type {args.hash_type}. Defaulting to md5')
        hash_func = hashlib.md5

    target_hash = hash_file(pathlib.Path(args.target_file), hash_func())

    assert args.num_match < len(target_hash) // 2
    start = target_hash[:args.num_match]
    end = target_hash[-args.num_match:]

    print(f'target hash is {target_hash}. Matching {start} and {end}.')

    with open(args.payload_file, 'r') as payload:
        original = payload.read()
    iters = 0
    while True:
        hasher = hash_func()
        the_str = original + "\n" + '#'*iters
        hasher.update(buffer_of(the_str))

        h = hasher.hexdigest()
        print(h)
        if h.startswith(start) and h.endswith(end):
            print(f'HIT! With {iters} iters.')
            break
        iters += 1

    path = pathlib.Path(args.target_file)
    output_file = path.parent / (path.stem + "_mal" + path.suffix)
    with open(output_file, 'w') as out_file:
        out_file.write(the_str)


if __name__ == '__main__':
    main()
