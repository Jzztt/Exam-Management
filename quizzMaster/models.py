from django.db import models
from django.utils.timezone import now

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
class Role(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Subject(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    lecturer = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


from django.contrib.auth.models import BaseUserManager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password
from django.utils.timezone import now
class User(AbstractBaseUser,BaseModel):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


    def __str__(self):
        return self.username

class UserSubject(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'subject')
    def __str__(self):
        return f"{self.user.username} - {self.subject.name}"

from cloudinary.models import CloudinaryField
class Question(BaseModel):
    question_text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    is_mixed = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text

class Exam(BaseModel):
    exam_code = models.CharField(max_length=100, unique=True)
    duration = models.IntegerField()
    num_questions = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return self.exam_code


class ExamQuestion(BaseModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class ExamSchedule(BaseModel):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

class Choice(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    option = models.CharField(max_length=1)


class CorrectAnswer(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

class Submission(BaseModel):
    score = models.FloatField()
    answers = models.JSONField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

