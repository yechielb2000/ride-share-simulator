echo "building base dockerfile"
docker build -f Dockerfile.base -t ride-share-base:latest .
echo "loading services"
docker compose up -d