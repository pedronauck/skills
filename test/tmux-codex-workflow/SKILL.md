---
name: tmux-codex-workflow
description: Monitor and interact with AI coding agent sessions (Claude Code / Codex) running inside tmux — launch, monitor progress, then commit & push results
---

# TMUX + AI Agent Workflow (Claude Code & Codex)

Lançar, monitorar e finalizar sessões de agentes de código AI (Claude Code ou Codex) rodando dentro do tmux em background.

## Suportados

| Agente | Comando | Flag skip permissions |
|--------|---------|----------------------|
| **Claude Code** | `claudey` | `--dangerously-skip-permissions` |
| **Codex CLI** | `codex exec` | (padrão auto-approve) |

## Pré-requisitos

- `tmux` instalado (via Homebrew em `/home/linuxbrew/.linuxbrew/bin/tmux`)
- Claude Code ou Codex CLI no PATH

## Comandos Básicos

### Listar sessões tmux ativas
```bash
tmux list-sessions
```

### Ver output de uma sessão sem attach
```bash
tmux capture-pane -t <session-name> -p
```

### Enviar comando para uma sessão (sem attach)
```bash
tmux send-keys -t <session-name> '<comando>' Enter
```

### Attach numa sessão interativa
```bash
tmux attach -t <session-name>
```
Detach: `Ctrl+B` depois `D`

## Workflow de Monitoramento

1. **Ver status atual** — capture o pane da sessão para ver onde está
2. **Context check** — prestar atenção na barra de contexto `[███ ]`. Quando cheia [███▏], o Codex pode travar/ficar lento
3. **Se travado** — enviar um `Enter` (`tmux send-keys -t <sessao> Enter`) pode despertar
4. **Rodando em background** — não precisa ficar attachado; capture periodicamente

## Padrões Observados

### Context quase cheio → comportamento lento/travado
- O Codex pode parar de responder quando contexto está 90%+
- Um `Enter` via `tmux send-keys` geralmente desperta
- Após finalizar tarefa com contexto cheio, ele pode liberar espaço automaticamente

### Pre-commit hooks com PATH incompleto
Se o husky pre-commit falhar com `command not found`:
```bash
# Go está no Homebrew
export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
# Bun/Go podem estar no mise
export PATH="$HOME/.local/share/mise/shims:$PATH"
git commit -m "mensagem" --no-verify  # ou retry com PATH fixo
```

### Git commit em projeto com hooks que precisam de ferramentas específicas
```bash
cd ~/Projects/<projeto>
export PATH="/home/linuxbrew/.linuxbrew/bin:$HOME/.local/share/mise/shims:$PATH"
git add .
git commit -m "msg"
git push
```

## Exemplo de Fluxo Completo (Codex)

```bash
# 1. Checar status
tmux capture-pane -t agh -p

# 2. Mandar trabalho novo
tmux send-keys -t agh 'fix the integration test failure' Enter

# 3. Monitorar periodicamente
tmux capture-pane -t agh -p | tail -20

# 4. Quando terminar, fazer commit/push fora da sessão
cd ~/Projects/agh && export PATH="/home/linuxbrew/.linuxbrew/bin:$HOME/.local/share/mise/shims:$PATH" && git add . && git commit -m "fix: ..." && git push
```

## Exemplo de Fluxo Completo (Claude Code)

```bash
# 1. Criar sessão tmux no diretório do projeto
tmux new-session -d -s <nome-sessao> -c ~/Projects/<projeto>

# 2. Lançar Claude Code com task e skip permissions
tmux send-keys -t <nome-sessao> "claudey --dangerously-skip-permissions '<SEU PROMPT DETALHADO AQUI>'" Enter

# 3. Monitorar progresso periodicamente (~2-5 min entre checks)
tmux capture-pane -t <nome-sessao> -p | tail -40

# 4. Indicadores de progresso Claude Code:
#    ● = tarefa ativa, ✽ = pensando, ✢ = escrevendo/arquivando
#    "Done" ou "Cooked for Xm Xs" = terminou
#    Subagents aparecem como "Explore(...)" ou "● agent finished"
#    Checklist ◻ / ✔ mostra tarefas pendentes/concluídas
#    Token count (↑/↓ Xk tokens) dá ideia de volume de trabalho

# 5. Quando terminar ("Cooked"), verificar commit e push
cd ~/Projects/<projeto>
git log --oneline -3        # ver o commit que o Claude Code fez
git status --short          # confirmar clean working tree
git push origin main        # push para remote
```

### Prompt Pattern para Documentação em Massa (com Subagents)

Quando pedir ao Claude Code para revisar/melhorar documentação de um projeto:

```
Analise o projeto <nome> (um port/rewrite de <ref>). Sua tarefa: use subagents 
(claude --print) para revisar e melhorar TODA a documentação do projeto:
1) AGENTS.md - atualizar se houver mudanças recentes
2) README.md - melhorar descrição, badges, instruções
3) Qualquer doc em internal/ packages (godoc comments)
4) Config examples
5) CONTRIBUTING.md se existir ou criar um
Foque em documentação desatualizada, incorreta ou incompleta.
Use subagents para paralelizar o trabalho em diferentes arquivos/pacotes.
Quando terminar tudo, faça um git commit com todas as mudanças.
```

## Git Push: HTTPS → SSH Fallback

Se `git push` falhar com `could not read Username` (HTTPS sem credenciais):

```bash
# Trocar remote de HTTPS para SSH (usa a SSH key já configurada)
cd ~/Projects/<projeto>
git remote set-url origin git@github.com:<user>/<repo>.git
git push origin main
```

## Pitfalls

- **Não use `tmux send-keys` com aspas complexas** — o shell do tmux pode interpretar diferente
- **Capture-pane mostra apenas o visible buffer** — se houve scroll, pode não ver tudo. Usar `capture-pane -t <sessao> -S -50` para mais linhas
- **Context bar** é visual-only no output capturado — útil para estimar capacidade restante
- **Claude Code com prompts longos** — quebre o prompt em múltiplas linhas no send-keys ou use um arquivo de prompt. Aspas dentro do prompt precisam de escape adequado
- **Claude Code pode rodar 10+ minutos** para tasks pesadas (ex: doc review em 16+ pacotes com subagents). Não assuma que travou — cheque o token count e tool uses ativos
- **`sleep` no terminal tem timeout clamp** — background waits são truncados para ~60s pelo sistema. Use múltiplos checks sequenciais em vez de uma espera longa única
- **HTTPS remote + push sem TTY** → falha silenciosa com "could not read Username". Trocar pra SSH resolve permanentemente
