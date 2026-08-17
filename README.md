# Load Balancer Demo

A multi-threaded HTTP Load Balancer built with **Python** and **Flask** that distributes incoming client requests across multiple backend servers using multiple load-balancing algorithms.

The project also uses **Apache JMeter** for concurrent load and performance testing.

---

## Tech Stack

* Python 3.x
* Flask
* Requests
* Threading & Locks
* Apache JMeter
* Git & GitHub

---

## Load Balancing Algorithms

This project implements six load-balancing strategies:

1. **Round Robin** — Distributes requests sequentially across backend servers.
2. **Weighted Round Robin** — Distributes requests according to server weights.
3. **Least Connections** — Routes requests to the server with the fewest active connections.
4. **Weighted Least Connections** — Considers both server weight and active connections.
5. **IP Hash** — Uses the client's IP address to consistently route requests to the same backend server.
6. **Random Selection** — Randomly selects a backend server for each request.

---

## Architecture

```text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Load Balancer   │
                         │   Port: 8000    │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │ Backend  │  │ Backend  │  │ Backend  │
              │   8001   │  │   8002   │  │   8003   │
              └──────────┘  └──────────┘  └──────────┘
```

---

## Ports

| Component        | Port |
| ---------------- | ---: |
| Load Balancer    | 8000 |
| Backend Server 1 | 8001 |
| Backend Server 2 | 8002 |
| Backend Server 3 | 8003 |

All load-balancing algorithms use **port 8000** as the client-facing entry point.

Only one load-balancing algorithm is run on port 8000 at a time during comparison testing.

---

## Key Features

* Multiple load-balancing algorithms
* Multi-threaded request handling
* Thread-safe connection tracking
* Weighted backend support
* IP-based request persistence
* Random server selection
* Backend request forwarding
* Request distribution logging
* Backend failure handling
* HTTP 503 response when a backend server is unavailable
* Apache JMeter load and performance testing

---

## Project Structure

```text
load-balancer-demo/
│
├── backend_server.py
│
├── round_robin.py
├── weighted_round_robin.py
├── least_connections.py
├── weighted_least_connections.py
├── ip_hash.py
├── random_selection.py
│
├── requirements.txt
├── README.md
├── .gitignore
│
└── venv/
```

> `venv/`, log files, Python cache files, and other generated files should not be committed to GitHub.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Soumya-singh602/load-balancer-demo.git
cd load-balancer-demo
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running Backend Servers

The project uses three backend servers.

Start Backend Server 1:

```bash
python backend_server.py 8001
```

Start Backend Server 2 in another terminal:

```bash
python backend_server.py 8002
```

Start Backend Server 3 in another terminal:

```bash
python backend_server.py 8003
```

The backend servers will be available at:

```text
http://127.0.0.1:8001
http://127.0.0.1:8002
http://127.0.0.1:8003
```

---

## Running Load Balancing Algorithms

Only one algorithm is run on port **8000** at a time.

### Round Robin

```bash
python round_robin.py
```

### Weighted Round Robin

```bash
python weighted_round_robin.py
```

### Least Connections

```bash
python least_connections.py
```

### Weighted Least Connections

```bash
python weighted_least_connections.py
```

### IP Hash

```bash
python ip_hash.py
```

### Random Selection

```bash
python random_selection.py
```

The selected load balancer will run at:

```text
http://127.0.0.1:8000
```

---

## Request Flow

Client requests are sent to the Load Balancer:

```text
Client
   │
   ▼
127.0.0.1:8000
   │
   ▼
Load Balancing Algorithm
   │
   ├──────► 127.0.0.1:8001
   │
   ├──────► 127.0.0.1:8002
   │
   └──────► 127.0.0.1:8003
```

The client does not directly select the backend server.

The load balancer determines which backend should handle each request.

---

## Monitoring

Each load-balancing algorithm prints routing information in the terminal.

Example:

```text
Round Robin | Forwarded to: http://127.0.0.1:8001
Round Robin | Forwarded to: http://127.0.0.1:8002
Round Robin | Forwarded to: http://127.0.0.1:8003
```

### IP Hash Example

```text
IP Hash
| Client IP: 127.0.0.1
| Hash: <SHA-256 hash>
| Server Index: 0
| Forwarded to: http://127.0.0.1:8001
```

The same client IP produces the same hash and therefore maps to the same backend server, as long as the backend server list remains unchanged.

---

## Backend Failure Handling

If the selected backend server is unavailable, the Load Balancer returns:

```text
HTTP 503 SERVICE UNAVAILABLE
```

Example:

```json
{
    "error": "Backend server unavailable"
}
```

This behavior can also be observed during load testing when one of the backend servers is stopped.

---

## Load Testing with Apache JMeter

**Apache JMeter** is used to test the Load Balancer with concurrent requests.

JMeter sends requests to:

```text
http://127.0.0.1:8000
```

The same JMeter configuration can be used for different load-balancing algorithms.

Only the Python load-balancer script running on port `8000` needs to be changed.

### Example Test Configuration

```text
Threads:       50
Ramp-up:       5 seconds
Loop Count:    1
Target:        127.0.0.1:8000
Method:        GET
Path:          /
```

For example, to test Round Robin:

```bash
python round_robin.py
```

Run the JMeter test.

Stop the algorithm:

```text
Ctrl + C
```

Then test another algorithm:

```bash
python weighted_round_robin.py
```

The JMeter target remains:

```text
127.0.0.1:8000
```

---

## Performance Metrics

JMeter is used to evaluate:

* Total requests
* Response time
* Minimum response time
* Maximum response time
* Average response time
* Throughput
* Error percentage
* Concurrent request handling

The terminal logs are also used to observe how requests are distributed across backend servers.

---

## Testing Approach

The project uses two types of testing.

### 1. Functional / Script Testing

Each load-balancing algorithm is executed independently and tested by sending HTTP requests to port `8000`.

The terminal logs are checked to verify that requests are routed according to the selected algorithm.

### 2. Load / Performance Testing

Apache JMeter generates multiple concurrent requests against the Load Balancer.

This helps evaluate the behavior and performance of each algorithm under load.

```text
Functional Testing
        │
        ▼
Verify Algorithm Logic
        │
        ▼
JMeter Load Testing
        │
        ▼
Evaluate Performance
```

---

## Requirements

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
Flask
requests
```

---

## GitHub

Repository:

https://github.com/Soumya-singh602/load-balancer-demo

---

## Author

**Soumya Singh**
