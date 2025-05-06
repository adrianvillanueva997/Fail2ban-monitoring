# Fail2ban Monitoring

A monitoring solution for Fail2ban that helps track and analyze blocked IPs across your infrastructure.

![Dashboard example](https://raw.githubusercontent.com/adrianvillanueva997/Fail2ban-monitoring/master/dashboard.png)

## Features

- Track Fail2ban blocks across multiple servers
- Store data in PostgreSQL, SQLite, or MariaDB/MySQL
- Visualize block data and trends
- Identify recurring attackers

## Requirements

- Python 3.8+
- Database (PostgreSQL, SQLite, or MariaDB/MySQL)
- Fail2ban installed on servers you want to monitor

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Fail2ban-monitoring.git
cd Fail2ban-monitoring

# Install dependencies
uv sync --extra (sqlite/mysql/postgres)
```

## Environment Variables

The application can be configured using the following environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DRIVER | Database driver (```sqlite+aiosqlite``` / ```mysql+aiomysql``` / ```postgresql+asyncpg```) |  | Yes |
| HOST | Database host address |  | Yes (for postgres/mariadb) |
| PORT| Database port |  | Yes (for postgres/mariadb) |
| USERNAME| Database username |  | Yes (for postgres/mariadb) |
| DB_PASSWORD | Database password | | Yes (for postgres/mariadb) |
| DATABASE | Database name |  | Yes |
| CONFIG_PATH | Path to configuration file | ```/var/log/fail2ban.log``` | No |

## Usage

Setup your environment variables and run the code

```bash
uv sync --extra sqlite
uv sync --extra postgres
uv sync --extra mysql
```

## Docker

You can run Fail2ban Monitoring using Docker with your preferred database backend:

### SQLite (simplest setup)

```bash
# Build and run with SQLite
docker-compose -f docker-compose.sqlite.yml up -d
```

### PostgreSQL

```bash
# Build and run with PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d
```

### MariaDB/MySQL

```bash
# Build and run with MariaDB
docker-compose -f docker-compose.mariadb.yml up -d
```

## Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest tests/

# Run linters
uv run ruff check src
uv run mypy src
uv run bandit src
```
