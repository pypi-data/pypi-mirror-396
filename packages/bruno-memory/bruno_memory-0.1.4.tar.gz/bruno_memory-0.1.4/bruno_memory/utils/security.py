"""
Privacy and security utilities for bruno-memory.

Provides encryption, anonymization, GDPR compliance, and audit logging.
Uses cryptography library for secure encryption.
"""

import hashlib
import json
import logging
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

from bruno_core.models import MemoryEntry, Message

logger = logging.getLogger(__name__)


class FieldEncryptor:
    """
    Encrypt and decrypt sensitive fields using Fernet (symmetric encryption).

    Uses cryptography library for secure AES encryption.
    """

    def __init__(self, key: bytes | None = None, password: str | None = None):
        """
        Initialize encryptor.

        Args:
            key: 32-byte encryption key (or None to generate)
            password: Password to derive key from (alternative to key)

        Raises:
            ImportError: If cryptography not available
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography library required for encryption. " "Install: pip install cryptography"
            )

        if password:
            # Derive key from password using PBKDF2
            salt = b"bruno-memory-salt"  # In production, use random salt per user
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = kdf.derive(password.encode())

        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        logger.info("FieldEncryptor initialized")

    def encrypt(self, data: str) -> str:
        """
        Encrypt a string.

        Args:
            data: String to encrypt

        Returns:
            Encrypted string (base64 encoded)
        """
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode("ascii")

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string.

        Args:
            encrypted_data: Encrypted string

        Returns:
            Decrypted string
        """
        decrypted = self.cipher.decrypt(encrypted_data.encode("ascii"))
        return decrypted.decode()

    def encrypt_message(self, message: Message, fields: set[str] | None = None) -> Message:
        """
        Encrypt specified fields in a message.

        Args:
            message: Message to encrypt
            fields: Fields to encrypt (default: content)

        Returns:
            Message with encrypted fields
        """
        if fields is None:
            fields = {"content"}

        message_dict = message.model_dump()

        for field in fields:
            if field in message_dict and message_dict[field]:
                message_dict[field] = self.encrypt(str(message_dict[field]))

        return Message(**message_dict)

    def decrypt_message(self, message: Message, fields: set[str] | None = None) -> Message:
        """
        Decrypt specified fields in a message.

        Args:
            message: Message to decrypt
            fields: Fields to decrypt (default: content)

        Returns:
            Message with decrypted fields
        """
        if fields is None:
            fields = {"content"}

        message_dict = message.model_dump()

        for field in fields:
            if field in message_dict and message_dict[field]:
                try:
                    message_dict[field] = self.decrypt(str(message_dict[field]))
                except Exception as e:
                    logger.warning(f"Failed to decrypt field {field}: {e}")

        return Message(**message_dict)

    def save_key(self, path: Path) -> None:
        """
        Save encryption key to file.

        Args:
            path: Path to save key
        """
        path.write_bytes(self.key)
        logger.info(f"Encryption key saved to {path}")

    @classmethod
    def load_key(cls, path: Path) -> "FieldEncryptor":
        """
        Load encryptor from key file.

        Args:
            path: Path to key file

        Returns:
            FieldEncryptor instance
        """
        key = path.read_bytes()
        return cls(key=key)


class DataAnonymizer:
    """
    Anonymize personal data for privacy compliance (GDPR, etc.).

    Supports field redaction and pseudonymization.
    """

    def __init__(self, salt: str | None = None):
        """
        Initialize anonymizer.

        Args:
            salt: Salt for pseudonymization (generates random if None)
        """
        self.salt = salt or secrets.token_hex(16)
        self.anonymized_fields = {
            "user_id",
            "session_id",
            "conversation_id",
            "email",
            "name",
            "phone",
            "address",
        }
        logger.info("DataAnonymizer initialized")

    def pseudonymize(self, value: str) -> str:
        """
        Create pseudonymized version of value.

        Uses SHA-256 hash with salt for consistent pseudonyms.

        Args:
            value: Value to pseudonymize

        Returns:
            Pseudonymized value (hash)
        """
        combined = f"{value}{self.salt}"
        hash_obj = hashlib.sha256(combined.encode())
        return f"pseudo_{hash_obj.hexdigest()[:16]}"

    def redact(self, value: str, show_length: bool = True) -> str:
        """
        Redact a value.

        Args:
            value: Value to redact
            show_length: Show original length

        Returns:
            Redacted string
        """
        if show_length:
            return f"[REDACTED:{len(value)}]"
        return "[REDACTED]"

    def anonymize_message(self, message: Message, mode: str = "redact") -> Message:
        """
        Anonymize personal data in message.

        Args:
            message: Message to anonymize
            mode: "redact" or "pseudonymize"

        Returns:
            Anonymized message
        """
        message_dict = message.model_dump()

        # Anonymize metadata
        if message_dict.get("metadata"):
            metadata = message_dict["metadata"]
            for field in self.anonymized_fields:
                if field in metadata and metadata[field]:
                    if mode == "pseudonymize":
                        metadata[field] = self.pseudonymize(str(metadata[field]))
                    else:
                        metadata[field] = self.redact(str(metadata[field]))

        return Message(**message_dict)

    def anonymize_memory(self, memory: MemoryEntry, mode: str = "redact") -> MemoryEntry:
        """
        Anonymize personal data in memory.

        Args:
            memory: Memory to anonymize
            mode: "redact" or "pseudonymize"

        Returns:
            Anonymized memory
        """
        memory_dict = memory.model_dump()

        # Anonymize user_id and conversation_id
        if memory_dict.get("user_id"):
            if mode == "pseudonymize":
                memory_dict["user_id"] = self.pseudonymize(memory_dict["user_id"])
            else:
                memory_dict["user_id"] = self.redact(memory_dict["user_id"])

        if memory_dict.get("conversation_id"):
            if mode == "pseudonymize":
                memory_dict["conversation_id"] = self.pseudonymize(memory_dict["conversation_id"])
            else:
                memory_dict["conversation_id"] = self.redact(memory_dict["conversation_id"])

        return MemoryEntry(**memory_dict)


