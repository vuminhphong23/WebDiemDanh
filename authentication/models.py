from django.db import models

class Classroom(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100)

    def __str__(self):
        return self.class_name

class TblStudents(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    date_birth = models.DateField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='students', null=True)

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    student = models.ForeignKey(TblStudents, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True) 
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.datetime} - {'Present' if self.attended else 'Absent'}"
