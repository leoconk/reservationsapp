from django.db import models

# Create your models here.
class Table(models.Model):
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"Table {self.id} (Capacity: {self.capacity})"

class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # 👈 ADD THIS
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Table {self.table.id} - {self.name} - {self.start_time} to {self.end_time}"
