pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Test') {
      steps {
        sh '''
            python3 -m venv .venv
            . .venv/bin/activate
            pip install -r requirements.txt
            pytest --junitxml=results.xml
        '''

        junit 'results.xml' 
      }
    }

    stage('Build Docker') {
      steps {

        sh 'docker build -t notes-todo:latest .'
      }
    }

    stage('Deploy') {
      steps {
        sh 'docker-compose up -d --build'
      }
    }
  }
}