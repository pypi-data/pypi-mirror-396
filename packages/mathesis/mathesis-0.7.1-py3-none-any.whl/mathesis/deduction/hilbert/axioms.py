from copy import deepcopy
from itertools import count

from anytree import Node

from mathesis.forms import Conditional, Conjunction, Disjunction, Formula, Negation
from mathesis.deduction.sequent_calculus.rules import Rule, SequentItem, _apply, sign


def _apply_axiom(target: Node, axiom: Formula, counter=count(1)):
    assert target.sign == sign.NEGATIVE, "Not on the right side of sequent"

    new_item = SequentItem(axiom, sign.POSITIVE, n=next(counter))
    branch_sequent = _apply(target, [target.clone(), new_item], counter)

    return {
        "queue_items": [branch_sequent],
        "counter": counter,
    }


class Axiom:
    formula: Formula


class SAxiom(Axiom):
    """Axiom schema of substitution"""

    def __init__(self, p: Formula, q: Formula, r: Formula):
        self.formula = Conditional(
            Conditional(p, Conditional(q, r)),
            Conditional(Conditional(p, q), Conditional(p, r)),
        )


class KAxiom(Axiom):
    """Axiom schema of constant"""

    def __init__(self, p: Formula, q: Formula):
        self.formula = Conditional(p, Conditional(q, p))


class IdentityAxiom(Axiom):
    """Axiom schema of identity"""

    def __init__(self, p: Formula):
        self.formula = Conditional(p, p)


class DisjunctionIntroductionAxiom:
    """Axiom schema of disjunction introduction"""

    def __init__(self, disj1: Formula, disj2: Formula, antecendent: Formula):
        """
        Args:
            disj1 (Formula): Left disjunct
            disj2 (Formula): Right disjunct
            antecendent (Formula): Antecendent identical to one of the disjuncts
        """
        if antecendent != disj1 and antecendent != disj2:
            raise ValueError("Antecendent must be one of the disjunctions")
        self.formula = Conditional(disj1, Disjunction(disj1, disj2))


class DisjunctionEliminationAxiom:
    """Axiom schema of disjunction elimination"""

    def __init__(self, disj1: Formula, disj2: Formula, consequent: Formula):
        self.formula = Conditional(
            Conditional(disj1, consequent),
            Conditional(
                Conditional(disj2, consequent),
                Conditional(Disjunction(disj1, disj2), consequent),
            ),
        )


class ConjunctionIntroductionAxiom:
    """Axiom schema of conjunction introduction"""

    def __init__(self, conj1: Formula, conj2: Formula):
        self.formula = Conditional(conj1, Conditional(conj2, Conjunction(conj1, conj2)))


class ConjunctionEliminationAxiom:
    """Axiom schema of conjunction elimination"""

    def __init__(self, conj1: Formula, conj2: Formula, consequent: Formula):
        if consequent != conj1 and consequent != conj2:
            raise ValueError("Antecendent must be one of the disjunctions")
        self.formula = Conditional(
            Conjunction(conj1, conj2),
            consequent,
        )


class DNEAxiom:
    """Axiom schema of double negation elimination"""

    def __init__(self, p: Formula):
        self.formula = Conditional(Negation(Negation(p)), p)
