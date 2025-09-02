# Ride-share-Simulator


## installation Process
First build the base image for our services:
````shell
docker build -f Dockerfile.base -t ride-share-base:latest .
````
It should take less than a minute...  
Now you can run the services:
```bash
docker compose up -d
```



## Base Architecture Approach
**Producer**:
  >Reads rides.json and Publishes to Kafka under `ride_requests` topic.  
  Uses Redis `sim_clock` to simulate timestamps

**Dispatcher(s)**:
  >Consumes ride_requests from Kafka
  Checks `ride.timestamp <= sim_clock`
  Assigns drivers using strategy
  Updates driver state in Redis
  Publishes assignment to Redis assignments

**Metrics Service**:
  >Provides HTTP endpoint to get the report and metrics.