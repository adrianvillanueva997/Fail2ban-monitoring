import re
from pathlib import Path


class Fail2BanLogParser:
    """Parse fail2ban logs and extract IP addresses."""

    def __init__(self, log_path: str | None, output_file: str | None) -> None:
        """Initialize the Fail2BanLogParser with log and output file paths.

        Args:
            log_path: Path to the fail2ban log file.
            output_file: Path to the output file where banned IPs will be written.

        """
        self.log_path = log_path
        self.output_file = output_file
        self.pattern = re.compile(r"Ban (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")

    def read_logs(self) -> set[str]:
        """Read logs from the specified file path and extract banned IP addresses.

        Returns:
            Set of banned IP addresses.

        """
        banned_ips = set()
        if not self.log_path:
            return banned_ips
        if not Path(self.log_path).exists():
            return banned_ips
        try:
            with Path(self.log_path).open() as log_file:
                content = log_file.read()
                matches = self.pattern.findall(content)
                for ip in matches:
                    banned_ips.add(ip)
                if not banned_ips:
                    pass

            if self.output_file and banned_ips:
                with Path(self.output_file).open("w") as out_file:
                    for ip in banned_ips:
                        out_file.write(f"{ip}\n")
        except Exception as e:
            return banned_ips
        else:
            return banned_ips
