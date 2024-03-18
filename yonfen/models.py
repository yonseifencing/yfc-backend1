from django.db import models
from .validators import validate_no_special_characters
from datetime import date

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # primary_key를 User의 pk로 설정하여 통합적으로 관리
   
    name = models.CharField(
        max_length=10,
        
        validators=[validate_no_special_characters],
        error_messages={'unique':'이미 등록된 이름입니다'}
    )  # 이름
    user_pic = models.ImageField(default='default_profile_pic.jpg', upload_to='user_pics')
    # 유저 사진인데 이건 유저 페이지에서 수정버튼 누르면 될 듯 
    student_number = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        validators=[validate_no_special_characters],
        error_messages={'unique':'이미 등록된 학번입니다'}
    ) # 학번 
    major = models.CharField(
        max_length=20,
        
        validators=[validate_no_special_characters],
    
        
    ) # 학과
    current_year = date.today().year
    YEAR_CHOICES = [(str(year) + '-' + str(semester), str(year) + '-' + str(semester)) for year in range(1987, current_year +1) for semester in [1, 2]]
    join_year = models.CharField(
        max_length=7,
        choices=YEAR_CHOICES,
        default='2020-1', ) 
     # 입부년도 


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)