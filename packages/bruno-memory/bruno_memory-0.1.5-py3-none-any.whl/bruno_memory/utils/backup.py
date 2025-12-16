"""
Backup and export utilities for bruno-memory.

Uses pandas for efficient data export to multiple formats.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from bruno_core.models import MemoryEntry, Message

from bruno_memory.exceptions import BackupError

logger = logging.getLogger(__name__)


def _get_timestamp(obj: Message | MemoryEntry) -> datetime | None:
    """Get timestamp from Message (timestamp) or MemoryEntry (created_at)."""
    return getattr(obj, "timestamp", None) or getattr(obj, "created_at", None)


class BackupExporter:
    """
    Backup and export utility using pandas for data transformation.

    Supports multiple export formats:
    - JSON (preserves all data)
    - CSV (tabular format)
    - Excel (multiple sheets)
    - Parquet (efficient binary format)
    """

    def __init__(self, output_dir: str = "./backups"):
        """
        Initialize backup exporter.

        Args:
            output_dir: Directory for backup files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BackupExporter initialized: {self.output_dir}")

    def _generate_filename(self, prefix: str, extension: str) -> Path:
        """Generate timestamped filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{prefix}_{timestamp}.{extension}"

    def export_messages_to_json(
        self, messages: list[Message], filename: str | None = None
    ) -> Path:
        """
        Export messages to JSON format.

        Args:
            messages: List of Message objects
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if not messages:
            raise BackupError("No messages to export")

        output_file = filename or self._generate_filename("messages", "json")
        output_path = Path(output_file) if filename else output_file

        # Convert to dictionaries
        data = [
            {
                "id": str(msg.id),
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content": msg.content,
                "message_type": (
                    msg.message_type.value
                    if hasattr(msg.message_type, "value")
                    else msg.message_type
                ),
                "created_at": ts.isoformat() if (ts := _get_timestamp(msg)) else None,
                "metadata": msg.metadata.model_dump() if msg.metadata else {},
            }
            for msg in messages
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(messages)} messages to: {output_path}")
        return output_path

    def export_messages_to_csv(
        self, messages: list[Message], filename: str | None = None
    ) -> Path:
        """
        Export messages to CSV format using pandas.

        Args:
            messages: List of Message objects
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for CSV export. Install: pip install pandas")

        if not messages:
            raise BackupError("No messages to export")

        output_file = filename or self._generate_filename("messages", "csv")
        output_path = Path(output_file) if filename else output_file

        # Convert to DataFrame
        data = [
            {
                "id": str(msg.id),
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content": msg.content,
                "message_type": (
                    msg.message_type.value
                    if hasattr(msg.message_type, "value")
                    else msg.message_type
                ),
                "created_at": ts.isoformat() if (ts := _get_timestamp(msg)) else None,
                "session_id": (
                    msg.metadata.session_id
                    if msg.metadata and hasattr(msg.metadata, "session_id")
                    else None
                ),
                "user_id": (
                    msg.metadata.user_id
                    if msg.metadata and hasattr(msg.metadata, "user_id")
                    else None
                ),
            }
            for msg in messages
        ]

        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding="utf-8")

        logger.info(f"Exported {len(messages)} messages to CSV: {output_path}")
        return output_path

    def export_messages_to_excel(
        self, messages: list[Message], filename: str | None = None
    ) -> Path:
        """
        Export messages to Excel format with multiple sheets.

        Args:
            messages: List of Message objects
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if not PANDAS_AVAILABLE:
            raise ImportError(
                "pandas is required for Excel export. Install: pip install pandas openpyxl"
            )

        if not messages:
            raise BackupError("No messages to export")

        output_file = filename or self._generate_filename("messages", "xlsx")
        output_path = Path(output_file) if filename else output_file

        # Main messages data
        messages_data = [
            {
                "id": str(msg.id),
                "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                "content": msg.content[:1000],  # Truncate long content
                "message_type": (
                    msg.message_type.value
                    if hasattr(msg.message_type, "value")
                    else msg.message_type
                ),
                "created_at": _get_timestamp(msg),
                "session_id": (
                    msg.metadata.session_id
                    if msg.metadata and hasattr(msg.metadata, "session_id")
                    else None
                ),
            }
            for msg in messages
        ]

        # Summary statistics
        roles = {}
        for msg in messages:
            role = msg.role.value if hasattr(msg.role, "value") else msg.role
            roles[role] = roles.get(role, 0) + 1

        summary_data = [{"role": k, "count": v} for k, v in roles.items()]

        # Write to Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            pd.DataFrame(messages_data).to_excel(writer, sheet_name="Messages", index=False)
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

        logger.info(f"Exported {len(messages)} messages to Excel: {output_path}")
        return output_path

    def export_memories_to_json(
        self, memories: list[MemoryEntry], filename: str | None = None
    ) -> Path:
        """
        Export memory entries to JSON format.

        Args:
            memories: List of MemoryEntry objects
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if not memories:
            raise BackupError("No memories to export")

        output_file = filename or self._generate_filename("memories", "json")
        output_path = Path(output_file) if filename else output_file

        # Convert to dictionaries
        data = [
            {
                "id": str(mem.id),
                "content": mem.content,
                "memory_type": (
                    mem.memory_type.value if hasattr(mem.memory_type, "value") else mem.memory_type
                ),
                "user_id": str(mem.user_id) if mem.user_id else None,
                "created_at": mem.created_at.isoformat() if mem.created_at else None,
                "updated_at": mem.updated_at.isoformat() if mem.updated_at else None,
                "metadata": mem.metadata.model_dump() if mem.metadata else {},
            }
            for mem in memories
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(memories)} memories to: {output_path}")
        return output_path

    def import_messages_from_json(self, filename: str) -> list[dict[str, Any]]:
        """
        Import messages from JSON format.

        Args:
            filename: Path to JSON file

        Returns:
            List of message dictionaries
        """
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Imported {len(data)} messages from: {filename}")
        return data

    def anonymize_messages(
        self, messages: list[Message], fields_to_anonymize: list[str] | None = None
    ) -> list[Message]:
        """
        Anonymize sensitive fields in messages.

        Args:
            messages: List of Message objects
            fields_to_anonymize: Fields to anonymize (default: user_id, session_id)

        Returns:
            List of anonymized messages
        """
        if fields_to_anonymize is None:
            fields_to_anonymize = ["user_id", "session_id"]

        anonymized = []

        for msg in messages:
            # Create a copy
            msg_dict = msg.model_dump()

            # Anonymize metadata
            if msg_dict.get("metadata"):
                for field in fields_to_anonymize:
                    if field in msg_dict["metadata"]:
                        msg_dict["metadata"][
                            field
                        ] = f"REDACTED_{hash(msg_dict['metadata'][field]) % 10000}"

            # Recreate Message object
            anonymized.append(Message(**msg_dict))

        logger.info(f"Anonymized {len(messages)} messages")
        return anonymized

    def create_backup_archive(
        self,
        messages: list[Message] | None = None,
        memories: list[MemoryEntry] | None = None,
        archive_name: str | None = None,
    ) -> Path:
        """
        Create complete backup archive with all data.

        Args:
            messages: Optional messages to backup
            memories: Optional memories to backup
            archive_name: Optional archive name

        Returns:
            Path to backup archive directory
        """
        archive_dir = archive_name or self._generate_filename("backup", "archive")
        archive_path = Path(archive_dir) if archive_name else archive_dir
        archive_path.mkdir(parents=True, exist_ok=True)

        if messages:
            self.export_messages_to_json(messages, str(archive_path / "messages.json"))

        if memories:
            self.export_memories_to_json(memories, str(archive_path / "memories.json"))

        # Create manifest
        manifest = {
            "created_at": datetime.now().isoformat(),
            "message_count": len(messages) if messages else 0,
            "memory_count": len(memories) if memories else 0,
        }

        with open(archive_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Created backup archive: {archive_path}")
        return archive_path


def quick_export_to_csv(messages: list[Message], output_file: str) -> None:
    """
    Quick utility to export messages to CSV.

    Args:
        messages: List of messages
        output_file: Output CSV file path
    """
    exporter = BackupExporter()
    exporter.export_messages_to_csv(messages, output_file)


def quick_backup(
    messages: list[Message], memories: list[MemoryEntry], output_dir: str = "./backups"
) -> Path:
    """
    Quick utility to create a complete backup.

    Args:
        messages: Messages to backup
        memories: Memories to backup
        output_dir: Output directory

    Returns:
        Path to backup directory
    """
    exporter = BackupExporter(output_dir)
    return exporter.create_backup_archive(messages, memories)
