from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    
    RegisterAPIView,
    UserManagementView,
    UserListView,
    QuizzCreateView,
    QuizTakingView,
    QuizResultView,
    QuizListingView,
    QuizFilterView,
    QuizAnalyticsView,
    UserProfileView
)

urlpatterns = [
   
    #user
    path('registeruser/', RegisterAPIView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(' ', UserProfileView.as_view(), name='user-profile'),

    
    #admin
    path('users/', UserListView.as_view(), name='userlist'),
    path('users/<int:pk>/', UserManagementView.as_view(), name='usermanagement'),

    #Quiz
    path('quiz/creat/', QuizzCreateView.as_view(), name='quizcreate'),
    path('quiz/<int:pk>/', QuizTakingView.as_view(), name='quiztaking'),
    path('quiz/result/', QuizResultView.as_view(), name='quizresult'),
    path('quiz/list/', QuizListingView.as_view(), name='quizlist'),
    path('quiz/filter/', QuizFilterView.as_view(), name='quizfilter'),
    path('quiz/analytics/', QuizAnalyticsView.as_view(), name='quizanalytics'),
    

]
