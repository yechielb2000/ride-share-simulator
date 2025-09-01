# Ride-share-Simulator



## Base architecture approach
**Producer**:
  >Reads rides.json → Publishes to Kafka ride_requests
  Uses Redis sim_clock to simulate timestamps

**Dispatcher(s)**:
  >Consumes ride_requests from Kafka
  Checks ride.timestamp <= sim_clock
  Assigns drivers using strategy
  Updates driver state in Redis
  Publishes assignment to Kafka assignments

**Metrics Service**:
  >Consumes assignments
  Tracks assigned/unassigned rides + ETA
  Outputs report.json