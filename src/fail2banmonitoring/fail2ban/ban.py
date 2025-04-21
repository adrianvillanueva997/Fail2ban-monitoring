from datetime import UTC, datetime
from pathlib import Path


class Fail2BanLogParser:
    def __init__(
        self,
        log_path: str = "/var/log/fail2ban.log",
        output_file: None | str = None,
    ) -> None:
        self.log_path = Path(log_path)
        self.output_filename = None if output_file is None else Path(output_file)
        self.today = datetime.now(UTC).strftime("%Y-%m-%d")

    def read_logs(self) -> set[str]:
        if not self.log_path.exists():
            msg = "File: %s does not exist", self.log_path.as_posix()
            raise FileNotFoundError(msg)
        ips: set[str] = set()
        with Path(self.log_path).open() as file:
            for line in file:
                if "Ban " in line and self.today in line:
                    ip = line.strip().split()[-1]
                    ips.add(ip)
        return ips

    # def export_results(self) -> None:
    #     if self.output_filename is None:
    #         msg = "Output filename has not been defined"
    #         raise Exception(msg)
    #     with Path(self.log_path)
