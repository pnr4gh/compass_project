from django.urls import path
from . import views



urlpatterns = [

      # Company views
    path('companies/', views.company_list, name='company_list'),
    path('companies/add/', views.add_company, name='add_company'),
    

    # Job role views
    path('job-roles/', views.job_role_view, name='job_role_list'),
    path('company/<int:company_id>/job-roles/', views.job_role_view, name='company_job_roles'),
    path('company/update/', views.update_company, name='update_company'),
    path('add-job-role/', views.add_job_role, name='add_job_role'),


     # Interview round views
    path('interview-rounds/<int:job_role_id>/', views.interview_rounds, name='interview_rounds'),
    path('rounds/add/', views.add_interview_round, name='add_interview_round'),
        # Skill management URLs
        path('rounds/skill/add/', views.add_skill_to_round, name='add_skill_to_round'),
        path('rounds/skill/remove/', views.remove_skill_from_round, name='remove_skill_from_round'),
        #Topics API endpoints
        path('api/round-skill/<int:round_skill_id>/topics/', views.get_topics_for_skill, name='get_topics_for_skill'),
        path('api/round-skill/add-topic/', views.add_topic_to_skill, name='add_topic_to_skill'),
        path('api/round-skill/remove-topic/', views.remove_topic_from_skill, name='remove_topic_from_skill'),
        path('api/round-skill/save-topics/', views.save_topics, name='save_topics'),
        path('api/all-topics/', views.get_all_topics, name='all_topics'),
        path('api/all-skills/', views.get_all_skills, name='all_skills'),
  

  #company datavisualization
   path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
   path('api/skill-company-data/', views.skill_company_data, name='skill_company_data'),
   path('api/salary-band-data/', views.salary_band_data, name='salary_band_data'),
]