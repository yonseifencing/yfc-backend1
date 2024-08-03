from django.db import models
from .validators import validate_no_special_characters
from datetime import date
from datetime import timedelta
from django.utils import timezone

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
import random


def post_pic_upload_to(instance, filename):
    return f'post_pics/{filename}'

def profile_pic_upload_to(instance, filename):
    return f'user_pic/{filename}'


class UserManager(BaseUserManager):
    # 일반 user 생성
    def create_user(self, student_number, password=None, **extra_fields):
        if not student_number:
            raise ValueError('must have email')

        user = self.model(
            student_number=student_number,
            **extra_fields  # 추가 필드 값
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
        # 관리자 user 생성
    def create_superuser(self, student_number, password):
        user = self.create_user(
            student_number=student_number,
            password = password

        )
        user.is_admin = True
        user.save(using=self._db)
        return user






#학번 중복 체크 문자 반환 

class User(AbstractBaseUser):
    
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=6,
        validators=[validate_no_special_characters],
    ) 
    user_pic = models.FileField(upload_to=profile_pic_upload_to, blank=True)
    user_pic_url = models.URLField(blank=True, default='https://yonfen.s3.amazonaws.com/default_profile_pic.jpg')  # 기본 이미지 
    student_number = models.CharField(
        max_length=14,
        unique=True,
        error_messages={'unique':'이미 등록된 학번입니다'} )
    
    # 성별 
    GENDER_CHOICES = [
        ('여자', '여자'),
        ('남자', '남자'),
    ]
    gender = models.CharField(max_length=2 , choices=GENDER_CHOICES,null=True) # 왜 인지는 모르겟는데 null 은 계속 True로 설정해야 됨 

    
     # 입부년도 
    phone_number = models.CharField(max_length=13) #  help_text=('예시: 010-1234-5678') 이런식으로 프론트에서 
    email = models.EmailField(max_length=254,verbose_name='email', unique=True,null=True)
    is_admin = models.BooleanField(default=False) # 추가한거 

    # is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 

	# 헬퍼 클래스 사용
    objects = UserManager()

	# 사용자의 username field는 email으로 설정 (이메일로 로그인)
    USERNAME_FIELD = 'student_number'
    
    def __str__(self):
        return self.student_number

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property 
    def is_staff(self):
        return self.is_admin
    @receiver(post_save, sender=User) 
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
         Student.objects.create(user=instance) 
    # user 인스턴스가 생성될 때 마다 자동으로 관련된 student 인스턴스가 생성되도록 하고 사용자와 학생 정보가 자동으로 연결됨 
    
    

