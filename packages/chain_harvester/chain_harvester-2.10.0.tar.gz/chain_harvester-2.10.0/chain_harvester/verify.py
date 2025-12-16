from eth_account import Account
from eth_account.messages import encode_defunct


def verify_signature(message, signature, address):
    """Verify that the message was signed by theaddress."""
    try:
        # Format the message as an specific message
        message_hash = encode_defunct(text=message)
        # Recover the address from the signature
        recovered_address = Account.recover_message(message_hash, signature=signature)
        # Check if the recovered address matches the claimed address
        return recovered_address.lower() == address.lower()
    except Exception:
        return False
