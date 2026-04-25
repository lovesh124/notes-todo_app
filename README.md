# Notes & Todo REST API

 This is a Notes and Todo REST API built to demonstrate continuous integration and deployment workflows. 

## Tech Stack
* **Backend:** Flask (Python)
* **Testing:** pytest
* **CI/CD:** Jenkins
* **Deployment:** Docker & Docker Compose
* **Version Control:** GitHub

## Project Overview
We are building a simple CRUD API where users can create, read, update, and delete notes. Every time code is pushed to our GitHub repository, Jenkins will automatically pull the code, run our test suite using `pytest`, and if everything passes, deploy the new version using Docker.

## How to run locally
1. Make sure you have Docker and Docker Compose installed.
2. Clone this repository.
3. Run the following command in the terminal:
   ```bash
   docker-compose up --build
   ```
4. The API will be available on `http://localhost:5000`.

## Testing
To run tests locally before pushing, you can just run:
```bash
pytest
```
