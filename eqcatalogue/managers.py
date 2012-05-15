"""
Managers definition
"""


class MeasureManager(object):
    def __init__(self, name):
        self.measures = []
        self.sigma = []
        self.name = name

    def __repr__(self):
        return self.name
