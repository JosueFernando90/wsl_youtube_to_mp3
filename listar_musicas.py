import os
import pandas as pd

# Caminho da pasta onde estão os arquivos MP3
folder = './meus_mp3s/'

# Lista para armazenar os caminhos dos arquivos MP3
mp3_files = []

# Caminhar pela pasta e procurar arquivos .mp3
for root, dirs, files in os.walk(folder):
    for file in files:
        if file.lower().endswith('.mp3'):
            # Adiciona o caminho completo do arquivo
            mp3_files.append(os.path.join(root, file))

# Verificar se encontramos arquivos MP3
if mp3_files:
    # Criar um DataFrame com a lista de arquivos
    df = pd.DataFrame(mp3_files, columns=["Caminho do arquivo MP3"])
    
    # Salvar o DataFrame em um arquivo Excel
    df.to_excel('mp3_files.xlsx', index=False)
    print("Arquivo Excel criado com sucesso: mp3_files.xlsx")
else:
    print("Nenhum arquivo MP3 encontrado na pasta.")
