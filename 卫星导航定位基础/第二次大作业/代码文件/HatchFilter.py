class HatchFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.previous_value = None
        self.smoothed_values = []

    def filter(self, carrier_phase, pseudorange):
        if self.previous_value is None:
            self.previous_value = pseudorange - carrier_phase
        else:
            self.previous_value = self.alpha * self.previous_value + \
                                  (1 - self.alpha) * (pseudorange - carrier_phase)
        self.smoothed_values.append(self.previous_value)
        return self.previous_value