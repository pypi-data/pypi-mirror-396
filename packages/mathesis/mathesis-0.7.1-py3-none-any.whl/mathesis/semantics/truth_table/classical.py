from mathesis import forms
from mathesis.semantics.truth_table.base import TruthTable, ConnectiveClause


class NegationClause(ConnectiveClause):
    column_names = ["P", "Negation(P)"]
    # TODO: Custom truth values
    table = {
        (1,): 0,
        (0,): 1,
    }


class ConjunctionClause(ConnectiveClause):
    column_names = ["P", "Q", "Conjunction(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 0): 0,
        (0, 1): 0,
        (0, 0): 0,
    }


class DisjunctionClause(ConnectiveClause):
    column_names = ["P", "Q", "Disjunction(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 0): 1,
        (0, 1): 1,
        (0, 0): 0,
    }


class ConditionalClause(ConnectiveClause):
    column_names = ["P", "Q", "Conditional(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 0): 0,
        (0, 1): 1,
        (0, 0): 1,
    }


class ClassicalTruthTable(TruthTable):
    """The classical truth table class."""

    truth_values = {1, 0}
    designated_values = {1}
    truth_value_symbols = {1: "1", 0: "0"}
    clauses = {
        forms.Negation: NegationClause(),
        forms.Conjunction: ConjunctionClause(),
        forms.Disjunction: DisjunctionClause(),
        forms.Conditional: ConditionalClause(),
    }
