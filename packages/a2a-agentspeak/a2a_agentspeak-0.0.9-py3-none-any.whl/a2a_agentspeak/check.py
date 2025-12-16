import agentspeak
from a2a_acl.protocol.acl_message import Illocution


def check_achievement(functor: str, ast: agentspeak.parser.AstAgent) -> bool:
    """The literal occurs as trigger in a plan."""
    # exists
    for p in ast.plans:
        if (
            p.event.goal_type == agentspeak.GoalType.achievement
            and p.event.head.functor == functor
        ):
            return True
    return False


def check_input_belief(functor: str, ast: agentspeak.parser.AstAgent) -> bool:
    """The literal occurs as trigger in a plan."""
    # exists
    for p in ast.plans:
        if (
            p.event.goal_type == agentspeak.GoalType.belief
            and p.event.head.functor == functor
        ):
            return True
    return False


def check_ask_belief(functor: str, ast: agentspeak.parser.AstAgent) -> bool:
    """The literal occurs in a belief or as a target belief in a plan."""
    # exists
    for b in ast.beliefs:
        if b.functor == functor:
            return True
    # not found in beliefs, check in input beliefs
    return check_input_belief(functor, ast)


tell_illoc = agentspeak.Literal(Illocution.TELL)
achieve_illoc = agentspeak.Literal(Illocution.ACHIEVE)
ask_illoc = agentspeak.Literal(Illocution.ASK)


def check_outgoing_illoc(illoc: agentspeak.Literal) -> bool:
    """Check that this literal represents a valid illocution."""
    return illoc in [tell_illoc, achieve_illoc, ask_illoc, agentspeak.Literal("propose")]
