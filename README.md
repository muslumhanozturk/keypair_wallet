# Keypair Wallet

Bulut hizmet sağlayıcılarında kullanılan servislere erişim için access key, secret key ve keypair.pem dosyalarını oluşturmak genellikle uygulanan bir yöntemdir. Ancak bu özel anahtar dosyalarını sadece lokal bilgisayarımızda saklamak, Bulut Hizmet Sağlayıcılarına sadece kendi bilgisayarımızdan erişim sağlama yeteneğimizi sınırlar. Bu dosyaların silinmesi veya farklı bir bilgisayardan erişim sağlama ihtiyacı ortaya çıktığında, her seferinde yeni anahtarlar oluşturmak zaman kaybına neden olabilir. 

Özellikle acil durumlarda, müşteri sunucusuna hızlı müdahale yapabilmek için bu anahtar dosyalarına hızla erişim sağlamak kritik öneme sahiptir. Müşteri anlaşmalarında belirtilen ciddi ücret ve cezaların önlenmesi için bu süreç hızlı ve etkili bir şekilde gerçekleştirilmelidir. 

Bu nedenle, bu süreci optimize etmek için anahtar dosyalarını güvenli bir şekilde depolamak, gerektiğinde hızlı erişim sağlamak ve yeni anahtarlar oluşturma sürecini kolaylaştırmak için bir strateji oluşturmak önemlidir. Bu, iş sürekliliğini sağlamak ve acil durum müdahalelerini en aza indirmek için hayati bir adımdır. 

Bu projeyi version-1 olarak sundum ancak geliştirme aşamasında ve 2 önemli konuda geliştirmeyi hedeflemekteyim.

1- Daha hızlı aksiyon alınabilmesi için yeni key dosyalarının script yardımıyla Bulut Hizmet Sağlayacılarında oluşturulması ve uygulamaya eklenmesi.

2- Bu key dosyalarının daha korunaklı saklanabilmesi için kendi şifreleme algoraitmamı oluşturup sisteme dahil etmek istiyorum. 

Keypair Wallet adını verdiğim projede Ansible, Docker, Kubernetes, Prometheus, Grafana, Jaeger, Jenkins gibi DevOps araçlarının yanı sıra Python, HTML, SQL Database, Nginx gibi teknolojiler ve Slack bildirimleri de aktif olarak kullanılmaktadır. 

Şimdi sizlerle bu projeyi daha yakından inceleyip adım adım ilerleyerek uygulayalım.  
 
GitHub repodan gerekli uygulama dosyalarını kendi çalışma alanımıza çekelim.
```bash
git clone https://github.com/muslumhanozturk/keypair_wallet.git 

cd keypair_wallet/  
```
### Ansible Kurulumu

