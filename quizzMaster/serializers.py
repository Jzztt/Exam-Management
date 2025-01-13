from rest_framework import serializers
from .models import Choice, Exam, Question, Subject, ExamSchedule, ExamQuestion, CorrectAnswer, User, Submission, Role, UserSubject

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'exam_code', 'duration', 'num_questions', 'subject', 'subject_name']

class ExamQuestionSerializer(serializers.ModelSerializer):
    exam = ExamSerializer()
    question = QuestionSerializer()

    class Meta:
        model = ExamQuestion
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ExamScheduleSerializer(serializers.ModelSerializer):
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all())

    class Meta:
        model = ExamSchedule
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'role_name']
        extra_kwargs = {'password': {'write_only': True}}

class SubmissionSerializer(serializers.ModelSerializer):
    exam = ExamSerializer()
    user = UserSerializer()

    class Meta:
        model = Submission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class UserSubjectSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subject = SubjectSerializer()

    class Meta:
        model = UserSubject
        fields = '__all__'

