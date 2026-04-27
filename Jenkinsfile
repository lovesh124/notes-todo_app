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
        // Install dependencies and run pytest; make the Verify/Test stage meaningful
        sh 'python3 -m pip install --upgrade pip'
        sh 'pip3 install -r requirements.txt'
        sh 'pytest -q'
      }
    }

    stage('Build Docker') {
      when {
        expression { return env.BRANCH_NAME == null || env.BRANCH_NAME == 'main' }
      }
      steps {
        sh 'docker build -t notes-todo:latest .'
      }
    }

    stage('Deploy') {
      when {
        expression { return env.BRANCH_NAME == null || env.BRANCH_NAME == 'main' }
      }
      steps {
        sh 'docker-compose up -d --build'
      }
    }
  }
}
