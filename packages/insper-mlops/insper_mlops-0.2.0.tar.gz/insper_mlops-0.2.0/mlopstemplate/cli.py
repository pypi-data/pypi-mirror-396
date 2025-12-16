"""Command-line interface for the MLOps Template tool."""

import os
import subprocess

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from mlopstemplate import config, core

app = typer.Typer(
    help="🚀 Ferramenta de linha de comando para padronizar e automatizar projetos de MLOps no Insper.",
    add_completion=False,
)
console = Console()

def _print_header():
    """Imprime o cabeçalho estilizado da aplicação."""
    console.print(
        Panel.fit(
            "[bold blue]Insper MLOps CLI[/bold blue]\n"
            "[italic]Padronizando o desenvolvimento de IA[/italic]",
            border_style="blue",
            padding=(1, 2),
        )
    )

def get_token_from_gh_cli() -> str:
    """
    Retrieves the GitHub authentication token from the GitHub CLI.

    This function first checks if the user is authenticated. If not, it
    initiates the interactive login process for the user to authenticate.

    Returns:
        The GitHub authentication token.

    Raises:
        typer.Exit: If the GitHub CLI is not installed or if the login
                    process fails.
    """
    # 1. Verifica se o GitHub CLI (gh) está instalado
    try:
        subprocess.run(
            ["gh", "--version"], capture_output=True, check=True, text=True
        )
    except FileNotFoundError:
        console.print(
            "[bold red]❌ GitHub CLI (gh) não encontrado. "
            "Instale em https://cli.github.com/ e tente novamente.[/bold red]"
        )
        raise typer.Exit(code=1)

    # 2. Tenta obter o token silenciosamente
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    # 3. Se não houver token, inicia o processo de login interativo
    console.print(
        Panel(
            "[bold yellow]🔐 GitHub CLI não está autenticado.[/bold yellow]\\n\\n"
            "Iniciando processo de login interativo. "
            "Por favor, siga as instruções no seu terminal e navegador.",
            title="Ação Necessária",
            border_style="yellow",
        )
    )

    try:
        subprocess.run(["gh", "auth", "login"], check=True)
    except subprocess.CalledProcessError:
        console.print(
            "[bold red]❌ O processo de login com o GitHub CLI falhou ou foi cancelado.[/bold red]"
        )
        raise typer.Exit(code=1)

    # 4. Após o login, tenta obter o token novamente
    console.print("✅ [bold green]Autenticação concluída.[/bold green] Verificando token...")
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    else:
        console.print(
            "[bold red]❌ Falha ao obter o token após o login. "
            "Por favor, tente 'mlops login' novamente.[/bold red]"
        )
        raise typer.Exit(code=1)


@app.command(hidden=True)
def login(
    temp: bool = typer.Option(
        False, "--temp-login", help="Login temporário, não salva token em arquivo"
    )
):
    """
    Authenticates the user via GitHub CLI and saves the token.
    """
    console.print("🔐 Verificando autenticação via GitHub CLI...")
    token = get_token_from_gh_cli()

    if temp:
        config.set_session_token(token)
        console.print("⚠️  [yellow]Login temporário. Token armazenado apenas nesta sessão.[/yellow]")
    else:
        config.save_token(token)

    console.print("✅ [bold green]Login bem-sucedido![/bold green]")

@app.command(hidden=True)
def make_repo_pesq(nome: str):
    """
    Clones the base MLOps template for the 'Pesquisa' profile.
    (This command is intended for internal use by the 'start' command).
    """
    token = config.get_token()
    core.clonar_template_com_nome(
        config.TEMPLATE_REPO_URL_PESQUISA.format(token=token), nome
    )

@app.command(hidden=True)
def make_repo(nome: str):
    """
    Clones the base MLOps template repository into a new directory.
    """
    token = config.get_token()
    core.clonar_template_com_nome(
        config.TEMPLATE_REPO_URL.format(token=token), nome
    )

def _handle_auth_flow(org_name: str):
    """
    Trata o fluxo de autenticação e logout/login para garantir acesso à organização correta.
    """
    console.print(Panel(
        f"[bold yellow]⚠️ Para criar repositórios na organização '{org_name}', você precisa estar autenticado com uma conta que tenha acesso a ela.[/bold yellow]\n\n"
        "Se você já estiver logado com outra conta no GitHub CLI, recomenda-se fazer logout antes de prosseguir.",
        title="Atenção",
        border_style="yellow"
    ))

    if Confirm.ask("Deseja fazer logout do GitHub CLI antes de continuar?", default=True):
        console.print("🔐 Fazendo logout do GitHub CLI...")
        subprocess.run(["gh", "auth", "logout", "--hostname", "github.com"], check=False)

    console.print("🔑 Iniciando processo de login com a conta certa (use o navegador quando solicitado)...")
    login(temp=True)


