
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.accolade_list, name='accolade_list'),
    path('post/', views.create_accolade, name='create_accolade'),
     path('like/<int:accolade_id>/', views.like_accolade, name='like_accolade'),
    path('organization/add/', views.add_organization, name='add_organization'),
     path('add-outcome/', views.add_outcome, name='add_outcome'),
     path('add-scope/', views.add_scope, name='add_scope'),
     path('upload-image/',views.upload_image, name='upload_image'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
