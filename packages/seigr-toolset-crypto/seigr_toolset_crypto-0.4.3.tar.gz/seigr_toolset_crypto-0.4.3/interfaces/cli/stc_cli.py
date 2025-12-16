#!/usr/bin/env python3
"""
STC CLI - Command-line interface for Seigr Toolset Crypto

Provides commands for encryption, hashing, and cryptographic operations.
"""

import argparse
import sys
import os
import struct

from interfaces.api import stc_api


def _serialize_metadata_to_binary(metadata: dict) -> bytes:
    """Serialize CLI metadata dictionary to self-sovereign binary format"""
    if not metadata:
        return b''
    
    # Magic header for CLI metadata: STCM (SeigrToolsetCrypto Metadata)
    binary_data = bytearray(b'STCM')
    
    # Serialize each key-value pair
    for key, value in metadata.items():
        # Key (length-prefixed string)
        key_bytes = key.encode('utf-8')
        binary_data.extend(struct.pack('<H', len(key_bytes)))
        binary_data.extend(key_bytes)
        
        # Value (type-tagged)
        if isinstance(value, bool):
            binary_data.extend(b'\x01')  # Boolean type
            binary_data.extend(struct.pack('<?', value))
        elif isinstance(value, int):
            binary_data.extend(b'\x02')  # Integer type
            binary_data.extend(struct.pack('<q', value))  # 64-bit signed
        elif isinstance(value, float):
            binary_data.extend(b'\x03')  # Float type
            binary_data.extend(struct.pack('<d', value))  # 64-bit double
        elif isinstance(value, str):
            binary_data.extend(b'\x04')  # String type
            value_bytes = value.encode('utf-8')
            binary_data.extend(struct.pack('<I', len(value_bytes)))
            binary_data.extend(value_bytes)
        elif isinstance(value, bytes):
            binary_data.extend(b'\x05')  # Bytes type
            binary_data.extend(struct.pack('<I', len(value)))
            binary_data.extend(value)
        # Skip unsupported types for self-sovereignty
        
    return bytes(binary_data)


def _deserialize_binary_to_metadata(data: bytes) -> dict:
    """Deserialize binary data to metadata dictionary"""
    if not data or len(data) < 4:
        return {}
        
    # Check magic header
    if data[:4] != b'STCM':
        raise ValueError("Invalid metadata: missing STCM magic number")
    
    result = {}
    offset = 4
    
    while offset < len(data):
        # Read key
        key_len = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2
        key = data[offset:offset+key_len].decode('utf-8')
        offset += key_len
        
        # Read value type and data
        value_type = data[offset:offset+1]
        offset += 1
        
        if value_type == b'\x01':  # Boolean
            value = struct.unpack('<?', data[offset:offset+1])[0]
            offset += 1
        elif value_type == b'\x02':  # Integer
            value = struct.unpack('<q', data[offset:offset+8])[0]
            offset += 8
        elif value_type == b'\x03':  # Float
            value = struct.unpack('<d', data[offset:offset+8])[0]
            offset += 8
        elif value_type == b'\x04':  # String
            str_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            value = data[offset:offset+str_len].decode('utf-8')
            offset += str_len
        elif value_type == b'\x05':  # Bytes
            bytes_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            value = data[offset:offset+bytes_len]
            offset += bytes_len
        else:
            break  # Unknown type, stop parsing
            
        result[key] = value
        
    return result


def cmd_encrypt(args):
    """Encrypt data"""
    # Read input
    if args.input:
        with open(args.input, 'rb') as f:
            data = f.read()
    else:
        data = input("Enter data to encrypt: ")
    
    # Get seed
    seed = args.seed or input("Enter seed: ")
    
    # Initialize context
    print("Initializing STC context...")
    context = stc_api.initialize(seed)
    
    # Encrypt
    print("Encrypting...")
    encrypted, metadata = context.encrypt(data)
    
    # Output
    if args.output:
        with open(args.output, 'wb') as f:
            f.write(encrypted)
        
        # Save metadata in binary format
        metadata_file = args.output + ".meta"
        metadata_binary = _serialize_metadata_to_binary(metadata)
        with open(metadata_file, 'wb') as f:
            f.write(metadata_binary)
        
        print(f"Encrypted data saved to: {args.output}")
        print(f"Metadata saved to: {metadata_file}")
    else:
        print(f"\nEncrypted (hex): {encrypted.hex()}")
        print(f"\nMetadata: {metadata}")


