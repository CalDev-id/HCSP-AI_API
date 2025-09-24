from typing import List
from llm.apilogy_runtime import ApilogyRunTime

def ms_agent(nama_posisi: str, band_posisi: str, retrieve_data: List[str]):
    apilogy_run = ApilogyRunTime()
    
    context_text = "\n\n".join(retrieve_data) if retrieve_data else "Tidak ada konteks pasal relevan."

    user_prompt = f"""
    sekarang, buatkan mission statement untuk posisi berikut :

Nama Posisi : {nama_posisi}


Mission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya, tanpa penanda seperti (-/*), dan tidak dibold !

Buatkan mission statement untuk posisi berikut: \n\n Nama Posisi: {nama_posisi} dengan band posisi nya : {band_posisi} \n\n Mission Statement hanya berupa teks narasi langsung sebutkan misinya tanpa ada kata pengantarnya LANGSUNG MISI DIA APA TAK USAH SEBUT NAMA POSISI, langsung diawali kata kerja nya, tanpa penanda seperti (-/*), dan tidak dibold! Berikut konteks yang dapat anda gunakan untuk membentuk MS dari posisi tersebut :{context_text}
    """

    system_prompt = f"""
Kamu adalah asisten AI HC yang membantu membuat mission statement untuk suatu posisi.\n\nTugas:\n1. Pahami informasi mengenai posisi dan band (SGM = BAND 1, SM = BAND 2).\n2. Jika posisi memiliki BAND (BP) I atau II:\n   - Gunakan context yang diberikan user untuk mencari informasi relevan.\n   - Jawab 3 pertanyaan: untuk apa posisi ini ada, apa kontribusinya, dan strategi/unit apa yang didukung.\n   - Susun jawaban jadi satu paragraf mission statement.\n3. Output hanya mission statement dalam bentuk teks narasi langsung, tanpa pengantar, tanpa penanda (-/*), dan tidak dibold.

"""
    response = apilogy_run.generate_response(system_prompt, user_prompt)

    if response and "choices" in response:
        mission_statement = response["choices"][0]["message"]["content"].strip()
        print(mission_statement)
        return mission_statement
    else:
        print("Tidak ada respons dari AI.")
        return ""