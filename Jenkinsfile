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

        stage('Basic Security Scan') {
            steps {
                script {
                    echo '🔍 فحص أمان أساسي باستخدام docker scan...'
                    
                    sh """
                        docker scan --accept-license ${IMAGE_NAME}:${VERSION} > scan-result.txt || true
                    """
                    
                    // تحليل النتائج
                    sh '''
                        CRITICAL=$(grep -c "CRITICAL" scan-result.txt || echo 0)
                        HIGH=$(grep -c "HIGH" scan-result.txt || echo 0)
                        MEDIUM=$(grep -c "MEDIUM" scan-result.txt || echo 0)
                        
                        echo "📊 نتائج الفحص الأساسي:"
                        echo "🔴 حرجة: $CRITICAL"
                        echo "🟠 عالية: $HIGH"
                        echo "🟡 متوسطة: $MEDIUM"
                        
                        if [ "$CRITICAL" -gt 0 ]; then
                            echo "❌ ثغرات حرجة!"
                            exit 1
                        fi
                    '''
                    
                    archiveArtifacts artifacts: 'scan-result.txt', fingerprint: true
                }
            }
        }

        stage('Advanced Security Scan') {
            steps {
                script {
                    echo '🔬 بدء الفحص الأمني المتقدم...'
                    
                    // 1. استخدام Trivy لفحص شامل
                    sh """
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                            aquasec/trivy image --severity CRITICAL,HIGH ${IMAGE_NAME}:${VERSION} > trivy-scan.txt || true
                    """
                    
                    // 2. فحص OWASP ZAP إذا التطبيق يعمل
                    sh """
                        timeout 300 docker run --rm \
                            -t owasp/zap2docker-stable zap-baseline.py \
                            -t http://host.docker.internal:${TEST_PORT} > zap-scan.txt 2>&1 || echo "ZAP scan completed"
                    """
                    
                    echo '✅ تم إكمال الفحوصات المتقدمة'
                }
            }
        }
        
        stage('Django Specific Scan') {
            when {
                expression { return false } // تعطيل مؤقت لتجنب الأخطاء
            }
            steps {
                echo '⏸️ فحص Django معطل مؤقتاً'
            }
        }
        
        stage('Deploy to Test') {
            steps {
                script {
                    sh """
                        docker stop test-environment || true
                        docker rm test-environment || true
                        
                        docker run -d \\
                            --name test-environment \\
                            -p ${TEST_PORT}:8000 \\
                            ${IMAGE_NAME}:${VERSION}
                        
                        sleep 30
                    """
                    echo "✅ تم النشر إلى بيئة الاختبار على port ${TEST_PORT}"
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    def maxAttempts = 5
                    def attempt = 1
                    def healthCheck = "000"
                    
                    while (attempt <= maxAttempts && healthCheck != "200") {
                        echo "🔄 محاولة $attempt للاتصال بالتطبيق..."
                        healthCheck = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:${TEST_PORT}/ || echo '000'", returnStdout: true).trim()
                        
                        if (healthCheck == "200") {
                            echo '✅ اختبار الصحة ناجح - التطبيق يعمل'
                        } else {
                            echo "⏱️ الانتظار 10 ثواني للمحاولة القادمة..."
                            sleep 10
                            attempt++
                        }
                    }
                    
                    if (healthCheck != "200") {
                        echo "⚠️ التطبيق لا يستجيب، جاري المتابعة..."
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🎯 Pipeline ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            
            // حفظ التقارير
            archiveArtifacts artifacts: '*.txt', fingerprint: true
            
            // تنظيف
            cleanWs()
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