Öncelikle ansible'ın ne olduğuna bakalım. Ansible, otomasyon, yapılandırma yönetimi ve uygulama dağıtımı için kullanılan açık kaynaklı bir araçtır. Sunucuları ve altyapıyı yönetmek için YAML tabanlı bir dil kullanır. Mimarimizdeki tüm süreçte kullanılmak üzere tüm toolların yüklenmesi ve gerekli konfigurasyon ayarlamaların yapılabilmesi için gerekli olan aracımızdır.
```bash
apt update -y 
DEBIAN_FRONTEND=noninteractive apt-get install -y ansible
```
Ansible'ı başarıyla kullanabilmek için bazı önemli konfigürasyon dosyalarını düzenlemeniz gerekmektedir. İlk olarak, ansible.cfg dosyası genel Ansible yapılandırma ayarlarını içerir. Bu dosyayı düzenleyerek, Ansible'ın nasıl çalışacağını belirleyebilir ve özel tercihleri tanımlayabilirsiniz.
```bash
[defaults]
host_key_checking = False   #SSH check-in işlemini devre dışı bırakır. Kullanılmasada olur.
inventory = inventory.txt   
deprecation_warnings=False
interpreter_python=auto_silent
```
Ayrıca, inventory.txt dosyası, Ansible'ın yönettiği sistemleri ve bu sistemlerle ilişkilendirilmiş grupları içerir. Bu dosya, hedef sistemlerin IP adresleri veya host isimleri gibi bilgileri içerir. Ansible bu dosyayı kullanarak hedef sistemlere bağlanır ve belirli görevleri gerçekleştirir.
```bash
[webserver]
10.244.155.113 ansible_connection=local 
```
Bu iki dosya, Ansible'ın etkili bir şekilde çalışabilmesi için önemlidir. ansible.cfg dosyası genellikle Ansible'ın genel yapılandırmasıyla ilgili ayarları içerirken, inventory.txt dosyası hedef sistemlerin tanımlandığı yerdir. Bu dosyaları doğru şekilde yapılandırmak, Ansible'ı kullanmaya başlamak için temel bir adımdır. 
```bash
# UYARI: Aşağıdaki komutu inventory.txt dosyasının bulunduğu yerde giriniz.
# IP adresiniz farklı olacağı için bu komut yardımıyla inventory.txt dosyasını güncelleyin.

echo -e "[webserver]\n$(hostname -I | tr -s ' ' '\n' | head -n 1) ansible_connection=local" > inventory.txt
```
Projemizde Docker, Kubernetes, Prometheus, Node Exporter, Grafana, Jaeger yüklemeleri ve gerekli configurasyon ayarlamaları ansible playbook dosyaları yazılarak yapılacaktır. 
Playbook, belirli bir hedef üzerindeki bir dizi otomasyon görevini tanımlayan, okunabilir bir YAML dosyasıdır. Playbook'lar, Ansible ile sistem yapılandırma, uygulama dağıtımı, güvenlik güncelleştirmeleri ve diğer otomasyon görevlerini gerçekleştirmek için kullanılır. Playbook'lar genellikle birden çok rolü ve görevi bir araya getirerek belli bir hedef üzerinde kapsamlı bir otomasyon sağlar.

Playbook dosyaları oluşturulurken görevlerine ve amaçlarına göre 3 farklı playbook şeklinde oluşturuldu. Bunlar;

