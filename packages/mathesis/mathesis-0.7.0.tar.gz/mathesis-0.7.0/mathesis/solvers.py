import logging
from collections import namedtuple
from typing import List

from mathesis import forms
from mathesis.deduction.tableau import Tableau, rules

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Result:
    def __init__(self, tab):
        self.tab = tab

    def htree(self):
        return self.tab.tree()

    def is_valid(self):
        return self.tab.is_closed()


class ClassicalSolver:
    """A simple solver for classical propositional logic."""

    def solve(self, premises: List[forms.Formula], concusions: List[forms.Formula]):
        queue = []
        tab = Tableau(premises, concusions)
        root = tab.root
        queue += [root] + list(root.descendants)
        while queue:
            logger.debug("queue: %s", queue)

            item = queue.pop(0)

            Tactic = namedtuple("Tactic", ["condition", "rule"])

            # TODO: Use structural pattern matching with Python 3.10
            tactics = [
                Tactic(
                    lambda item: isinstance(item.fml, forms.Negation)
                    and isinstance(item.fml.sub, forms.Negation),
                    rules.DoubleNegationRule(),
                ),
                Tactic(
                    lambda item: isinstance(item.fml, forms.Conjunction),
                    rules.ConjunctionRule(),
                ),
                Tactic(
                    lambda item: isinstance(item.fml, forms.Negation)
                    and isinstance(item.fml.sub, forms.Disjunction),
                    rules.NegatedDisjunctionRule(),
                ),
                Tactic(
                    lambda item: isinstance(item.fml, forms.Negation)
                    and isinstance(item.fml.sub, forms.Conditional),
                    rules.NegatedConditionalRule(),
                ),
                Tactic(
                    lambda item: isinstance(item.fml, forms.Disjunction),
                    rules.DisjunctionRule(),
                ),
                Tactic(
                    lambda item: isinstance(item.fml, forms.Negation)
                    and isinstance(item.fml.sub, forms.Conjunction),
                    rules.NegatedConjunctionRule(),
                ),
                Tactic(
                    lambda item: isinstance(item.fml, forms.Conditional),
                    rules.ConditionalRule(),
                ),
            ]
            rule = next((t.rule for t in tactics if t.condition(item)), None)
            if rule:
                logger.debug("applying rule: %s", rule)
                queue_items = tab.apply_and_queue(item, rule)
                queue += queue_items
                logger.debug("added to queue: %s", queue_items)

        return Result(tab)
