
pipeline {
    agent any

    environment {
        NAMESPACE = 'jenkins-demo'
        RELEASE_NAME = 'flask-jenkins'
        KUBECONFIG = '/tmp/kubeconfig'

        BACKEND_IMAGE = 'flask-backend'
        FRONTEND_IMAGE = 'flask-frontend'

        IMAGE_TAG = 'ci'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm

                echo 'Latest source code checked out successfully'
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
                    sh '''
                        python3 -m pip install \
                        --break-system-packages \
                        -r requirements.txt
                    '''
                }
            }
        }

        stage('Frontend Dependencies') {
            steps {
                dir('frontend') {
                    sh '''
                        python3 -m pip install \
                        --break-system-packages \
                        -r requirements.txt
                    '''
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    docker build --no-cache \
                        -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend

                    docker build --no-cache \
                        -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend
                '''
            }
        }

        stage('Load Images into Minikube') {
            steps {
                sh '''
                    minikube image load ${BACKEND_IMAGE}:${IMAGE_TAG}
                    minikube image load ${FRONTEND_IMAGE}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy with Helm') {
            steps {
                sh '''
                    helm upgrade --install ${RELEASE_NAME} \
                        ./helm/flask-microservices \
                        --kubeconfig=${KUBECONFIG} \
                        --namespace ${NAMESPACE} \
                        --create-namespace
                '''
            }
        }

        stage('Restart Deployments') {
            steps {
                sh '''
                    kubectl --kubeconfig=${KUBECONFIG} \
                        rollout restart deployment/backend \
                        deployment/frontend \
                        -n ${NAMESPACE}

                    kubectl --kubeconfig=${KUBECONFIG} \
                        rollout status deployment/backend \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    kubectl --kubeconfig=${KUBECONFIG} \
                        rollout status deployment/frontend \
                        -n ${NAMESPACE} \
                        --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Checking deployed images..."

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get deployments -n ${NAMESPACE} \
                        -o wide

                    echo "Checking pods..."

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get pods -n ${NAMESPACE}

                    echo "Checking services..."

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get services -n ${NAMESPACE}
                '''
            }
        }
    }

    post {
        success {
            echo 'Flask microservices CI/CD completed successfully!'
            echo 'Latest Docker images deployed to Minikube.'
        }

        failure {
            echo 'Pipeline failed. Check Console Output.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}
