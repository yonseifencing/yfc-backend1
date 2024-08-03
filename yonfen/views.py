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
# view 의 역할 http 요청 처리 ,데이터베이스 상호작용

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
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticatedOrReadOnly]

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
   # authentication_classes = [JWTAuthentication]
   #  permission_classes = [IsAuthenticatedOrReadOnly,CustomReadOnly]


class PostListView(generics.ListAPIView): # 게시물 조회 페이지 
    queryset = Post.objects.all()
    serializer_class = PostListSerializer


class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
   # authentication_classes = [JWTAuthentication]
   #  permission_classes = [IsAuthenticatedOrReadOnly]

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
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticatedOrReadOnly]

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



# class CodeCreateView(generics.CreateAPIView):
#     queryset = Code.objects.all()
#     serializer_class = CodeSerializer
#     # permission_classes = [IsAdminUser]

#     def create(self, request, *args, **kwargs):
#         code = ''.join(random.choices(string.digits, k=4))
#         while Code.objects.filter(code=code).exists():
#             code = ''.join(random.choices(string.digits, k=4))
#         Code.objects.create(code=code)
#         return Response({'code': code}, status=status.HTTP_201_CREATED)

# class AttandanceCheckView(generics.CreateAPIView):
#     queryset = Attandance.objects.all()
#     serializer_class = AttandanceSerializer
#     # permission_classes = [IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         code = request.data.get('code')
#         try:
#             code_obj = Code.objects.get(code=code, valid_until__gte=timezone.now())
#             attandance, created = Attandance.objects.get_or_create(user=request.user)
#             attandance.check_count += 1  # 필드 이름을 check에서 check_count로 변경
#             attandance.save()
#             return Response({'message': '확인되었습니다'}, status=status.HTTP_200_OK)
#         except Code.DoesNotExist:
#             return Response({'error': '다시 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
# view 3개 필요한거 아녀? list , create , 수정,삭제 

class Image(APIView):
    def post(self,request, format=None):
        serializers = PhotoSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    

User = get_user_model()
# 출석체크 코드 생성 
class CodeCreateView(generics.CreateAPIView): # createAPIView 는 클라이언트가 request 해서 post 하면 그걸 어떻게 그 객체를 어떻게 생성할지 create 메소드로 한다 
    queryset = Code.objects.all()
    serializer_class = CodeSerializer
    # permission_classes = [IsAdminUser]
    # args,kwargs 함수에서 여러 값을 받게 해주는거 args > 튜플, kwagrs > 딕셔너리 
    def create(self, request, *args, **kwargs): # creatr 오버라이드 
        code = ''.join(random.choices(string.digits, k=4))
        while Code.objects.filter(code=code).exists(): # 중복된 번호가 있는지 있으면 새로 만들기 
            code = ''.join(random.choices(string.digits, k=4))
        Code.objects.create(code=code, valid_until=timezone.now() + timezone.timedelta(hours=2)) # 허용시간 2시간 
        return Response({'code': code}, status=status.HTTP_201_CREATED) # http 응답을 반환하는 코드 

# class AttendanceCheckView(generics.CreateAPIView): # 유저가 인증하느 
#     queryset = UserAttendance.objects.all()
#     serializer_class = UserAttendanceSerializer
#     # permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs): 
#         code_input = request.data.get('code')
#         try:
#             code_obj = Code.objects.get(code=code_input)  # 인풋 데이터를 가지고 데이터베이스에 query 날리기 
#             if code_obj.valid_until < timezone.now(): 
#                 return Response({'error': '유효 기간이 끝났습니다'}, status=status.HTTP_400_BAD_REQUEST)

