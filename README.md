Markdown
# Load Balancer Demo

A robust, multi-threaded HTTP load balancer built using **Python** and **Flask**. This application demonstrates core distributed systems concepts by distributing incoming client requests across multiple backend servers using various industry-standard load-balancing algorithms.

---

## 🚀 Tech Stack

* **Language:** Python 3.x
* **Framework:** Flask
* **HTTP Library:** Requests
* **Concurrency:** Python Threading & Locks
* **Load Testing:** Apache JMeter
* **Version Control:** Git & GitHub

---

## 🧠 Load Balancing Algorithms

The load balancer supports six core algorithms to manage traffic distribution:

1. **Round Robin:** Sequentially cycles through the list of available backend servers.
2. **Weighted Round Robin:** Allocates requests proportional to pre-configured server weights/capacities.
3. **Least Connections:** Routes incoming requests to the server with the fewest active connections currently.
4. **Weighted Least Connections:** Combines active connection counts with server weights for optimal routing.
5. **IP Hash:** Computes a hash of the client's IP address to ensure session persistence (same client consistently hits the same backend).
6. **Random Selection:** Randomly chooses a healthy backend server for each request.

---

## 📐 Architecture & Topology

```text
Client Request 
       │
       ▼
 ┌───────────┐         ┌───────────────┐
 │           ├────────►│ Backend 1     │ (127.0.0.1:8001)
 │   Load    ├────────►│ Backend 2     │ (127.0.0.1:8002)
 │  Balancer │         ├───────────────┤
 │ (Port 8000│         │ Backend 3     │ (127.0.0.1:8003)
 └───────────┘         └───────────────┘
Load Balancer Entry Point: http://127.0.0.1:8000

Backend Server 1: http://127.0.0.1:8001

Backend Server 2: http://127.0.0.1:8002

Backend Server 3: http://127.0.0.1:8003

✨ Key Features
Multiple Algorithms: Easily switch between 6 different load balancing strategies.

Thread-Safe Concurrency: Built with Python threading.Lock to safely manage shared state across concurrent requests.

Weighted Server Support: Distribute higher traffic loads to more powerful backend nodes.

IP-Based Session Persistence: Maintain client stickiness using IP hashing.

Comprehensive Load Testing: Validated under high concurrency using Apache JMeter.

Real-Time Monitoring: Detailed request distribution tracking and logging via server console outputs.

🛠️ Getting Started & Installation
Prerequisites
Python 3.8 or higher installed on your machine.

pip package manager.

1. Clone the Repository
Bash
git clone [https://github.com/your-username/load-balancer-demo.git](https://github.com/your-username/load-balancer-demo.git)
cd load-balancer-demo
2. Install Dependencies
Bash
pip install flask requests
🚀 Running the Application
To run the complete demonstration, you need to spin up the backend servers and the load balancer.

Step 1: Start Backend Servers
Open separate terminal windows and start your backend instances on ports 8001, 8002, and 8003:

Bash
python backend_server.py --port 8001
python backend_server.py --port 8002
python backend_server.py --port 8003
Step 2: Start the Load Balancer
Run the main load balancer script:

Bash
python load_balancer.py
The load balancer will now be active at http://127.0.0.1:8000.

📊 Load Testing with Apache JMeter
To verify throughput, latency, and request distribution under stress:

Open Apache JMeter.

Create a Thread Group (e.g., 50 threads, ramp-up period of 5 seconds, loop count 100).

Add an HTTP Request Sampler pointing to 127.0.0.1, port 8000.

Add listeners such as Summary Report, Aggregate Report, and Results Tree.

Run the test plan and observe how requests are distributed across backends in the server logs.

👤 Author
Soumya Singh