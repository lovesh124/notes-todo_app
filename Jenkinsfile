pipeline {
    agent {
        docker {
            image 'python:3.10'
        }
    }

    stages {
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