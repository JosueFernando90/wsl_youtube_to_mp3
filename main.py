import os
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs, urlunparse
import traceback
import time
import random
import re

def limpar_nome_arquivo(titulo):
    return re.sub(r'[\\/*?:"<>|]', "", titulo)

def limpar_url_suja(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    video_id = query.get('v')
    if not video_id:
        return url
    video_id = video_id[0]
    clean_query = f"v={video_id}"
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', clean_query, ''))
    return clean_url

def baixar_youtube_para_mp3(lista_urls, pasta_destino='./meus_mp3s'):
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta '{pasta_destino}' criada.")
    else:
        print(f"Pasta '{pasta_destino}' já existe. Continuando...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    erros = []

    with YoutubeDL(ydl_opts) as ydl:
        for url in lista_urls:
            url_limpa = limpar_url_suja(url)
            print(f"Processando: {url_limpa}")
            try:
                info_dict = ydl.extract_info(url_limpa, download=False)
                title = info_dict.get('title', 'video')
                nome_arquivo = os.path.join(pasta_destino, f"{limpar_nome_arquivo(title)}.mp3")

                ydl.download([url_limpa])

                if not os.path.isfile(nome_arquivo):
                    raise Exception(f"Arquivo mp3 não encontrado após download: {nome_arquivo}")

            except Exception as e:
                erro_completo = traceback.format_exc()
                print(f"Erro no download/conversão de {url_limpa}: {e}")
                erros.append(f"URL: {url_limpa}\nErro: {str(e)}\nTraceback:\n{erro_completo}\n")

            # Evitar excesso de solicitações
            tempo_espera = random.uniform(3, 7)  # entre 3 e 7 segundos
            print(f"Aguardando {tempo_espera:.1f} segundos antes do próximo download...\n")
            time.sleep(tempo_espera)


    if erros:
        with open('log_erros.txt', 'w', encoding='utf-8') as f:
            for linha in erros:
                f.write(linha + '\n' + '-'*80 + '\n')
        print(f"Alguns downloads falharam. Veja 'log_erros.txt' para detalhes.")
    else:
        print("Todos os downloads foram concluídos com sucesso!")

if __name__ == '__main__':
    try:
        with open('urls.txt', 'r', encoding='utf-8') as f:
            urls_lidas = [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        print("Arquivo 'urls.txt' não encontrado. Por favor, crie o arquivo com uma URL por linha.")
        exit(1)

    # Limpar URLs e remover duplicatas com base na versão limpa
    urls_limpa_unicas = list({limpar_url_suja(url) for url in urls_lidas})

    with open('urls_processadas.txt', 'w', encoding='utf-8') as f:
        for url in urls_limpa_unicas:
            f.write(url + '\n')

    baixar_youtube_para_mp3(urls_limpa_unicas, pasta_destino="./meus_mp3s")


