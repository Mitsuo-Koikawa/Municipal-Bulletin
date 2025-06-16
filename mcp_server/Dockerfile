FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Install gh CLI and models extension
RUN apt-get update && \
    apt-get install -y git curl && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    gh extension install github/gh-models && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY mcp_server/ /home/site/wwwroot/
COPY csv /home/site/wwwroot/csv
COPY docs/index.json /home/site/wwwroot/docs/index.json

RUN pip install -r /home/site/wwwroot/requirements.txt

