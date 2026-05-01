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
        sh '''
          echo "Workspace: $(pwd)"
          ls -la
          docker-compose down || true
          docker-compose build --no-cache
          docker-compose up -d --force-recreate
          echo "Waiting for services to start..."
          sleep 10
          echo "Web logs:"
          docker-compose logs --tail=100 web
          echo "Verifying application is up..."
          curl -f http://localhost:5000/
        '''
      }
    }
  }
}