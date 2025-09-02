# Ride-share-Simulator


## installation Process
Make kafka cluster id 
```bash
powershell$ [guid]::NewGuid().ToString()
bash$ cat /proc/sys/kernel/random/uuid
```
Edit the `CLUSTER_ID` of kafka in `docker-compose.yaml`.  
Run docker compose:
```bash
docker compose up -d
```

## Base architecture approach
**Producer**:
  >Reads rides.json → Publishes to Kafka ride_requests
  Uses Redis sim_clock to simulate timestamps

**Dispatcher(s)**:
  >Consumes ride_requests from Kafka
  Checks `ride.timestamp <= sim_clock`
  Assigns drivers using strategy
  Updates driver state in Redis
  Publishes assignment to Kafka assignments

**Metrics Service**:
  >Consumes assignments
  Tracks assigned/unassigned rides + ETA
  Outputs report.json