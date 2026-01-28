up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose run --rm web pytest

clean:
	docker compose down -v
	rm -rf data/*.db