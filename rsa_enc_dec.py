from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import zlib
import base64


def get_encrypted_message(message):
    byte_message = message.encode('utf-8')
    # Import the Public Key and use for encryption using PKCS1_OAEP
    rsa_key = RSA.importKey(public_key)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    # compress the data first
    blob = zlib.compress(byte_message)

    # In determining the chunk size, determine the private key length used in bytes
    # and subtract 42 bytes (when using PKCS1_OAEP). The data will be in encrypted
    # in chunks
    chunk_size = 470
    offset = 0
    repeat = True
    encrypted = b''

    while repeat:
        # The chunk
        chunk = blob[offset:offset + chunk_size]

        # If the data chunk is less then the chunk size, then we need to add
        # padding with " ". This indicates the we reached the end of the file
        # so we end loop here
        if len(chunk) % chunk_size != 0:
            repeat = False
            chunk += b' ' * (chunk_size - len(chunk))

        # Append the encrypted chunk to the overall encrypted file
        encrypted += rsa_key.encrypt(chunk)

        # Increase the offset by chunk size
        offset += chunk_size

    # Base 64 encode the encrypted file
    return base64.b64encode(encrypted)


def get_decrypted_message(message):
    # Import the Private Key and use for decryption using PKCS1_OAEP
    rsa_key = RSA.importKey(private_key)
    rsa_key = PKCS1_OAEP.new(rsa_key)

    # Base 64 decode the data
    encrypted_blob = base64.b64decode(message)

    # In determining the chunk size, determine the private key length used in bytes.
    # The data will be in decrypted in chunks
    chunk_size = 512
    offset = 0
    decrypted = b''

    # keep loop going as long as we have chunks to decrypt
    while offset < len(encrypted_blob):
        # The chunk
        chunk = encrypted_blob[offset: offset + chunk_size]

        # Append the decrypted chunk to the overall decrypted file
        decrypted += rsa_key.decrypt(chunk)

        # Increase the offset by chunk size
        offset += chunk_size

    # return the decompressed decrypted data
    return zlib.decompress(decrypted).decode('utf-8')


def generate_rsa_keys():
    # Generate a public/ private key pair using 4096 bits key length (512 bytes)
    new_key = RSA.generate(4096, e=65537)

    # The private key in PEM format
    private_key = new_key.exportKey("PEM")

    # The public key in PEM Format
    public_key = new_key.publickey().exportKey("PEM")

    # Save private key pem file
    private_key_filename = "keys/private_key.pem"
    fd = open(private_key_filename, "wb")
    fd.write(private_key)
    fd.close()
    print("Private key is saved to ", private_key_filename)

    # Save public key pem file
    public_key_filename = "keys/public_key.pem"
    fd = open(public_key_filename, "wb")
    fd.write(public_key)
    fd.close()
    print("Public key is saved to ", public_key_filename)


# Use the public key for encryption
public_key_file = open("keys/public_key.pem", "rb")
public_key = public_key_file.read()
public_key_file.close()

# Use the private key for decryption
fd = open("keys/private_key.pem", "rb")
private_key = fd.read()
fd.close()
