from django.urls import path 
from .views import (
    LeadListView, LeadDetailView, LeadCreateView, LeadUpdateView, LeadDeleteView,
    AssignAgentView, CategoryListView, CategoryDetailView, LeadCategoryUpdateView
)

app_name = "leads"

# Classed based views
urlpatterns = [
    path('', LeadListView.as_view(), name='lead-list'),
    path('<int:pk>/', LeadDetailView.as_view(), name='lead-detail'), 
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='lead-update'), 
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='lead-delete'), 
    path('<int:pk>/assign-agent/', AssignAgentView.as_view(), name='assign-agent'),
    path('<int:pk>/category/', LeadCategoryUpdateView.as_view(), name='lead-category-update'),
    # Always put create above slug/pk OR type cast pk to int
    path('create/', LeadCreateView.as_view(), name='lead-create'), 
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]

# Function based views
# urlpatterns = [
#     path('', lead_list, name='lead-list'), 
#     path('<int:pk>/', lead_detail, name='lead-detail'), 
#     path('<int:pk>/update/', lead_update, name='lead-update'), 
#     path('<int:pk>/delete/', lead_delete, name='lead-delete'), 
#     path('create/', lead_create, name='lead-create'), # Always put create above slug/pk OR type cast pk to int
# ]