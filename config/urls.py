from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quiz/', include('quiz.urls')),
    path('question/', include('question.urls')),
    path('attempt/', include('quiz_attempt.urls')),
]
