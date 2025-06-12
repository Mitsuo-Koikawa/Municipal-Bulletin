FROM mcr.microsoft.com/azure-functions/python:4-python3.10

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY mcp_server/ /home/site/wwwroot/
COPY csv /home/site/wwwroot/csv
COPY docs/index.json /home/site/wwwroot/docs/index.json

RUN pip install -r /home/site/wwwroot/requirements.txt

