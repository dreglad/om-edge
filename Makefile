
run:
	docker-compose up -d

restart:
	docker-compose restart nginx

logs:
	docker-compose logs --tail 100 -f nginx
