# Load Balancer Demo

A multi-threaded HTTP Load Balancer built with **Python** and **Flask** that distributes incoming client requests across multiple backend servers using different load-balancing algorithms.

---

## Tech Stack

* **Python 3.x**
* **Flask**
* **Requests**
* **Threading & Locks**
* **Apache JMeter**
* **Git & GitHub**

---

## Load Balancing Algorithms

This project implements six load-balancing strategies:

1. **Round Robin** — Distributes requests sequentially across backend servers.
2. **Weighted Round Robin** — Distributes more requests to servers with higher weights.
3. **Least Connections** — Routes requests to the server with the fewest active connections.
4. **Weighted Least Connections** — Considers both server weight and active connections.
5. **IP Hash** — Uses the client's IP address to consistently route requests to the same backend.
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

### Endpoints

* **Load Balancer:** `http://127.0.0.1:8000`
* **Backend Server 1:** `http://127.0.0.1:8001`
* **Backend Server 2:** `http://127.0.0.1:8002`
* **Backend Server 3:** `http://127.0.0.1:8003`

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
* Apache JMeter load testing

---

## Load Testing

**Apache JMeter** is used to test the Load Balancer under concurrent requests.

The tests help evaluate:

* Request distribution
* Response time
* Throughput
* Error percentage
* Concurrent request handling

Example test configuration:

```text
Threads:       50
Ramp-up:       5 seconds
Requests:      100
Target:        127.0.0.1:8000
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Soumya-singh602/load-balancer-demo.git
cd load-balancer-demo
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install flask requests
```

---

## Running the Project

Start the backend servers on ports:

```text
8001
8002
8003
```

Then start the Load Balancer:

```bash
python load_balancer.py
```

The Load Balancer will run at:

```text
http://127.0.0.1:8000
```

Send requests to the Load Balancer instead of directly accessing the backend servers.

---

## Monitoring

The Load Balancer prints request-routing information in the terminal.

Example:

```text
Request forwarded to http://127.0.0.1:8001
Request completed on http://127.0.0.1:8001
```

For algorithms such as **IP Hash**, **Weighted Least Connections**, and **Random Selection**, the logs also show the selected backend and relevant routing information.

---

## Project Structure

```text
load-balancer-demo/
│
├── load_balancer.py
├── README.md
└── venv/
```

---

## Author

**Soumya Singh**

