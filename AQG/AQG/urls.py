"""
URL configuration for AQG project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from Generator import views, static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  
    path('summary/', views.summary, name='summary'),
    path('generate_questions/', views.generate_questions, name='generate_questions'),
    path('input_text/', views.input_text, name='input_text'),
    path('upload/', views.upload_file, name='upload_file'),
    path('process_selected_chapter/', views.process_selected_chapter, name='process_selected_chapter'),
    path('calculate_accuracy/', views.calculate_accuracy, name='calculate_accuracy'),
]
