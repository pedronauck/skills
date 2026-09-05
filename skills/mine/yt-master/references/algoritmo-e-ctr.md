# Algoritmo, CTR & Distribuição

Applicability: use the parts relevant to the requested video, format, or diagnosis. Formula counts, timing targets, production mixes, checklists, and corpus benchmarks are adaptable examples, not prerequisite gates. Current platform rules and the creator's actual evidence take precedence.

## Conteúdo

- O funil de 5 etapas (modelo mental)
- CTR: definição, regra inversa, benchmark relativo, amostragem
- Onde achar o CTR
- Janela de teste pós-publicação (timing)
- Tabela mito × regra real
- SEO e descoberta: dois canais (funil interno + busca/Google)
  - O YouTube recomenda conteúdo, não canais
  - Indexar ≠ ranquear
  - Anatomia da descrição (5 blocos — "descrição Lego")
  - Capítulos = subtítulos rankeáveis
  - Playlists e conteúdo episódico
  - Tags: importam, mas perderam força
- Técnica do "canal fake"
- Prompts "Pergunte ao Studio"
- "Views reais" / co-viewing
- Alcance ≠ engajamento
- Fontes

## O funil de 5 etapas (modelo mental)

O YouTube não é caixa-preta mística: é um **sistema de medição de satisfação** que entrega o vídeo **em ondas**. Ao publicar, mostra primeiro para o **público mais quente** (quem já consumiu seu canal); mede; e expande para públicos progressivamente mais frios/aleatórios via as origens de tráfego (home/início, sugeridos, busca, notificação, página do canal).

```
Impressão → CTR → Retenção → Satisfação → Sessão
```

| Etapa | O que é | Sinal mensurável |
| --- | --- | --- |
| **1. Impressão** | Thumbnail+título mostrados a N pessoas | nº de impressões |
| **2. CTR (clique)** | cliques ÷ impressões | % de CTR no Studio |
| **3. Retenção** | quanto/como assistem; re-watch/loop | AVD, % de retenção, gráfico |
| **4. Satisfação** | like, inscrição, comentário, compartilhamento, tempo assistido | dados de consumo |
| **5. Sessão** | tempo total na plataforma após o vídeo | objetivo final do YouTube (mais sessão → mais anúncio → mais receita) |

**Sempre diagnostique na ordem do funil** — atribua a falha à etapa certa antes de sugerir mudança. (Ex.: CTR ok mas retenção baixa = problema de roteiro, não de thumbnail.)

## CTR: definição, regra inversa, benchmark relativo, amostragem

- **Definição:** CTR (click-through rate / taxa de cliques) = cliques ÷ impressões, em %. Ex.: 100 impressões, 10 cliques = 10%.
- **Inversamente proporcional ao alcance:** "quanto mais um vídeo bomba, mais o YouTube entrega, menor fica o CTR" — porque o público fica mais frio/aleatório. **CTR baixo num vídeo que bomba NÃO significa thumbnail ruim.** Exemplo real do canal: 1ª semana = 540.000 impressões / 33.000 cliques = **4,1%**; vida toda = 51M impressões / 2,7M cliques = **2,6%**.
- **Benchmark é relativo, nunca absoluto:** "Mira em 5%? Não é assim." Cada nicho tem CTR típico (games alto; educativo/finanças baixo). **Use a média de 90 dias do próprio canal como linha de base** (exemplo do canal: 6,2% — idiossincrático, não transferível).
- **Amostragem distorce canal pequeno:** 5 cliques em 10 impressões = 50%, mas "não representa a realidade". Quanto maior a amostragem, mais real o CTR. Canal pequeno vê CTR "grotescamente alto" que cai conforme cresce.

Use `scripts/ctr-baseline.py` para calcular o CTR e compará-lo à baseline do próprio canal.

## Onde achar o CTR

YouTube Studio → **Analytics → Conteúdo → filtrar por Vídeos** (Shorts não têm CTR significativo) → usar **últimos 28 ou 90 dias** como base.

## Janela de teste pós-publicação (timing)

