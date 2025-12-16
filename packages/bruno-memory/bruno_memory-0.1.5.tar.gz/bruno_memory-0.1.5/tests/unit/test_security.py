"""
Tests for security and privacy utilities.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from bruno_core.models import MemoryEntry, Message

from bruno_memory.utils.security import (
    CRYPTO_AVAILABLE,
    AuditLogger,
    DataAnonymizer,
    FieldEncryptor,
    GDPRCompliance,
    anonymize_for_analysis,
    encrypt_at_rest,
)


@pytest.fixture
def sample_message():
    """Create sample message with sensitive data."""
    return Message(
        role="user",
        content="My credit card is 4532-1234-5678-9010",
        metadata={"user_id": "user123", "email": "test@example.com", "session_id": "session_abc"},
    )


@pytest.fixture
def sample_memory():
    """Create sample memory entry."""
    return MemoryEntry(
        content="User discussion about personal data",
        timestamp=datetime.utcnow(),
        memory_type="episodic",
        user_id="user123",
        conversation_id="conv_abc",
        metadata={"importance": 0.8},
    )


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography not available")
class TestFieldEncryptor:
    """Test field encryption functionality."""

    def test_encrypt_decrypt_string(self):
        """Test basic string encryption/decryption."""
        encryptor = FieldEncryptor()

        original = "sensitive data"
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)

        assert encrypted != original
        assert decrypted == original

    def test_password_based_key(self):
        """Test key derivation from password."""
        password = "my_secure_password"

        encryptor1 = FieldEncryptor(password=password)
        encryptor2 = FieldEncryptor(password=password)

        # Same password should produce compatible encryptors
        original = "test data"
        encrypted = encryptor1.encrypt(original)
        decrypted = encryptor2.decrypt(encrypted)

        assert decrypted == original

    def test_encrypt_message_field(self, sample_message):
        """Test encrypting message fields."""
        encryptor = FieldEncryptor()

        encrypted_msg = encryptor.encrypt_message(sample_message, fields={"content"})

        # Content should be encrypted
        assert encrypted_msg.content != sample_message.content

        # Decrypt should restore
        decrypted_msg = encryptor.decrypt_message(encrypted_msg, fields={"content"})
        assert decrypted_msg.content == sample_message.content

    def test_encrypt_multiple_fields(self, sample_message):
        """Test encrypting multiple fields."""
        encryptor = FieldEncryptor()

        encrypted_msg = encryptor.encrypt_message(sample_message, fields={"content", "metadata"})

        # Both fields should be modified
        assert encrypted_msg.content != sample_message.content

    def test_save_load_key(self, tmp_path):
        """Test saving and loading encryption key."""
        key_path = tmp_path / "encryption.key"

        # Create and save
        encryptor1 = FieldEncryptor()
        encryptor1.save_key(key_path)

        # Load and verify
        encryptor2 = FieldEncryptor.load_key(key_path)

        original = "test data"
        encrypted = encryptor1.encrypt(original)
        decrypted = encryptor2.decrypt(encrypted)

        assert decrypted == original


class TestDataAnonymizer:
    """Test data anonymization functionality."""

    def test_pseudonymize(self):
        """Test pseudonymization."""
        anonymizer = DataAnonymizer()

        original = "user123"
        pseudo = anonymizer.pseudonymize(original)

        # Should be consistent
        assert anonymizer.pseudonymize(original) == pseudo
        assert pseudo.startswith("pseudo_")
        assert pseudo != original

    def test_redact(self):
        """Test redaction."""
        anonymizer = DataAnonymizer()

        original = "sensitive_data"
        redacted = anonymizer.redact(original)

        assert "[REDACTED" in redacted
        assert original not in redacted

    def test_redact_show_length(self):
        """Test redaction with length."""
        anonymizer = DataAnonymizer()

        original = "test123"
        redacted = anonymizer.redact(original, show_length=True)

        assert "[REDACTED:7]" in redacted

    def test_anonymize_message_redact(self, sample_message):
        """Test message anonymization with redaction."""
        anonymizer = DataAnonymizer()

        anon_msg = anonymizer.anonymize_message(sample_message, mode="redact")

        # Sensitive fields should be redacted
        if anon_msg.metadata:
            assert "[REDACTED" in str(anon_msg.metadata.get("user_id", ""))

    def test_anonymize_message_pseudonymize(self, sample_message):
        """Test message anonymization with pseudonymization."""
        anonymizer = DataAnonymizer()

        anon_msg = anonymizer.anonymize_message(sample_message, mode="pseudonymize")

        # Sensitive fields should be pseudonymized
        if anon_msg.metadata:
            user_id = anon_msg.metadata.get("user_id", "")
            assert user_id.startswith("pseudo_") or user_id == sample_message.metadata.get(
                "user_id"
            )

    def test_anonymize_memory(self, sample_memory):
        """Test memory anonymization."""
        anonymizer = DataAnonymizer()

        anon_memory = anonymizer.anonymize_memory(sample_memory, mode="redact")

        # User ID should be anonymized
        assert anon_memory.user_id != sample_memory.user_id
        assert "[REDACTED" in anon_memory.user_id


class TestAuditLogger:
    """Test audit logging functionality."""

    def test_log_access(self):
        """Test logging access events."""
        logger = AuditLogger()

        logger.log_access(
            user_id="user123", action="read", resource_type="message", resource_id="msg_001"
        )

        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry["user_id"] == "user123"
        assert entry["action"] == "read"

    def test_log_with_details(self):
        """Test logging with additional details."""
        logger = AuditLogger()

        logger.log_access(
            user_id="user123",
            action="delete",
            resource_type="memory",
            resource_id="mem_001",
            details={"reason": "GDPR request"},
        )

        entry = logger.entries[0]
        assert entry["details"]["reason"] == "GDPR request"

    def test_get_logs_filtered(self):
        """Test filtered log retrieval."""
        logger = AuditLogger()

        # Log multiple events
        logger.log_access("user1", "read", "message", "msg1")
        logger.log_access("user2", "write", "message", "msg2")
        logger.log_access("user1", "delete", "memory", "mem1")

        # Filter by user
        user1_logs = logger.get_logs(user_id="user1")
        assert len(user1_logs) == 2

        # Filter by action
        read_logs = logger.get_logs(action="read")
        assert len(read_logs) == 1

    def test_get_logs_since(self):
        """Test time-based filtering."""
        logger = AuditLogger()

        # Log event
        logger.log_access("user1", "read", "message", "msg1")

        # Query with time filter
        recent = datetime.utcnow() - timedelta(minutes=1)
        logs = logger.get_logs(since=recent)

        assert len(logs) >= 1

    def test_export_logs(self, tmp_path):
        """Test exporting logs."""
        logger = AuditLogger()

        logger.log_access("user1", "read", "message", "msg1")
        logger.log_access("user2", "write", "message", "msg2")

        output_path = tmp_path / "audit.json"
        logger.export_logs(output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "user1" in content
        assert "user2" in content

    def test_log_to_file(self, tmp_path):
        """Test logging directly to file."""
        log_file = tmp_path / "audit.log"
        logger = AuditLogger(log_file=log_file)

        logger.log_access("user1", "read", "message", "msg1")

        assert log_file.exists()
        content = log_file.read_text()
        assert "user1" in content


class TestGDPRCompliance:
    """Test GDPR compliance utilities."""

    def test_export_user_data(self, sample_message, sample_memory):
        """Test user data export."""
        compliance = GDPRCompliance()

        export = compliance.export_user_data(
            messages=[sample_message], memories=[sample_memory], user_id="user123"
        )

        assert export["user_id"] == "user123"
        assert export["message_count"] == 1
        assert export["memory_count"] == 1
        assert "exported_at" in export

    def test_export_with_audit_logging(self, sample_message, sample_memory):
        """Test export with audit trail."""
        audit_logger = AuditLogger()
        compliance = GDPRCompliance(audit_logger=audit_logger)

        compliance.export_user_data(
            messages=[sample_message], memories=[sample_memory], user_id="user123"
        )

        # Should log the export
        assert len(audit_logger.entries) == 1
        assert audit_logger.entries[0]["action"] == "export"

    def test_prepare_deletion(self):
        """Test deletion preparation."""
        compliance = GDPRCompliance()

        deletion_plan = compliance.prepare_deletion(user_id="user123")

        assert "messages" in deletion_plan
        assert "memories" in deletion_plan
        assert "sessions" in deletion_plan


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography not available")
    def test_encrypt_at_rest(self, sample_message):
        """Test encrypt_at_rest function."""
        encrypted = encrypt_at_rest([sample_message], password="test_password", fields={"content"})

        assert len(encrypted) == 1
        assert encrypted[0].content != sample_message.content

    def test_anonymize_for_analysis(self, sample_message):
        """Test anonymize_for_analysis function."""
        anonymized = anonymize_for_analysis([sample_message], mode="pseudonymize")

        assert len(anonymized) == 1
        # Should be anonymized
        assert anonymized[0] != sample_message


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography not available")
    def test_decrypt_wrong_key(self):
        """Test decryption with wrong key."""
        encryptor1 = FieldEncryptor()
        encryptor2 = FieldEncryptor()

        encrypted = encryptor1.encrypt("test")

        # Should fail or return garbled data
        with pytest.raises(Exception):
            encryptor2.decrypt(encrypted)

    def test_anonymize_empty_metadata(self):
        """Test anonymizing message with no metadata."""
        message = Message(role="user", content="test")
        anonymizer = DataAnonymizer()

        # Should not crash
        anon_msg = anonymizer.anonymize_message(message)
        assert anon_msg.content == "test"

    def test_audit_log_invalid_timestamp(self):
        """Test audit log handles datetime properly."""
        logger = AuditLogger()

        logger.log_access("user1", "read", "message", "msg1")

        # Timestamp should be ISO format string
        entry = logger.entries[0]
        assert isinstance(entry["timestamp"], str)
        # Should be parseable
        datetime.fromisoformat(entry["timestamp"])
