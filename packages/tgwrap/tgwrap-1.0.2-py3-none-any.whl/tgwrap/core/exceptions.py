"""Custom exceptions for tgwrap."""

class TgWrapError(Exception):
    """Base exception for all tgwrap errors."""


class ConfigurationError(TgWrapError):
    """Configuration-related errors."""


class ValidationError(TgWrapError):
    """Input validation errors."""


class CommandExecutionError(TgWrapError):
    """Command execution errors."""
    def __init__(self, message: str, command: str | None = None, return_code: int | None = None):
        super().__init__(message)
        self.command = command
        self.return_code = return_code


class SecurityError(TgWrapError):
    """Security-related errors."""


class TerragruntVersionError(TgWrapError):
    """Terragrunt version compatibility errors."""


class FileSystemError(TgWrapError):
    """File system operation errors."""


class NetworkError(TgWrapError):
    """Network-related errors."""


class AzureAuthenticationError(TgWrapError):
    """Azure authentication errors."""


class AnalysisError(TgWrapError):
    """Plan analysis errors."""


class DeploymentError(TgWrapError):
    """Deployment operation errors."""
