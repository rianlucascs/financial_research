# Pipeline: BCB — Histórico de Taxas de Juros

Extrai o histórico de decisões do COPOM e as taxas de juros Selic (meta e over) publicadas pelo Banco Central do Brasil, salvando os dados em CSV.

**Fonte:** [Banco Central do Brasil — Histórico de Taxas de Juros](https://www.bcb.gov.br/controleinflacao/historicotaxasjuros)  
**Periodicidade da fonte:** atualizada após cada reunião do COPOM (aproximadamente a cada 45 dias)  
**Cobertura:** todas as reuniões do COPOM disponíveis na página

---

## O que é atualizado a cada execução?

| Processo | O que é atualizado | O que é pulado |
|---|---|---|
| `extract` | Tabela completa da página do BCB é sempre re-extraída | Nenhum — o arquivo CSV é sempre recriado do zero |

> O `extract` sempre recria o CSV com os dados mais recentes da página. Não há etapas de transform ou load neste pipeline.

---

## Processos

### 1. `extract`

Acessa a página do Banco Central via Selenium, lê a tabela de histórico de reuniões do COPOM e salva os dados em CSV na camada `raw`.

**Entrada:** Página web do BCB (`https://www.bcb.gov.br/controleinflacao/historicotaxasjuros`)  
**Saída:** `raw/bcb_historico_taxas_juros.csv`

**Colunas do CSV:**

| Coluna | Descrição |
|---|---|
| `Reunião` | Número sequencial da reunião do COPOM |
| `Data da Reunião` | Data em que ocorreu a reunião |
| `Data da Divulgação` | Data de divulgação da decisão |
| `Período de Vigência` | Período de vigência da taxa definida |
| `Taxa Selic Meta (%)` | Taxa Selic meta definida na reunião |
| `Taxa Selic Over (%)` | Taxa Selic over do período |
| `Taxa Selic Meta Anterior (%)` | Taxa Selic meta da reunião anterior |
| `Taxa Selic Over Anterior (%)` | Taxa Selic over da reunião anterior |

**Comportamento:**
- Abre o navegador Chrome via Selenium (modo headless).
- Aguarda o carregamento da tabela na página (timeout: 20s).
- Se a tabela retornar menos de 20 linhas, considera falha de carregamento e lança erro.
- O CSV é sempre recriado do zero a cada execução.
- Checkpoints gravados em: `state/checkpoints/.../extract/download/`.
