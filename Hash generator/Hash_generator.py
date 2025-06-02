import time
import hashlib
import base64
import argparse

# Clipboard support
try:
    import pyperclip
except ImportError:
    pyperclip = None
    print("The function to copy to clipboard isn't available, run:\n pip install pyperclip")
	
# Argon hash support
try:
    from argon2.low_level import hash_secret_raw, Type
except ImportError:
    hash_secret_raw = None
    Type = None

# Static salt, update to dynamic if need
SALT = b'Something_[]_ASDF'

# Mappings for output length categories, just add up or remove as you like...
SIZE_MAP = {
    'short': 16,
    'small': 32,
    'medium': 64,
    'big': 128,
    'long': 236,
    'huge': 472,
    'full': None,  # None means no truncation
}

# PBKDF2 hasher
def pbkdf2_hasher(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        500_000,
        dklen=512
    )

# Argon2 hasher
def argon2_hasher(password: str, salt: bytes) -> bytes:
    if hash_secret_raw is None:
        raise RuntimeError("argon2-cffi is required for the 'deep' scheme, run:\n  pip install argon2-cffi")
    return hash_secret_raw(
        password.encode('utf-8'),
        salt,
        time_cost=10,
        memory_cost=102400,
        parallelism=4,
        hash_len=512,
        type=Type.ID
    )

# Available hashing schemes - you may remove, but to add you need:
    # Add a def hasher and update dispatch table
HASH_SCHEMES = {
    'interactive': 'PBKDF2-HMAC-SHA256',
    'deep': 'Argon2id'
}

# Dispatch table
dispatch = {
    'interactive': pbkdf2_hasher,
    'deep': argon2_hasher
}

def derive_password(password: str, scheme: str, salt: bytes) -> str:
    """
    Derive a password using the specified scheme and return a Base64-url string.
    """
    raw = dispatch[scheme](password, salt)
    return base64.urlsafe_b64encode(salt + raw).decode('utf-8')


def generate_reliable_password(password: str, scheme: str) -> str:
    """
    Run derive_password 3 times with 1s pause to ensure consistency.
    """
    outputs = []
    print("\n Generating and validating, please wait.\n")

    for _ in range(3):
        outputs.append(derive_password(password, scheme, SALT))
        time.sleep(1)
    if len(set(outputs)) == 1:
        return outputs[0]
    else:
        raise ValueError("Inconsistent outputs: derivation not reliable. check coding")


def generate_password_with_size(password: str, scheme: str, size: str) -> str:
    """
    Derive a reliable password and truncate according to size.
    """
    full_pw = generate_reliable_password(password, scheme)
    length = SIZE_MAP[size]
    return full_pw if length is None else full_pw[:length]


def copy_to_clipboard(text: str):
    """
    Copy text to clipboard if pyperclip is available.
    """
    if pyperclip:
        try:
            pyperclip.copy(text)
        except Exception:
            pass

def ask_run_again() -> bool:
    """
    Prompt the user if they want to run the program again.
    """
    while True:
        choice = input("\nGenerate another Hash? (y/N): ").strip().lower()
        if choice in ('y', 'yes', '1'):
            return True
        if choice in ('n', 'no', '0', ''):
            return False
        print("Please enter 'y -Yes' or 'n -no'.")

def main():
    parser = argparse.ArgumentParser(
        description="Generate a hash with selectable hashing and length. that can be easily modified"
    )

    parser.add_argument('-i', '--input', type=str, help='Base password/passphrase')
    parser.add_argument('-e', '--encryption', type=str, choices=HASH_SCHEMES.keys(),
                        default=None, help='Hashing scheme: ' + ', '.join(HASH_SCHEMES.keys()))
    parser.add_argument('-s', '--size', type=str, choices=SIZE_MAP.keys(),
                        default=None, help='Output size category: ' + ', '.join(SIZE_MAP.keys()))
    args = parser.parse_args()

    # Prompt for password if not provided
    if not args.input:
        args.input = input("Enter your base password/passphrase: ")
    while not args.input.strip():
        args.input = input("Enter your base password/passphrase (cannot be empty): ")

    # Prompt for encryption if not provided
    if not args.encryption:
        print("Available encryption schemes:")
        for code, name in HASH_SCHEMES.items():
            print(f"  - {code}: {name}")

        while True:
            choice = input("Select encryption scheme: ").strip().lower()
            if choice in HASH_SCHEMES:
                args.encryption = choice
                break
            print(f"Invalid choice. Choose from: {', '.join(HASH_SCHEMES.keys())}")

    # Prompt for size if not provided
    if not args.size:
        print("Available size categories:\n  - ", ', '.join(SIZE_MAP.keys()))
        """
        for key in SIZE_MAP:
            print(f"  - {key}")
        """
        while True:
            choice = input("Select desired size: ").strip().lower()
            if choice in SIZE_MAP:
                args.size = choice
                break
            print(f"Invalid. Choose from: {', '.join(SIZE_MAP.keys())}")
            # print("Invalid. Choose from: \n  - ", ', '.join(SIZE_MAP.keys()))

    try:
        result = generate_password_with_size(args.input, args.encryption, args.size)
        print(f"\nDerived hash [{args.encryption}] was copied to clipboard ({args.size}, {len(result)} chars):\n{result}\n")
        copy_to_clipboard(result)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Run interactively as many times as desired
    while True:
        main()
        if not ask_run_again():
            print("Exiting")
            break
