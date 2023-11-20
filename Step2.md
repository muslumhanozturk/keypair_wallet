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