kubernetes_docker_config.yml adındaki ilk çalıştırılacak playbook, kubernetes cluster kurulumu, docker kurulumu ve gerekli paket yüklemelerini yapıyor.
```bash
---
- name: Ubuntu 22.04 K3s Kurulumu
  hosts: webserver
  become: true  

  tasks:
    - name: Sistem Güncelleme
      ansible.builtin.apt:
        upgrade: yes
        update_cache: yes

    - name: Python3 ve Pip Yükle
      ansible.builtin.apt:
        name:
          - python3
          - python3-pip
      become: true

    - name: Docker'i Yükle
      ansible.builtin.shell: "pip3 install docker"
      become: true

    - name: curl yükle
      ansible.builtin.apt:
        name:
          - curl
      become: true

    - name: K3s Kurulum Komutunu Calistir
      ansible.builtin.shell: "curl -sfL https://get.k3s.io | sh -"
      become: true

    - name: 10 Saniye Bekle
      ansible.builtin.pause:
        seconds: 10

    - name: Kubectl Get Nodes Komutunu Calistir
      ansible.builtin.shell: "kubectl get nodes"
      become: true
      register: kubectl_output

    - name: Debug - Kubectl Output
      ansible.builtin.debug:
        var: kubectl_output.stdout_lines
```
prometheus_grafana_nodeexporter.yml adındaki ikinci çalıştırılacak playbook, kubernetes clusterdan metric bilgilerini
çekebilmek için prometheus kurulumunu, nodelara agent kurulumunu gerçekleştirmek için node exporter kurulumunu ve bu bilgileri
görselleştirmek için grafana kurulumu yapıyor.
```bash
---
- name: Prometheus, Grafana ve Node Exporter Kurulumu
  hosts: webserver
  become: true

  tasks:
    - name: Prometheus için gerekli paketleri yükle
      apt:
        name: "{{ item }}"
        state: present
      loop: 
        - prometheus

    - name: Ek depo için apt-transport-https yükle
      apt:
        name: apt-transport-https
        state: present

    - name: Grafana'nin APT anahtarini ekleyin
      apt_key:
        url: https://packages.grafana.com/gpg.key
        state: present

    - name: Grafana APT deposunu ekleyin
      apt_repository:
        repo: deb https://packages.grafana.com/oss/deb stable main
        state: present

    - name: Grafana için gerekli paketleri yükle
      apt:
        name: "{{ item }}"
        state: present 
      loop:
        - grafana

    - name: Node Exporter için gerekli paketleri yükle
      apt:
        name: "{{ item }}"
        state: present
      loop:
        - prometheus-node-exporter

    - name: Prometheus servisini başlat ve başlangiçta otomatik olarak başlatilmasini sağla
      systemd:
        name: prometheus
        state: started
        enabled: yes

    - name: Grafana servisini başlat ve başlangiçta otomatik olarak başlatilmasini sağla
      systemd:
        name: grafana-server
        state: started
        enabled: yes

    - name: Node Exporter servisini başlat ve başlangiçta otomatik olarak başlatilmasini sağla
      systemd:
        name: prometheus-node-exporter
        state: started
        enabled: yes
```
jaeger.yml adındaki son çalıştırılacak playbook, performans sorunlarını tanımlamamıza, hataları ayıklamamıza ve kullanıcı deneyimini geliştirmemize yardımcı olan bir dağıtık izleme aracı kurulumunu gerçekleştirmekte.
```bash
--- 
- name: Jaeger Kurulumu
  hosts: webserver
  become: true
  vars:
    ansible_python_interpreter: /usr/bin/python3
  tasks:
    - name: Jaeger'i baslat
      community.docker.docker_container:
        name: jaeger-container
        image: jaegertracing/all-in-one:latest
        ports:
          - "8080:16686"
          - "9411:9411" 
        detach: true

    - name: HotROD örneğini baslat
      community.docker.docker_container: 
        name: jaeger-hotrod-container
        image: jaegertracing/example-hotrod:latest
        ports:
          - "8081:8080"
        detach: true
``` 
Playbook dosyalarını tek bir playbook dosyası halinde yazılabiliyor. Ancak bu projede amaçlarına ve görevlerine göre 3 farklı playbook olarak  yazılmıştır. Burda yapılmak istenen amaç farklı projelere bu playbookları entegre edilebilir halde bırakmak.
```bash
# Aşağıdaki komutlar ile playbooklarımızı çalıştıralım.

ansible-playbook -i inventory.txt kubernetes_docker_config.yml

ansible-playbook -i inventory.txt prometheus_grafana_nodeexporter.yml

ansible-playbook -i inventory.txt jaeger.yml
```
Prometheus'un web arayüzüne erişmek için ```9090``` portuyla gidebilirsiniz.

Node Exportur web arayüzüne erişmek için ```9100``` portuyla erişip, ```Metrics``` seçeneğine tıklayarak bilgilere ulaşabilirsiniz.

Grafana web arayüzüne erişmek için ```3000``` portuyla erişip, ```admin``` kullanıcı ve ```admin``` parola girişiyle giriş yapabilirsiniz. 

Grafana' da kullanıcı görselliği sağlamak için prometheus' u tanımlamamız ve dashboard oluşturmamız gerekir. Bunun için aşağıdaki adımları uygulayınız;
```bash
Hamburger menüde bulunan; Connections --> Data sources --> Add data source --> Prometheus

Name : Prometheus
Prometheus server URL * : http://localhost:9090
Save

Dashboard eklemek için; Home --> Dashboards --> New Altında bulunan Import 

Dashboard ID: 1860  --> Load
Select a Prometheus data source --> Prometheus --> Import
```
Jaeger web arayüzüne erişmek için tarayıcınızı kullanarak ```8080``` portunu ziyaret edebilirsiniz. Aynı şekilde, HotROD uygulamasında veri oluşturmak içinse ```8081``` portunu kullanabilirsiniz. Bu sayede Jaeger'ın izleme yeteneklerini test edebilirsiniz.

### Kaynak Kodu

