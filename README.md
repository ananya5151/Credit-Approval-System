# Credit Approval System - Backend Project

This project is a fully containerized credit approval system built with Django, Django REST Framework, and PostgreSQL. It evaluates loan eligibility based on historical data, customer information, and a credit scoring model.

---
## ✅ FULL API DOCUMENTATION FROM POSTMAN

<img width="700" height="400" alt="Screenshot 2025-07-29 031259" src="https://github.com/user-attachments/assets/82523351-26ed-4a81-bc02-52f8dae58d68" />
<img width="700" height="400" alt="Screenshot 2025-07-29 031313" src="https://github.com/user-attachments/assets/5f2adc49-c317-4c20-ab29-a7ddd3d10387" />
<img width="700" height="400" alt="Screenshot 2025-07-29 031326" src="https://github.com/user-attachments/assets/32df4a1b-4b3a-483e-991a-1430d1c36028" />
<img width="700" height="400" alt="Screenshot 2025-07-29 031340" src="https://github.com/user-attachments/assets/971d2c64-3b76-468b-a12e-c5dc0ae5787c" />
<img width="700" height="400" alt="Screenshot 2025-07-29 031349" src="https://github.com/user-attachments/assets/3cb0139c-d0cf-4b23-8ed7-d8c286cd7a0c" />

## ✅ BONUS

<img width="600" height="278" alt="Screenshot 2025-07-29 031743" src="https://github.com/user-attachments/assets/de1514c1-e4b3-41e3-a262-df49facb3fae" />


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
    
    # Create the new migration instructions
    docker-compose exec web python manage.py makemigrations

    # Build the new database tables
    docker-compose exec web python manage.py migrate

    # Load the initial data
    docker-compose exec web python manage.py ingest_data
    ```
The application is now running at `http://localhost:8000`.

---

## 🧪 Running the Bonus Unit Tests
To run the bonus unit tests, use the following command:
```sh
docker-compose exec web python manage.py test
