from datetime import UTC, datetime
from pathlib import Path


class Fail2BanLogParser:
    """Parser for Fail2Ban log files to extract banned IP addresses."""

    def __init__(
        self,
        log_path: str = "/var/log/fail2ban.log",
        output_file: None | str = None,
    ) -> None:
        """Initialize the Fail2BanLogParser.

        Args:
            log_path (str): Path to the Fail2Ban log file.
            output_file (None | str): Optional path to the output file.

        """
        self.log_path = Path(log_path)
        self.output_filename = None if output_file is None else Path(output_file)
        self.today = datetime.now(UTC).strftime("%Y-%m-%d")
        self._ips: set[str] = set()

    def read_logs(self) -> set[str]:
        """Read the Fail2Ban log file and extract banned IP addresses for today.

        Returns:
            set[str]: A set of banned IP addresses found in today's log entries.

        Raises:
            FileNotFoundError: If the specified log file does not exist.

        """
        if not self.log_path.exists():
            msg = "File: %s does not exist", self.log_path.as_posix()
            raise FileNotFoundError(msg)
        self._ips.clear()  # To avoid overlapping of IPs the set is cleared before putting in the new IPs
        with Path(self.log_path).open("r") as file:
            for line in file:
                if "Ban " in line and self.today in line:
                    ip = line.strip().split()[-1]
                    self._ips.add(ip)
        return self._ips

    @property
    def ips(self) -> set[str]:
        """Get the set of banned IP addresses extracted from the log file."""
        return self._ips

    def export_results(self) -> None:
        """Export the set of banned IP addresses to the specified output file.

        Raises:
            Exception: If the output file path is not specified.

        """
        if self.output_filename is None:
            msg = "File: %s does not exist", self.log_path.as_posix()
            raise Exception(msg)
        with Path(self.output_filename).open("w") as file:
            for ip in sorted(self._ips):
                file.write(ip + "\n")
