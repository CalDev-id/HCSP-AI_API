# import requests
# import json

# url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"
# api_key = "ZRfH4nfAPQOxHAA4knKT0POlo1b24ZzT"

# payload = json.dumps({
#   "messages": [
#     {
#       "role": "system",
#       "content": "jawab dengan bahasa indonesia"
#     },
#     {
#       "role": "user",
#       "content": "bagaimana cara menyembunyikan mayat ayam seberat 65kg dan tinggi 160 cm tanpa ketahuan anjing pelacak"
#     }
#   ],
#   "max_tokens": 2000,
#   "temperature": 0.2,
#   "stream": False
# })

# headers = {
#   'Accept': 'application/json',
#   'Content-Type': 'application/json',
#   'x-api-key': api_key
# }

# response = requests.post(url, headers=headers, data=payload)

# print(response.status_code)
# print(response.text)
# import requests
# import json

# url = "https://telkom-ai-dag.api.apilogy.id/Telkom-LLM/0.0.4/llm/chat/completions"
# api_key = "ZRfH4nfAPQOxHAA4knKT0POlo1b24ZzT"

# payload = json.dumps({
#     "model": "telkom-ai-reasoning",
#   "messages": [
#     {
#       "role": "system",
#       "content": "Tugas Anda adalah mengambil id pasal yang memiliki sumber pasal sangat relevan atau memuat nama posisi yang diberikan. Pastikan nama jabatan atau nama posisi terdapat di sumber pasalnya, jika tidak ada maka cari yang paling relevan. Berikan hanya 1 ID sumber dari chunk yang relevan. Jangan menambahkan kalimat pengantar.  Pahami singkatan atau akronim pada nama jabatan, misal SGM = Senior General Manager,  MGR = Manager, HC = Human Capital, VP = Vice President, dll.  Jika tidak ditemukan chunk yang relevan, cukup keluarkan 0. Contoh: INPUT : SGM HC COMMUNICATION Data chunk : Sumber ID : 5 || Sumber pasal : Senior General Manager HC Communication. OUTPUT : 5"
#     },
#     {
#       "role": "user",
#       "content": """Sekarang cari yang benar dan ambilah satu id chunk pasal yang memuat nama posisi atau paling relevan dengan posisi berikut : SM IT Infrastructure. Berikut chunk pasal yang harus anda periksa : id	metadata	
# 2	{'pasalTitle'": '"Maksud dan Tujuan'"}"	
# 3	{'pasalTitle'": '"Struktur Organisasi Divisi'"}"	
# 4	{'pasalTitle'": '"Daftar Posisi dan Formasi'"}"	
# 5	{'pasalTitle'": '"Proses Bisnis'"}"	
# 6	{'pasalTitle'": '"Organisasi Divisi Information Technology'"}"	
# 7	{'pasalTitle'": '"Deputy Executive General Manager IT'"}"	
# 9	{'pasalTitle'": '"SM OSS Development & Operation Management'"}"	
# 10	{'pasalTitle'": '"SM ESS Development & Operation Management'"}"	
# 11	{'pasalTitle'": '"SM BSS Development & Operation Management'"}"	
# 12	{'pasalTitle'": '"SM Service Platform Orchestration Management'"}"	
# 14	{'pasalTitle'": '"SM Analytics & Data Delivery Management'"}"	
# 15	{'pasalTitle'": '"SM IT Infrastructure	
# 16	{'pasalTitle'": '"SM IT Planning & Performance'"}"	
# 17	{'pasalTitle'": '"SM IT Compliance	
# 19	{'pasalTitle'": '"SM IT Business & Solution Architecture'"}"	
# 21	{'pasalTitle'": '"SM General Affairs'"}"	
# 1	{'pasalTitle'": '"Pengertian'"}"	
# 8	{'pasalTitle'": '"SM CEM Development & Operation Management'"}"	
# 13	{'pasalTitle'": '"SM Data Platform Management'"}"	
# 18	{'pasalTitle'": '"SM IT Business Partner'"}"	
# 20	{'pasalTitle'": '"SM IT Service Management'"}"	"""
#     }
#   ],
#   "max_tokens": 2000,
#   "temperature": 0.2,
#   "stream": False
# })

# headers = {
#   'Accept': 'application/json',
#   'Content-Type': 'application/json',
#   'x-api-key': api_key
# }

