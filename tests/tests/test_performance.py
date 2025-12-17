import time
from backend.aes.aes_utils import generate_aes_key, encrypt_file

data = b"A" * 1024 * 1024  # 1MB file
key = generate_aes_key()

start = time.time()
encrypt_file(data, key)
end = time.time()

print("Encryption Time (seconds):", round(end - start, 4))
