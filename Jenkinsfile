pipeline {
    agent any
    triggers {
        pollSCM('* * * * *')  // يتحقق كل دقيقة من التغييرات
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/AdnanAlrashed/studentPro.git',
                credentialsId: 'github-token'
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