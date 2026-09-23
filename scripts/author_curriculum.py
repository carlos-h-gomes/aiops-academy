"""Generate versioned references to existing lessons and explicitly planned units."""
import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.models.catalog import COURSE, LAB_MAP
from app.schemas.curriculum import Curriculum, validate_content_links

TRACKS = [
    ('infra', 'Infraestrutura e AIOps',
     'Da investigação do primeiro incidente à automação e operação de IA.',
     'Investigar e recuperar um serviço com hipóteses, testes e evidências.',
     ['start', 'ansible', 'dynatrace', 'event-correlation', 'fundamentals-github', 'fundamentals-actions', 'fundamentals-cicd']),
    ('data', 'Dados, SQL e RAG',
     'Entender dados, consultar com eficiência e sustentar respostas com fontes.',
     'Recuperar um banco e explicar se uma resposta está sustentada pelos dados.',
     ['python', 'search', 'tools-nifi', 'mlops-drift']),
    ('security', 'Segurança operacional',
     'Limitar permissões, proteger dados e praticar resposta e recuperação.',
     'Corrigir uma configuração vulnerável e demonstrar recuperação em ambiente isolado.',
     ['setup', 'templates', 'fundamentals-cicd', 'resilience-canary']),
    ('agents', 'Agentes e processos',
     'Escolher onde usar IA e manter regras, aprovação e estado sob controle.',
     'Automatizar etapas de um processo sintético com testes, rastreabilidade e revisão.',
     ['tools-map', 'llmops-agents', 'tools-n8n', 'tools-power-automate']),
]

# Editorial plan approved for V1. No body, duration or completion is claimed here.
PLANNED = {
    'data': [
        ('Modelagem relacional', 'Representar entidades, chaves e relações de um serviço fictício.', ['Identificar entidades e relações', 'Explicar chaves e integridade referencial']),
        ('SQL e joins', 'Investigar registros e combinar tabelas sem perder a interpretação do resultado.', ['Construir consultas com filtros e joins', 'Reconhecer duplicação e ausência de dados']),
        ('PostgreSQL: índices e EXPLAIN', 'Ler um plano de execução e justificar uma melhoria de consulta.', ['Interpretar o plano de uma consulta', 'Comparar leitura, escrita e custo de índices']),
        ('Transações, backup e restauração', 'Preservar consistência e demonstrar recuperação com dados sintéticos.', ['Explicar limites de uma transação', 'Verificar uma restauração sem sobrescrever a origem']),
        ('Embeddings e busca com pgvector', 'Comparar busca semântica e filtros usando exemplos controlados.', ['Explicar embeddings e similaridade', 'Avaliar recuperação com filtros e casos fixos']),
        ('RAG com evidência e acesso', 'Avaliar respostas com citações e respeitar a permissão do documento recuperado.', ['Conferir citações e ausência de evidência', 'Aplicar controle de acesso antes da recuperação']),
    ],
    'security': [
        ('Identidade e menor privilégio', 'Desenhar permissões limitadas por recurso e operação.', ['Distinguir autenticação de autorização', 'Testar acesso permitido e negado']),
        ('Segredos e proteção de dados', 'Separar credenciais, configurações e dados de estudo.', ['Reconhecer exposição de segredo', 'Definir retenção e recuperação sem copiar dados reais']),
        ('Redes e hardening', 'Reduzir a superfície de um serviço mantendo acesso de recuperação.', ['Explicar regras de entrada e saída', 'Verificar uma configuração de rede em lab isolado']),
        ('Containers e dependências', 'Inspecionar imagem, permissões e dependências antes de executar.', ['Interpretar achados sem confundir scanner com garantia', 'Priorizar correções e registrar versões']),
        ('Detectar, responder e recuperar', 'Praticar contenção e restauração em um incidente fictício.', ['Preservar evidências permitidas', 'Verificar recuperação e prevenir recorrência']),
        ('Segurança de agentes e contexto', 'Tratar instruções em documentos como dados sem conceder autoridade.', ['Testar instrução maliciosa e ferramenta negada', 'Impor limites e autorização fora do prompt']),
    ],
    'agents': [
        ('Processos, regras e agentes', 'Escolher fluxo determinístico ou agente a partir do problema e do risco.', ['Mapear entradas, decisões e responsáveis', 'Justificar onde IA agrega valor ao processo']),
        ('Modelos, assistentes e ferramentas', 'Distinguir modelo, aplicativo, runtime e integração.', ['Descrever o papel de cada camada', 'Comparar resultados com uma tarefa e critérios fixos']),
        ('Saídas estruturadas e ferramentas', 'Validar pedidos de ação antes de executar uma ferramenta permitida.', ['Validar entrada e saída com schema', 'Rejeitar ferramenta ou alvo fora do escopo']),
        ('Estado, avaliação e aprovação', 'Controlar repetição, retomada e aprovação sem depender da resposta do modelo.', ['Aplicar idempotência e limite de execução', 'Avaliar falhas e aprovação recusada']),
        ('Desenvolvimento: triagem de bugs', 'Investigar código sintético, propor correção e revisar testes e diff.', ['Vincular hipótese a evidência no código', 'Preparar alteração revisável sem publicação automática']),
        ('Atendimento: chamados e runbooks', 'Classificar solicitações e preparar resposta citando procedimentos.', ['Recuperar fontes permitidas', 'Recusar sem evidência e encaminhar para revisão']),
        ('Marketing: briefing e revisão', 'Transformar um briefing fictício em rascunho sujeito a revisão editorial.', ['Separar fatos fornecidos de afirmações sem suporte', 'Solicitar aprovação sem postar ou enviar']),
        ('Financeiro: conciliação sintética', 'Explicar divergências de arquivos fictícios com cálculos feitos em código.', ['Conciliar valores e identificar exceções', 'Preservar revisão humana sem pagamentos']),
    ],
}

