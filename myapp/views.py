from django.shortcuts import render
#from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import generics,permissions
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , IsAdminUser,AllowAny
from .serializers import RegisterSerializer, QuizSerializer,  QuestionSerializer, ChoiceSerializer,QuizResultSerializer,UserProfileSerializer
from .models import User,Quizzz, Question, Choice, QuizResult
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied,ValidationError
from django_filters.rest_framework import DjangoFilterBackend 
from django.db.models import Avg, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Quizzz, QuizResult, Question
from rest_framework.generics import CreateAPIView
    
   
    


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    Permission_class=[AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            return Response({'status': status.HTTP_201_CREATED, 
                             #'payload': response.data,
                              'message': 'User created.'})
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'errors': response.data})



class UserListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    serializer_class = RegisterSerializer
    def get_queryset(self):
        return User.objects.filter(is_staff=False)
    def get(self, request):
        users = self.get_queryset()
        serializer = RegisterSerializer(users, many=True)
        return Response(serializer.data)
    
   

class UserManagementView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    Permission_class=[AllowAny]
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.is_staff and request.user != user:
            raise PermissionDenied("You do not have permission to edit this user.")
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'status': 200, 'payload': serializer.data})
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.is_staff and request.user != user:
            raise PermissionDenied("You do not have permission to delete this user.")
        user.delete()
        return Response({"message": "User deleted successfully"})
    




class QuizzCreateView(CreateAPIView):
    serializer_class = QuizSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set the creator of the quiz as the currently authenticated user
            serializer.validated_data['creator'] = self.request.user
            quiz = serializer.save()
            questions_data = request.data.get('questions', [])
            for question_data in questions_data:
                question = Question.objects.create(quiz=quiz, text=question_data['text'])
                choices_data = question_data.get('choices', [])
                for choice_data in choices_data:
                    Choice.objects.create(question=question, text=choice_data['text'], is_correct=choice_data['is_correct'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizTakingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            quiz = Quizzz.objects.get(pk=pk)
            serializer = QuizSerializer(quiz)
            return Response(serializer.data)
        except Quizzz.DoesNotExist:
            raise ValidationError("Quiz not found.")

    def post(self, request, pk):
        try:
            quiz = Quizzz.objects.get(pk=pk)
            questions = quiz.questions.all()
            total_questions = questions.count()
            correct_answers = 0
            for question in questions:
                question_id = question.id
                selected_choice_id = request.data.get(str(question_id), None)
                if selected_choice_id is not None:
                    selected_choice = Choice.objects.get(pk=selected_choice_id)
                    if selected_choice.is_correct:
                        correct_answers += 1
            score = (correct_answers / total_questions) * 100
            QuizResult.objects.create(user=request.user, quiz=quiz, score=score)
            quiz_serializer = QuizSerializer(quiz)
            return Response({"quiz": quiz_serializer.data, "score": score})
        except Quizzz.DoesNotExist:
            return Response({"error": "Quiz not found."})       

class QuizResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        quiz_results = QuizResult.objects.filter(user=user)
        serializer = QuizResultSerializer(quiz_results, many=True)
        return Response(serializer.data)  
          
class QuizListingView(generics.ListAPIView):
    queryset = Quizzz.objects.all()
    serializer_class = QuizSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['topic', 'difficulty_level', 'created_at']

class QuizFilterView(generics.ListAPIView):
    queryset = Quizzz.objects.all()
    serializer_class = QuizSerializer
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        topic = self.request.query_params.get('topic')
        difficulty_level = self.request.query_params.get('difficulty_level')
        created_date = self.request.query_params.get('created_date')
        queryset = Quizzz.objects.all()
        if topic:
            queryset = queryset.filter(topic=topic)
        if difficulty_level:
            queryset = queryset.filter(difficulty_level=difficulty_level)
        if created_date:
            queryset = queryset.filter(created_at=created_date)
        return queryset


class QuizAnalyticsView(APIView):
    def get(self, request):
        
        total_quizzes = Quizzz.objects.count()
        total_quiz_takers = QuizResult.objects.values('user').distinct().count()
        average_quiz_score = QuizResult.objects.aggregate(Avg('score'))['score__avg']
        quiz_scores = QuizResult.objects.values('quiz').annotate(average_score=Avg('score'))
        highest_score = max(quiz_scores, key=lambda x: x['average_score'])['average_score']
        lowest_score = min(quiz_scores, key=lambda x: x['average_score'])['average_score']
        most_answered_questions = Question.objects.annotate(num_times_answered=Count('choices')).order_by('-num_times_answered')[:2]
        least_answered_questions = Question.objects.annotate(num_times_answered=Count('choices')).order_by('num_times_answered')[:2]
        passing_users_count = QuizResult.objects.filter(score__gte=40).values('user').distinct().count()
        passing_percentage = (passing_users_count / total_quiz_takers) * 100

        question_scores = QuizResult.objects.values('quiz__questions').annotate(average_score=Avg('score'))
        
        question_avg_scores = {}
        for question_score in question_scores:
            question_id = question_score['quiz__questions']
            avg_score = question_score['average_score']
            question_avg_scores[question_id] = avg_score

        quiz_overview = {
            "no_of_quizzes": total_quizzes,
            "no_of_quiz_takers": total_quiz_takers,
            "average_quiz_score": average_quiz_score,
        }
        performance_metrics = {
            "average_score": question_avg_scores,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
        }
        most_answered_question_texts = [question.text for question in most_answered_questions]
        least_answered_question_texts = [question.text for question in least_answered_questions]

        data = {
            "quiz_overview": quiz_overview,
            "performance_metrics": performance_metrics,
            "most_answered_questions": most_answered_question_texts,
            "least_answered_questions": least_answered_question_texts,
            "passing_percentage": passing_percentage,
        }

        return Response(data)
  
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_serializer = UserProfileSerializer(user)
        quizzes_created = Quizzz.objects.filter(creator=user)
        quiz_serializer = QuizSerializer(quizzes_created, many=True)
        profile_data = {
            "user_info": user_serializer.data,
            "quizzes_created": quiz_serializer.data,
        }

        return Response(profile_data, status=status.HTTP_200_OK)