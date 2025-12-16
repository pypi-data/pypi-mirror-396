# MLOps Template

🚀 Ferramenta de linha de comando para padronizar e automatizar projetos de MLOps no Insper CDIA.

## Instalação

```bash
pip install insper-mlops
```

## Uso

```bash
mlops start
```

Siga as instruções no terminal para criar seu repositório de MLOps.

## Funcionalidades

- ✅ Criação automática de repositórios GitHub
- ✅ Configuração de branches (dev/prod)
- ✅ Aplicação de regras de proteção de branch
- ✅ Configuração de permissões de equipe
- ✅ Templates pré-configurados para diferentes perfis

## Requisitos

- Python 3.8+
- GitHub CLI (`gh`) instalado
- Conta GitHub com acesso às organizações Insper


## Desenvolvimento Local

Para testar alterações localmente sem instalar o pacote globalmente:

1. Clone o repositório
2. Na raiz do projeto, instale em modo editável:
   ```bash
   pip install -e .
   ```
3. Execute o comando normalmente:
   ```bash
   mlops start
   ```


## Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
