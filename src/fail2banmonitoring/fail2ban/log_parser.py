import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class Fail2BanLogParser:
    """Parse fail2ban logs and extract IP addresses."""

    def __init__(self, log_path: str | None, output_file: str | None) -> None:
        """Initialize the Fail2BanLogParser with log and output file paths."""
        self.log_path = log_path
        self.output_file = output_file
        # Regex pattern to match ban entries with IP addresses
        self.pattern = re.compile(r"Ban (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")

    def read_logs(self) -> set[str]:
        """Read logs from the specified file path and extract banned IP addresses.

        Returns:
            Set of banned IP addresses.

        Raises:
            FileNotFoundError: If the log file does not exist
            PermissionError: If the log file cannot be accessed due to permissions
            ValueError: If the log path is not provided

        """
        banned_ips = set()

        if not self.log_path:
            logger.error("No log path provided")
            msg = "Log path must be provided"
            raise ValueError(msg)
        if not Path(self.log_path).exists():
            logger.error("Log file not found at path: %s", self.log_path)
            msg = f"Log file not found: {self.log_path}"
            raise FileNotFoundError(msg)
            raise FileNotFoundError(msg)
        try:
            logger.info("Reading log file from: %s", self.log_path)
            with Path(self.log_path).open() as log_file:
                content = log_file.read()
                content = log_file.read()

                # Use findall to capture all matches at once
                matches = self.pattern.findall(content)
                for ip in matches:
                    banned_ips.add(ip)
                if not banned_ips:
                    logger.warning("No IP addresses found in the log file")
                else:
                    logger.info("Found %d unique banned IPs", len(banned_ips))
                    logger.debug("Found IPs: %s", banned_ips)
            if self.output_file and banned_ips:
                logger.info("Writing banned IPs to: %s", self.output_file)
                with Path(self.output_file).open("w") as out_file:
                    for ip in banned_ips:
                        out_file.write(f"{ip}\n")
                        out_file.write(f"{ip}\n")

        except PermissionError:
            logger.exception("Permission denied when reading log file")
            raise
        except UnicodeDecodeError as e:
            logger.exception("Error decoding log file: %s")
            msg = f"Could not decode log file: {e}"
            raise ValueError(msg)
        except Exception:
            logger.exception("Unexpected error reading log file")
            raise
        else:
            return banned_ips
