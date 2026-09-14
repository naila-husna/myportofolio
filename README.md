Nama: Naila Husna Teguh Suasono

NPM: 2506620444
Kelas: PBP A

## Tugas 1

Tugas pertama dalam mata kuliah Pemrograman Bebasis Platform yang meminta mahasiswa untuk mengembangkan hasil dari portofolio yang telah dibuat di tutorial 1 yang dilakukan di lab

### Intruksi Penggunaan
1. Pastikan Python sudah terinstal pada perangkat.
2. Buka terminal pada direktori proyek.
3. Aktifkan virtual environment dengan perintah: env\Scripts\activate
4. Jalankan website dengan perintah: python manage.py runserver
5. Setelah berhasil dijalankan, buka browser dan akses link yang tertera
6. Tekan Ctrl+C apabilang ingin menghentikan server

### Jawaban Pertanyaan Reflektif
1. Saya menggunakan elemen semantik HTML5, terutama <section> dan <article>. Di tugas 1 ini, saya memanfaatkan <section> sebagai pembagi halaman menjadi beberapa bagian, seperti profile, formal education, dan work experiences. Tak hanya itu,saya juga menggunakan <article> agar tiap item memiliki informasi yang bisa berdiri dengan sendirinya. Saya merasa dengan menggunakan elemen semantik, membuat portofolio saya lebih terstruktur. Struktur tersebut juga sangat membantu saya dalam implementasi css, karena tiap section jadi bisa memiliki template css yang berbeda.

2. Tantangan yang saya temui saat membuat tampilan responsive adalah pada saat mengatur perubahan layout dari desktop ke layar yang lebih kecil. Apabila dalam kondisi ukuran tidak diubah, bagian Profile menggunakan CSS Grid dengan dua kolom (informasi dan foto profile side-to-side). Sedangkan pada bagian education, saya seperti menggunakan sebuah timeline, dan dalam bagian experience, saya menggunakan 3 kolom yg membagi work experiences saya. Karena keterbatasan ukuran pada mobile, maka saya menggunakan media query untuk mengubah profile menjadi satu kolom, experiences menjadi satu card perbaris, serta menyesuaikan lebar timeline dan card education. Dalam proses menentukan mana yang harus didahulukan, saya memilih apakah isi portofolio saya dapat terbaca terlebih dahulu, karena saya ingin mendahulukan bahwa pesan yang ingin saya sampaikan ini tersampaikan dengan baik

3. Karena untuk tugas ini masih menggunakan static web, seluruh informasi yang saya sampaikan saya tulis langsung di HTML. Pada tugas ini, portofolio saya juga belum bisa menerima input ataupun memberikan output. Oleh karena itu, untuk kedepannya saya ingin membuat data menjadi lebih dinamis tanpa mengubah HTML secara lgsg dan saya juga ingin merapihkan code saya sedikit lagi

### Penggunaan AI
Dalam pengerjaan tugas ini, saya menggunakan ChatGPT sebagai alat bantu proses pengembangan website, karena saya merasa masih sangat awam dengan HTML. AI saya gunakan untuk memastikan struktur HTML, membantu memberikan ide untuk styling, serta memberikan arahan ketika ada masalah pada tampilan website. Tetapi, tentunya saran-saran dari ChatGPT tidak saya terima secara mentah-mentah, saya juga memodifikasikan kembali agar sesuai dengan desain yang saya inginkan.

## Tugas 2
1. Ketika user membuka page Education lewat navbar, browser akan mengirimkan request ke URL /education/. Request tersebut akan diproses oleh urls.py pada portofolio/urls.pt yang akan meneruskan ke main/urls.py. Yang selanjutnya akan diteruskan ke view show_education, yang kemudian mengambil seluruh data dari model Education dengan Education.objects.all(), kemudian memasukkannya ke context dengan education_list, yang akhirnya akan diteruskan ke education.html. Di dalam template, Django dengan DTL akan melakukan perulangan terhadap education_list, sehingga tiap object yang ada di education_list tampil secara dinamis. Jika tidak ada data, {% empty %} akan menampilkan pesan bahwa data pendidikan belum tersedia. Setelah proses rendering selesai, Django mengirim HTML sebagai response kembali ke browser.

2. Karena model memisahkan data dari tampilan HTML. Dengan ini, saya dapat dengan mudah meng-edit data-data yang ada tanpa harus membuat elemen HTML baru dengan manual. Dengan adanya template, portofolio saya lebih mudah untuk dipelihara karena perubahan data tidak mengharuskan perubahan struktur tampilan

3. makemigrations digunakan untuk mendeteksi perubahan pada model Django dan membuat file migration yang berisi instruksi perubahan struktur database. Sementara itu, migrate digunakan untuk menerapkan file migration tersebut ke database sehingga struktur database benar-benar berubah. Contohnya adalahh ketika saya menambahkan model baru Education dengan field institution, program, start_year, end_year, dan activities. Saya me-running python manage.py migrate agar tabel agar 0003_education.py dibuat oleh Django, yang dilanjutkan dengan menjalankan python manage.py migrate agar tabel untuk model Education benar-benar dibuat di database

### Penggunaan AI

Dalam pengerjaan Tugas 2, saya menggunakan ChatGPT (GPT-5.6 Sol) sebagai alat bantu saya untuk lebih memahami materi dan juga debugging, serta membantu menganalisis permasalahan ketika implementasi yang saya inginkan tidak sesuai. Saya tidak meminta AI untuk lgsg memberikan solusi untuk seluruh tugas. Pada sesi ini, sayameminta AI unruk membimbing saya dalam proses pengerjaannya dan saya meminta AI untuk menjelaskan materi lebih dalam. Saya juga memberikan dokumen soal dan tutorial sebagai acuan agar AI tidak melebihi dari batasan yang diminta oleh tugas.

Dengan strategi iteratif, pada awalnya saya meminta ChatGPT secara eksplisit untuk jangan membantu saya memberikan jawaban, alih-alih membimbing saya dengan mengikuti tutorial 2. Setelah mencoba sendiri, saya menghadapi masalah bahwa tampilan css saya tidak dapat berubah, jadi saya bertanya mengenai kemungkinan yang dapat terjadi sebagai kemungkinan alasan ketidakbisaan saya mengubah css. ChatGPT membantu saya pada beberapa bagian terutama dalam css dan mendalami unit testing dalam Django

Implementasi tetap saya lakukan sendiri, pemilihan keseluruhan tetap saya yang memutuskan, AI hanya sebatas alat mempertimbangkan dan debugging saja

Log chat: https://chatgpt.com/share/6aa7a5db-62a8-83ec-97ba-e2a7c440fd0d
