# Simple Book CRUD

This project provides a simple CRUD application for managing books. Users can:

- Add books they want to read
- Update the reading status of books
- Delete books or modify their details

## Setup

#### Clone the repository

    git clone <repository-url>


#### Update the env file

1. Copy the Example Environment File:
    - Copy the .env.example file to a new file named .env.

2. Update the Database URL:
    - Open the .env file and update the DATABASE_URL variable if needed.
    - If you change the database URL, ensure you also update it in the docker-compose.yml file.

#### Run the docker app

To build and start the application, use Docker Compose:

    docker-compose up --build -d

#### Access the app

Once the containers are running, you can access the application via Swagger UI at:
    
    http://127.0.0.1:8000/docs


#### Run unit tests

To execute the unit tests, run:
    
    docker-compose exec web pytest