PUBLISHED_INITIAL = {
    'data-01': {'content_version': '2026.09.20.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'data-01', 'title': 'Fixture relacional local', 'limitations': 'Use somente os arquivos sintéticos e o verificador local; não conecta PostgreSQL nem um banco externo.'}},
    'data-02': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'data-02', 'title': 'Joins e contagens locais', 'limitations': 'Avalia escolhas fechadas sobre fixtures SQLite; não executa SQL do aluno nem conecta um banco externo.'}},
    'data-03': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'data-03', 'title': 'Plano de execução sintético', 'limitations': 'Usa um plano desenhado para estudo; não mede PostgreSQL, runtime, buffers ou desempenho.'}},
    'data-04': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'data-04', 'title': 'Rollback e restauração local', 'limitations': 'Usa conexões SQLite em memória; não abre dumps, arquivos do aluno ou um banco PostgreSQL.'}},
    'data-05': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'data-05', 'title': 'Busca vetorial sintética', 'limitations': 'Usa vetores escritos à mão e filtros fechados; não chama modelo, pgvector, banco ou rede.'}},
    'data-06': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'data-06', 'title': 'Evidência e acesso local', 'limitations': 'Avalia casos de citação predefinidos; não interpreta texto livre, chama modelo ou altera permissões.'}},
    'security-01': {'content_version': '2026.09.20.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'security-01', 'title': 'Matriz local de autorização', 'limitations': 'Avalia somente identidades e recursos sintéticos; não cria contas, credenciais, políticas ou chamadas de rede.'}},
    'security-02': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'security-02', 'title': 'Redação de evidência local', 'limitations': 'Avalia escolhas fechadas sobre registros sintéticos; não lê, testa, registra ou transmite segredos.'}},
    'security-03': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'security-03', 'title': 'Hardening de topologia local', 'limitations': 'Avalia escolhas fechadas de manifests sintéticos; não inicia Docker, rede, serviço ou processo.'}},
    'security-04': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'security-04', 'title': 'Cadeia de suprimento sintética', 'limitations': 'Avalia decisões fechadas de artefatos fictícios; não baixa imagem, consulta registry, executa scanner ou runtime.'}},
    'security-05': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'security-05', 'title': 'Resposta a incidente em memória', 'limitations': 'Avalia decisões fechadas sobre snapshots sintéticos; não restaura arquivo, banco, volume ou serviço.'}},
    'security-06': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'security-06', 'title': 'Política estática de agentes', 'limitations': 'Avalia escolhas fechadas de policy; não chama modelo, ferramenta, rede, processo ou aprovação real.'}},
    'agents-01': {'content_version': '2026.09.20.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-01', 'title': 'Classificação determinística de processos', 'limitations': 'Não chama modelo, rede, ferramenta, subprocesso ou sistema externo; os cenários são fixtures fechadas.'}},
    'agents-02': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-02', 'title': 'Camadas e autoridade local', 'limitations': 'Avalia escolhas fechadas sobre camadas sintéticas; não chama modelo, rede, ferramenta, subprocesso ou sistema externo.'}},
    'agents-03': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-03', 'title': 'Contratos e ferramentas fechadas', 'limitations': 'Avalia escolhas fechadas de contratos sintéticos; não interpreta comandos, URLs, caminhos, SQL ou texto livre.'}},
    'agents-04': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-04', 'title': 'Estado e aprovação sintéticos', 'limitations': 'Avalia decisões fechadas em memória; não cria aprovação, persiste estado, chama modelo ou executa ferramenta externa.'}},
    'agents-05': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 90, 'complete': 150}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-05', 'title': 'Triagem de bug sintética', 'limitations': 'Avalia escolhas fechadas de revisão; não abre repositório, executa Docker, cria commit, envia alteração ou acessa rede.'}},
    'agents-06': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-06', 'title': 'Chamados e runbooks locais', 'limitations': 'Avalia escolhas fechadas de atendimento; não envia mensagens, altera contas, executa runbooks ou acessa rede.'}},
    'agents-07': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-07', 'title': 'Briefing e revisão local', 'limitations': 'Avalia escolhas fechadas de revisão editorial; não publica, envia conteúdo, chama modelo ou acessa plataforma externa.'}},
    'agents-08': {'content_version': '2026.09.21.1', 'duration_minutes': {'essential': 75, 'complete': 120}, 'practice': {'kind': 'guided_fixture', 'lab_id': 'agents-08', 'title': 'Conciliação sintética local', 'limitations': 'Avalia escolhas fechadas de registros fictícios; não importa arquivos, transfere valores, conecta banco ou acessa rede.'}},
}

