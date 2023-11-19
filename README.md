Bulut hizmet sağlayıcılarında kullanılan servislere erişim için access key, secret key ve keypair.pem dosyalarını oluşturmak genellikle uygulanan bir yöntemdir. Ancak bu özel anahtar dosyalarını sadece lokal bilgisayarımızda saklamak, Bulut Hizmet Sağlayıcılarına sadece kendi bilgisayarımızdan erişim sağlama yeteneğimizi sınırlar. Bu dosyaların silinmesi veya farklı bir bilgisayardan erişim sağlama ihtiyacı ortaya çıktığında, her seferinde yeni anahtarlar oluşturmak zaman kaybına neden olabilir. 

Özellikle acil durumlarda, müşteri sunucusuna hızlı müdahale yapabilmek için bu anahtar dosyalarına hızla erişim sağlamak kritik öneme sahiptir. Müşteri anlaşmalarında belirtilen ciddi ücret ve cezaların önlenmesi için bu süreç hızlı ve etkili bir şekilde gerçekleştirilmelidir. 

Bu nedenle, bu süreci optimize etmek için anahtar dosyalarını güvenli bir şekilde depolamak, gerektiğinde hızlı erişim sağlamak ve yeni anahtarlar oluşturma sürecini kolaylaştırmak için bir strateji oluşturmak önemlidir. Bu, iş sürekliliğini sağlamak ve acil durum müdahalelerini en aza indirmek için hayati bir adımdır. 

Keypair Wallet adını verdiğim projede Ansible, Docker, Kubernetes, Prometheus, Grafana, Jaeger, Jenkins gibi DevOps araçlarının yanı sıra Python, HTML, SQL Database, Nginx gibi teknolojiler ve Slack bildirimleri de aktif olarak kullanılmaktadır. 

Şimdi sizlerle bu projeyi daha yakından inceleyip adım adım ilerleyerek uygulayalım.  
 
GitHub repodan gerekli uygulama dosyalarını kendi çalışma alanımıza çekelim.
```bash
git clone https://github.com/muslumhanozturk/keypair_wallet.git 

cd keypair_wallet/  
```
Ansible Kurulumu

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


