import os
import pandas as pd
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs, urlunparse
import re

# Função para limpar a URL do YouTube e obter apenas o ID do vídeo
def limpar_url_suja(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # Extrair o 'v' (ID do vídeo) e garantir que é o único parâmetro necessário
    video_id = query.get('v')
    if not video_id:
        return url  # Retorna a URL original se não houver 'v'
    
    video_id = video_id[0]
    clean_query = f"v={video_id}"  # Limpa a query, mantendo apenas o ID do vídeo
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', clean_query, ''))
    return clean_url


# Função para obter o título de um vídeo no YouTube
def obter_titulo_video(url, log_erro):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Título não encontrado')
            return title
        except Exception as e:
            # Registrar o erro no log
            with open(log_erro, 'a', encoding='utf-8') as f:
                f.write(f"Erro ao obter título para {url}: {str(e)}\n")
            return None

# Função para remover duplicatas e registrar as duplicatas removidas em um log
def remover_duplicatas_preservando_ordem(urls, log_duplicatas):
    urls_unicas = []
    urls_vistas = set()
    duplicatas = []

    for url in urls:
        if url not in urls_vistas:
            urls_unicas.append(url)
            urls_vistas.add(url)
        else:
            duplicatas.append(url)
    
    # Se houver duplicatas, registrar no log
    if duplicatas:
        with open(log_duplicatas, 'a', encoding='utf-8') as f:
            f.write("URLs duplicadas removidas:\n")
            for url in duplicatas:
                f.write(f"{url}\n")
            f.write("\n")

    return urls_unicas

# Função principal para ler o arquivo, limpar as URLs e pegar os títulos
def processar_urls_para_excel(arquivo_urls, arquivo_excel='titulos_videos.xlsx', log_erro='log_erros.txt', log_duplicatas='log_duplicatas.txt'):
    # Criar ou limpar o arquivo de log antes de começar
    with open(log_erro, 'w', encoding='utf-8') as f:
        f.write("Log de erros de extração de títulos:\n")

    with open(log_duplicatas, 'w', encoding='utf-8') as f:
        f.write("Log de URLs duplicadas removidas:\n")
    
    # Ler URLs do arquivo
    try:
        with open(arquivo_urls, 'r', encoding='utf-8') as f:
            urls_lidas = [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        print(f"Arquivo '{arquivo_urls}' não encontrado. Por favor, crie o arquivo com uma URL por linha.")
        return

    # Verificar as URLs lidas antes de limpar
    print(f"URLs lidas: {len(urls_lidas)}")
    print("URLs lidas (antes de limpar):")
    for url in urls_lidas:
        print(url)

    # Limpar URLs duplicadas e limpar cada uma, mantendo a ordem
    urls_limpa_unicas = remover_duplicatas_preservando_ordem([limpar_url_suja(url) for url in urls_lidas], log_duplicatas)

    # Verificar as URLs após limpeza e remoção de duplicatas
    print(f"URLs após limpeza e remoção de duplicatas: {len(urls_limpa_unicas)}")
    print("URLs após limpeza e remoção de duplicatas:")
    for url in urls_limpa_unicas:
        print(url)

    # Obter títulos e URLs limpas dos vídeos
    dados = []
    for i, url in enumerate(urls_limpa_unicas, 1):
        print(f"Processando ({i}/{len(urls_limpa_unicas)}): {url}")
        titulo = obter_titulo_video(url, log_erro)
        if titulo:
            url_limpa = limpar_url_suja(url)
            dados.append([titulo, url_limpa])  # Adiciona título e URL limpa

    # Salvar os dados em um arquivo Excel
    if dados:
        df = pd.DataFrame(dados, columns=["Título do Vídeo", "URL Limpa"])
        df.to_excel(arquivo_excel, index=False)
        print(f"🎉 Títulos e URLs salvos com sucesso em '{arquivo_excel}'!")
    else:
        print("❌ Não foi possível obter títulos para nenhum dos vídeos.")

if __name__ == '__main__':
    # Especificar o nome do arquivo com as URLs
    processar_urls_para_excel('urls.txt')