class AuditLogger:
    """
    Audit logging for compliance and security monitoring.

    Records all data access and modifications.
    """

    def __init__(self, log_file: Path | None = None):
        """
        Initialize audit logger.

        Args:
            log_file: Path to audit log file (None = memory only)
        """
        self.log_file = log_file
        self.entries: list[dict[str, Any]] = []
        logger.info(f"AuditLogger initialized: {log_file}")

    def log_access(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Log a data access event.

        Args:
            user_id: User performing action
            action: Action performed (read, write, delete, etc.)
            resource_type: Type of resource (message, memory, etc.)
            resource_id: Resource identifier
            details: Additional details
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
        }

        self.entries.append(entry)

        if self.log_file:
            self._write_to_file(entry)

        logger.info(f"Audit: {user_id} {action} {resource_type}:{resource_id}")

    def _write_to_file(self, entry: dict[str, Any]) -> None:
        """Write audit entry to file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def get_logs(
        self,
        user_id: str | None = None,
        action: str | None = None,
        since: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve audit logs with filtering.

        Args:
            user_id: Filter by user
            action: Filter by action
            since: Filter by timestamp

        Returns:
            List of matching audit entries
        """
        results = self.entries

        if user_id:
            results = [e for e in results if e["user_id"] == user_id]

        if action:
            results = [e for e in results if e["action"] == action]

        if since:
            since_iso = since.isoformat()
            results = [e for e in results if e["timestamp"] >= since_iso]

        return results

    def export_logs(self, output_path: Path) -> None:
        """
        Export all audit logs to JSON file.

        Args:
            output_path: Path to output file
        """
        output_path.write_text(json.dumps(self.entries, indent=2))
        logger.info(f"Exported {len(self.entries)} audit logs to {output_path}")


class GDPRCompliance:
    """
    GDPR compliance utilities.

    Provides right to access, rectification, erasure, and portability.
    """

    def __init__(self, audit_logger: AuditLogger | None = None):
        """
        Initialize GDPR compliance helper.

        Args:
            audit_logger: Optional audit logger for tracking requests
        """
        self.audit_logger = audit_logger
        logger.info("GDPRCompliance initialized")

    def export_user_data(
        self, messages: list[Message], memories: list[MemoryEntry], user_id: str
    ) -> dict[str, Any]:
        """
        Export all user data (right to data portability).

        Args:
            messages: User's messages
            memories: User's memories
            user_id: User identifier

        Returns:
            Dictionary of user data
        """
        if self.audit_logger:
            self.audit_logger.log_access(
                user_id=user_id, action="export", resource_type="user_data", resource_id=user_id
            )

        return {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "messages": [m.model_dump() for m in messages],
            "memories": [m.model_dump() for m in memories],
            "message_count": len(messages),
            "memory_count": len(memories),
        }

    def prepare_deletion(self, user_id: str) -> dict[str, list[str]]:
        """
        Prepare list of resources to delete for user (right to erasure).

        Args:
            user_id: User identifier

        Returns:
            Dictionary of resource types to IDs
        """
        if self.audit_logger:
            self.audit_logger.log_access(
                user_id=user_id,
                action="prepare_deletion",
                resource_type="user_data",
                resource_id=user_id,
            )

        # In practice, this would query the backend
        return {
            "messages": [],  # List of message IDs
            "memories": [],  # List of memory IDs
            "sessions": [],  # List of session IDs
        }


# Convenience functions
def encrypt_at_rest(
    data: list[Message], password: str, fields: set[str] | None = None
) -> list[Message]:
    """
    Encrypt messages for storage.

    Args:
        data: Messages to encrypt
        password: Encryption password
        fields: Fields to encrypt

    Returns:
        List of encrypted messages
    """
    encryptor = FieldEncryptor(password=password)
    return [encryptor.encrypt_message(msg, fields) for msg in data]


def anonymize_for_analysis(data: list[Message], mode: str = "pseudonymize") -> list[Message]:
    """
    Anonymize messages for analytics.

    Args:
        data: Messages to anonymize
        mode: "redact" or "pseudonymize"

    Returns:
        List of anonymized messages
    """
    anonymizer = DataAnonymizer()
    return [anonymizer.anonymize_message(msg, mode) for msg in data]
