pipeline {
    agent any

    environment {
        // We tag the image with Jenkins build ID to ensure unique tags per run
        IMAGE_NAME = "aceest-gym:${env.BUILD_ID}"
    }

    stages {
        stage('Checkout') {
            steps {
                // Check out source code from Git
                checkout scm
            }
        }
        
        stage('Build Image') {
            steps {
                // Build the Docker image containing our Flask app and dependencies
                sh "docker build -t ${IMAGE_NAME} ."
            }
        }

        stage('Lint & Test') {
            steps {
                // Run flake8 linting using the image we just built
                sh "docker run --rm ${IMAGE_NAME} flake8 app.py --max-line-length=100"
                
                // Run tests using pytest inside the container
                sh "docker run --rm ${IMAGE_NAME} pytest test_app.py -v"
            }
        }

        stage('Deploy to Vercel') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'VERCEL_TOKEN', variable: 'VERCEL_TOKEN'),
                    string(credentialsId: 'VERCEL_ORG_ID', variable: 'VERCEL_ORG_ID'),
                    string(credentialsId: 'VERCEL_PROJECT_ID', variable: 'VERCEL_PROJECT_ID')
                ]) {
                    // Install Vercel CLI globally
                    sh 'npm install -g vercel'
                    
                    // Deploy to Vercel stringently with the production flag
                    sh 'vercel pull --yes --environment=production --token=$VERCEL_TOKEN'
                    sh 'vercel build --prod --token=$VERCEL_TOKEN'
                    sh 'vercel deploy --prebuilt --prod --token=$VERCEL_TOKEN'
                }
            }
        }
    }
    
    post {
        always {
            // Clean up the Docker image to free up space, even if the build fails
            sh "docker rmi ${IMAGE_NAME} || true"
        }
    }
}
