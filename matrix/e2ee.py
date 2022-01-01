from typing import List
from olm import Account
from olm.utility import ed25519_verify, OlmVerifyError
from dataclasses import dataclass
import json

# https://poljar.github.io/python-olm/html/olm.html
# https://matrix.org/docs/guides/end-to-end-encryption-implementation-guide
# https://matrix.org/docs/spec/client_server/r0.4.0#post-matrix-client-r0-keys-upload


@dataclass
class Identity_Keys:
    """Identity keys."""
    curve25519: str
    ed25519: str


@dataclass
class One_time_keys:
    """One time keys."""
    keys: List[str]


@dataclass
class Encrypted_Event_Content:
    """Content of an encrypted event."""
    sender_key: str  # our curve25519 device key
    ciphertext: str  # encrypted payload
    session_id: str  # outbound group session id
    device_id: str  # our device ID
    algorithm: str = "m.megolm.v1.aes-sha2"


# from https://spec.matrix.org/v1.1/appendices/#signing-json
def canonical_json(value: dict) -> str:
    """
    Canonicalize a JSON object.

    :param value: The JSON object.
    :return: The canonicalized JSON object.
    """
    return json.dumps(
        value,
        # Encode code-points outside of ASCII as UTF-8 rather than \u escapes
        ensure_ascii=False,
        # Remove unnecessary white space.
        separators=(',', ':'),
        # Sort the keys of dictionaries.
        sort_keys=True,
        # Encode the resulting Unicode as UTF-8 bytes.
    ).encode("UTF-8")


def check_device_key_signature(data: dict) -> bool:
    """
    The client must first check the signatures 
    on the DeviceKeys objects returned by /keys/query. 
    To do this, it should remove the signatures and 
    unsigned properties, format the remainder as Canonical 
    JSON, and pass the result into olm_ed25519_verify, using 
    the Ed25519 key for the key parameter, and the corresponding 
    signature for the signature parameter. If the signature 
    check fails, no further processing should be done on the device.

    :param device_key: The device key to check
    :return: True if the signature is valid, False otherwise
    """

    device_keys = data["device_keys"]

    # Remove the signature
    device_key_json = device_keys.copy()
    del device_key_json["signatures"]

    # TODO: fix and test this

    try:
        ed25519_verify(device_keys["signatures"]["ed25519"],
                       canonical_json(device_keys["signatures"]),
                       device_keys["signatures"]["ed25519_key"])
        return True
    except OlmVerifyError:
        return False


def get_encrypted_content(sender):
    raise NotImplementedError


class Olm():
    def __init__(self):
        """Initialize the Olm class."""
        self.active = False
        self.account = Account

    def create(self) -> Account:
        """
        Create a new Olm account.
        
        :return: The new Olm account.
        """
        self.account = Account()
        self.active = True
        return self.account

    def load(self, pickle: str, passphrase: str = "") -> Account:
        """
        Load an Olm account from a pickle.
        
        :param pickle: The pickle to load.
        :param passphrase: The passphrase to decrypt the pickle.
        :return: The Olm account.
        """
        self.account = Account.from_pickle(pickle, passphrase)
        self.active = True
        return self.account

    def get_identity_keys(self):
        """
        Get the identity keys.
        
        :return: The identity keys.
        """


        return self.account.identity_keys

    def get_one_time_keys(self):
        """
        Get the one time keys.
        
        :return: The one time keys.
        """
        return self.account.one_time_keys

    def generate_one_time_keys(self, count: int):
        """
        Generate one time keys.
        
        :param count: The number of keys to generate.
        """
        self.account.generate_one_time_keys(count)
