from django.urls import path, include
from rest_framework import routers

from vacancies import views
from vacancies.test_views import StoreView

simple_router = routers.SimpleRouter()
simple_router.register('lookup_queries', StoreView)

urlpatterns = [
    path('', views.VacancyListView.as_view()),
    path('<int:pk>/', views.VacancyDetailView.as_view()),
    path('create/', views.VacancyCreateView.as_view()),
    path('<int:pk>/update/', views.VacancyUpdateView.as_view()),
    path('<int:pk>/delete/', views.VacancyDeleteView.as_view()),
    path('by_user/', views.user_vacancies),
    # path('slug/<str:slug>/', views.VacancyDetailView.as_view()),
    path('like/', views.VacancyLikeView.as_view()),
    path('', include(simple_router.urls)),
]
