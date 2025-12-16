from eth_account import Account
from eth_account.messages import encode_defunct


def verify_signature(message, signature, address):
    """Verify that the message was signed by the address."""
    try:
        # Format the message as an Ethereum specific message
        message_hash = encode_defunct(text=message)
        # Recover the address from the signature
        recovered_address = Account.recover_message(message_hash, signature=signature)
        # Check if the recovered address matches the claimed address
        return recovered_address.lower() == address.lower()
    except Exception:
        return False


def sign_message(message, private_key):
    """Sign a message using the provided private key.

    Args:
        message (str): The message to sign
        private_key (str): Ethereum private key to sign with

    Returns:
        str: The signature as a hex string
    """
    message_hash = encode_defunct(text=message)
    signed_message = Account.sign_message(message_hash, private_key)
    return signed_message.signature.to_0x_hex()