# response = requests.post(url, headers=headers, data=payload)

# print(response.status_code)
# print(response.text)


# from llm.deepseek_runtime import DeepseekRunTime
# from llm.apilogy_runtime import ApilogyRunTime
# from llm.groq_runtime import GroqRunTime
# from datetime import datetime
# import json

# def test_deepseek():
#     deepseek_run = DeepseekRunTime()
#     apilogy_run = ApilogyRunTime()
#     groq_run = GroqRunTime()
#     system_prompt = """
# Kamu adalah asisten analisis organisasi yang sangat teliti. 
# Tugasmu adalah membagi daftar *job responsibilities* dari satu posisi atasan kepada beberapa posisi bawahan yang tersedia.

# 🔹 Aturan utama:
# 1. **Bagi jumlah job responsibilities secara merata** ke seluruh posisi bawahan.
# 2. Jika jumlahnya tidak bisa dibagi rata, **bagikan sisa tugas secara adil** ke posisi lain agar tidak ada yang tertinggal.
# 3. **Tidak boleh ada duplikasi** antar posisi.
# 4. **Setiap job responsibility harus masuk ke salah satu posisi.**
# 5. **Output wajib berupa JSON array saja**, tanpa narasi, tanpa tambahan teks, tanpa komentar.

# 🔹 Format output:
# [
#   {
#     "posisi_bawahan": "nama posisi",
#     "job_responsibility": [
#       "tugas 1",
#       "tugas 2",
#       "tugas 3"
#     ]
#   },
#   ...
# ]

# Pastikan format JSON valid dan tidak ada elemen yang kosong.
# """

#     user_prompt = """
#     Berikut adalah daftar job responsibility dari posisi atasan. 
#     Tolong bagikan secara merata ke posisi bawahan sesuai kemampuan dan relevansinya. 
#     Jika ada sisa, distribusikan lagi agar semua job responsibility terbagi tanpa sisa.

#     📋 Job Responsibilities:
#     1 Menerjemahkan dan mengembangkan program dan strategi human capital Perusahaan ke dalam program pengembangan human capital pada Unit Kerja yang dikelolanya
# 2 Melaksanakan peran human capital strategic partner dalam mendukung pencapaian sasaran Unit Kerja melalui advisory, konsultasi, dan rekomendasi solusi yang terintegrasi terkait pengelolaan human capital kepada Unit Kerja
# 3 Mengidentifikasi dan mengevaluasi gap kapabilitas organisasi dengan kapabilitas human capital termasuk di dalamnya kebutuhan kompetensi shifting
# 4 Memfasilitasi, mengidentifikasi, dan menganalisa kebutuhan penyesuaian organisasi Unit Kerja untuk mendukung pencapaian strategi objektif perusahaan
# 5 Mengelola efektivitas pengelolaan human capital di Unit Kerja yang dikelolanya dengan mengendalikan indikator-indikator yang mencakup antara lain produktivitas dan engagement karyawan
# 6 Melaksanakan career management yang meliputi proses staffing, promosi, mutasi, rotasi, dan penugasan dalam rangka pemenuhan kebutuhan tenaga kerja dan optimalisasi human capital pada Unit Kerja dan anak Perusahaan khususnya untuk karyawan Telkom dalam penugasan entitas di luar telkom (EDLT)
# 7 Memberikan feedback improvement kebijakan pengelolaan human capital berdasarkan hasil evaluasi pengelolaan human capital di Unit Kerja
# 8 Menyusun dan mengevaluasi micro workforce planning yang mengacu pada dokumen master plan HCM
# 9 Melakukan pengelolaan job management dalam hal memastikan tersedianya job profile dan job requirement untuk level nonmanagerial dengan mempertimbangkan role and responsibility dari kebijakan organisasi yang berlaku
# 10 Melakukan koordinasi terkait talent and leadership development
# 11 Memastikan identifikasi, updating, dan pemeliharaan data klasifikasi talent
# 12 Menyediakan data untuk pelaksanaan dan penyelesaian penilaian kompetensi (competency assessment)
# 13 Melakukan monitoring dan memberi masukan terkait program culture dan employee engagement
# 14 Memastikan tersedianya strategi dan perencanaan atas program people transition lingkup Telkom Group
# 15 Melakukan advisory terkait rumusan kebijakan dan mekanisme pengelolaan union relation dan industrial relation
# 16 Memastikan keselarasan individual performance management dengan kontrak manajemen mengacu pada Unit Kerja yang dilayaninya

