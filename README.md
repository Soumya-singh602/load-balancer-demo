# Load Balancer Demo

A Python Flask-based Load Balancer that distributes HTTP requests
across multiple backend servers using different load balancing algorithms.

## Tech Stack

- Python
- Flask
- Requests
- Threading
- Apache JMeter
- Git & GitHub

## Load Balancing Algorithms

- Round Robin
- Weighted Round Robin
- Least Connections
- Weighted Least Connections
- IP Hash
- Random Selection

## Architecture

Client → Load Balancer → Backend Servers

- Load Balancer: `127.0.0.1:8000`
- Backend 1: `127.0.0.1:8001`
- Backend 2: `127.0.0.1:8002`
- Backend 3: `127.0.0.1:8003`

## Load Testing

Apache JMeter is used to test the load balancer under concurrent requests
and verify request distribution, response time, throughput, and errors.

## Key Features

- Multiple load balancing algorithms
- Concurrent request handling
- Weighted server support
- IP-based server persistence
- Load testing with Apache JMeter
- Request distribution monitoring through server logs

## Run

```bash
python load_balancer.py
http://127.0.0.1:8000

## Author

**Soumya Singh**  
