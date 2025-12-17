import json
import time
import random
import ctypes

class DataDomeEncryptor:
    def __init__(self, hash_str, cid, salt=None, ctype="captcha"):
        self.hash = hash_str
        self.cid = cid
        self.ctype = ctype
        self._hsv = self._generate_hsv()
        self._external_salt = salt
        self._init_encryptor()

    def _generate_hsv(self):
        last4 = self.hash[-4:]
        rand_index = int(random.random() * 9)
        rand_hex = hex(int(random.random() * (16**8)))[2:].upper().zfill(8)
        return rand_hex[:rand_index] + last4 + rand_hex[rand_index:]

    def _custom_hash(self, s):
        if not s:
            return 1789537805
        hash_val = 0
        for c in s:
            hash_val = ((hash_val << 5) - hash_val + ord(c)) & 0xFFFFFFFF
            hash_val = ctypes.c_int32(hash_val).value
        return hash_val if hash_val != 0 else 1789537805

    def _mix_int(self, value):
        value ^= (value << 13) & 0xFFFFFFFF
        value = ctypes.c_int32(value).value
        value ^= (value >> 17) & 0xFFFFFFFF
        value = ctypes.c_int32(value).value
        value ^= (value << 5) & 0xFFFFFFFF
        value = ctypes.c_int32(value).value
        return value

    def _create_prng(self, seed, salt):
        state = seed
        round_ = -1
        salt_state = salt
        use_alt = getattr(self, '_use_alt', False)
        self._use_alt = False
        cache = [None]
        def prng(flag=False):
            if cache[0] is not None:
                result = cache[0]
                cache[0] = None
            else:
                nonlocal state, round_, salt_state, use_alt
                round_ += 1
                if round_ > 2:
                    state = self._mix_int(state)
                    round_ = 0
                result = state >> (16 - 8 * round_)
                if use_alt:
                    salt_state -= 1
                    result ^= salt_state
                result &= 255
                if flag:
                    cache[0] = result
            return result
        return [prng]

    def _encode6_bits(self, value):
        if value > 37:
            return 59 + value
        elif value > 11:
            return 53 + value
        elif value > 1:
            return 46 + value
        else:
            return 50 * value + 45

    def _utf8_xor(self, s, prng):
        utf8_bytes = []
        idx = 0
        i = 0
        while i < len(s):
            code = ord(s[i])
            if code < 128:
                utf8_bytes.append(code)
                idx += 1
            elif code < 2048:
                utf8_bytes.append((code >> 6) | 192)
                utf8_bytes.append((code & 63) | 128)
                idx += 2
            elif (code & 0xFC00) == 0xD800 and i + 1 < len(s) and (ord(s[i + 1]) & 0xFC00) == 0xDC00:
                code = 0x10000 + ((code & 0x3FF) << 10) + (ord(s[i + 1]) & 0x3FF)
                utf8_bytes.append((code >> 18) | 240)
                utf8_bytes.append(((code >> 12) & 63) | 128)
                utf8_bytes.append(((code >> 6) & 63) | 128)
                utf8_bytes.append((code & 63) | 128)
                idx += 4
                i += 1
            else:
                utf8_bytes.append((code >> 12) | 224)
                utf8_bytes.append(((code >> 6) & 63) | 128)
                utf8_bytes.append((code & 63) | 128)
                idx += 3
            i += 1
        for j in range(len(utf8_bytes)):
            utf8_bytes[j] ^= prng()
        return utf8_bytes

    def _safe_json(self, value):
        try:
            return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        except Exception:
            return None

    def _encode_payload(self, byte_arr, salt, encode6_bits):
        i = 0
        output = []
        n = salt
        while i < len(byte_arr):
            b1 = (255 & (n - 1) ^ byte_arr[i]) if i < len(byte_arr) else 0
            b2 = (255 & (n - 2) ^ byte_arr[i + 1]) if i + 1 < len(byte_arr) else 0
            b3 = (255 & (n - 3) ^ byte_arr[i + 2]) if i + 2 < len(byte_arr) else 0
            chunk = (b1 << 16) | (b2 << 8) | b3
            output.append(chr(encode6_bits((chunk >> 18) & 63)))
            output.append(chr(encode6_bits((chunk >> 12) & 63)))
            output.append(chr(encode6_bits((chunk >> 6) & 63)))
            output.append(chr(encode6_bits(chunk & 63)))
            i += 3
            n -= 3
        mod = len(byte_arr) % 3
        if mod:
            output = output[:-(3 - mod)]
        return ''.join(output)

    def _reset_encryption_state(self):
        self._use_alt = True
        self._xor_value = -1748112727 if self.ctype == "captcha" else -883841716
        self._prng_seed = (9959949970 & 0xFFFFFFFF) ^ (self._custom_hash(self.hash) & 0xFFFFFFFF) ^ (self._xor_value & 0xFFFFFFFF)
        if self._external_salt is not None:
            self._salt = self._external_salt
        else:
            five_seconds_ago = time.time() - 5
            self._salt = self._mix_int(self._mix_int((int(five_seconds_ago * 1000) >> 3) ^ 11027890091) * 9959949970)
        self.salt = self._salt
        self._prng = self._create_prng(self._prng_seed, self._salt)[0]
        self._buffer = []
        self._is_first = True
        self._seen_keys = set()
        self.prng_seed = self._prng_seed
        self.cid_prng_seed = 1809053797 ^ self._custom_hash(self.cid)

    def _init_encryptor(self):
        self._reset_encryption_state()
        self.add_signal = self._add_signal
        self.build_payload = self._build_payload

    def _add_signal(self, key, value):
        allowed_types = (int, float, str, bool)
        if isinstance(key, str) and key and (value is None or isinstance(value, allowed_types)):
            hsv_temp = None
            key_str = self._safe_json(key)
            value_str = self._safe_json(value)
            if key and value_str is not None and key != 'xt1':
                start_byte = self._prng() ^ (44 if self._buffer else 123)
                self._buffer.append(start_byte)
                key_bytes = self._utf8_xor(key_str, self._prng)
                self._buffer.extend(key_bytes)
                sep_byte = 58 ^ self._prng()
                self._buffer.append(sep_byte)
                value_bytes = self._utf8_xor(value_str, self._prng)
                self._buffer.extend(value_bytes)
                if self._is_first:
                    self._is_first = False
                    if (isinstance(self._hsv, str) and self._hsv) or (isinstance(self._hsv, (int, float)) and not isinstance(self._hsv, bool)):
                        hsv_temp = self._hsv

    def _build_payload(self, cid):
        cid_prng = self._create_prng(1809053797 ^ self._custom_hash(cid), self._salt)[0]
        output = []
        for b in self._buffer:
            output.append(b ^ cid_prng())
        output.append(125 ^ self._prng(True) ^ cid_prng())
        encoded = self._encode_payload(output, self._salt, self._encode6_bits)
        return encoded

    def add(self, key, value):
        self.add_signal(key, value)

    def encrypt(self):
        return self.build_payload(self.cid)

    @staticmethod
    def check_result(encrypted, excepted_path):
        with open(excepted_path, 'r', encoding='utf-8') as f:
            excepted = f.read()
        return encrypted == excepted