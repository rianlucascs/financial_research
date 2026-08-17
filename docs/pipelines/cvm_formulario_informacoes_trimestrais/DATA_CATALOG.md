# Data Catalog — CVM Formulario Informacoes Trimestrais

Catálogo objetivo do dado: o que cada fonte representa, quais datasets/campos existem e como interpretar as colunas principais.

---

## Fontes

### CVM (Comissão de Valores Mobiliários)

- Origem: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/`
- Conteúdo: Informações Trimestrais (ITR) de companhias abertas.
- Cobertura atual no projeto: ativa (anos de 2011 até o ano corrente).

---

## Datasets CVM disponíveis

Os arquivos seguem o padrão `itr_cia_aberta_<codigo>_<ano>` na origem e são consolidados por código no dataset processado.

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

- Unidade de observação: uma linha por combinação de empresa, período de referência, versão do documento, exercício contábil e conta contábil.
- Chave prática para identificação de linha:
	- `CNPJ_CIA`, `DT_REFER`, `VERSAO`, `CD_CVM`, `GRUPO_DFP`, `DT_INI_EXERC`, `DT_FIM_EXERC`, `ORDEM_EXERC`, `CD_CONTA`

---

## Dicionário de campos principais

| Campo | Tipo esperado | O que representa | Exemplo de granularidade |
|---|---|---|---|
| `CNPJ_CIA` | `string` | CNPJ da companhia | empresa |
| `DENOM_CIA` | `string` | Nome da companhia | empresa |
| `CD_CVM` | `string` | Código CVM da companhia | empresa |
| `DT_REFER` | `datetime` | Data de referência do ITR (fim do trimestre) | trimestre |
| `VERSAO` | `Int64` | Versão da entrega/retificação do documento | versão do documento |
| `GRUPO_DFP` | `string` | Grupo/tipo textual da demonstração | tipo de demonstração |
| `MOEDA` | `string` | Moeda declarada no registro | registro contábil |
| `ESCALA_MOEDA` | `string` | Escala da moeda (ex.: MIL) | registro contábil |
| `ORDEM_EXERC` | `string` | Indicador do exercício ou período comparado | comparação entre exercícios |
| `DT_INI_EXERC` | `datetime` | Data inicial do período contábil | exercício/período |
| `DT_FIM_EXERC` | `datetime` | Data final do período contábil | exercício/período |
| `CD_CONTA` | `string` | Código da conta contábil | conta |
| `DS_CONTA` | `string` | Descrição da conta contábil | conta |
| `VL_CONTA` | `float64` | Valor monetário da conta reportado pela CVM | valor da conta por linha |
| `ST_CONTA_FIXA` | `string` | Indicador de conta fixa da fonte | atributo da conta |
| `ORIGEM_FORMULARIO` | `string` | Origem do dado no projeto; derivado como `ITR` | metadado |
| `INTERVALO_EXERC` | `Int64` | Número de dias entre `DT_INI_EXERC` e `DT_FIM_EXERC` | exercício/período |

---

## O que é `VL_CONTA` e de onde vem

- Origem: coluna `VL_CONTA` dos arquivos ITR da CVM.
- Significado: valor da conta contábil (`CD_CONTA`/`DS_CONTA`) para a empresa e período da linha.
- Unidade: deve ser interpretada junto de `MOEDA` e `ESCALA_MOEDA`.
- Tipo no projeto: convertido para `float64`.

---

## Peculiaridades do dado

- Periodicidade trimestral: a referência temporal normalmente cai no fim do trimestre, como `2024-03-31`.
- Exercício contábil em intervalo: `DT_INI_EXERC` e `DT_FIM_EXERC` permitem distinguir o período específico da linha.
- Retificação: a CVM pode republicar/retificar dados; isso aparece em `VERSAO`.
- Comparação por período: `ORDEM_EXERC` ajuda a diferenciar valores do exercício atual e de exercício anterior ou período comparativo.

---

## Observações de qualidade

- O arquivo bruto vem em `;` e encoding `iso-8859-1`.
- A transformação de `VL_CONTA` usa conversão numérica com `errors="coerce"` para evitar que textos inválidos quebrem a pipeline.
- Datas inválidas são convertidas para `NaT` e registradas em checkpoint de transformação.
