FROM python:3.13-slim

WORKDIR /app

ARG USERNAME=appuser

ARG HOST_UID=1000

ARG HOST_GID=${HOST_UID}

COPY . .

RUN groupadd --gid $HOST_GID $USERNAME \
	&& useradd --uid $HOST_UID --gid $HOST_GID -m $USERNAME \
	&& chown -R $HOST_UID:$HOST_GID /app \
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
		sqlite3

USER $USERNAME

RUN pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/bot.py"]
