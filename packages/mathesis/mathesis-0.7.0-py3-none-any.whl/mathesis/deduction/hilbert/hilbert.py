import logging
from itertools import count
from operator import itemgetter
from types import SimpleNamespace
from typing import Any

from anytree import Node, RenderTree, find_by_attr

from mathesis import _utils, forms
from mathesis.deduction.sequent_calculus import SequentTree
from mathesis.forms import Formula
from mathesis.deduction.hilbert.axioms import Axiom, _apply_axiom

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Hilbert:
    counter = count(1)

    def __init__(self, premises: list[Formula], conclusion: Formula):
        assert isinstance(conclusion, Formula), "Conclusion must be a single formula"
        self._sequent_tree = SequentTree(premises, [conclusion])
        self.bookkeeper = self._sequent_tree.bookkeeper
        self.counter = self._sequent_tree.counter

        # Proof tree
        for item in self._sequent_tree.root.left:
            item.subproof = Node(item, children=[])
        self._sequent_tree.root.right[0].subproof = Node(
            self._sequent_tree.root.right[0],
            children=[item.subproof for item in self._sequent_tree.root.left],
        )

    def __getitem__(self, index):
        return self.bookkeeper[index]

    def axiom(self, target, axiom: Axiom):
        res = _apply_axiom(target, axiom.formula, self.counter)
        queue_items = res["queue_items"]

        # new_sequents = []

        for branch in queue_items:
            for node in branch.items:
                self.bookkeeper[node.n] = node
            branch.parent = target.sequent
            # new_sequents.append(branch)

        return self

    def apply(self, target: Node, rule):
        res = rule.apply(target, self.counter)
        queue_items = res["queue_items"]

        # new_sequents = []

        for branch in queue_items:
            for node in branch.items:
                self.bookkeeper[node.n] = node
            branch.parent = target.sequent
            # new_sequents.append(branch)

        return self

    def tree(self, style=None, number=True):
        if style == "gentzen":
            output = ""
            root = self._sequent_tree.root.right[0].subproof
            for pre, fill, node in RenderTree(root):
                output += "{}{} {}\n".format(
                    pre,
                    f"[{node.name}]" if getattr(node, "marked", False) else node.name,
                    # self.proof_tree.mapping[node].n,
                    " ×" if getattr(node, "marked", False) else "",
                )
            return output
        else:
            return self._sequent_tree.tree(number=number)

    # def latex(self, number=False, arrow=r"\Rightarrow"):
    #     output = ""
    #     root = self._sequent_tree.root.right[0].subproof
    #     for node in PostOrderIter(root):
    #         tmpl = ""
    #         if len(node.children) == 0:
    #             tmpl = r"\AxiomC{{${}$}}"
    #         elif len(node.children) == 1:
    #             tmpl = r"\UnaryInfC{{${}$}}"
    #         elif len(node.children) == 2:
    #             tmpl = r"\BinaryInfC{{${}$}}"
    #         elif len(node.children) == 3:
    #             tmpl = r"\TrinaryInfC{{${}$}}"
    #         output += tmpl.format(node.name.fml.latex()) + "\n"
    #     return """\\begin{{prooftree}}\n{}\\end{{prooftree}}""".format(output)
