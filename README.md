# Calculadora de lucro

Aplicação de linha de comando para cadastrar produtos, administrar taxas e
calcular o valor após taxas e o lucro.

## Requisitos

- Python 3.15.2 (versão indicada em `.python-version`)
- `venv` para manter as dependências isoladas

## Instalação

Na raiz do repositório, crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows, ative-o com:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências dentro do ambiente virtual:

```bash
python -m pip install -r requirements.txt
```

Crie o arquivo de configuração `.env` a partir do exemplo:

```bash
cp .env.example .env
```

No Windows:

```powershell
Copy-Item .env.example .env
```

O arquivo `.env` define `FILE_DATA`, o caminho do arquivo usado para armazenar
os registros. O exemplo usa `data/profits.real`.

## Como executar

Com o ambiente virtual ativado e a partir da raiz do projeto:

```bash
python app.py
```

O menu permite:

1. **Criar** um profit informando nome, preço de custo e preço de venda.
   É possível adicionar uma ou mais taxas pelo nome e valor.
2. **Atualizar** um profit selecionado, alterando nome, preço de custo ou preço
   de venda, ou adicionando/removendo uma taxa.
3. **Excluir** um profit pelo ID.
4. **Consultar** pelo nome ou listar todos os registros deixando a busca vazia.
0. **Sair**.

Os valores decimais aceitam ponto ou vírgula como separador decimal.

## Cálculo

- `after_fees = price_sale - soma dos valores das fees`
- `profit = after_fees - price_cost`

Os campos `after_fees` e `profit` são calculados pela aplicação ao criar ou
atualizar um registro.

## Saída e cores

As consultas são exibidas como um array JSON formatado. No terminal interativo,
colchetes, chaves, propriedades e valores recebem cores diferentes. As cores
ANSI são desativadas quando a saída é redirecionada ou quando a variável
`NO_COLOR` está definida:

```bash
NO_COLOR=1 python app.py
```

## Armazenamento

Os registros são persistidos no caminho configurado em `FILE_DATA`. O formato
interno utiliza `pickle`; mantenha o arquivo de dados sob controle e não carregue
arquivos recebidos de fontes não confiáveis.
