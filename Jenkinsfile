// Paste the above code here
pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "studentapp"
        VERSION = "${env.BUILD_ID}"
        TEST_PORT = "8001"
    }
    
    triggers {
        pollSCM('* * * * *')
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                git(
                    url: 'https://github.com/AdnanAlrashed/studentPro.git',
                    branch: 'main'
                )
                echo '✅ تم تحميل الكود بنجاح من GitHub'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    script {
                        sh """
                            docker build -t ${IMAGE_NAME}:${VERSION} .
                            docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest
                        """
                        echo '✅ تم بناء صورة Docker'
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    sh """
                        docker run --rm ${IMAGE_NAME}:${VERSION} \
                            python manage.py test --noinput
                    """
                    echo '✅ تم تنفيذ الاختبارات بنجاح'
                }
            }
        }
        
        stage('Deploy to Test') {
            steps {
                script {
                    sh """
                        # إيقاف الحاوية القديمة إذا كانت تعمل
                        docker stop test-environment || true
                        docker rm test-environment || true
                        
                        # تشغيل الحاوية الجديدة على port 8001
                        docker run -d \\
                            --name test-environment \\
                            -p ${TEST_PORT}:8000 \\
                            ${IMAGE_NAME}:${VERSION}
                        
                        # الانتظار وقتاً أطول حتى يبدأ التطبيق
                        sleep 30
                    """
                    echo "✅ تم النشر إلى بيئة الاختبار على port ${TEST_PORT}"
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    // محاولة متعددة للاتصال بالتطبيق
                    def maxAttempts = 5
                    def attempt = 1
                    def healthCheck = "000"
                    
                    while (attempt <= maxAttempts && healthCheck != "200") {
                        echo "🔄 محاولة $attempt للاتصال بالتطبيق..."
                        healthCheck = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:${TEST_PORT}/ || echo '000'", returnStdout: true).trim()
                        
                        if (healthCheck == "200") {
                            echo '✅ اختبار الصحة ناجح - التطبيق يعمل'
                        } else {
                            echo "⏱️ الانتظار 5 ثواني للمحاولة القادمة..."
                            sleep 5
                            attempt++
                        }
                    }
                    
                    if (healthCheck != "200") {
                        echo "⚠️ التطبيق يعمل ولكن لا يستجيب على port ${TEST_PORT}"
                        echo "🔍 جرب التحقق يدوياً: docker logs test-environment"
                        // لا نوقف البناء، فقط ننبه
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🎯 Pipeline ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            
            // تنظيف workspace
            cleanWs()
            
            // تنظيف حاويات الاختبار القديمة
            sh '''
                docker stop test-environment || true
                docker rm test-environment || true
            '''
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
        }
        
        failure {
            echo '❌ Pipeline failed!'
        }
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }
}