from mathesis import forms
from mathesis.semantics.truth_table.base import TruthTable, ConnectiveClause


class NegationClause(ConnectiveClause):
    column_names = ["P", "Negation(P)"]
    # TODO: Custom truth values
    table = {
        (1,): 0,
        (2,): 2,
        (0,): 1,
    }


class ConjunctionClause(ConnectiveClause):
    column_names = ["P", "Q", "Conjunction(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 2): 2,
        (1, 0): 0,
        (2, 1): 2,
        (2, 2): 2,
        (2, 0): 0,
        (0, 1): 0,
        (0, 2): 0,
        (0, 0): 0,
    }


class DisjunctionClause(ConnectiveClause):
    column_names = ["P", "Q", "Disjunction(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 2): 1,
        (1, 0): 1,
        (2, 1): 1,
        (2, 2): 2,
        (2, 0): 2,
        (0, 1): 1,
        (0, 2): 2,
        (0, 0): 0,
    }


class ConditionalClause(ConnectiveClause):
    column_names = ["P", "Q", "Conditional(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 2): 2,
        (1, 0): 0,
        (2, 1): 1,
        (2, 2): 2,
        (2, 0): 2,
        (0, 1): 1,
        (0, 2): 1,
        (0, 0): 1,
    }


class LPTruthTable(TruthTable):
    """The 3-valued logic LP truth table class."""

    truth_values = {1, 0, 2}
    designated_values = {1, 2}
    truth_value_symbols = {1: "1", 0: "0", 2: "i"}
    clauses = {
        forms.Negation: NegationClause(),
        forms.Conjunction: ConjunctionClause(),
        forms.Disjunction: DisjunctionClause(),
        forms.Conditional: ConditionalClause(),
    }
