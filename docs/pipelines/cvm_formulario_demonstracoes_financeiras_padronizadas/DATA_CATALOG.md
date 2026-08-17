# Data Catalog — cvm_formulario_demonstracoes_financeiras_padronizadas

Catálogo objetivo do dado: o que cada fonte representa, quais datasets/campos existem e como interpretar as colunas principais.

---

## Fontes

### CVM (Comissão de Valores Mobiliários)

- Origem: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/`
- Conteúdo: Demonstrações Financeiras Padronizadas (DFP) de companhias abertas.
- Cobertura atual no projeto: ativa (anos de 2011 até o ano corrente).


## Datasets CVM disponíveis

Os arquivos seguem o padrão `dfp_cia_aberta_<codigo>_<ano>` na origem e são consolidados por código no dataset processado.

### Códigos de demonstração usados

- `BPA_con`, `BPA_ind`
- `BPP_con`, `BPP_ind`
- `DFC_MD_con`, `DFC_MD_ind`
- `DFC_MI_con`, `DFC_MI_ind`
- `DMPL_con`, `DMPL_ind`
- `DRA_con`, `DRA_ind`
- `DRE_con`, `DRE_ind`
- `DVA_con`, `DVA_ind`

### Granularidade

- Unidade de observação: uma linha por combinação de empresa, referência temporal, versão do documento e conta contábil.
- Chave prática para identificação de linha:
	- `CD_CVM`, `DT_REFER`, `VERSAO`, `GRUPO_DFP`, `ORDEM_EXERC`, `DT_FIM_EXERC`, `CD_CONTA`

---

## Dicionário de campos principais

| Campo | Tipo esperado | O que representa | Exemplo de granularidade |
|---|---|---|---|
| `CNPJ_CIA` | `string` | CNPJ da companhia | empresa |
| `DENOM_CIA` | `string` | Nome da companhia | empresa |
| `CD_CVM` | `string` | Código CVM da companhia | empresa |
| `DT_REFER` | `datetime` | Data de referência do DFP | período de referência |
| `VERSAO` | `Int64` | Versão da entrega/retificação do documento | versão do documento |
| `GRUPO_DFP` | `string` | Grupo/tipo textual da demonstração | tipo de demonstração |
| `MOEDA` | `string` | Moeda declarada no registro | registro contábil |
| `ESCALA_MOEDA` | `string` | Escala da moeda (ex.: MIL) | registro contábil |
| `ORDEM_EXERC` | `string` | Indicador de exercício (ex.: último/penúltimo) | comparação entre exercícios |
| `DT_FIM_EXERC` | `datetime` | Data de fechamento do exercício | exercício social |
| `CD_CONTA` | `string` | Código da conta contábil | conta |
| `DS_CONTA` | `string` | Descrição da conta contábil | conta |
| `VL_CONTA` | `float64` | Valor monetário da conta reportado pela CVM | valor da conta por linha |
| `ST_CONTA_FIXA` | `string` | Indicador de conta fixa da fonte | atributo da conta |

---

## O que é `VL_CONTA` e de onde vem

- Origem: coluna `VL_CONTA` dos arquivos DFP da CVM.
- Significado: valor da conta contábil (`CD_CONTA`/`DS_CONTA`) para a empresa e período da linha.
- Unidade: deve ser interpretada junto de `MOEDA` e `ESCALA_MOEDA`.
- Tipo no projeto: convertido para `float64`.

---

## Peculiaridades do dado

- Retificação: a CVM pode republicar/retificar dados; isso aparece em `VERSAO`.
- Multi-exercício na mesma referência: `ORDEM_EXERC` separa valores de exercício atual e anterior.