- **Espera técnica de 15–30 min (real):** suba como não listado/privado/programado; o YouTube leva ~5–10 min para varredura de copyright + gerar legendas automáticas (ele "entende palavra por palavra"). Dê esses minutos antes de publicar.
- **Esperar 24–48h para "o algoritmo entender" é MITO.** Os dados que importam vêm de **quem assistiu** depois de público, não de pré-indexação.
- **Primeiras 12/24/48h = teste com público quente.** Se a base mais engajada não clica/retém, é forte sinal de que o vídeo não está bom e o YouTube entrega com cautela. Revise o embrulho antes de buscar alcance.

## Tabela mito × regra real

| Mito | Regra real (canal) |
| --- | --- |
| "Mire em 5% de CTR" | CTR é relativo ao seu nicho/canal; use a média de 90 dias |
| "Espere 24–48h para o algoritmo entender" | Mito; suba, espere 15–30 min (técnico), publique |
| "Frequência tem número mágico" | Frequência = curva de aprendizado; depende da audiência |
| "SEO pesado salva vídeo ruim" | SEO básico para todos; sem a base (ideia/thumb/título) não adianta |
| "CTR caindo = thumbnail piorou" | CTR cai porque o vídeo escala para público frio (sinal de sucesso) |
| "Canal dark tem algoritmo diferente" | Mesmo algoritmo: clique + retenção + interação |
| "Vídeo de 10 min indexa/rankeia melhor" | 10 min é regra de **monetização** (mais ad breaks), não de ranqueamento; a duração ótima é a do conteúdo (Camilo) |
| "Vídeo antigo com mais views é melhor" | Acumula view por **tempo no ar**; compare últimos **28/90 dias** (mesma régua). Se o antigo ganha, talvez você mudou o tema e a comunidade não quer (Camilo) |
| "Canal antigo rankeia só por ser antigo" | Idade pesa pouco; o que pesa é a **comunidade/consistência** que o tempo acumulou (Camilo) |

## SEO e descoberta: dois canais (funil interno + busca/Google)

A descoberta tem **dois motores** que pedem otimizações diferentes; não os confunda:

- **Descoberta interna (sugeridos / home / notificação)** — governada pelo **funil de 5 etapas** acima (CTR + retenção + satisfação). É o motor que a base Caique prioriza: embrulho e retenção mandam, SEO "hard" não move o ponteiro.
- **Descoberta por busca (YouTube + Google)** — o YouTube é também um **buscador subordinado ao Google** (Camilo). Descrição estruturada, capítulos e playlists são alavancas de **tráfego de busca** que valem para *qualquer* canal — com teto de esforço.

**SEO = otimizar os metadados que o sistema lê** (texto): título, descrição, tags, capítulos. Básico para TODOS: achar a palavra-chave/tema central e colocá-la no **título, descrição e tags**.

**Hierarquia de prioridade (não muda):** (1) ideia/ângulo, (2) thumbnail, (3) título, (4) vídeo-para-os-outros; **depois** SEO. "Pode fazer o SEO que quiser, não adianta" se a base (embrulho/retenção) falhar. SEO "hard" (renomear arquivo de vídeo/thumbnail) **não é divisor de águas** — só compensa em nichos cujo tráfego principal vem de busca. O que o eixo Camilo muda: **descrição, capítulos e playlists** saem da gaveta "só para quem vive de busca" e viram **higiene básica de descoberta** para todos, porque puxam tráfego do Google, não do funil interno.

### O YouTube recomenda conteúdo, não canais

O algoritmo recomenda **vídeos por nicho**, não pune "canal pequeno". Canal = agrupamento de vídeos de um tema; leva **~7 a 9 vídeos do mesmo nicho** para o YouTube "entender" sobre o que você fala e começar a recomendar. Logo: canal pequeno não é penalizado — **canal sem foco de nicho** é que não decola. (Desmonta o mito "sou pequeno, o algoritmo me ignora".)

### Indexar ≠ ranquear

