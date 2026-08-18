# Load Balancer Demo

A multi-threaded HTTP Load Balancer built with **Python** and **Flask** that distributes incoming client requests across multiple backend servers using multiple load-balancing algorithms.

The project also implements **PostgreSQL Primary-Replica (Master-Slave) replication**, **read/write database routing**, REST APIs, and **Apache JMeter** load and performance testing.

---

## Tech Stack

* Python 3.x
* Flask
* PostgreSQL
* psycopg2
* python-dotenv
* Requests
* Threading & Locks
* Apache JMeter
* Git & GitHub

---

## Project Features

* Multiple load-balancing algorithms
* Multi-threaded request handling
* Thread-safe connection tracking
* Weighted backend support
* IP-based request persistence
* Random server selection
* Backend request forwarding
* Backend failure handling
* HTTP 503 response when a backend server is unavailable
* Health check API
* Server status API
* User CRUD APIs
* Search and count APIs
* Primary-Replica database architecture
* Read/Write database separation
* PostgreSQL streaming replication
* Database consistency verification
* Apache JMeter load and performance testing
* 300-user concurrent load testing

---

# Load Balancing Algorithms

This project implements six load-balancing strategies:

1. **Round Robin** — Distributes requests sequentially across backend servers.
2. **Weighted Round Robin** — Distributes requests according to server weights.
3. **Least Connections** — Routes requests to the server with the fewest active connections.
4. **Weighted Least Connections** — Considers both server weight and active connections.
5. **IP Hash** — Uses the client's IP address to consistently route requests to the same backend server.
6. **Random Selection** — Randomly selects a backend server for each request.

Only one load-balancing algorithm is run on port `8000` at a time during comparison testing.

---

# Complete Architecture

```text
                         ┌─────────────────┐
                         │     Client      │
                         │ Postman/JMeter  │
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
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Database       │
                         │     Router      │
                         └────────┬────────┘
                                  │
                       ┌──────────┴──────────┐
                       │                     │
                    WRITE                  READ
                       │                     │
                       ▼                     ▼
                ┌─────────────┐      ┌─────────────┐
                │   PRIMARY   │      │   REPLICA   │
                │   :5432     │─────►│   :5434     │
                │ PostgreSQL  │ WAL  │ PostgreSQL  │
                └─────────────┘      └─────────────┘
```

---

# Ports

| Component          | Port |
| ------------------ | ---: |
| Load Balancer      | 8000 |
| Backend Server 1   | 8001 |
| Backend Server 2   | 8002 |
| Backend Server 3   | 8003 |
| PostgreSQL Primary | 5432 |
| PostgreSQL Replica | 5434 |

All client requests enter through **port 8000**.

The backend servers run on ports `8001`, `8002`, and `8003`.

The PostgreSQL Primary database runs on `5432`, while the Replica database runs on `5434`.

---

# Database Architecture

The project uses a **Primary-Replica database architecture**.

## Primary Database

```text
PostgreSQL Primary
Port: 5432
```

The Primary database handles all write operations:

```text
POST
PUT
DELETE
```

## Replica Database

```text
PostgreSQL Replica
Port: 5434
```

The Replica database handles read operations:

```text
GET
```

---

# Read/Write Database Routing

The database router determines which database connection should be used based on the HTTP method.

```text
GET
 ↓
Replica :5434
```

```text
POST
PUT
DELETE
 ↓
Primary :5432
```

The routing logic is implemented through:

```text
database/router.py
```

Primary connection:

```text
database/primary.py
```

Replica connection:

```text
database/replica.py
```

---

# Database Consistency

PostgreSQL streaming replication is used to synchronize data between the Primary and Replica databases.

The flow is:

```text
Write Request
     │
     ▼
Primary :5432
     │
     ▼
PostgreSQL WAL
     │
     ▼
Streaming Replication
     │
     ▼
Replica :5434
```

**WAL** stands for **Write-Ahead Log**.

PostgreSQL records database changes in WAL records. During streaming replication, these changes are transferred from the Primary to the Replica and replayed on the Replica.

This allows the Replica to maintain a synchronized copy of the Primary database.

---

# Primary and Replica Verification

The Primary database can be verified using:

```bash
sudo -u postgres psql -p 5432 -c "SELECT pg_is_in_recovery();"
```

Expected result:

```text
f
```

`f` means the server is not in recovery and is acting as the Primary.

The Replica can be verified using:

```bash
sudo -u postgres psql -p 5434 -c "SELECT pg_is_in_recovery();"
```

