pipeline {
    agent any
    
    // إضافة خيارات للتخصيص
    options {
        timestamps()  // إظهار التواقيت في السجلات
        timeout(time: 30, unit: 'MINUTES')  // وقت أقصى للبناء
        buildDiscarder(logRotator(numToKeepStr: '10'))  // الاحتفاظ بآخر 10 بناءات فقط
    }
    
    // محددات التشغيل
    triggers {
        pollSCM('* * * * *')  // يتحقق كل دقيقة من التغييرات
        // يمكن إضافة GitHub hook trigger أيضاً
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/AdnanAlrashed/studentPro.git',
                credentialsId: 'github-token',
                changelog: true  // تسجيل التغييرات
            }
            
            // إضافة post actions للمرحلة
            post {
                success {
                    echo '✅ تم تحميل الكود بنجاح من GitHub'
                }
                failure {
                    echo '❌ فشل في تحميل الكود من GitHub'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t studentapp:${BUILD_ID} .'
                sh 'docker tag studentapp:${BUILD_ID} studentapp:latest'
            }
            
            post {
                success {
                    echo '✅ تم بناء image Docker بنجاح'
                    archiveArtifacts artifacts: '**/Dockerfile', fingerprint: true
                }
            }
        }
        
        stage('Run Tests') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'docker run --rm studentapp python manage.py test --tag=unit --noinput'
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh 'docker run --rm studentapp python manage.py test --tag=integration --noinput'
                    }
                }
            }
            
            post {
                always {
                    junit '**/test-reports/*.xml'  // جمع نتائج الاختبارات
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh 'docker scan studentapp:latest --file Dockerfile'
            }
        }
        
        stage('Deploy to Test') {
            steps {
                sh 'docker-compose down --remove-orphans'
                sh 'docker-compose up -d --build'
                sh 'sleep 10'  // انتظار حتى يعمل التطبيق
            }
            
            post {
                success {
                    echo '✅ تم النشر بنجاح على test environment'
                    // إرسال إشعار
                    slackSend channel: '#deployments', 
                              message: "تم النشر بنجاح: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
                }
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    # اختبار أن التطبيق يعمل
                    curl -f http://localhost:8000/ || exit 1
                    echo "✅ التطبيق يعمل بشكل صحيح"
                '''
            }
        }
    }
    
    // إجراءات بعد انتهاء الـ Pipeline
    post {
        always {
            echo '🎯 Pipeline ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}'
            cleanWs()  // تنظيف مساحة العمل
        }
        success {
            echo '🎉 تم تنفيذ الـ Pipeline بنجاح!'
            emailext subject: '✅ Pipeline نجح: ${env.JOB_NAME} #${env.BUILD_NUMBER}',
                     body: 'تم تنفيذ الـ Pipeline بنجاح. التفاصيل: ${env.BUILD_URL}',
                     to: 'your-email@example.com'
        }
        failure {
            echo '❌ فشل في تنفيذ الـ Pipeline'
            emailext subject: '❌ Pipeline فشل: ${env.JOB_NAME} #${env.BUILD_NUMBER}',
                     body: 'فشل في تنفيذ الـ Pipeline. التفاصيل: ${env.BUILD_URL}',
                     to: 'your-email@example.com'
        }
        unstable {
            echo '⚠️ Pipeline غير مستقر'
        }
    }
    
    // إعداد environment variables
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        SLACK_CHANNEL = '#deployments'
        BUILD_ID = "${env.BUILD_NUMBER}"
    }
}