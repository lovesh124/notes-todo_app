pipeline {
  agent any

  stages {

    stage('Test') {
      agent {
        docker {
          image 'python:3.10'
          args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
      }
      steps {
        sh '''
          python --version
          pip install --upgrade pip
          pip install -r requirements.txt
          pytest --junitxml=results.xml
        '''
      }
      post {
        always {
          junit 'results.xml'
        }
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