

# Monitorización de Fail2ban

Una solución de monitorización para Fail2ban que ayuda a rastrear y analizar las IPs bloqueadas en toda su infraestructura.

![Ejemplo del panel](https://raw.githubusercontent.com/adrianvillanueva997/Fail2ban-monitoring/master/dashboard.png)

## Características

- Rastrea bloqueos de Fail2ban en varios servidores
- Almacena datos en PostgreSQL, SQLite o MariaDB/MySQL
- Visualiza datos de bloqueos y tendencias
- Identifica atacantes recurrentes

## Requisitos

- Python 3.8+
- Base de datos (PostgreSQL, SQLite o MariaDB/MySQL)
- Fail2ban instalado en los servidores que desea monitorizar

## Instalación

```bash
# Clona el repositorio
git clone https://github.com/yourusername/Fail2ban-monitoring.git
cd Fail2ban-monitoring

# Instala las dependencias
uv sync --extra (sqlite/mysql/postgres)
# Después de configurar las variables de entorno (consulta la tabla inferior), ejecuta el siguiente comando:
uv run src/fail2banmonitoring
```

## Variables de Entorno

La aplicación se puede configurar utilizando las siguientes variables de entorno:

| Variable | Descripción | Predeterminado | Obligatorio |
|----------|-------------|---------|----------|
| DRIVER | Controlador de base de datos (```sqlite+aiosqlite``` / ```mysql+aiomysql``` / ```postgresql+asyncpg```) |  | Sí |
| HOST | Dirección del host de la base de datos |  | Sí (para postgres/mariadb) |
| PORT| Puerto de la base de datos |  | Sí (para postgres/mariadb) |
| USERNAME| Nombre de usuario de la base de datos |  | Sí (para postgres/mariadb) |
| DB_PASSWORD | Contraseña de la base de datos | | Sí (para postgres/mariadb) |
| DATABASE | Nombre de la base de datos |  | Sí |
| CONFIG_PATH | Ruta al archivo de configuración | ```/var/log/fail2ban.log``` | No |

## Uso

Configure sus variables de entorno y ejecute el código

```bash
uv sync --extra sqlite
uv sync --extra postgres
uv sync --extra mysql
```

## Docker

Puede ejecutar Fail2ban Monitoring utilizando Docker con el backend de base de datos de su preferencia:

### SQLite (configuración más simple)

```bash
# Construye y ejecuta con SQLite
docker-compose -f docker-compose.sqlite.yml up -d
```

### PostgreSQL

```bash
# Construye y ejecuta con PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d
```

### MariaDB/MySQL

```bash
# Construye y ejecuta con MariaDB
docker-compose -f docker-compose.mariadb.yml up -d
```

## Desarrollo

```bash
# Instala las dependencias de desarrollo
uv sync

# Ejecuta las pruebas
uv run pytest tests/

# Ejecuta los linters
uv run ruff check src
uv run mypy src
uv run bandit src
```
