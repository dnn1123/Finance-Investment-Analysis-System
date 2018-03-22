class positionRecord(object):
    def __init__(self,code,shares,total_cost):
        self.__code = code
        self.__shares= shares
        self.__total_cost= total_cost
    @property
    def code(self):
        return self.__code
    @code.setter
    def code(self,value):
        self.__code=value
    @property
    def shares(self):
        return self.__shares
    @shares.setter
    def shares(self,value):
        self.__shares=value
    @property
    def total_cost(self):
        return self.__total_cost
    @total_cost.setter
    def total_cost(self,value):
        self.__total_cost=value
