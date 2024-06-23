# users/views.py
import jwt
from django.contrib.auth.models import User
from rest_framework import generics, status ,permissions,viewsets
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import random
import string

from .serializers import *
from rest_framework.views import APIView
from .models import *
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from .permissions import CustomReadOnly
from knox.auth import TokenAuthentication
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
SECRET_KEY = settings.SECRET_KEY
from rest_framework_simplejwt.views import TokenObtainPairView

# 회원가입 할 때 

def index(request):
    return JsonResponse({'message': 'Welcome to the main page!'})
# view에서 설정하는 것은 그 페이지안에서 활용될 수 있는 기능들을 만드는 곳 

class LoginView(TokenObtainPairView): # post 가 내부적으로 구현되어있음 , 로그인할 때만 token 얻을 수 있게 하는거
    serializer_class = LoginSerializer


class RegisterView(generics.CreateAPIView): # 회원가입 
    queryset = User.objects.all()
    serializer_class = UserSerializer



class UserInformUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()  # User 모델 대신 Profile 모델을 사용
    serializer_class = UserUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if 'user_pic' in request.FILES:
            user_pic = request.FILES['user_pic']
            file_name = default_storage.save(profile_pic_upload_to(user, user_pic.name), ContentFile(user_pic.read()))
            file_url = default_storage.url(file_name)
            user.user_pic_url = file_url  # URL 필드에 저장
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserListView(generics.ListAPIView): # 인스타 처럼 유저 화면 
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly,CustomReadOnly]


class PostListView(generics.ListAPIView): # 게시물 조회 페이지 
    queryset = Post.objects.all()
    serializer_class = PostListSerializer


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        post_data = request.data.copy()
        image_fields = ['image1', 'image2','image3','image4','image5']

        for field in image_fields:
            if field in request.FILES:
                image_file = request.FILES[field]
                file_name = default_storage.save(f'post_pics/{image_file.name}', image_file)
                file_url = default_storage.url(file_name)
                post_data[f'{field}_url'] = file_url  # URL을 post_data에 추가

        serializer = self.get_serializer(data=post_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView): # 게시물 수정,삭제 다 됨 
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        post_data = request.data.copy()
        image_fields = ['image1', 'image2', 'image3', 'image4', 'image5']

        for field in image_fields:
            if field in request.FILES:
                image_file = request.FILES[field]
                file_name = default_storage.save(f'post_pics/{image_file.name}', ContentFile(image_file.read()))
                file_url = default_storage.url(file_name)
                post_data[f'{field}_url'] = file_url

        serializer = self.get_serializer(post, data=post_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly,CustomReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)



class CodeCreateView(generics.CreateAPIView):
    queryset = Code.objects.all()
    serializer_class = CodeSerializer
    # permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        code = ''.join(random.choices(string.digits, k=4))
        while Code.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.digits, k=4))
        Code.objects.create(code=code)
        return Response({'code': code}, status=status.HTTP_201_CREATED)

class AttandanceCheckView(generics.CreateAPIView):
    queryset = Attandance.objects.all()
    serializer_class = AttandanceSerializer
    # permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        code = request.data.get('code')
        try:
            code_obj = Code.objects.get(code=code, valid_until__gte=timezone.now())
            attandance, created = Attandance.objects.get_or_create(user=request.user)
            attandance.check_count += 1  # 필드 이름을 check에서 check_count로 변경
            attandance.save()
            return Response({'message': '확인되었습니다'}, status=status.HTTP_200_OK)
        except Code.DoesNotExist:
            return Response({'error': '다시 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
# view 3개 필요한거 아녀? list , create , 수정,삭제 

class Image(APIView):
    def post(self,request, format=None):
        serializers = PhotoSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)