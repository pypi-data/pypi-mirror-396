class NumericTruthValues:
    # TODO: support for a range for values and a function for designated_values
    def __init__(self, values=[0, 1], designated_values=[1]):
        self.values = values
        self.designated_values = designated_values
