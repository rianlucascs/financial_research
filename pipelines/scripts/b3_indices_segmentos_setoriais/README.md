# Pipeline: B3 — Indices e Segmentos Setoriais

Extrai as carteiras diárias dos índices da B3, salva os dados brutos em CSV por índice e carrega o consolidado em um banco SQLite.

**Fonte:** páginas diárias de índices da B3 (`https://sistemaswebb3-listados.b3.com.br/indexPage/day/{INDICE}?language=pt-br`)  
**Periodicidade da fonte:** diária em dias úteis de mercado  
**Cobertura:** índices configurados em `settings.py` (`IDIV`, `MLCX`, `SMLL`, `IVBX`, `AGFS`, `IFNC`, `IBEP`, `IBEE`, `IBHB`, `IFIX`, `IBLV`, `IMOB`, `UTIL`, `ICON`, `IEEX`, `IFIL`, `IMAT`, `INDX`, `IBSD`, `BDRX`)

---

## O que é atualizado a cada execução?

| Processo | O que é atualizado | O que é pulado |
|---|---|---|
| `extract` | O CSV mais recente de cada índice é sempre rebaixado e substituído na camada `raw` | Nenhum — o conteúdo do diretório do índice é limpo antes do download |
| `load` | Todos os CSVs brutos disponíveis são lidos e a tabela SQLite consolidada é recriada do zero | Índices sem CSV disponível no `raw/`, que são registrados com checkpoint de ausência |

> O `extract` trabalha por índice e sempre busca a versão mais recente da carteira diária. O `load` lê os CSVs brutos disponíveis e recria uma tabela SQLite única com o consolidado.

---

## Processos

### 1. `extract`

Acessa a página diária de cada índice da B3 via Selenium, aciona o download da carteira do dia e salva o CSV na camada `raw`.

**Entrada:** página web da B3 por índice  
**Saída:** `raw/{INDICE}/{INDICE}Dia_{data}.csv`

**Colunas do CSV:**

| Coluna | Descrição |
|---|---|
| `Código` | Código do ativo na carteira do índice |
| `Ação` | Nome resumido do ativo |
| `Tipo` | Tipo do papel / segmento de listagem |
| `Qtde. Teórica` | Quantidade teórica do ativo na carteira |
| `Part. (%)` | Participação percentual do ativo no índice |

**Comportamento:**
- Abre o navegador Chrome via Selenium para cada índice.
- Limpa o conteúdo do diretório `raw/{INDICE}/` antes de iniciar novo download.
- Tenta criar o driver até 3 vezes por índice.
- Tenta clicar no link `Download` e aguardar o arquivo baixado até 10 vezes por índice.
- Se nenhum arquivo for detectado após o clique, registra falha de detecção de arquivo.
- Checkpoints gravados em: `state/checkpoints/.../extract/download/`.

### 2. `load`

Lê os CSVs brutos mais recentes dos índices disponíveis, normaliza os campos e grava tudo em uma tabela SQLite única.

**Entrada:** `raw/{INDICE}/{INDICE}Dia_{data}.csv`  
**Saída:** `load/b3_indices_segmentos_setoriais.db` (tabela `b3_indices_segmentos_setoriais`)

**Schema da tabela:**

| Coluna | Descrição |
|---|---|
| `Indice` | Código do índice (ex: `IDIV`) |
| `Data Referencia` | Data de referência extraída do cabeçalho do arquivo |
| `Código` | Código do ativo |
| `Ação` | Nome resumido do ativo |
| `Tipo` | Tipo do papel |
| `Qtde. Teórica` | Quantidade teórica convertida para inteiro |
| `Part. (%)` | Participação percentual convertida para float |

**Comportamento:**
- Lê apenas o CSV mais recente disponível em cada diretório de índice.
- Ignora índices sem CSV bruto disponível, registrando checkpoint com `STATUS_NO_FILE_DETECTED`.
- Recria a tabela SQLite do zero a cada execução (`if_exists="replace"`).
- Checkpoints gravados em: `state/checkpoints/.../load/load/`.