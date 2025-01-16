import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from quizzMaster.models import Role, Subject, User, UserSubject, Question, Exam, ExamSchedule, Choice, CorrectAnswer, ExamQuestion

class Command(BaseCommand):
    help = 'Create sample data for the application'

    def handle(self, *args, **kwargs):

        # ExamQuestion.objects.all().delete()
        # CorrectAnswer.objects.all().delete()
        # ExamSchedule.objects.all().delete()
        # Exam.objects.all().delete()
        # Question.objects.all().delete()
        # Choice.objects.all().delete()
        # User.objects.all().delete()
        # UserSubject.objects.all().delete()
        # Role.objects.all().delete()
        # Subject.objects.all().delete()

        # Tạo các role
        candidate_role = Role.objects.create(name='Candidate', description='Role to take exams')
        exam_manager_role = Role.objects.create(name='Exam Manager', description='Role to manage exams')
        question_manager_role = Role.objects.create(name='Question Manager', description='Role to manage questions')

        # Tạo subject
        vuejs_subject = Subject.objects.create(name='Vue.js')

        # Tạo users
        candidate_user = User.objects.create(username='candidate_user', email='candidate@example.com', password='candidatepass123', role=candidate_role)
        exam_manager_user = User.objects.create(username='exam_manager', email='manager@example.com', password='managerpass123', role=exam_manager_role)
        question_manager_user = User.objects.create(username='question_manager', email='questionmanager@example.com', password='questionmanagerpass123', role=question_manager_role)

        # Gán subject cho users
        UserSubject.objects.create(user=candidate_user, subject=vuejs_subject)
        UserSubject.objects.create(user=exam_manager_user, subject=vuejs_subject)
        UserSubject.objects.create(user=question_manager_user, subject=vuejs_subject)

        # Tạo câu hỏi
        question1 = Question.objects.create(question_text='What is Vue.js?', subject=vuejs_subject)
        question2 = Question.objects.create(question_text='How does the v-model directive work in Vue.js?', subject=vuejs_subject)

        # Tạo kỳ thi
        exam1 = Exam.objects.create(exam_code='EXAM_VUEJS_001', duration=60, num_questions=2, subject=vuejs_subject)

        # Chuyển đổi thời gian thành timezone-aware datetime
        start_time = timezone.make_aware(datetime.datetime(2025, 2, 1, 10, 0, 0))
        end_time = timezone.make_aware(datetime.datetime(2025, 2, 1, 11, 0, 0))

        # Tạo lịch thi
        exam_schedule1 = ExamSchedule.objects.create(start_time=start_time, end_time=end_time, exam=exam1)

        # Tạo lựa chọn cho câu hỏi
        choice1 = Choice.objects.create(question=question1, choice_text='A JavaScript framework')
        choice2 = Choice.objects.create(question=question1, choice_text='A database')

        # Tạo câu trả lời đúng
        correct_answer1 = CorrectAnswer.objects.create(question=question1, choice=choice1)

        # Liên kết các câu hỏi với kỳ thi
        exam_question1 = ExamQuestion.objects.create(exam=exam1, question=question1)
        exam_question2 = ExamQuestion.objects.create(exam=exam1, question=question2)

        self.stdout.write(self.style.SUCCESS('Sample data created successfully for Candidate, Exam Manager, and Question Manager roles!'))