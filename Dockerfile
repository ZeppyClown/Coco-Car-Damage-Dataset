FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY scripts ./scripts
COPY alembic ./alembic
COPY alembic.ini .
# Manual assistant: code plus the development notes and public summaries it indexes at start (one library, one folder).
COPY ["car mechanic assistant/src", "car mechanic assistant/src"]
COPY ["car mechanic assistant/templates", "car mechanic assistant/templates"]
COPY ["car mechanic assistant/static", "car mechanic assistant/static"]
COPY ["car mechanic assistant/web_app.py", "car mechanic assistant/workshop_policy.md", "car mechanic assistant/"]
COPY ["car mechanic assistant/knowledge_base", "car mechanic assistant/knowledge_base"]
COPY ["car mechanic assistant/public_reference_corpus", "car mechanic assistant/knowledge_base/public_reference_corpus"]
ENV CHROMA_PERSIST_DIRECTORY=runtime/releases/hosted
RUN python scripts/generate_training_data.py && python scripts/train_intent_simple.py
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3)"
# Bring the database up to date, start the assistant's library build if switched on, then serve. Hosts put HTTPS in
# front and pass the real address in headers.
CMD ["scripts/start_hosted.sh"]
