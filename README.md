# AQG-summary

untuk menjalankan project ini memerlukan beberapa setup

1. clone repository
unduh repository ke dalam perangkat dengan perintah:
- https://github.com/coconato04/AQG-summary.git

2. membuat environment untuk framework django, berikut caranya:
- python -m venv ENV
- ENV\Scripts\activate

setelah ENV aktif, maka dilanjutkan instalasi dependencies menggunakan txt yang telah disediakan dengan perintah:

- pip install -r requirements.txt

3. Migrasi
setelah selesai dengan instalasi maka lanjutkan dengan migrasi database dengan perintah:

- python manage.py migrate