- **Indexar** (entrar na busca) é rápido — ~**3–4 min** em nicho com volume e baixa concorrência. "Já apareço na busca" só significa indexado.
- **Ranquear** (subir posição) depende do **pacote inteiro** (SEO + sinais de satisfação) e leva tempo. Não confunda os dois no diagnóstico.
- Tática: suba **não listado já 100% otimizado** (título/descrição/tags/capítulos) e só então publique — casa com a espera técnica de 15–30 min acima.

### Anatomia da descrição (5 blocos — "descrição Lego")

A descrição não é depósito de palavra-chave: o robô "lê o vídeo" pela descrição (YouTube/Google não leem o áudio bruto). Estrutura:

1. **3 primeiras linhas** — o que aparece na busca/preview: gancho + 1 link. Decide o clique na busca.
2. **Resumo do vídeo (~3–4 parágrafos)** — descreve o conteúdo para o robô e para acessibilidade (pessoas surdas dependem da descrição/legenda).
3. **Links citados no vídeo** — cumprir o que prometeu (não cumprir = a pessoa compra do concorrente).
4. **Vídeos relacionados do MESMO tema** — cachorro→cachorro, não cachorro→gato (puxa sessão coerente).
5. **Rodapé social** — só redes com conteúdo ativo; equilibre link × texto.

Blocos 3–5 viram **template fixo** ("Lego") → você só escreve 1–2 e posta mais rápido. Hashtag ≠ tag (agrupa conteúdo; cuidado com hashtag da concorrência).

### Capítulos = subtítulos rankeáveis

Capítulos são timestamps que o Google indexa como **subtítulos** → abrem porta de tráfego externo. **Escreva você** (não terceirize para o automático). Não matam retenção num vídeo de **tema único**; só derrubam quando você junta 3 temas que deveriam ser 3 vídeos — aí o problema é o roteiro, não o capítulo.

### Playlists e conteúdo episódico

Playlists aparecem no filtro de busca e cada vez mais direto nos resultados (e no Google). Recompensam quem tem **vários vídeos do mesmo tema**: conteúdo **episódico** (não vídeos órfãos) preenche playlists, vira porta de descoberta e puxa **sessão** (assistir em sequência). Liga-se à "Fortaleza de Vídeos" em `piramide-e-ideia.md`.

### Tags: importam, mas perderam força

Tags = etiquetas que dizem o tema ao robô; "importante, não único". Perderam força vs. o início do YouTube porque a plataforma ficou esperta contra **tag-stuffing** (pôr "Anitta/Neymar" num vídeo de cavalgada). Regra: escolha tags como **quem pesquisa aquele assunto**. Vídeo sem tags = robô com menos informação.

## Técnica do "canal fake"

Crie um **canal secundário "limpo"**, assista ~30s de 3–4 vídeos de vários canais do nicho para **treinar o algoritmo**, e use a home desse canal como **biblioteca de ideias/thumbnails/títulos** do que está funcionando AGORA — "é o YouTube te falando o que funciona, de graça". Refine com "não tenho interesse / não recomendar canal" para conteúdo fora do nicho. **Olhar crítico:** views altas ≠ replicável; vídeo "muito específico" engaja a base e não foi feito para trazer público novo.

## Prompts "Pergunte ao Studio"

> ⚠️ Recurso de 2026, dependente da UI atual. Descreva a *intenção* (extrair padrões dos top-vídeos), não a tela literal.

Quando o usuário tem **≥5 vídeos com histórico de 90 dias**, use os prompts em `assets/prompts-pergunte-ao-studio.md` para extrair: (1) padrão de tema dos 5 mais assistidos; (2) padrão visual das thumbnails dos 10 com maior CTR **cruzado com** mais views; (3) gatilhos/estrutura dos títulos mais assistidos. Reaproveite a saída (palavras magnéticas, 2–4 palavras na thumb, CAIXA ALTA) como defaults de empacotamento.

## "Views reais" / co-viewing

> ⚠️ Recurso emergente 2026, estimativa estatística com margem grande.

Métricas: **views** (quantas vezes o vídeo foi iniciado) × **espectadores únicos** (dispositivos) × **alcance real** (pessoas, considerando consumo coletivo na TV/sala). Um vídeo de 100k views pode ter sido visto por ~150k pessoas. Útil sobretudo para **negociar publi** (vender alcance qualificado) — sempre com o disclaimer de que é estimativa, não contagem exata.

