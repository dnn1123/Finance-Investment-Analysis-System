class backtestOrder(object):
    def __init__(self,code,position,price,amount,commission,time):
        self.__code = code
        self.__position= position
        self.__price= price
        self.__amount=amount
        self.__commission=commission
        self.__time=time
    @property
    def code(self):
        return self.__code

    @property
    def position(self):
        return self.__position

    @property
    def price(self):
        return self.__price

    @property
    def amount(self):
        return self.__amount

    @property
    def commission(self):
        return self.__commission

    @property
    def time(self):
        return self.__time
    # @age.setter
    # def age(self,age):
    #     if isinstance(age,str):
    #         self._age = int(age)
    #     elif isinstance(age,int):
    #         self._age = age
    # @age.deleter
    # def age(self):
    #     del self._age