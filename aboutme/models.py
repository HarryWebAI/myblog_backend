from django.db import models

# 根绝前端数据模型，创建数据库模型

class WorkExperience(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    period = models.CharField(max_length=50)
    achievements = models.JSONField()  # 存储字符串数组
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period']

    def __str__(self):
        return f"{self.title} at {self.company}"

class Education(models.Model):
    major = models.CharField(max_length=100)
    school = models.CharField(max_length=100)
    period = models.CharField(max_length=50)
    degree = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period']

    def __str__(self):
        return f"{self.degree} in {self.major} at {self.school}"

class Project(models.Model):
    name = models.CharField(max_length=100)
    techStack = models.CharField(max_length=200)
    details = models.JSONField()  # 存储字符串数组
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SkillCategory(models.Model):
    name = models.CharField(max_length=50)
    skills = models.JSONField()  # 存储字符串数组
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
