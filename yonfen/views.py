# users/views.py
from django.contrib.auth.models import User
from rest_framework import generics, status ,permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer,LoginSerializer,ProfileUpdateSerializer,ProfileViewSerializer,PostSerializer
from .models import Profile,Post
from rest_framework.permissions import IsAuthenticated

from .permissions import CustomReadOnly
from knox.auth import TokenAuthentication

# view에서 설정하는 것은 그 페이지안에서 활용될 수 있는 기능들을 만드는 곳 
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data # validate()의 리턴값인 token을 받아온다.
        return Response({"token": token.key}, status=status.HTTP_200_OK)
    
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
    serializer_class = PostSerializer

class PostCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated] # 인증된 사용자에게만 허용 

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 
    # 인증된 사용자에게는 모든 작업 허용 , 인증되지 않는 사람에게는 읽기만 허용 