Flask uygulaması, MySQL veritabanında keypair yönetim sistemi sunan backend ve frontend den oluşan bir uygulamadır.. /add /update /delete ve /search endpointleri sunarak kullanıcıya temel CRUD işlemlerini gerçekleştirmek için bir arayüz sunar. Backend servisi create, delete ve update işlemleri için gerekli web sayfalarını sunar. Frontend servisi ise read işlemleri için bir arama sayfası sağlar.
```bash 
Flask Uygulaması Dosya Yapısı

|-- result_server       
|   |-- Dockerfile      
|   |-- app.py
|   |-- requirements.txt
|   |-- static
|   |   |-- backgrounds.jpg
|   |   |-- tt.png
|   |   `-- ttbb.png       
|   `-- templates
|       |-- index.html
|       `-- login.html
`-- web_server        
    |-- Dockerfile    
    |-- app.py        
    |-- requirements.txt
    |-- static
    |   |-- backgrounds.jpg
    |   |-- tt.png
    |   `-- ttbb.png
    `-- templates
        |-- add-update.html
        |-- delete.html
        |-- index.html
        `-- login.html
```
### Dockerfile

Backend ve frontend kaynak kodları için iki ayrı Dockerfile dosyası oluşturuldu. Bu dosyalardan image'lar build edildi ve DockerHub'a muslumhanozturk/web:latest  ve muslumhanozturk/result:latest olarak gönderildi.
```bash 
FROM python:alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD python ./app.py
```
### Kubernetes

Kubernetes cluster içinde backend, frontend ve database image larından pod lar oluşturmam gerekiyor. Bu podları, deployment ve replicaset objeleriyle birlikte ayağa kaldırmam gerekiyor. 

**Deployment**, Replicaset'i yöneten bir denetleyicidir. Replicaset, belirli bir sayıda aynı özelliklere sahip Pod'un çalışmasını sağlar. Pod'lar, uygulamanın çalıştığı objelerdir. Yani, Deployment, istenilen Pod sayısını belirler, Replicaset bu sayıyı sürdürür ve bu Pod'lar uygulamayı çalıştırır.

**Persistent Volume**, uygulamaların verilerini saklamak için kullanılan bir depolama objesidir. Kalıcı veri depolaması sağlar ve uygulamalar yeniden başlasa bile veriler korunmasını sağlar.

**Persistent Volume Claim**, uygulamalar PV yi talep eder, bu talep üzerine uygun bir PV ile eşleştirilir ve veriler kalıcı olarak saklanır.

**Secret**, parolalar, token ve ssh anahtarları gibi hassas bilgileri depolamanıza ve yönetmenize olanak tanır. Kubernetes te en güvenli yöntemlerden biridir. Base64 encode edilerek saklanır. Bunun yanında ayar yaparsak etcd üzerinde encrypt durabilir.

**Configmap**, gizli olmayan verileri anahtar/değer çiftleri olarak depolamak için kullanılan objedir.

**Service**, Bir dizi pod üzerinde çalışan bir uygulamayı ağ hizmeti olarak göstermenin soyut bir yolu. Kubernetes, pod'lara kendi IP adreslerini ve bir dizi pod için tek bir DNS adı verir ve bunlar arasında yük dengeleyebilir.

**NGINX Ingress Controller**,  Ingress, HTTP ve HTTPS gibi uygulama protokollerine dayalı istekleri yönlendirmek için kullanılır. YAML dosyasındaki örnekte, HTTP protokolü kullanıldığı için bu Ingress kaynağı L7 katmanında çalışmaktadır. http alanı, kural setlerini ve belirli HTTP yollarını içerir.

Bu Ingress kaynağı, gelen isteklerin belirli URL yollarına göre yönlendirilmesini sağlar. Bizim uygulamamızda / yolundaki istekler bir servise, /result yolundaki istekler ise başka bir servise yönlendirilir.  
```bash 
Kubernetes manifest dosya yapısı

|-- database_configmap.yaml
|-- ingress.yaml
|-- mysql-secret.yaml      
|-- mysql_deployment.yml   
|-- mysql_service.yaml     
|-- persistent_volume.yaml 
|-- persistent_volume_claim.yaml
|-- result_server_deployment.yml
|-- result_server_service.yaml  
|-- servers_configmap.yaml      
|-- web_server_deployment.yml
`-- web_server_service.yaml 
```
Kubernetes yaml dosyalarını çalıştırmak için aşağıdaki komutu kullanabilirsiniz.
```bash 
kubectl apply -f manifest_files/
```
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