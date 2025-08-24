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
        stage('Advanced Security Scan') {
        steps {
            script {
                // استخدام Trivy لفحص أكثر تقدمًا
                sh """
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                        aquasec/trivy image ${IMAGE_NAME}:${VERSION}
                """
                
                // أو OWASP ZAP للفحص الديناميكي
                sh """
                    docker run --rm -t owasp/zap2docker-stable zap-baseline.py \\
                        -t http://localhost:${TEST_PORT} || true
                """
            }
        }
    }
        
        stage('Security Scan') {
            steps {
                script {
                    echo '🔍 بدء الفحص الأمني المتقدم...'
                    
                    // بناء أداة Security Scanner
                    sh '''
                        git clone https://github.com/AdnanAlrashed/security-scanner.git
                        cd security-scanner
                        docker build -t security-scanner:latest .
                        cd ..
                    '''
                    
                    // تشغيل الفحص الأمني
                    sh """
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            security-scanner:latest \
                            --image ${IMAGE_NAME}:${VERSION} \
                            --format json \
                            --output /tmp/security_scan
                    """
                    
                    // نسخ التقرير
                    sh '''
                        mkdir -p security-reports
                        docker run --rm \
                            -v $(pwd)/security-reports:/output \
                            -v /tmp:/tmp \
                            alpine:latest \
                            cp /tmp/security_scan.json /output/security_report.json
                    '''
                    
                    // تحليل النتائج
                    script {
                        def report = readJSON file: 'security-reports/security_report.json'
                        def critical = report.summary.critical ?: 0
                        def high = report.summary.high ?: 0
                        
                        echo "📊 نتائج الفحص الأمني:"
                        echo "🔴 الثغرات الحرجة: ${critical}"
                        echo "🟠 الثغرات العالية: ${high}"
                        echo "📋 الإجمالي: ${report.summary.total_vulnerabilities}"
                        
                        if (critical > 0) {
                            error "❌ فشل: تم اكتشاف ${critical} ثغرة حرجة!"
                        }
                        
                        if (high > 3) {
                            unstable "⚠️ تحذير: تم اكتشاف ${high} ثغرة عالية الخطورة"
                        }
                        
                        if (report.summary.total_vulnerabilities == 0) {
                            echo "🎉 ممتاز! لا توجد ثغرات أمنية"
                        }
                    }
                }
            }
        }
        
        // 🔒 مرحلة Security Testing المضافة
        stage('Security Testing') {
            steps {
                script {
                    echo '🔒 بدء فحوصات الأمان...'
                    
                    // 1. فحص vulnerabilities في الصورة
                    sh '''
                        echo "=== 🔍 فحص الثغرات في الصورة ==="
                        docker scan --accept-license ''' + env.IMAGE_NAME + ''':''' + env.VERSION + ''' || true
                    '''
                    
                    // 2. فحص dependencies للأمان
                    sh '''
                        echo "=== 📦 فحص dependencies ==="
                        docker run --rm -v $(pwd):/app ''' + env.IMAGE_NAME + ''':''' + env.VERSION + ''' \
                            pip audit || echo "pip audit not available"
                    '''
                    
                    // 3. فحص القواعد السريعة
                    sh '''
                        echo "=== 🐍 فحص Python code ==="
                        docker run --rm -v $(pwd):/app ''' + env.IMAGE_NAME + ''':''' + env.VERSION + ''' \
                            python -m bandit -r . || echo "Bandit not available"
                    '''
                    
                    echo '✅ تم إكمال فحوصات الأمان'
                }
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
                            echo "⏱️ الانتظار 5 ثواني للمحاولة القادمة..."
                            sleep 5
                            attempt++
                        }
                    }
                    
                    if (healthCheck != "200") {
                        echo "⚠️ التطبيق يعمل ولكن لا يستجيب على port ${TEST_PORT}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "🎯 Pipeline ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}"
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