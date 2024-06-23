from django.urls import path,include
from .views import *
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView ,TokenVerifyView



urlpatterns = [
    path('',views.index, name='index'),
    path('signup/', RegisterView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    
    # user
    path('profile/<int:pk>/', UserListView.as_view(), name='profile'), # 유저 개인 페이지 
    path('profile/update/',UserInformUpdateView.as_view(), name='profile-update') ,# 유저 개인정보 업데이트 페이지 

    # post 
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/comments/', CommentViewSet.as_view(), name='post-comment'),

    # 출석체크
    path('create-code/', CodeCreateView.as_view(), name='create-code'),
    path('check-attendance/', AttandanceCheckView.as_view(), name='check-attendance'),
    # token
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 프론트에서 access 끝나면 여기로 요청 
    path('image/',views.Image.as_view(),name='image'),
    # 추가로 로직을 만들필요 없음 이미 내장되어 있음 
]
