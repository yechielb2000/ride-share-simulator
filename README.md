# Ride-share-Simulator

A simulation system for ride-sharing services that demonstrates driver-to-ride matching strategies.

## Input Files

**Important**. When you provide JSON of rides, the ride **must have a future datetime** in its timestamp, for the
obvious reason that you cannot ask for a ride where the requested ride time was already passed. To make it easier for
the testing, I did not force it with the type `FutureDatetime` only for me to update its request ride time randomly
after the current time. It's ofcourse only to make the testing nicer. In the real world It will fail to get the request.

> Note: There are already input files, but if you want to set your own, don't skip this step
> Place your input files:

- Put `drivers.json` in `services/drivers_loader/`
- Put `rides.json` in `services/rides_producer/`

<details>
  <summary>drivers.json content format</summary>

```json
{
  "drivers": [
    {
      "id": "1",
      "name": "Alice",
      "vehicle_type": "private",
      "location": {
        "lat": 32.0853,
        "lon": 34.7818
      },
      "rating": 4.9
    },
    {
      ...
    }
  ]
}
```

</details>

<details>
  <summary>rides.json content format</summary>

```json
{
  "rides": [
    {
      "id": "1",
      "pickup": {
        "lat": 32.0830,
        "lon": 34.7805
      },
      "dropoff": {
        "lat": 37.1000,
        "lon": 36.7900
      },
      "vehicle_type": "private",
      "timestamp": "2025-09-03T15:00:00",
      "user_rating": 5
    },
    {
      ...
    }
  ]
}
```

</details>

# Setup & Installation

Build the base image for our services:

````shell
docker build -f Dockerfile.base -t ride-share-base:latest .
````

The base image sets global envs, copies the `shared` directory, installing essential binaries, and syncing project
packages using uv.

Now you can run the services:

```bash
docker compose up -d
```

You can watch the logs of each service to see the records and related logs for the service actions.

**Get a report:**

```bash
  curl http://localhost:8000/report
```

----

# Matching Strategies

The system supports two matching strategies configurable in : `config.yaml`

1. **Nearest Driver** (`strategy: "nearest"`)
    - Matches rides to drivers based on minimum straight-line distance to pickup location
    - Best for minimizing pickup times

2. **Weighted Score** () `strategy: "weighted"`
    - Considers user and drivers ratings
    - Matches higher-rated users with higher-rated drivers

# Architecture & Design

This project uses Docker Compose for local development and testing. The setup includes:

- Redis for in-memory data storage (configured to flush data on restart for testing purposes)
- Kafka for message queuing
- Multiple Python microservices handling different aspects of the simulation

> **⚠️ Development Note**:
> The current Redis configuration is optimized for development and testing, where we automatically flush data between
> restarts and disable persistence. In a production environment, you would want to enable data persistence and manage
> data lifecycle differently.

**Structure**

- `config.yaml` configurable file for the services, [file structure](shared/config/config.py).
- `Dockerfile.base` the base ride-share-simulator image for our services.
- `shared/` shares sources across all services.
    - `config/` the configuration schema, instance, and loader.
    - `kafka/` generic interfaces for kafka such as adjusted `kafka consumer` etc...
    - `logger/` setup for logger (I use loguru, great library).
    - `models/` all shared models such ass `Driver`, `Ride` etc...
    - `redis_sdk/` manages actions for us. holding drivers, assignment, metrics, etc...
    - `files.py` generic actions for files, specifics yielding models from JSON files.
- `services/` services sits here.
    - `dispatcher/` consumes rides and assigns them to drivers.
    - `drivers_loader/` load drivers to redis (once).
    - `metrics/` an API for providing reports.
    - `clock/` Provides a ticking mechanism to simulate time (used for freeing drivers when the estimated_travel_time >=
      clock_time). Note that the clock is set to UTC tz (if you add ride, it should come with UTC tz)
    - `rides_producer/` produce rides for the simulation.

The infra structure choices like the base image and shared directory seemed very legit since we don't want to compile
the same binaries and packages again and again. For the shared directory, in production I would probably make each
package there as an internal package.

### Redis SDK

The reason I didn't inherit the client, and instead I pass the controllers of each entity (rides, metrics, drivers,
clock) is because I think it's nicer to have one endpoint for the sdk instead of making an object for each controller.

### Reading from JSON

I used `ijson` to generate each ride object from the JSON, so I can yield them instead of loading all to memory, (same
for `drivers loader`).

### Metrics API

The report is provided via an API.

```http request
localhost:8000/report
```

### Kafka Adjusted Objects

For reducing code. I made generic consumer and producer on a given Generic type bounded by BaseModel.

### Dispatcher

**Matching strategies**
The matching strategies are pretty straightforward. You have an interface that shows how strategies should look.  
Each new strategy inherits this class, and a factory utility provides the wanted strategy given via the config file.
We provide the class from the factory, and then we execute the `.match` function to match rides
to drivers.

**Dispatcher Flow**

Consumes rides, check if there are available drivers for this ride, fileter available drivers by the vehicle type, match
by strategy, assign a ride.

# Things I could do next

Add rides and assignments to a DB. I didn't research what's best, but from the first view, postgres look good here
since our DTOs have relation, and we care about ACID; also, postgres have an extension for geo if we ever needed.  
I would also add drivers' table to store them there, and I would keep the available drivers in redis for fast response.
