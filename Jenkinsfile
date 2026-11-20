
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

        stage('Checkout') {
            steps {
                checkout scm
                echo 'Latest source code checked out successfully'
            }
        }

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

        stage('Check Python') {
            steps {
                sh '''
                    python3 --version
                    python3 -m pip --version
                '''
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
                    echo "Building Backend Image: ${BACKEND_IMAGE}:${IMAGE_TAG}"

                    docker build --no-cache \
                        -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                        ./backend

                    echo "Building Frontend Image: ${FRONTEND_IMAGE}:${IMAGE_TAG}"

                    docker build --no-cache \
                        -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                        ./frontend

                    docker images | grep flask
                '''
            }
        }

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
                        --set backend.image.pullPolicy=IfNotPresent \
                        --set frontend.image.repository=${FRONTEND_IMAGE} \
                        --set frontend.image.tag=${IMAGE_TAG} \
                        --set frontend.image.pullPolicy=IfNotPresent \
                        --wait \
                        --timeout 180s

                    echo "Helm deployment completed"
                '''
            }
        }

        stage('Verify Deployment') {
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

                    echo "========== DEPLOYED IMAGES =========="

                    kubectl --kubeconfig=${KUBECONFIG} \
                        get deployments -n ${NAMESPACE} -o wide

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
