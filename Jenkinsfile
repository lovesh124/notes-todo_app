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
            python3 -m venv venv
            . venv/bin/activate
            pip install -r requirements.txt
            pytest --junitxml=results.xml
        '''
        // This makes the stage "Meaningful" by visualizing results in Jenkins
        junit 'results.xml' 
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
