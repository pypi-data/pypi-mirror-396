"""Tests for backup utilities."""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from bruno_core.models import MemoryEntry, MemoryType, Message, MessageRole, MessageType

from bruno_memory.utils.backup import BackupExporter, quick_backup, quick_export_to_csv


@pytest.fixture
def sample_messages():
    """Create sample messages."""
    return [
        Message(
            content="Hello",
            role=MessageRole.USER,
            message_type=MessageType.TEXT,
        ),
        Message(
            content="Hi there!",
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT,
        ),
        Message(
            content="How are you?",
            role=MessageRole.USER,
            message_type=MessageType.TEXT,
        ),
    ]


@pytest.fixture
def sample_memories():
    """Create sample memories."""
    return [
        MemoryEntry(
            content="User prefers Python",
            memory_type=MemoryType.FACT,
            user_id="user1",
        ),
        MemoryEntry(
            content="Previous conversation about AI",
            memory_type=MemoryType.EPISODIC,
            user_id="user1",
        ),
    ]


@pytest.fixture
def exporter(tmp_path):
    """Create backup exporter with temp directory."""
    return BackupExporter(str(tmp_path))


class TestBackupExporter:
    """Tests for BackupExporter."""

    def test_initialization(self, tmp_path):
        """Test exporter initialization."""
        exporter = BackupExporter(str(tmp_path))
        assert exporter.output_dir == tmp_path
        assert tmp_path.exists()

    def test_export_messages_to_json(self, exporter, sample_messages):
        """Test JSON export of messages."""
        output_file = exporter.export_messages_to_json(sample_messages)

        assert output_file.exists()
        assert output_file.suffix == ".json"

        # Verify content
        with open(output_file) as f:
            data = json.load(f)

        assert len(data) == 3
        assert data[0]["content"] == "Hello"
        assert data[0]["role"] == "user"

    def test_export_empty_messages(self, exporter):
        """Test exporting empty message list."""
        from bruno_memory.exceptions import BackupError

        with pytest.raises(BackupError):
            exporter.export_messages_to_json([])

    def test_export_messages_to_csv(self, exporter, sample_messages):
        """Test CSV export of messages."""
        try:
            import pandas as pd

            output_file = exporter.export_messages_to_csv(sample_messages)

            assert output_file.exists()
            assert output_file.suffix == ".csv"

            # Verify content
            df = pd.read_csv(output_file)
            assert len(df) == 3
            assert df["content"].iloc[0] == "Hello"

        except ImportError:
            pytest.skip("pandas not available")

    def test_export_messages_to_excel(self, exporter, sample_messages):
        """Test Excel export of messages."""
        try:
            import pandas as pd

            output_file = exporter.export_messages_to_excel(sample_messages)

            assert output_file.exists()
            assert output_file.suffix == ".xlsx"

            # Verify content
            df = pd.read_excel(output_file, sheet_name="Messages")
            assert len(df) == 3

        except ImportError:
            pytest.skip("pandas or openpyxl not available")

    def test_export_memories_to_json(self, exporter, sample_memories):
        """Test JSON export of memories."""
        output_file = exporter.export_memories_to_json(sample_memories)

        assert output_file.exists()
        assert output_file.suffix == ".json"

        # Verify content
        with open(output_file) as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["content"] == "User prefers Python"
        assert data[0]["memory_type"] == "fact"

    def test_import_messages_from_json(self, exporter, sample_messages):
        """Test importing messages from JSON."""
        # Export first
        output_file = exporter.export_messages_to_json(sample_messages)

        # Import
        imported = exporter.import_messages_from_json(str(output_file))

        assert len(imported) == 3
        assert imported[0]["content"] == "Hello"

    def test_anonymize_messages(self, exporter, sample_messages):
        """Test message anonymization."""
        # Add metadata to messages
        for msg in sample_messages:
            if msg.metadata:
                msg.metadata.user_id = "sensitive_user_123"
                msg.metadata.session_id = "sensitive_session_456"

        anonymized = exporter.anonymize_messages(sample_messages)

        assert len(anonymized) == len(sample_messages)
        # Check that sensitive data was anonymized
        for msg in anonymized:
            if msg.metadata and hasattr(msg.metadata, "user_id") and msg.metadata.user_id:
                assert "REDACTED_" in msg.metadata.user_id

    def test_create_backup_archive(self, exporter, sample_messages, sample_memories):
        """Test creating complete backup archive."""
        archive_path = exporter.create_backup_archive(
            messages=sample_messages, memories=sample_memories
        )

        assert archive_path.exists()
        assert (archive_path / "messages.json").exists()
        assert (archive_path / "memories.json").exists()
        assert (archive_path / "manifest.json").exists()

        # Verify manifest
        with open(archive_path / "manifest.json") as f:
            manifest = json.load(f)

        assert manifest["message_count"] == 3
        assert manifest["memory_count"] == 2

    def test_custom_filename(self, exporter, sample_messages, tmp_path):
        """Test export with custom filename."""
        custom_file = tmp_path / "custom_export.json"

        output_file = exporter.export_messages_to_json(sample_messages, str(custom_file))

        assert output_file == custom_file
        assert output_file.exists()

    def test_filename_generation(self, exporter):
        """Test automatic filename generation."""
        filename = exporter._generate_filename("test", "json")

        assert isinstance(filename, Path)
        assert "test_" in filename.name
        assert filename.suffix == ".json"


class TestQuickUtilities:
    """Tests for quick utility functions."""

    def test_quick_export_to_csv(self, sample_messages, tmp_path):
        """Test quick CSV export."""
        try:
            import pandas as pd

            output_file = tmp_path / "quick_export.csv"
            quick_export_to_csv(sample_messages, str(output_file))

            assert output_file.exists()
            df = pd.read_csv(output_file)
            assert len(df) == 3

        except ImportError:
            pytest.skip("pandas not available")

    def test_quick_backup(self, sample_messages, sample_memories, tmp_path):
        """Test quick backup function."""
        archive_path = quick_backup(sample_messages, sample_memories, str(tmp_path))

        assert archive_path.exists()
        assert (archive_path / "messages.json").exists()
        assert (archive_path / "memories.json").exists()
