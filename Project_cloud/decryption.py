import base64
import os

def encode_file(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        base64_data = base64.b64encode(file_data)
        return base64_data

def decode_file(base64_data, output_path):
    with open(output_path, 'wb') as f:
        decoded_data = base64.b64decode(base64_data)
        f.write(decoded_data)

if __name__ == '__main__':
    base64_data = b'...'

    decode_file(base64_data, 'output_file.mp4')