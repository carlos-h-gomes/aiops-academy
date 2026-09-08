# Entrega com evidências — laboratório offline

Requisito: Python 3.12 ou superior. Não instala dependências nem acessa rede. Leia o guia CI/CD da Biblioteca ou o MANUAL.md do kit.

1. Implemente `decide(checks, approval, same_artifact)` em exercise.py seguindo o contrato do guia.
2. Na pasta delivery, execute `python check.py`. O exercício incompleto falha intencionalmente.
3. Use `python check.py --solution` para conferir os seis casos de referência. Leia solution.py depois de tentar.
4. Registre casos que promovem, aguardam e bloqueiam, além das entradas inválidas.

Os estados são sintéticos. `same_artifact` não verifica assinatura real, e `approval` não autentica uma pessoa. Uma aplicação de produção precisa impor esses controles no serviço responsável. Nada aqui publica, implanta, reverte ou movimenta dinheiro.

`ci-example.yml` é um exemplo inativo. Para a prática remota opcional, a raiz de um repositório de estudo próprio deve conter a pasta delivery. Revise os pins e o conteúdo antes de copiar o exemplo para `.github/workflows`. O gatilho é manual, com permissão de leitura e timeout. O workflow verifica sua implementação, que precisa estar concluída; a solução de referência não deve ser usada para esconder um exercício incompleto.

A Academy não executou esse exemplo no GitHub. Não é necessário criar repositório ou usar cota de Actions para concluir a parte local. Encerramento: os processos terminam ao final dos testes; não há serviço ou recurso externo para remover.
