
# users/views.py
import jwt
from django.contrib.auth.models import User
from rest_framework import generics, status ,permissions,viewsets
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from .models import Profile,Post,Comment
from rest_framework.permissions import IsAuthenticated
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
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# class RegisterAPIView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
            
#             # jwt 토큰 접근
#             token = TokenObtainPairSerializer.get_token(user)
#             refresh_token = str(token)
#             access_token = str(token.access_token)
#             res = Response(
#                 {
#                     "user": serializer.data,
#                     "message": "register successs",
#                     "token": {
#                         "access": access_token,
#                         "refresh": refresh_token,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )
            
#             # jwt 토큰 => 쿠키에 저장
#             res.set_cookie("access", access_token, httponly=True)
#             res.set_cookie("refresh", refresh_token, httponly=True)
            
#             return res
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class AuthAPIView(APIView):
#     # 로그인
#     def post(self, request):
#       # 유저 인증
#         user = authenticate(
#             student_number=request.data.get("student_number"), password=request.data.get("password")
#         )
#         # 이미 회원가입 된 유저일 때
#         if user is not None:
#             serializer = UserSerializer(user)
#             # jwt 토큰 접근
#             token = TokenObtainPairSerializer.get_token(user)
#             refresh_token = str(token)
#             access_token = str(token.access_token)
#             res = Response(
#                 {
#                     "user": serializer.data,
#                     "message": "login success",
#                     "token": {
#                         "access": access_token,
#                         "refresh": refresh_token,
#                     },
#                 },
#                 status=status.HTTP_200_OK,
#             )
#             # jwt 토큰 => 쿠키에 저장
#             res.set_cookie("access", access_token, httponly=True)
#             res.set_cookie("refresh", refresh_token, httponly=True)
#             return res
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#     # 로그아웃
#     def delete(self, request):
#         # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
#         response = Response({
#             "message": "Logout success"
#             }, status=status.HTTP_202_ACCEPTED)
#         response.delete_cookie("access")
#         response.delete_cookie("refresh")
#         return response




# class LoginView(generics.GenericAPIView):
#     serializer_class = LoginSerializer
    
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         token = serializer.validated_data # validate()의 리턴값인 token을 받아온다.
#         return Response({"token": token.key}, status=status.HTTP_200_OK)
    
class ProfileUpdateview(generics.RetrieveUpdateAPIView): # 제네릭 뷰로 put , post 등 만 받을 수 있게 할 수 있음
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
# 나중에 url로 바로 들어오면 볼 수 있는데 그것도 수정할려면 middleware로 고치거나 , response를 하나하나 다 고쳐야됨 
    
class ProfileView(generics.ListAPIView): # 자신의 프로필 보는거 ,post 모델 보냄
    queryset = Profile.objects.all()
    serializer_class = ProfileViewSerializer 
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
 # 요청한 유저가 다른 유저이면 수정은 안되고 read만 됨 
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] # 인증된 사용자에게만 허용 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) # 객체를 생성하고 author 필드에 request.user 저장하기 
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly,CustomReadOnly] # custom 은 자신만 수정할 수 있고 다른 사람은 read만 가능 
   # permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    # 인증된 사용자에게는 모든 작업 허용 , 인증되지 않는 사람에게는 읽기만 허용 
class CommentViewSet(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly,CustomReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def signup(request):
#     email = request.data.get('email')
#     password = request.data.get('password')
#     name = request.data.get('name')
#     student_number = request.data.get('student_number')
#     join_year = request.data.get('join_year')
#     major = request.data.get('major')
#     phone_number = request.data.get('phone_number')

#     serializer = UserSerializer(data=request.data)
#     serializer.email = email
#     serializer.name = name
#     serializer.name = student_number
#     serializer.name = join_year
#     serializer.name = major
#     serializer.name = phone_number
#     if serializer.is_valid(raise_exception=True):
#         user = serializer.save()
#         user.set_password(password)
#         user.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def signup(request):
#     email = request.data.get('email')
#     password = request.data.get('password')
#     name = request.data.get('name')
#     student_number = request.data.get('student_number')
#     join_year = request.data.get('join_year')
#     major = request.data.get('major')
#     phone_number = request.data.get('phone_number')
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid(raise_exception=True):
#         user = serializer.save(email=email, name=name, student_number=student_number, join_year=join_year, major=major, phone_number=phone_number)
#         user.set_password(password)
#         user.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def login(request):
#     student_number = request.data.get('student_number')
#     password = request.data.get('password')
#     user = authenticate(student_number=student_number, password=password)
#     if user is None:
#         return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
#     refresh = RefreshToken.for_user(user)
#     update_last_login(None, user)
#     return Response({'refresh_token': str(refresh),
#                      'access_token': str(refresh.access_token), }, status=status.HTTP_200_OK)
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def signup(request):
#     email = request.data.get('email')
#     password = request.data.get('password')
#     name = request.data.get('name')
#     serializer = UserSerializer(data=request.data)
#     serializer.email = email
#     serializer.name = name
#     if serializer.is_valid(raise_exception=True):
#         user = serializer.save()
#         user.set_password(password)
#         user.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# view 3개 필요한거 아녀? list , create , 수정,삭제 
