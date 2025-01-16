from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'choices', views.ChoiceViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'exam-questions', views.ExamQuestionViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'exam-schedules', views.ExamScheduleViewSet)
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'submissions', views.SubmissionViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'user-subjects', views.UserSubjectViewSet)
router.register(r'auth', views.AuthViewSet, basename='auth')


urlpatterns = [
    path('', include(router.urls)),
    path('import-docx/', views.ImportDocxView.as_view(), name='import-docx'),
    path('exam-import-docx/', views.ImportExamView.as_view(), name='exam-import-docx'),
    # path('exams/<int:exam_id>/questions/', views.ExamQuestionsView.as_view(), name='exam-questions'),

]
