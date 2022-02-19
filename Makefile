production:
	poetry install --no-dev
dev:
	poetry install
black: 
	poetry run black src
pylama:
	poetry run pylama src
script:
	poetry run python ./src/script.py
shell:
	 cd src && sudo ./fail2ban_output.sh

lint: black pylama
run: script shell 