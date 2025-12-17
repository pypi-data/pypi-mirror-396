import json
from datadome_encryption import DataDomeDecryptor, DataDomeEncryptor

if __name__ == "__main__":
    cid = "k6~sz7a9PBeHLjcxOOWjR162xQq2Uxsx6wLzxeGlO7~6k3JVwDkwAaQ04wdFEMm2Jt2s0y61mLfJdhWuqtqeJzFMuo7Lf8P5btYX0K4EeoLRcNAtNW04rGhTE3nKpMxi"
    hash_str = "14D062F60A4BDE8CE8647DFC720349"
    excepted_encrypted = open("excepted.txt", "r", encoding="utf-8").read()
    original_signals = json.loads(open("original.json", "r", encoding="utf-8").read())
    
    decryptor = DataDomeEncryptor(hash_str, cid, ctype="captcha")
    for key, value in original_signals:
        decryptor.add(key, value)
    encrypted = decryptor.encrypt()

    # We ignore the last char on compilation due to the 
    # fact that is salt based, so unless you pass
    # the same salt it will be a different char based
    # on the timestamp
    print(f"Encryption matches expected?  {encrypted[:-1] == excepted_encrypted[:-1]}")

    decryptor = DataDomeDecryptor(hash_str, cid, ctype="captcha")
    rebuild_decrypted = decryptor.decrypt(encrypted)
    original_decrypted = decryptor.decrypt(excepted_encrypted)

    mismatch = False
    for rebuild, original in zip(rebuild_decrypted, original_decrypted):
        rebuild_key, rebuil_value = rebuild[0], rebuild[1]
        original_key, original_value = original[0], original[1]

        if rebuild_key != original_key or \
            rebuil_value != original_value:
            mismatch = True
            print(f"(ORIGINAL) Mismatch {original_key} {original_value=}")
            print(f"(REBUILD ) Mismatch {rebuild_key} {rebuil_value=}")
            print("*"*20)

    print(f"Got any mismatch on decryption? {mismatch}")
        