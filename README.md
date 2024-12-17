# AQG-summary

untuk menjalankan project ini memerlukan beberapa setup

1. clone repository
unduh repository ke dalam perangkat dengan perintah:
- https://github.com/coconato04/AQG-summary.git
- cd AQG-summary

2. membuat environment untuk framework django, berikut caranya:
- python -m venv ENV
- ENV\Scripts\activate

setelah ENV aktif, maka dilanjutkan instalasi dependencies menggunakan txt yang telah disediakan dengan perintah:

- pip install -r requirements.txt


3. masuk ke project
setelah instalasi selesai maka diharuskan terlebih dahulu untuk masuk ke dalam project dengan perintah:

- cd AQG


4. Migrasi
setelah masuk ke dalam project maka lanjutkan dengan migrasi database dengan perintah:

- python manage.py migrate


5. menjalankan server
jalankan server lokal untuk mengakses project:

- python manage.py runserver

di terminal akan ditampilkan sebuah akses website program dengan link lokal: http://127.0.0.1:8000 


penjelasan lebih lanjut terkait fungsi dan fitur yang ada di dalam website dapat dilihat melalui buku panduan manual website yang berjudul: 535210014_MANUALBOOK.pdf