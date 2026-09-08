"""Complete one function at a time. Run python check.py TOPIC. No network required."""

def correlate(events):
    """Deduplicate (env,id), then count by (env,service,minute//5)."""
    raise NotImplementedError('Implemente correlação por ambiente, serviço e janela.')

def replicas(demand, capacity, utilization, spare):
    """ceil(demand / (capacity * utilization)) + spare. Validate documented bounds."""
    raise NotImplementedError('Implemente capacidade e reserva.')

def seasonal(values, current):
    """Mean of >=3 positive comparable observations; absolute deviation strictly >20%."""
    raise NotImplementedError('Implemente baseline, deviation_pct e flag.')

def model_triage(missing_before, missing_now, accuracy_before, accuracy_now, labelled):
    """Sample floor, then missing-data increase, then accuracy loss, then monitor."""
    raise NotImplementedError('Implemente a política de triagem do módulo MLOps.')

def agent_gate(cases):
    """Evaluate success, grounding, unauthorized actions, nearest-rank p95 and cost."""
    raise NotImplementedError('Implemente o gate de avaliação de agentes.')

def canary(control_errors, control_total, candidate_errors, candidate_total):
    """Require 1000/group, rollback if absolute error-rate increase >0.005."""
    raise NotImplementedError('Implemente hold, rollback ou promote sem executar ações.')
