#class
class People:
    ZPY = 23

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def changeName(self, Newname):
        self.name = Newname
    def changeAge(self, Newage):
        self.age = Newage

    def jianghua(self):
        print("Hello, my name is %s, I am %d years old." % (self.name, self.age))

people = People("ZhangSan", 23)
print(people.jianghua())


# alist = list(range(10))
# aList.append(5)
# aList._class_