def _start_pesquisador_flow():
    """Handles the workflow for the 'Pesquisador' profile."""
    _handle_auth_flow("Insper-CDIA-Pesquisa")

    repo_nome = Prompt.ask("Qual o nome do repositório que você deseja criar?")
    make_repo_pesq(repo_nome)
    console.print(f"✅ Repositório '[bold cyan]{repo_nome}[/bold cyan]' criado com sucesso!")

    # Automatically upload the repository to GitHub
    console.print("🚀 Enviando repositório para o GitHub...")
    token = config.get_token()
    org_name = "Insper-CDIA-Pesquisa"
    pasta_projeto = os.path.join(".", repo_nome)

    core.criar_repositorio(token, org_name, pasta_projeto, repo_type="pesquisa")
    console.print(
        Panel(
            "✅ [bold green]Processo concluído com sucesso![/bold green]",
            title="Finalizado",
            border_style="green",
        )
    )

def _start_administrativo_flow():
    """Handles the workflow for the 'Administrativo' profile."""
    _handle_auth_flow("centro-dados-ia")

    repo_nome = Prompt.ask("Qual o nome do repositório que você deseja criar a partir do template?")
    make_repo(repo_nome)
    console.print(f"✅ Repositório '[bold cyan]{repo_nome}[/bold cyan]' criado com sucesso!")

    console.print("🚀 Enviando repositório para o GitHub com branches dev e prod...")
    token = config.get_token()
    org_name = "centro-dados-ia"
    pasta_projeto = os.path.join(".", repo_nome)

    try:
        core.criar_repositorio(token, org_name, pasta_projeto, repo_type="administrativo")
        console.print(
            Panel(
                "✅ [bold green]Processo concluído com sucesso![/bold green]\n\n",
                title="Finalizado",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(Panel(
            f"[bold red]❌ Erro durante a criação do repositório:[/bold red]\n\n{str(e)}",
            title="Erro",
            border_style="red"
        ))

def _check_directory_is_project_root():
    """
    Checks if the current directory is a valid project root.

    If the directory contains only one subdirectory, it suggests the user
    to change into that directory.
    """
    items = os.listdir(".")
    dirs = [d for d in items if os.path.isdir(d) and not d.startswith(".")]
    files = [f for f in items if os.path.isfile(f)]

    if len(dirs) == 1 and not files:
        project_dir = dirs[0]
        console.print(
            Panel(
                f"❌ [bold red]Comando executado no diretório errado.[/bold red]\\n\\n"
                f"Parece que seu projeto está na pasta '[bold cyan]{project_dir}[/bold cyan]'.\\n"
                f"Por favor, entre na pasta do projeto e tente novamente:\\n\\n"
                f"[green]cd {project_dir}[/green]\\n"
                f"[green]mlops upload-repo[/green]",
                title="Erro de Diretório",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)


@app.command(hidden=True)
def upload_repo():
    """
    Creates a GitHub repository from the current directory and uploads the files.

    This command guides the user to select an organization and then triggers
    the repository creation and configuration process.
    """
    _check_directory_is_project_root()

    console.print(
        Panel(
            "[bold]Em qual organização você deseja criar o repositório?[/bold]\n"
            "[cyan]1[/cyan]: Pesquisa (Insper-CDIA-Pesquisa)\n"
            "[cyan]2[/cyan]: Administrativo (centro-dados-ia)",
            title="Seleção de Organização",
            border_style="blue",
        )
    )
    choice = Prompt.ask("Digite o número da opção", choices=["1", "2"], default="1")

    if choice == "1":
        org_name = "Insper-CDIA-Pesquisa"
        repo_type = "pesquisa"
    elif choice == "2":
        org_name = "centro-dados-ia"
        repo_type = "administrativo"

    token = config.get_token()
    pasta_atual = "."

    core.criar_repositorio(token, org_name, pasta_atual, repo_type=repo_type)
    console.print(
        Panel(
            "✅ [bold green]Processo concluído com sucesso![/bold green]",
            title="Finalizado",
            border_style="green",
        )
    )

@app.command()
def start():
    """Starts the interactive setup process for a new MLOps project."""
    _print_header()
    console.print(Panel("[bold green]Bem-vindo à biblioteca MLOps Insper![/bold green]", title="👋 Boas-vindas"))
    
    console.print(
        "Para começar, por favor, selecione o seu perfil:\n"
        "  [cyan]1[/cyan]: Pesquisador\n"
        "  [cyan]2[/cyan]: Administrativo"
    )
    choice = Prompt.ask("Digite o número da opção", choices=["1", "2"])

    if choice == "1":
        _start_pesquisador_flow()
    elif choice == "2":
        _start_administrativo_flow()