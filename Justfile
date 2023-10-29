set dotenv-load
set export
DOCKER_IMAGE_NAME := "fail2ban-monitoring-rs"


test:
    @echo "Running tests"
    cargo nextest run

build:
    @echo "Building the app"
    cargo build --release

audit:
    @echo "Auditing the app"
    cargo audit

clippy:
    @echo "Linting the app"
    cargo clippy --all-targets --all-features -- -D warnings

clean:
    @echo "Cleaning the app"
    cargo clean

hadolint:
    @echo "Linting the dockerfile"
    hadolint Dockerfile

docker-build:
    @echo "Building the docker image"
    docker build -t $(DOCKER_IMAGE_NAME) .

sqlite-run:
    @echo "Running the sqlite database"
    rm sqlite.db
    cargo run
