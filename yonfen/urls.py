from django.urls import path,include
from .views import LoginView,RegisterView,ProfileView,ProfileUpdateview,PostListView,PostCreateView,PostDetailView
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView ,TokenVerifyView



urlpatterns = [
    # 인덱스 뷰가 없어서 그럼 
    path('',views.index, name='index'),
    path('signup/', RegisterView.as_view()), # 나중에 register/ 해줘야 함 
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/update/',ProfileUpdateview.as_view(), name='profile-update'),

    # post 
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    
    # token
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # 프론트에서 access 끝나면 여기로 요청 

]