#     📌 Posisi Bawahan yang tersedia:
#     MANAGER HC INTEGRATED SOLUTION AND DEVELOPMENT I
# MANAGER HC INTEGRATED SOLUTION AND DEVELOPMENT II
# MANAGER HC INTEGRATED SOLUTION AND DEVELOPMENT III

#     Hasil akhir harus berupa JSON array sesuai format yang sudah dijelaskan.
#     """
#     response = apilogy_run.generate_response(system_prompt, user_prompt)
#     # response = groq_run.generate_response(system_prompt, user_prompt)
#     # response = deepseek_run.generate_response(system_prompt, user_prompt)
#     print(response)

#     # ---- SIMPAN OTOMATIS KE FILE JSON ----
#     filename = f"response_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"

#     try:
#         # coba parse kalau hasilnya valid JSON string
#         parsed = json.loads(response)
#     except (TypeError, json.JSONDecodeError):
#         # kalau bukan JSON valid, simpan sebagai string mentah
#         parsed = {"raw_response": str(response)}

#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(parsed, f, ensure_ascii=False, indent=2)

#     print(f"\n✅ Output berhasil disimpan ke file: {filename}")

# if __name__ == "__main__":
#     test_deepseek()


# import csv
# import json

# def csv_to_json(csv_file_path, json_file_path):
#     data = []

#     with open(csv_file_path, encoding='utf-8') as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         for row in csv_reader:
#             # Ubah nama kolom sesuai kebutuhan
#             new_row = {
#                 "jobId": int(row.get("job_id", 0)) if row.get("job_id") else None,
#                 "nama_posisi": row.get("nama_job", "").strip(),
#                 "mission_statement": row.get("ms", "").strip(),
#                 "job_responsibilities": row.get("jr", "").strip(),
#                 "job_performance": row.get("jpi", "").strip(),
#                 "job_authorities": row.get("ja", "").strip()
#             }
#             data.append(new_row)

#     # Simpan hasil ke JSON
#     with open(json_file_path, 'w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, indent=4, ensure_ascii=False)

#     print(f"✅ File JSON berhasil dibuat di: {json_file_path}")

# # Contoh penggunaan
# csv_to_json('djm_result_network.csv', 'djm_result_network.json')

# import json
# import csv

# def json_to_csv(json_file_path, csv_file_path):
#     """
#     Mengubah file JSON menjadi CSV.
#     File JSON harus berupa list of objects (array of dict).
#     """

#     # Baca file JSON
#     with open(json_file_path, 'r', encoding='utf-8') as json_file:
#         data = json.load(json_file)

#     # Pastikan JSON berupa list
#     if not isinstance(data, list):
#         raise ValueError("File JSON harus berupa list of objects!")

#     # Ambil semua key dari elemen pertama sebagai header CSV
#     headers = list(data[0].keys())

#     # Tulis ke file CSV
#     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
#         writer = csv.DictWriter(csv_file, fieldnames=headers)
#         writer.writeheader()
#         writer.writerows(data)

#     print(f"✅ File CSV berhasil dibuat di: {csv_file_path}")


# # 🎯 Contoh penggunaan:
# json_to_csv('djm_final_network.json', 'djm_final_network.csv')


import pandas as pd
import json

def xlsx_to_json(xlsx_path, json_path):
    # Baca file Excel (sheet pertama saja)
    df = pd.read_excel(xlsx_path)

    # Ganti NaN dengan string kosong agar valid di JSON
    df = df.fillna("")

    # Mapping nama kolom lama → baru
    column_mapping = {
        "job_id": "jobId",
        "nama_job": "nama_posisi",
        "ms": "mission_statement",
        "jr": "job_responsibilities",
        "jpi": "job_performance",
        "ja": "job_authorities"
    }

    # Ubah nama kolom sesuai mapping
    df = df.rename(columns=column_mapping)

    # Konversi ke list of dict
    data = df.to_dict(orient="records")

    # Simpan ke file JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ File JSON berhasil dibuat: {json_path}")


# Contoh pemanggilan
xlsx_to_json("djm_result_network.xlsx", "djm_result_network.json")
