# Ride-share-Simulator

## installation Process

First build the base image for our services:

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

----

## Base Architecture Approach

**Drivers Loader**:
> Loads drivers to redis. Run once at the start.

**Rides Producer**:
> Reads rides.json and Publishes to Kafka under `ride_requests` topic.  
> Uses Redis `sim_clock` to simulate timestamps

**Dispatcher(s)**:
> Consumes ride_requests from Kafka
> Checks `ride.timestamp <= sim_clock`
> Updates driver state in Redis
> Assigns drivers using strategy
> Publishes assignment to Redis assignments

**Metrics Service**:
> Provides HTTP endpoint to get the report and metrics

## Detailed Structure

**Structure**

- `Config.yaml` configurable file for the services, [file structure](shared/config/config.py).
- `Shared` shares sources across all services.
    - `Config` the configuration schema, instance and loader.
    - `Kafka` generic interfaces for kafka such as adjusted `kafka consumer` etc...
    - `Logger` setup for logger (I use loguru, great library).
    - `Models` all shared models such ass `Driver`, `Ride` etc...
    - `redis_sdk` manages actions for us. holding drivers, assignment, metrics, etc...
    - `Files` generic actions for files, specifics yielding models from JSON files.
    - `GEO` geo utils such as measure distance and estimated arrival time.
- `Services` services sits here.
    - `Dispatcher` consumes rides and assigns them to drivers.
    - `Drivers_loader` load drivers to redis (once).
    - `Metrics` an API for providing reports.
    - `Rides_producer` produce rides for the simulation.

### Design Choices

#### infra structure

The infra structure choices like the base image and shared directory seemed very legit since we don't want to compile
the same binaries and packages again and again. For the shared directory, in production I would probably make each
package there as an internal package.

#### Reading from JSON

I really wanted to generate rides without using the JSON file, but it was required by the assignment.
I used `ijson` to generate each ride object from the JSON, so I can yield them instead of loading all to memory, (same
for `drivers loader`).

#### Metrics API

I thought it would be much nicer to get the report from an api endpoint instead of getting it from the docker
containers.  
So even though you requested to output the JSON file of the report to the filesystem, I hope you could forgive me for
providing it to use differently :)

#### Kafka Adjusted Objects

Just for reducing code. Pass `BaseModel` bounded generic type for the model_class, and it will consume/produce the
model.

#### Clock

I was thinking about 2 ways:

1. Marking drivers busy / free via a custom clock that holds time which ticks from ride timestamp to another (The clock
   is not really ticking by "worldwide time"), usage is in the dispatcher since I used this one.
2. Marking drivers as busy in Redis with a TTL (with estimation of completion time). When the TTL expires, a background
   service listens to Redis keyspace notifications and automatically marks the driver as free,

Both are adding them back to the available pool.

#### Dispatcher

**Matching strategies**
The matching strategies is pretty simple. You have an interface that shows how each Strategy should look.  
Each new strategy inherits this class and a factory utility helps us choose from StrategyType the right Strategy.
We provide the class from the factory, and it gets its kwargs, and then we execute the `.match` function to match rides
to drivers.

**Dispatcher Flow**
The flow of the service is very important because it's the heart of the system.  
Let's begin.  
For each consumed ride we want to check if the ride request time (ride.timestamp) is grater than the current clock we
update the clock to be as ride timestamp. After that we free drivers that already passed the clock time. (the flow uses
the first clock method since this is what we are using).  
Then we assign a driver to the ride by the chosen strategy (pulling the right strategy using the factory).  
Then we publish assignment to redis assignments. If no driver is assigned we add the ride id to the unassigned rides.

**Redis SDK**
No need to say why I made it, it's pretty clear. I just want to declare that the reason I didn't inherited the client,
and instead I pass the controllers of each entity (rides, metrics, drivers, clock) is because I think it's nicer to have
one endpoint for the sdk instead of making an object for each controller.

## Things I would do next

Add rides and assignments to a DB. I didn't research what's best but from the first view, postgres looks good here since
our DTOs have relation, and we care about ACID; also postgres have an extension for geo if we ever needed.  
I would also add drivers' table to store them there, and I would keep the available drivers in redis for fast response.  

