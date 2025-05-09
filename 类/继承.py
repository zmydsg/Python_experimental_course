class Animal():
    def __init__(self,name,age):
        self.__name = name
        self.__age = age
    def speak(self):
        print('speak:')
    def get_name(self):
        print(self.__name)
    def get_age(self):
        print(self.__age)
    def set_name(self,name):
        self.__name = name
    def set_age(self,age):
        self.__age = age

#法一，逐个继承，重写方法
class Lion(Animal):
    def __init__(self, name, age):
        super().__init__(name, age)
    def speak(self):
        print('Roarl!')

class Elephant(Animal):
    def __init__(self, name, age):
        super().__init__(name, age)
    def speak(self):
        print('Trumpet!')
#法二，定义一个函数，通过参数实现
def animal_sound(animal):
    animal.speak()

class Zoo():
    def __init__(self):
        self.animals = []

    def add_animal(self, animal: Animal, *args: Animal):
        self.animals.append(animal)
        for arg in args:
            self.animals.append(arg)

    def remove_animals(self,name):
        for animal in self.animals:
            if animal == name:
                self.animals.remove(animal)

    #附加题
    def make_all_speak(self):
        for animal in self.animals:
            animal.speak()
        #用重载，接受任意个数的动物参数量，让他们都叫一下
    
# 测试代码
zoo = Zoo()
simba = Lion("Simba", 5)
dumbo = Elephant("Dumbo", 10)

zoo.add_animal(simba, dumbo)
zoo.make_all_speak()
