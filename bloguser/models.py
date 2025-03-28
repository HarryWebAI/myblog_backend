from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from shortuuidfield import ShortUUIDField


class BlogUserManager(BaseUserManager):
    """
    重写 UserManager
    """
    use_in_migrations = True

    # 创建用户
    def _create_user(self, email, name, telephone, password, **extra_fields):
        if not email:
            raise ValueError("必须设置登录账号!")
        if not name:
            raise ValueError("必须填写姓名!")
        if not telephone:
            raise ValueError("必须填写电话!")
        user = self.model(email=email, name=name, telephone=telephone, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    # 普通用户
    def create_user(self, email=None, name=None, telephone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, name, telephone, password, **extra_fields)

    # 超级用户
    def create_superuser(self, email=None, name=None, telephone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置is_staff = True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置is_superuser = True")

        return self._create_user(email, name, telephone, password, **extra_fields)


class BlogUser(AbstractBaseUser, PermissionsMixin):
    """
    重写 User
    """
    uid = ShortUUIDField(primary_key=True)
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=10)
    telephone = models.CharField(max_length=11, unique=True)
    avatar = models.CharField(max_length=255, default='/media/avatar/default.png')

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    objects = BlogUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name', 'telephone', 'password']

    class Meta:
        ordering = ['is_active', 'last_login']