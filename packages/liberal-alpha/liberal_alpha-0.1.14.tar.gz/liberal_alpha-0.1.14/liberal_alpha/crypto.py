#!/usr/bin/env python3
"""
crypto.py - Encryption and Decryption functions for Liberal Alpha SDK

This module provides functions for key derivation, ECIES decryption,
AES-GCM decryption (for alpha messages), JSON cleanup, and utilities for handling Ethereum keys.
"""

import logging
import hashlib
import hmac
import struct
import json
from typing import Optional, Tuple

from coincurve import PrivateKey
from Crypto.Cipher import AES
from eth_account import Account

logger = logging.getLogger(__name__)


def hex_to_bytes(hex_string):
    """Convert a hex string to bytes, removing 0x prefix if present."""
    if isinstance(hex_string, str) and hex_string.startswith('0x'):
        hex_string = hex_string[2:]
    return bytes.fromhex(hex_string)


def concat_kdf(hash_func, z: bytes, s1: bytes, kd_len: int) -> bytes:
    """
    NIST SP 800-56 Concatenation Key Derivation Function.
    Matches the Go implementation.
    """
    k = bytearray()
    hash_size = hash_func().digest_size
    counter = 1
    while len(k) < kd_len:
        counter_bytes = struct.pack('>I', counter)
        h_inst = hash_func()
        h_inst.update(counter_bytes)
        h_inst.update(z)
        if s1:
            h_inst.update(s1)
        k.extend(h_inst.digest())
        counter += 1
    return k[:kd_len]


def derive_keys(shared_secret: bytes, s1: bytes, key_len: int) -> Tuple[bytes, bytes]:
    """
    Derive encryption and MAC keys from the shared secret.
    Matches the Go implementation's deriveKeys function.
    """
    # Use SHA-512 as the hash function
    hash_func = hashlib.sha512
    # Generate combined key material
    K = concat_kdf(hash_func, shared_secret, s1, 2 * key_len)
    ke = K[:key_len]
    km = K[key_len:]
    # Hash the MAC key
    h = hashlib.sha256()
    h.update(km)
    km = h.digest()
    return ke, km


def decrypt_ecies(private_key_hex: str, encrypted_data_hex: str) -> Optional[bytes]:
    """
    Decrypt data encrypted with ECIES (Go implementation compatibility).
    """
    try:
        private_key_bytes = hex_to_bytes(private_key_hex)
        encrypted_bytes = hex_to_bytes(encrypted_data_hex)
        private_key = PrivateKey(private_key_bytes)
        pub_key_len = 65
        mac_len = 32
        if len(encrypted_bytes) < pub_key_len + mac_len + 16:
            logger.error(f"Encrypted data too short: {len(encrypted_bytes)} bytes")
            return None
        ephemeral_pub_key = encrypted_bytes[:pub_key_len]
        mac_tag = encrypted_bytes[-mac_len:]
        em = encrypted_bytes[pub_key_len:-mac_len]
        # ECDH shared secret
        shared_secret = private_key.ecdh(ephemeral_pub_key)
        # Derive keys
        key_len = 32
        s1 = b''
        encryption_key, mac_key = derive_keys(shared_secret, s1, key_len)
        # Verify MAC
        h_mac = hmac.new(mac_key, digestmod=hashlib.sha256)
        h_mac.update(em)
        h_mac.update(b'')
        if not hmac.compare_digest(mac_tag, h_mac.digest()):
            # try without s2
            h_mac = hmac.new(mac_key, digestmod=hashlib.sha256)
            h_mac.update(em)
            if not hmac.compare_digest(mac_tag, h_mac.digest()):
                return None
        # Decrypt AES-CTR
        iv = em[:16]
        ciphertext = em[16:]
        cipher = AES.new(encryption_key, AES.MODE_CTR, nonce=iv)
        return cipher.decrypt(ciphertext)
    except Exception as e:
        logger.error(f"ECIES decryption error: {e}")
        return None


def decrypt_aes_gcm(aes_key_hex: str, encrypted_data_hex: str) -> Optional[bytes]:
    """Decrypt data using AES-GCM"""
    try:
        aes_key = hex_to_bytes(aes_key_hex)
        encrypted_data = hex_to_bytes(encrypted_data_hex)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt(ciphertext)
    except Exception as e:
        logger.error(f"AES-GCM decryption error: {e}")
        return None


def clean_json_output(text):
    """
    Clean up JSON output by removing trailing characters after last valid JSON brace.
    """
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    if not isinstance(text, str):
        return text
    if '{' in text:
        brace_count = 0
        last = -1
        for i, c in enumerate(text):
            if c == '{': brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    try:
                        json.loads(text[:i+1])
                        last = i
                        break
                    except json.JSONDecodeError:
                        continue
        if last != -1:
            return text[:last+1]
    return text


def decrypt_alpha_message(private_key_hex: str, encrypted_message) -> Optional[object]:
    """
    Decrypt a message using AES key or ECIES fallback with JSON cleanup.
    """
    try:
        if isinstance(encrypted_message, str):
            try:
                msg = json.loads(encrypted_message)
            except json.JSONDecodeError:
                return decrypt_ecies(private_key_hex, encrypted_message)
        else:
            msg = encrypted_message
        aes_key = msg.get('aes_key')
        data_hex = msg.get('encrypted_data')
        if aes_key and data_hex:
            plaintext = decrypt_aes_gcm(aes_key, data_hex)
            if plaintext:
                cleaned = clean_json_output(plaintext)
                if isinstance(cleaned, str) and cleaned.startswith('{'):
                    return json.loads(cleaned)
                return cleaned
        # fallback to ECIES
        if isinstance(msg, str) or data_hex:
            return decrypt_ecies(private_key_hex, data_hex or msg)
    except Exception as e:
        logger.error(f"Message processing error: {e}")
    return None


def get_wallet_address(private_key: str) -> str:
    """Get Ethereum wallet address from private key."""
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    return Account.from_key(private_key).address
