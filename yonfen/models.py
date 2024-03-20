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
    )  # 이름 이름 똑 같은면 + 1 카운팅 되는거 입력해야 할 듯 
    # 그리고 남자인지 여자인지 써야 되나?
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
    title = models.CharField(max_length=50)
    image1 = models.ImageField(upload_to='post_pics',blank=True) # 용량 확장 공사 진행해야 되고 , 프론트에서 필드를 추가할때 +누르면 이미지 필드 나올 수 있게 하면 되지 않을까
    image2 = models.ImageField(upload_to='post_pics',blank=True)
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

    author = models.ForeignKey(User, on_delete=models.CASCADE ,related_name='reviews') # 이렇게 등록하면 post 에 대한 글 화면 비출 때 user 화면 띄울 수 있음 
    # likes = GenericRelation('Like', related_query_name='review') like 모델 연결하면 

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-dt_created'] # 최신순으로 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
