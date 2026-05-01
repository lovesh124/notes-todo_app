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


## How to run locally (with jenkins)
1. Go into the `jenkins` folder.
2. Build the Jenkins Docker image:
   ```bash
   docker build -t my-jenkins .
   ```
3. Run the Jenkins container:
   ```bash
   docker run -d -u root --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock my-jenkins
   ```
4. The Jenkins server should now be alive and accessible at `http://localhost:8080`.
5. Set up the Jenkins server:
   - Initialize plugins including Docker and Docker Pipeline.
   - Add a new item as a Pipeline.
   - Choose "Pipeline script from SCM".
   - Add the repository link.
   - For Git push triggers, choose "GitHub hook trigger for GITScm polling".
   - Expose your server (for local setup, use ngrok) and add the link in the GitHub repository settings under webhooks.
   - Choose "main" for the branch and save.
6. The pipeline will automatically run on every push to the specified branch.

## How to run locally (without jenkins)
1. Make sure you have Docker and Docker Compose installed.
2. Clone this repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize MongoDB (make sure MongoDB is running):
   ```bash
   python init_db.py
   ```
5. Run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```
6. The API will be available on `http://localhost:5000`.

## MongoDB Initialization
MongoDB is initialized with:
- Database: `notesdb`
- Collection: `notes`
- Indexes: `created_at`, `done`

To manually initialize MongoDB, run:
```bash
python init_db.py
```

The initialization script will:
- Connect to MongoDB
- Create the database and collection if they don't exist
- Create indexes for query optimization
- Verify the connection

## Testing
To run tests locally before pushing, you can just run:
```bash
pytest
```
