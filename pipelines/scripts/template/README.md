# Template de Pipeline

Este diretório é um esqueleto para criação de novos pipelines no projeto.

## Estrutura

- `extract.py`: etapa de extração.
- `transform.py`: etapa de transformação.
- `load.py`: etapa de carga.
- `pipeline.py`: orquestra a execução `extract -> transform -> load`.
- `settings.py`: constantes comuns do pipeline.

## Como usar

1. Copie este diretório para `pipelines/scripts/<novo_pipeline>/`.
2. Renomeie classes e `PIPELINE_NAME`.
3. Implemente a lógica de negócio nos métodos privados `_extract`, `_transform` e `_load`.
4. Se necessário, adicione checkpoints específicos usando o padrão dos pipelines CVM.

## Execução

Use o `main()` de `pipeline.py` como entrypoint local/container.
