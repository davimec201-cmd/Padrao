# Imagem do diagramador. O WeasyPrint precisa de Pango, Cairo e amigos — é por
# isso que o serviço roda em Docker no Render, e não no runtime Python padrão.
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# libpango + libharfbuzz: texto; libcairo/libgdk-pixbuf: desenho e imagem;
# fontconfig: é o que faz o @font-face das fontes da marca ser encontrado;
# shared-mime-info: detecção de tipo dos assets.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz0b \
        libharfbuzz-subset0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libffi8 \
        fontconfig \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ordem pensada para o cache: o que muda pouco entra primeiro
COPY assets/ ./assets/
COPY design/ ./design/
COPY FORMATO.md ./
COPY exemplo/ ./exemplo/
COPY diagramador/ ./diagramador/

# confere na hora do build que as fontes da marca estão embutidas de verdade —
# a falha silenciosa do @font-face já aconteceu uma vez e não acontece de novo
RUN python3 diagramador/ferramentas/verificar_fontes.py

EXPOSE 10000
ENV PORT=10000

CMD ["sh", "-c", "uvicorn diagramador.app.principal:app --host 0.0.0.0 --port ${PORT} --workers 1 --timeout-keep-alive 75"]
