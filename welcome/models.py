from django.db import models

# Create your models here.
class Welcome(models.Model):
    title = models.CharField(max_length=10)
    buttonText = models.CharField(max_length=10)

class Description(models.Model):
    content = models.CharField(max_length=10)
    welcome = models.ForeignKey(Welcome, on_delete=models.CASCADE, related_name='descriptions', related_query_name='descriptions')