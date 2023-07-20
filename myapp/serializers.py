from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User,Quizzz, Question, Choice, QuizResult
from rest_framework.exceptions import ValidationError






class RegisterSerializer(serializers.ModelSerializer):
    #is_admin = serializers.BooleanField(required=False)
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, data):
        username = data['username']
        email = data['email']

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exists.')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists.')

        return data
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    #def update(self, instance, validated_data):
    #    instance.username = validated_data.get('username', instance.username)
    #    instance.email = validated_data.get('email', instance.email)
    #    instance.first_name = validated_data.get('first_name', instance.first_name)
    #    instance.last_name = validated_data.get('last_name', instance.last_name)

     #   password = validated_data.get('password')
      #  if password:
       #     instance.set_password(password)

        #instance.save()
        #return instance
  

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'text', 'choices']

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = '__all__'



class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quizzz
        fields = ['id', 'title', 'topic','difficulty_level', 'created_at', 'questions']
        
class UserProfileSerializer(serializers.ModelSerializer):
    quizzes_created = QuizSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'quizzes_created']