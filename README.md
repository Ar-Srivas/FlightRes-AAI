## Intelligent Flight Route Optimization and Reservation System

### Overview

An AI-powered flight route optimizer that recommends the most efficient flight paths between cities.
It considers factors like travel time, ticket price, and layovers to find the best possible route.
The airline network is modeled as a graph where airports are nodes and flights are edges.
Using graph algorithms such as Dijkstra’s and A*, the system computes the optimal route based on combined weights.

---

### Features

* Models flights as a weighted directed graph
* Finds optimal routes using Dijkstra’s and A* algorithms
* Combines multiple factors like duration, price, and layover time
* Modular structure for graph modeling and route optimization
* Flask-based backend for easy integration and testing
* SQLite database seeded with sample airport and flight data

---

### Tech Stack

| Component                | Tools / Libraries       |
| ------------------------ | ----------------------- |
| Language                 | Python                  |
| Backend Framework        | Flask                   |
| Database                 | SQLite (via SQLAlchemy) |
| Graph Algorithms         | NetworkX, heapq, NumPy  |
| Data Handling            | pandas                  |
| ML (optional)            | scikit-learn            |
| Visualization (optional) | Plotly, Folium          |

---

### Setup Instructions

1. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Initialize and seed the database:

   ```bash
   python seed.py
   ```

4. Run the Flask server:

   ```bash
   python app.py
   ```

   The backend will start on `http://127.0.0.1:5000`.
