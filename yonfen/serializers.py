# users/serializers.py
# from django.contrib.auth.models import User # User 모델
from django.contrib.auth.password_validation import validate_password # Django의 기본 pw 검증 도구
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers
from rest_framework.authtoken.models import Token # Token 모델
from rest_framework.validators import UniqueValidator # 이메일 중복 방지를 위한 검증 도구
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
# Django의 기본 authenticate 함수 -> 우리가 설정한 DefaultAuthBackend인 TokenAuth 방식으로 유저를 인증해준다.

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             student_number = validated_data['student_number'],
#             password = validated_data['password']
#         )
#         return user


# 프로필 설정  
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("major","join_year","status","fencing")


class UserSerializer(serializers.ModelSerializer):
    student = ProfileSerializer()  # 각 사용자는 하나의 프로필을 가짐
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],  # 비밀번호에 대한 검증, validate_password는 내장 함수
    )
    password2 = serializers.CharField(  # 비밀번호 확인을 위한 필드
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ["student_number",'email', 'name', 'password', 'password2', 'phone_number', 'gender','student'] # 이게 순서에 영향을 받음 
        # drf 에서는 이렇게 student 모델을 user 모델 안으로 넣는다고 생각함 
    def validate(self, data):  # password와 password2의 일치 여부 확인
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 다릅니다."})
        return data

    def create(self, validated_data):
        student_data = validated_data.pop('student')
        user = User.objects.create_user(
            student_number = validated_data['student_number'],
            name=validated_data['name'],
            email=validated_data['email'],
            gender=validated_data['gender'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],  # 비밀번호 필드 추가
        )
        user.set_password(validated_data['password'])  # 암호화 저장
        user.save()  # 데이터베이스에 저장
        
        # Student 인스턴스 생성
        Student.objects.create(
            user=user,
            major=student_data['major'],
            join_year=student_data['join_year']
        )

        return user

class UserPostListSerializer(serializers.ModelSerializer):
    class Meta :
        model = Post
        fields = ('image1')




class UserProfileSerializer(serializers.ModelSerializer): # 유저 개인 페이지 시리얼라이즈 인스타 처럼 
    post = UserPostListSerializer
    class Meta : 
        models = User 
        fields = ('name','user_pic','post')

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("status")

class UserUpdateSerializer(serializers.ModelSerializer): # 유저 개인 프로필 수정 
    student = ProfileUpdateSerializer()
    class Meta : 
        model = User
        fields = ("phone_number","user_pic","student")

class PostSerializer(serializers.ModelSerializer): 
    class Meta : 
        model = Post
        fields = '__all__'


















# 원래 됐던거 원래데로 되돌릴려면 모델 수정해야 됨 
class uUserSerializer(serializers.ModelSerializer):
    student = ProfileSerializer()
    # password = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # 비밀번호에 대한 검증 , validate_password 는 내장 함수 
    )
    password2 = serializers.CharField( # 비밀번호 확인을 위한 필드
        write_only=True,
        required=True,
    )


    class Meta:
        model = User
        fields = ['student_number', 'email', 'name', 'password','password2', 'join_year', 'major', 'phone_number']
    def validate(self, data): # password과 password2의 일치 여부 확인
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "비밀번호가 다릅니다."})
        
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            student_number=validated_data['student_number'],
            major=validated_data['major'],
            join_year=validated_data['join_year'],
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            password=validated_data['password'],  # 비밀번호 필드 추가
        )
        user.set_password(validated_data['password']) # 암호와 저장 
        user.save() # 데이터베이스에 저장하는 
        return user
    


class LoginSerializer(TokenObtainPairSerializer): # view.py tokenobtain과 연결해서 

    @classmethod # 이 부분은 아직이해가 잘 
    def get_token(cls, user):
        token = super().get_token(user)

        token['student_number'] = user.student_number # 페이로드에 추가하는 부분 > 
        token['name'] = user.name
        # 사용자 정보를 jwt 토큰 포함 시킴 > 로그인한 사용자의 정보를 바로 확인할 수 있음 

        return token
    def validate(self, attrs):
        data = super().validate(attrs)

        data['message'] = "hello"

        return data


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.name')
    class Meta:
        model = Post
        fields = ('author','title','image1')

        # fields = ("id","title","image1","image2","image3","imgae4","image5","content","dt_created","dt_updated")
    def get_authors_student_number(self, obj):
        return obj.author.student_number
class PostCreateSerializer(serializers.ModelSerializer): # 폼처럼 사용하는 시리얼라이즈 
    class Meta:
        model = Post
        fields = '__all__'

class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.name') # user 정보는 post 로 들어와도 수정하지 못 하게 source 는 comment가 역관계이니까 user모델 에서도 student_number를 user 정보를 가져와서 user로 삼는다 
    class Meta:
        model = Comment
        fields = ['post', 'user', 'created_at', 'comment']

# 현재 프로필을 보여주는 밑에 게시글 보여주는 프로필 업데이트랑 같이해도 되기는 하는데 가독성상 
class ProfileViewSerializer(serializers.ModelSerializer):
    posts = PostListSerializer(many=True ,read_only = True)

    class Meta : 
        model = Student
        fields = ("name", "user_pic", "student_number", "major","join_year")


class PhotoSerializer(serializers.ModelSerializer):
    class Meta : 
        model = test
        fields = '__all__'


# class AttandanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attandance
#         fields = ['id', 'user', 'check_count']  # 필드 이름을 check에서 check_count로 변경

# class CodeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Code
#         fields = ['id', 'code', 'created_at', 'valid_until']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = '__all__'


class UserAttendanceSerializer(serializers.ModelSerializer):
    code_input = serializers.CharField(write_only=True) # 사용자 한테서 받을 코드 입력 창 굳이 모델에 만들지 않고 여기서 바로 비교 

    class Meta:
        model = UserAttendance
        fields = ['user', 'code', 'created_at', 'is_correct', 'last_attendance_date', 'total_attendances', 'code_input']

class RankingSerializer(serializers.ModelSerializer):
    user = UserSerializer() # 이렇게 하고 fields all 하면 유저 페이지 에 있는거 전부 소환 하는 거임 
    class Meta:
        model = Ranking
        fields = '__all__' 
        # 여기서도 바로 할 수 없나? 이건 내가 한 번 해볼까 