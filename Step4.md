### Jenkins

Jenkins, açık kaynaklı bir sürekli entegrasyon ve sürekli dağıtım (CI/CD) aracıdır. Yazılım geliştirme süreçlerini otomatikleştirmek, testleri yönetmek ve sürekli olarak yazılımı dağıtmak için kullanılır. Jenkins, kod tabanındaki değişiklikleri takip eder, otomatik testleri çalıştırır ve başarıyla tamamlananları belirli bir ortama dağıtarak yazılım geliştirme sürecini hızlandırır.
```bash 
#Jenkins kurulumu

#8080 portu Jaeger uygulaması tarafından kullanıldığı için 8082 portunu kullanıyoruz.
docker volume create jenkins
docker container run --name jenkins-container -d -p 8082:8080 --restart=always -v jenkins:/var/jenkins_home jenkins/jenkins:lts
```
Jenkin'in web arayüzüne erişmek için ```8082``` portuyla gidebilirsiniz.
```bash 
#Jenkins bağlantı ayarları
docker container exec -it jenkins-container /bin/bash  # container'a bağlanıyoruz.
cat /var/jenkins_home/secrets/initialAdminPassword     # jenkins server parola bilgisini kopyalayın.
                                                       # 8082 ekranından parola girişini yapıyoruz.
# Install suggested plugins          # Seçeneğini seçerek gerekli pluginlerin yüklenmesini sağlıyoruz.
# Getting Started ekranında gerekli kişisel parola bilgilerini giriyoruz.
```
Projemizde çalışmalarımızı doğru yürütebilmemiz için gerekli pluginleri yüklememiz gerekiyor. Bunlar;
```bash 
Manage Jenkins --> Plugins --> Available plugins --> Ansible            --> Install
                                                     Kubernetes
                                                     Slack Notification
                                                     AnsiColor
                                                     Deploy to container
                                                     Copy Artifact       
```
Şimdi de oluşturmuş olduğumuz Jenkinsfile pipeline dosyasını kullanarak github repomuzdan çekeceğimiz dosyaların çalıştırılmasını otomatize edelim. Ama öncesinde Slack Notification için gerekli credentials ve ayarlamaları yapalım.
```bash 
# Slack uygulamasını açarak kendimize BBK2023 adında bir workspace oluşturalım ve channel olarakta keypair-wallet adında kanal açalım.
BBK2023 --> Settings & Administration --> Manage Apps --> Jenkins CI --> Add to Slack
Açılan yeni sekmede --> Choose a channel... --> keypair-wallet --> Add jenkins CI integration
# Açılan yeni menüde Subdomain ve Credentials ID bilgileri bulunmakta bunları, Jenkins Server'a geçip şimdi yapacağımız adımlarla ayarlamaları tamamlamış olacağız.
Manage Jenkins --> System --> Slack --> Workspace = "Subdomain bilgisini gir"
                                        Default channel = "#keypair-wallet"
                                        Credentials --> Add --> Secret Text seçilip ve Secret bölümüne Credentials ID girilerek kaydedilir.
```
New Item ile Jenkins te pipeline çalıştırma işlemlerine başlayabiliriz.
```bash 
Dashboard --> +New Item --> "Item Name" --> Pipeline --> Ok
Description --> Keypair Wallet Project Pipeline
Discard old builds --> Strategy --> Log Rotation --> Days 5 --> builds keep 3
Github Project --> https://github.com/muslumhanozturk/keypair_wallet.git
GitHub hook trigger for GITScm polling 
Poll SCM --> Schedule --> H 3 * * *
Pipeline --> Pipeline script from SCM --> Git --> https://github.com/muslumhanozturk/keypair_wallet.git --> */main
```
Jenkinsfile pipeline dosyamız aşağıda belirtildiği gibidir. Bütün CI/CD (Continuous Integration/Continuous Deployment) sürecini otomatize etmektedir.
```bash 
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
                     sh 'cd keypair_wallet && ansible-playbook kubernetes_docker_config.yml'
                     sh 'cd keypair_wallet && ansible-playbook prometheus_grafana_nodeexporter.yml'
                     sh 'cd keypair_wallet && ansible-playbook jaeger.yml'
                }
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                script { 
                     sh 'cd keypair_wallet && kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/aws/deploy.yaml'
                     sh 'cd keypair_wallet && kubectl apply -f manifest_files/'
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
```
