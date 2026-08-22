# Data Catalog — cvm_cias_abertas_informacao_cadastral

Catálogo objetivo do dado: o que cada fonte representa, quais datasets/campos existem e como interpretar as colunas principais.

---

## Fontes

### CVM (Comissão de Valores Mobiliários)

- Origem: `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv`
- Conteúdo: cadastro cadastral de companhias abertas, incluindo identificação, situação societária, endereço, responsável legal e auditor.
- Cobertura atual no projeto: ativa (base disponível em atualização periódica pela CVM).

---

## Datasets CVM disponíveis

O arquivo bruto disponibilizado pela CVM é o `cad_cia_aberta.csv`, consolidado em uma tabela única no projeto.

### Granularidade

- Unidade de observação: uma linha por companhia aberta.
- Chave prática para identificação da linha:
	- `CNPJ_CIA`, `CD_CVM`, `DENOM_SOCIAL`

---

## Dicionário de campos principais

| Campo | Tipo esperado | O que representa | Exemplo de granularidade |
|---|---|---|---|
| `CNPJ_CIA` | `string` | CNPJ da companhia | empresa |
| `DENOM_SOCIAL` | `string` | Nome social da companhia | empresa |
| `DENOM_COMERC` | `string` | Nome comercial da companhia | empresa |
| `DT_REG` | `datetime` | Data de registro da companhia | cadastro |
| `DT_CONST` | `datetime` | Data de constituição da companhia | empresa |
| `DT_CANCEL` | `datetime` | Data de cancelamento, quando houver | evento societário |
| `MOTIVO_CANCEL` | `string` | Motivo do cancelamento ou encerramento | evento societário |
| `SIT` | `string` | Situação atual da companhia | status da empresa |
| `DT_INI_SIT` | `datetime` | Data de início da situação atual | status da empresa |
| `CD_CVM` | `string` | Código da companhia na CVM | empresa |
| `SETOR_ATIV` | `string` | Setor de atividade da companhia | classificação da empresa |
| `TP_MERC` | `string` | Tipo de mercado de negociação | classificação da empresa |
| `CATEG_REG` | `string` | Categoria de registro da emissora | classificação da empresa |
| `SIT_EMISSOR` | `string` | Situação do emissor como companhia aberta | status regulatório |
| `DT_INI_SIT_EMISSOR` | `datetime` | Data de início da situação do emissor | status regulatório |
| `CONTROLE_ACIONARIO` | `string` | Estrutura de controle acionário | governança |
| `TP_ENDER` | `string` | Tipo de endereço cadastral | endereço |
| `LOGRADOURO` | `string` | Logradouro do endereço da empresa | endereço |
| `COMPL` | `string` | Complemento do endereço | endereço |
| `BAIRRO` | `string` | Bairro do endereço | endereço |
| `MUN` | `string` | Município do endereço | endereço |
| `UF` | `string` | Unidade federativa do endereço | endereço |
| `PAIS` | `string` | País do endereço | endereço |
| `CEP` | `string` | CEP do endereço | endereço |
| `DDD_TEL` | `string` | DDD do telefone principal | contato |
| `TEL` | `string` | Telefone principal da empresa | contato |
| `EMAIL` | `string` | E-mail corporativo da companhia | contato |
| `TP_RESP` | `string` | Tipo do responsável cadastral | responsável legal |
| `RESP` | `string` | Nome do responsável | responsável legal |
| `DT_INI_RESP` | `datetime` | Data de início do mandato do responsável | responsável legal |
| `CNPJ_AUDITOR` | `string` | CNPJ do auditor independente | auditor |
| `AUDITOR` | `string` | Nome do auditor independente | auditor |

---

## Entendendo campos-chave

- `SIT`: indica a situação atual da companhia, como ativa, suspensa, em recuperação judicial ou cancelada.
- `SIT_EMISSOR`: representa a condição regulatória da companhia como emissora listada na CVM.
- `SETOR_ATIV` e `CATEG_REG`: ajudam a classificar a companhia por segmento econômico e regime regulatório.
- `DT_INI_SIT` e `DT_INI_SIT_EMISSOR`: são úteis para reconstruir a cronologia da situação da empresa ao longo do tempo.
- `CNPJ_CIA` e `CD_CVM`: são as chaves principais para cruzamento com outros datasets do projeto.

---

## Peculiaridades do dado

- Registro por empresa: o dataset representa o cadastro da companhia, e não uma série temporal por exercício ou trimestre.
- A maioria dos campos é textual ou cadastral, e não numérica; o principal valor analítico está em identificadores, status e atributos institucionais.
- `DT_CANCEL` e `MOTIVO_CANCEL` podem ficar vazios para companhias ativas.
- Dados de endereço e contato podem conter valores textuais com acentos, abreviações e variações de padronização.
- `RESP`, `CNPJ_AUDITOR` e `AUDITOR` podem mudar ao longo do tempo e exigem atenção em comparações históricas.

---

## Observações de qualidade

- O arquivo bruto é lido com separador `;` e encoding `iso-8859-1`.
- Campos de data são convertidos com `to_datetime(..., errors="coerce")`, preservando datas inválidas como `NaT` para facilitar rastreio.
- Colunas textuais são convertidas para `string` para evitar problemas de dtype em operações de concatenação e filtros.
- Em pipelines com histórico, o cadastro costuma servir como base de referência para identificar empresas, status, setor e estrutura regulatória.