def load_published_authored_unit(identity):
    path = ROOT / 'backend/content/planned-units' / f'{identity}.json'
    raw = path.read_bytes()
    if len(raw) > 100_000:
        raise ValueError('Published lesson source exceeds size limit.')
    value = json.loads(raw)
    if value.get('id') != identity or value.get('status') != 'available' or not isinstance(value.get('body'), str):
        raise ValueError('Published lesson source is inconsistent.')
    return value


def build_catalog(course, manuals, labs):
    sources = {source['id']: source for source in course['sources']}
    guides = {guide['id']: guide for guide in manuals}
    tracks = [dict(id=id, title=title, summary=summary, outcome=outcome,
                   guides=[dict(id=key, title=guides[key]['title']) for key in keys])
              for id, title, summary, outcome, keys in TRACKS]
    units = []
    for lesson in sorted(course['lessons'], key=lambda item: item['day']):
        day = lesson['day']
        lab = labs[lesson['lab']]
        units.append(dict(id=f'infra-{day:02d}', track_id='infra', order=day,
            title=lesson['title'], summary=lesson['summary'], status='available',
            content_version=course['version'], lesson_day=day, competencies=lesson['objectives'],
            prerequisites=[f'infra-{day-1:02d}'] if day > 1 else [],
            duration_minutes=dict(essential=180, complete=lesson['minutes']),
            practice=dict(kind='simulation', lab_id=lab['id'], title=lab['title'], limitations=lab['limitations']),
            sources=[dict(title=sources[key]['title'], url=sources[key]['url']) for key in lesson['sources']],
            translations=[dict(locale=locale, status='available' if locale=='pt-BR' else 'planned',
                               content_version=course['version'] if locale=='pt-BR' else None) for locale in ('pt-BR','en','es')],
            verified_tool_versions=[]))
    bases = {'data':'infra-05', 'security':'infra-03', 'agents':'infra-06'}
    for track_id, items in PLANNED.items():
        for order, (title, summary, competencies) in enumerate(items, 1):
            identity = f'{track_id}-{order:02d}'
            published = PUBLISHED_INITIAL.get(identity)
            if published:
                authored = load_published_authored_unit(identity)
                if authored['title'] != title or authored['summary'] != summary or authored['competencies'] != competencies:
                    raise ValueError('Published lesson metadata does not match the editorial plan.')
                units.append(dict(id=identity, track_id=track_id, order=order, title=title, summary=summary, competencies=competencies, status='available', content_version=published['content_version'], lesson_day=None, duration_minutes=published['duration_minutes'], practice=published['practice'], sources=[dict(title=item['title'], url=item['url']) for item in authored['sources']], prerequisites=[f'{track_id}-{order-1:02d}' if order > 1 else bases[track_id]], translations=[dict(locale='pt-BR', status='available', content_version=published['content_version']), *[dict(locale=locale, status='planned', content_version=None) for locale in ('en','es')]], verified_tool_versions=[]))
            else:
                units.append(dict(id=identity, track_id=track_id, order=order, title=title, summary=summary, competencies=competencies, status='planned', content_version=None, lesson_day=None, duration_minutes=None, practice=None, sources=[], prerequisites=[f'{track_id}-{order-1:02d}' if order > 1 else bases[track_id]], translations=[dict(locale=locale, status='planned', content_version=None) for locale in ('pt-BR','en','es')], verified_tool_versions=[]))
    value = Curriculum.model_validate(dict(schema_version='1.0', version='2026.09.07.1',
        metadata_reviewed_on='2026-09-07', tracks=tracks, units=units))
    return validate_content_links(value, course, manuals, labs)


def atomic_write(destination, content):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=destination.parent, suffix='.tmp', delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_catalog(course, manuals, labs, destination):
    value = build_catalog(course, manuals, labs)
    atomic_write(destination, json.dumps(value.model_dump(), ensure_ascii=False, indent=2)+'\n')
    return value


def main():
    manuals = json.loads((ROOT/'backend/content/manuals.json').read_text(encoding='utf-8'))
    value = write_catalog(COURSE, manuals, LAB_MAP, ROOT/'backend/content/curriculum.json')
    atomic_write(ROOT/'schemas/curriculum.schema.json', json.dumps(Curriculum.model_json_schema(), ensure_ascii=False, indent=2)+'\n')
    print(f'{len(value.tracks)} tracks; {sum(unit.status == "available" for unit in value.units)} available; {sum(unit.status == "planned" for unit in value.units)} planned. No progress writes.')


if __name__ == '__main__':
    main()
