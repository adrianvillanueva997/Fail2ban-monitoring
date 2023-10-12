FROM rust:1.73.0-bookworm AS builder
WORKDIR /build
COPY . .
RUN cargo build --release

# Path: Dockerfile
FROM debian:bookworn-slim
COPY --from=builder /build/target/release/fail2banmonitoring /usr/local/bin/fail2banmonitoring
