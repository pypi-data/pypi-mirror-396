from anytree import Node
from itertools import count

from mathesis import forms
from mathesis.deduction.tableau import sign


class Rule:
    pass


class PositiveNegationRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.POSITIVE, "Sign is not positive"
        assert isinstance(target.fml, forms.Negation), "Not a negation"
        subfml = target.fml.sub
        node = Node(
            str(subfml), sign=sign.NEGATIVE, fml=subfml, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [[node]],
            "counter": counter,
        }


class NegativeNegationRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.NEGATIVE, "Sign is not negative"
        assert isinstance(target.fml, forms.Negation), "Not a negation"
        subfml = target.fml.sub
        node = Node(
            str(subfml), sign=sign.POSITIVE, fml=subfml, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [[node]],
            "counter": counter,
        }


class NegationRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        if target.sign == sign.POSITIVE:
            return PositiveNegationRule().apply(target, tip, counter=counter)
        elif target.sign == sign.NEGATIVE:
            return NegativeNegationRule().apply(target, tip, counter=counter)


class PositiveConjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.POSITIVE, "Sign is not positive"
        assert isinstance(target.fml, forms.Conjunction), "Not a conjunction"
        conj1, conj2 = target.fml.subs
        node1 = Node(
            str(conj1), sign=target.sign, fml=conj1, parent=tip, n=next(counter)
        )
        node2 = Node(
            str(conj2), sign=target.sign, fml=conj2, parent=node1, n=next(counter)
        )
        return {
            "queue_items": [[node1, node2]],
        }


class NegativeConjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.NEGATIVE, "Sign is not negative"
        assert isinstance(target.fml, forms.Conjunction), "Not a conjunction"
        conj1, conj2 = target.fml.subs
        nodeL = Node(
            str(conj1), sign=sign.NEGATIVE, fml=conj1, parent=tip, n=next(counter)
        )
        nodeR = Node(
            str(conj2), sign=sign.NEGATIVE, fml=conj2, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [[nodeL], [nodeR]],
            "counter": counter,
        }


class ConjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        if target.sign == sign.POSITIVE:
            return PositiveConjunctionRule().apply(target, tip, counter=counter)
        elif target.sign == sign.NEGATIVE:
            return NegativeConjunctionRule().apply(target, tip, counter=counter)


class PositiveDisjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.POSITIVE, "Sign is not positive"
        assert isinstance(target.fml, forms.Disjunction), "Not a disjunction"
        disj1, disj2 = target.fml.subs
        nodeL = Node(
            str(disj1), sign=target.sign, fml=disj1, parent=tip, n=next(counter)
        )
        nodeR = Node(
            str(disj2), sign=target.sign, fml=disj2, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [[nodeL], [nodeR]],
            "counter": counter,
        }


class NegativeDisjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.NEGATIVE, "Sign is not negative"
        assert isinstance(target.fml, forms.Disjunction), "Not a disjunction"
        disj1, disj2 = target.fml.subs
        node1 = Node(
            str(disj1), sign=sign.NEGATIVE, fml=disj1, parent=tip, n=next(counter)
        )
        node2 = Node(
            str(disj2), sign=sign.NEGATIVE, fml=disj2, parent=node1, n=next(counter)
        )
        return {
            "queue_items": [[node1, node2]],
            "counter": counter,
        }


class DisjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        if target.sign == sign.POSITIVE:
            return PositiveDisjunctionRule().apply(target, tip, counter=counter)
        elif target.sign == sign.NEGATIVE:
            return NegativeDisjunctionRule().apply(target, tip, counter=counter)


class PositiveConditionalRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.POSITIVE, "Sign is not positive"
        assert isinstance(target.fml, forms.Conditional), "Not a conditional"
        antec, desc = target.fml.subs
        nodeL = Node(
            str(antec), sign=sign.NEGATIVE, fml=antec, parent=tip, n=next(counter)
        )
        nodeR = Node(
            str(desc), sign=sign.POSITIVE, fml=desc, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [[nodeL], [nodeR]],
            "counter": counter,
        }


class NegativeConditionalRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        assert target.sign == sign.NEGATIVE, "Sign is not negative"
        assert isinstance(target.fml, forms.Conditional), "Not a conditional"
        antec, desc = target.fml.subs
        node1 = Node(
            str(antec), sign=sign.POSITIVE, fml=antec, parent=tip, n=next(counter)
        )
        node2 = Node(
            str(desc), sign=sign.NEGATIVE, fml=desc, parent=node1, n=next(counter)
        )
        return {
            "queue_items": [[node1, node2]],
            "counter": counter,
        }


class ConditionalRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        if target.sign == sign.POSITIVE:
            return PositiveConditionalRule().apply(target, tip, counter=counter)
        elif target.sign == sign.NEGATIVE:
            return NegativeConditionalRule().apply(target, tip, counter=counter)
