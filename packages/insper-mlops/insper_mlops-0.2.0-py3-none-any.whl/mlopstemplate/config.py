"""Configurações e utilitários para autenticação e templates do MLOps Template."""

import os
from typing import Optional

# URLs dos templates para cada perfil
TEMPLATE_REPO_URL = "https://github.com/centro-dados-ia/cdiaTemplateMlops.git"
TEMPLATE_REPO_URL_PESQUISA = "https://github.com/Insper-CDIA-Pesquisa/cdiaTemplateMlops.git"

TOKEN_ENV_VAR = "GITHUB_TOKEN"
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".mlops_token")
TEAMS_WEBHOOK_URL = os.environ.get("MLOPS_TEAMS_WEBHOOK")


def set_session_token(token: str):
    """Armazena o token do GitHub como uma variável de ambiente para a sessão atual."""
    os.environ[TOKEN_ENV_VAR] = token


def save_token(token: str):
    """Salva o token do GitHub em um arquivo de configuração local."""
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    # Tenta restringir permissões de leitura/escrita apenas para o dono
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass  # Ignora erros de permissão em sistemas incompatíveis


def get_token() -> Optional[str]:
    """
    Obtém o token do GitHub, priorizando a variável de ambiente da sessão.
    Se não encontrar, busca no arquivo de configuração local.
    """
    # 1. Prioriza o token da sessão (variável de ambiente)
    token = os.environ.get(TOKEN_ENV_VAR)
    if token:
        return token

    # 2. Se não houver, tenta ler do arquivo
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()

    return None