Expected result:

```text
t
```

`t` indicates that the server is operating as a Replica/Standby.

---

# Database Consistency Test

Data consistency can be checked by comparing the Primary and Replica databases.

Primary:

```bash
sudo -u postgres psql -p 5432 -d loadbalancer_db
```

```sql
SELECT * FROM users ORDER BY id DESC;
```

Replica:

```bash
sudo -u postgres psql -p 5434 -d loadbalancer_db
```

```sql
SELECT * FROM users ORDER BY id DESC;
```

The same replicated records should be available on both databases.

For example:

```text
Primary :5432

id | name  | email
---+-------+-------------------
4  | Rahul | rahul@example.com
```

```text
Replica :5434

id | name  | email
---+-------+-------------------
4  | Rahul | rahul@example.com
```

This verifies that the data has been replicated from the Primary to the Replica.

---

# REST APIs

The project provides **10 API endpoints**.

| Method | Endpoint        | Database    |
| ------ | --------------- | ----------- |
| GET    | `/health`       | Application |
| GET    | `/status`       | Application |
| GET    | `/`             | Backend     |
| GET    | `/users`        | Replica     |
| POST   | `/users`        | Primary     |
| GET    | `/users/search` | Replica     |
| GET    | `/users/count`  | Replica     |
| GET    | `/users/<id>`   | Replica     |
| PUT    | `/users/<id>`   | Primary     |
| DELETE | `/users/<id>`   | Primary     |

---

# API Details

## Health Check

```http
GET /health
```

Example:

```text
http://127.0.0.1:8000/health
```

Response:

```json
{
    "status": "healthy",
    "server": "Server-8001",
    "port": 8001
}
```

---

## Server Status

```http
GET /status
```

Returns the backend server and active connection count.

Example:

```json
{
    "server": "Server-8001",
    "port": 8001,
    "active_connections": 0
}
```

---

## Get All Users

```http
GET /users
```

Read operation.

```text
GET
 ↓
Replica :5434
```

---

## Create User

```http
POST /users
```

Example request:

```json
{
    "name": "Soumya",
    "email": "soumya@example.com"
}
```

Write operation:

```text
POST
 ↓
Primary :5432
```

---

## Get Single User

```http
GET /users/<id>
```

Example:

```text
GET /users/4
```

Read operation:

```text
Replica :5434
```

---

## Search Users

```http
GET /users/search?q=Rahul
```

Read operation:

```text
Replica :5434
```

---

## Count Users

```http
GET /users/count
```

Read operation:

```text
Replica :5434
```

---

## Update User

```http
PUT /users/<id>
```

Example:

```json
{
    "name": "Updated Name"
}
```

Write operation:

```text
Primary :5432
```

---

## Delete User

```http
DELETE /users/<id>
```

Write operation:

```text
Primary :5432
```

---

# Request Flow

Client requests are always sent to the Load Balancer:

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

The Load Balancer determines which backend should handle each request.

---

# Project Structure

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
├── database/
│   ├── __init__.py
│   ├── primary.py
│   ├── replica.py
│   ├── router.py
│   └── crud.py
│
├── requirements.txt
├── README.md
├── .gitignore
├── .env
└── venv/
```

> `.env`, `venv/`, Python cache files, log files, and other generated files should not be committed to GitHub.

---

# Environment Variables

Database credentials are stored in environment variables instead of being hard-coded.

Example configuration:

```text
PRIMARY_DB_HOST
PRIMARY_DB_PORT
PRIMARY_DB_NAME
PRIMARY_DB_USER
PRIMARY_DB_PASSWORD

