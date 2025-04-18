mkdir -p caddy/caddy_config caddy/caddy_data
docker-compose down
docker-compose build
docker-compose up -d