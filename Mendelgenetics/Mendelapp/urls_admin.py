from os import name
from django.urls.conf import path
from .views import*
from django.conf.urls.static import static
from django.urls import path
from Mendelapp.views_admin import  *



urlpatterns = [
    path("admin_user_login", admin_user_login, name="admin_user_login"),
    path('admin_user_logout', admin_user_logout, name="admin_user_logout"),
    path('admin_dashboard', admin_dashboard, name="admin_dashboard"),
    path('show_corprate_user_to_admin', show_corprate_user_to_admin,name='show_corprate_user_to_admin'),
    path('show_individual_user_to_admin', show_individual_user_to_admin,name="show_individual_user_to_admin"),
    path('pending_test', pending_test, name='pending_test'),
    path('published_test', published_test, name='published_test'),
    path('uploaded_result_test', uploaded_result_test, name="uploaded_result_test"),
    path('get_lot_of_test_from_admin', get_lot_of_test_from_admin,name="get_lot_of_test_from_admin"),
    path('test_reject_by_admin', test_reject_by_admin, name="test_reject_by_admin"),
    path('support_chat_admin/', support_chat_admin, name="support_chat"),
    path('upload_result_by_admin', upload_result_by_admin,name="upload_result_by_admin")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


