"""Reference for synthetic promotion decisions; not production authorization."""


def decide(checks, approval, same_artifact):
    if not isinstance(checks, dict) or set(checks) != {'unit', 'integration', 'security'}:
        raise ValueError('Conjunto de verificações inválido.')
    if any(type(value) is not str or value not in ('passed', 'failed', 'missing') for value in checks.values()):
        raise ValueError('Resultado de verificação inválido.')
    if type(approval) is not str or approval not in ('approved', 'denied', 'pending'):
        raise ValueError('Aprovação inválida.')
    if type(same_artifact) is not bool:
        raise ValueError('Identidade de artefato deve ser booleana neste exercício.')
    if any(value != 'passed' for value in checks.values()) or not same_artifact or approval == 'denied':
        return 'block'
    return 'promote' if approval == 'approved' else 'hold'