# profile 에서 user_pic 이랑 상태만 받으면 될 듯 그리고 리시버 사용하면 됨 
class Student(models.Model):# 여기다가는 학교에 대한 것들을 적어둘까 기본 유저 는 유저에 두고 근데 왜 그래야지? 커리 검색이 쉬워지나? 
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    
    major = models.CharField(
        max_length=20,
        
        validators=[validate_no_special_characters],)
    
    current_year = date.today().year
    YEAR_CHOICES = [(str(year) + '-' + str(semester), str(year) + '-' + str(semester)) for year in range(1987, current_year +1) for semester in [1, 2]]
    join_year = models.CharField(
        max_length=7,
        choices=YEAR_CHOICES,
        default='2020-1', )  
    STATUS_CHOICES = [
        ('졸업', '졸업'),
        ('재학', '재학'),
        ('휴학', '휴학'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    FENCING_CHOICES = [
        ('플뢰레','플뢰레'),
        ('에페','에페'),
        ('사브르','사브르'),
        ('미정','미정'),
    ]
    fencing = models.CharField(max_length=10,choices=FENCING_CHOICES)







class Post(models.Model):  
    # id 필드 안만들어도됨 자동임  , 근데 이렇게 만드는게 맞나? 설정을 
    title = models.CharField(max_length=50)
    image1 = models.FileField(upload_to=post_pic_upload_to,blank=True) # 용량 확장 공사 진행해야 되고 , 프론트에서 필드를 추가할때 +누르면 이미지 필드 나올 수 있게 하면 되지 않을까
    image1_url = models.URLField(blank=True)

    image2 = models.FileField(upload_to=post_pic_upload_to,blank=True) # > 이미지 , 동영상 > 외부 스토리지에 저장하고 mongodb에 url 저장해야됨 
    image2_url = models.URLField(blank=True)

    image3 = models.FileField(upload_to=post_pic_upload_to,blank=True)
    image3_url = models.URLField(blank=True)

    image4 = models.FileField(upload_to=post_pic_upload_to,blank=True)
    image4_url = models.URLField(blank=True)

    image5 = models.FileField(upload_to=post_pic_upload_to,blank=True)
    image5_url = models.URLField(blank=True)
    # image6 = models.ImageField(upload_to='post_pics',blank=True)
    # image7 = models.ImageField(upload_to='post_pics',blank=True)
    # image8 = models.ImageField(upload_to='post_pics',blank=True)
    # image9 = models.ImageField(upload_to='post_pics',blank=True)
    # image10 = models.ImageField(upload_to='post_pics',blank=True)
    content = models.TextField()
    dt_created = models.DateTimeField(auto_now_add=True)

    dt_updated = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE ,related_name='posts') # 이렇게 등록하면 post 에 대한 글 화면 비출 때 user 화면 띄울 수 있음 
    # likes = GenericRelation('Like', related_query_name='review') like 모델 연결하면 
    # author 이렇게 하면 값은 user 에 id 값이 들어가는건가?
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-dt_created'] # 최신순으로 
 # 이게 무슨 역할인지 모르겠네 
class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments') # 역참조 post모델에서>post.commets.all() 이런식으로 접근가능 
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comments')
    created_at = models.DateField(auto_now_add=True)
    comment = models.TextField()
    def __str__(self):
        return self.comment 
# class Attandance(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attandace')
#     check_count = models.IntegerField(default=0)  # 필드 이름을 check에서 check_count로 변경

# class Code(models.Model):
#     code = models.CharField(max_length=4, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     valid_until = models.DateTimeField()

#     def save(self, *args, **kwargs):
#         if not self.valid_until:
#             self.valid_until = timezone.now() + timedelta(hours=2)
#         super().save(*args, **kwargs)

class test(models.Model):
    testfield = models.CharField(max_length=200)
    photo = models.FileField()
    def __str__(self):
        return self.testfield
    


class Code(models.Model):
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class UserAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.IntegerField(default=0)  # 1로 변경될 필드
    last_attendance_date = models.DateField(null=True, blank=True)  # 마지막 출석 날짜
    total_attendances = models.IntegerField(default=0)  # 총 출석 횟수

    def check_code(self, code_input):
        if self.code.code == code_input: # self.code.code는 UserAttendance 인스턴스가 참조하는 Code 모델 인스턴스의 code 필드
            self.is_correct = 1  # 출석 시 1로 설정
            self.last_attendance_date = timezone.now().date()  # 마지막 출석 날짜 업데이트
            self.total_attendances += 1  # 총 출석 횟수 증가
            self.save()  # 변경된 필드 저장
            self.update_ranking()
        else:
            self.is_correct = 0  # 출석 실패 시 0으로 설정
            self.save()

    def update_ranking(self):
        ranking, created = Ranking.objects.get_or_create(user=self.user) # 연결된 객체를 가져오거나 존재하지 않으면 새로 생성 
        ranking.score += 0.5 # rangking 모델에 score 에 0.5추가 
        ranking.save()

class Ranking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # 
    score = models.FloatField(default=0.0) #출석 점수 
    rank_score = models.FloatField(default=0.0) # 랭킹전을 통해 부여된 점수 
    total_score = models.FloatField(default=0.0, editable=False) # 토탈 점수 
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_score = self.score + self.rank_score
        super().save(*args, **kwargs)

    def update_rank_score(self, rank):
        rank_points = {1: 10, 2: 8, 3: 6, 4: 4, 5: 2}
        self.rank_score = rank_points.get(rank, 0)
        self.save()

        # 일단 jwt 이런거 다 끄고 실험해 봐야 할 듯 