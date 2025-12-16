from mathesis import forms
from mathesis.semantics.truth_table.base import TruthTable, ConnectiveClause


class NegationClause(ConnectiveClause):
    column_names = ["P", "Negation(P)"]
    # TODO: Custom truth values
    table = {
        (1,): 0,
        (0,): 1,
        (2,): 2,
        (0.5,): 0.5,
    }


class ConjunctionClause(ConnectiveClause):
    column_names = ["P", "Q", "Conjunction(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 2): 2,
        (1, 0): 0,
        (1, 0.5): 0.5,
        (2, 1): 2,
        (2, 2): 2,
        (2, 0): 0,
        (2, 0.5): 0.5,
        (0, 1): 0,
        (0, 2): 0,
        (0, 0): 0,
        (0, 0.5): 0,
        (0.5, 1): 0.5,
        (0.5, 2): 0.5,
        (0.5, 0): 0,
        (0.5, 0.5): 0.5,
    }


class DisjunctionClause(ConnectiveClause):
    column_names = ["P", "Q", "Disjunction(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 2): 1,
        (1, 0): 1,
        (1, 0.5): 1,
        (2, 1): 1,
        (2, 2): 2,
        (2, 0): 2,
        (2, 0.5): 2,
        (0, 1): 1,
        (0, 2): 2,
        (0, 0): 0,
        (0, 0.5): 0.5,
        (0.5, 1): 1,
        (0.5, 2): 2,
        (0.5, 0): 0.5,
        (0.5, 0.5): 0.5,
    }


class ConditionalClause(ConnectiveClause):
    column_names = ["P", "Q", "Conditional(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 2): 2,
        (1, 0): 0,
        (1, 0.5): 0.5,
        (2, 1): 1,
        (2, 2): 2,
        (2, 0): 2,
        (2, 0.5): 2,
        (0, 1): 1,
        (0, 2): 1,
        (0, 0): 1,
        (0, 0.5): 1,
        (0.5, 1): 1,
        (0.5, 2): 2,
        (0.5, 0): 0.5,
        (0.5, 0.5): 0.5,
    }


class FDETruthTable(TruthTable):
    """The 4-valued logic FDE truth table class."""

    truth_values = {0, 1, 0.5, 2}
    designated_values = {1, 2}
    truth_value_symbols = {1: "1", 0: "0", 2: "b", 0.5: "i"}
    clauses = {
        forms.Negation: NegationClause(),
        forms.Conjunction: ConjunctionClause(),
        forms.Disjunction: DisjunctionClause(),
        forms.Conditional: ConditionalClause(),
    }
