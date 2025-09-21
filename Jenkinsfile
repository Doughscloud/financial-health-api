pipeline {
    agent any
    
    environment {
        // Docker configuration
        DOCKER_IMAGE = 'financial-health-api'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'your-registry' // Update with your registry
        
        // Application configuration
        APP_NAME = 'financial-health-api'
        PORT = '5001'
        
        // AWS configuration (if deploying to AWS)
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '123456789012.dkr.ecr.us-east-1.amazonaws.com' // Update with your ECR
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
                
                // Display build information
                sh '''
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Build ID: ${BUILD_ID}"
                    echo "Job Name: ${JOB_NAME}"
                    echo "Workspace: ${WORKSPACE}"
                '''
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    # Create virtual environment
                    python3 -m venv venv
                    
                    # Activate virtual environment and install dependencies
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Install testing dependencies
                    pip install pytest pytest-cov flake8 black
                '''
            }
        }
        
        stage('Code Quality & Linting') {
            steps {
                echo 'Running code quality checks...'
                sh '''
                    . venv/bin/activate
                    
                    # Check code formatting with black
                    echo "Checking code formatting..."
                    black --check --diff app.py || true
                    
                    # Run linting with flake8
                    echo "Running linting checks..."
                    flake8 app.py --max-line-length=88 --ignore=E203,W503 || true
                    
                    # Display code statistics
                    echo "Code statistics:"
                    wc -l *.py
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    
                    # Create test file if it doesn't exist
                    if [ ! -f test_app.py ]; then
                        cat > test_app.py << 'EOF'
import pytest
import json
from app import app, db, Tip

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_home_endpoint(client):
    """Test the home endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['status'] == 'running'

def test_get_tips_empty(client):
    """Test getting tips when none exist"""
    response = client.get('/tips')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['tips'] == []

def test_add_tip(client):
    """Test adding a new tip"""
    tip_data = {'tip': 'Save 20% of your income'}
    response = client.post('/tips', 
                          data=json.dumps(tip_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Tip added!'

def test_get_tips_with_data(client):
    """Test getting tips after adding one"""
    # Add a tip first
    tip_data = {'tip': 'Build an emergency fund'}
    client.post('/tips', 
                data=json.dumps(tip_data),
                content_type='application/json')
    
    # Get tips
    response = client.get('/tips')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['tips']) == 1
    assert 'Build an emergency fund' in data['tips']

def test_add_tip_invalid_json(client):
    """Test adding tip with invalid JSON"""
    response = client.post('/tips', 
                          data='invalid json',
                          content_type='text/plain')
    assert response.status_code == 400

def test_add_tip_missing_field(client):
    """Test adding tip without required field"""
    response = client.post('/tips', 
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
EOF
                    fi
                    
                    # Run tests with coverage
                    python -m pytest test_app.py -v --cov=app --cov-report=term-missing
                '''
            }
            post {
                always {
                    // Archive test results if using pytest-html
                    publishTestResults testResultsPattern: 'test-results.xml'
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security scans...'
                sh '''
                    . venv/bin/activate
                    
                    # Install security scanning tools
                    pip install safety bandit || true
                    
                    # Check for known security vulnerabilities in dependencies
                    echo "Checking dependencies for security vulnerabilities..."
                    safety check || true
                    
                    # Run static security analysis
                    echo "Running static security analysis..."
                    bandit -r . -f json -o bandit-report.json || true
                    bandit -r . || true
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    // Build Docker image
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    
                    // Also tag as latest
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                    
                    // Display image information
                    sh '''
                        echo "Docker images built:"
                        docker images | grep financial-health-api
                        
                        echo "Image size:"
                        docker images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}" | grep financial-health-api
                    '''
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                sh '''
                    # Run container in background for testing
                    docker run -d --name test-container -p 5002:5001 ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    # Wait for container to start
                    sleep 10
                    
                    # Test if the application is responding
                    echo "Testing application health..."
                    curl -f http://localhost:5002/ || exit 1
                    
                    # Test API endpoints
                    echo "Testing API endpoints..."
                    curl -f http://localhost:5002/tips || exit 1
                    
                    # Test adding a tip
                    echo "Testing POST endpoint..."
                    curl -X POST http://localhost:5002/tips \
                         -H "Content-Type: application/json" \
                         -d '{"tip": "Test tip from Jenkins"}' || exit 1
                    
                    # Cleanup test container
                    docker stop test-container
                    docker rm test-container
                    
                    echo "Docker image tests passed!"
                '''
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    // Push to Docker registry (configure based on your registry)
                    docker.withRegistry('', 'docker-registry-credentials') {
                        def image = docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}")
                        image.push()
                        image.push("latest")
                    }
                }
                
                // Alternative: Push to AWS ECR
                /*
                sh '''
                    # Login to ECR
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    
                    # Tag image for ECR
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${ECR_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${ECR_REGISTRY}/${DOCKER_IMAGE}:latest
                    
                    # Push to ECR
                    docker push ${ECR_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker push ${ECR_REGISTRY}/${DOCKER_IMAGE}:latest
                '''
                */
            }
        }
        
        stage('Deploy to Staging') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                    branch 'master'
                }
            }
            steps {
                echo 'Deploying to staging environment...'
                sh '''
                    # Stop existing staging container if running
                    docker stop financial-health-staging || true
                    docker rm financial-health-staging || true
                    
                    # Run new container in staging
                    docker run -d \
                        --name financial-health-staging \
                        -p 5003:5001 \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    
                    # Wait for application to start
                    sleep 15
                    
                    # Verify staging deployment
                    echo "Verifying staging deployment..."
                    curl -f http://localhost:5003/ || exit 1
                    
                    echo "Staging deployment successful!"
                    echo "Staging URL: http://localhost:5003"
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
                parameters {
                    choice(
                        name: 'DEPLOYMENT_STRATEGY',
                        choices: ['rolling', 'blue-green', 'recreate'],
                        description: 'Choose deployment strategy'
                    )
                }
            }
            steps {
                echo "Deploying to production with ${DEPLOYMENT_STRATEGY} strategy..."
                
                script {
                    if (params.DEPLOYMENT_STRATEGY == 'blue-green') {
                        // Blue-Green deployment
                        sh '''
                            # Check current production container
                            CURRENT_PORT=$(docker port financial-health-prod 2>/dev/null | cut -d: -f2 || echo "5001")
                            NEW_PORT=$((CURRENT_PORT == 5001 ? 5004 : 5001))
                            
                            echo "Current port: $CURRENT_PORT, New port: $NEW_PORT"
                            
                            # Deploy to new port
                            docker run -d \
                                --name financial-health-prod-new \
                                -p $NEW_PORT:5001 \
                                --restart unless-stopped \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                            
                            # Wait and verify
                            sleep 15
                            curl -f http://localhost:$NEW_PORT/ || exit 1
                            
                            # Switch traffic (update load balancer configuration here)
                            echo "Blue-green deployment completed on port $NEW_PORT"
                        '''
                    } else {
                        // Rolling/Recreate deployment
                        sh '''
                            # Stop current production container
                            docker stop financial-health-prod || true
                            docker rm financial-health-prod || true
                            
                            # Deploy new version
                            docker run -d \
                                --name financial-health-prod \
                                -p 5001:5001 \
                                --restart unless-stopped \
                                -v financial-health-data:/app/instance \
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                            
                            # Wait for application to start
                            sleep 15
                            
                            # Verify production deployment
                            curl -f http://localhost:5001/ || exit 1
                            
                            echo "Production deployment successful!"
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
            
            // Cleanup
            sh '''
                # Clean up test containers
                docker stop test-container || true
                docker rm test-container || true
                
                # Clean up old images (keep last 5)
                docker images ${DOCKER_IMAGE} --format "{{.Tag}}" | tail -n +6 | xargs -I {} docker rmi ${DOCKER_IMAGE}:{} || true
            '''
            
            // Archive artifacts
            archiveArtifacts artifacts: '**/*.log, bandit-report.json', allowEmptyArchive: true
            
            // Clean workspace
            cleanWs()
        }
        
        success {
            echo 'Pipeline succeeded! 🎉'
            
            // Send success notification (configure based on your setup)
            /*
            emailext (
                subject: "✅ Jenkins Build Successful: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    Build successful!
                    
                    Job: ${env.JOB_NAME}
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                    
                    Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}
                """,
                to: "team@company.com"
            )
            */
        }
        
        failure {
            echo 'Pipeline failed! ❌'
            
            // Send failure notification
            /*
            emailext (
                subject: "❌ Jenkins Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    Build failed!
                    
                    Job: ${env.JOB_NAME}
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                    
                    Please check the build logs for details.
                """,
                to: "team@company.com"
            )
            */
        }
        
        unstable {
            echo 'Pipeline is unstable! ⚠️'
        }
    }
}

