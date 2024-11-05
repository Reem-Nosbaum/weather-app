pipeline {
    agent { label 'agent-node' }
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub_token')
        DOCKERHUB_REPO = 'reemnu26/weather-app'
        GIT_REPO = 'http://172.31.32.26/root/wheater-app.git'
        MANIFEST_REPO = 'http://172.31.32.26/root/python-app-deployment.git'
        SSH_CREDENTIALS = credentials('weather_app_ssh_key')
        SLACK_CHANNEL = '#general'
        SLACK_CREDENTIAL_ID = 'slack-bot-token'
        API_KEY = credentials('api-key-credential-id')
        SUCCESS_CHANNEL = '#succeeded-build'
        FAILURE_CHANNEL = '#DevOps-alerts'
        GIT_CREDENTIALS = 'git-credentials'
    }
    stages {
        stage('Clone Repository') {
            steps {                
                echo 'Cloning app repository...'
                git branch: 'main', url: "${GIT_REPO}", credentialsId: "${GIT_CREDENTIALS}"
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    dockerImage = docker.build("${DOCKERHUB_REPO}:${env.BUILD_ID}", "--build-arg API_KEY=${env.API_KEY} --no-cache .")
                }
            }
        }
        stage('Push to DockerHub') {
            steps {
                script {
                    echo 'Logging in to DockerHub...'
                    sh "echo Nosbaum94 | docker login -u reemnu26 --password-stdin"
                    echo 'Pushing Docker image to DockerHub...'
                    dockerImage.push("${env.BUILD_ID}")
                    dockerImage.push("latest")
                    sh "docker logout"
                }
            }
        }
        stage('Clone Manifest Repository') {
            steps {
                script {
                    echo 'Cloning manifest repository...'
                    dir('manifest-repo') {
                        git branch: 'main', url: "${MANIFEST_REPO}", credentialsId: "${GIT_CREDENTIALS}"
                    }
                }
            }
        }
        stage('Update Kubernetes Manifests') {
            steps {
                script {
                    echo 'Updating Kubernetes manifests...'
                    dir('manifest-repo') {
                        withCredentials([usernamePassword(credentialsId: "${GIT_CREDENTIALS}", passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                            sh """
                            git config user.name "reemnu"
                            git config user.email "reemnu@gmail.com"
                            sed -i 's|image: ${DOCKERHUB_REPO}:.*|image: ${DOCKERHUB_REPO}:${env.BUILD_ID}|' deployment.yaml
                            git add deployment.yaml
                            git commit -m "Update Kubernetes manifest with new Docker image version ${env.BUILD_ID}"
                            git push http://${GIT_USERNAME}:${GIT_PASSWORD}@172.31.32.26/root/python-app-deployment.git main
                            """
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                sh 'docker image prune -af'
                cleanWs()
            }
        }
        success {
            slackSend (
                channel: "${env.SUCCESS_CHANNEL}",
                color: '#00FF00',
                message: "Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) succeeded.",
                tokenCredentialId: 'slack-bot-token'
            )
        }
        failure {
            slackSend (
                channel: "${env.FAILURE_CHANNEL}",
                color: '#FF0000',
                message: "Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL}) failed.",
                tokenCredentialId: 'slack-bot-token'
            )
        }
    }
}
