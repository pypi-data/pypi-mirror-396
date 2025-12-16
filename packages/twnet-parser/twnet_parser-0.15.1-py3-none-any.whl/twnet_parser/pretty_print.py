class PrettyPrint():
    def __repr__(self):
        return "<class: '" + str(self.__class__.__name__) + "'>"
    def __str__(self):
        return "<class: '" + str(self.__class__.__name__) + "'>: " + str(self.__dict__)

