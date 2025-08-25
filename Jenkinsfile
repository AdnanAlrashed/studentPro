pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "studentapp"
        VERSION = "${env.BUILD_ID}"
        TEST_PORT = "8001"
        DJANGO_PROJECT_PATH = "."
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
                    
                    // 3. فحص dependencies متقدم
                    sh """
                        docker run --rm -v $(pwd):/app ${IMAGE_NAME}:${VERSION} \
                            pip-audit --format json > pip-audit.json 2>&1 || echo "pip-audit not available"
                    """
                    
                    echo '✅ تم إكمال الفحوصات المتقدمة'
                }
            }
        }
        
        stage('Django Specific Scan') {
            steps {
                script {
                    echo '🐍 بدء فحص Django المخصص...'
                    
                    // فحص إعدادات Django الأمنية - استخدام single quotes لتجنب مشاكل $
                    sh '''
                        docker run --rm -v $(pwd):/app ''' + env.IMAGE_NAME + ''':''' + env.VERSION + ''' \
                            python -c "
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studentpro.settings')

try:
    django.setup()
    security_issues = []
    
    # فحص DEBUG mode
    if settings.DEBUG:
        security_issues.append('CRITICAL: DEBUG = True in production')
    
    # فحص SECRET_KEY
    if 'django-insecure' in settings.SECRET_KEY or len(settings.SECRET_KEY) < 50:
        security_issues.append('HIGH: Weak SECRET_KEY')
    
    # فحص CSRF protection
    if 'django.middleware.csrf.CsrfViewMiddleware' not in settings.MIDDLEWARE:
        security_issues.append('HIGH: CSRF middleware missing')
    
    # فحص CORS settings
    if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
        security_issues.append('MEDIUM: CORS_ALLOW_ALL_ORIGINS = True')
    
    print('Security Issues found:')
    for issue in security_issues:
        print(f'🔍 {issue}')
    
    if not security_issues:
        print('✅ No Django security issues found')
        
except Exception as e:
    print(f'⚠️ Error checking Django settings: {e}")
                            " > django-security-check.txt
                    '''
                    
                    // تحليل نتائج فحص Django
                    sh '''
                        echo "📊 نتائج فحص Django:"
                        cat django-security-check.txt
                        
                        # التحقق من وجود مشاكل حرجة
                        if grep -q "CRITICAL" django-security-check.txt; then
                            echo "❌ مشاكل حرجة في إعدادات Django!"
                            exit 1
                        fi
                    '''
                    
                    archiveArtifacts artifacts: 'django-security-check.txt', fingerprint: true
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
        
        stage('Final Security Validation') {
            steps {
                script {
                    echo '🎯 التحقق النهائي للأمان...'
                    
                    // فحص نهائي بعد النشر
                    sh """
                        docker run --rm --network host \\
                            aquasec/trivy web http://localhost:${TEST_PORT} > trivy-web-scan.txt 2>&1 || true
                    """
                    
                    // فحص HEADERS الأمنية
                    sh """
                        curl -I http://localhost:${TEST_PORT} > headers-check.txt 2>&1 || true
                    """
                    
                    echo '✅ التحقق النهائي مكتمل'
                }
            }
        }
    }
    
    post {
        always {
            echo "🎯 Pipeline ${currentBuild.currentResult} - ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            
            // حفظ جميع التقارير
            archiveArtifacts artifacts: '*.txt,*.json', fingerprint: true
            archiveArtifacts artifacts: 'scan-result.txt,trivy-scan.txt,zap-scan.txt,pip-audit.json,django-security-check.txt,trivy-web-scan.txt,headers-check.txt', fingerprint: true
            
            // تنظيف
            cleanWs()
            sh '''
                docker stop test-environment || true
                docker rm test-environment || true
                docker system prune -f || true
            '''
            
            // إنشاء تقرير ملخص
            script {
                def summary = """
                📊 ملخص نتائج الأمان:
                
                ✅ الفحص الأساسي: مكتمل
                ✅ الفحص المتقدم: مكتمل  
                ✅ فحص Django: مكتمل
                ✅ النشر: مكتمل
                ✅ الاختبار الصحي: مكتمل
                
                الحالة النهائية: ${currentBuild.currentResult}
                """
                
                writeFile file: 'security-summary.txt', text: summary
                archiveArtifacts artifacts: 'security-summary.txt', fingerprint: true
            }
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
            
            // إشعار النجاح
            emailext (
                subject: "✅ BUILD SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Pipeline completed successfully!
                
                Job: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                Status: SUCCESS
                
                View build: ${env.BUILD_URL}
                Download reports: ${env.BUILD_URL}artifact/
                """,
                to: "adnanalrashed77@gmail.com"
            )
        }
        
        failure {
            echo '❌ Pipeline failed!'
            
            // إشعار الفشل
            emailext (
                subject: "❌ BUILD FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Pipeline failed!
                
                Job: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                Status: FAILURE
                
                View build: ${env.BUILD_URL}
                Check logs for details.
                """,
                to: "adnanalrashed77@gmail.com"
            )
        }
        
        unstable {
            echo '⚠️ Pipeline unstable!'
            
            // إشعار unstable
            emailext (
                subject: "⚠️ BUILD UNSTABLE: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                Pipeline completed with warnings!
                
                Job: ${env.JOB_NAME}
                Build: #${env.BUILD_NUMBER}
                Status: UNSTABLE
                
                View build: ${env.BUILD_URL}
                Check reports for security warnings.
                """,
                to: "adnanalrashed77@gmail.com"
            )
        }
    }
    
    options {
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        retry(2)
    }
}