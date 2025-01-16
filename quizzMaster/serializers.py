from rest_framework import serializers
from .models import Choice, Exam, Question, Subject, ExamSchedule, ExamQuestion, CorrectAnswer, User, Submission, Role, UserSubject
from rest_framework.exceptions import ValidationError
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

    def validate(self, attrs):
        name = attrs.get('name')
        if Subject.objects.filter(name=name).exists():
            raise ValidationError({
                "name": "Subject with this name already exists."})

        if len(name) < 3 or len(name) > 100:
            raise ValidationError({"name": "Subject name must be between 3 and 100 characters."})
        return attrs

class ExamScheduleSerializer(serializers.ModelSerializer):
    exam = serializers.PrimaryKeyRelatedField(queryset=Exam.objects.all())

    class Meta:
        model = ExamSchedule
        fields = '__all__'

    def validate(self, attrs):
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')
        exam = attrs.get('exam')

        if start_at > end_at:
            raise serializers.ValidationError({
                "end_at": "End time must be after start time."
            })

        if ExamSchedule.objects.filter( exam=exam, start_at=start_at, end_at=end_at).exists():
            raise serializers.ValidationError("The exam schedule conflicts with another schedule.")

        return attrs

    def validate_start_at(self, value):
        from datetime import datetime
        if value < datetime.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return value

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

