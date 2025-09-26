.PHONY: install migrate runserver tailwind-install tailwind-build

# Install uv
install:
	curl -LsSf https://astral.sh/uv/install.sh | sh

# Run database migrations
migrate:
	python manage.py migrate

# Start the Django server
runserver:
	python manage.py runserver

# Install Node.js packages for Tailwind
tailwind-install:
	npm install

# Run Tailwind build watcher
tailwind-build:
	npm run twbuild