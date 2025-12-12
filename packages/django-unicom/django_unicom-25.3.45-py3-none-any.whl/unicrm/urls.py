from django.urls import path

from .views import TemplateVariableListView
from .views_communication import (
    CommunicationComposeView,
    CommunicationListView,
    retry_delivery,
)
from .views_public import UnsubscribeView
from .views_api import AudiencePreviewView

app_name = 'unicrm'

urlpatterns = [
    path('api/template-variables/', TemplateVariableListView.as_view(), name='template_variables'),
    path('api/audience-preview/', AudiencePreviewView.as_view(), name='audience_preview'),
    path('communications/', CommunicationListView.as_view(), name='communications-list'),
    path('communications/compose/', CommunicationComposeView.as_view(), name='communications-compose'),
    path(
        'communications/deliveries/<int:delivery_id>/retry/',
        retry_delivery,
        name='delivery-retry',
    ),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
]
