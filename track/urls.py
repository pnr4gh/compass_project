from django.urls import path, include
from . import views
from .core import user as uviews
from .core import profile as pviews
from .core import leaderboard as lview
from django.contrib.auth import views as auth_views
from .core.course import course_list_view, create_course, create_assignment,edit_assignment, edit_course, course_detail, load_leaderboard,student_progress, problem_list, add_problem_to_assignment, remove_problem_from_assignment
from .import discussion as dviews

urlpatterns = [
    path('contest/<str:dmoj_key>/', views.contest_redirect, name='contest_redirect'),
    path('contest-stats/', views.contest_and_solved_stats, name='contest_and_solved_stats'),
    #User Management Urls
    path('signup/',views.signup, name='signup'),
    path('', auth_views.LoginView.as_view(template_name='decodeschool/login.html'), name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('password/', views.change_password, name='change_password'),
    path('forgot-password/', uviews.forgot_password, name='forgot_password'),
    path('upload_students',views.import_from_excel,name="upload_students"),
    path('users/', uviews.list_users, name='list_users'),
    path('users/create/', uviews.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', uviews.edit_user, name='edit_user'),
    path('users/reset-password/<int:user_id>/', uviews.reset_password, name='reset_password'),
    path('users/assign_group/',uviews.assign_group, name='assign_group'),
    path('profile/', pviews.user_profile, name='user_profile'),
    path('add_user_handle/', pviews.add_user_handle, name='add_user_handle'),
    path('remove_user_handle/', pviews.remove_user_handle, name='remove_user_handle'),

    #Landing Page and Portal Connect Urls
    path("api/contests/", views.ContestAPI.as_view(), name="contests-api"),
    path('api/contest-result/', views.ContestResultView.as_view(), name='contest-result'),
    path('dashboard/contest-stats/', views.contest_stats, name='contest_stats'),
    # path('dashboard/conteststats', views.admin_contest_stats, name='admin_contest_stats'),
    path('home/',views.home,name='home'),
    path('myadmin',views.myadmin,name="myadmin"),
    path('dashboard',views.view_dashboard,name='dashboard'),
    path('get_portal_problems/<str:portal_name>',views.get_portal_problems,name='get_portal_problems'),
    path('update_solved/<str:uh>/<str:platform>',views.update_solved,name='update_solved'),
    path('leaderboard', lview.leaderboard,name='leaderboard'),
    #Course and Assignmenr Urls
    path('courses/', course_list_view, name='course_list'),
    path('course/create/', create_course, name='create_course'),
    path('course/<int:course_id>/edit/', edit_course, name='edit_course'),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('course/<int:course_id>/load_leaderboard/', load_leaderboard, name='load_leaderboard'),
    path('student_progress/<int:id>/',student_progress,name='student_progress'),
    path('course/<int:course_id>/add_assignment/', create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/edit/', edit_assignment, name='edit_assignment'),
    path('assignment/<int:assignment_id>/problems/', problem_list, name='problem_list'),
    path('add_to_assignment/', add_problem_to_assignment, name='add_to_assignment'),
    path('remove_from_assignment/',remove_problem_from_assignment, name='remove_from_assignment'),

    #Discussion Urls
    path('course/<int:course_id>/', dviews.discussion_view, name='course_detail'),
    path('course/<int:course_id>/course_discussion/<int:discussion_id>/', dviews.discussion_detail_view, name='course_discussion'),
    path('course/<int:course_id>/discussion_results/<int:discussion_id>/', dviews.discussion_results, name='discussion_results'),
    path('get_user_solved_problems/<int:user_id>/', dviews.get_solved_problems, name='get_user_solved_problems'),
    path('discussions/<int:course_id>/', dviews.add_or_show_discussion, name='discussions_view'),


]