REPLICA_DB_HOST
REPLICA_DB_PORT
REPLICA_DB_NAME
REPLICA_DB_USER
REPLICA_DB_PASSWORD
```

The `.env` file should remain private.

---

# Installation

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

# Running Backend Servers

The project uses three backend servers.

Start Backend Server 1:

```bash
python backend_server.py 8001
```

Start Backend Server 2:

```bash
python backend_server.py 8002
```

Start Backend Server 3:

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

# Running Load Balancing Algorithms

Only one algorithm is run on port `8000` at a time.

## Round Robin

```bash
python round_robin.py
```

## Weighted Round Robin

```bash
python weighted_round_robin.py
```

## Least Connections

```bash
python least_connections.py
```

## Weighted Least Connections

```bash
python weighted_least_connections.py
```

## IP Hash

```bash
python ip_hash.py
```

## Random Selection

```bash
python random_selection.py
```

The selected Load Balancer runs at:

```text
http://127.0.0.1:8000
```

---

# Monitoring Load Distribution

Each load-balancing algorithm prints routing information in the terminal.

Example:

```text
Round Robin | Forwarded to: http://127.0.0.1:8001
Round Robin | Forwarded to: http://127.0.0.1:8002
Round Robin | Forwarded to: http://127.0.0.1:8003
```

For Random Selection:

```text
Random Selection | Forwarded to: http://127.0.0.1:8002
Random Selection | Forwarded to: http://127.0.0.1:8003
Random Selection | Forwarded to: http://127.0.0.1:8001
```

---

# IP Hash Example

```text
IP Hash
| Client IP: 127.0.0.1
| Hash: <SHA-256 hash>
| Server Index: 0
| Forwarded to: http://127.0.0.1:8001
```

The same client IP produces the same hash and therefore maps to the same backend server as long as the backend server list remains unchanged.

---

# Backend Failure Handling

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

# Testing with Postman

Postman can be used for functional API testing.

Example:

```text
GET http://127.0.0.1:8000/users
```

The response identifies the backend server and database being used.

Example:

```json
{
    "server": "Server-8001",
    "database": "replica",
    "users": [...]
}
```

For a write operation:

```text
POST http://127.0.0.1:8000/users
```

The response identifies the Primary database:

```json
{
    "server": "Server-8002",
    "database": "primary",
    "user": {...}
}
```

This demonstrates the application's read/write database routing.

---

# Database Consistency Testing

A complete consistency test follows this flow:

```text
POST /users
      │
      ▼
Primary :5432
      │
      ▼
PostgreSQL WAL
      │
      ▼
Replica :5434
      │
      ▼
GET /users
```

Example:

1. Create a user using `POST /users`.
2. Verify that the write is handled by the Primary.
3. PostgreSQL replicates the change to the Replica.
4. Execute `GET /users`.
5. Verify that the newly created user is available from the Replica.
6. Compare the data directly in both PostgreSQL instances.

This demonstrates Primary-Replica data consistency.

---

# Load Testing with Apache JMeter

**Apache JMeter** is used to test the Load Balancer with concurrent requests.

JMeter sends requests to:

```text
http://127.0.0.1:8000
```

The same JMeter configuration can be used for different load-balancing algorithms.

Only the Python Load Balancer script running on port `8000` needs to be changed.

---

# Example JMeter Test Configuration

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

Then run the JMeter test.

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

# Concurrent Load Testing

The project can also be tested with higher concurrent loads, including a **300-user JMeter test**.

Example flow:

```text
300 Concurrent Users
        │
        ▼
      JMeter
        │
        ▼
Load Balancer :8000
        │
   ┌────┼────┐
   ▼    ▼    ▼
 8001  8002  8003
```

The backend terminals can be monitored to observe how requests are distributed.

---

# Performance Metrics

JMeter is used to evaluate:

* Total requests
* Response time
* Minimum response time
* Maximum response time
* Average response time
* Throughput
* Error percentage
* Concurrent request handling

The Load Balancer terminal logs are also used to observe request distribution.

---

# Testing Approach

The project uses multiple levels of testing.

## 1. Functional Testing

Each Load Balancing algorithm is executed independently and tested using HTTP requests.

The terminal logs are checked to verify that requests are routed according to the selected algorithm.

## 2. API Testing

Postman is used to test:

* Health API
* Status API
* User creation
* User retrieval
* User search
* User count
* User update
* User deletion

## 3. Database Testing

Primary and Replica PostgreSQL instances are checked directly to verify:

* Primary role
* Replica role
* Data replication
* Data consistency

## 4. Load Testing

Apache JMeter generates concurrent requests against the Load Balancer.

This evaluates the behavior and performance of the different algorithms under load.

```text
Functional Testing
        │
        ▼
Algorithm Verification
        │
        ▼
API Testing
        │
        ▼
Database Consistency Testing
        │
        ▼
JMeter Load Testing
        │
        ▼
Performance Evaluation
```

---

# Requirements

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
Flask
requests
psycopg2-binary
python-dotenv
```

---

# Git and GitHub

Repository:

https://github.com/Soumya-singh602/load-balancer-demo

Before pushing code, make sure sensitive files such as `.env` are excluded using `.gitignore`.

Example:

```text
.env
venv/
__pycache__/
*.pyc
*.log
```

---

# Author

**Soumya Singh**

