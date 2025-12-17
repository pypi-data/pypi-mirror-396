import json
import ctypes

class PRNGHelper:
    def _mix_int(self, value):
        value ^= (value << 13) & 0xFFFFFFFF
        value = ctypes.c_int32(value).value
        value ^= (value >> 17) & 0xFFFFFFFF
        value = ctypes.c_int32(value).value
        value ^= (value << 5) & 0xFFFFFFFF
        value = ctypes.c_int32(value).value
        return value

    def _create_prng(self, seed, salt, use_alt=True):
        state = seed
        round_ = -1
        salt_state = salt
        use_alt_copy = use_alt
        cache = [None]
        def prng(flag=False):
            if cache[0] is not None:
                result = cache[0]
                cache[0] = None
            else:
                nonlocal state, round_, salt_state, use_alt_copy
                round_ += 1
                if round_ > 2:
                    state = self._mix_int(state)
                    round_ = 0
                result = state >> (16 - 8 * round_)
                if use_alt_copy:
                    salt_state -= 1
                    result ^= salt_state
                result &= 255
                if flag:
                    cache[0] = result
            return result
        return [prng]

def custom_hash(s):
    if not s:
        return 1789537805
    hash_val = 0
    for c in s:
        hash_val = ((hash_val << 5) - hash_val + ord(c)) & 0xFFFFFFFF
        hash_val = ctypes.c_int32(hash_val).value
    return hash_val if hash_val != 0 else 1789537805

