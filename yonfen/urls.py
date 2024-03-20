from django.urls import path
from .views import RegisterView,LoginView,ProfileView,ProfileUpdateview,PostListView,PostCreateView,PostDetailView


urlpatterns = [
    # 인덱스 뷰가 없어서 그럼 
    path('', RegisterView.as_view()), # 나중에 register/ 해줘야 함 
    path('login/', LoginView.as_view(), name='login'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/update/',ProfileUpdateview.as_view(), name='profile-update'),

    # post 
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),


]
