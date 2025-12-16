"""Core logic for handling Git and GitHub operations."""

import os
import shutil
from typing import List

import typer

import git
from github import Github, GithubException, Repository
from github.Organization import Organization
from rich.console import Console

from . import config

console = Console()


def clonar_template_com_nome(
    template_repo_url: str, nome_projeto: str, destino_base: str = ".", verbose: bool = True
) -> str:
    """
    Clones a template repository into a new directory with a given name.

    Args:
        template_repo_url: The URL of the template repository to clone.
        nome_projeto: The name of the new project and directory.
        destino_base: The base directory where the new project will be created.

    Returns:
        The destination path of the cloned repository.
    """
    destino = os.path.join(destino_base, nome_projeto)
    if os.path.exists(destino):
        if verbose:
            console.print(f"[red]❌ A pasta '{destino}' já existe. Por segurança, o processo será interrompido.[/red]")
            console.print("[yellow]💡 Dica: Apague manualmente ou escolha outro nome para o repositório.[/yellow]")
            raise typer.Exit(code=1)
        else:
            raise FileExistsError(f"A pasta '{destino}' já existe.")
            
    if verbose:
        console.print(f"🌱 Criando seu repositório em {destino}")
    git.Repo.clone_from(template_repo_url, destino)
    
    # Remove o histórico git do template para iniciar um novo repositório limpo
    shutil.rmtree(os.path.join(destino, ".git"), ignore_errors=True)
    
    return destino


def _get_or_create_repo(
    org: Organization, repo_nome: str, visibilidade: str
) -> Repository:
    """Gets an existing repository or creates a new one."""
    try:
        return org.get_repo(repo_nome)
    except GithubException as e:
        if e.status == 404:
            return org.create_repo(repo_nome, private=(visibilidade == "private"))
        raise e


def _init_and_configure_git(
    pasta: str, repo_url: str, branches_to_push: List[str], repo_type: str
) -> git.Repo:
    """Initializes and configures the local Git repository."""
    repo_git = git.Repo.init(pasta)

    if "origin" in [remote.name for remote in repo_git.remotes]:
        repo_git.remote("origin").set_url(repo_url)
    else:
        repo_git.create_remote("origin", repo_url)

    # ⚠️ Cria commit inicial diretamente na branch 'main'
    repo_git.git.checkout("-b", "main")
    repo_git.git.add(A=True)

    if repo_git.is_dirty(untracked_files=True):
        repo_git.index.commit("Commit inicial (gerado via Insper MLOps CLI) [skip ci]")


    # ⚙️ Cria a branch 'dev' a partir da 'main' se for administrativo
    if repo_type == "administrativo":
        if "dev" not in [b.name for b in repo_git.branches]:
            repo_git.create_head("dev", "main")

    # 🚀 Push das branches existentes
    for branch in branches_to_push:
        if branch in [b.name for b in repo_git.branches]:
            repo_git.git.push("--set-upstream", "origin", branch)

    return repo_git

def _apply_branch_protection(repo: 'Repository', branch_name: str):
    """Applies a comprehensive set of branch protection rules."""
    try:
        console.print(f"🛡️  Aplicando regras de proteção à branch '[bold]{branch_name}[/bold]'...")
        branch = repo.get_branch(branch_name)
        branch.edit_protection(
            # Requer 1 aprovação em PRs
            required_approving_review_count=1,
            # Desabilita revisões obsoletas após novos pushes
            dismiss_stale_reviews=True,
            # Não permite deletar a branch
            allow_deletions=False,
            # Exige que o histórico de commits seja linear (impede merge fast-forward)
            required_linear_history=True,
            # Passando outras regras como kwargs, baseado na API do GitHub
            require_code_owner_reviews=False,
            required_conversation_resolution=False,
        )
        if hasattr(console, 'print'): # Check simples para evitar erro se console for mock
             console.print(f"✅ Proteção da branch '[bold]{branch_name}[/bold]' configurada.")
    except GithubException as e:
        if e.status == 403:
            console.print(f"[yellow]⚠️  Aviso: A proteção de branch em '{branch_name}' não foi aplicada (requer plano Pro/Team).[/yellow]")
        else:
            console.print(f"[red]❌ Erro ao proteger a branch '{branch_name}': {e}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Erro inesperado ao proteger a branch '{branch_name}': {e}[/red]")


