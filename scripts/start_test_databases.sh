#!/bin/bash
# Start MySQL and Postgres containers for local testing with CI-compatible credentials

echo "Starting MySQL (test:test@test) on 3306..."
docker run --rm -d \
  --name fail2ban-mysql-test \
  -e MYSQL_ROOT_PASSWORD=test \
  -e MYSQL_DATABASE=test \
  -e MYSQL_USER=test \
  -e MYSQL_PASSWORD=test \
  -p 3306:3306 \
  mysql:8.0

echo "Starting Postgres (test:test@test) on 5432..."
docker run --rm -d \
  --name fail2ban-postgres-test \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=test \
  -p 5432:5432 \
  postgres:15

echo "Containers started. Use 'docker ps' to check status."
echo "Run 'docker stop fail2ban-mysql-test fail2ban-postgres-test' to stop them."
