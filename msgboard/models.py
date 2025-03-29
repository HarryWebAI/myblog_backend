from django.db import models
from bloguser.models import BlogUser


class Message(models.Model):
    """
    主留言模型
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(BlogUser, on_delete=models.CASCADE, verbose_name='用户')
    time = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    content = models.TextField(verbose_name='留言内容')

    class Meta:
        verbose_name = '留言'
        verbose_name_plural = verbose_name
        ordering = ['-time']

    def __str__(self):
        return f'{self.user.name}的留言 - {self.time}'


class Reply(models.Model):
    """
    回复模型
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(BlogUser, on_delete=models.CASCADE, verbose_name='用户')
    time = models.DateTimeField(auto_now_add=True, verbose_name='回复时间')
    content = models.TextField(verbose_name='回复内容')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='replies', verbose_name='关联的留言')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', verbose_name='父回复')

    class Meta:
        verbose_name = '回复'
        verbose_name_plural = verbose_name
        ordering = ['time']

    def __str__(self):
        return f'{self.user.name}的回复 - {self.time}'
