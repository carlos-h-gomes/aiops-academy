"""Public learning catalog independent of learner persistence."""
from app.models.curriculum import load_curriculum


def catalog():
    return load_curriculum()
