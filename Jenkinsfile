
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        NAMESPACE = 'jenkins-demo'
        RELEASE_NAME = 'flask-jenkins'
        KUBECONFIG = '/tmp/kubeconfig'

        BACKEND_IMAGE = 'flask-backend'
        FRONTEND_IMAGE = 'flask-frontend'

        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        // 1. Checkout latest source code
        stage('Checkout') {
            steps {
                checkout scm

                echo 'Latest source code checked out successfully'
            }
        }

        // 2. Verify latest GitHub code
        stage('Verify Latest Code') {
            steps {
                sh '''
                    echo "========== LATEST COMMIT =========="
                    git log -1 --oneline

                    echo "========== FRONTEND HTML =========="
                    cat frontend/templates/index.html

                    echo "========== WORKSPACE =========="
                    pwd
                '''
            }
        }

        // 3. Check Python
        stage('Check Python') {
            steps {
                sh '''
                    python3 --version
                    python3 -m pip --version
                '''
            }
        }

        // 4. Install backend dependencies
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

        // 5. Install frontend dependencies
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

        // 6. Build Docker images
        stage('Build Docker Images') {
            steps {
                sh '''
                    echo "Building Backend Image..."

                    docker build --no-cache \
                        -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                        ./backend

                    echo "Building Frontend Image..."

                    docker build --no-cache \
                        -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                        ./frontend

                    echo "Docker images built successfully"

                    docker images | grep flask
                '''
            }
        }

        // 7. Load images into Minikube
        stage('Load Images into Minikube') {
            steps {
                sh '''
                    echo "Loading Backend Image..."

                    minikube image load \
                        ${BACKEND_IMAGE}:${IMAGE_TAG}

                    echo "Loading Frontend Image..."

                    minikube image load \
                        ${FRONTEND_IMAGE}:${IMAGE_TAG}

                    echo "Images loaded into Minikube"
                '''
            }
        }

        // 8. Deploy using Helm
        stage('Deploy with Helm') {
            steps {
                sh '''
                    echo "Deploying Flask Microservices..."

                    helm upgrade --install ${RELEASE_NAME} \
                        ./helm/flask-microservices \
                        --kubeconfig=${KUBECONFIG} \
                        --namespace ${NAMESPACE} \
                        --create-namespace \
                        --set backend.image.repository=${BACKEND_IMAGE} \
                        --set backend.image.tag=${IMAGE_TAG} \
                        --set frontend.image.repository=${FRONTEND_IMAGE} \
                        --set frontend.image.tag=${IMAGE_TAG} \
                        --wait \
                        --timeout 180s

                    echo "Helm deployment completed"
                '''
            }
        }

        // 9. Wait for Kubernetes rollout
        stage('Restart Deployments') {
            steps {
                sh '''
                    echo "Waiting for Backend rollout..."

                    kubectl --kubeconfig=${KUBECONFIG} \
                        rollout status deployment/backend \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    echo "Waiting for Frontend rollout..."

                    kubectl --kubeconfig=${KUBECONFIG} \
                        rollout status deployment/frontend \
                        -n ${NAMESPACE} \
                        --timeout=180s
                '''
            }
        }

        // 10. Verify deployment
        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "========== DEPLOYED IMAGES =========="

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get deployments -n ${NAMESPACE} \
                        -o wide

                    echo "========== POD STATUS =========="

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get pods -n ${NAMESPACE} -o wide

                    echo "========== SERVICES =========="

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get services -n ${NAMESPACE}

                    echo "========== FRONTEND IMAGE =========="

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get deployment frontend -n ${NAMESPACE} \
                        -o jsonpath='{.spec.template.spec.containers[*].image}'

                    echo ""

                    echo "========== BACKEND IMAGE =========="

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get deployment backend -n ${NAMESPACE} \
                        -o jsonpath='{.spec.template.spec.containers[*].image}'

                    echo ""
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
            echo 'Pipeline failed. Check Jenkins Console Output.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}
