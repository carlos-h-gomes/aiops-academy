"""Validate authored manual modules before replacing the generated catalog."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

FIELDS = {'id', 'title', 'summary', 'category', 'minutes', 'recommended_after', 'body', 'sources'}


def validate_module(value, seen):
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError('O módulo deve conter exatamente os campos do contrato.')
    for field in ('id', 'title', 'summary', 'category', 'body'):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ValueError(f'Campo textual inválido: {field}')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,79}', value['id']) or value['id'] in seen:
        raise ValueError('ID inválido ou duplicado.')
    if value['category'] not in ('extension', 'tooling'):
        raise ValueError('Categoria de módulo desconhecida.')
    for field, maximum in (('minutes', 600), ('recommended_after', 30)):
        if type(value[field]) is not int or not 1 <= value[field] <= maximum:
            raise ValueError(f'Inteiro fora dos limites: {field}')
    sources = value['sources']
    if not isinstance(sources, list) or not 1 <= len(sources) <= 30:
        raise ValueError('Informe entre uma e 30 fontes.')
    for source in sources:
        if not isinstance(source, dict) or set(source) != {'title', 'url'}:
            raise ValueError('Fonte inválida.')
        if any(not isinstance(source[key], str) or not source[key].strip() for key in ('title', 'url')):
            raise ValueError('Título e URL da fonte são obrigatórios.')
        url = urlsplit(source['url'])
        if url.scheme != 'https' or not url.hostname or url.username or url.password or any(c.isspace() for c in source['url']):
            raise ValueError('A fonte deve usar HTTPS sem credenciais ou espaços.')
    return value


def assemble(core, directory: Path):
    result = list(core)
    seen = {manual['id'] for manual in core}
    if len(seen) != len(core):
        raise ValueError('ID duplicado nos manuais essenciais.')
    for path in sorted(directory.glob('*.json')):
        if path.stat().st_size > 200_000:
            raise ValueError(f'Módulo excede 200 KB: {path.name}')
        value = validate_module(json.loads(path.read_text(encoding='utf-8')), seen)
        result.append(value)
        seen.add(value['id'])
    return result


def write_catalog(core, directory: Path, destination: Path):
    # Assemble and serialize first: invalid input cannot replace valid output.
    content = json.dumps(assemble(core, directory), ensure_ascii=False, indent=2)
    destination.parent.mkdir(parents=True, exist_ok=True)
    from tempfile import NamedTemporaryFile
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, suffix='.tmp', delete=False) as file:
            temporary = Path(file.name)
            file.write(content)
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
