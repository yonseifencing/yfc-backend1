from django.db import models
from .validators import validate_no_special_characters
from datetime import date

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError

# 펜싱부 로그인 메인 페이지에서 listcreate view 로 해야됨 
# status 랑 사진 수정 할 수 있게 profile.html 이 게시판이랑 이런거 다 볼 수 있는거네 
# ycc 처럼 get , post , put , 하면 될 듯 > 프로필 업데이트 페이지를 따로 만드는게 아니라 
 

# # 헬퍼 클래스
# class UserManager(BaseUserManager):
#     def create_user(self, student_number, password, **kwargs):
    	
#         if not student_number:
#             raise ValueError('학번 입력해주세요')
#         user = self.model(
#             student_number=self.student_number,
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, student_number=None, password=None, **extra_fields):
    	
#         superuser = self.create_user(
#             student_number=student_number,
#             password=password,
#         )
        
#         superuser.is_staff = True
#         superuser.is_superuser = True
#         superuser.is_active = True
        
#         superuser.save(using=self._db)
#         return superuser

# AbstractBaseUser를 상속해서 유저 커스텀


class UserManager(BaseUserManager):
    # 일반 user 생성
    def create_user(self, student_number, password=None, **extra_fields):
        if not student_number:
            raise ValueError('must have student number')

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
            student_number,
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
    student_number = models.CharField(
        max_length=14,
        unique=True,
        null=True,
        error_messages={'unique':'이미 등록된 학번입니다'}
    ) # 학번 
    major = models.CharField(
        max_length=20,
        
        validators=[validate_no_special_characters],
    )
    current_year = date.today().year
    YEAR_CHOICES = [(str(year) + '-' + str(semester), str(year) + '-' + str(semester)) for year in range(1987, current_year +1) for semester in [1, 2]]
    join_year = models.CharField(
        max_length=7,
        choices=YEAR_CHOICES,
        default='2020-1', ) 
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
    
    


# profile 에서 user_pic 이랑 상태만 받으면 될 듯 그리고 리시버 사용하면 됨 
class Profile(models.Model):# 여기다가는 학교에 대한 것들을 적어둘까 기본 유저 는 유저에 두고 근데 왜 그래야지? 커리 검색이 쉬워지나? 
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_pic = models.ImageField(default='default_profile_pic.jpg', upload_to='user_pics')# 유저 수정페이지 때 보내주면 될 듯 

    STATUS_CHOICES = [
        ('졸업', '졸업'),
        ('재학', '재학'),
        ('휴학', '휴학'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)






# 만들어야 될 게 게시판 , 출석체크 , 장비 관련 모델 
# post, put, get , patch 는 요청 crud는 기능 
# 게시판 만들때 댓글일아 , 좋아요 있으면 좋긴 하지 
# 요청을 게시판 list 는 get,[read]  요청만 받고 , 추가 버튼 누르면 post , [create] api 호출 , detail(게시물 들어가면) get,patch,[read,delete,update](개인) , 
# 모델 만들고 > 시리얼즈 하고 > view 3개 조금 어려운데 > url 3개  이렇게 하면 될 듯 
# 일단 게시물 만들고 좋아요와 코멘트 구현하기 
# 만약 한다고 하면 게시물에 들어갈 때 post와 create가 있어야 되는건가 
# 이 개념이 맞나 view에서 해당 url에서 필요한 기능을 genericapi 설정해서 보내면 그 안에서 는 여기서 정의한 것 만 사용할 수 있음 
# 게시판을 만드는데 공지게시판이랑 자유 게시판 만들면 될 듯 permission 에서 staff아니면 안된다고 하면 되지 않을까 
# 원래 풀스택에서 좋아요와 코멘트 어떻게 띄웠지 
# 모델 정의 > related_name 작성했고 > list view에 데이터를 추가했던거 같은데 
# 유저 리스트만 볼 수 있게 따로 만들고 옆에 버튼을 누르면 수정 페이지로 가게하면 되나 
# 로그인하고 > 바로 수정페이지로 가게끔 하고  
# 이런개념인가 view에서 해당 기능이 필요한 api 로 들어가면 거기서 일어나는 모든 작동은 view에서 정의한 api 한해서 결정되는건가 
# 삭제하면 삭제버튼을 누르면 api에서 가능하게끔 설정해뒀으니 그렇게 되는건가 ? 
class Post(models.Model):  
    # id 필드 안만들어도됨 자동임  , 근데 이렇게 만드는게 맞나? 설정을 
    title = models.CharField(max_length=50)
    image1 = models.ImageField(upload_to='post_pics',blank=True) # 용량 확장 공사 진행해야 되고 , 프론트에서 필드를 추가할때 +누르면 이미지 필드 나올 수 있게 하면 되지 않을까
    image2 = models.ImageField(upload_to='post_pics',blank=True) # > 이미지 , 동영상 > 외부 스토리지에 저장하고 mongodb에 url 저장해야됨 
    image3 = models.ImageField(upload_to='post_pics',blank=True)
    image4 = models.ImageField(upload_to='post_pics',blank=True)
    image5 = models.ImageField(upload_to='post_pics',blank=True)
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

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-dt_created'] # 최신순으로 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments') # 역참조 post모델에서>post.commets.all() 이런식으로 접근가능 
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comments')
    created_at = models.DateField(auto_now_add=True)
    comment = models.TextField()
    def __str__(self):
        return self.comment 
class Attandance(models.Model) : 
    User = models.ForeignKey(User, on_delete=models.CASCADE,related_name='attandace')
    

# 지금 필요한게 게시글 , 댓글 , 좋아요? 이고 좋아요를 누르면 그 사람이 무엇을 좋아하는지 알고리즘 돌릴 수 있지 않나?
# 모델 만들고 (전에 했던거 참고) , 시리얼라이즈 하고 , view 하면 되는데 궁금한게 
# 모델을 2~3개 이용해야 되는데 어떻게 사용하지 view 나 거기서 원래 view 에서 추가해서 보내줬는데 

