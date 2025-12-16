from itertools import count

from mathesis.deduction.sequent_calculus import rules as classical_rules


class Weakening:
    class Left(classical_rules.Weakening.Left):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) == 1, "Right side length of the sequent must be 1"
            return super().apply(target, tip, counter=counter)

    class Right(classical_rules.Weakening.Right):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)


class Negation:
    class Left(classical_rules.Negation.Left):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) == 0, "Right side length of the sequent must be empty"
            return super().apply(target, tip, counter=counter)

    class Right(classical_rules.Negation.Right):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) == 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)


class Conjunction:
    class Left(classical_rules.Conjunction.Left):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)

    class Right(classical_rules.Conjunction.Right):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)


class Disjunction:
    class Left(classical_rules.Disjunction.Left):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)

    class Right(classical_rules.Disjunction.Right):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)


class Conditional:
    class Left(classical_rules.Conditional.Left):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)

    class Right(classical_rules.Conditional.Right):
        def apply(self, target, tip, counter=count(1)):
            right = target.sequent_node.sequent.right
            assert len(right) <= 1, "Right side length of the sequent must be 0 or 1"
            return super().apply(target, tip, counter=counter)
