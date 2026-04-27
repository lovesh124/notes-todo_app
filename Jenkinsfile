pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/lovesh124/notes-todo_app.git'
            }
        }

        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Verify') {
            steps {
                sh 'pytest'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker-compose up --build -d'
            }
        }
    }
}