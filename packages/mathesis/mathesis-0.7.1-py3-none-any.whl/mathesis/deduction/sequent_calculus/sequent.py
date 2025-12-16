from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
from typing import List

from anytree import NodeMixin

from mathesis.deduction import sequent_calculus
from mathesis.forms import Formula

sign = SimpleNamespace(
    **{
        "POSITIVE": "True",
        "NEGATIVE": "False",
    }
)


class SequentItem:
    n: int | None
    sequent: Sequent | None

    def __init__(
        self, fml: Formula, sign, n: int | None = None, sequent: Sequent | None = None
    ):
        self.fml = fml
        self.sign = sign
        self.n = n
        self.sequent = sequent

    def clone(self):
        clone = deepcopy(self)
        clone.__dict__ = deepcopy(clone.__dict__)
        return clone

    @property
    def name(self):
        return str(self)

    def __str__(self) -> str:
        return str(self.fml)


class Sequent(NodeMixin):
    """A sequent is a pair of premises and conclusions."""

    __items: list
    derived_by: sequent_calculus.rules.Rule | None
    # parent: Sequent | None
    # children: List[Sequent]

    def __init__(
        self,
        left: List[Formula],
        right: List[Formula],
        parent: Sequent | None = None,
        children: list[Sequent] | None = None,
    ):
        super().__init__()
        self.__items = []

        initial_items = []
        for fml in left:
            item = SequentItem(fml, sign.POSITIVE)
            initial_items.append(item)
        for fml in right:
            item = SequentItem(fml, sign.NEGATIVE)
            initial_items.append(item)

        self.items = initial_items
        self.parent = parent
        if children:
            self.children = children

        self.derived_by = None

    def __getitem__(self, index):
        if index == 0:
            return self.left
        elif index == 1:
            return self.right

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, value):
        for item in value:
            item.sequent = self
        self.__items = value

    @property
    def name(self):
        return str(self)

    @property
    def left(self) -> list[SequentItem]:
        return [item for item in self.items if item.sign == sign.POSITIVE]

    @property
    def right(self) -> list[SequentItem]:
        return [item for item in self.items if item.sign == sign.NEGATIVE]

    # @property
    def tautology(self):
        left = set(str(item.fml) for item in self.left)
        right = set(str(item.fml) for item in self.right)
        if left.intersection(right):
            return True
        else:
            return False

    def latex(self, arrow=r"\Rightarrow"):
        return "{} {} {}".format(
            ", ".join(map(lambda x: f"{x.fml.latex()}", self.left)),
            arrow,
            ", ".join(map(lambda x: f"{x.fml.latex()}", self.right)),
        )

    def __str__(self):
        return "{} ⇒ {}".format(
            ", ".join(map(lambda x: f"{x.name}", self.left)),
            ", ".join(map(lambda x: f"{x.name}", self.right)),
        )
