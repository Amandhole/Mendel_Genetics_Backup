from os import name
from django.urls.conf import path
from .views import*
from django.conf.urls.static import static
from django.urls import path
from Mendelapp import views

urlpatterns = [
#     path('add_data', add_css_data_coutnry_state_city, name="add_data"),
    path('', landing_page, name="landing_page"),
    path('user_signup', user_signup, name='user_signup'),
    path('login_page', user_login, name="login_page"),
    path('userlogout', userlogout, name="userlogout"),
    path("send_otp_for_signup_verification", send_otp_for_signup_verification,
         name="send_otp_for_signup_verification"),
    path("forget_password", forget_password_OTP, name="forget_password"),
    path("reset_password", reset_password, name="reset_password"),
    path("user_profile_page", user_profile_page, name="user_profile_page"),
    path('edit_user_proifle_page', edit_user_proifle_page,
         name="edit_user_proifle_page"),
    path('edit_user_profile_image', edit_user_profile_image,name="edit_user_profile_image"),
    path("change_user_email_otp", change_user_email_send_otp,
         name="change_user_email_otp"),
    path('add_users_new_email_address', add_users_new_email_address,
         name="add_users_new_email_address"),
    path('reset_current_password', reset_current_password,
         name="reset_current_password"),
    path('add_test_by_user',  add_test_by_user, name='add_test_by_user'),
    path('test_added_by_user_list', test_added_by_user_list,
         name="test_added_by_user_list"),
    path('All_test_list_exclude_current_user', All_test_list_exclude_current_user,
         name="All_test_list_exclude_current_user"),
    path('get_state_of_country', get_state_of_country,
         name="get_state_of_country"),
    path('get_city_of_state', get_city_of_state, name="get_city_of_state"),
    path("bid_auction_status_toggle", bid_auction_status_toggle,
         name="bid_auction_status_toggle"),
    path('change_state/', Show_state, name='change_state'),
    path('posted_test_delete_by_user', posted_test_delete_by_user,
         name='posted_test_delete_by_user'),
    path('posted_test_edit_by_user', posted_test_edit_by_user,
         name="posted_test_edit_by_user"),
    path("User_bids_on_other_users_test", User_bids_on_other_users_test,
         name="User_bids_on_other_users_test"),
    path("User_edit_bids_on_other_users_test",
         User_edit_bids_on_other_users_test, name="User_edit_bids_on_other_users_test"),
    path('view_all_bids_on_my_test', view_all_bids_on_my_test,
         name='view_all_bids_on_my_test'),
    path('Approve_users_bid_on_test', Approve_users_bid_on_test,
         name="Approve_users_bid_on_test"),
    path('Reject_bid_on_users_test', Reject_bid_on_users_test,
         name='Reject_bid_on_users_test'),
   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
