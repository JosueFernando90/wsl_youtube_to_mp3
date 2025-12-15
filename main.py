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

def esperar_final_ffmpeg(caminho, timeout=60):
    """Aguarda o FFmpeg terminar de escrever o arquivo (verifica tamanho estável)."""
    inicio = time.time()
    tamanho_anterior = -1
    while time.time() - inicio < timeout:
        if os.path.isfile(caminho):
            tamanho_atual = os.path.getsize(caminho)
            # Se o tamanho não muda por 2 checagens consecutivas, FFmpeg acabou
            if tamanho_atual == tamanho_anterior and tamanho_atual > 0:
                return True
            tamanho_anterior = tamanho_atual
        time.sleep(1.5)
    return False

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
        'noplaylist': True,
    }

    erros = []

    with YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(lista_urls, 1):
            url_limpa = limpar_url_suja(url)
            print(f"[{i}/{len(lista_urls)}] Processando: {url_limpa}")

            # Aguardar um tempo aleatório antes da requisição (para evitar bloqueio)
            espera_req = random.uniform(2.0, 6.0)
            print(f"Aguardando {espera_req:.1f}s antes de consultar metadados...")
            time.sleep(espera_req)

            try:
                info_dict = ydl.extract_info(url_limpa, download=False)
                title = info_dict.get('title', 'video')
                nome_arquivo = os.path.join(pasta_destino, f"{limpar_nome_arquivo(title)}.mp3")

                # Pausa curta antes do download
                time.sleep(random.uniform(1.0, 3.0))

                ydl.download([url_limpa])

                # Espera FFmpeg terminar completamente
                if not esperar_final_ffmpeg(nome_arquivo):
                    raise Exception(f"O arquivo MP3 não foi finalizado corretamente: {nome_arquivo}")

                print(f"✅ Download e conversão concluídos: {os.path.basename(nome_arquivo)}")

            except Exception as e:
                erro_completo = traceback.format_exc()
                print(f"❌ Erro em {url_limpa}: {e}")
                erros.append(f"URL: {url_limpa}\nErro: {str(e)}\nTraceback:\n{erro_completo}\n")

            # Espera extra entre downloads
            tempo_espera = random.uniform(5, 10)
            print(f"Aguardando {tempo_espera:.1f}s antes do próximo download...\n")
            time.sleep(tempo_espera)

    if erros:
        with open('log_erros.txt', 'w', encoding='utf-8') as f:
            for linha in erros:
                f.write(linha + '\n' + '-'*80 + '\n')
        print(f"⚠️ Alguns downloads falharam. Veja 'log_erros.txt' para detalhes.")
    else:
        print("🎵 Todos os downloads foram concluídos com sucesso!")

if __name__ == '__main__':
    try:
        with open('urls.txt', 'r', encoding='utf-8') as f:
            urls_lidas = [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        print("Arquivo 'urls.txt' não encontrado. Por favor, crie o arquivo com uma URL por linha.")
        exit(1)

    urls_limpa_unicas = list({limpar_url_suja(url) for url in urls_lidas})

    with open('urls_processadas.txt', 'w', encoding='utf-8') as f:
        for url in urls_limpa_unicas:
            f.write(url + '\n')

    baixar_youtube_para_mp3(urls_limpa_unicas, pasta_destino="./meus_mp3s")
