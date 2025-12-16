"""
Resource strings and constants for Itinerizer.

This module centralizes all hardcoded strings used throughout the application
for better maintainability, consistency, and potential internationalization.
"""

from typing import Dict, Any


class Directories:
    """Directory names and paths."""
    CONFIG_DIR = ".itinerizer"
    ITINERARIES_DIR = "itineraries"
    BACKUPS_DIR = "backups"
    SRC_DIR = "src"
    PACKAGE_DIR = "itinerizer"
    DATA_DIR = "data"
    LOGS_DIR = "logs"


class FileExtensions:
    """File extensions."""
    JSON = ".json"
    MARKDOWN = ".md"
    YAML = ".yaml"
    YML = ".yml"
    LOG = ".log"


class ConfigKeys:
    """Configuration keys."""
    STORAGE_PATH = "storage_path"
    BACKUP_PATH = "backup_path"
    WEB_UI_PORT = "web_ui_port"
    API_PORT = "api_port"
    LOG_LEVEL = "log_level"
    AUTO_BACKUP = "auto_backup"
    BACKUP_RETENTION_DAYS = "backup_retention_days"


class ConfigDefaults:
    """Default configuration values."""
    WEB_UI_PORT = 5001
    API_PORT = 8001
    LOG_LEVEL = "INFO"
    AUTO_BACKUP = True
    BACKUP_RETENTION_DAYS = 30


class CLICommands:
    """CLI command names."""
    LIST = "list"
    GET = "get"
    CREATE = "create"
    DELETE = "delete"
    VALIDATE = "validate"
    EXPORT = "export"
    CONFIG = "config"
    
    # Config subcommands
    CONFIG_SHOW = "show"
    CONFIG_INIT = "init"
    CONFIG_SET = "set"


class CLIArguments:
    """CLI argument names."""
    VERSION = "--version"
    STORAGE_PATH = "--storage-path"
    STATUS = "--status"
    TRIP_TYPE = "--trip-type"
    JSON = "--json"
    FILE = "--file"
    OUTPUT = "--output"
    FORMAT = "--format"
    FORCE = "--force"
    ID = "id"
    KEY = "key"
    VALUE = "value"


class ExportFormats:
    """Export format options."""
    JSON = "json"
    MARKDOWN = "markdown"


class SegmentTypes:
    """Itinerary segment types."""
    FLIGHT = "FLIGHT"
    HOTEL = "HOTEL"
    MEETING = "MEETING"
    ACTIVITY = "ACTIVITY"
    TRANSFER = "TRANSFER"
    CUSTOM = "CUSTOM"


class Messages:
    """User-facing messages."""
    
    class Success:
        """Success messages."""
        CONFIG_INITIALIZED = "✅ Configuration initialized"
        CONFIG_RESET = "✅ Configuration reset to defaults"
        ITINERARY_CREATED = "Created itinerary: {}"
        ITINERARY_DELETED = "Deleted itinerary: {}"
        ITINERARY_EXPORTED = "Exported itinerary ({}) to: {}"
        CONFIG_UPDATED = "✅ Updated {} = {}"
        ITINERARY_VALID = "✓ Itinerary is valid"
    
    class Error:
        """Error messages."""
        ITINERARY_NOT_FOUND = "Itinerary {} not found."
        FILE_NOT_FOUND = "File not found: {}"
        INVALID_CONFIG_FILE = "Warning: Invalid config file, creating default: {}"
        INVALID_CONFIG_KEYS = "Invalid configuration keys: {}"
        CONFIG_UPDATE_FAILED = "❌ Failed to update configuration: {}"
        ITINERARY_INVALID = "✗ Itinerary has validation errors:"
        INVALID_FORMAT = "✗ Invalid itinerary format: {}"
        GENERIC_ERROR = "Error: {}"
    
    class Info:
        """Informational messages."""
        NO_ITINERARIES = "No itineraries found."
        ITINERARIES_FOUND = "Found {} itinerary(ies):"
        CURRENT_CONFIG = "Current Itinerizer Configuration:"
        VALIDATION_WARNINGS = "\nWarnings:"


class MarkdownTemplates:
    """Markdown export templates."""
    YAML_FRONT_MATTER_START = "---"
    YAML_FRONT_MATTER_END = "---"
    
    # Headers
    MAIN_HEADER = "# {} Days {}"
    TRIP_OVERVIEW_HEADER = "## Trip Overview"
    TRAVELERS_HEADER = "## Travelers"
    ITINERARY_HEADER = "## Itinerary"
    FINANCIAL_SUMMARY_HEADER = "## Financial Summary"
    ADDITIONAL_INFO_HEADER = "## Additional Information"
    DAY_HEADER = "### Day {} - {}"
    
    # Segment headers with emojis
    FLIGHT_HEADER = "#### ✈️ Flight: {} ({} - {})"
    HOTEL_HEADER = "#### 🏨 Hotel: {}"
    MEETING_HEADER = "#### 🤝 Meeting: {} ({} - {})"
    ACTIVITY_HEADER = "#### 🎯 Activity: {} ({} - {})"
    TRANSFER_HEADER = "#### 🚗 Transfer: {} ({} - {})"
    CUSTOM_HEADER = "#### 📋 {} ({} - {})"


class NetworkDefaults:
    """Network-related defaults."""
    LOCALHOST = "localhost"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class EncodingDefaults:
    """File encoding defaults."""
    UTF8 = "utf-8"


# Convenience mappings for backward compatibility
BOOLEAN_TRUE_VALUES = ("true", "1", "yes", "on")
INTEGER_CONFIG_KEYS = (ConfigKeys.WEB_UI_PORT, ConfigKeys.API_PORT, ConfigKeys.BACKUP_RETENTION_DAYS)
BOOLEAN_CONFIG_KEYS = (ConfigKeys.AUTO_BACKUP,)