class DataDomeDecryptor:
    def __init__(self, hash_str, cid, salt=0, ctype="captcha"):
        self.hash = hash_str
        self.cid = cid
        self.salt = salt
        self.ctype = ctype
        self._xor_value = -1748112727 if self.ctype == "captcha" else -883841716
        self.prng_seed = 9959949970 ^ custom_hash(hash_str) ^ self._xor_value
        self.cid_prng_seed = 1809053797 ^ custom_hash(cid)
        self.prng_helper = PRNGHelper()

    def _decode6_bits(self, char_code):
        if 97 <= char_code <= 122:
            return char_code - 59
        if 65 <= char_code <= 90:
            return char_code - 53
        if 48 <= char_code <= 57:
            return char_code - 46
        if char_code == 45:
            return 0
        if char_code == 95:
            return 1
        return 0

    def _decode_custom_base64(self, encoded):
        bytes_ = []
        n = self.salt
        i = 0
        # Process full groups of 4 characters (3 bytes each)
        while i + 4 <= len(encoded):
            c1 = self._decode6_bits(ord(encoded[i]))
            c2 = self._decode6_bits(ord(encoded[i + 1]))
            c3 = self._decode6_bits(ord(encoded[i + 2]))
            c4 = self._decode6_bits(ord(encoded[i + 3]))
            chunk = (c1 << 18) | (c2 << 12) | (c3 << 6) | c4
            bytes_.append(((chunk >> 16) & 255) ^ ((n - 1) & 255))
            bytes_.append(((chunk >> 8) & 255) ^ ((n - 2) & 255))
            bytes_.append((chunk & 255) ^ ((n - 3) & 255))
            i += 4
            n -= 3
        
        # Handle remaining characters (padding case)
        remaining = len(encoded) - i
        if remaining == 2:
            # 2 chars encode 1 byte
            c1 = self._decode6_bits(ord(encoded[i]))
            c2 = self._decode6_bits(ord(encoded[i + 1]))
            chunk = (c1 << 18) | (c2 << 12)
            bytes_.append(((chunk >> 16) & 255) ^ ((n - 1) & 255))
        elif remaining == 3:
            # 3 chars encode 2 bytes
            c1 = self._decode6_bits(ord(encoded[i]))
            c2 = self._decode6_bits(ord(encoded[i + 1]))
            c3 = self._decode6_bits(ord(encoded[i + 2]))
            chunk = (c1 << 18) | (c2 << 12) | (c3 << 6)
            bytes_.append(((chunk >> 16) & 255) ^ ((n - 1) & 255))
            bytes_.append(((chunk >> 8) & 255) ^ ((n - 2) & 255))
        
        return bytes_

    def decrypt(self, encoded):
        buffer_cidprng = self._decode_custom_base64(encoded)
        cid_prng = self.prng_helper._create_prng(self.cid_prng_seed, self.salt, False)[0]
        buffer_with_marker = [b ^ cid_prng() for b in buffer_cidprng]
        return self._parse_buffer(buffer_with_marker)

    def _parse_buffer(self, buffer_with_marker):
        buffer = buffer_with_marker[:-1]  # Remove marker
        prng = self.prng_helper._create_prng(self.prng_seed, self.salt, True)[0]
        decoded_bytes = [b ^ prng() for b in buffer]
        # Decode UTF-8 bytes properly (encryption encodes strings as UTF-8)
        json_str = bytes(decoded_bytes).decode('utf-8')
        return self._parse_json_string(json_str)

    def _json_unescape(self, s):
        """Properly unescape JSON string escape sequences while preserving UTF-8."""
        result = []
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                next_char = s[i + 1]
                if next_char == '"':
                    result.append('"')
                    i += 2
                elif next_char == '\\':
                    result.append('\\')
                    i += 2
                elif next_char == 'n':
                    result.append('\n')
                    i += 2
                elif next_char == 'r':
                    result.append('\r')
                    i += 2
                elif next_char == 't':
                    result.append('\t')
                    i += 2
                elif next_char == 'b':
                    result.append('\b')
                    i += 2
                elif next_char == 'f':
                    result.append('\f')
                    i += 2
                elif next_char == '/':
                    result.append('/')
                    i += 2
                elif next_char == 'u' and i + 5 < len(s):
                    hex_str = s[i + 2:i + 6]
                    try:
                        result.append(chr(int(hex_str, 16)))
                        i += 6
                    except ValueError:
                        result.append(s[i])
                        i += 1
                else:
                    # Unknown escape, keep as-is
                    result.append(s[i])
                    i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    def _parse_json_string(self, json_str):
        result = []
        i = 0
        while i < len(json_str):
            try:
                if json_str[i] == '{' or json_str[i] == ',':
                    i += 1
                    while i < len(json_str) and json_str[i].isspace():
                        i += 1
                    if i >= len(json_str) or json_str[i] != '"':
                        i += 1
                        continue
                    i += 1
                    key_start = i
                    while i < len(json_str) and json_str[i] != '"':
                        if json_str[i] == '\\':
                            i += 2
                        else:
                            i += 1
                    if i >= len(json_str):
                        break
                    key = json_str[key_start:i]
                    i += 1
                    while i < len(json_str) and json_str[i] != ':':
                        i += 1
                    if i >= len(json_str):
                        break
                    i += 1
                    while i < len(json_str) and json_str[i].isspace():
                        i += 1
                    if i >= len(json_str):
                        break
                    value = None
                    if json_str[i] == '"':
                        i += 1
                        value_content = ''
                        escaped = False
                        while i < len(json_str):
                            if escaped:
                                value_content += json_str[i]
                                escaped = False
                            elif json_str[i] == '\\':
                                value_content += json_str[i]
                                escaped = True
                            elif json_str[i] == '"':
                                break
                            else:
                                value_content += json_str[i]
                            i += 1
                        if i < len(json_str):
                            i += 1
                        value = value_content
                    elif json_str[i] == '{':
                        nest = 1
                        i += 1
                        object_str = '{'
                        while i < len(json_str) and nest > 0:
                            if json_str[i] == '{':
                                nest += 1
                            elif json_str[i] == '}':
                                nest -= 1
                            elif json_str[i] == '"':
                                object_str += json_str[i]
                                i += 1
                                while i < len(json_str) and json_str[i] != '"':
                                    if json_str[i] == '\\':
                                        object_str += json_str[i]
                                        i += 1
                                        if i < len(json_str):
                                            object_str += json_str[i]
                                            i += 1
                                    else:
                                        object_str += json_str[i]
                                        i += 1
                                if i < len(json_str):
                                    object_str += json_str[i]
                            if i < len(json_str):
                                object_str += json_str[i]
                                i += 1
                        try:
                            value = json.loads(object_str)
                        except Exception:
                            value = object_str
                    elif json_str[i] == '[':
                        nest = 1
                        i += 1
                        array_str = '['
                        while i < len(json_str) and nest > 0:
                            if json_str[i] == '[':
                                nest += 1
                            elif json_str[i] == ']':
                                nest -= 1
                            elif json_str[i] == '"':
                                array_str += json_str[i]
                                i += 1
                                while i < len(json_str) and json_str[i] != '"':
                                    if json_str[i] == '\\':
                                        array_str += json_str[i]
                                        i += 1
                                        if i < len(json_str):
                                            array_str += json_str[i]
                                            i += 1
                                    else:
                                        array_str += json_str[i]
                                        i += 1
                                if i < len(json_str):
                                    array_str += json_str[i]
                            if i < len(json_str):
                                array_str += json_str[i]
                                i += 1
                        try:
                            value = json.loads(array_str)
                        except Exception:
                            value = array_str
                    elif json_str[i] in '-0123456789':
                        # Parse JSON number: digits, minus, decimal point, and scientific notation (e.g. -3.14e+10)
                        num_str = ''
                        while i < len(json_str) and json_str[i] in '-0123456789.eE+':
                            num_str += json_str[i]
                            i += 1
                        try:
                            value = float(num_str) if '.' in num_str or 'e' in num_str or 'E' in num_str else int(num_str)
                        except Exception:
                            value = num_str
                    elif json_str[i:i+4] == 'true':
                        value = True
                        i += 4
                    elif json_str[i:i+5] == 'false':
                        value = False
                        i += 5
                    elif json_str[i:i+4] == 'null':
                        value = None
                        i += 4
                    else:
                        i += 1
                        continue
                    result.append([
                        key, 
                        self._json_unescape(value) if isinstance(value, str) else value
                    ])
                else:
                    i += 1
            except Exception:
                i += 1
        return result