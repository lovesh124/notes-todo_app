pipeline {
  agent any

  stages {

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

    stage('Build Docker') {
      steps {
        sh 'docker build -t notes-todo:latest .'
      }
    }

    stage('Deploy') {
      steps {
        // Person 3: Docker Deployment & Verification
        sh '''
          docker-compose down || true
          docker-compose up -d --build
          echo "Waiting for services to start..."
          sleep 10
          echo "Verifying application is up..."
          curl -f http://localhost:5000/
        '''
      }
    }
  }
}