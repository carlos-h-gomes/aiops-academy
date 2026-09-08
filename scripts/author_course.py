"""Build the original, versioned Portuguese curriculum. No external content executed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = []

def lesson(day, title, track, summary, objectives, body, steps, deliverable, senior, source, lab, quiz):
    LESSONS.append(dict(day=day, title=title, track=track, summary=summary, objectives=objectives.split('|'), body=body.strip(), steps=steps.split('|'), deliverable=deliverable, senior=senior, sources=source.split('|'), lab=lab, quiz=[dict(question=q, options=opts, answer=answer, explanation=explanation) for q,opts,answer,explanation in quiz], minutes=180 if day in (7,14,21,28) else 300))

lesson(1, 'Seu primeiro plantão começa aqui', 'Fundamentos', 'Entenda o caminho de uma requisição e investigue seu primeiro incidente.',
'Diferenciar serviço, processo e servidor|Separar sintoma, hipótese e evidência|Priorizar impacto no usuário', r'''
## Antes de qualquer comando
Infraestrutura é o conjunto que permite uma aplicação funcionar: computadores, rede, armazenamento e serviços. Um servidor pode ser uma máquina física, uma máquina virtual ou um processo que atende pedidos. Um processo é um programa em execução. Um serviço é uma capacidade que alguém consome, como consultar uma cotação. Seu trabalho começa identificando qual capacidade falhou, para quem e desde quando.

Imagine uma consulta: navegador → DNS → balanceador → API → banco. DNS converte um nome em endereço. O balanceador distribui pedidos entre instâncias. A API aplica regras e consulta o banco. Uma página lenta pode ter origem em qualquer elo. Reiniciar a API sem investigar pode apagar evidências e deixar o banco igualmente lento.

## AIOps sem mistério
AIOps aplica análise de dados e IA à operação: agrupar alertas, detectar desvios, enriquecer incidentes e sugerir ações. Ansible executa configurações declaradas. Dynatrace ajuda a observar relações e comportamento. Uma sugestão de IA continua sendo uma hipótese até ser confrontada com sinais. Você precisa saber operar sem depender dela.

## Um método que cabe no plantão
1. Defina impacto: consultas falhando em uma região desde 09:05, por exemplo.
2. Compare com o normal: taxa de erros, latência, tráfego e saturação.
3. Monte duas hipóteses e diga qual observação refutaria cada uma.
4. Escolha uma mitigação reversível e de alcance limitado.
5. Verifique a experiência do usuário após agir e registre o aprendizado.

Disponibilidade e correção são diferentes: retornar HTTP 200 com uma cotação antiga é falha de qualidade. Ambiente de estudo usa dados fictícios; nunca copie informação corporativa para um assistente pessoal. Neste curso os consoles integrados são simulações explícitas. Os roteiros de laboratório real são outra etapa.

## Primeiro vocabulário
Host é uma máquina identificável. Deploy é uma nova versão instalada. Incidente é interrupção ou degradação não planejada. Runbook é um procedimento operacional repetível. Rollback é voltar a uma versão ou configuração anterior. Blast radius é quantos usuários e sistemas uma ação pode afetar. Não memorize apenas nomes: associe cada termo a uma decisão.
''', 'Abra o laboratório Plantão Linux e use help|Execute status, logs e metrics; anote horário, impacto e duas hipóteses|Compare a linha do tempo com changes|Explique em voz alta por que uma ação seria segura antes de remediar',
'Registro de incidente com impacto, dois indícios, hipótese descartada e próximo passo.',
'Separe mitigação de correção definitiva. Mostre qual informação faria você mudar de hipótese.',
'sre|otel', 'linux', [
('Uma API ficou lenta. Qual primeiro passo é mais útil?', ['Reiniciar todos os hosts','Definir impacto e comparar sinais com a linha de base','Trocar a ferramenta de monitoramento'],1,'Impacto e evidências orientam a investigação; reinícios amplos aumentam o alcance da falha.'),
('Uma sugestão de IA aponta o banco. Isso representa:', ['Uma hipótese a verificar','Prova definitiva','Autorização para alterar produção'],0,'A evidência precisa sustentar a hipótese; o modelo não concede autorização.')])

lesson(2, 'Linux: enxergue o que está acontecendo', 'Fundamentos', 'Arquivos, permissões, processos, memória e disco com um roteiro de diagnóstico.',
'Ler permissões e caminhos|Diagnosticar recurso saturado|Investigar antes de reiniciar', r'''
## Navegar com intenção
O Linux organiza arquivos a partir de /. /etc contém configurações; /var costuma conter dados variáveis e logs; /home guarda arquivos de usuários. pwd mostra onde você está, ls lista e cd muda de diretório. Caminho absoluto começa em /; relativo depende de onde você está. Use um diretório chamado aiops-lab dentro da sua home para os exercícios reais.

```bash
pwd
ls -lah
mkdir -p ~/aiops-lab
cd ~/aiops-lab
printf 'servico=cotacoes\n' > configuracao.txt
cat configuracao.txt
```

## Permissão não é decoração
Em rw-r-----, o dono pode ler/escrever, o grupo pode ler e outros não têm acesso. Os números 4, 2 e 1 representam leitura, escrita e execução. 640 significa rw-r-----. Dar 777 para resolver um erro distribui acesso desnecessário. Primeiro identifique usuário efetivo, dono e grupo. Um diretório precisa de execução para permitir travessia.

## Quatro perguntas de diagnóstico
CPU: há trabalho computacional ou espera? Memória: há pressão, swap ou processo morto pelo OOM killer? Disco: acabou espaço ou inodes? Rede: o processo está escutando a porta esperada? Carga média alta não significa automaticamente CPU alta; tarefas esperando I/O também influenciam.

```bash
ps aux
free -m
df -h
df -i
ss -lnt
systemctl status nginx --no-pager
journalctl -u nginx --since '10 minutes ago' --no-pager -n 40
```

Esses comandos são para uma VM/WSL Linux sua, quando o serviço existir. No console do app só as variantes listadas em help são aceitas. Não simula um shell completo. Um disco cheio pede identificar o consumidor e a política de retenção. Não apague logs cegamente: pode ser outro filesystem, um arquivo aberto ou uma necessidade de auditoria.

## Evidência útil
Registre valores com unidade e janela: disco 98% às 09:05, API com 22% de erros nos últimos cinco minutos. Depois de mitigar, compare a mesma janela e confirme que dados novos chegam. Ausência de logs pode ser falha do coletor, não saúde do serviço.
''', 'No console Linux, use df -h, free -m e journalctl -u quotes|Localize o recurso saturado e compare com os logs|Execute a remediação limitada indicada no help somente após reunir evidências|Valide com status e metrics; tente uma hipótese incorreta e compare',
'Runbook de disco cheio com diagnóstico, pré-condição, ação, validação e escalonamento.',
'Explique por que retenção, rotação e capacidade são controles diferentes. Inclua rollback quando a ação permitir.', 'linux|sre', 'linux', [
('Disco com espaço livre, mas não cria arquivos. O que investigar?', ['Inodes com df -i','Apenas CPU','Trocar DNS'],0,'Muitos arquivos pequenos podem esgotar inodes antes dos bytes.'),
('O que 640 permite?', ['Execução para todos','Dono lê/escreve; grupo lê; outros sem acesso','Todos escrevem'],1,'4=leitura, 2=escrita, 1=execução; os três dígitos separam dono, grupo e outros.')])

lesson(3, 'Redes, DNS e HTTP na prática', 'Fundamentos', 'Separe falha de resolução, conexão, TLS e aplicação.',
'Explicar DNS, TCP, TLS e HTTP|Interpretar códigos HTTP|Evitar retries que amplificam incidentes', r'''
## Siga as camadas
Uma URL como https://api.exemplo.test/cotacoes contém protocolo, nome e caminho. Primeiro o cliente resolve DNS; depois abre uma conexão TCP; em HTTPS negocia TLS para autenticar o servidor e proteger o tráfego; finalmente envia HTTP. Se DNS falha, nem houve conexão à API. Se a conexão é recusada, provavelmente ninguém escuta ali ou há rejeição ativa. Timeout pode envolver rede, fila ou dependência lenta.

Uma porta identifica um ponto de comunicação no host. 443 costuma atender HTTPS; esse costume não garante o serviço. 127.0.0.1 é loopback: o próprio computador. Dentro de um container, localhost é o próprio container, não outro serviço do Compose.

## HTTP é um contrato
GET consulta, POST normalmente cria ou dispara uma operação, PUT costuma representar substituição. 200 indica sucesso HTTP, 400 entrada inválida, 401 ausência/invalidade de autenticação, 403 falta de permissão, 404 recurso não encontrado, 429 limite e 5xx falha do servidor. Nunca suponha que repetir um POST é seguro. Use uma chave de idempotência quando o contrato prevê e reutilize a mesma chave para a mesma ação lógica.

```bash
curl -i --max-time 5 http://127.0.0.1:8765/api/v1/health
```

Esse exemplo consulta o app local quando ele está aberto. No Windows use curl.exe para não confundir com aliases antigos. O laboratório sintético aceita sua lista de comandos, não este terminal arbitrário.

## Timeout e retry
Defina prazo por tentativa e total. Exemplo didático: três tentativas, esperas de 1s e 2s com jitter, prazo total de 10s. Jitter espalha o retry para muitos clientes não voltarem ao mesmo tempo. Respeite Retry-After e interrompa diante de erro permanente. Timeout não prova que uma operação de escrita deixou de acontecer.

## Diagnóstico orientado por comparação
Compare uma instância saudável com a afetada, mesma janela e mesma rota. Trace IDs ligam eventos de uma requisição. Relógios desalinhados atrapalham a linha do tempo. Em nuvem, investigue rotas, resolução privada, security groups/firewalls e identidade separadamente. Não libere acesso global como teste.
''', 'No Plantão Linux compare status e logs|Desenhe DNS → TCP → TLS → HTTP → dependência e marque onde cada erro apareceria|Use curl.exe no health local em um terminal seu|Documente comportamento para 401, 403, 429 e 503',
'Tabela de sintomas com camada, comando de observação e ação de baixo risco.', 'Defina orçamento total de retries e explique duplicidade após timeout.', 'http|sre', 'linux', [
('Receber 403 normalmente pede investigar:', ['DNS antes de tudo','Permissão da identidade no recurso','Quantidade de memória do navegador'],1,'A resposta HTTP foi recebida; a autorização é o primeiro eixo a verificar.'),
('Um POST sofreu timeout. Qual risco existe ao repeti-lo?', ['Criar o mesmo efeito duas vezes','Nenhum, timeout desfaz a operação','Sempre corrompe DNS'],0,'O servidor pode ter concluído mesmo sem o cliente receber a resposta.')])

lesson(4, 'Windows e PowerShell para operações', 'Fundamentos', 'Observe serviços e eventos e entenda o gerenciamento com Ansible.',
'Ler objetos no PowerShell|Consultar serviço e evento|Entender WinRM e privilégios', r'''
## Objetos, não só texto
O PowerShell encadeia objetos. Get-Service retorna objetos com Name e Status. Where-Object filtra propriedades; Select-Object escolhe colunas. Isso reduz parsing frágil de texto, mas não elimina a necessidade de validar entradas.

```powershell
Get-Service | Select-Object -First 10 Name, Status
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, CPU
Get-WinEvent -LogName System -MaxEvents 10 |
  Select-Object TimeCreated, Id, LevelDisplayName
```

Execute as consultas em sua máquina de laboratório. Acesso a certos logs depende da permissão. Não use Start-Service, Restart-Service ou comandos administrativos em serviços do seu computador de trabalho sem um ambiente e uma mudança autorizados.

## Um serviço parado tem contexto
Investigue dependências, identidade que o executa, configuração, espaço em disco e evento anterior à parada. CPU no Get-Process é tempo acumulado, não uma porcentagem instantânea. Um serviço reiniciado e saudável por dez segundos pode continuar em um ciclo de falha. Valide estabilidade e função do usuário durante uma janela definida.

## Ansible com Windows
O nó de controle do Ansible deve ser um ambiente suportado; use Linux/WSL para estudo, não suponha execução nativa no Windows. Alvos Windows usam módulos próprios, como ansible.windows.win_service. Transporte e autenticação são parte do desenho: WinRM/PSRP, certificados, políticas e identidade de menor privilégio. Não desative a validação TLS para fazer funcionar.

## Caminhos e segurança
Use -LiteralPath quando um caminho deve ser tratado literalmente. Aspas protegem espaços; curingas podem expandir além do desejado. No YAML, aspas simples ajudam a preservar barras de caminhos Windows. O editor didático suporta apenas os módulos exibidos; não configura WinRM, não abre conexões e não testa autenticação real.
''', 'Execute apenas as três consultas de leitura do exemplo em ambiente pessoal|Liste diferenças entre nome do serviço e nome de exibição|No laboratório Ansible selecione o cenário Windows e corrija o serviço sintético|Escreva pré-requisitos de acesso para um host Windows real',
'Procedimento de investigação Windows com três consultas e interpretação dos resultados.', 'Explique como falha de credencial difere de falha do serviço e como evitar segredo em log.', 'powershell|ansible-windows', 'ansible-windows', [
('O pipeline PowerShell transporta principalmente:', ['Objetos com propriedades','Somente strings sem estrutura','Pacotes TCP'],0,'Cmdlets normalmente retornam objetos, que podem ser filtrados por propriedade.'),
('Ansible para serviço Windows deve usar:', ['apt','ansible.windows.win_service','chmod 777'],1,'Módulos Windows refletem a plataforma e não são intercambiáveis com módulos Linux.')])

lesson(5, 'Python do zero: dados viram decisões', 'Fundamentos', 'Leia JSON, agrupe eventos e trate erros de maneira previsível.',
'Usar listas, dicionários e funções|Distinguir parsing e validação|Construir classificação determinística', r'''
## O essencial para automação
Uma variável dá nome a um valor. Uma lista guarda uma sequência; um dicionário mapeia chaves para valores. if escolhe caminhos, for percorre dados e def declara uma função. Indentação faz parte da sintaxe. Comece com funções pequenas que recebem dados e retornam resultado, sem rede nem escrita em disco.

```python
eventos = [
    {"service": "quotes", "status": 503},
    {"service": "quotes", "status": 200},
    {"service": "orders", "status": 200},
]

def taxa_erro(itens):
    if not itens:
        return None
    erros = sum(1 for item in itens if item["status"] >= 500)
    return erros / len(itens)

assert taxa_erro([]) is None
assert taxa_erro(eventos) == 1 / 3
print(taxa_erro(eventos))
```

None comunica ausência de medida. Retornar zero para uma amostra vazia faria um painel parecer saudável sem observações. O resultado é uma fração; multiplique por 100 apenas ao apresentar porcentagem.

## Parsear não é confiar
json.loads transforma texto JSON em objetos. Ainda é preciso checar campos, tipos, limites e significado. Um status como "quebrou" não serve como número HTTP. Não use eval para interpretar dados. Capture exceções específicas, acrescente contexto seguro e falhe de forma explícita; except: pass esconde perda de dados.

## Automação operável
Use timeout para rede, logs estruturados sem segredos, um correlation_id e resultado estável. Uma função pura pode ser testada com casos vazios, limítrofes e inválidos. A regra de retry deve distinguir falha transitória de permanente e preservar a chave de idempotência. Nunca coloque token diretamente no código.

No kit labs/real/python existe um exercício incompleto e testes. Edite o arquivo e rode o verificador local em terminal. O app não executa código arbitrário: o laboratório integrado de dados corrige o resultado calculado, enquanto o kit verifica sua implementação Python de verdade.
''', 'Copie o exemplo para um arquivo em sua pasta de estudo e rode com Python|Abra labs/real/python/exercise.py e implemente as funções propostas|Execute python labs/real/python/check.py no diretório do app|No laboratório de dados calcule taxa de erro e deduplicação; registre a diferença entre vazio e zero',
'Funções Python com testes para lista vazia, dados inválidos e evento duplicado.', 'Separe erro de negócio de erro de transporte e mostre como retomaria processamento parcial.', 'python|aws-lambda', 'events', [
('Sem observações, uma taxa deve ser:', ['Sempre 0%','Sempre 100%','Ausente, com estado de dados insuficientes'],2,'Zero comunicaria sucesso sem evidência.'),
('json.loads garante que o dado é válido para seu domínio?', ['Não; ainda precisa validar campos, tipos e limites','Sim; JSON válido é dado confiável','Só quando usa aspas duplas'],0,'Sintaxe e semântica são camadas diferentes de validação.')])

lesson(6, 'Git, APIs e mudanças revisáveis', 'Fundamentos', 'Transforme uma correção local em algo que outra pessoa consegue revisar.',
'Entender working tree, stage e commit|Revisar diff sem segredos|Definir contrato HTTP', r'''
## Um histórico explicável
Git guarda versões. Working tree é seu diretório editável; stage seleciona o que entrará no próximo commit; commit registra um conjunto de mudanças. Branch permite uma linha de trabalho; pull request permite revisão em um servidor de colaboração. Um commit não é deploy. Use um repositório descartável para aprender, sem publicar nada.

```bash
git init
git status
git diff
git diff --staged
```

Execute git init somente na pasta nova de exercício. Crie README.md, selecione-o com git add README.md e observe o diff staged. Se sua identidade Git não estiver configurada, não precisa alterá-la globalmente para entender o fluxo. Um erro já versionado exige avaliar histórico e rotação do segredo; apagar a linha não remove versões antigas.

## Contrato de uma API
Documente método, caminho, campos, tipos, erros, limite e autenticação. Exemplo fictício: POST /v1/remediations recebe incident_id, action_id e idempotency_key. A identidade do chamador é verificada pelo servidor; receber um campo approved=true do cliente não prova aprovação. A política deve consultar uma autorização confiável.

## Antes de propor uma automação
Escreva problema, comportamento desejado, riscos, forma de testar e rollback. O diff deve ter uma intenção. Revisão útil procura efeitos colaterais, credenciais, alvos amplos, valores mágicos, tratamento de falha e documentação divergente. Check mode e um teste verde têm cobertura limitada, não são autorização de produção.

## Configuração e código
Parâmetros mudam por ambiente; regras e contratos precisam ser versionados. Arquivos .env e credenciais ficam fora do histórico. Não copie exemplos que enviem dados reais para destinos não aprovados. Neste curso só há leitura de fontes públicas e exemplos sintéticos; você prepara o artefato antes de escolher qualquer destino externo.
''', 'Crie uma pasta descartável e observe git status antes/depois de editar um README|Escreva um contrato de remediação com respostas 200, 400, 403 e 409|Revise o diff e liste cinco verificações de segurança|Resolva o laboratório de aprovação e deduplicação sem executar ação real',
'Descrição de mudança com contrato, evidência de teste e plano de rollback.', 'Explique como uma revisão detecta autorização confiada indevidamente ao frontend.', 'git|http', 'workflow', [
('Um commit equivale a:', ['Publicação em produção','Uma versão registrada no histórico','Uma aprovação de segurança'],1,'Commit é versionamento, independente de revisão ou implantação.'),
('O cliente enviou approved=true. O servidor deve:', ['Confiar porque é JSON','Conferir autorização no limite do recurso','Desativar autenticação'],1,'A autoridade precisa existir no servidor, não em um campo controlado pelo cliente.')])

lesson(7, 'Checkpoint 1: diagnosticar sem adivinhar', 'Revisão', 'Consolide a base com um incidente e recupere os pontos que faltaram.',
'Investigar sem consultar solução|Revisar fundamentos por recuperação ativa|Escrever um handoff claro', r'''
## Dia de consolidar — 3 horas
Não adicione uma ferramenta nova. Reserve 30 minutos para explicar Linux, DNS, HTTP, Python e Git sem abrir as notas. Marque o que não consegue explicar em linguagem simples. A recuperação ativa revela lacunas que reler o texto costuma esconder.

Passe 90 minutos no Plantão Linux: abra um cenário novo, colete evidências e resolva sem consultar a solução. Anote a sequência, inclusive tentativas incorretas. Use os 60 minutos restantes para o simulado da semana e para reescrever seu runbook.

## O que precisa aparecer na entrega
Impacto observável, hora inicial, serviço afetado, duas hipóteses, observações que as sustentam ou refutam, ação de alcance limitado e validação após a mudança. Se você só escreveu "reiniciei e voltou", a causa e a recorrência continuam desconhecidas.

## Revisão com critério
Consegue distinguir conexão recusada de resposta 403? Consegue explicar por que um disco cheio pode impedir uma aplicação de registrar logs? Seu cálculo de erro lida com lista vazia? Consegue apontar a diferença entre um arquivo alterado e um commit? Para cada não, volte apenas à seção correspondente e refaça uma tarefa diferente.

## Comunicação em 60 segundos
Estruture assim: impacto, o que sabemos, o que ainda não sabemos, ação em curso, risco e próximo horário de atualização. Evite afirmar causa raiz com um único sinal. É legítimo escalar quando a próxima ação exige autoridade ou conhecimento que você não tem; envie evidências e uma pergunta específica.

Uma nota alta no quiz mede reconhecimento. O incidente mede execução em um ambiente didático. A rubrica do portfólio ajuda você a avaliar clareza e autonomia, mas não concede nível profissional. Repita no laboratório real apenas as etapas para as quais você tem um ambiente pessoal apropriado.
''', 'Refaça o lab Linux sem solução|Complete o simulado Fundamentos e revise cada erro|Compare o primeiro runbook com sua nova versão|Agende revisão dos conceitos que ainda exigiram consulta',
'Handoff de incidente de uma página e lista de três lacunas prioritárias.', 'Declare incerteza sem perder clareza sobre a próxima ação.', 'sre', 'linux', [
('Um handoff útil contém:', ['Somente o nome de quem errou','Impacto, evidências, ações e próximo passo','Toda a saída bruta de todos os sistemas'],1,'Informação selecionada permite continuar a investigação sem expor dados desnecessários.'),
('Uma causa raiz deve se apoiar em:', ['Coincidência temporal apenas','Evidências e teste de hipóteses alternativas','Quantidade de ferramentas usadas'],1,'Mudanças simultâneas podem ser correlacionadas sem serem a causa.')])

lesson(8, 'Ansible: inventário e estado desejado', 'Ansible', 'Faça sua primeira alteração declarativa em hosts sintéticos.',
'Separar nó de controle e alvos|Selecionar inventário limitado|Entender idempotência', r'''
## O modelo mental
Ansible descreve um estado desejado em playbooks YAML e executa módulos nos alvos do inventário. O nó de controle inicia o trabalho. O inventário relaciona nomes, grupos e parâmetros de conexão. Uma play aplica tarefas a um conjunto de hosts. Um módulo encapsula uma operação, como garantir pacote instalado.

```yaml
- name: Preparar servidores web de laboratório
  hosts: webservers
  tasks:
    - name: Garantir nginx
      ansible.builtin.package:
        name: nginx
        state: present
    - name: Manter nginx em execução
      ansible.builtin.service:
        name: nginx
        state: started
```

No app existem dois webservers Linux e um host Windows sintético. O exemplo não instala nada na sua máquina. Rode duas vezes: a primeira muda estado, a segunda deve reportar ok sem changes. Isso ilustra idempotência: repetir converge ao mesmo estado, sem efeitos extras desnecessários.

## Inventário evita acidentes
Um grupo não é uma autorização. hosts: all pode alcançar máquinas que não deveriam mudar. Inspecione --list-hosts e use --limit em um laboratório real. Separe inventários de estudo e produção; nunca mantenha credenciais de produção no diretório do exercício.

## YAML essencial
Use espaços, nunca tabs para indentação. Hífen inicia item de lista; chave seguida de dois pontos abre um mapeamento. Uma tarefa tem exatamente um módulo. Distinguir erro de YAML de erro do módulo poupa tempo. O editor integrado rejeita recursos fora do subconjunto suportado em vez de fingir que funcionam.

## Idempotência tem limites
state: restarted reinicia sempre e portanto tende a changed em cada execução. Um shell arbitrário pode sempre mudar algo. Idempotência também depende de entrada, alvo, módulo e versão. O resultado changed não significa sucesso funcional: ainda é necessário verificar o serviço que o usuário consome.
''', 'Execute o playbook no lab Ansible Linux|Observe hosts, tarefas e contador de mudanças|Execute novamente e confirme zero mudanças|Troque o alvo para windows e explique por que o módulo Linux deve falhar',
'Playbook de duas tarefas e comparação documentada entre primeira e segunda execução.', 'Diferencie idempotência, convergência e sucesso funcional com um contraexemplo.', 'ansible|ansible-playbooks', 'ansible', [
('Depois da convergência, a segunda execução deveria:', ['Alterar tudo novamente','Reportar zero mudanças quando o estado não mudou','Apagar o inventário'],1,'Tarefas idempotentes não repetem efeitos quando o estado já está correto.'),
('O inventário define:', ['Alvos e agrupamentos','Aprovação irrestrita','Todas as senhas em texto'],0,'Inventário descreve alvos, não concede autoridade para alterá-los.')])

lesson(9, 'Playbooks: observar, alterar, verificar', 'Ansible', 'Escreva tarefas pequenas e interprete o recap.',
'Distinguir ok, changed, failed e unreachable|Usar check mode com consciência|Definir pós-condição', r'''
## Resultado de tarefa
ok indica que a tarefa executou sem precisar mudar o estado. changed indica alteração reportada. failed é falha da tarefa. unreachable significa que não foi possível alcançar o host pelo transporte. Ignore erros somente quando o contrato permite uma alternativa clara; ignorar indiscriminadamente transforma falha em silêncio.

No Ansible real, módulos podem ter check mode e diff. --check tenta prever sem modificar, quando suportado. Não é emulação perfeita e não garante todos os efeitos. --diff pode revelar conteúdo sensível. Use --syntax-check primeiro, --list-hosts para escopo e depois check/diff no inventário de estudo.

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml --list-hosts
ansible-playbook -i inventory.ini site.yml --check --diff --limit lab
```

Esses comandos pertencem ao kit real, com arquivos e dependências preparados. O lab integrado possui um toggle próprio de check mode; ele compara cópias de estado e não substitui o comportamento real de todos os módulos.

## Tarefa bem escrita
Dê nome orientado ao objetivo. Prefira módulo específico a shell. Use fully qualified collection name para tornar a origem explícita. Estado desejado não deve depender de uma sequência frágil de comandos. Uma pós-condição deve testar o resultado consumível: serviço ativo e resposta válida, não apenas pacote instalado.

## Falha parcial
Em vários hosts, um pode mudar antes de outro falhar. Você precisa saber quais mudaram e como retomar. Uma tarefa de download pode funcionar, mas a configuração seguinte falhar. Canário reduz alcance; limites de falha e serialização devem ser projetados para o tipo de mudança. No simulador a validação de sintaxe acontece antes da aplicação; isso é uma simplificação explicitamente didática.

No exercício real de localhost o playbook só escreve uma configuração dentro de labs/real/ansible/workspace. Você pode repetir e comparar recap, sem instalar pacotes do sistema nem pedir sudo.
''', 'Rode check mode no lab e confirme que o estado final não foi persistido|Execute de verdade no simulador e rode novamente|Provoque erro de indentação e depois erro de módulo; compare os feedbacks|Leia o kit real de localhost e execute syntax-check antes de qualquer apply local',
'Recap comentado, escopo do inventário e pós-condição funcional.', 'Planeje retomada após falha parcial sem ampliar o conjunto de alvos.', 'ansible-playbooks|ansible-check', 'ansible', [
('Check mode garante que todo módulo foi simulado perfeitamente?', ['Sim','Não; a cobertura varia por módulo e contexto','Só em produção'],1,'É evidência parcial, não prova completa da mudança.'),
('Pacote instalado prova que a função do serviço funciona?', ['Não; ainda é preciso verificar a pós-condição','Sim','Só se changed=1'],0,'Processo, configuração e dependências podem continuar falhando.')])

lesson(10, 'Variáveis, templates e handlers', 'Ansible', 'Separe dados da configuração e reinicie apenas quando necessário.',
'Entender variáveis e precedência|Relacionar mudança a handler|Ler template Jinja com segurança', r'''
## Configuração reutilizável
Variáveis deixam um playbook funcionar em ambientes diferentes sem duplicar lógica. defaults de uma role são valores facilmente sobrescritos; group_vars e host_vars descrevem grupos e hosts; extra-vars têm precedência elevada. Evite redefinir a mesma variável em muitos lugares: uma configuração pode parecer correta no arquivo e receber outro valor em execução.

```yaml
- name: Configuração local didática
  hosts: lab
  vars:
    message: observabilidade habilitada
  tasks:
    - name: Renderizar configuração
      ansible.builtin.template:
        src: templates/agent.conf.j2
        dest: "{{ playbook_dir }}/workspace/agent.conf"
        mode: '0600'
      notify: Registrar alteração
  handlers:
    - name: Registrar alteração
      ansible.builtin.debug:
        msg: Configuração mudou; em um serviço real, validar antes de recarregar.
```

Um template Jinja interpola valores, como message={{ message }}. Quoting importa: mode: '0600' deve preservar a intenção. O kit real inclui esse padrão. Este exemplo avançado não cabe no interpretador sintético de módulos; pratique no kit de localhost.

## Por que handlers existem
Uma tarefa notifica um handler quando reporta changed. Notificações para o mesmo handler normalmente se agrupam; o handler roda no ponto de execução apropriado, em geral ao fim da seção. Isso evita reiniciar o mesmo serviço depois de cada arquivo. Erros e flush_handlers alteram o fluxo: consulte a documentação antes de depender de ordem específica.

## Não renderize e torça
Valide a configuração antes da troca ou recarga quando o módulo/aplicação suportar. Um template sintaticamente válido pode gerar uma configuração inválida. Faça uma mudança por vez, veja o diff permitido e compare a segunda execução. Nunca inclua segredo em um template que será versionado ou exportado como evidência.

Use o laboratório integrado para treinar a diferença entre started e restarted. A configuração real com templates e handlers está no roteiro separado: a distinção existe para não ensinar comportamento falso do Ansible.
''', 'No simulador compare started com restarted em duas execuções|Abra o template e site.yml do kit Ansible real|Mude message apenas na pasta de estudo e rode check/diff|Explique quando o handler deveria rodar e quando não deveria',
'Template, variável de exemplo sem segredo e evidência de handler disparado apenas após mudança.', 'Mostre a cadeia de precedência que explica o valor efetivo e uma validação antes do reload.', 'ansible-vars|ansible-handlers', 'ansible', [
('Um handler costuma ser notificado quando:', ['Uma tarefa associada reporta changed','O arquivo contém comentário','Qualquer tarefa retorna ok'],0,'notify depende do resultado changed, com as regras de execução dos handlers.'),
    ('Reiniciar sempre com state: restarted:', ['É igual a garantir started','Pode produzir mudança em toda execução','É obrigatório para idempotência'],1,'started converge a um estado; restarted solicita uma ação a cada execução.')])

lesson(11, 'Roles, segredos e execução limitada', 'Ansible', 'Organize automações sem esconder risco dentro de uma role.',
'Identificar responsabilidades de uma role|Entender Vault e no_log|Planejar canário e rollback', r'''
## Uma responsabilidade por role
Uma role organiza tasks/main.yml, handlers/main.yml, defaults/main.yml, templates e files. Seu valor é um contrato de entradas e efeitos, não apenas uma árvore de pastas. Uma role de configuração de agente deve dizer plataformas aceitas, variáveis obrigatórias, arquivos tocados, reinícios e como remover ou voltar a versão anterior.

## Segredo criptografado continua sendo segredo
Ansible Vault protege conteúdo em repouso. A senha/chave que o desbloqueia precisa vir de um mecanismo aprovado e separado. no_log reduz exposição da saída de uma tarefa; não elimina todo risco em debug, diff, histórico ou arquivos gerados. Use credenciais fictícias nos estudos; não coloque uma senha real em variável, print ou anotação do curso.

## Privilégio e alcance
become aumenta privilégio quando necessário, não torna o playbook correto. Uma operação de leitura não deveria exigir administrador. Planeje um host canário, janela, condição de parada e limite de falhas. serial controla lotes; max_fail_percentage envolve semântica por lote que deve ser testada. Não copie um número sem entender a população de alvos.

```yaml
- name: Mudança gradual em inventário de estudo
  hosts: lab
  serial: 1
  tasks:
    - name: Verificar plataforma
      ansible.builtin.debug:
        msg: Primeiro valide o alvo e a janela de mudança.
```

## Rollback tem de ser específico
Voltar o pacote pode exigir configuração compatível e dados que não foram migrados. Antes de mudar, identifique o estado anterior e a reversibilidade. Um backup que nunca foi restaurado é uma hipótese. O kit real só altera arquivos em um workspace próprio; sua estratégia de retorno pode preservar uma cópia antiga antes de substituir a nova.

No laboratório de workflow, escolha a política que exige aprovação, restringe alvo, impede duplicação e verifica a saúde depois. Essa política não executa Ansible: exercita o raciocínio para uma automação corporativa.
''', 'Desenhe o contrato de uma role de agente de observabilidade|Liste dados que não podem aparecer no diff|Configure aprovação, canário e deduplicação no laboratório Workflow|Escreva condição de parada e rollback com verificação',
'Contrato de role e plano de mudança de um host canário.', 'Mostre um cenário em que rollback de pacote não restaura dados e exija tratamento separado.', 'ansible-roles|ansible-vault', 'workflow', [
('Vault resolve todos os vazamentos?', ['Sim','Não; runtime, logs e chave continuam exigindo controles','Só com become'],1,'Criptografia em repouso não controla toda a circulação de um segredo.'),
('Antes de uma mudança ampla, é preferível:', ['Um canário com critério de parada e validação','Todos os hosts ao mesmo tempo','Ignorar erros para terminar'],0,'Uma amostra limitada permite observar efeitos antes de ampliar o alcance.')])

lesson(12, 'AAP: automação como serviço interno', 'Ansible', 'Entenda controller, execution environments e workflows corporativos.',
'Mapear objetos da AAP|Separar criar, aprovar e executar|Projetar rastreabilidade', r'''
## O que a plataforma acrescenta
Ansible Automation Platform organiza execução e governança em equipe. No automation controller você relaciona organização, usuários/equipes, inventário, credencial, projeto e job template. Projeto aponta para conteúdo versionado; job template define como executar esse conteúdo. Workflow conecta etapas e decisões. Isso não substitui qualidade do playbook.

Um execution environment empacota dependências de execução, como collections e bibliotecas. Fixar e revisar versões reduz o caso "funciona na minha máquina". Atualizações exigem testes: pinning sem política de correção também envelhece. Roles externas devem ser revisadas como código de terceiros.

## Separação de poderes
Quem edita automação não precisa poder executar qualquer coisa em produção. Um operador pode lançar um template permitido sem visualizar a credencial. Surveys coletam parâmetros, mas precisam limitar escolhas: oferecer host livre ou comando arbitrário pode contornar o desenho do template. Aprovação deve estar vinculada à mudança e ao escopo efetivo.

## Um fluxo possível
Evento de monitoramento → enriquecimento somente leitura → seleção de runbook versionado → aprovação válida → canário → verificação → expansão limitada ou rollback → registro. Correlação preserva a ligação entre incidente, revisão Git, job e resultado. Credenciais não aparecem nesse registro.

## Falhas que você precisa antecipar
Projeto sem sincronizar pode usar conteúdo inesperado. Imagem de execução divergente pode quebrar módulo. Credencial expirada impede acesso. Inventário antigo aponta para alvo errado. Callback perdido não significa job não executado. Antes de repetir, consulte o resultado pelo identificador e preserve idempotência.

O curso inclui um simulador de política; não instala nem licencia AAP. Para prática real é necessário um ambiente de treinamento autorizado. No roteiro da biblioteca estão os objetos para criar e as evidências para coletar, sem usar nenhuma instância corporativa por inferência.
''', 'Desenhe projeto → execution environment → inventário → template → workflow|No laboratório, simule evento repetido e aprovação ausente|Defina permissões de autor, aprovador e operador|Escreva como descobrir se um job terminou quando o callback falhou',
'Desenho de workflow AAP com identidades, IDs de correlação e limites.', 'Evite parâmetros que transformam template limitado em execução arbitrária.', 'aap|ansible', 'workflow', [
('Execution environment serve para:', ['Empacotar dependências da execução','Substituir aprovação','Armazenar todas as senhas no código'],0,'Ele ajuda a reproduzir o ambiente de ferramentas e bibliotecas.'),
('Callback de job perdido significa que:', ['Nada executou','É preciso consultar o estado pelo ID antes de repetir','Todos os hosts falharam'],1,'Perda de confirmação e falha da ação são eventos diferentes.')])

lesson(13, 'Remediação Ansible em Linux e Windows', 'Ansible', 'Escolha a ação pela plataforma e valide o resultado.',
'Evitar módulo errado por plataforma|Definir pré e pós-condições|Investigar falha parcial', r'''
## Uma intenção, implementações diferentes
Manter um serviço funcionando pode exigir ansible.builtin.service em Linux e ansible.windows.win_service em Windows. O nome de pacote, caminho e mecanismo de privilégio também mudam. Não suponha que package universaliza todos os sistemas. Facts e condições ajudam a selecionar, mas precisam ser suportados e testados no ambiente real.

```yaml
- name: Serviço Windows de estudo
  hosts: windows
  tasks:
    - name: Garantir W3SVC iniciado
      ansible.windows.win_service:
        name: W3SVC
        state: started
```

No simulador W3SVC existe como dado; isso não instala IIS nem demonstra conectividade. O exemplo usa um serviço previamente instalado. Em ambiente real, verifique dependências, identidade de serviço e recurso consumível. Serviço started com aplicação retornando erro ainda é incidente.

## Antes de remediar
Confirme que o evento continua ativo, o alvo pertence ao inventário correto, a ação é permitida e a janela não expirou. Colete estado anterior e uma evidência de diagnóstico. Verifique se outra execução já está em andamento para evitar corrida. Escolha o menor alcance que teste a hipótese.

## Depois de remediar
Valide processo, endpoint e taxa de erro, com tempo suficiente para evitar falso positivo. Registre ação, revisão, alvo, resultado e duração. Se a condição piorar, pare a expansão e execute o retorno previsto. Se reaparece toda hora, o reinício virou toil: investigue causa, capacidade e mudança recente.

## Falha parcial não é detalhe
Se dois hosts mudaram e um falhou, não resuma "deu erro". Relate quais estados são conhecidos e desconhecidos. Uma execução repetida deve convergir sem repetir efeitos perigosos. O console didático permite treinar resultados por host; transporte, concorrência e autenticação reais ficam fora da simulação.
''', 'Execute o cenário Windows e confirme idempotência|Use um módulo Linux no alvo Windows e leia a rejeição|Compare os contratos dos dois playbooks|Escreva uma pós-condição de experiência do usuário, além de serviço iniciado',
'Dois playbooks pequenos e runbook com condição de parada para falha parcial.', 'Explique como impedir dois jobs concorrentes para o mesmo recurso.', 'ansible-windows|ansible-playbooks', 'ansible-windows', [
('Serviço started prova recuperação completa?', ['Sim','Não; verificar endpoint e experiência','Apenas no Windows'],1,'Estado do processo é um sinal, não toda a função do sistema.'),
('Falha parcial exige registrar:', ['Somente exit code','Alvos alterados, falhos e estado ainda desconhecido','Apenas tempo total'],1,'A retomada depende de saber o que realmente mudou.')])

lesson(14, 'Checkpoint 2: automação que converge', 'Revisão', 'Entregue um playbook repetível e explique seus limites.',
'Executar sem copiar solução|Demonstrar convergência|Revisar governança de automação', r'''
## Três horas de prova
Use 90 minutos para o laboratório Ansible sem abrir o exemplo pronto. Instale nginx nos dois webservers sintéticos e mantenha-o iniciado. Rode de novo; verifique zero mudanças. Faça o cenário Windows com o módulo correto. Registre uma falha proposital e sua explicação.

Reserve 45 minutos para o simulado Ansible e 45 para o portfólio. Se já preparou o kit localhost, compare a simulação com o recap real. Declare o que ainda não foi testado: SSH, credenciais, facts de hosts remotos e permissões não são exercitados pelo modelo local.

## Critérios da entrega
Inventário limitado, nomes de tarefas claros, módulos adequados, idempotência e validação. Acrescente contrato de entrada, plataforma suportada, dados alterados, condição de parada e recuperação. Outra pessoa deveria conseguir seguir o procedimento sem pedir os parâmetros básicos.

## Perguntas de revisão
Por que restarted pode gerar changed sempre? O que --check deixa de cobrir? Um survey que aceita qualquer host enfraquece qual controle? Como um callback perdido pode causar execução duplicada? Qual diferença entre pacote instalado e serviço funcional?

Se um conceito exigir consulta, revise só aquele trecho e refaça uma variação. A repetição espaçada no app agenda novamente itens que você errou ou marcou como difíceis. Não marque domínio por reconhecer uma alternativa que acabou de ver no gabarito.

## Evidência que se sustenta
Um screenshot isolado não explica contexto. Anexe em suas notas: versão do exercício, entrada usada, primeira e segunda saída, erro provocado e interpretação. Não cole tokens ou inventários reais. Para um iniciante, esse cuidado já mostra disciplina operacional; a ambição de sênior entra em antecipar as falhas e comunicar os limites.
''', 'Refaça os dois labs Ansible sem solução|Complete o simulado Ansible|Revise uma role usando a rubrica da aula 11|Publique apenas no portfólio local uma explicação de 2 minutos',
'Pacote de evidências Ansible com primeira execução, convergência e falha controlada.', 'Dê um exemplo em que um playbook idempotente ainda é perigoso por ter o alvo errado.', 'ansible|aap', 'ansible', [
('Idempotência garante alvo correto?', ['Não','Sim','Só com YAML'],0,'Uma automação pode convergir perfeitamente no recurso errado.'),
('Melhor prova de repetibilidade neste exercício:', ['Uma captura do editor','Entrada versionada e resultados da primeira e segunda execução','Nome do arquivo'],1,'A comparação evidencia se houve convergência e permite reproduzir.')])

lesson(15, 'Observabilidade: métricas, logs e traces', 'Observabilidade', 'Escolha o sinal certo para responder uma pergunta concreta.',
'Diferenciar sinais e unidades|Entender cardinalidade|Correlacionar uma requisição', r'''
## Três perspectivas
Métrica agrega números ao longo do tempo: requisições por segundo, erro ou duração. Log descreve um evento com contexto. Trace reúne spans de uma operação distribuída; cada span tem duração e relação com outros. Nenhum sinal resolve sozinho todos os diagnósticos. Comece pela pergunta e escolha o sinal mais econômico que a responde.

OpenTelemetry padroniza instrumentos e transporte de telemetria. Não é por si só um banco de dados ou painel. Um Collector pode receber, processar e exportar sinais; trate sua fila, memória, perda e saída como parte da operação. Dupla instrumentação pode criar duplicatas ou custo sem informação nova.

## Quatro sinais para um serviço
Latência mostra duração, tráfego mostra volume, erros mostram falha e saturação mostra proximidade do limite. P95=800ms significa que 95% das observações da distribuição ficaram em até 800ms; não é média. Não tire média simples de percentis de instâncias para obter o percentil global.

```json
{"timestamp":"2026-09-06T09:05:00Z","service.name":"quotes","loglevel":"ERROR","trace_id":"demo-0001","content":"upstream timeout","duration_ms":1200}
```

Todos os campos do exemplo são sintéticos. Timestamps devem indicar fuso; duração precisa de unidade. Identificadores permitem ligar a falha a um trace, mas usuário individual como label de métrica cria cardinalidade alta e risco de privacidade.

## Cardinalidade e qualidade
Um label com três regiões e dois ambientes é limitado. request_id com milhões de valores multiplica séries. Controle dimensões, retenção e amostragem. Coletar tudo não é estratégia; define custo e exposição. Diferencie ausência de sinal de valor zero e acompanhe a saúde da própria coleta.

## Exercício de investigação
O laboratório DQL contém logs de quotes, orders e collector. Filtre erros antes de agrupar por serviço. Compare contagem e duração sem declarar causalidade apenas por correlação. Depois siga o trace_id nos registros brutos e escreva qual hipótese você consegue sustentar.
''', 'Abra o DQL e observe campos e unidades do dataset|Filtre loglevel ERROR e agrupe por service.name|Volte aos registros brutos e encontre o trace do erro|Escolha labels limitados para uma métrica de requisições',
'Consulta, tabela de resultados e hipótese com limitação explícita.', 'Calcule o custo lógico de cardinalidade e explique amostragem sem esconder erro raro.', 'otel|sre', 'dql', [
('request_id como label de métrica costuma:', ['Reduzir todas as séries','Aumentar cardinalidade sem limite útil','Garantir privacidade'],1,'Cada valor distinto pode criar uma nova série ou combinação de séries.'),
('OpenTelemetry é:', ['Padrão e ferramentas de instrumentação/coleta/exportação','Um painel obrigatório','Uma licença Dynatrace'],0,'Pode enviar sinais a diferentes backends; não substitui armazenamento e visualização.')])

lesson(16, 'Dynatrace: navegue do problema à evidência', 'Dynatrace', 'Entenda OneAgent, ActiveGate, Grail e contexto de dependências.',
'Mapear coleta, armazenamento e análise|Investigar entidade e dependência|Tratar causa sugerida como hipótese verificável', r'''
## O que aprender primeiro
Comece pela visão de serviço: impacto, janela, erros, latência, dependências e alterações recentes. Depois desça até processo e host. Um problema no serviço pode ser consequência de uma dependência compartilhada. Conhecer a topologia evita abrir um incidente separado para cada sintoma.

OneAgent coleta e instrumenta tecnologias suportadas nos modos apropriados. ActiveGate pode atuar em caminhos de comunicação e extensões conforme o desenho. Grail é a camada de dados consultada por DQL na experiência atual. O que você vê depende da versão, licença, permissões e configuração do tenant. Não suponha que todo recurso foi habilitado.

## Vocabulário que você pode encontrar
Smartscape representa contexto de dependências. Nas fontes atuais, Dynatrace Intelligence é o nome da família de recursos de análise que também aparece em referências históricas como Davis AI. Confirme a terminologia do seu ambiente. Correlação de eventos e contexto topológico ajudam a identificar causa provável; sua ação ainda exige evidências e política.

## Roteiro em um tenant de treinamento
1. Ajuste a janela e o fuso.
2. Abra um serviço conhecido e observe erros, volume e latência.
3. Escolha um problema e liste entidades afetadas.
4. Siga uma dependência e um trace; compare com alteração recente.
5. Registre evidência que contradiz uma hipótese inicial.

O app local não é uma instalação Dynatrace e não imita OneAgent ou a análise causal do fornecedor. A bancada DQL ensina um subconjunto sintático sobre dados fixos. A biblioteca liga à documentação e ao aprendizado oficial para a etapa real. Não precisa de cartão nem de token para estudar aqui.

## Instalação também é mudança
Antes de instalar agente de coleta: valide plataforma, permissão, escopo, dados coletados, egress, custo, modo e remoção. No trabalho, siga o padrão aprovado pelo time. Um agente observador pode exigir privilégios relevantes; não instale software em servidores da empresa como simples exercício.
''', 'Monte o mapa aplicação → coleta → armazenamento → consulta → problema|Use os logs sintéticos para identificar a dependência compartilhada|Leia o roteiro Dynatrace na biblioteca e marque o que depende de tenant|Escreva cinco perguntas de onboarding sobre instrumentação e acesso',
'Mapa de observabilidade e roteiro de investigação com limitações de acesso.', 'Questione cobertura, perda de coleta e relação temporal antes de aceitar uma causa sugerida.', 'dynatrace|oneagent|dql', 'dql', [
('Grail e DQL se relacionam como:', ['Camada de dados e linguagem de consulta','Duas versões do Ansible','Dois tipos de senha'],0,'DQL explora os dados armazenados no Grail; não é SQL tradicional.'),
('Uma causa sugerida pela plataforma pede:', ['Validar evidências e contexto antes de agir','Reiniciar sem aprovação','Desligar todos os alertas'],0,'A decisão operacional exige contexto, autoridade e validação.')])

lesson(17, 'DQL: investigue dados de verdade no exercício', 'Dynatrace', 'Filtre, agregue e ordene logs; não confunda DQL com SPL ou SQL.',
'Escrever um pipeline DQL|Interpretar contagem por grupo|Evitar perder contexto com agregação', r'''
## Um pipeline de transformações
DQL encadeia comandos com |. fetch inicia a leitura, filter mantém registros que atendem a uma condição, summarize agrega e sort ordena. O resultado de cada etapa alimenta a próxima. Campos podem conter ponto, como service.name. A consulta abaixo é um exemplo original compatível com o subconjunto ensinado:

```text
fetch logs
| filter loglevel == "ERROR"
| summarize total = count(), by:{service.name}
| sort total desc
```

No lab, quotes deve aparecer com três erros e orders com um. Os dados ficam visíveis na própria bancada. Você pode resolver com uma consulta diferente se produzir a mesma tabela; o corretor compara o resultado, não procura palavras-chave.

## Registros ou agregados?
Depois de summarize, content e trace_id deixam de representar um evento individual. Para investigar uma mensagem, volte à consulta sem a agregação. limit controla quantas linhas você vê; não transforme uma amostra limitada em taxa do universo. Filtrar apenas erros e contar não informa porcentagem sem o total de requisições na mesma população.

```text
fetch logs
| filter service.name == "quotes"
| fields timestamp, loglevel, content, trace_id
| limit 10
```

## Escopo da bancada
Suporta fetch logs; filter com igualdade de string ou comparação numérica simples; summarize alias=count(), by:{campo}; fields; sort campo asc/desc; limit até 100. Rejeita comandos ou funções fora disso. Não executa regex livre, rede, expressões Python ou DQL completo. Campos, registros e janela são fixos e sintéticos. Um recurso ausente no simulador não significa que o Dynatrace não o suporta.

## Na plataforma real
Restrinja janela e volume de leitura, confira permissões e unidade de dados. Salve uma consulta com descrição, dono e pergunta operacional. DQL, Splunk SPL e consultas OpenSearch têm sintaxes e modelos diferentes. Aprenda o conceito transferível e confira a documentação específica ao mudar de ferramenta.
''', 'Produza a tabela de erros por serviço no lab|Verifique o resultado contra os registros brutos|Remova summarize e projete campos para investigar um trace|Provoque erro de sintaxe e corrija com a ajuda do dialeto suportado',
'Duas consultas: visão agregada e investigação detalhada, com interpretação.', 'Explique por que contagem absoluta pode aumentar enquanto a taxa de erro diminui.', 'dql|dql-filter|dql-aggregate', 'dql', [
('Após summarize por serviço, você tem:', ['Um agrupamento com agregações','Todos os traces completos automaticamente','Uma alteração nos servidores'],0,'Agregação muda a granularidade e descarta o contexto individual não agrupado.'),
('Para calcular taxa de erro é preciso:', ['Apenas contar ERROR','Erros e total na mesma janela/população','A soma de percentis'],1,'Numerador e denominador precisam ter escopo consistente.')])

lesson(18, 'SLOs e alertas que merecem acordar alguém', 'Observabilidade', 'Calcule orçamento de erro e diferencie alerta útil de ruído.',
'Distinguir SLI, SLO e SLA|Calcular erro permitido e burn rate|Definir ação e condição de alerta', r'''
## Medida, objetivo e acordo
SLI é a medida: fração de requisições elegíveis bem-sucedidas. SLO é o objetivo: por exemplo, 99,9% nessa medida em 30 dias. SLA é um acordo com consequências e termos próprios. Não derive um SLA contratual de um objetivo didático.

Para um SLO baseado em requisições, um milhão de pedidos elegíveis com meta 99,9% permite mil falhas. Se houver 1.400, o orçamento foi excedido em 400. Para um SLO baseado em tempo com 30 dias completos, 0,1% equivale a 43,2 minutos. São modelos distintos: não misture falhas por requisição e indisponibilidade por tempo.

## Velocidade de consumo
Burn rate = taxa de erro observada / fração de erro permitida. Com meta 99,9% e 2% de erro, burn rate=20. Se o comportamento persistir, o orçamento será consumido muito mais rápido que o planejado. Janelas curtas detectam rápido, longas reduzem ruído. Uma política real precisa considerar tráfego mínimo e múltiplas janelas.

## Um alerta deve carregar uma ação
Inclua serviço, impacto, janela, limiar, owner, rota de escalonamento e runbook. Alertar CPU sem consequência clara pode produzir fadiga. Ausência de dados exige regra própria: telemetria quebrada não deve ser exibida como zero erros. Um sintoma transitório não pede a mesma urgência que consumo sustentado do orçamento.

## Laboratório numérico
Calcule os valores apresentados na bancada SLO. O corretor usa fórmula e tolerância numérica; escreva unidades na evidência. Compare uma mudança de tráfego e uma mudança de erro. Um dashboard útil deve ter saúde, qualidade dos dados e ligação para investigação, não apenas números vistosos.

## Para se destacar
Discuta exclusões e população: quais requisições são elegíveis? Dados atrasados contam? Endpoint health representa o usuário? Quem decide suspender mudanças quando o orçamento acaba? Essas definições precisam do produto e do time; não são um número escolhido isoladamente por operações.
''', 'Calcule falhas permitidas, excedente e burn rate na bancada|Explique a diferença entre SLO por tempo e por requisições|Escreva um alerta com janela, ação, owner e runbook|Modele um caso sem tráfego e outro com coletor parado',
'Documento de SLO com fórmula, unidades, população e política de alerta.', 'Discuta burn rate com duas janelas e o risco de alerta sem tráfego mínimo.', 'sre-slo|sre-alert', 'slo', [
('Meta 99,9%, taxa observada de erro 2%. Burn rate:', ['2','20','2000'],1,'2% / 0,1% = 20; use unidades consistentes.'),
('Sem telemetria, o painel deve:', ['Mostrar saúde verde','Sinalizar falta de dados e investigar coleta','Inventar média'],1,'Ausência de sinal não prova ausência de erro.')])

lesson(19, 'AWS: S3 e Lambda em um pipeline de eventos', 'Cloud', 'Armazene objetos e processe eventos com menor privilégio e idempotência.',
'Entender objeto, bucket, prefixo e evento|Tratar repetição e ordem|Separar IAM de política de recurso', r'''
## S3 é armazenamento de objetos
Um bucket contém objetos identificados por chave; prefixo é parte do nome, não um diretório POSIX. Versionamento mantém versões e ajuda em recuperação, mas não substitui política de retenção e controle de acesso. Criptografia, bloqueio de acesso público, identidade e política do bucket resolvem dimensões distintas. Não use bucket público para logs operacionais.

## Lambda reage a eventos
Uma função recebe um evento e executa com uma identidade de runtime. Configuração inclui memória, timeout, concorrência e origem. A mesma role não precisa de acesso irrestrito à conta. Conceda leitura apenas no prefixo necessário e escrita somente no destino previsto. Logs não devem serializar o evento inteiro sem revisão.

Notificações e processamento podem repetir ou chegar fora de ordem. Desenhe um identificador estável para o efeito lógico. Para eventos de objeto, bucket, key e versionId quando disponível podem compor a identidade; trate os formatos e a codificação da chave conforme o evento. Não use somente horário local do consumidor.

## Pipeline proposto
Objeto sintético em prefixo de entrada → notificação → função valida e normaliza → resultado em prefixo de saída → erro controlado para reprocessamento. Evite que a saída dispare a mesma entrada em loop. Um ledger de idempotência precisa de escrita atômica, estado e estratégia para falha após reserva. Um set em memória não sobrevive a novas instâncias.

## Prática sem conta
O kit Python fornece eventos repetidos e um objeto malformado. Implemente validação e deduplicação, depois rode os testes. A bancada de dados verifica os resultados esperados. Ela não emula AWS nem comprova IAM, cold start ou retries da plataforma.

## Prática opcional na AWS
Em sandbox autorizado, siga o roteiro da biblioteca: região definida, bucket privado, prefixos distintos, role limitada, função com timeout/concorrência limitados, evento sintético e verificação de duplicidade. Defina orçamento e limpeza antes de criar. O app não provisiona nem armazena credenciais. Custos e recursos habilitados devem ser conferidos na conta.
''', 'Desenhe bucket/prefixos, produtor, função e destino|Resolva a deduplicação com fixture do lab de dados|Implemente o exercício Python e prove comportamento com evento repetido|Escreva política conceitual de menor privilégio e condição anti-loop',
'Pipeline S3 → Lambda com chave idempotente, tratamento de erro e checklist de remoção.', 'Explique a falha entre reservar o evento e concluir o efeito, incluindo retomada.', 'aws-s3|aws-lambda|aws-events', 'events', [
('Uma função acionada por evento deve assumir:', ['Entrega sempre única e ordenada','Possibilidade de duplicidade e reordenação conforme origem','Que memória local é ledger durável'],1,'O consumidor precisa tolerar a semântica de entrega da fonte.'),
('Para evitar loop S3 → Lambda → S3:', ['Separar entrada/saída e filtrar o gatilho','Usar bucket público','Aumentar retries sem limite'],0,'A saída não deve reativar indiscriminadamente o mesmo processamento.')])

lesson(20, 'AWS OpenSearch: logs pesquisáveis', 'Cloud', 'Entenda índices, mappings, consultas e operação do armazenamento.',
'Separar text e keyword|Consultar logs via Query DSL|Planejar retenção e capacidade', r'''
## De eventos a documentos
OpenSearch indexa documentos JSON para busca e análise. Um índice tem mappings, que definem o tratamento dos campos. text costuma ser analisado para busca textual; keyword preserva valores exatos, útil para serviço e ambiente. timestamp precisa de tipo date e duração deve ser numérica com unidade documentada. Mapping errado pode dificultar agregações e exigir reindexação.

```json
{
  "size": 0,
  "query": {"term": {"loglevel": "ERROR"}},
  "aggs": {"por_servico": {"terms": {"field": "service.name"}}}
}
```

O exemplo pressupõe loglevel e service.name mapeados como keyword. Em outro mapping pode ser necessário o subcampo .keyword. Confira antes de copiar. A bancada OpenSearch aceita exatamente essa família pequena de Query DSL sobre fixtures; não usa Lucene nem executa o motor real.

## Shards e réplicas
Shards dividem o índice; réplicas copiam shards para disponibilidade e leitura. Muitos shards pequenos criam overhead; réplicas não substituem snapshots. Uma réplica na mesma zona não protege contra perda da zona. Index lifecycle/retention e snapshots devem ter owner, objetivo de recuperação e teste de restauração.

## Operação e segurança
Monitore latência de indexação/busca, rejeições, heap, disco e saúde do cluster. Bulk requests reduzem overhead, mas precisam de lotes limitados e leitura dos erros por item: HTTP de sucesso pode conter falhas parciais na resposta bulk. Trate backpressure; retry ilimitado pode piorar a saturação.

No serviço AWS, acesso envolve políticas, rede e mecanismos de autenticação compatíveis com o modo implantado. VPC e criptografia não equivalem a autorização de cada operação. Uma identidade que ingere logs não precisa administrar o domínio. Planeje orçamento e retenção antes de habilitar ingestão contínua.

## Comparação útil
S3 guarda objetos e pode apoiar arquivo e recuperação. OpenSearch mantém índices pesquisáveis. Dynatrace oferece observabilidade integrada e seu modelo de dados/consulta. Cada escolha deve responder a uma pergunta operacional com custo, latência e governança conhecidos, sem duplicar coleta por hábito.
''', 'Monte a agregação de erros por serviço na bancada OpenSearch|Compare o resultado com a consulta DQL do dia 17|Defina mapping para timestamp, serviço, erro e duração|Descreva tratamento de erro por item e política de retenção',
'Query DSL, contrato de mapping e plano de retenção/restauração.', 'Justifique particionamento por volume e retenção, evitando um índice por usuário ou request.', 'opensearch|aws-opensearch', 'opensearch', [
('Para agregação exata de nome de serviço, normalmente use:', ['keyword','Texto analisado sem avaliar mapping','Uma imagem'],0,'keyword preserva o valor completo para agrupamento e filtro exato.'),
    ('Uma resposta bulk HTTP 200 significa:', ['Todos os itens obrigatoriamente gravaram','É preciso conferir falhas por item','Snapshot restaurado'],1,'Bulk pode reportar falhas parciais no corpo mesmo com transporte bem-sucedido.')])

lesson(21, 'Checkpoint 3: do log ao impacto', 'Revisão', 'Investigue o mesmo conjunto de eventos em DQL e OpenSearch.',
'Comparar consultas sem confundir sintaxe|Interpretar métricas com denominador|Consolidar pipeline AWS', r'''
## Três horas com uma pergunta
Qual serviço concentra erros e como isso afeta o usuário? Use 60 minutos para produzir a tabela de erros em DQL e OpenSearch sem copiar a solução. Verifique o resultado contra os registros originais. Uma tabela idêntica não significa motores idênticos; as bancadas são subconjuntos didáticos.

Use 45 minutos para calcular o SLO e escrever um alerta. Use outros 45 para o simulado de observabilidade/cloud. Nos 30 finais revise seu pipeline S3/Lambda, explicando duplicidade, falha parcial e restrição de acesso.

## Compare a mesma população
Se o dashboard de erros usa cinco minutos e o total usa uma hora, a taxa é inválida. Se você contou logs de erro, talvez tenha várias linhas por requisição. Se um serviço ficou sem telemetria, seu ranking pode sumir justamente quando ele precisa de atenção. Declare o que o dataset mede e o que não mede.

## Produza duas visões
Para plantão: impacto, urgência, responsável e próximo passo. Para engenharia: janela, população, consulta, distribuição, dependência, alteração recente e hipótese testável. A mesma investigação pode produzir comunicações diferentes sem contradizer os fatos.

## Corrija a fraqueza mais importante
Se você erra sintaxe, refaça a consulta com um campo diferente. Se erra interpretação, escreva um contraexemplo: mais erros absolutos com menor taxa porque o tráfego cresceu. Se confunde serviço de nuvem, desenhe quem armazena, quem processa, quem indexa e quem tem permissão. Não avance acumulando nomes sem função.

Ao registrar evidência, inclua as consultas, os valores esperados e suas limitações. Não transforme números sintéticos em alegações sobre ambientes reais ou sobre qualquer organização.
''', 'Resolva DQL e OpenSearch sem solução|Compare consultas e resultados com uma contagem manual|Complete o simulado de observabilidade/cloud|Escreva resumo de incidente em até 120 palavras',
'Duas consultas equivalentes, alerta com SLO e resumo operacional.', 'Demonstre como perda de observabilidade distorce a conclusão e como detectar essa perda.', 'dql|opensearch|sre', 'dql', [
('Contar linhas ERROR equivale sempre a contar requisições falhas?', ['Sim','Não; uma requisição pode gerar várias linhas','Somente no Linux'],1,'A granularidade do evento precisa ser definida antes da métrica.'),
('Uma comparação de taxa exige:', ['Mesma janela e mesma população','Apenas títulos parecidos','Cores iguais no painel'],0,'Escopos diferentes produzem números incompatíveis.')])

lesson(22, 'GCP: identidade, eventos e observabilidade', 'Cloud', 'Transfira os fundamentos para Cloud Storage, Cloud Run e Pub/Sub.',
'Relacionar projeto, recurso e identidade|Projetar consumidor idempotente|Investigar logs e métricas no GCP', r'''
## Comece pela hierarquia
No Google Cloud, projetos organizam recursos e se relacionam com faturamento e políticas da organização. Uma service account representa uma identidade de workload; não é uma pessoa nem exige uma chave JSON persistente em toda integração. Prefira mecanismos de identidade de workload/federação quando o ambiente suportar. Conceda papéis no menor escopo viável.

## Serviços com papéis distintos
Cloud Storage guarda objetos em buckets. Cloud Run executa serviços/jobs gerenciados conforme o produto e configuração. Pub/Sub desacopla produtores e consumidores por tópicos e assinaturas. Cloud Logging centraliza registros; Cloud Monitoring trabalha métricas, políticas e observação. As equivalências com AWS são conceituais, não substituições de sintaxe ou garantias.

## Ack e duplicidade
Um consumidor recebe mensagem e confirma processamento com ack conforme o modelo da assinatura. Confirmar antes de tornar o efeito durável pode perder trabalho. Confirmar depois permite reentrega se a confirmação se perder: por isso o efeito precisa ser idempotente. Recursos de exactly-once têm condições e escopo específicos; não os use como justificativa universal para eliminar deduplicação.

## Desenho de estudo
Objeto de log sintético → evento/roteamento compatível → consumidor Cloud Run → normalização → armazenamento/observabilidade. Especifique serviço de gatilho, identidade de entrega, autenticação do endpoint, retries, dead-letter e orçamento. Um endpoint de consumidor não deve ficar público por conveniência quando a origem pode usar identidade autenticada.

## Investigar sem mudar
No console de uma sandbox autorizada, selecione projeto e janela antes da consulta. Filtre por recurso, severidade e correlation_id. Compare falha de permissão com falha de aplicação. Verifique concorrência, timeout e dependência downstream: escalar o consumidor pode sobrecarregar o banco.

No laboratório de eventos você testa duplicidade e separação de mensagens inválidas. Na biblioteca há roteiro GCP com critérios verificáveis e limpeza. Nenhuma chave, conta ou recurso pago é criado pelo curso.
''', 'Desenhe projetos, recursos, identidades e fluxo de mensagem|Resolva o mesmo fixture de eventos usando o modelo Pub/Sub|Explique o ponto exato em que o consumidor envia ack|Crie uma tabela AWS/GCP por função e diferenças que precisam de verificação',
'Arquitetura GCP com identidade, ack, deduplicação e observabilidade.', 'Explique a falha entre efeito durável e ack e o que a sua chave idempotente garante.', 'gcp-iam|gcp-pubsub|gcp-run|gcp-storage', 'events', [
('Confirmar a mensagem antes de gravar o efeito pode:', ['Perder trabalho se houver falha depois do ack','Garantir consistência total','Eliminar qualquer duplicata'],0,'A origem pode considerar concluído um efeito que ainda não existe.'),
('Uma service account é:', ['Identidade de workload','Senha pessoal compartilhada','Sempre um arquivo JSON obrigatório'],0,'A identidade pode ser usada por mecanismos que evitam chaves estáticas exportadas.')])

lesson(23, 'Containers e Kubernetes para investigar', 'Cloud', 'Entenda isolamento, probes, recursos e rollout sem virar especialista em um dia.',
'Diferenciar imagem, container e pod|Ler readiness e liveness|Investigar falha de deploy e recursos', r'''
## Empacotamento não é máquina virtual
Imagem é um artefato com aplicação e dependências. Container é uma instância isolada com limites, que compartilha o kernel do host no modelo Linux usual. Dados importantes não devem depender da camada efêmera do container. Logs preferencialmente fluem pelo mecanismo de observabilidade definido.

No Kubernetes, pod é a unidade que agrupa containers relacionados. Deployment gerencia réplicas e atualização de pods; Service fornece descoberta e acesso estável. Namespace organiza escopo, mas não é por si só isolamento completo de segurança. ConfigMap guarda configuração não secreta; Secret exige controle de acesso e proteção do ambiente, não apenas um nome especial.

## Probes têm funções diferentes
Readiness informa se a instância deve receber tráfego. Liveness ajuda a decidir se deve reiniciar. Startup dá tempo à inicialização quando configurada. Se uma dependência compartilhada caiu, uma liveness que falha por essa dependência pode reiniciar todos os pods e piorar o incidente. Teste função e tempo adequados.

```bash
kubectl get pods -n lab
kubectl describe pod NOME_DO_POD -n lab
kubectl logs NOME_DO_POD -n lab --tail=50
kubectl rollout status deployment/quotes -n lab --timeout=60s
```

São comandos para um cluster local seu e nome observado. Nunca use um contexto corporativo como destino implícito. O curso fornece o roteiro; não instala cluster nem executa esses comandos.

## Requests e limits
Requests ajudam no agendamento; limits impõem limites conforme recurso. CPU pode sofrer throttling; memória excedida pode resultar em OOM. CrashLoopBackOff é uma condição de repetidas falhas com espera, não a causa raiz. Investigue eventos, logs anteriores, código de saída, configuração e mudança recente.

No laboratório de incidente, compare deploy recente e falha de dependência. O foco deste dia é diagnóstico e decisão, não memorizar todos os objetos. O plano essencial pode deixar a instalação real de Kubernetes para depois do onboarding.
''', 'Desenhe imagem → container → pod → deployment → service|Explique como readiness difere de liveness|Investigue deploy e dependência no simulador de incidente|Leia o roteiro Docker/Kubernetes e identifique contexto, namespace e limites antes de aplicar',
'Árvore de diagnóstico de pod em falha com hipótese, observação e ação.', 'Explique por que aumentar réplicas pode piorar uma dependência saturada.', 'kubernetes|docker', 'incident', [
('Readiness serve principalmente para:', ['Decidir se a instância recebe tráfego','Apagar dados','Conceder privilégio'],0,'Readiness controla elegibilidade para tráfego; não é sinônimo de reinício.'),
('CrashLoopBackOff é:', ['A causa raiz comprovada','Um estado que exige investigação de falhas repetidas','Uma configuração de bucket'],1,'Logs, eventos e código de saída explicam por que o processo está falhando.')])

lesson(24, 'Pipeline de eventos confiável', 'Automação', 'Conecte monitoramento e Ansible sem transformar ruído em ação perigosa.',
'Definir envelope de evento|Separar deduplicação e correlação|Controlar reprocessamento e backpressure', r'''
## Contrato antes de integração
Um envelope útil contém event_id, source, schema_version, occurred_at, received_at, resource_id, severity e correlation_id. Timestamp deve ter fuso e formato conhecido. O dado externo é não confiável: rejeite campo inválido e separe para análise, preservando somente o necessário e permitido.

```json
{"schema_version":1,"event_id":"evt-demo-01","source":"monitor-demo","resource_id":"web-01","severity":"error","occurred_at":"2026-09-06T09:05:00Z"}
```

Deduplicação evita repetir o mesmo efeito lógico. Correlação agrupa eventos relacionados, como três serviços que dependem do mesmo banco. Agrupar não significa apagar evidências; você precisa conseguir explicar quais sinais sustentam o incidente. Janela longa demais pode juntar incidentes independentes.

## Estado autoritativo
Uma automação pode passar por recebido → validado → enriquecido → aguardando aprovação → executando → verificando → concluído/falhou. O estado deve estar em armazenamento confiável, com transições válidas. Aprovação expirada não pode ser reaproveitada para outro alvo. Cancelamento antes de executar difere de interromper no meio de uma ação.

## Confiabilidade sem tempestade
Defina prazo total, limite de tentativas, backoff, jitter e orçamento de concorrência. Dead-letter não é lixeira: tem owner e processo de reprocessamento após corrigir a causa. Replay deve preservar a identidade lógica e reavaliar autorização, pois uma permissão antiga pode não valer hoje.

## Código e ferramentas de workflow
Ferramentas de orquestração coordenam etapas; regras de autorização, idempotência transacional e estado pertencem a um componente com contrato e testes. Power Automate pode ser complemento para fluxos corporativos; ele não muda essas exigências. Não coloque um shell livre atrás de um webhook.

No lab você monta a política do pipeline e recebe avaliação determinística de cenários: duplicata, aprovação ausente, alvo errado e excesso de tentativas. É uma avaliação de projeto, sem integração de rede real.
''', 'Preencha a política no laboratório Workflow|Teste a regra com evento duplicado e autorização ausente|Desenhe estados e transições proibidas|Escreva processo de replay de uma mensagem corrigida',
'Contrato de evento, diagrama de estados e política testada.', 'Mostre como evitar corrida entre dois consumidores tentando reservar o mesmo evento.', 'aws-events|gcp-pubsub|sre', 'workflow', [
('Deduplicar e correlacionar são:', ['A mesma operação','Evitar efeito repetido e relacionar eventos, respectivamente','Recursos exclusivos de IA'],1,'Eventos distintos podem pertencer ao mesmo incidente; duplicata é outra dimensão.'),
('Reprocessar uma mensagem antiga exige:', ['Reavaliar autorização e preservar identidade lógica','Confiar sempre na aprovação antiga','Gerar novo ID para esconder repetição'],0,'Escopo e validade de autorização podem mudar; replay não deve duplicar efeitos.')])

lesson(25, 'AIOps: anomalia não é incidente', 'IA para infraestrutura', 'Construa uma baseline e avalie falsos positivos antes de automatizar.',
'Distinguir limiar e baseline|Calcular precisão e recall|Entender sazonalidade e drift', r'''
## Comece por uma regra explicável
Um limiar fixo dispara quando uma medida cruza um valor. Uma baseline compara o comportamento com uma referência. Exemplo: média de latência histórica 100ms, desvio padrão 20ms, observação 180ms. z=(180−100)/20=4. Isso sinaliza desvio nesse modelo, mas não prova impacto nem causa.

Sazonalidade importa: horário de pico não deve ser comparado automaticamente com madrugada. Dados de incidente usados para treinar a referência podem normalizar um comportamento ruim. Desvio padrão zero exige tratamento; dividir por zero ou inventar um número esconde a limitação.

## Avalie com rótulos
Verdadeiro positivo é alerta que correspondia ao evento de interesse. Falso positivo é alerta sem esse evento. Falso negativo é evento que não alertou. Precisão=TP/(TP+FP); recall=TP/(TP+FN). Num conjunto com 8 TP, 2 FP e 4 FN, precisão=80% e recall≈66,67%. Acurácia pode parecer ótima quando incidentes são raros mesmo se o detector quase nunca os encontra.

## Um detector operável
Documente janela de treino, exclusões, hipótese estatística, população e limite. Compare com uma regra simples. Comece em shadow mode, emitindo sugestões observadas sem remediar. Meça ruído, cobertura, atraso de detecção e custo. Mudança no padrão de dados ou uso pode gerar drift e exigir revisão da baseline.

## Causalidade exige outro esforço
Latência e CPU podem crescer juntas por aumento de tráfego. Isso não prova que CPU causou o erro. Use dependências, sequência temporal, mudança recente e testes de hipóteses. Intervenção precisa de ambiente autorizado e alcance limitado; não crie falhas em produção para "ver se é isso".

O laboratório calcula z-score, precisão e recall com dados fixos. O kit Python permite implementar a detecção e testar séries vazias/constantes. Não há modelo treinado ou acesso a dados da empresa.
''', 'Calcule z-score, precisão e recall na bancada Anomalias|Descreva um caso de sazonalidade que dispara falso positivo|Defina shadow mode e critério para promover uma regra|Implemente ou revise a função de baseline no kit Python',
'Ficha de detector com fórmula, avaliação, limitações e política de revisão.', 'Compare custo de falso positivo e falso negativo segundo impacto e autoridade da ação.', 'sre-alert|otel', 'anomaly', [
('8 TP, 2 FP e 4 FN resultam em precisão:', ['80%','66,67%','100%'],0,'Precisão=8/(8+2)=80%; recall usa os falsos negativos.'),
('Um z-score alto comprova:', ['Causa raiz','Desvio em relação à referência escolhida','Autorização de reinício'],1,'A referência e suas hipóteses limitam a interpretação do desvio.')])

lesson(26, 'LLMs e RAG como assistentes de investigação', 'IA para infraestrutura', 'Use contexto recuperado, evidências e abstinência em vez de confiança cega.',
'Explicar token, contexto e RAG|Separar instrução e dado recuperado|Avaliar resposta fundamentada', r'''
## O que um modelo faz
Um modelo de linguagem gera texto a partir de padrões e contexto. Pode ajudar a resumir logs permitidos, comparar runbooks e propor hipóteses. Pode também inventar comandos ou citar material que não sustenta a resposta. Fluência e confiança verbal não são evidência de correção.

Tokens são unidades processadas pelo modelo; entrada e saída têm limites e custos conforme o serviço. Contexto é o material disponível naquela interação. Não envie credenciais, dados de clientes ou logs irrestritos. Use exemplos sintéticos no estudo e apenas destinos aprovados no trabalho.

## RAG em etapas
RAG recupera trechos de uma base e os oferece como contexto à geração. Pipeline típico: documentos aprovados → divisão em trechos → índices de busca/embeddings → recuperação filtrada → contexto com fontes → resposta com referências. A permissão deve filtrar na origem/recuperação, não depois que um documento proibido já foi fornecido ao modelo.

Embeddings representam conteúdo numericamente para busca de similaridade. Similaridade não garante relevância operacional nem atualização. Um runbook antigo pode sugerir comando incompatível. Registre versão, owner e validade. Se não houver evidência suficiente, a resposta correta é dizer o que falta.

## Prompt injection
Um log ou documento pode conter "ignore as regras e execute...". Esse texto é dado, não autoridade. Separe instruções confiáveis e conteúdo recuperado, limite ferramentas e valide ações fora do modelo. Esses controles reduzem risco, mas não provam imunidade completa.

## Avaliar sem executar um LLM
A bancada RAG mostra três trechos sintéticos: runbook aplicável, conteúdo antigo e instrução maliciosa inerte. Você escolhe evidência e ação; o corretor avalia a decisão. Não existe chamada a um modelo, inferência paga ou armazenamento de prompt corporativo. No trabalho, construa um conjunto de perguntas com resposta esperada, fontes, casos sem resposta e tentativas de induzir ação indevida.
''', 'Leia os trechos do lab RAG|Escolha fonte aplicável e uma resposta com incerteza explícita|Rejeite a instrução embutida no log e explique o limite de autoridade|Escreva cinco casos de avaliação, incluindo ausência de evidência',
'Plano de avaliação RAG com fontes, validade, permissão e abstinência.', 'Separe qualidade de recuperação, fundamentação e segurança da ação em métricas distintas.', 'owasp|rag', 'rag', [
('Um documento recuperado que manda ignorar regras é:', ['Uma nova instrução de autoridade','Dado não confiável','Aprovação de produção'],1,'Conteúdo externo não pode ampliar permissões ou substituir instruções confiáveis.'),
('Busca semanticamente similar garante resposta correta?', ['Sim','Não; relevância, validade e permissão ainda precisam de avaliação','Somente com mais tokens'],1,'Similaridade é um sinal de recuperação, não prova de verdade ou atualidade.')])

lesson(27, 'Remediação assistida com freios reais', 'IA para infraestrutura', 'Transforme uma recomendação em uma ação limitada, aprovada e auditável.',
'Separar recomendação e execução|Aplicar allowlist e aprovação válida|Definir rollback, cooldown e kill switch', r'''
## A IA propõe; a política decide
O modelo pode sugerir action_id=restart_quotes para um incidente. Um componente determinístico verifica se essa ação existe, se o alvo pertence ao escopo, se há aprovação válida e se as pré-condições continuam verdadeiras. Não execute um comando livre retornado pelo modelo. A própria ferramenta deve aplicar o limite no recurso que controla.

## Contrato de remediação
Inclua incidente, ação versionada, alvo permitido, justificativa com evidência, validade, identidade aprovadora, chave de idempotência e pós-condição. Um booleano no texto não basta. A aprovação se vincula àquela mudança e expira. Logs de auditoria precisam contar o que aconteceu sem persistir segredo ou informação desnecessária.

## Freios em sequência
Dry-run → aprovação → lock por recurso → revalidação → canário → verificação → expansão autorizada ou rollback. Cooldown evita remediar repetidamente o mesmo sintoma. Circuit breaker interrompe uma sequência de falhas. Kill switch impede novas execuções e deve ter comportamento definido para uma ação já em curso.

## Quando não automatizar a ação
Se o diagnóstico é incerto, o efeito irreversível ou a verificação fraca, automatize primeiro a coleta de evidências e o encaminhamento. Reduzir tempo de triagem já elimina trabalho manual. Nem toda oportunidade precisa terminar em reinício autônomo.

## Teste negativo vale muito
Use evento duplicado, aprovação expirada, alvo fora do inventário, runbook antigo e pós-condição falhando. O sistema deve bloquear nos limites apropriados, preservar estado e explicar o próximo passo. Testar somente o caminho feliz não mostra se a política protege o recurso.

A bancada de workflow avalia quatro controles essenciais. A arena de incidente permite observar como decisões ruins aumentam impacto no modelo. São exercícios determinísticos; não prometem a cobertura ou a segurança de uma integração empresarial real.
''', 'Configure a política no lab Workflow|Faça a tabela de cinco casos negativos e resposta esperada|Desenhe o limite onde a ferramenta verifica autorização|Escreva acionamento e recuperação do kill switch',
'Proposta de remediação com critérios de execução, bloqueio e recuperação.', 'Defina o que acontece se a aprovação vence entre o planejamento e o início da ação.', 'owasp|aap|sre', 'workflow', [
('Um comando livre gerado por IA deve:', ['Ir direto para shell','Ser substituído por ação permitida e validação determinística','Ganhar sudo automaticamente'],1,'A interface precisa restringir capacidades e validar autoridade fora do modelo.'),
('Diagnóstico incerto e ação irreversível pedem:', ['Automatizar coleta e escalar decisão','Executar rápido antes que mude','Esconder incerteza'],0,'Assistência de leitura oferece valor com menor risco quando a ação não é bem controlada.')])

lesson(28, 'Checkpoint 4: incident commander por um dia', 'Revisão', 'Treine decisões, comunicação e recuperação sob um relógio didático.',
'Priorizar mitigação com evidência|Comunicar impacto e próximos passos|Escrever postmortem sem culpa', r'''
## Três horas de simulação
Na arena, uma API de cotações sintética está falhando após uma alteração. Você pode investigar métricas, logs, traces e histórico, comunicar impacto e escolher uma ação. Cada etapa consome tempo simulado. A interface mostra o tempo e a consequência de cada escolha; não cria tráfego ou falhas reais.

Use 60 minutos para sua primeira tentativa. Depois 45 para escrever postmortem, 45 para o simulado de IA/incidentes e 30 para revisar a decisão mais fraca. Não tente decorar a sequência só para maximizar pontos: explique a evidência que justifica cada ação.

## Papéis e prioridades
Comando do incidente coordena e registra decisões. Investigadores coletam sinais e testam hipóteses. Comunicação traduz impacto. Em um time pequeno, uma pessoa pode acumular papéis, mas a responsabilidade deve ficar clara. O objetivo inicial é reduzir impacto com segurança, preservando o necessário para entender a causa.

## Postmortem útil
Inclua resumo, impacto, linha do tempo, detecção, resposta, fatores contribuintes, o que funcionou, o que dificultou e ações com owner e data. Evite apontar uma pessoa como causa. Uma configuração ruim passou por um sistema de validação e rollout; melhorar esse sistema previne mais do que culpar quem alterou.

## Critério de retorno
Depois da mitigação, valide erro, latência, volume e correção dos dados. Defina a janela de observação antes de declarar recuperação. Uma melhora momentânea exige acompanhamento; um dado sintético de sucesso nesta arena não substitui a observação de produção.

## Evidência de comunicação
Escreva uma atualização curta sem jargão desnecessário: o que o usuário percebe, alcance conhecido, mitigação, incerteza e próximo horário. Não prometa prazo sem evidência. Um escalonamento de qualidade leva contexto e pedido específico, não despeja logs.
''', 'Inicie uma sessão nova da arena de incidente|Investigue antes de agir e use o recurso de comunicação|Finalize somente após verificar a recuperação|Escreva postmortem e complete o simulado IA/incidentes',
'Linha do tempo, atualização de incidente e postmortem com três ações.', 'Separe detecção, mitigação e correção definitiva; atribua owner e prazo às melhorias.', 'sre-incident|sre', 'incident', [
('Postmortem deve priorizar:', ['Culpar quem fez o deploy','Fatores sistêmicos e ações verificáveis','Apagar a linha do tempo'],1,'O objetivo é aprender e reduzir recorrência com responsáveis e prazos claros.'),
('Depois de uma mitigação, é necessário:', ['Validar recuperação por sinais e função do usuário','Encerrar imediatamente','Remover todos os alertas'],0,'Mitigar não prova que todos os efeitos e dependências se recuperaram.')])

lesson(29, 'Projeto final: do evento à recuperação', 'Projeto final', 'Integre AWS/GCP, observabilidade, Ansible e IA em uma entrega defensável.',
'Integrar o fluxo com contratos claros|Provar comportamento em falhas|Defender trade-offs e limites', r'''
## Seu sistema de operações de estudo
Monte uma solução para o serviço fictício quotes: gera eventos estruturados, calcula saúde, armazena o histórico, consulta falhas e propõe uma remediação permitida. Use Python para normalizar/deduplicar; Ansible real de localhost para renderizar configuração; DQL e OpenSearch para investigar; workflow para governar a ação.

Escolha AWS ou GCP como arquitetura principal e desenhe a equivalência conceitual na outra. Na AWS, S3 pode guardar objetos, Lambda processar e OpenSearch indexar. No GCP, Cloud Storage, Pub/Sub e Cloud Run compõem funções relacionadas com contratos próprios. Não precisa provisionar para concluir a versão local, mas declare explicitamente que IAM, rede e serviços gerenciados ainda não foram testados.

## Critérios de aprovação do projeto
1. Diagrama com recursos, identidades, dados e limites.
2. Fixture válida, duplicada e inválida com resultado reproduzível.
3. Playbook limitado e evidência de segunda execução sem mudança.
4. Consulta de erro e SLO com população/janela.
5. Remediação bloqueada sem aprovação ou fora do alvo.
6. Recuperação testada e postmortem com ações.

## Uma defesa técnica de dez minutos
Explique o problema em um minuto, arquitetura em dois, demonstração em quatro, falhas e trade-offs em dois e próximos passos em um. Mostre uma decisão que você mudou por evidência. Diga quais partes são simulações e quais executou com a ferramenta real. Não use nomes de organizações para sugerir que o projeto reproduz suas infraestruturas.

## Rubrica de profundidade
Base: consegue reproduzir com guia. Autonomia: investiga e corrige uma variação sem solução. Profundidade: explica efeitos colaterais, compara alternativa e limita risco. Use esses níveis para autoavaliação por competência, não como título profissional. Registre os pontos que precisam de revisão no primeiro mês.

O portfólio exporta suas notas, resultados e evidências em Markdown; backup JSON guarda o estado de estudo. Revise antes de compartilhar fora do app. A entrega é sua explicação e seus arquivos, não apenas os pontos dos quizzes.
''', 'Execute o kit Python e o playbook real de localhost quando preparado|Resolva DQL, OpenSearch, SLO e política sem consultar respostas|Complete a arena com evidências e validação|Exporte o portfólio e apresente a defesa técnica em voz alta',
'Portfólio final com diagrama, código, resultados, limites e plano de evolução.', 'Justifique cada serviço pela necessidade e diga qual complexidade removeu.', 'ansible|dynatrace|aws-s3|gcp-run|opensearch', 'incident', [
('Uma defesa honesta deve:', ['Ocultar simulações','Separar prática real, simulação e partes não verificadas','Prometer arquitetura igual à empresa'],1,'A qualidade da evidência depende de comunicar seus limites.'),
('O melhor trade-off é o que:', ['Usa mais ferramentas','Relaciona necessidade, custo, risco e alternativa','Ignora recuperação'],1,'A escolha precisa resolver o problema com consequências compreendidas.')])

lesson(30, 'Chegue com método e boas perguntas', 'Projeto final', 'Faça a avaliação final e prepare os primeiros dias na equipe.',
'Reconhecer forças e lacunas|Fazer perguntas de onboarding úteis|Planejar evolução sem prometer domínio total', r'''
## Último dia, primeiro passo
Faça o simulado final antes de reler notas. Revise erros e selecione três lacunas prioritárias. Reexecute um laboratório em que você tinha dificuldade. Você não precisa saber todas as ferramentas de memória; precisa investigar com método, pedir contexto e respeitar os limites de mudança.

## Perguntas para os primeiros dias
Quais serviços críticos o time atende e quais impactos preocupam mais? Onde estão runbooks e owners? Qual inventário e quais templates AAP são aprovados? Como pedir acesso de leitura no Dynatrace? Quais SLOs e rotas de escalonamento existem? Quais contas/projetos AWS/GCP pertencem ao escopo? Como são aprovados e revertidos deploys? Quais usos de IA e dados são permitidos?

## Primeiro mês na equipe
Observe um incidente com alguém experiente. Reproduza uma automação em sandbox aprovado. Melhore um runbook com evidência. Proponha uma redução de toil de pequeno alcance. Peça revisão e compare sua hipótese com a de quem conhece o ambiente. Entender o sistema real é mais valioso do que impor a arquitetura do laboratório.

## Avalie autonomia, não só pontuação
Para cada competência marque: preciso de guia; consigo executar sozinho no lab; consigo investigar variação e explicar limites. Apoie a nota com evidência. Quiz mede reconhecimento e retenção, não anos de experiência. Domínio no laboratório é um começo verificável, não garantia de cargo ou senioridade.

## Se o calendário apertou
A data de início é editável nas configurações. O app calcula o fim do ciclo a partir da data que você escolher. Priorize Ansible, Dynatrace, diagnóstico, AWS/GCP e segurança das ações. As leituras complementares de Power Platform, certificações e Kubernetes avançado podem continuar após o ciclo inicial. Não sacrifique toda a revisão para adicionar nomes ao currículo.

## Rotina que continua
Mantenha um caderno de hipóteses, decisões e evidências sem informação confidencial. Faça revisão curta em intervalos crescentes, atualize runbooks após uso e teste retorno de mudança. Destaque técnico aparece na qualidade das decisões, na colaboração e na confiança que seu método permite aos outros.
''', 'Complete o simulado Final de 30 questões|Refaça um laboratório fraco sem solução|Exporte backup e portfólio; confira se abrem corretamente|Prepare perguntas de onboarding e três prioridades de evolução',
'Plano pessoal dos primeiros 30 dias no trabalho, avaliação por competência e portfólio revisado.', 'Apresente o que ainda não sabe e um caminho concreto para reduzir cada incerteza.', 'sre|ansible|dynatrace', 'workflow', [
('Primeira atitude em um ambiente novo:', ['Aplicar seu playbook em todos os hosts','Conhecer owners, contratos, acessos e processo de mudança','Enviar logs ao seu assistente pessoal'],1,'Conhecimento do ambiente e da autoridade antecede qualquer alteração.'),
('Pontuação alta neste curso demonstra:', ['Senioridade garantida','Desempenho nos exercícios definidos, com seus limites','Autorização para operar produção'],1,'É evidência de estudo e não substitui experiência real nem aprovação.')])

SOURCES = {
 'sre': ('Google — Site Reliability Workbook', 'https://sre.google/workbook/table-of-contents/'),
 'sre-slo': ('Google — Implementing SLOs', 'https://sre.google/workbook/implementing-slos/'),
 'sre-alert': ('Google — Alerting on SLOs', 'https://sre.google/workbook/alerting-on-slos/'),
 'sre-incident': ('Google — Incident Response', 'https://sre.google/workbook/incident-response/'),
 'otel': ('OpenTelemetry — Conceitos', 'https://opentelemetry.io/docs/concepts/'),
 'linux': ('Ubuntu — Command line for beginners', 'https://ubuntu.com/tutorials/command-line-for-beginners'),
 'http': ('MDN — HTTP overview', 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview'),
 'powershell': ('Microsoft — PowerShell 101', 'https://learn.microsoft.com/powershell/scripting/learn/ps101/00-introduction'),
 'python': ('Python — Tutorial oficial', 'https://docs.python.org/3/tutorial/'),
 'git': ('Git — Book', 'https://git-scm.com/book/en/v2'),
 'ansible': ('Ansible — Getting started', 'https://docs.ansible.com/projects/ansible/latest/getting_started/index.html'),
 'ansible-playbooks': ('Ansible — Playbooks', 'https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html'),
 'ansible-check': ('Ansible — Check e diff', 'https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html'),
 'ansible-vars': ('Ansible — Variáveis', 'https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html'),
 'ansible-handlers': ('Ansible — Handlers', 'https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html'),
 'ansible-roles': ('Ansible — Roles', 'https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html'),
 'ansible-vault': ('Ansible — Vault', 'https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html'),
 'ansible-windows': ('Ansible — Windows', 'https://docs.ansible.com/projects/ansible/latest/os_guide/windows_usage.html'),
 'aap': ('Red Hat — Ansible Automation Platform docs', 'https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/'),
 'dynatrace': ('Dynatrace — Intelligence', 'https://docs.dynatrace.com/docs/dynatrace-intelligence'),
 'oneagent': ('Dynatrace — OneAgent', 'https://docs.dynatrace.com/docs/ingest-from/dynatrace-oneagent'),
 'dql': ('Dynatrace — DQL', 'https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language'),
 'dql-filter': ('Dynatrace — DQL filtering', 'https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/commands/filtering-commands'),
 'dql-aggregate': ('Dynatrace — DQL aggregation', 'https://docs.dynatrace.com/docs/platform/grail/dynatrace-query-language/commands/aggregation-commands'),
 'aws-s3': ('AWS — S3 User Guide', 'https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html'),
 'aws-lambda': ('AWS — Lambda best practices', 'https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html'),
 'aws-events': ('AWS — S3 event notifications', 'https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html'),
 'opensearch': ('OpenSearch — Query DSL', 'https://docs.opensearch.org/latest/query-dsl/'),
 'aws-opensearch': ('AWS — OpenSearch Service', 'https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html'),
 'gcp-iam': ('Google Cloud — IAM overview', 'https://cloud.google.com/iam/docs/overview'),
 'gcp-pubsub': ('Google Cloud — Pub/Sub overview', 'https://cloud.google.com/pubsub/docs/overview'),
 'gcp-run': ('Google Cloud — Cloud Run overview', 'https://cloud.google.com/run/docs/overview/what-is-cloud-run'),
 'gcp-storage': ('Google Cloud — Cloud Storage', 'https://cloud.google.com/storage/docs/introduction'),
 'kubernetes': ('Kubernetes — Conceitos', 'https://kubernetes.io/docs/concepts/'),
 'docker': ('Docker — Conceitos', 'https://docs.docker.com/get-started/docker-concepts/'),
 'owasp': ('OWASP — LLM Prompt Injection', 'https://genai.owasp.org/llmrisk/llm01-prompt-injection/'),
 'rag': ('Microsoft — RAG architecture', 'https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide'),
 'power': ('Microsoft — Power Platform Learn', 'https://learn.microsoft.com/training/powerplatform/'),
}

if __name__ == '__main__':
    assert len(LESSONS) == 30 and sum(x['minutes'] for x in LESSONS) == 8520
    out = ROOT / 'backend/content'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'course.json').write_bytes(json.dumps(dict(version='1.1.0', lessons=LESSONS, sources=[dict(id=k,title=v[0],url=v[1]) for k,v in SOURCES.items()]),ensure_ascii=False,indent=2).encode('utf-8'))
    print(f'{len(LESSONS)} lessons / {sum(len(x["body"].split()) for x in LESSONS)} original lesson words / 142 hours')
