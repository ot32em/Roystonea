
class myclass():
    @classmethod
    def hello(cls):
        print( cls)
        print("class helloworld")

    @staticmethod
    def hellostatic():
        print("static hellowrld")

class my2class(myclass):
    pass

my2class.hello()
