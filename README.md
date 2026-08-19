# ⚡ Distributed Load Balancer & Database Sharding System

A **distributed backend system built with Python, Flask, and PostgreSQL** that demonstrates load balancing, horizontal database sharding, Primary–Replica replication, read/write routing, failure handling, and concurrent performance testing.

The project is designed to demonstrate practical concepts used in **scalable and distributed backend systems**.

---

## 🚀 Key Features

* ⚖️ **6 Load Balancing Algorithms**
* 🔄 Round Robin
* ⚖️ Weighted Round Robin
* 🔗 Least Connections
* ⚖️ Weighted Least Connections
* 🌐 IP Hash
* 🎲 Random Selection
* 🗄️ **PostgreSQL Database Sharding**
* 🔁 **Primary–Replica Streaming Replication**
* 📖 Read / Write Database Routing
* 🖥️ 3 Flask Backend Servers
* ❤️ Health & Status Monitoring
* 🛡️ Backend Failure Handling
* 🧪 Postman API Testing
* 📊 Apache JMeter Load Testing
* 🚀 300 Concurrent User Testing
* 🔍 WAL / LSN Replication Verification

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
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           :8001        :8002        :8003
          Flask        Flask        Flask
          Server       Server       Server
              └────────────┼────────────┘
                           ▼
                  ┌─────────────────┐
                  │ Database Router │
                  └────────┬────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
              SHARD 1             SHARD 2
                 │                   │
             Primary              Primary
              :5432                :5435
                 │                   │
             Replica              Replica
              :5434                :5436
```

---

## ⚖️ Load Balancing Algorithms

| Algorithm                      | Strategy                                       |
| ------------------------------ | ---------------------------------------------- |
| **Round Robin**                | Sequential server distribution                 |
| **Weighted Round Robin**       | Distribution based on server weight            |
| **Least Connections**          | Selects server with minimum active connections |
| **Weighted Least Connections** | Combines connection count and server weight    |
| **IP Hash**                    | Consistent routing based on client IP          |
| **Random**                     | Random backend selection                       |

Only one algorithm runs on **port 8000** at a time for comparison testing.

---

## 🗄️ Database Sharding

User data is horizontally distributed across **two PostgreSQL shards**.

```text
                    Database Router
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
          SHARD 1                   SHARD 2
             │                         │
       Primary :5432             Primary :5435
             │                         │
       Replica :5434             Replica :5436
```

Each shard contains its own Primary and Replica database.

### Database Routing

```text
POST / PUT / DELETE  → Shard Primary
GET / SEARCH / COUNT → Shard Replica
```

The API response exposes the selected **server, shard, primary port, and replica port**, making routing behavior easy to verify.

---

## 🔄 PostgreSQL Replication

```text
Shard 1
Primary :5432
     │
     │ WAL Streaming
     ▼
Replica :5434


Shard 2
Primary :5435
     │
     │ WAL Streaming
     ▼
Replica :5436
```

Replication is verified using PostgreSQL:

```sql
SELECT pg_is_in_recovery();
```

Expected:

```text
Primary  → f
Replica  → t
```

Replication status can also be inspected using `pg_stat_replication` and WAL/LSN positions.

---

## 🔌 REST API

| Method | Endpoint           | Route         |
| ------ | ------------------ | ------------- |
| GET    | `/health`          | Health check  |
| GET    | `/status`          | Server status |
| GET    | `/users`           | Replica       |
| POST   | `/users`           | Primary       |
| GET    | `/users/search?q=` | Replica       |
| GET    | `/users/count`     | Replica       |
| GET    | `/users/<id>`      | Replica       |
| PUT    | `/users/<id>`      | Primary       |
| DELETE | `/users/<id>`      | Primary       |

### Example

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

## 🧪 Testing

### Postman

Used for:

* CRUD testing
* Shard routing verification
* Primary/Replica routing
* Health checks
* Search and count APIs
* Failure testing

Example response:

```json
{
  "server": "Server-8003",
  "database": "primary",
  "shard": 2,
  "primary_port": 5435,
  "replica_port": 5436
}
```

### Apache JMeter

The system is tested with **300 concurrent users**:

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

Measured metrics include:

* Response Time
* Throughput
* Error Rate
* Concurrent Requests
* Backend Distribution

---

## 🛡️ Failure Handling

Backend servers can be stopped independently to test failure scenarios.

The load-balancing layer detects unavailable backends and handles failed requests appropriately.

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
│   ├── crud.py
│   ├── primary.py
│   ├── replica.py
│   ├── router.py
│   ├── shard_router.py
│   ├── shard2_primary.py
│   └── shard2_replica.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ Tech Stack

**Backend**

* Python 3
* Flask
* Threading
* Requests

**Database**

* PostgreSQL
* psycopg2
* Streaming Replication
* WAL / LSN

**Testing & Tools**

* Postman
* Apache JMeter
* Git / GitHub

---

## ▶️ Quick Start

### Clone

```bash
git clone https://github.com/Soumya-singh602/load-balancer-demo.git
cd load-balancer-demo
```

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start Backend Servers

```bash
python backend_server.py 8001
python backend_server.py 8002
python backend_server.py 8003
```

### Start Load Balancer

```bash
python round_robin.py
```

Application:

```text
http://127.0.0.1:8000
```

---

## 🎯 What This Project Demonstrates

This project brings together:

**Load Balancing + Database Sharding + Replication + Read/Write Separation + REST APIs + Failure Handling + Concurrency + Performance Testing**

to demonstrate the architecture and implementation principles of a **scalable distributed backend system**.

---

## 👩‍💻 Author

### Soumya Singh

**Backend & Distributed Systems Project**

Python • Flask • PostgreSQL • Load Balancing • Database Sharding • Apache JMeter
