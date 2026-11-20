
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
                sh '''
                    docker build -t flask-backend:ci ./backend
                    docker build -t flask-frontend:ci ./frontend
                '''
            }
        }

        stage('Load Images into Minikube') {
            steps {
                sh '''
                    minikube image load flask-backend:ci
                    minikube image load flask-frontend:ci
                '''
            }
        }

        stage('Deploy with Helm') {
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

        stage('Restart Deployments') {
            steps {
                sh '''
                    kubectl --kubeconfig=/tmp/kubeconfig \
                        rollout restart deployment/backend \
                        deployment/frontend \
                        -n jenkins-demo

                    kubectl --kubeconfig=/tmp/kubeconfig \
                        rollout status deployment/backend \
                        -n jenkins-demo

                    kubectl --kubeconfig=/tmp/kubeconfig \
                        rollout status deployment/frontend \
                        -n jenkins-demo
                '''
            }
        }
    }

    post {
        success {
            echo 'Flask microservices CI/CD completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
