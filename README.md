# Train Station Management API

This is a Django REST API for managing train stations, routes, trains, trips, and orders. The API provides functionality for users to view and manage stations, routes, train types, trips, tickets, and crew members. It supports features like filtering and pagination for better management of data.

## Features
- Manage stations, routes, trains, trip details, orders, and crews.
- Filters to search and sort stations, routes, and trips.
- Pagination for trip orders.
- Permission-based access control for different users.
---
## Database Structure
![img.png](img.png)

---
## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/KKvladys/api-service-train-station.git

# Set up the virtual environment
python -m venv venv
source venv/bin/activate  # For macOS/Linux
# venv\Scripts\activate   # For Windows

# Install dependencies
pip install -r requirements.txt

# Set up the database (make sure you have PostgreSQL running and configured)
# Update DATABASES section in train_station/settings.py with your database credentials
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Run the server locally
python manage.py runserver
```

---
#### Running with Docker
Build and Start the Services
Use Docker Compose to build and run the application and database:
```bash
docker-compose up --build
```
***
The API will be available at http://127.0.0.1:8000/

API Endpoints:
* Stations: /stations/
* Routes: /routes/
* Trains: /trains/
* Trips: /trips/
* Orders: /orders/
* Train Types: /train-types/
* Crews: /crews/

## Environment Variables

This project uses environment variables for configuration. A template file `.env.sample` is provided to guide you in setting up these variables. Before running the project, create a `.env` file based on the template and provide the required values.

### Setting Up Environment Variables
1. Copy the `.env.sample` file to create your `.env` file:

   ```bash
   cp .env.sample .env
    ```