def _set_repository_permissions(org: 'Organization', repo: 'Repository', g: 'Github'):
    """Sets repository permissions for the admin team and the creator."""
    try:
        team = org.get_team_by_slug("cdia-admin")
        team.set_repo_permission(repo, "admin")

        creator = g.get_user()
        if creator and creator.login:
            repo.add_to_collaborators(creator.login, permission="push")
            console.print(f"✅ Permissões configuradas: Equipe '[bold]CDIA-Admin[/bold]' é admin, usuário '[bold]{creator.login}[/bold]' é writer.")
        else:
            console.print("✅ Permissões configuradas: Equipe '[bold]CDIA-Admin[/bold]' é admin.")
            console.print("[yellow]⚠️  Aviso: Não foi possível rebaixar o criador do repositório para 'writer' (usuário não identificado).[/yellow]")

    except GithubException as e:
        if e.status == 404:
            console.print("[yellow]⚠️  Aviso: Equipe 'cdia-admin' não encontrada. Permissões de equipe não ajustadas.[/yellow]")
        else:
            console.print(f"[red]❌ Erro ao configurar permissões: {e}[/red]")





def criar_repositorio(
    github_token: str,
    org_name: str,
    pasta: str,
    repo_type: str = "administrativo",
    visibilidade: str = "private",
    verbose: bool = True,
):
    """
    Creates and configures a GitHub repository based on the specified type.

    This function handles the entire workflow: creating the repo on GitHub,
    configuring the local git repository, pushing branches, and setting up
    permissions and protections.

    Args:
        github_token: The GitHub personal access token.
        org_name: The name of the GitHub organization.
        pasta: The local path to the project directory.
        repo_type: The type of repository ('administrativo' or 'pesquisa').
                   This determines the configuration applied.
        visibilidade: The visibility of the repository ('private' or 'public').
        verbose: If True, prints status updates to the console.
    """
    from contextlib import nullcontext
    
    # Usa nullcontext se não for verbose, para não mostrar spinner
    status_ctx = console.status("[bold green]Iniciando processo...") if verbose else nullcontext()
    
    with status_ctx as status:
        repo_nome = os.path.basename(os.path.abspath(pasta))
        if verbose:
            console.print(f"📝 Nome do repositório: [bold cyan]{repo_nome}[/bold cyan]")

        if verbose and hasattr(status, 'update'):
            status.update("Conectando ao GitHub e criando repositório...")
            
        g = Github(github_token)
        try:
            org = g.get_organization(org_name)
        except GithubException as e:
            if e.status == 404:
                if verbose:
                    console.print(f"[red]❌ Organização '{org_name}' não encontrada ou sem acesso.[/red]")
                    console.print("[yellow]💡 Dicas:[/yellow]")
                    console.print("   • Verifique se o nome da organização está correto")
                    console.print("   • Confirme se você tem acesso à organização")
                    console.print("   • Considere usar sua conta pessoal do GitHub")
                raise e
            else:
                raise e
        repo = _get_or_create_repo(org, repo_nome, visibilidade)
        if verbose:
            console.print("✅ Repositório criado com sucesso.")

        if verbose and hasattr(status, 'update'):
            status.update("Configurando repositório local e enviando branches...")
            
        repo_url = repo.clone_url.replace("https://", f"https://{github_token}@")
        branches_to_push = ["main", "dev"] if repo_type == "administrativo" else ["main"]
        repo_git = _init_and_configure_git(pasta, repo_url, branches_to_push, repo_type)
        
        if verbose:
            console.print("✅ Branches enviadas.")

        if verbose and hasattr(status, 'update'):
            status.update("Configurando permissões e proteções...")
            
        if repo_type == "administrativo":
            # Configura os métodos de merge permitidos para o repositório
            repo.edit(
                allow_merge_commit=True,
                allow_squash_merge=True,
                allow_rebase_merge=True,
                delete_branch_on_merge=True, # Conveniência: apaga a branch após o merge
            )
            if verbose:
                console.print("✅ Métodos de merge e configurações do repositório aplicados.")
            
            # Garante que a branch default seja 'main' antes de proteger
            repo.edit(default_branch="main")
            
            _apply_branch_protection(repo, "main")
            _apply_branch_protection(repo, "dev")
        
        # Commit e push extra para acionar monitoramento (ex: Teams)
        # Feito após as proteções para ser o último evento significativo
        # if verbose:
        #    console.print("📡 Enviando trigger de monitoramento...")
        # repo_git.git.commit("--allow-empty", "-m", "Trigger: Project creation monitoring")
        # repo_git.git.push()
        _set_repository_permissions(org, repo, g)
        


    if verbose:
        console.print("✅ Processo concluído com sucesso!")