# DataDome Encryption System: Python Implementation

**A clean Python implementation of DataDome's client-side encryption and decryption, with a simple classes and practical usage examples.**

<div align="center">
  <img src="https://img.shields.io/badge/Status-Complete-brightgreen" alt="Status: Complete">
  <img src="https://img.shields.io/badge/Type-Research-blue" alt="Type: Research">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License: MIT">
  <a href="https://pypi.org/project/datadome-encryption/"><img src="https://img.shields.io/pypi/v/datadome-encryption?color=blue&logo=pypi&style=flat-square" alt="PyPI version"></a>
  <a href="https://github.com/GlizzyKingDreko/datadome-encryption-python"><img src="https://img.shields.io/github/stars/GlizzyKingDreko/datadome-encryption-python?style=flat-square&logo=github" alt="GitHub stars"></a>
</div>
<br>
<div align="center">

  <a href="https://github.com/GlizzyKingDreko/datadome-encryption"><img src="https://img.shields.io/badge/Node.js%20version-339933?logo=nodedotjs&logoColor=white&style=flat-square" alt="Node.js version"></a>
  <a href="https://medium.com/@glizzykingdreko/breaking-down-datadome-captcha-waf-d7b68cef3e21"><img src="https://img.shields.io/badge/Read%20the%20full%20article%20on%20Medium-12100E?logo=medium&logoColor=white&style=flat-square" alt="Read the full article on Medium"></a>
</div>

---

## Table of Contents
- [DataDome Encryption System: Python Implementation](#datadome-encryption-system-python-implementation)
  - [Table of Contents](#table-of-contents)
  - [Installation \& Quick Start](#installation--quick-start)
    - [Basic Usage Example](#basic-usage-example)
  - [Full Example: Encryption/Decryption Validity Check](#full-example-encryptiondecryption-validity-check)
  - [About This Project](#about-this-project)
    - [Converting from NodeJS](#converting-from-nodejs)
  - [Author](#author)
  - [Development](#development)
    - [Running Tests](#running-tests)
    - [Contributing](#contributing)


---

**Need DataDome Bypass Solutions?**

If you need a reliable DataDome bypass solution for your project, turn to the experts who truly understand the technology. My company, TakionAPI, offers professional anti-bot bypass APIs with proven effectiveness against DataDome and other bot-defense systems.

No more worrying about understanding, reversing, and solving the challenge yourself, or about keeping it up to date every day. One simple API call does it all.

We provide free trials, example implementations, and setup assistance to make the entire process easy and smooth.  
- 📄 [Check our straightforward documentation](https://docs.takionapi.tech)  
- 🚀 [Start your trial](https://dashboard.takionapi.tech)  
- 💬 [Contact us on Discord](https://takionapi.tech/discord) for custom development and support.

**Visit [TakionAPI.tech](https://takionapi.tech) for real, high-quality anti-bot bypass solutions — we know what we're doing.**

---

## Installation & Quick Start

Install the module from PyPI:

```bash
pip install datadome-encryption
```

### Basic Usage Example

```python
import json
from datadome_encryption import DataDomeDecryptor, DataDomeEncryptor

cid = "YOUR_CLIENT_ID"
hash_str = "YOUR_HASH_STRING"
signals = [
    ["key1", "value1"],
    ["key2", 123],
    # ... more key-value pairs
]

# Encryption
encryptor = DataDomeEncryptor(hash_str, cid, ctype="captcha")
for key, value in signals:
    encryptor.add(key, value)
encrypted = encryptor.encrypt()
print('Encrypted:', encrypted)

# Decryption
decryptor = DataDomeDecryptor(hash_str, cid, ctype="captcha")
decrypted = decryptor.decrypt(encrypted)
print('Decrypted:', decrypted)
```

Replace `YOUR_CLIENT_ID` and `YOUR_HASH_STRING` with your actual values. The `signals` list should contain your key-value pairs to encrypt.

---

## Full Example: Encryption/Decryption Validity Check

```python
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
```

---

## About This Project

This repository provides a clean, well-documented Python implementation of DataDome's client-side encryption and decryption logic. It is designed for:
- Security researchers
- Developers integrating with DataDome-protected endpoints
- Anyone interested in reverse engineering or cryptography

For a full technical analysis, reverse engineering details, and a Node.js implementation, see the [Node.js version](https://github.com/GlizzyKingDreko/datadome-encryption) and the [Medium article](https://medium.com/@glizzykingdreko/breaking-down-datadome-captcha-waf-d7b68cef3e21).

### Converting from NodeJS
The hardest part of converting the module from NodeJS to Python was ensuring that all calculations were correctly translated and still executed as 32-bit operations, just as NodeJS/JavaScript does—whereas Python uses 64-bit integers by default.

---

## Author

If you found this project helpful or interesting, consider starring the repo and following me for more security research and tools, or buy me a coffee to keep me up

<p align="center">
  <a href="https://github.com/GlizzyKingDreko"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <a href="https://twitter.com/GlizzyKingDreko"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
  <a href="https://medium.com/@GlizzyKingDreko"><img src="https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white" alt="Medium"></a>
  <a href="https://discord.com/users/GlizzyKingDreko"><img src="https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="mailto:glizzykingdreko@protonmail.com"><img src="https://img.shields.io/badge/ProtonMail-8B89CC?style=for-the-badge&logo=protonmail&logoColor=white" alt="Email"></a>
  <a href="https://buymeacoffee.com/glizzykingdreko"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-yellow?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white" alt="Buy Me a Coffee"></a>
</p>

---

## Development

### Running Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests with:

```bash
pytest
```

### Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.