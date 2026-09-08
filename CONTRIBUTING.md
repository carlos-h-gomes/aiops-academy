# Como contribuir

AIOps Academy evolui por incrementos pequenos: uma melhoria observável, evidência de funcionamento e documentação correspondente. Leia o [roadmap](ROADMAP.md) e a [arquitetura](docs/TECHNICAL-DOCUMENTATION.md) antes de propor mudanças.

## Preparar o projeto

No Windows, instale Python 3.12+ e Node LTS 22.12+ ou 24+. Execute `preparar.cmd`, depois `iniciar.cmd`. O ambiente validado é Python 3.14 e Node 24. A instalação é local; não há necessidade de credencial de nuvem. Linux e macOS ainda não têm inicializadores validados.

## Uma contribuição por vez

1. Descreva o problema, quem é afetado e como reproduzir.
2. Defina o que deve ser possível observar quando estiver resolvido.
3. Altere a menor parte coerente do sistema.
4. Verifique comportamento e compatibilidade; inclua regressão quando houver lógica alterada.
5. Atualize documentação e o changelog em Unreleased. Abra um PR quando existir um remoto publicado.

## Conteúdo didático

Edite `scripts/author_course.py` para o curso, `scripts/author_manuals.py` para manuais essenciais ou `backend/content/modules/*.json` para aprofundamentos/guias. Regenere com os scripts de autoria; `scripts/content_catalog.py` valida módulos antes de substituir o catálogo. Inclua objetivo, explicação original, exercício, resultado verificável, limitações e fonte oficial. Não copie manuais de terceiros para dentro do curso. Não ensine uma simulação como se fosse execução da ferramenta real. IDs de dias e laboratórios fazem parte do progresso: não renumere silenciosamente.

Após alterar curso/manuais, execute `.venv/Scripts/python.exe scripts/author_curriculum.py` pelo runner. Ele atualiza catálogo e schema das trilhas, rejeitando referências inconsistentes. Status planned não é conteúdo entregue; ativar novas aulas exige prática, avaliação e contrato de progresso próprios. Preserve IDs infra-01…30 e os vínculos dos dias antigos. Testes de calendário/projeção: em frontend, `python ../scripts/bounded.py 30 node --test tests/dates.test.mjs tests/curriculum.test.mjs`. Teste de trilhas: `python ../scripts/bounded.py 120 node tests/tracks.test.mjs`, depois do build, com Chrome instalado e banco temporário.

## Código e validação

Mantenha FastAPI e React separados por `/api/v1`. Entrypoints compõem; serviços possuem regras; repositórios fazem persistência. Não execute entrada do aluno como código do sistema. Não inclua dados reais em fixtures, screenshots ou exemplos.

Na raiz, execute:

```text
python scripts/bounded.py 90 .venv/Scripts/python.exe -m unittest discover -s backend/tests -v
python scripts/bounded.py 30 python labs/real/python/check.py --solution
python scripts/bounded.py 45 python labs/real/http_lab/bench.py
```

Em `frontend`, execute `npm run build`. Para mudanças de interface, revise teclado, foco, erros, recuperação, desktop e telas estreitas. `scripts/qa/audit.html` é uma bancada local, habilitada apenas pelo launcher com `--qa`; não é parte da interface do aluno. Auditoria automática não substitui revisão manual.

## Dados e distribuição

`data/`, `.venv/`, `artifacts/`, builds e memória privada em `docs/ai/` são ignorados pelo Git. Confira o diff antes de enviar arquivos. Backups pertencem ao aluno. Mudanças incompatíveis exigem migração e teste de restauração. Código e exemplos originais usam MIT; conteúdo didático original usa CC BY 4.0. Consulte LICENSE e CONTENT-LICENSE.md. Não contribua com material de terceiros sem direitos compatíveis.