#             user_attendance, created = UserAttendance.objects.get_or_create(
#                 user=request.user,
#                 code=code_obj,
#                 defaults={'created_at': timezone.now()}
#             )
#             # 조회 및 인스턴스 생성 , 첫번째 값에는 조건에 맞는 객체가 있다면 반화 , 없다면 새로운 객체를 생성하고 그 객체 반환 , 두번째 변수 객체가 새로 생성되면 true , 이미 존재하면 false 
#             if created or user_attendance.is_correct == 0: # 둘 중에 하나라도 true 면 됨 
#                 user_attendance.check_code(code_input)
#                 user_attendance.save()
#                 message = '확인되었습니다' if user_attendance.is_correct == 1 else '다시 입력해주세요' # 삼항 연산자 ture 면 확인되었습니다 flase 면 다시 입력해주세요 가 message 에 담김 
#                 return Response({'message': message}, status=status.HTTP_200_OK)
#             else:
#                 return Response({'message': '이미 출석하셨습니다'}, status=status.HTTP_200_OK)
#         except Code.DoesNotExist:
#             return Response({'error': '다시 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)

class UserAttendanceCheckView(generics.CreateAPIView):
    queryset = UserAttendance.objects.all()
    serializer_class = UserAttendanceSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        code_input = request.data.get('code_input') # 시리얼라이즈에 있는 code_input 가지고 오기 
        if not code_input:
            return Response({'error': 'code_input이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            code_obj = Code.objects.get(code=code_input)
            if code_obj.valid_until < timezone.now(): # valid_until 에 현재 시간 + 두시간 해 놔서 그 값 보다 높으면 유효 기간이 끝났다고 나오기 
                return Response({'error': '유효 기간이 끝났습니다'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_attendance, created = UserAttendance.objects.get_or_create( 
                user=user,
                code=code_obj,
                defaults={'created_at': timezone.now()}
            )
            if not created and user_attendance.is_correct == 1:
                return Response({'message': '이미 출석하셨습니다'}, status=status.HTTP_200_OK)
            
            user_attendance.check_code(code_input)
            user_attendance.save()
            message = '확인되었습니다' if user_attendance.is_correct == 1 else '다시 입력해주세요'
            return Response({'message': message}, status=status.HTTP_200_OK)
        except Code.DoesNotExist:
            return Response({'error': '다시 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
        

class RankingListView(generics.ListAPIView): # 랭킹 보여주는 정렬 해서 
    queryset = Ranking.objects.all().order_by('-total_score')
    serializer_class = RankingSerializer

class RankingUpdateView(generics.GenericAPIView): # 랭킹 업데이트 수정하는 페이지 
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
  #   permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        rankings = request.data.get('rankings', []) # 프런트에서 보낸 데이터 가지고 오고 없으면 빈르스트 반환 
        
        # rankings 리스트의 길이가 5가 아니면 예외를 발생시킵니다.
        if len(rankings) != 5:
            raise ValidationError('5명의 사용자를 선택해야 합니다.')

        # rankings 리스트에 있는 각 항목에 대해 반복문을 실행합니다.
        for rank_info in rankings:
            user_id = rank_info.get('user_id')  # 현재 항목에서 'user_id'를 가져옵니다.
            rank = rank_info.get('rank')  # 현재 항목에서 'rank'를 가져옵니다.
            
            # user_id 또는 rank가 없으면 예외를 발생시킵니다.
            if not user_id or not rank:
                raise ValidationError('모든 항목에 user_id와 rank가 필요합니다.')
            
            try:
                # user_id에 해당하는 사용자를 데이터베이스에서 가져옵니다.
                user = User.objects.get(pk=user_id)
                # 해당 사용자의 랭킹 점수를 업데이트합니다.
                user.ranking.update_rank_score(rank) # 모델에 있는 함수 
            except User.DoesNotExist:
                # user_id에 해당하는 사용자가 존재하지 않으면 예외를 발생시킵니다.
                raise ValidationError(f'User with id {user_id} does not exist.')
        
        # 모든 작업이 성공적으로 완료되면 응답을 반환합니다.
        return Response({'message': '선택된 사용자들에게 랭킹 점수 부여 완료'}, status=status.HTTP_200_OK)