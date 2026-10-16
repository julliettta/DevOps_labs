# ===== ХОРОШИЙ DOCKERFILE =====

# --- Стадия 1: builder. Здесь ставим зависимости ---
# GOOD 1: версия базового образа зафиксирована (+ slim вместо полного)
FROM python:3.12.7-slim-bookworm AS builder
WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# GOOD 2: порядок слоёв под кеш. Сначала только requirements.txt,
#         и слой с pip меняется только при изменении зависимостей.
COPY requirements.txt .
# GOOD 3: --no-cache-dir, чтобы кеш pip не раздувал образ
RUN pip install --no-cache-dir -r requirements.txt

# --- Стадия 2: финальный образ ---
# GOOD 4: multi-stage. В финал едет только готовое окружение, без сборочного мусора.
FROM python:3.12.7-slim-bookworm
# GOOD 5: отдельный непривилегированный пользователь
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1

# Код копируем последним, потому что он меняется чаще всего
COPY app.py .

USER appuser
EXPOSE 5000

# GOOD 6: HEALTHCHECK (без curl, на стандартной библиотеке Python)
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# GOOD 7: боевой сервер gunicorn вместо dev-сервера Flask
CMD ["gunicorn", "--preload", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
