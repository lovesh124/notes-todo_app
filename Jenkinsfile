pipeline {
  agent any

  stages {

    stage('Debug Environment') {
      steps {
        sh 'docker --version'
        sh 'docker-compose --version'
      }
    }


    stage('Test') {
      agent {
        docker {
          image 'python:3.10'
          args '-u root'
        }
      }

      steps {
        sh '''
          python3 --version

          python3 -m venv .venv
          . .venv/bin/activate

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

    stage('Deploy') {
      steps {
        sh 'docker-compose up -d --build'
      }
    }
  }
}