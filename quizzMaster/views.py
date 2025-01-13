from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Choice, Exam, Question, Subject, ExamSchedule,CorrectAnswer, ExamQuestion, User, Submission, Role, UserSubject
from .serializers import ChoiceSerializer, ExamSerializer, QuestionSerializer, SubjectSerializer, ExamScheduleSerializer, ExamQuestionSerializer, UserSerializer, SubmissionSerializer, RoleSerializer, UserSubjectSerializer
from .permissions import IsStudent, IsAdmin, IsExamAdministrator, IsQuestionManager
from docx import Document


class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Protected data"}, status=status.HTTP_200_OK)
class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsQuestionManager | IsAdmin]

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    # queryset = Exam.objects.select_related('subject').all()
    # serializer_class = ExamSerializer

    # def get_queryset(self):
    #     subject_id = self.request.query_params.get('subject_id')
    #     if subject_id:
    #         return self.queryset.filter(subject_id=subject_id)
    #     return self.queryset
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsExamAdministrator]

class ExamQuestionViewSet(viewsets.ModelViewSet):
    queryset = ExamQuestion.objects.all()
    serializer_class = ExamQuestionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsExamAdministrator | IsQuestionManager]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated | IsAdmin | IsQuestionManager]

class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsExamAdministrator]

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

class UserSubjectViewSet(viewsets.ModelViewSet):
    queryset = UserSubject.objects.all()
    serializer_class = UserSubjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

class ImportDocxView(APIView):
    def save_to_database( self, questions, exam_id, subject_id):
        for question in questions:
            question_text = question['question']
            choices = question['choices']
            correct_choice = question.get('correct_choice')

            subject = Subject.objects.get(id=subject_id)
            question = Question.objects.create(question_text=question_text, subject=subject)
            correct_choice_obj = None
            for choice_data in choices:
                choice_text = choice_data["text"]
                choice = Choice.objects.create(question=question, choice_text=choice_text)
                if choice_data["option"] == correct_choice:
                    correct_choice_obj = choice
            if correct_choice_obj:
                CorrectAnswer.objects.create(question=question, choice=correct_choice_obj)
            exam = Exam.objects.get(id=exam_id)
            ExamQuestion.objects.create(exam=exam, question=question)

    def post(self, request, *args, **kwargs):
        exam_id = request.data.get('exam_id')
        subject_id = request.data.get('subject_id')
        docx_file = request.FILES.get('file')
        questions = []
        current_question = None
        current_choices = []
        correct_choice = None
        if not docx_file:
            return Response({"error": "No file provided"}, status=400)
        try:
            document = Document(docx_file)
            for paragraph in document.paragraphs:
                text = paragraph.text.strip()
                if text.startswith("Câu"):
                    if current_question and current_choices:
                        questions.append({
                            "question": current_question,
                            "choices": current_choices
                        })
                    question_text = text.split(":")[1].strip()
                    current_question = question_text
                    current_choices = []
                elif text.startswith(("A.", "B.", "C.", "D.")):
                    option,choice_text = text.split(".", 1)
                    current_choices.append({
                        "option": option.strip(),
                        "text": choice_text.strip()
                    })
                elif text.startswith("Đáp án"):
                    correct_choice = text.split(":")[1].strip()
                    if current_choices and current_question:
                        questions.append({
                            "question": current_question,
                            "choices": current_choices,
                            "correct_choice": correct_choice
                        })
                        current_question = None
                        current_choices = []
                        correct_choice = None
            if current_question and current_choices:
                questions.append({
                    "question": current_question,
                    "choices": current_choices
                })
            self.save_to_database(questions, exam_id, subject_id)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        else:
            return Response({"message": "File imported successfully"}, status=200)



class AuthViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
       username = request.data.get('username')
       email = request.data.get('email')
       password = request.data.get('password')

       try:
        role = Role.objects.get(name='Candidate')
       except Role.DoesNotExist:
        #    logger.error('Role does not exist')
           return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

       if User.objects.filter(username=username).exists():
            return Response({'error': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
       if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

       user = User.objects.create(username=username, email=email, password=make_password(password), role=role)
       user.save()
       return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


