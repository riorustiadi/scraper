---
source: https://help-center.talenta.co/hc/id/articles/51294417204761-Bagaimana-Cara-Menyusun-dan-Mengelola-Salary-Structure
title: Bagaimana Cara Menyusun dan Mengelola Salary Structure
article_id: 51294417204761
---

Fitur **Salary Structure** pada Mekari Talenta HRIS memberikan kemudahan bagi Anda dalam menyusun struktur upah sesuai dengan ketentuan Permenaker Nomor 10 Tahun 2017. Melalui fitur ini, Anda dapat membuat laporan berdasarkan tahun dan komponen gaji, sehingga apabila pada sistem telah tersedia salary history atas komponen tertentu di tahun yang sama, data riil tersebut dapat langsung ditarik untuk menyusun struktur upah.

Namun demikian, Anda juga tetap dapat membuat *salary structure* meskipun belum terdapat [riwayat gaji](https://help-center.talenta.co/hc/id/articles/18882874548121) pada sistem. Untuk saat ini, tujuan utama dari fitur ini adalah menghasilkan laporan yang dapat digunakan sebagai bahan audit maupun perencanaan keuangan perusahaan.

Berikut adalah langkah-langkah menyusun hingga mengelola *salary structure*.

## A. Membuat Salary Structure

1. Pergi ke menu **Payroll** lalu pilih **Salary structure**.
2. Klik **“Create salary structure”** untuk membuat struktur gaji.
3. Kemudian, Anda dapat mengisi halaman form pertama, yaitu **Structure information**.

|  |  |  |
| --- | --- | --- |
| **No.** | **Nama Tombol/Kolom** | **Deskripsi** |
| 1 | Structure name | Isi dengan nama struktur gaji. Contohnya, ‘Salary structure for Customer Support and Marketing 2024’. |
| 2 | Payroll component | Pilih komponen gaji yang ingin Anda susun strukturnya, di antaranya adalah **Basic salary, All allowances, All benefits,** atau **Custom component**. Pada contoh di atas, dipilih Basic salary.  Pilihan komponen **akan memengaruhi** ***field*** apa saja yang dapat diatur di halaman form ketiga, yaitu **Calculation method & structure**. |
| 3 | Period | Pilih periode tahun payroll. Pada contoh di atas, dipilih 2024. |
| 4 | Description | Isi penjelasan tentang struktur gaji ini jika diperlukan (opsional). |

4. Apabila sudah terisi, Anda dapat lanjut mengisi form berikutnya dengan klik **“Continue”**.
5. Pada halaman form kedua, Anda dapat mengisi **Criteria & salary benchmark**. Tentukan kriteria struktur gaji berdasarkan **Branch** dan **Organization (wajib)**. Anda dapat menambahkan kriteria selain Branch dan Organization dengan klik **“Add criteria”**.
6. Selanjutnya, Anda dapat secara **opsional** menerapkan fitur **Salary benchmark** untuk menetapkan skala gaji yang kompetitif secara kustom ke dalam strukur gaji dengan klik **“Insert salary benchmark”**. Anda dapat mengunduh *template*-nya dengan klik **“Download template”,** lalu isikan benchmark atau kisaran dan rata-rata gaji sesuai dengan kebijakan perusahaan Anda dan menyimpan *file*nya. Lalu, unggah *file* yang sudah terisi tersebut dengan klik **“Browse”**.
7. Setelah selesai melengkapi form dan pengaturan form halaman kedua ini, Anda dapat lanjut ke form halaman ketiga dengan klik **“Continue”**.
8. Pada form ketiga ini, Anda dapat melengkapi **Calculation method & structure** di mana bagian pertamanya adalah **Calculation method**.

|  |  |  |
| --- | --- | --- |
| **No.** | **Nama Tombol/Kolom** | **Deskripsi** |
| 1 | Configure salary range calculation | Aktifkan tombol ini untuk menentukan jumlah kisaran minimal dan maksimalnya gaji aktual dan target. |
| 2 | Spread percentage | Pilih metode ini apabila Anda ingin menentukan kisaran gaji berdasarkan KEPMEN 49 Tahun 2004. Metode ini akan memengaruhi **Review structure** yang akan dijelaskan pada poin 9a. |
| 3 | Actual salary target percentile | Pilih metode ini apabila Anda ingin menentukan kisaran gaji berdasarkan gaji aktual yang didapatkan dari data Mekari Talenta. Metode ini akan memengaruhi **Review structure** yang akan dijelaskan pada poin 9b.  Keterangan:   1. Centang **Apply target for all minimum salary range** untuk menentukan angka (%) kolom target **Minimum salary target** agar diterapkan ke seluruh karyawan dengan kriteria yang telah Anda tentukan sebelumnya secara massal. 2. Centang **Apply target for all mid-salary range** untuk menentukan angka (%) kolom target **Mid-salary target** agar diterapkan ke seluruh karyawan dengan kriteria yang telah Anda tentukan sebelumnya secara massal. 3. Centang **Apply target for all maximum salary range** untuk menentukan angka (%) kolom target **Maximum salary target** agar diterapkan ke seluruh karyawan dengan kriteria yang telah Anda tentukan sebelumnya secara massal. |
| 4 | Custom amount | Pilih metode ini apabila Anda ingin menentukan kisaran gaji berdasarkan gaji minimal, mid, hingga maksimal secara kustom. Metode ini akan memengaruhi **Review structure** yang akan dijelaskan pada poin 9c. |

9. Kemudian, Anda dapat melengkapi bagian **Review structure**.  
   a. Apabila sebelumnya Anda memilih **method** **Spread percentage**, maka Anda dapat menentukan kisaran gaji berdasarkan KEPMEN 49 Tahun 2004 pada kolom **Spread** yang akan sistem secara otomatis kalkulasikan di kolom **Actual min., mid., max salary**.

   Berdasarkan contoh di atas, karena berdasarkan kriteria **Organization** yang telah dipilih di halaman form kedua, maka yang ditampilkan merupakan Organization berikut. Kemudian, ditentukan **Spread** **15%** untuk **Sales & Marketing** dan **20%** untuk **Marketing**.

   b. Apabila sebelumnya Anda memilih **method Actual salary target percentile**, maka Anda dapat menyusun struktur gaji dari gaji aktual yang didapatkan dari data Mekari Talenta yang tercantum pada masing-masing kolom yang tidak dapat diubah datanya. Pada kolom **Min. salary target (%), Mid. salary target (%) dan Max. salary target,** Anda dapat menyusun target gaji secara kustom atau berdasarkan penerapan massal yang telah Anda lakukan di langkah pada poin 8 tabel nomor 3.

   Berdasarkan contoh di atas, karena berdasarkan kriteria **Organization** yang telah dipilih di halaman form kedua, maka yang ditampilkan merupakan Organization berikut. Kemudian, ditentukan **Min. salary target (%) 10%, Mid. salary target (%) 10% dan Max. salary target 10%**.

   c. Apabila sebelumnya Anda memilih **method** **Custom amount**, maka Anda dapat menentukan kisaran gaji secara kustom pada kolom **Min., mid., max salary target (Rp)** dalam jumlah Rupiah secara langsung seperti pada contoh berikut.
10. Jika target seluruh pengaturan hingga struktur gaji sudah sesuai dengan jumlah yang Anda inginkan, klik **“Save”**.

## B. Mengelola Salary Structure yang Telah Dibuat

1. Setelah Anda menyimpan struktur gaji, maka Anda akan diarahkan ke halaman **Salary structure**. Di sini, terdapat daftar seluruh struktur gaji yang telah Anda buat. Kemudian, Anda dapat mengelola data-data tersebut seperti yang akan dijelaskan berikut ini.

|  |  |  |
| --- | --- | --- |
| **No.** | **Nama Tombol/Kolom** | **Deskripsi** |
| 1 | Filter | Klik untuk menerapkan filter berdasarkan komponen atau periode gaji. |
| 2 | Download Salary Structure index | Klik untuk mengunduh daftar *Salary structure* yang pernah Anda buat berdasarkan filter yang telah Anda terapkan. |
| 3 | Search structure name | Cari *Salary structure* tertentu berdasarkan kata kunci yang Anda masukkan di kolom ini. |
| 4 | Actions | Klik untuk melakukan tindakan tertentu terhadap *Salary structure*, seperti **View details, Lock structure, Send report, Download report, Edit structure,** dan **Delete Structure** yang akan dijelaskan di poin-poin berikutnya.  **Penting** Tindakan **Edit** dan **Delete structure** tidak dapat dilakukan terhadap *Salary structure* yang dikunci **(Lock)**. |

2. Apabila Anda memilih **Actions - View details**, maka Anda akan diarahkan ke halaman rincian *Salary structure*. Pada halaman ini, Anda dapat klik **“Actions”** untuk melakukan tindakan **Lock structure, Send report, Download report, Edit structure,** dan **Delete Structure.** Selain itu, Anda dapat mengunduh rincian ini dengan klik **“Download”**.
3. Apabila Anda memilih **Actions - Lock structure** untuk mengunci susunan struktur gaji ini, maka Anda tidak akan dapat melakukan **Edit** dan **Delete structure.** Klik **“Lock structure”** pada *pop up* yang muncul untuk menerapkan.

   Dengan diterapkannya pengaturan ini, status struktur gaji yang telah Anda kunci akan berubah menjadi **Locked**.
4. Apabila Anda memilih **Actions - Send report** untuk mengirimkan laporan salary structure, maka Anda dapat memilih siapa saja karyawan yang akan mendapatkan laporan ini di kolom **Select employee**. Klik **“Send”** untuk mengirimkan laporan tersebut ke nama-nama karyawan terpilih.
5. Apabila Anda memilih **Actions - Download report,** maka Anda akan mendapatkan pesan laporan **Salary structure** pada menu **Inbox Talenta**.

Demikian panduan cara menyusun dan mengelola *Salary Structure*. Selanjutnya, Anda dapat mempelajari panduan cara melihat laporan *payroll*, [di sini.](https://help-center.talenta.co/hc/id/articles/40669391137561)



---
source: https://help-center.talenta.co/hc/id/articles/51035280784537-Case-Study-Contract-and-Probation
title: Case Study - Contract and Probation
article_id: 51035280784537
---

|  |  |
| --- | --- |
| Contract & Probation: Membuat Template Form Penilaian pada Masa Percobaan/Kontrak (Studi Kasus #1) | Contract & Probation: Menyusun Siklus Evaluasi Kinerja Karyawan (Studi Kasus #2) |
| Contract & Probation: Melakukan Penilaian di Masa Percobaan/Kontrak sebagai Reviewer (Studi Kasus#3) | Contract & Probation: Menghasilkan Laporan Penilaian Evaluasi Karyawan (Studi Kasus #4) |



---
source: https://help-center.talenta.co/hc/id/articles/50768908382617-Bagaimana-Cara-Mengundang-Karyawan-sebagai-role-Employee-untuk-Menggunakan-Talenta-LMS
title: Bagaimana Cara Mengundang Karyawan sebagai role Employee untuk Menggunakan Talenta LMS
article_id: 50768908382617
---

Talenta LMS *(Learning Management System)* merupakan perangkat lunak yang digunakan untuk merancang, menjalankan, serta mengevaluasi suatu proses pembelajaran. Untuk membuat sebuah *course* di Mekari Talenta LMS, Super Admin perlu menentukan *role* di dalam LMS. Contohnya, ***role*** **Admin** memiliki tanggung jawab untuk **mengelola LMS, seperti akses karyawan, konten pembelajaran serta** ***progress*****-nya** dan hal-hal lain terkait. Sedangkan, ***role*** **Employee** memiliki tanggung jawab untuk [**mengerjakan dan menyelesaikan** ***course***.](https://help-center.talenta.co/hc/id/articles/50168290887321)

**Penting**  
Untuk berlangganan fitur ini dan mengintegrasikannya ke Mekari Talenta HRIS, Anda dapat menghubungi tim support kami dengan mengirimkan email ke [support-hr@mekari.com](mailto:support-hr@mekari.com).

Pada panduan ini, akan dijelaskan langkah-langkah mengundang karyawan sebagai***role*** **Employee** untuk menggunakan Talenta LMS.

1. Untuk mengakses Talenta LMS, Anda dapat masuk ke akun Talenta Anda. Kemudian klik **“HRIS”** pilih **LMS Backyard**.
2. Setelah berhasil masuk ke akun Anda, Anda dapat masuk ke menu **Settings** dan pilih submenu **Users**.
3. Kemudian, klik tombol **“Create data”**.
4. Pilih nama karyawan yang ingin diundang pada kolom **Employees**.
5. Kemudian, pilih **Role** karyawan sebagai **Employee**. Setelah itu, klik **“Invite user”**.
6. Maka, nama karyawan yang telah Anda undang *(invite)* akan muncul di daftar. Anda dapat mengubah akses karyawan tersebut dengan klik **“Edit”** atau klik **“Remove”** untuk menghapus karyawan.
7. Anda juga dapat melihat kuota karyawan yang telah diundang pada submenu **User quota**.
8. Contoh pada gambar berikut terdapat 9 karyawan yang telah diundang dari total 9999.

Demikian panduan cara mengundang karyawan untuk menggunakan Mekari Talenta LMS. Selanjutnya, Anda dapat mempelajari cara membuat dan menerbitkan *course*, [di sini.](https://help-center.talenta.co/hc/id/articles/50166612266009)



---
source: https://help-center.talenta.co/hc/id/articles/50542194748569-Case-Study-Performance-Appraisal
title: Case Study - Performance Appraisal
article_id: 50542194748569
---

|  |  |
| --- | --- |
| Performance Appraisal: Menyusun KPI & Goal Karyawan di Mekari Talenta (Studi Kasus #1) | Performance Appraisal: Memperbarui Pencapaian KPI di Mekari Talenta (Studi Kasus #2) |
| Performance Appraisal: Membuat Template Review di Mekari Talenta (Studi Kasus #3) | Performance Appraisal: Membuat Review Cycle di Mekari Talenta (Studi Kasus #4) |
| Performance Appraisal: Proses Pengisian hingga Penyerahan Review di Mekari Talenta (Studi Kasus #5) | Performance Appraisal: Menghasilkan Laporan KPI dan Review dengan Mekari Talenta (Studi Kasus #6) |
