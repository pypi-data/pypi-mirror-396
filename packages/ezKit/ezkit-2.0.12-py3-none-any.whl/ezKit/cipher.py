import base64
from dataclasses import dataclass
from os import environ, urandom
from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from loguru import logger

DEBUG = environ.get("DEBUG")


@dataclass
class AESCipher:
    """
    Modern AES Encryption using cryptography (AES-GCM mode).
    """

    key_string: str
    algo: str = "sha256"

    def __post_init__(self):

        # 派生 32 字节 AES 密钥（256bit）
        algo_map = {
            "sha256": hashes.SHA256(),
            "sha384": hashes.SHA384(),
            "sha512": hashes.SHA512(),
            "sha3_256": hashes.SHA3_256(),
            "sha3_512": hashes.SHA3_512(),
        }

        hash_algo = algo_map.get(self.algo, hashes.SHA256())

        hkdf = HKDF(
            algorithm=hash_algo,
            length=32,  # AES-256
            salt=None,
            info=b"aes-gcm-key-derivation",
        )
        self.key = hkdf.derive(self.key_string.encode())
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, text: str, aad: Optional[bytes] = None) -> str:
        try:
            nonce = urandom(12)  # 推荐 12 字节
            ciphertext = self.aesgcm.encrypt(nonce, text.encode(), aad)
            # 输出格式： nonce + ciphertext
            return base64.b64encode(nonce + ciphertext).decode()
        except Exception as e:
            logger.error(f"AES encrypt error: {e}")
            if DEBUG:
                logger.exception(e)
            else:
                logger.error(e)
            return ""

    def decrypt(self, token: str, aad: Optional[bytes] = None) -> str:
        try:
            data = base64.b64decode(token)
            nonce = data[:12]
            ciphertext = data[12:]
            plaintext = self.aesgcm.decrypt(nonce, ciphertext, aad)
            return plaintext.decode()
        except Exception as e:
            logger.error(f"AES decrypt error: {e}")
            if DEBUG:
                logger.exception(e)
            else:
                logger.error(e)
            return ""


# 测试
# if __name__ == "__main__":
#     aes = AESCipher("vB7DoRm9C2Kd", algo="sha256")
#     text_instance = {"info": "Hello World"}
#     token_instance = aes.encrypt(json.dumps(text_instance))
#     print(token_instance)
#     dec = aes.decrypt(token_instance)
#     print(dec)
