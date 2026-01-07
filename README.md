### Instalação FFMPEG
sudo apt update
sudo apt install -y ffmpeg

### Verificação
ffmpeg -version
ffprobe -version

## Verificar se está no PATH
which ffmpeg
which ffprobe

## Teste rápido manual (opcional, mas recomendado)
### Primeiro
ffmpeg -f lavfi -i sine=frequency=1000:duration=3 teste.mp3

### Depois
ls -lh teste.mp3