## Alcance ≠ engajamento

Separe **alcance** (views, vpf, alcance real) de **engajamento** (like/comentário/share). A evidência cross-channel mostra que os maiores alcances (vpf alto) frequentemente têm **engajamento% baixo** — alcance amplo é função de CTR+retenção+empacotamento que atrai público frio, não de like/comentário por view. Engajamento **absoluto** na janela de teste é sinal positivo; engajamento **%** não prediz viralização. Ao reportar performance, não prometa que aumentar engajamento amplia alcance.

## Fontes

### Corpus Escola Para Youtubers (Caique)

- `taxa-de-cliques-do-youtube-e-o-algoritmo-tudo-que-voc-precisa-saber-10.md` — CTR, regra inversa, benchmark relativo, amostragem, onde achar.
- `ainda-precisa-fazer-seo-em-v-deos-do-youtube.md` — SEO básico × hard; 5 origens de tráfego; hierarquia.
- `funcion-rio-do-youtube-falou-sobre-esperar-para-publicar-um-v-deo.md` — mito 24–48h; regra 15–30 min.
- `o-youtube-mostra-exatamente-o-que-d-views-se-voc-fizer-isso.md` — técnica do canal fake; olhar crítico.
- `youtube-liberou-a-ia-que-diz-o-que-d-views-no-seu-canal.md` — prompts "Pergunte ao Studio"; palavras magnéticas; CAIXA ALTA.
- `nova-m-trica-de-views-reais-chegou-no-youtube.md` — views × únicos × alcance real (co-viewing).
- `n-o-o-algoritmo.md` — mito da frequência.
- `o-youtube-mudou-e-vai-te-prender-por-mais-tempo.md` — objetivo da plataforma: tempo de sessão.
- `como-esse-v-deo-bobo-explodiu-no-youtube.md` — retenção >100% via loop; engajamento expande entrega.
- `cross-channel-metrics` — vpf (alcance) × eng% (engajamento) em 7 canais.

### Corpus Camilo Coutinho (eixo SEO/busca)

- `voc-est-lendo-o-algoritmo-do-youtube-de-maneira-errada.md` — algoritmo quer relevância, não volume.
- `youtube-n-o-recomenda-canais-pequenos-a-verdade-playguntas-ep-029.md` — recomenda conteúdo, não canais; ~7–9 vídeos para entender o nicho.
- `seo-para-youtube-um-jogo-de-equipe-e-n-o-um-trabalho-solit-rio.md` — SEO é soma de elementos; desconfie de "morreu a tag/título".
- `qual-o-tempo-ideal-de-um-v-deo-para-indexar-no-youtube.md` — 10 min é monetização, não ranqueamento; duração = a do conteúdo.
- `como-criar-a-descri-o-do-youtube-perfeita-palestra-gratuita-camilo-coutinho.md` — descrição em 5 blocos ("Lego"); robô lê o vídeo pela descrição; acessibilidade.
- `entenda-como-funcionam-os-cap-tulos-do-youtube.md` — capítulos = subtítulos rankeáveis; só matam retenção em vídeo multi-tema.
- `encontre-playlists-usando-os-filtros-de-pesquisa-do-youtube-simples-e-pr-tico.md` — playlists como descoberta + conteúdo episódico.
- `tags-o-que-s-o-as-tags-para-v-deos-dicion-rio-de-v-deos.md` — tags importam mas perderam força; anti-stuffing; pense como quem pesquisa.
- `a-idade-do-canal-importante-para-o-ranqueamento-do-youtube-video-seo.md` — idade pesa pouco; comunidade/consistência pesa.
- `v-deos-antigos-tem-mais-visualiza-es-no-youtube-pois-s-o-melhores.md` — compare 28/90 dias; antigo ganha = pode ter mudado o tema.
- `7-perguntas-sobre-otimiza-o-de-v-deos-em-2-minutos.md` — indexar ≠ ranquear; subir não listado já otimizado.
