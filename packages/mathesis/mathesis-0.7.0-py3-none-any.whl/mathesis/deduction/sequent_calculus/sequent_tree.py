from __future__ import annotations

from itertools import count
from operator import itemgetter

from anytree import PostOrderIter, RenderTree

from mathesis.deduction.sequent_calculus.sequent import Sequent, SequentItem
from mathesis.forms import Formula


class SequentTree:
    """A tree of sequents."""

    def __init__(self, premises: list[Formula], conclusions: list[Formula]):
        self.counter = count(1)
        self.bookkeeper = dict()
        left, right = (premises, conclusions)
        sequent = Sequent(left, right)
        for item in sequent.items:
            item.n = next(self.counter)
            self.bookkeeper[item.n] = item
        self.root = sequent

    def __getitem__(self, index):
        return self.bookkeeper[index]

    def _apply(self, target: SequentItem, rule):
        queue_items = itemgetter("queue_items")(rule.apply(target, self.counter))

        new_sequents = []

        for branch in queue_items:
            for node in branch.items:
                self.bookkeeper[node.n] = node
            branch.parent = target.sequent
            new_sequents.append(branch)

        return new_sequents

    def apply(self, target: SequentItem, rule):
        self._apply(target, rule)
        return self

    def tree(self, number=True):
        output = ""
        for pre, fill, node in RenderTree(self.root):
            output += "{}{}\n".format(
                pre,
                "{} ⇒ {}{}".format(
                    ", ".join(
                        map(
                            lambda x: str(x) + (f" {x.n}" if number else ""),
                            node.left,
                        )
                    ),
                    ", ".join(
                        map(
                            lambda x: str(x) + (f" {x.n}" if number else ""),
                            node.right,
                        )
                    ),
                    f" [{node.derived_by}]" if node.derived_by is not None else "",
                ),
            )
        return output

    def latex(self, number=False, arrow=r"\Rightarrow"):
        output = ""
        for node in PostOrderIter(self.root):
            if node.derived_by is not None and hasattr(node.derived_by, "latex"):
                label_part = f"\\RightLabel{{{node.derived_by.latex()}}}\n"
            else:
                label_part = ""

            tmpl = ""
            if len(node.children) == 0:
                tmpl += r"\AxiomC{{${}$}}"
            elif len(node.children) == 1:
                tmpl += r"\UnaryInfC{{${}$}}"
            elif len(node.children) == 2:
                tmpl += r"\BinaryInfC{{${}$}}"
            output += label_part + tmpl.format(node.latex()) + "\n"
        return """\\begin{{prooftree}}\n{}\\end{{prooftree}}""".format(output)
