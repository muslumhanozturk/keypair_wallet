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