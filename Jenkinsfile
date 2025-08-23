pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/AdnanAlrashed/studentPro.git',
                credentialsId: 'jenkins_git_login'
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker build -t studentapp .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run studentapp python manage.py test'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker-compose down && docker-compose up -d'
            }
        }
    }
}