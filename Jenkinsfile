pipeline {
    agent any

    tools {
        ansible 'ansible'
        kubernetesTools 'kubectl' 
    }

    stages {
        stage('Ansible Playbooks') {
            steps {
                script {
                    // Ansible dosyalarını çalıştır
                    sh 'ansible-playbook kubernetes_and_config.yml'
                    sh 'ansible-playbook prometheus_grafana_nodeexporter.yml'
                }
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                script {
                    // Kubernetes YAML dosyalarını uygula
                    sh 'kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/aws/deploy.yaml'
                    sh 'kubectl apply -f kubernetes-files/'
                }
            }
        }
    }
}