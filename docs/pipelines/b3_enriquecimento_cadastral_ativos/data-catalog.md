# Data Catalog - B3 Enriquecimento Cadastral de Ativos

Catalogo dos dados cadastrais e de negociacao obtidos no detalhe de companhias listadas da B3.

---

## Fonte

### B3

- Origem: `https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/GetDetail/`
- Conteudo: dados cadastrais da emissora, classificacao de mercado e codigos de negociacao/ISIN.
- Cobertura no projeto: companhias com `SIT = ATIVO` no snapshot de `cvm_cias_abertas_informacao_cadastral`.

---

## Datasets

### `empresas`

- Granularidade: uma linha por companhia retornada pela B3.
- Chave: `codeCVM`.

| Campo | Tipo esperado | O que representa |
|---|---|---|
| `codeCVM` | `string` | Codigo da companhia na CVM. |
| `issuingCompany` | `string` | Sigla ou identificador da emissora. |
| `companyName` | `string` | Razao social da companhia. |
| `tradingName` | `string` | Nome de pregao. |
| `cnpj` | `string` | CNPJ da emissora, preservado como texto. |
| `industryClassification` | `string` | Classificacao setorial em portugues. |
| `industryClassificationEng` | `string` | Classificacao setorial em ingles, quando informada. |
| `activity` | `string` | Atividade economica principal. |
| `website` | `string` | Site institucional. |
| `hasQuotation` | `string` | Indicador de existencia de cotacao. |
| `status` | `string` | Status da companhia na B3. |
| `marketIndicator` | `string` | Codigo categorial do mercado. |
| `market` | `string` | Segmento de listagem ou mercado. |
| `institutionCommon` | `string` | Nome da instituicao para acao ordinaria, quando informado. |
| `institutionPreferred` | `string` | Nome da instituicao para acao preferencial, quando informado. |
| `code` | `string` | Codigo principal apresentado pela B3. |
| `hasEmissions` | `boolean` | Indicador de emissoes registradas. |
| `hasBDR` | `boolean` | Indicador de BDR. |
| `typeBDR` | `string` | Tipo do BDR, quando aplicavel. |
| `describleCategoryBVMF` | `string` | Categoria BVMF retornada pela B3, quando informada. |
| `dateQuotation` | `datetime` | Data de inicio ou referencia da cotacao. |
| `lastDate` | `datetime` | Data e hora da ultima atualizacao retornada. |

### `codigos`

- Granularidade: uma linha por codigo de negociacao/ISIN da companhia.
- Chave pratica: `codeCVM`, `code`, `isin`.
- Relacionamento: muitos `codigos` para uma linha de `empresas` por `codeCVM`.

| Campo | Tipo esperado | O que representa |
|---|---|---|
| `codeCVM` | `string` | Codigo da companhia na CVM, usado para relacionar com `empresas`. |
| `code` | `string` | Ticker ou codigo de negociacao do ativo. |
| `isin` | `string` | Identificador internacional do valor mobiliario. |

---

## Peculiaridades e qualidade

- `otherCodes` e uma lista no JSON bruto e e normalizada em `codigos`; manter as duas tabelas evita a perda de ativos adicionais.
- Campos textuais podem ser nulos quando a B3 nao disponibiliza a informacao.
- `cnpj`, `codeCVM`, tickers e ISINs sao identificadores e nao devem ser convertidos para numeros.
- As datas de origem usam dia antes do mes; valores invalidos sao convertidos para `NaT` durante a transformacao.