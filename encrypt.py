#coding:utf8

import base64
import binascii
try:
    from M2Crypto import RSA as rsa
    rsa_enabled = True
except ImportError:
    rsa_enabled = False

from Utils.rijndael import rijndael

def add_padding(s, block_size, padding_str='\0'):
    """添加填充符号，默认为\0
    """
    floor = len(s) / block_size
    if floor * block_size != len(s):
        exceed_length = (floor+1) * block_size -len(s)
        return s + padding_str * exceed_length
    return s

def remove_padding(s, block_size, padding_str='\0'):
    """删除填充符号
    """
    blocks = len(s) /block_size
    first_part, last_part = s[:(blocks-1) * blocks], s[-block_size:]

    reverse_last_part = last_part[::-1]
    for i,ch in enumerate(reverse_last_part):
        if ch!= padding_str:
            positon = i
            break
    stripped_last_part = reverse_last_part[positon:][::-1]
    return first_part + ''.join(stripped_last_part)

def remove_pcks5_padding(s, block_size):
    pad_len = ord(s[-1]) # last byte contains number of padding bytes
    return s[:-pad_len]

def add_pcks7_padding(s, block_size):
    """添加pcks7填充
    """
    pad_len = block_size - (len(s)% block_size)
    padding = (chr(pad_len) * pad_len)
    return s + padding

def rsa_decrypt(encrypted_msg, key, block_size=128):
    """使用私钥解密，no padding模式
    参数:
        - encrypt_msg: 加密密文(str)
        - key: rsa key或者key文件路径(RsaKey/str)
        - block_size: 块长度(int)
    """
    assert rsa_enabled
    if isinstance(key, basestring):
        key = rsa.load_key(key)
    encrypt_msg = base64.b64decode(encrypted_msg)
    blocks = len(encrypted_msg) / block_size
    decrypt_blocks = []
    for i in range(blocks):
        d = key.private_decrypt(encrypt_msg[i*block_size:(i+1)*block_size], rsa.no_padding)
        unpad_msg = remove_padding(d, block_size)
        decrypt_blocks.append(unpad_msg)

    return ''.join(decrypt_blocks)
    
def rsa_encrypt(plain_msg, key, block_size=128):
    """使用公钥加密 no padding模式
    参数:
        - encrypt_msg: 加密密文(str)
        - key: rsa key或者key文件路径(RsaKey/str)
        - block_size: 块长度(int)
    """
    assert rsa_enabled
    if isinstance(key, basestring):
        key = rsa.load_pub_key(key)
    padded_msg = add_padding(plain_msg, block_size=block_size)
    blocks = len(padded_msg) / block_size
    encrypt_blocks = []
    for i in range(blocks):
        encrypt_msg = key.public_encrypt(padded_msg[i*block_size:(i+1)*block_size],
                rsa.no_padding)
        encrypt_blocks.append(encrypt_msg)
    return base64.b64encode(''.join(encrypt_blocks))


def aes_decrypt(encrypted_msg, key, block_size=16, padding_mode='PCKS7'):
    """AES 解密，key长度为16/24/32位
    参数:
        - encrypt_msg: 加密密文(str)
        - key: 密钥(str)
        - block_size: 块长度(int)
    """
    binary_msg = binascii.a2b_hex(encrypted_msg)
    blocks = len(binary_msg) / block_size
    decrypted_blocks = []
    for i in range(blocks):
        r = rijndael(key, block_size=block_size)
        decrypted_msg = r.decrypt(binary_msg[i*block_size:(i+1)*block_size])
        decrypted_blocks.append(decrypted_msg)

    if padding_mode=='PCKS7':
        return remove_pcks5_padding(''.join(decrypted_blocks), block_size)
    else:
        return remove_padding(''.join(decrypted_blocks))

def aes_encrypt(plain_msg, key, uppercase=True, block_size=16, padding_mode='PCKS7'):
    """AES 加密，key长度为16/24/32位
    参数:
        - encrypt_msg: 加密密文(str)
        - key: 密钥(str)
        - block_size: 块长度(int)
    """
    r = rijndael(key, block_size=block_size)
    if padding_mode == 'PCKS7':
        padded_msg = add_pcks7_padding(plain_msg, block_size=block_size)
    else:
        padded_msg = add_padding(plain_msg, block_size=block_size)
    blocks = len(padded_msg) / block_size
    encrypted_blocks = []
    for i in range(blocks):
        encrypted_msg = r.encrypt(padded_msg[i*block_size:(i+1)*block_size])
        ascii_msg = binascii.b2a_hex(encrypted_msg)
        if uppercase:
            ascii_msg = ascii_msg.upper()
        encrypted_blocks.append(ascii_msg)
    return ''.join(encrypted_blocks)


