# Agenda de execução dos pipelines

Visão geral dos horários programados para os pipelines ativos do projeto.

| Pipeline | Horário programado | Frequência | Observação |
|---|---:|---|---|
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | 08:00:00 | Diária | Executado pelo serviço `financial-research-cvm-dfp.timer`. |
| `cvm_formulario_informacoes_trimestrais` | 08:30:00 | Diária | Executado pelo serviço `financial-research-cvm-itr.timer`. |

## Visão geral da execução

- O projeto atualmente agenda a execução dos pipelines por meio de timers do `systemd`.
- Ambos os pipelines estão configurados com `Persistent=true`, portanto, execuções perdidas são retomadas quando o sistema volta a ficar disponível.
- O agendamento é diário e segue o fluxo operacional dos jobs ETL.