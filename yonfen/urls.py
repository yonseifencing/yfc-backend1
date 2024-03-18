from django.urls import path
from .views import RegisterView,LoginView,ProfileView

urlpatterns = [
    # 인덱스 뷰가 없어서 그럼 
    path('', RegisterView.as_view()), # 나중에 register/ 해줘야 함 
    path('login/', LoginView.as_view()),
    path('profile/<int:pk>/', ProfileView.as_view()),


]
