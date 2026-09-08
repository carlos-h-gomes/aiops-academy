# Segurança e privacidade

O app é individual e local. Bind em loopback, validação de origem e parsers limitados não isolam outros processos com acesso à mesma conta do sistema. Não publique o servidor na internet como se fosse uma aplicação com autenticação.

Use apenas dados sintéticos em aulas, notas e exemplos. O app não precisa de chaves de nuvem nem envia notas a um modelo. Links para fontes externas são acessados pelo navegador. Recursos cloud dos roteiros são opcionais e pertencem ao ambiente de treinamento do aluno.

Ao identificar uma falha, preserve apenas uma reprodução mínima sintética. Não abra issues públicas com segredos, dados pessoais ou detalhes de exploração que afetem usuários. Na página **Security** do repositório, use **Report a vulnerability** quando o canal privado estiver disponível; se ele não aparecer, contate o proprietário do repositório por um canal privado antes de divulgar detalhes. Ainda não há endereço de suporte nem prazo de resposta publicado.

Dependências são travadas pelos arquivos de lock e devem ser revisadas antes de atualizar. A CI usa permissões de leitura e actions fixadas por SHA. Confira o estado hospedado em [Actions](https://github.com/carlos-h-gomes/aiops-academy/actions); um workflow verde e relatórios locais não garantem ausência de vulnerabilidades.
