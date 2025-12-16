from anytree import Node, Walker
from itertools import count
from copy import copy

from mathesis import forms


class Rule:
    pass


class DoubleNegationRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        """
        Args:
            target: a node
            tip: a leaf node of the branch to extend
            counter: a counter
        """
        subsubfml = target.fml.sub.sub
        node = Node(
            str(subsubfml), sign=target.sign, fml=subsubfml, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [node],
            "counter": counter,
        }


class ConjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        conj1, conj2 = target.fml.subs
        node1 = Node(
            str(conj1), sign=target.sign, fml=conj1, parent=tip, n=next(counter)
        )
        node2 = Node(
            str(conj2), sign=target.sign, fml=conj2, parent=node1, n=next(counter)
        )
        return {
            "queue_items": [node1, node2],
        }


class NegatedConjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        conj1, conj2 = target.fml.sub.subs
        nconj1, nconj2 = map(lambda v: forms.Negation(v), [conj1, conj2])
        nodeL = Node(
            str(nconj1), sign=target.sign, fml=nconj1, parent=tip, n=next(counter)
        )
        nodeR = Node(
            str(nconj2), sign=target.sign, fml=nconj2, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [nodeL, nodeR],
            "counter": counter,
        }


class DisjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        disj1, disj2 = target.fml.subs
        nodeL = Node(
            str(disj1), sign=target.sign, fml=disj1, parent=tip, n=next(counter)
        )
        nodeR = Node(
            str(disj2), sign=target.sign, fml=disj2, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [nodeL, nodeR],
            "counter": counter,
        }


class NegatedDisjunctionRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        disj1, disj2 = target.fml.sub.subs
        ndisj1, ndisj2 = map(lambda v: forms.Negation(v), [disj1, disj2])
        node1 = Node(
            str(ndisj1), sign=target.sign, fml=ndisj1, parent=tip, n=next(counter)
        )
        node2 = Node(
            str(ndisj2), sign=target.sign, fml=ndisj2, parent=node1, n=next(counter)
        )
        return {
            "queue_items": [node1, node2],
            "counter": counter,
        }


class ConditionalRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        antec, conseq = target.fml.subs
        nantec = forms.Negation(antec)
        nodeL = Node(
            str(nantec), sign=target.sign, fml=nantec, parent=tip, n=next(counter)
        )
        nodeR = Node(
            str(conseq), sign=target.sign, fml=conseq, parent=tip, n=next(counter)
        )
        return {
            "queue_items": [nodeL, nodeR],
            "counter": counter,
        }


class NegatedConditionalRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        antec, conseq = target.fml.sub.subs
        nconseq = forms.Negation(conseq)
        node1 = Node(
            str(antec), sign=target.sign, fml=antec, parent=tip, n=next(counter)
        )
        node2 = Node(
            str(nconseq), sign=target.sign, fml=nconseq, parent=node1, n=next(counter)
        )
        return {
            "queue_items": [node1, node2],
            "counter": counter,
        }


class UniversalInstantiationRule(Rule):
    def __init__(self, replacing_term):
        self.replacing_term = replacing_term

    def apply(self, target, tip, counter=count(1)):
        target_variable = target.fml.variable
        # TODO: copy recusrively
        subfml = target.fml.sub.clone()
        # TODO: check if a valid replacing_term
        for term in subfml.free_terms:
            if term == target_variable:
                subfml = subfml.replace_term(term, self.replacing_term)
        # print(target_variable, subfml.terms)
        node = Node(
            str(subfml),
            sign=target.sign,
            fml=subfml,
            parent=tip,
            n=next(counter),
        )
        return {
            "queue_items": [[node]],
            "counter": counter,
        }


class NegatedUniversalRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        subfml = target.fml.sub
        subsubfml = subfml.sub.clone()
        fml = forms.Particular(subfml.variable, forms.Negation(subsubfml))
        node = Node(
            str(fml),
            sign=target.sign,
            fml=fml,
            parent=tip,
            n=next(counter),
        )
        return {
            "queue_items": [node],
            "counter": counter,
        }


class ParticularInstantiationRule(Rule):
    def __init__(self, replacing_term):
        self.replacing_term = replacing_term

    def apply(self, target, tip, counter=count(1)):
        target_variable = target.fml.variable
        # TODO: copy recusrively
        subfml = target.fml.sub.clone()

        # NOTE: check if a valid replacing_term
        ancestors = (tip,) + tip.ancestors
        for ancestor in ancestors:
            fml = ancestor.fml
            # print(fml, fml.free_terms)
            assert self.replacing_term not in fml.free_terms, "Replacing term has been already occurred in the branch"

        for term in subfml.free_terms:
            if term == target_variable:
                subfml.replace_term(term, self.replacing_term)
        node = Node(
            str(subfml),
            sign=target.sign,
            fml=subfml,
            parent=tip,
            n=next(counter),
        )
        return {
            "queue_items": [[node]],
            "counter": counter,
        }


class NegatedParticularRule(Rule):
    def apply(self, target, tip, counter=count(1)):
        subfml = target.fml.sub
        subsubfml = subfml.sub.clone()
        fml = forms.Universal(subfml.variable, forms.Negation(subsubfml))
        node = Node(
            str(fml),
            sign=target.sign,
            fml=fml,
            parent=tip,
            n=next(counter),
        )
        return {
            "queue_items": [[node]],
            "counter": counter,
        }
