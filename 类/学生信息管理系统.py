class Student:
    def __init__(self, name, age, student_id):
        self.name = name
        self.age = age
        self.student_id = student_id

    def __str__(self):  # 修正方法名
        return f"Student(Name: {self.name}, Age: {self.age}, ID: {self.student_id})"
    
class StudentManager:
    def __init__(self):
        self.students = []  # 存储学生对象的列表

    def add_student(self, student):
        """
        添加一个学生对象到列表中
        参数:
            student: Student对象
        """
        self.students.append(student)
        print(f"{student.name} 已被添加。")

    def remove_student(self, student_id):
        """
        根据学生ID移除学生对象
        参数:
            student_id: 学生的ID
        """
        for student in self.students:
            if student.student_id == student_id:
                self.students.remove(student)
                print(f"{student.name} 已被移除。")
                return
        print(f"没有找到ID为 {student_id} 的学生。")

    def get_student(self, student_id):
        """
        根据学生ID获取学生对象
        参数:
            student_id: 学生的ID
        返回:
            Student对象或None
        """
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def get_all_students(self):
        """
        获取所有学生对象
        返回:
            学生对象列表
        """
        for student in self.students:
            print(student.__str__())
        return self.students
    
# 创建 StudentManager 实例
manager = StudentManager()  # 添加这行

# 创建几个学生实例，测试系统功能
student1 = Student("Alice", 20, "S001")
student2 = Student("Bob", 22, "S002")
student3 = Student("Charlie", 21, "S003")

# 使用实例方法调用
manager.add_student(student1)
manager.remove_student("S002")
print(manager.get_student("S001"))
print(manager.get_all_students())
