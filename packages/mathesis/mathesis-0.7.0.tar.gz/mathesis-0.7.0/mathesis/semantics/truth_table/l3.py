from mathesis import forms
from mathesis.semantics.truth_table.base import TruthTable, ConnectiveClause
from mathesis.semantics.truth_table.k3 import (
    NegationClause,
    DisjunctionClause,
    ConjunctionClause,
)


class ConditionalClause(ConnectiveClause):
    column_names = ["P", "Q", "Conditional(P, Q)"]
    table = {
        (1, 1): 1,
        (1, 0.5): 0.5,
        (1, 0): 0,
        (0.5, 1): 1,
        (0.5, 0.5): 1,
        (0.5, 0): 0.5,
        (0, 1): 1,
        (0, 0.5): 1,
        (0, 0): 1,
    }


class L3TruthTable(TruthTable):
    """The 3-valued logic Ł3 truth table class."""

    truth_values = {1, 0, 0.5}
    designated_values = {1}
    truth_value_symbols = {1: "1", 0: "0", 0.5: "i"}
    clauses = {
        forms.Negation: NegationClause(),
        forms.Conjunction: ConjunctionClause(),
        forms.Disjunction: DisjunctionClause(),
        forms.Conditional: ConditionalClause(),
    }
