# Agenda de execução dos pipelines

Visão geral dos horários programados para os pipelines ativos do projeto.

| Pipeline | Horário programado | Frequência | Observação |
|---|---:|---|---|
| `start_ubuntu_server` | 07:40:00 | Diária | Executado pelo serviço `bioss`. |
| `cvm_formulario_demonstracoes_financeiras_padronizadas` | 08:00:00 | Diária | Executado pelo serviço `kairos-trap-cvm-dfp.timer`. |
| `cvm_formulario_informacoes_trimestrais` | 08:30:00 | Diária | Executado pelo serviço `kairos-trap-cvm-itr.timer`. |
| `cvm_cias_abertas_informacao_cadastral` | 09:10:00 | Diária | Executado pelo serviço `kairos-trap-cvm-cad.timer`. |
| `b3_enriquecimento_cadastral_ativos` | 01/09/2026 22:00:00 | Única | Executado uma vez pelo serviço `kairos-trap-b3-cad.timer`. |
| `cvm_formulario_de_referencia` | 19:00:00 | Diária | Executado pelo serviço `kairos-trap-cvm-fre.timer`. |

## Visão geral da execução

- O projeto atualmente agenda a execução dos pipelines por meio de timers do `systemd`.
- Ambos os pipelines estão configurados com `Persistent=true`, portanto, execuções perdidas são retomadas quando o sistema volta a ficar disponível.
- O agendamento é diário e segue o fluxo operacional dos jobs ETL.