def cmd_decrypt(args):
    """Decrypt data"""
    # Read encrypted data
    if not args.input:
        print("Error: Input file required for decryption")
        sys.exit(1)
    
    with open(args.input, 'rb') as f:
        encrypted = f.read()
    
    # Read metadata
    metadata_file = args.metadata or (args.input + ".meta")
    if not os.path.exists(metadata_file):
        print(f"Error: Metadata file not found: {metadata_file}")
        sys.exit(1)
    
    with open(metadata_file, 'rb') as f:
        metadata_binary = f.read()
    metadata = _deserialize_binary_to_metadata(metadata_binary)
    
    # Get seed
    seed = args.seed or input("Enter seed: ")
    
    # Initialize context and decrypt
    print("Initializing STC context...")
    context = stc_api.initialize(seed)
    # Context initialization triggers internal state setup needed for decryption
    del context  # Explicitly mark as used for side effects only
    
    print("Decrypting...")
    try:
        decrypted = stc_api.quick_decrypt(encrypted, metadata, seed)
        
        # Output
        if args.output:
            if isinstance(decrypted, str):
                with open(args.output, 'w') as f:
                    f.write(decrypted)
            else:
                with open(args.output, 'wb') as f:
                    f.write(decrypted)
            print(f"Decrypted data saved to: {args.output}")
        else:
            if isinstance(decrypted, str):
                print(f"\nDecrypted: {decrypted}")
            else:
                print(f"\nDecrypted (hex): {decrypted.hex()}")
    except Exception as e:
        print(f"Error during decryption: {e}")
        sys.exit(1)


def cmd_hash(args):
    """Generate hash"""
    # Read input
    if args.input:
        with open(args.input, 'rb') as f:
            data = f.read()
    else:
        data = input("Enter data to hash: ")
    
    # Get seed
    seed = args.seed or input("Enter seed: ")
    
    # Initialize context
    context = stc_api.initialize(seed)
    
    # Hash
    hash_result = context.hash(data)
    
    print(f"\nHash (hex): {hash_result.hex()}")
    print(f"Hash (base64): {__import__('base64').b64encode(hash_result).decode()}")


def cmd_derive_key(args):
    """Derive key"""
    # Get seed
    seed = args.seed or input("Enter seed: ")
    
    # Get key length
    length = args.length or 32
    
    # Initialize context
    context = stc_api.initialize(seed)
    
    # Derive key
    key = context.derive_key(length=length)
    
    print(f"\nDerived Key ({length} bytes):")
    print(f"Hex: {key.hex()}")
    print(f"Base64: {__import__('base64').b64encode(key).decode()}")


def cmd_status(args):
    """Show context status"""
    seed = args.seed or input("Enter seed: ")
    
    context = stc_api.initialize(seed)
    
    # Perform some operations to show evolution
    context.hash("test data 1")
    context.hash("test data 2")
    context.derive_key()
    
    print("\n" + context.get_status())


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Seigr Toolset Crypto - Post-classical cryptographic engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encrypt data
  stc encrypt -i data.txt -o encrypted.bin -s "my-seed"
  
  # Decrypt data
  stc decrypt -i encrypted.bin -o decrypted.txt -s "my-seed"
  
  # Generate hash
  stc hash -i data.txt -s "my-seed"
  
  # Derive key
  stc derive-key -s "my-seed" -l 32
  
  # Show status
  stc status -s "my-seed"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt data')
    encrypt_parser.add_argument('-i', '--input', help='Input file (stdin if not provided)')
    encrypt_parser.add_argument('-o', '--output', help='Output file (stdout if not provided)')
    encrypt_parser.add_argument('-s', '--seed', help='Seed for encryption')
    
    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt data')
    decrypt_parser.add_argument('-i', '--input', required=True, help='Input encrypted file')
    decrypt_parser.add_argument('-o', '--output', help='Output file (stdout if not provided)')
    decrypt_parser.add_argument('-m', '--metadata', help='Metadata file (auto-detected if not provided)')
    decrypt_parser.add_argument('-s', '--seed', help='Seed for decryption')
    
    # Hash command
    hash_parser = subparsers.add_parser('hash', help='Generate probabilistic hash')
    hash_parser.add_argument('-i', '--input', help='Input file (stdin if not provided)')
    hash_parser.add_argument('-s', '--seed', help='Seed for hashing')
    
    # Derive key command
    derive_parser = subparsers.add_parser('derive-key', help='Derive ephemeral key')
    derive_parser.add_argument('-s', '--seed', help='Seed for key derivation')
    derive_parser.add_argument('-l', '--length', type=int, default=32, help='Key length in bytes')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show context status')
    status_parser.add_argument('-s', '--seed', help='Seed for context')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'encrypt':
        cmd_encrypt(args)
    elif args.command == 'decrypt':
        cmd_decrypt(args)
    elif args.command == 'hash':
        cmd_hash(args)
    elif args.command == 'derive-key':
        cmd_derive_key(args)
    elif args.command == 'status':
        cmd_status(args)


if __name__ == '__main__':
    main()
