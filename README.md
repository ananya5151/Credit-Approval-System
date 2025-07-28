# Credit Approval System - Alemeno Backend Internship Assignment

This project is a fully containerized credit approval system built with Django, Django REST Framework, and PostgreSQL. It evaluates loan eligibility based on historical data, customer information, and a credit scoring model.

---

## ✅ Features & Requirements Checklist

This project successfully implements all the requirements outlined in the assignment:

-  Built with Django 4+ and Django REST Framework.
-  Uses a PostgreSQL database for data storage.
-  Implements complete API with 5 endpoints (`/register`, `/check-eligibility`, `/create-loan`, `/view-loan`, `/view-loans`).
-  Ingests initial customer and loan data using background workers (Celery & Redis).
- 🏆 **Bonus:** Includes a suite of unit tests for the core API endpoints.
-  The entire application and all dependencies are containerized using Docker.
-  The system runs from a single `docker-compose up` command.

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL
- **Async Tasks:** Celery, Redis
- **Containerization:** Docker, Docker Compose

---

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose installed.
- The `customer_data.xlsx` and `loan_data.xlsx` files.

### How to Run
1.  **Clone the repository:**
    ```sh
    git clone <your-repo-link>
    cd <your-repo-name>
    ```
2.  **Place Data Files:**
    Place the `customer_data.xlsx` and `loan_data.xlsx` files in the root of the project directory.

3.  **Run the application:**
    Use the single docker-compose command. This will build the images and start all services.
    ```sh
    docker-compose up --build
    ```

4.  **Set up the database (in a second terminal):**
    Once the containers are running, open a new terminal and run the following commands to set up the database and ingest the data.
    ```sh
    # Apply database migrations
    docker-compose exec web python manage.py migrate

    # Ingest data from Excel files
    docker-compose exec web python manage.py ingest_data
    ```
The application is now running at `http://localhost:8000`.

---

## 🧪 Running the Bonus Unit Tests
To run the bonus unit tests, use the following command:
```sh
docker-compose exec web python manage.py test
