from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role.name == 'Candidate'

class IsExamAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role.name == 'Exam Administrator'

class IsQuestionManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role.name == 'Question Manager'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role.name == 'Admin'
