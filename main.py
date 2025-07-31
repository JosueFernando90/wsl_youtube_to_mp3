from yt_dlp import YoutubeDL
import os
from urllib.parse import urlparse, parse_qs, urlunparse

def limpar_url_suja(url):
    """
    Recebe uma URL do YouTube possivelmente "suja" (com parâmetros extras) e retorna
    somente a URL básica com ?v=VIDEO_ID.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    video_id = query.get('v')
    if not video_id:
        # Se não encontrar parâmetro v, retorna url original (ou pode tratar como inválida)
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
                ydl.download([url_limpa])
            except Exception as e:
                print(f"Erro no download de {url_limpa}: {e}")
                erros.append(f"{url_limpa} - {e}")

    if erros:
        with open('log_erros.txt', 'w', encoding='utf-8') as f:
            for linha in erros:
                f.write(linha + '\n')
        print(f"Alguns downloads falharam. Veja 'log_erros.txt' para detalhes.")
    else:
        print("Todos os downloads foram concluídos com sucesso!")

if __name__ == '__main__':
    urls_sujas = [
        "https://www.youtube.com/watch?v=azdwsXLmrHE&list=RDazdwsXLmrHE&start_radio=1",
        "https://www.youtube.com/watch?v=BF-yWPdQUmY&list=RDBF-yWPdQUmY&start_radio=1",
        "https://www.youtube.com/watch?v=CbFNwokMbG8&list=RDBF-yWPdQUmY&index=3",
        "https://www.youtube.com/watch?v=lk_EXr9xEr0&list=RDBF-yWPdQUmY&index=6",
        "https://www.youtube.com/watch?v=YB-qGRuSpsA&list=RDBF-yWPdQUmY&index=12"
        # ... cole todas as URLs sujas aqui ...
    ]
    baixar_youtube_para_mp3(urls_sujas, pasta_destino="./meus_mp3s")
