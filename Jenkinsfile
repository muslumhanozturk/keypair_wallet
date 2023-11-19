pipeline {
    agent any

    tools {
        ansible 'ansible'
        kubernetesTools 'kubectl'
    }

    stages {
        stage('Update ve Ansible Kurulum') {
            steps {
                script {
                    sh 'apt update -y'
                    sh 'apt install -y net-tools'
                    sh 'DEBIAN_FRONTEND=noninteractive apt-get install -y ansible'
                }
            }
        }

        stage('IP Adresini Sil ve Yeniden Yaz') {
            steps {
                script {
                    // IP adresini al 
                    def ipAddress = sh(script: "hostname -I | tr -s ' ' '\n' | head -n 1", returnStdout: true).trim()

                    // inventory.txt dosyasına yaz
                    writeFile file: 'keypair_wallet/inventory.txt', text: "[webserver]\n${ipAddress} ansible_connection=local\n"
                }
            }
        }

        stage('Ansible Playbooks') {
            steps {
                script {
                    sh 'ansible-playbook keypair_wallet/kubernetes_and_config.yml'
                    sh 'ansible-playbook keypair_wallet/prometheus_grafana_nodeexporter.yml'
                    sh 'ansible-playbook keypair_wallet/jaeger.yml' 
                }
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                script {
                    // Kubernetes YAML dosyalarını uygula 
                    sh 'kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/aws/deploy.yaml'
                    sh 'kubectl apply -f keypair_wallet/manifest_files/'
                }
            }
        }
    }

    post {
        success {
            script {
                slackSend channel: '#keypair-wallet', color: 'good', message: "Build başariyla tamamlandi: ${currentBuild.fullDisplayName}"
            }
        }
        failure {
            script {
                slackSend channel: '#keypair-wallet', color: 'danger', message: "Build başarisiz oldu: ${currentBuild.fullDisplayName}"
            }
        }
    }
}
