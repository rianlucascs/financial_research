# Data Catalog — cvm_formulario_de_referencia

Catálogo objetivo do dado: o que cada fonte representa, quais datasets/campos existem e como interpretar as colunas principais.

---

## Fontes

### CVM (Comissão de Valores Mobiliários)

- Origem: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/`
- Conteúdo: Formulário de Referência (FRE) de companhias abertas.
- Cobertura atual no projeto: ativa (anos de 2010 até o ano corrente).

---

## Datasets CVM disponíveis

Os arquivos seguem o padrão `fre_cia_aberta_<identificador>_<ano>` na origem e são consolidados por identificador no dataset processado (`fre_cia_aberta_<identificador>_2010-<ano_atual>.parquet`).

### Identificadores e tópicos disponíveis

O Formulário de Referência contempla diversos tópicos corporativos, governança, remuneração e finanças:

- `informacao_financeira`, `historico_emissor`
- `capital_social`, `capital_social_aumento`, `capital_social_aumento_classe_acao`, `capital_social_classe_acao`, `capital_social_desdobramento`, `capital_social_desdobramento_classe_acao`, `capital_social_reducao`, `capital_social_reducao_classe_acao`, `capital_social_titulo_conversivel`
- `posicao_acionaria`, `posicao_acionaria_classe_acao`, `distribuicao_capital`, `distribuicao_capital_classe_acao`, `distribuicao_dividendos`, `distribuicao_dividendos_classe_acao`
- `administrador_PCD`, `administrador_declaracao_genero`, `administrador_declaracao_raca`, `administrador_membro_conselho_fiscal`, `cargo_administrador`, `membro_comite`, `responsavel`
- `auditor`, `auditor_responsavel`
- `remuneracao_acao`, `remuneracao_maxima_minima_media`, `remuneracao_total_orgao`, `remuneracao_variavel`
- `endividamento`, `obrigacao`, `transacao_parte_relacionada`, `outro_valor_mobiliario`, `valor_mobiliario_tesouraria_movimentacao`, `valor_mobiliario_tesouraria_ultimo_exercicio`, `volume_valor_mobiliario`
- `ativo_imobilizado`, `ativo_intangivel`, `participacao_sociedade`, `participacao_sociedade_valorizacao_acao`
- `plano_recompra`, `plano_recompra_classe_acao`, `politica_negociacao`, `politica_negociacao_cargo`
- `empregado_PCD`, `empregado_local_declaracao_genero`, `empregado_local_declaracao_raca`, `empregado_local_faixa_etaria`, `empregado_posicao_declaracao_genero`, `empregado_posicao_declaracao_raca`, `empregado_posicao_faixa_etaria`, `empregado_posicao_local`
- `relacao_familiar`, `relacao_subordinacao`, `grupo_economico_reestruturacao`, `mercado_estrangeiro`, `titulo_exterior`, `titular_valor_mobiliario`, `direito_acao`, `acao_entregue`

### Granularidade

- Unidade de observação: uma linha por registro dentro de cada submódulo do FRE (por empresa, ano de referência e atributos específicos da tabela).
- Chave prática para identificação de linha:
	- `CNPJ_CIA`, `CD_CVM`, `DENOM_CIA`, `DT_REFER` (acrescida de identificadores específicos do módulo, como cargo, CPF/CNPJ ou código de conta/ativo).

---

## Dicionário de campos principais

| Campo | Tipo esperado | O que representa | Exemplo de granularidade |
|---|---|---|---|
| `CNPJ_CIA` | `string` | CNPJ da companhia emissora | empresa |
| `DENOM_CIA` | `string` | Nome social da companhia | empresa |
| `CD_CVM` | `string` | Código CVM da companhia | empresa |
| `DT_REFER` | `datetime` | Data de referência do Formulário de Referência | exercício/ano |
| `VERSAO` | `Int64` | Versão da entrega ou retificação do documento | versão do documento |
| `CATEG_DOC` | `string` | Categoria do documento CVM | metadado regulatório |
| `CPF` / `CNPJ` | `string` | Identificador de administradores, acionistas ou auditores | governança / partes |
| `Cargo_Administrador` | `string` | Cargo ocupado na administração da companhia | governança |
| `Auditor` | `string` | Nome da empresa de auditoria independente | auditores |
| `CNPJ_Auditor` | `string` | CNPJ da empresa de auditoria | auditores |
| `Classe_Acao` | `string` | Classe de ação (ex.: ON, PN) | estrutura de capital |
| `Valor_Mobiliario` | `string` | Tipo de valor mobiliário emitido | mercado de capitais |

---

## Entendendo campos-chave

- `CD_CVM` e `CNPJ_CIA`: chaves primárias para identificar a companhia emissora e cruzar com pipelines cadastrais e demonstrativos financeiros (DFP/ITR).
- `DT_REFER`: indica a data de referência anual à qual o Formulário de Referência pertence.
- `VERSAO`: indica se o documento é a entrega original (versão 1) ou se trata de uma entrega retificadora republicada pela empresa.

---

## Peculiaridades do dado

- Documento corporativo abrangente: cobre áreas não financeiras, como governança corporativa, dados de administradores, diversidade de quadro de funcionários, controle acionário e remuneração de executivos.
- Estrutura multi-tabela: diferentemente das demonstrações financeiras (que focam em contas contábeis), o FRE possui mais de 60 tabelas com esquemas de colunas heterogêneos.
- Atualização e retificação: retificações de anos anteriores podem ser enviadas a qualquer momento pela CVM, atualizando o histórico.

---

## Observações de qualidade

- O arquivo bruto é disponibilizado em CSV com separador `;` e encoding `iso-8859-1`.
- Colunas textuais e numéricas passam por padronização e conversão de tipos com tratamentos de exceção (`errors="coerce"`).
- O parse de datas padroniza os campos para `datetime`, gravando `NaT` em caso de formato inválido.
