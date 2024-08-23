from django.contrib.auth.decorators import login_required

from django.urls import path

from zipprocessor.views import (
    CameraDataView,
    CameraDetailsView,
    HomepageView,
    ProcessingView,
    ResultView,
)

app_name = 'zipprocessor'
urlpatterns = [
    path(
        '',
        HomepageView.as_view(),
        name='homepage',
    ),
    path(
        'processing/',
        login_required(ProcessingView.as_view()),
        name='processing',
    ),
    path(
        'processing/<str:filename>/',
        login_required(ProcessingView.as_view()),
        name='processing_id',
    ),
    path(
        'result/',
        login_required(ResultView.as_view()),
        name='result',
    ),
    path(
        'cameradata/',
        login_required(CameraDataView.as_view()),
        name='camera_data',
    ),
    path(
        'cameradetails/<int:num>',
        login_required(CameraDetailsView.as_view()),
        name='detail_camera_photos',
    ),
]
