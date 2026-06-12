from django.shortcuts import render
from .models import Pelamar, Kriteria, Penilaian, Soal
from django.shortcuts import redirect

def dashboard(request):
    total_pelamar = Pelamar.objects.count()
    total_kriteria = Kriteria.objects.count()
    
    context = {
        'total_pelamar': total_pelamar,
        'total_kriteria': total_kriteria,
    }
    return render(request, 'recruitment/dashboard.html', context)

def hitung_bobot_gap(gap):
    # Tabel Bobot Nilai GAP sesuai standar Profile Matching
    tabel_bobot = {
        0: 5,     # Kompetensi sesuai (No GAP)
        1: 4.5,   # Kelebihan 1 tingkat
        -1: 4,    # Kekurangan 1 tingkat
        2: 3.5,   # Kelebihan 2 tingkat
        -2: 3,    # Kekurangan 2 tingkat
        3: 2.5,   # Kelebihan 3 tingkat
        -3: 2,    # Kekurangan 3 tingkat
        4: 1.5,   # Kelebihan 4 tingkat
        -4: 1     # Kekurangan 4 tingkat
    }
    return tabel_bobot.get(gap, 1)

def proses_profile_matching(request):
    semua_pelamar = Pelamar.objects.all()
    kriteria_list = Kriteria.objects.all()
    hasil_ranking = []

    for pelamar in semua_pelamar:
        nilai_cf = []
        nilai_sf = []
        
        for kriteria in kriteria_list:
            # Ambil nilai yang diinput di admin untuk pelamar ini
            penilaian = Penilaian.objects.filter(pelamar=pelamar, kriteria=kriteria).first()
            if penilaian:
                # 1. Hitung GAP (Nilai Aktual - Nilai Target/Standar)
                gap = penilaian.nilai_aktual - kriteria.nilai_standar
                
                # 2. Konversi GAP ke Bobot
                bobot = hitung_bobot_gap(gap)
                
                # 3. Kelompokkan ke Core atau Secondary Factor
                if kriteria.jenis_faktor == 'Core':
                    nilai_cf.append(bobot)
                else:
                    nilai_sf.append(bobot)
        
        # 4. Hitung Rata-rata NCF dan NSF
        ncf = sum(nilai_cf) / len(nilai_cf) if nilai_cf else 0
        nsf = sum(nilai_sf) / len(nilai_sf) if nilai_sf else 0
        
        # 5. Hitung Nilai Total (Misal: 60% Core, 40% Secondary)
        nilai_total = (0.6 * ncf) + (0.4 * nsf)
        
        hasil_ranking.append({
            'nama': pelamar.nama,
            'ncf': round(ncf, 2),
            'nsf': round(nsf, 2),
            'total': round(nilai_total, 2)
        })

    # 6. Urutkan berdasarkan nilai total tertinggi (Ranking)
    hasil_ranking = sorted(hasil_ranking, key=lambda x: x['total'], reverse=True)

    return render(request, 'recruitment/hasil_ranking.html', {'ranking': hasil_ranking})

def pendaftaran(request):
    kriteria_list = Kriteria.objects.all()
    
    if request.method == 'POST':
        # 1. Simpan Data Pelamar
        nama = request.POST.get('nama')
        posisi = request.POST.get('posisi')
        pendidikan = request.POST.get('pendidikan')
        
        pelamar = Pelamar.objects.create(
            nama=nama, 
            posisi_dilamar=posisi, 
            pendidikan_terakhir=pendidikan
        )
        
        # 2. Simpan Nilai Kriteria ke Tabel Penilaian
        for kriteria in kriteria_list:
            nilai = request.POST.get(f'kriteria_{kriteria.id}')
            if nilai:
                Penilaian.objects.create(
                    pelamar=pelamar,
                    kriteria=kriteria,
                    nilai_aktual=int(nilai)
                )
        
        return redirect('ranking') # Setelah daftar, langsung lihat hasil ranking

    return render(request, 'recruitment/pendaftaran.html', {'kriteria_list': kriteria_list})

def persiapan_ujian(request):
    """Fungsi khusus pendaftaran jalur ujian CBT (Tanpa input nilai manual)"""
    if request.method == 'POST':
        nama = request.POST.get('nama')
        posisi = request.POST.get('posisi')
        pendidikan = request.POST.get('pendidikan')
        
        pelamar = Pelamar.objects.create(
            nama=nama, 
            posisi_dilamar=posisi, 
            pendidikan_terakhir=pendidikan
        )
        
        # Simpan ID pelamar di session lalu lempar ke halaman soal
        request.session['pelamar_id'] = pelamar.id
        return redirect('ujian')

    return render(request, 'recruitment/persiapan_ujian.html')

def ujian(request):
    """Fungsi untuk menampilkan soal CBT dan otomatis hitung nilai"""
    pelamar_id = request.session.get('pelamar_id')
    if not pelamar_id:
        return redirect('persiapan_ujian')
        
    pelamar = Pelamar.objects.get(id=pelamar_id)
    semua_soal = Soal.objects.all().select_related('kriteria')
    kriteria_list = Kriteria.objects.all()

    if request.method == 'POST':
        skor_benar = {kriteria.id: 0 for kriteria in kriteria_list}
        
        # Hitung jawaban benar
        for soal in semua_soal:
            jawaban_user = request.POST.get(f'soal_{soal.id}')
            if jawaban_user == soal.kunci_jawaban:
                skor_benar[soal.kriteria.id] += 1
        
        # Konversi jumlah benar ke Nilai Aktual (Skala 1-5)
        for kriteria in kriteria_list:
            jumlah_benar = skor_benar[kriteria.id]
            # Asumsi tiap kriteria punya maksimal 5 soal. Jika 0, minimal dapat 1.
            nilai_aktual = max(1, min(5, jumlah_benar)) 
            
            Penilaian.objects.create(
                pelamar=pelamar,
                kriteria=kriteria,
                nilai_aktual=nilai_aktual
            )
        
        # Hapus session selesai ujian
        del request.session['pelamar_id']
        return redirect('ranking')

    return render(request, 'recruitment/ujian.html', {'semua_soal': semua_soal, 'pelamar': pelamar})