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
            units.append(dict(id=f'{track_id}-{order:02d}', track_id=track_id, order=order,
                title=title, summary=summary, competencies=competencies, status='planned',
                content_version=None, lesson_day=None, duration_minutes=None, practice=None, sources=[],
                prerequisites=[f'{track_id}-{order-1:02d}' if order > 1 else bases[track_id]],
                translations=[dict(locale=locale, status='planned', content_version=None) for locale in ('pt-BR','en','es')],
                verified_tool_versions=[]))
    value = Curriculum.model_validate(dict(schema_version='1.0', version='2026.09.07.1',
        metadata_reviewed_on='2026-09-07', tracks=tracks, units=units))
    return validate_content_links(value, course, manuals, labs)


def atomic_write(destination, content):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, suffix='.tmp', delete=False) as file:
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
