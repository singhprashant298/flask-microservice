pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Check Python') {
            steps {
                sh 'python3 --version'
            }
        }

        stage('Backend Dependencies') {
            steps {
                dir('backend') {
                    sh 'python3 -m pip install --break-system-packages -r requirements.txt'
                }
            }
        }

        stage('Frontend Dependencies') {
            steps {
                dir('frontend') {
                    sh 'python3 -m pip install --break-system-packages -r requirements.txt'
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker build -t flask-backend:ci ./backend'
                sh 'docker build -t flask-frontend:ci ./frontend'
            }
        }
    }
    
    stage('Deploy to Minikube') {
    steps {
        sh '''
            helm upgrade --install flask-jenkins \
                ./helm/flask-microservices \
                --kubeconfig=/tmp/kubeconfig \
                --namespace jenkins-demo \
                --create-namespace
        '''
      }
    }

    post {
        success {
            echo 'Flask microservices CI completed successfully!'
        }
        failure {
            echo 'CI pipeline failed. Check Console Output.'
        }
    }
}
