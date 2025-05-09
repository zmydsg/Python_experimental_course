class Animal:
    """动物基类，定义了所有动物共有的属性和方法"""
    def __init__(self, name, age):
        self.__name = name
        self.__age = age

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_age(self):
        return self.__age

    def set_age(self, age):
        self.__age = age

    def speak(self):
        """
        基类中的发声方法，只是一个占位或默认实现，
        具体的叫声由子类来重写(方法重写)。
        """
        return "Some generic animal sound."


class Lion(Animal):
    """狮子类，继承自Animal基类"""
    def __init__(self, name, age):
        super().__init__(name, age)
        #2
        # super().set_name(name)
        # super().set_age(age)

    def speak(self):
        """重写基类的speak方法，实现狮子的叫声"""
        return "Roar!"


class Elephant(Animal):
    """大象类，继承自Animal基类"""
    def __init__(self, name, age):
        super().__init__(name, age)

    def speak(self):
        """重写基类的speak方法，实现大象的叫声"""
        return "Trumpet!"


class Zoo:
    """动物园类，管理动物园中的所有动物"""
    def __init__(self):
        self.animals = []  # 存储动物对象的列表

    def add_animal(self, *new_animals):
        """
        一次可以添加一个或多个动物对象到动物园里
        参数:
            *new_animals: 可变参数，接收任意数量的Animal对象
        """
        for animal in new_animals:
            self.animals.append(animal)
            print(f"{animal.get_name()} 已被添加到动物园。")

    def remove_animal(self, animal):
        """
        从动物园中移除指定的动物实例
        参数:
            animal: 要移除的Animal对象
        """
        if animal in self.animals:
            self.animals.remove(animal)
            print(f"{animal.get_name()} 已从动物园移除。")
        else:
            print(f"{animal.get_name()} 不在动物园中。")

    def make_all_speak(self):
        """
        让动物园中所有动物发出叫声，并打印它们各自的名字、年龄与叫声
        这里体现了多态性：不同种类的动物对象调用相同的speak()方法会产生不同的结果
        """
        s = ""
        for animal in self.animals:
            
            print(f"{animal.get_name()}({animal.get_age()} 岁): {animal.speak()}")


if __name__ == "__main__":
    # 创建动物实例
    lion1 = Lion("Simba", 3)
    elephant1 = Elephant("Dumbo", 2)
    sheep = Lion("Mufasa", 5)

    tiger = Elephant("Ella", 6)
    def speak(Elephant):
        return "aoooo"
    tiger.speak = speak
    # 创建动物园实例
    my_zoo = Zoo()

    # 将动物添加到动物园
    my_zoo.add_animal(lion1, elephant1, lion2, elephant2)

    print("\n让动物园中所有动物发出各自的叫声：")
    # 让动物园中的所有动物发声
    my_zoo.make_all_speak()

    print("\n移除一只动物（Mufasa）并再听一下:")
    my_zoo.remove_animal(lion2)
    my_zoo.make_all_speak()
