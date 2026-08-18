# ⚡ Load Balancer Demo

A **Python + Flask distributed backend system** that demonstrates multiple load-balancing algorithms, PostgreSQL Primary-Replica replication, read/write database routing, failure handling, and concurrent performance testing.

The project is designed to demonstrate how a backend system can distribute traffic across multiple servers while maintaining database consistency.

---

## 🚀 Key Features

* 6 Load Balancing Algorithms
* Multi-threaded Flask Backend Servers
* Round Robin
* Weighted Round Robin
* Least Connections
* Weighted Least Connections
* IP Hash
* Random Selection
* PostgreSQL Primary-Replica Replication
* Read/Write Database Routing
* RESTful User APIs
* Health & Status Monitoring
* Backend Failure Handling
* Database Consistency Verification
* WAL / LSN Replication Verification
* Apache JMeter Load Testing
* 300 Concurrent User Testing

---

## 🏗️ Architecture

```text
                    Client
                Postman / JMeter
                       │
                       ▼
              ┌─────────────────┐
              │  Load Balancer  │
              │     :8000       │
              └────────┬────────┘
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
           :8001     :8002     :8003
          Backend   Backend   Backend
             └─────────┼─────────┘
                       ▼
              ┌─────────────────┐
              │ Database Router │
              └────────┬────────┘
                       │
                ┌──────┴──────┐
                ▼             ▼
             WRITE           READ
                │             │
                ▼             ▼
             Primary        Replica
              :5432          :5434
                │             ▲
                └──── WAL ────┘
```

### Request Flow

```text
POST / PUT / DELETE
        ↓
Primary :5432
        ↓
   PostgreSQL WAL
        ↓
Replica :5434
```

```text
GET
 ↓
Replica :5434
```

---

## ⚖️ Load Balancing Algorithms

| Algorithm                  | Strategy                               |
| -------------------------- | -------------------------------------- |
| Round Robin                | Sequential distribution                |
| Weighted Round Robin       | Distribution based on server weights   |
| Least Connections          | Server with minimum active connections |
| Weighted Least Connections | Weight + active connections            |
| IP Hash                    | Consistent routing based on client IP  |
| Random Selection           | Random backend selection               |

Only one algorithm runs on **port 8000** at a time for comparison testing.

---

## 🗄️ Database Architecture

The project uses **PostgreSQL streaming replication**.

```text
Primary :5432
     │
     │ WAL
     ▼
Replica :5434
```

### Database Routing

```text
GET              → Replica
POST             → Primary
PUT              → Primary
DELETE           → Primary
```

Implemented through:

```text
database/
├── primary.py
├── replica.py
├── router.py
└── crud.py
```

---

## 🔄 Data Consistency

Replication consistency is verified by comparing Primary and Replica data.

```sql
SELECT * FROM users ORDER BY id;
```

The project also verifies PostgreSQL replication state:

```sql
SELECT pg_is_in_recovery();
```

Expected:

```text
Primary  → f
Replica  → t
```

WAL synchronization can be checked using:

```sql
-- Primary
SELECT pg_current_wal_lsn();

-- Replica
SELECT pg_last_wal_replay_lsn();
```

Matching LSN positions indicate that the Replica has replayed WAL up to the same position.

---

## 🔌 REST API

| Method | Endpoint           | Route                         |
| ------ | ------------------ | ----------------------------- |
| GET    | `/health`          | Health of backend + databases |
| GET    | `/status`          | Active connections            |
| GET    | `/users`           | Replica                       |
| POST   | `/users`           | Primary                       |
| GET    | `/users/search?q=` | Replica                       |
| GET    | `/users/count`     | Replica                       |
| GET    | `/users/<id>`      | Replica                       |
| PUT    | `/users/<id>`      | Primary                       |
| DELETE | `/users/<id>`      | Primary                       |

Example:

```http
POST http://127.0.0.1:8000/users
```

```json
{
  "name": "Soumya",
  "email": "soumya@example.com"
}
```

---

## 🖥️ Backend Servers

A single `backend_server.py` runs multiple instances:

```bash
python backend_server.py 8001
python backend_server.py 8002
python backend_server.py 8003
```

The same backend application provides the APIs for all three servers.

---

## 🧪 Testing

### API Testing

**Postman** is used for:

* CRUD testing
* Health checks
* Search
* Count
* Read/Write routing verification

### Load Testing

**Apache JMeter** is used for concurrent testing.

Example:

```text
300 Concurrent Users
        ↓
JMeter
        ↓
Load Balancer :8000
        ↓
8001 / 8002 / 8003
```

Measured metrics include:

* Response Time
* Throughput
* Error Rate
* Concurrent Requests
* Request Distribution

---

## 🛡️ Failure Handling

If a backend server becomes unavailable, the Load Balancer handles the failure and returns:

```text
HTTP 503 SERVICE UNAVAILABLE
```

This allows backend failures to be tested independently from the client.

---

## 📁 Project Structure

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
│   ├── primary.py
│   ├── replica.py
│   ├── router.py
│   └── crud.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

> `api_server.py` is not required. API functionality is handled directly by `backend_server.py`.

---

## 🛠️ Tech Stack

```text
Python 3
Flask
PostgreSQL
psycopg2
python-dotenv
Requests
Threading
Apache JMeter
Git / GitHub
```

---

## ▶️ Quick Start

### Install

```bash
git clone https://github.com/Soumya-singh602/load-balancer-demo.git
cd load-balancer-demo

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Start Backends

```bash
python backend_server.py 8001
python backend_server.py 8002
python backend_server.py 8003
```

### Start a Load Balancer

```bash
python round_robin.py
```

Then access:

```text
http://127.0.0.1:8000
```

---

## 🎯 What This Project Demonstrates

This project combines:

**Load Balancing + Concurrency + REST APIs + Database Replication + Read/Write Separation + Failure Handling + Data Consistency + Performance Testing**

into one distributed backend system.

---

## 👩‍💻 Author

**Soumya Singh**
