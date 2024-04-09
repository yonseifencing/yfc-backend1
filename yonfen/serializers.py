# users/serializers.py
# from django.contrib.auth.models import User # User 모델
from django.contrib.auth.password_validation import validate_password # Django의 기본 pw 검증 도구
from .models import Profile, Post ,User
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



class UserSerializer(serializers.ModelSerializer):
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

# # 회원가입 시리얼라이저
# class RegisterSerializer(serializers.ModelSerializer):
    
#     password = serializers.CharField(
#         write_only=True,
#         required=True,
#         validators=[validate_password], # 비밀번호에 대한 검증
#     )
#     password2 = serializers.CharField( # 비밀번호 확인을 위한 필드
#         write_only=True,
#         required=True,
#     ) 
    

#     class Meta:
#         model = User
#         # fields = ('username', 'email', 'password', 'password2')
#         fields = ('name','student_number','major','join_year','phone_number','password','password2')

#     def validate(self, data): # password과 password2의 일치 여부 확인
#         if data['password'] != data['password2']:
#             raise serializers.ValidationError(
#                 {"password": "Password fields didn't match."})
        
#         return data

#     def create(self, validated_data):
#         # CREATE 요청에 대해 create 메서드를 오버라이딩하여, 유저를 생성하고 토큰도 생성하게 해준다.
#         user = User.objects.create_user(
#             name=validated_data['name'],
#             student_number=validated_data['student_number'],
#             major=validated_data['major'],
#             join_year=validated_data['join_year'],
#             phone_number=validated_data['phone_number'],
#             email=validated_data['email'],
            
#         )

#         user.set_password(validated_data['password'])
#         user.save()
#         token = Token.objects.create(user=user)
#         return user


# class UserSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             student_number = validated_data['student_number'],
#             name = validated_data['name'],
#             password = validated_data['password']
#         )
#         return user
#     class Meta:
#         model = User
#         fields = ['student', 'email', 'name', 'password','password2','join_year','phone_number']
# 프런트와 소통하려면 시리얼 해야 하는데 굳이 안해도 되는 생성날짜나 이런것들 빼고 넣으면 될 듯 

# class LoginSerializer(serializers.Serializer):
#     student_number = serializers.CharField(required=True)
#     password = serializers.CharField(required=True, write_only=True)
#     # write_only=True 옵션을 통해 클라이언트->서버의 역직렬화는 가능하지만, 서버->클라이언트 방향의 직렬화는 불가능하도록 해준다.
    
#     def validate(self, data): # 유효성 검사 적용 
#         user = authenticate(**data)
#         if user:
#             token = Token.objects.get(user=user) # 해당 유저의 토큰을 불러옴
#             return token
#         raise serializers.ValidationError( # 가입된 유저가 없을 경우
#             {"error": "Unable to log in with provided credentials."}
#         )
class LoginSerializer(TokenObtainPairSerializer): # view.py tokenobtain과 연결해서 

    @classmethod # 이 부분은 아직이해가 잘 
    def get_token(cls, user):
        token = super().get_token(user)

        token['student_number'] = user.student_number # 페이로드에 추가하는 부분 > 
        token['name'] = user.name
        # 사용자 정보를 jwt 토큰 포함 시킴 > 로그인한 사용자의 정보를 바로 확인할 수 있음 

        return token


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

        # fields = ("id","title","image1","image2","image3","imgae4","image5","content","dt_created","dt_updated")
    def get_authors_student_number(self, obj):
        return obj.author.student_number

# 현재 프로필을 보여주는 밑에 게시글 보여주는 프로필 업데이트랑 같이해도 되기는 하는데 가독성상 
class ProfileViewSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True ,read_only = True)

    class Meta : 
        model = Profile
        fields = ("name", "user_pic", "student_number", "major","join_year")


# 프로필 업데이트 
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("name", "user_pic", "student_number", "major","join_year")
# django에서 form 이랑 비슷하다 그리고 여기가 데이터를 변환하는 곳 fields 에다가 이런 데이터들을 변환할거야 알려주고 
# profileserializer에 담는다 



# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = get_user_model()
#         fields = ('id','student_number', 'email', 'name', 'password', 'join_year','major','phone_number')

