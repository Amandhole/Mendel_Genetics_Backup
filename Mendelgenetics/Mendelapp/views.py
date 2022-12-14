import ast
import pandas as pd
from inspect import trace
import socket
from django.conf import settings

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import redirect, render
from html2text import pad_tables_in_text
from numpy import append, average
from requests import request
from .models import *
import json
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from datetime import datetime
from django.views.decorators.cache import cache_control

from django.template.loader import get_template, render_to_string
import random
import requests
import csv
import traceback
from django.db.models import Q
from django.core.mail import send_mail
# from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Avg
from django.utils.html import strip_tags


from pipes import Template
from django.core.mail import EmailMultiAlternatives


############ Function Use for Send Email ############

def send_email(subject, string, to_email):
    try:
        from_email = settings.EMAIL_HOST_USER
        email_msg = EmailMultiAlternatives(
            subject, string, from_email=from_email, to=[to_email])
        email_msg.mixed_subtype = 'related'
        # email_msg.attach_alternative(string, "user_rts/email_rts.html")
        email_msg.send()
        return "success"
    except Exception as e:
        print(str(traceback.format_exc()))
        return "error"





############ Function Use for render landing page ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def landing_page(request):
    return render(request, 'landing-page.html')




############ Function Use for User signup ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_signup(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            email = data['email_id']
            email = email.lower()
            name = data['name']
            # mobile_no = data['mobile_no']
            # address = data['address']
            user_type = data['user_type']

            password = data['password']

            if UserMaster.objects.filter(email=email).exists():
                send_data = {'status': "0", 'msg': "Email Already Exists"}

            else:
                # user_obj = UserMaster(name=name, email=email,mobile_no=mobile_no, address_line1=address, password=password, created_datime=datetime.now())
                # Remove the mobile no and address fields from signup Page
                user_obj = UserMaster(
                    name=name, email=email,  password=password, created_datime=datetime.now())
                if user_type == 'Corporate':
                    user_obj.is_corporate = True

                elif user_type == "Individual":
                    user_obj.is_individual = True

                user_obj.save()
                send_data = {
                    'status': "1", 'msg': "Account created Successful", 'user_id': str(user_obj.id)}
        else:
            return render(request, "signup.html")
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
        return redirect('landing_page')

    return JsonResponse(send_data)






############ Function Use for User Login ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    session_id = request.session.get('user_id')
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            email = data['email_id']
            password = data['password']
            user_type = data['user_type']

            if UserMaster.objects.filter(email=email, password=password).exists():
                obj = UserMaster.objects.get(email=email, password=password)

                request.session['user_id'] = str(obj.id)
                request.session['user_name'] = str(obj.email)

                if user_type == "Individual":
                    if obj.is_individual:
                        send_data = {
                            "status": "1", "msg": "individual Login succesfull", "obj": obj.id}
                    else:
                        send_data = {"status": "0",
                                     "msg": "Invalid credential", "obj": obj.id}
                    return JsonResponse(send_data)

                elif user_type == "Corporate":

                    if obj.is_corporate:
                        send_data = {
                            "status": "2", "msg": "Corporate Login succesfull", "obj": obj.id}
                    else:
                        send_data = {"status": "0",
                                     "msg": "Invalid credential", "obj": obj.id}
                    return JsonResponse(send_data)
            else:
                return JsonResponse({"status": "0", "msg": "invalid credential"})
        else:
            session_id = request.session.get('user_id')
            if session_id:
                return redirect('user_profile_page')
            else:
                return render(request, 'login.html', {"session_id": session_id})
    except:
        send_data = {"status": "0", "msg": "Invalid credential",
                     "error": str(traceback.format_exc())}
        print(traceback.format_exc())
        return redirect('landing_page')
    return JsonResponse(send_data)







############ Function Use for User logout ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlogout(request):
    try:
        del request.session['user_id']
    except:
        traceback.print_exc()
    return redirect('login_page')






############ Function Use for Send OTP for varification while signup ############

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_otp_for_signup_verification(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email_id']

        if UserMaster.objects.filter(email=email).exists():
            send_data = {'status': "2", 'msg': "Email Already Exists"}
        else:
            email_otp = str(random.randint(100000, 999999))
            

            context = {
                    "email_otp":email_otp,
                    }
            subject = " OTP for Signup"
            string = render_to_string('email_rts/signup_otp.html', context)
            plain_message = strip_tags(string)
            to_email = email
            email_status = send_email(subject, plain_message, to_email)

            send_data = {'status': "1",'msg': "OTP Sent Successfully", 'Email_OTP': email_otp}

            message = email_otp+" is your otp for verification."
            subject = "OTP Is"

            # email_status = send_email(subject, plain_message, to_email)
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)






############ Function Use for Send OTP for varification while Forget Password ############

@ csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def forget_password_OTP(request):
    
    session_id = request.session.get('user_id')
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            email = data['email_id']

            if UserMaster.objects.filter(email=email).exists():
                # email_otp = '123456'
                user_email = UserMaster.objects.get(email=email).email

                email_otp = str(random.randint(100000, 999999))
                
                context={
                    "email_otp":email_otp,
                    "user_email":user_email
                }

                subject = " OTP for forgot password"
                string = render_to_string('email_rts/forgot_password.html', context)
                plain_message = strip_tags(string)
                to_email = user_email
                email_status = send_email(subject, plain_message, to_email)


                send_data = {'status': "1", 'msg': "OTP Sent succesfully", "email_otp": email_otp}
            else:
                send_data = {'status': "0", 'msg': "Email Not Exists"}
            return JsonResponse(send_data)
        else:
            return render(request, 'forget-pasword.html')
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",'error': str(traceback.format_exc())}
    return redirect('landing_page')






############ Function Use for Reset Password ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_password(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email']
        email = email.lower()
        password = data['password']
        if UserMaster.objects.filter(email=email).exists():
            user_obj = UserMaster.objects.get(email=email)
            user_obj.password = password
            user_obj.save()

            send_data = {'status': "1",
                         'msg': "Your password has been reset successfully"}
        else:
            send_data = {'status': "0", 'msg': "Email Not Exists"}
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
        return redirect('landing_page')
    return JsonResponse(send_data)





############ Function Use for render User Profile page ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_profile_page(request):
    session_id = request.session.get('user_id')
    try:
        if session_id:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)
                countru_obj = CountryMaster.objects.all()

                contxt = {
                    "user_obj": user_obj,
                    "countru_obj": countru_obj,
                }
                return render(request, "profile.html", contxt)
            else:
                return redirect('landing_page')

        else:
            return redirect('landing_page')
    except:
        return redirect('landing_page')





@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def bid_auction_status_toggle(request):
    try:
        user_id = request.session.get('user_id')

        data = json.loads(request.body.decode('utf-8'))
        tgl_btn_value = data['tgl_btn_value']

        if request.method == "POST":
            if UserMaster.objects.filter(id=user_id).exists():
                obj = UserMaster.objects.get(id=user_id)

                if tgl_btn_value == 1:

                    obj.auc_bid_status = True
                    obj.save()

                elif tgl_btn_value == 0:
                    obj.auc_bid_status = False
                    obj.save()

                send_data = {'status': '1', 'msg': "Field Toggle Succesfully"}
            else:
                send_data = {'status': '0', 'msg': "User Not Found"}

        else:
            send_data = {'status': '0', 'msg': "Request Not Post"}
    except:
        send_data = {'status': '0', 'msg': "Something Went Wrong",
                     'error': traceback.format_exc()}
    return JsonResponse(send_data)







############ Function Use for Get State List Of Country ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_state_of_country(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        country_id = data['country_id']

        if request.method == "POST":

            state_obj = StateMaster.objects.filter(country_id=country_id)
            send_data = {'status': "1", 'msg': "Got States Of Country", "state_obj": list(
                state_obj.values())}  # json object not serilizable

        else:
            send_data = {'status': "0", 'msg': "Request Is Not Post"}
    except:

        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     "error": traceback(traceback.format_exc())}
    return JsonResponse(send_data)





############ Function Use for Get City List Of State ############
@csrf_exempt
def get_city_of_state(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        state_id = data['state_id']

        if request.method == "POST":

            city_obj = CityMaster.objects.filter(state_id=state_id)
    

            send_data = {'status': "1", 'msg': "Got city Of State","city_obj": list(city_obj.values())}

        else:
            send_data = {'status': "0", 'msg': "Request Is Not Post"}
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     "error": traceback(traceback.format_exc())}
    return JsonResponse(send_data)








############ Function Use for  Edit User Profile Image ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_user_profile_image(request):
    try:
        if request.method == "POST":
            user_id = request.session.get('user_id')
            profile_pic = request.FILES.get('profile-pic')

            if UserMaster.objects.filter(id=user_id).exists():
                user_obj = UserMaster.objects.get(id=user_id)
                user_obj.user_image = profile_pic
                user_obj.save()

                
                send_data = {'status': '1',
                             'msg': 'Profile Picture updated successfully'}
            else:
                send_data = {'status': '0', 'msg': 'User Not Exists'}

        else:
            send_data = {'status': '0', 'msg': 'Request is not post'}
    except:
        send_data = {'status': '0', 'msg': 'Something went wrong',
                     'error': traceback.format_exc()}
    return JsonResponse(send_data)






############ Function Use for  Edit User Profile ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_user_proifle_page(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_id = data['userid']
        name = data['name']
        mobile = data['mobile']
        address = data['address']
        country = data['country']
        state = data['state']
        city = data['city']
        landline = data['landline']
        cif_no = data['CIF_number']
        zipcode = data['zipcode']

        if UserMaster.objects.filter(id=user_id).exists():
            user_obj = UserMaster.objects.get(id=user_id)
            user_obj.name = name
            user_obj.mobile_no = mobile
            user_obj.address_line1 = address

            user_obj.country = "----" if country == "Select Country" else country

            if state == "Select State":
                user_obj.state = "----"
            else:
                user_obj.state = state

            if city == "Select City":
                user_obj.city = "----"
            else:
                user_obj.city = city
            user_obj.CIF_number = cif_no
            user_obj.Landline_number = landline
            user_obj.zipcode = zipcode
            user_obj.profile_status = True
            user_obj.save()

            send_data = {'status': "1", 'msg': "Profile Updated successfully"}
        else:
            send_data = {'status': "0", 'msg': "User Id Not Exists"}
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)




############ Function Use for Send OTP To Change Email ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_user_email_send_otp(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            email = data['email']

            if UserMaster.objects.filter(id=user_id, email=email).exists():
                user_email = UserMaster.objects.get(id=user_id).email
                email_otp = str(random.randint(100000, 999999))
                # email_otp = '123456'
                

                context={
                        "user_email":user_email,
                        "email_otp": email_otp
                    }

                subject = " OTP for Change the email"
                string = render_to_string('email_rts/change_email.html', context)
                plain_message = strip_tags(string)
                to_email = user_email
                email_status = send_email(subject, plain_message, to_email)
               

                send_data = {'status': "1", 'msg': "OTP Sent To Register Email", "email_otp": email_otp}
            else:

                send_data = {'status': "0", 'msg': "User Not Exists"}
        else:
            send_data = {'status': "0", 'msg': "Request is not post"}
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)




############ Function Use for Add User's New Email ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_users_new_email_address(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            old_email = data['old_email']
            new_email = data['new_email']

          
            if UserMaster.objects.filter(email=new_email).exists():
                send_data = {'status': "0", 'msg': "Email Already Exists", }

            elif UserMaster.objects.filter(id=user_id, email=old_email).exists():
                user_obj = UserMaster.objects.get(id=user_id, email=old_email)
                user_obj.email = new_email
                user_obj.save()
                send_data = {'status': "1",
                             'msg': "Email Address Change Succesfully", }
            else:
                send_data = {'status': "0", 'msg': "User Not Exists"}
        else:
            send_data = {'status': "0", 'msg': "Request is not post"}
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)




############ Function Use for Reset Current Password ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_current_password(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            old_password = data['old_password']
            new_password = data['new_password']

            if UserMaster.objects.filter(id=user_id, password=old_password).exists():
                user_obj = UserMaster.objects.get(
                    id=user_id, password=old_password)
                user_obj.password = new_password
                user_obj.save()
                send_data = {'status': "1",
                             'msg': "Reset password Succesfully", }
            else:
                send_data = {'status': "0",
                             'msg': "Incorrect Current Password"}
        else:
            send_data = {'status': "0", 'msg': "Request is not post"}
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)




############ Function Use for Add Test By User ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_test_by_user(request):
    try:
        session_id = request.session.get('user_id')

        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            user_id = data['user_id']
            first_name = data['first_name']
            last_name = data['last_name']
            patient_age = data['patient_age']
            patient_race = data["patient_race"]
            gender = data['select_gender']
            patient_weight = data['patient_weight']
            patient_height = data['patient_height']
            dr_name = data['dr_name']
            datepicker = data['datepicker']
            center = data["center"]
            Email = data['Email']
            other_way = data['other_way']
            Contact_person_name = data['contact_person']
            test_req_id = data['test_req_id']
            test_requested_type = data['test_requested_type']
            test_requested = data['test_req_disc']
            background_data = data['background_data']
            # patient_test = data['patient_test']
            weight_unit = data['weight_unit']
            height_unit = data['height_unit']
            external_reference = data['external_reference']

            format_data = '%d-%m-%Y'

            converted_date = datetime.strptime(datepicker, format_data)

            # strfdate = converted_date.strftime("%Y-%m-%d %H:%M:%S")

            user_id_len = len(user_id)
            test_count = UserTest.objects.count()
            if UserMaster.objects.filter(id=user_id).exists():
                user_obj = UserMaster.objects.get(id=user_id)
                now = datetime.now()

                test_obj = UserTest(fk_sample_master_id = test_req_id, fk_user_id = user_id,  patient_first_name=first_name, patient_last_name=last_name,patient_age = patient_age, patient_race = patient_race, patient_gender = gender, patient_weight = patient_weight,patient_height=patient_height, doctor_name=dr_name, date = converted_date,Centre = center ,Email = Email , other_way = other_way, test_requested = test_requested,background_data=background_data,  weight_unit=weight_unit, height_unit=height_unit, Contact_person_name=Contact_person_name, test_requested_type=test_requested_type, status="Pending", created_date_time=now,external_reference=external_reference)
                test_obj.save()
                test_obj.auction_test_id = f"{test_obj.fk_user.id:03d}{(test_count+1):07d}"
                test_obj.save()

            ############## send mail ################
            ################# Below code for send emai for each post ##################### 
                # context = {
                #     "user_obj": user_obj,
                #     "test_obj": test_obj,
                #     "auction_test_id": f"{test_obj.fk_user.id:03d}{(test_count+1):07d}"
                # }

                # subject = "Notificaci??n prueba" + '  ' + f"{test_obj.fk_user.id:03d}{(test_count+1):07d}" + '  ' "de" '  ' + test_requested
                # string = render_to_string('email_rts/post_test.html', context)
                # plain_message = strip_tags(string)
                # to_email = user_obj.email
                # email_status = send_email(subject, plain_message, to_email)
                

                send_data = {'status': "1" ,  'msg': "Test Added Succesfully" , "test_id": test_obj.auction_test_id} 
            else:
                send_data = {'status': "0", "msg": "User Not found"}
        else:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)
            sampletest = SampleTestMaster.objects.all()
            context = {
                "user_obj": user_obj,
                'sampletest': sampletest,
            }
            return render(request, 'post-test.html', context)
    except:
        send_data = {'status': '0', 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
        print(traceback.format_exc())
        return redirect('landing_page')

    return JsonResponse(send_data)



############  Get Test List Of Perticular User ############

def get_brief_path_list(test_list):
    temp_list = []
    for path in ast.literal_eval(test_list):
        if not any(d['pathalogy'] == path for d in temp_list):
            pathalogy_obj = SampleTestMaster.objects.filter(pathalogy=path).last()
            temp_list.append({
                'pathalogy': path,
                'gens': pathalogy_obj.gens,
                'quantity': 1
            })
        else:
            index = next((index for (index, d) in enumerate(
                temp_list) if d["pathalogy"] in path), None)
            temp_list[index]['quantity'] += 1
    return temp_list





############  Function Use For Get Pending , Active , Confirm and Complete Test List ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def test_added_by_user_list(request):
    ave_value = 0
   
    try:
        session_id = request.session.get('user_id')
        if session_id:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)

                pending_test = UserTest.objects.filter(fk_user_id=session_id, status="Pending").order_by('-id')                                # Pending

                test_active_obj = TestLots.objects.filter(fk_user_master_id=session_id, lot_status="Published").order_by('-id')                  # Published

                Confirm_test_obj = UserBids.objects.filter(bid_status='Approved', fk_test_lot__fk_user_master__id=session_id).order_by('-id')   # Approved or Result_Upload_By_Bidder

                Completed_test_obj = UserBids.objects.filter(
                    bid_status='Result_Upload_By_Bidder', fk_test_lot__fk_user_master__id=session_id).order_by('-id')  # Result_Upload_By_Admin

                cancelled_test_obj = UserTest.objects.filter(fk_user_id=session_id, status="Cancelled").order_by('-id')                         # Cancelled

                for test in test_active_obj:
                    test.bid_count = UserBids.objects.filter(fk_test_lot__id=test.id).exclude(bid_status="Cancelled").count()
                    test.view_path_brief_list = get_brief_path_list(test.test_pathalogy)
                    test.average = UserBids.objects.filter(fk_test_lot__id=test.id).aggregate(Avg('bid_Price'))

                for test in Completed_test_obj:
                    test.temp_string = " , ".join(ast.literal_eval(test.fk_test_lot.test_pathalogy))
                    test.temp_gens = " , ".join(ast.literal_eval(test.fk_test_lot.test_gen))
                    test.view_path_brief_list = get_brief_path_list(test.fk_test_lot.test_pathalogy)
                    test.bid_count = UserBids.objects.filter(fk_test_lot=test.fk_test_lot.id).count()
                    test.average = UserBids.objects.filter(fk_test_lot__id=test.fk_test_lot.id).aggregate(Avg('bid_Price'))

                for test in Confirm_test_obj:
                    test.temp_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_pathalogy))
                    test.temp_gens = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_gen))
                    test.view_path_brief_list = get_brief_path_list(
                        test.fk_test_lot.test_pathalogy)
                    test.bid_count = UserBids.objects.filter(
                        fk_test_lot=test.fk_test_lot.id).count()
                    test.average = UserBids.objects.filter(
                        fk_test_lot=test.fk_test_lot.id).aggregate(Avg('bid_Price'))

                if request.method == "POST":
                    data = json.loads(request.body.decode('utf-8'))
                    tab_type = data['tab_type']

                    if tab_type == "Active_tab":
                        context = {
                            "user_obj": user_obj,
                            "test_active_obj": test_active_obj,
                            "ave_value": ave_value
                        }
                        send_data = render_to_string( 'user_rts/active_post_rts.html', context)

                    elif tab_type == "Pending_tab":
                        user_obj = UserMaster.objects.get(id=session_id)
                        sampletest = SampleTestMaster.objects.all()
                        
                        context = {
                            "user_obj": user_obj,
                            "pending_test": pending_test,
                            "sampletest": sampletest
                        }
                        send_data = render_to_string('user_rts/pending_post_rts.html', context)

                    elif tab_type == "Cancelled_tab":
                        context = {
                            "user_obj": user_obj,
                            "cancelled_test_obj": cancelled_test_obj,
                        }
                        send_data = render_to_string('user_rts/cancelld_post_rts.html', context)

                    elif tab_type == "Confirm_tab":

                        context = {
                            "user_obj": user_obj,
                            "Confirm_test_obj": Confirm_test_obj,
                            "ave_value": ave_value,

                        }
                        send_data = render_to_string('user_rts/confirmed_post_rts.html', context)

                    elif tab_type == "Complete_tab":
                        context = {
                            "user_obj": user_obj,
                            "Completed_test_obj": Completed_test_obj,
                            "ave_value": ave_value
                        }
                        send_data = render_to_string('user_rts/completed.html', context)

                    return HttpResponse(send_data)
                else:
                    sampletest = SampleTestMaster.objects.all()
                    
                    context = {
                        "user_obj": user_obj,
                        "test_active_obj": test_active_obj,
                        "Confirm_test_obj": Confirm_test_obj,
                        "cancelled_test_obj": cancelled_test_obj,
                        "pending_test": pending_test,
                        "sampletest": sampletest
                    }
                    
                return render(request, 'posted-test.html', context)
        return redirect('landing_page')
    except:
        print(traceback.format_exc())
        return redirect('landing_page')








############  Function Use For Delete Posted Pending Test By User ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def posted_pending_test_delete_by_user(request):
    try:
        session_id = request.session.get('user_id')
        if request.method == "POST":

            data = json.loads(request.body.decode('utf-8'))
            test_id = data['test_id']

            if UserTest.objects.filter(id=test_id).exists():
                test_obj = UserTest.objects.get(id=test_id)
                test_obj.delete()
                pending_test = UserTest.objects.filter(fk_user_id=session_id, status="Pending").order_by('-id')
                context = {
                    "pending_test": pending_test
                }
                send_data = render_to_string(
                    'user_rts/pending_post_rts.html', context)
                return HttpResponse(send_data)
            else:
                send_data = {'status': '0', "msg": "Test Does Not Exist"}
                return JsonResponse(send_data)
        else:
            send_data = {'status': '0', "msg": "Request Is Not Post"}
            return JsonResponse(send_data)
    except:
        send_data = {'status': '0', "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
        print(traceback.format_exc())
        return JsonResponse(send_data)






############  Function use For Delete Cancelled Test By User ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def posted_cancelled_test_delete_by_user(request):
    try:
        session_id = request.session.get('user_id')
        if request.method == "POST":

            data = json.loads(request.body.decode('utf-8'))
            test_id = data['test_id']

            if UserTest.objects.filter(id=test_id).exists():
                test_obj = UserTest.objects.get(id=test_id)
                test_obj.delete()

                cancelled_test_obj = UserTest.objects.filter(
                    fk_user_id=session_id, status="Cancelled").order_by('-id')
                context = {
                    "cancelled_test_obj": cancelled_test_obj
                }
                send_data = render_to_string(
                    'user_rts/cancelld_post_rts.html', context)
                return HttpResponse(send_data)
            else:
                send_data = {'status': '0', "msg": "Test Does Not Exist"}
                return JsonResponse(send_data)
        else:
            send_data = {'status': '0', "msg": "Request Is Not Post"}
            return JsonResponse(send_data)
    except:
        send_data = {'status': '0', "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
        print(traceback.format_exc())
        return JsonResponse(send_data)


############  Function use For Edit Pending Test By User ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def posted_test_edit_by_user(request):

    try:
        if request.method == "POST":
        
            data = json.loads(request.body.decode('utf-8'))
            test_id = data['test_id']
            drname = data['drname']
            datepicker = data['datepicker']
            centre = data['centre']

            email = data['email']
            otherway = data['otherway']
            contact_pereson = data['contact_pereson']

            backgrounddata = data['backgrounddata']
            
            firstname = data['firstname']
            lastname = data['lastname']
            patientage = data['patientage']

            patientrace = data['patientrace']
            selectgender = data['selectgender']
            patientweight = data['patientweight']
            patientheight = data['patientheight']

            weight_unit = data['weight_unit']
            height_unit = data['height_unit']
            
        
            #Pending for dropdown
            
            test_req_id = data['test_req_id']
            test_requested_type = data['test_requested_type']
            test_req_disc = data['test_req_disc']


            converted_date = datetime.strptime(datepicker, "%d-%m-%Y")

            if UserTest.objects.filter(id=test_id).exists():
                test_obj = UserTest.objects.get(id=test_id)
                test_obj.doctor_name = drname
                test_obj.date = converted_date
                test_obj.Centre=centre
                test_obj.Email = email
                test_obj.other_way=otherway
                test_obj.Contact_person_name = contact_pereson
                test_obj.background_data=backgrounddata
                test_obj.patient_first_name=firstname
                test_obj.patient_last_name=lastname
                test_obj.patient_age = patientage
                test_obj.patient_race = patientrace
                test_obj.patient_gender = selectgender
                test_obj.patient_weight=patientweight
                test_obj.patient_height = patientheight
                test_obj.weight_unit = weight_unit
                test_obj.height_unit = height_unit

                test_obj.fk_sample_master_id = test_req_id
                test_obj.test_requested_type=test_requested_type
                test_obj.test_requested=test_req_disc

                test_obj.save()
                
                send_data = {'status': '1', "msg": "Test Updated Succesfully"}

            else:
                send_data = {'status': '0', "msg": "Test Not Exists"}
        else:
            send_data = {'status': '0', "msg": "Request Is Not Post"}
    except:
        send_data = {'status': '0', "msg": "Something Went Wrong","error": traceback.format_exc()}
        
    return JsonResponse(send_data)





############  Function use For Get Auction Test Exclude Curent User ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def All_test_list_exclude_current_user(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            
            today = datetime.today()
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)
                # tets_obj = UserTest.objects.filter(Q(status="Active") & Q(admin_action_status ="Published")).exclude(fk_user_id=session_id)

                tets_obj = TestLots.objects.filter(lot_status="Published").exclude(
                    fk_user_master__id=session_id).order_by('-id')

                ls = []
                for test in tets_obj:
                    test.temp_string = " , ".join(
                        ast.literal_eval(test.test_pathalogy))
                    test.temp_gens = " , ".join(
                        ast.literal_eval(test.test_gen))
                    bids = UserBids.objects.filter(fk_test_lot=test)
                    for bid in bids:
                        test.my_bid = True if bid.fk_user_master == user_obj else False
                        test.my_bid_obj = bid

                    temp_list = []
                    for path in ast.literal_eval(test.test_pathalogy):
                        if not any(d['pathalogy'] == path for d in temp_list):
                            pathalogy_obj = SampleTestMaster.objects.filter(
                                pathalogy=path).last()
                            temp_list.append({
                                'pathalogy': path,
                                'gens': pathalogy_obj.gens,
                                'quantity': 1
                            })
                        else:
                            index = next((index for (index, d) in enumerate(
                                temp_list) if d["pathalogy"] in path), None)
                            temp_list[index]['quantity'] += 1
                    test.view_path_brief_list = temp_list

                context = {
                    "user_obj": user_obj,
                    "test_obj": tets_obj,
                    # "bid_obj": bid_obj

                }
                return render(request, 'all-auctions.html', context)
        else:
            return redirect('landing_page')

    except:
        print(traceback.format_exc())
        return redirect('landing_page')





############  Function use For Get States when user do Signup ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Show_state(request):
    try:
        country = request.POST.get('country_id')
        state = request.POST.get('state')
        city = request.POST.get('city')

        state_id = StateMaster.objects.get(name=state).id
        state = StateMaster.objects.filter(
            country_id=CountryMaster.objects.get(name=country).id).values()
        city_list = CityMaster.objects.filter(state_id=state_id).values()

        return JsonResponse({'status': '1', 'msg': 'Success', 'subcategory': list(state), 'citycategory': list(city_list)})
    except:
        traceback.print_exc()
        return JsonResponse({'status': '0', 'msg': 'Something went wrong.'})






############  Function Use for Storing data In CSV File ############
fieldnames = ['id', 'sortname', 'name', 'phonecode']
'''rows = list(CityMaster.objects.all().values())

with open(f'{settings.BASE_DIR}/city.csv', 'w', encoding='UTF8', newline='') as f:
     writer = csv.DictWriter(f, fieldnames=fieldnames)
     writer.writeheader()
     writer.writerows(rows)'''




############  Function Use For  Add CSV Data In Database File ############
def add_css_data_coutnry_state_city(request):
    print(settings.BASE_DIR)
    SampleTestMaster.objects.all().delete()
    data = pd.read_excel(f'{settings.BASE_DIR}/sample.xlsx', engine='openpyxl')

    data = data.to_dict('records')

    for d in data:
        # pass
        SampleTestMaster.objects.create(group=d['Group'], plazo=d['Unnamed: 3'], pathalogy=d['Patology'], gens=d['Gens included'],sample_type=d['Sample type'], transport=d['transport conditions'])
    # with open(f'{settings.BASE_DIR}/sample_test_master.csv', 'r', encoding="utf8") as f:
        # csvreader = csv.reader(f)
        # header = next(csvreader)
        # for row in csvreader:
        #     # print(row[0].strip(), row[1].strip(), row[2].strip(), row[4].strip(), row[5].strip())
        #     SampleTestMaster.objects.create(
        #         group=row[0].strip(), pathalogy=row[1].strip(), gens=row[2].strip(),sample_type=row[4].strip(),transport=row[5].strip())
    return HttpResponse('data added succesfully')





############  Function Use For Bid On Other User Test ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def User_bids_on_other_users_test(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            user_id = data['user_id']
            lot_id = data['lot_id']
            bidprice = data['bidprice']
            expect_result_date = data['expect_result']
            checkbox = data['checkbox']

            converted_date = datetime.strptime(expect_result_date, "%d-%m-%Y")
            

            user_bid = UserBids(fk_user_master_id=user_id, fk_test_lot_id=lot_id, bid_Price=bidprice,
                                expect_result_date=datetime.now(), checkbox=checkbox, bid_status="Pending")

            user_bid.save()

            send_data = {"status": "1", "msg": "Bid Added Succesfully"}
        else:
            send_data = {"status": "0", "msg": "Request Is Not Post"}
    except:
        send_data = {"status": "0", "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
    return JsonResponse(send_data)






############  Function Use For Edit Bid On Test ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def User_edit_bids_on_other_users_test(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            bid_id = data['bid_id']
            bid_price = data['bid_price']
            biexpect_result_dated = data['expect_result_date']

            converted_date = datetime.strptime(biexpect_result_dated, "%d-%m-%Y")

            if UserBids.objects.filter(id=bid_id):
                userbid_obj = UserBids.objects.get(id=bid_id)
                userbid_obj.bid_Price = bid_price
                userbid_obj.expect_result_date = converted_date
                userbid_obj.save()
                send_data = {"status": '1', "msg": "Bid Updated Succesfully"}
            else:
                send_data = {"status": '0', "msg": "User Bid Not Found"}
        else:
            send_data = {"status": '0', "msg": "Request Is Not Post"}
    except:
        send_data = {"status": '0', "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
    return JsonResponse(send_data)





############  Function Use For See All the Bids On Test ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_all_bids_on_my_test(request):
    try:
        session_id = request.session.get('admin_user_id')
        if session_id:
            if request.method == "POST":
                data = json.loads(request.body.decode('utf-8'))
                lot_id = data['test_id']

                if AdminUser.objects.filter(id=session_id).exists():
                    user_obj = AdminUser.objects.get(id=session_id)
                    if TestLots.objects.filter(id=lot_id):
                        test_lot_obj = TestLots.objects.filter(id=lot_id)

                        for test in test_lot_obj:
                            test.temp_string = " , ".join(
                                ast.literal_eval(test.test_pathalogy))

                        for test in test_lot_obj:
                            test.temp_gens = " , ".join(
                                ast.literal_eval(test.test_gen))

                        bid_obj = UserBids.objects.filter(
                            fk_test_lot_id=lot_id, bid_status="Pending").order_by('-id')

                        approved_bid_obj = UserBids.objects.get(Q(fk_test_lot_id=lot_id, bid_status="Approved") | Q(fk_test_lot_id=lot_id, bid_status="Result_Upload_By_Bidder")) if UserBids.objects.filter(
                            Q(fk_test_lot_id=lot_id, bid_status="Approved") | Q(fk_test_lot_id=lot_id, bid_status="Result_Upload_By_Bidder")).exists() else None

                        recent_bid_obj = UserBids.objects.filter(fk_test_lot_id=lot_id, bid_status="Cancelled") if UserBids.objects.filter(
                            fk_test_lot_id=lot_id, bid_status="Cancelled").exists() else None
                    

                        bidcount = bid_obj.count()

                    context = {
                        "user_obj": user_obj,
                        "test_lot_obj": test_lot_obj,
                        "bid_obj": bid_obj,
                        "approved_bid": approved_bid_obj,
                        "recent_bid_obj": recent_bid_obj
                    }
                    send_data = render_to_string('rts_bid_detail.html', context)
                else:
                    send_data = {"msg": "User Not Exist"}
            else:
                send_data = {"msg": "Request Not Post"}
        else:
            send_data = {"msg": "User Not Exist"}
    except:
        send_data = {"msg": "Something Went Wrong",
                     "staus": "0", "error": traceback.format_exc()}
    return HttpResponse(send_data)





############  Function Use For Approve The Bid By Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Approve_users_bid_on_test(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            lot_id = data['lot_id']
            bid_id = data['bid_id']

            if TestLots.objects.filter(id=lot_id):
                test_obj = TestLots.objects.get(id=lot_id)
                test_obj.lot_status = "Approved"

                test_obj.save()

                bid_obj = UserBids.objects.get(id=bid_id)
                bid_obj.bid_status = "Approved"
                bid_obj.save()

                UserBids.objects.filter(fk_test_lot__id=lot_id).exclude(id=bid_id).update(bid_status="Cancelled")

                auctionr_name = TestLots.objects.get(
                    id=lot_id).fk_user_master.name
                auctionr_email = TestLots.objects.get(
                    id=lot_id).fk_user_master.email
                lot_number = TestLots.objects.get(id=lot_id).test_lot_id
                test_count = TestLots.objects.get(id=lot_id)
                new = test_count.tests_in_lot

                ####### auctioner send mail#########

                test_obj = TestLots.objects.get(id=lot_id).tests_in_lot
                test_data = eval(test_obj)

                test_obj = UserTest.objects.filter(id__in=test_data)

                result = ast.literal_eval(new)

                quantity_of_lot = 0
                for i in range(len(result)):
                    quantity_of_lot += 1

                context = {
                    "auctionr_name": auctionr_name,
                    "quantity_of_lot": quantity_of_lot,
                    "lot_number": lot_number,
                    "test_obj": test_obj
                }

                subject = "Datos de identificaci??n y de env??o de las muestras:"
                string = render_to_string(
                    'email_rts/email_auctioner.html', context)
                plain_message = strip_tags(string)
                to_email = auctionr_email
                email_status = send_email(subject, plain_message, to_email)
                send_data = {"msg": "Bid approved successfully", "status": "1"}

                ################# end auctinoner email#############

                ################ send mail to bider###############
                bidder_email = UserBids.objects.get(
                    fk_test_lot_id=lot_id, bid_status="Approved").fk_user_master.email

                

                subject = "Confirmaci??n adjudicaci??n del lote"  + ' ' + str(lot_number) + ' ' +  "que consta de " + '  ' +  str(quantity_of_lot) + ' '  +  "pruebas"

                string = render_to_string(
                    'email_rts/email_bidder.html', context)
                plain_message = strip_tags(string)
                to_email = bidder_email
                email_status = send_email(subject, plain_message, to_email)
                send_data = {"msg": "Bid approved successfully", "status": "1"}

        else:
            send_data = {"msg": "Request is not post", "status": "0"}

    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
    return JsonResponse(send_data)






############  Function Use For Reject The Bids ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Reject_bid_on_users_test(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            bid_id = data['bid_id']
            if UserBids.objects.filter(id=bid_id):
                UserBids.objects.filter(id=bid_id).update(
                    bid_status="Cancelled")
                send_data = {"msg": "Bid Rejected successfully", "status": "1"}

        else:
            send_data = {"msg": "Request is not post", "status": "0"}

    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
    return JsonResponse(send_data)





############  Function Use For  To See My Bids on Other User Test At Bidder Side   Pending , Active , Confirm , Complete, ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def my_bids_on_other_users_test(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)

            

                my_active_bid = UserBids.objects.filter(
                    fk_user_master__id=session_id, bid_status='Pending').order_by('-id')
                for test in my_active_bid:
                    test.temp_string = joined_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_pathalogy))
                    test.test_gen = joined_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_gen))

                my_approved_bid = UserBids.objects.filter(
                    fk_user_master__id=session_id, bid_status='Approved').order_by('-id')

                for test in my_approved_bid:
                    test.temp_string = joined_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_pathalogy))
                    test.test_gen = joined_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_gen))

                my_complete_bid = UserBids.objects.filter(Q(fk_user_master__id=session_id, bid_status='Result_Upload_By_Bidder') | Q(
                    fk_user_master__id=session_id, bid_status='Result_Upload_By_Admin')).order_by('-id')

                for test in my_complete_bid:
                    test.temp_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_pathalogy))
                    test.test_gen = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_gen))
                    
                    day_diff = datetime.now() - test.fk_test_lot.upload_date_time
                    test.day_diff = day_diff.days

                my_cancelled_bid = UserBids.objects.filter(
                    fk_user_master__id=session_id, bid_status='Cancelled')
                for test in my_cancelled_bid:
                    test.temp_string = joined_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_pathalogy))
                    test.test_gen = joined_string = " , ".join(
                        ast.literal_eval(test.fk_test_lot.test_gen))

                
                context = {
                    "user_obj": user_obj,
                    'my_active_bid': my_active_bid,
                    'my_approved_bid': my_approved_bid,
                    "my_complete_bid": my_complete_bid,
                    "my_cancelled_bid": my_cancelled_bid

                }
                return render(request, 'my-bids.html', context)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())
        return redirect('landing_page')







############  Function Use For Select Pathology and and Gens  At Post Test ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_sample_test_data(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            test_req_id = data['test_req_id']
            sample_test_obj = SampleTestMaster.objects.filter(id=test_req_id)

            for i in sample_test_obj:

                print(i)

            send_data = {"msg": "Data recicved succesfully","status": "1", "obj_data": list(sample_test_obj.values())}

        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
        print(traceback.format_exc())
    return JsonResponse(send_data)





############  Function Use For Support Chat View ############
def support_chat(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            user_obj = UserMaster.objects.get(id=session_id)
            support_tickets = Support.objects.filter(
                fk_user=user_obj, status='Open').order_by('-issue_date')

            support_content = render_to_string(
                'r_t_s_Templates/r_t_s_support_chat.html', {'support_tickets': support_tickets})

            context = {
                "user_obj": user_obj,
                'support_content': support_content,
            }

            return render(request, 'support_chat.html', context=context)
        return redirect('/login_page')
    except:
        traceback.print_exc()
    return redirect('/login_page')






############  Function Use For Raise_Support_Ticket ############
@csrf_exempt
def raise_support_ticket(request):
    try:
        send_data = {'status': '0', 'msg': 'Something went wrong...'}
        user_id = request.POST.get('user_id', None)
        subject = request.POST.get('subject', None)
        filter_status = request.POST.get('filter', None)
        admin_email = 'villamredon@gmail.com'
        status = 'Open'

        try:
            Support.objects.create(
                fk_user_id=user_id, subject=subject, admin_email=admin_email, status=status)

            support_tickets = Support.objects.filter(
                fk_user_id=user_id, status=filter_status).order_by('-issue_date')

            support_content = render_to_string(
                'r_t_s_Templates/r_t_s_support_chat.html', {'support_tickets': support_tickets})

            send_data = {'status': '1', 'msg': 'Support ticket saved successfully...',
                         'support_content': support_content}
        except:
            send_data = {'status': '0', 'msg': 'Something went wrong...'}
    except:
        traceback.print_exc()
    return JsonResponse(send_data)







############  Function Use For User support_ticket_filter ############
@csrf_exempt
def support_ticket_filter(request):
    try:
        send_data = {'status': '0', 'msg': 'Something went wrong...'}
        user_id = request.POST.get('user_id', None)
        filter_status = request.POST.get('filter', None)

        try:
            support_tickets = Support.objects.filter(
                fk_user_id=user_id, status=filter_status).order_by('-issue_date')

            support_content = render_to_string(
                'r_t_s_Templates/r_t_s_support_chat.html', {'support_tickets': support_tickets})

            send_data = {'status': '1', 'msg': 'Support ticket saved successfully...',
                         'support_content': support_content}
        except:
            send_data = {'status': '0', 'msg': 'Something went wrong...'}
    except:
        traceback.print_exc()
    return JsonResponse(send_data)







############  Function Use For Admin support_ticket_filter ############
@csrf_exempt
def support_ticket_filter_admin(request):
    try:
        send_data = {'status': '0', 'msg': 'Something went wrong...'}
        filter_status = request.POST.get('filter', None)

        try:
            support_tickets = Support.objects.filter(
                status=filter_status).order_by('-issue_date')

            support_content = render_to_string('r_t_s_Templates/r_t_s_support_chat.html', {
                                               'support_tickets': support_tickets, 'user': 'Admin'})

            send_data = {'status': '1', 'msg': 'Support ticket saved successfully...',
                         'support_content': support_content}
        except:
            send_data = {'status': '0', 'msg': 'Something went wrong...'}
    except:
        traceback.print_exc()
    return JsonResponse(send_data)






############  Function Use For Close_Support_Ticket ############
@csrf_exempt
def close_support_ticket(request):
    try:
        send_data = {'status': '0', 'msg': 'Something went wrong...'}
        support_id = request.POST['support_id']

        try:
            Support.objects.filter(
                support_id=support_id).update(status='Close')

            send_data = {'status': '1',
                         'msg': 'Support ticket closed successfully...'}
        except:
            send_data = {'status': '0', 'msg': 'Something went wrong...'}
    except:
        traceback.print_exc()
    return JsonResponse(send_data)






############  Function Use For Get Test Lot   ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_all_test_of_lot_from_active_tab(request):

    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            lot_id = data['lot_id']

            test_list = TestLots.objects.get(id=lot_id).tests_in_lot
            coment_on_lot = TestLots.objects.get(id=lot_id).comment

            
            test_data = eval(test_list)
        
            user_test_obj = UserTest.objects.filter(id__in=test_data)

            context = {
                "user_test_obj": user_test_obj,
                "coment_on_lot":coment_on_lot
            }

            send_data = render_to_string('edit_uploaded_document.html', context)

        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
        print(traceback.format_exc())
    return HttpResponse(send_data)






############  Function Use For Render To String To view Completed Test At Bidder Side ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Auctioner_completed_test(request):
    
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            lot_id = data['lot_id']

            test_list = TestLots.objects.get(id=lot_id).tests_in_lot
            coment_on_lot = TestLots.objects.get(id=lot_id).comment

            test_data = eval(test_list)

            user_test_obj = UserTest.objects.filter(id__in=test_data)

            context = {
                "user_test_obj": user_test_obj,
                "coment_on_lot": coment_on_lot
            }

            send_data = render_to_string('uploaded_document.html', context)

        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
        print(traceback.format_exc())
    return HttpResponse(send_data)







############  Function Use For Upload The Result User At Bidder Side ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def upload_result_by_bidder(request):

    try:
        if request.method == "POST":
            for key, file in request.FILES.items():
                test_list = key.split('_')              # ['file', '1', '349']
                # print(test_list[2], test_list[1], test_list)

                if test_list[1] == '1':
                    doc1_obj = UserTest.objects.get(id=test_list[2])
                    doc1_obj.bidder_doc_first = file
                    doc1_obj.save()

                elif test_list[1] == '2':
                    obj2_doc = UserTest.objects.get(id=test_list[2])
                    obj2_doc.bidder_doc_second = file
                    obj2_doc.save()

            test_lot_id = request.POST.get('test_lot_id')

            comment = request.POST.get('comment')

            TestLots.objects.filter(id=test_lot_id).update(upload_date_time=datetime.now(), result_upload_status="Upload", lot_status="Completed", comment=comment)

            bid_obj = UserBids.objects.get(fk_test_lot_id=test_lot_id, bid_status="Approved")

            bid_obj.bid_status = "Result_Upload_By_Bidder"

            bid_obj.save()

            auctionr_name = TestLots.objects.get(
                id=test_lot_id).fk_user_master.name
            auctionr_email = TestLots.objects.get(
                id=test_lot_id).fk_user_master.email
            lot_number = TestLots.objects.get(id=test_lot_id).test_lot_id
            test_count = TestLots.objects.get(id=test_lot_id)

            ####### auctioner send mail#########

            test_obj = TestLots.objects.get(id=test_lot_id).tests_in_lot
            test_data = eval(test_obj)
            test_obj = UserTest.objects.filter(id__in=test_data)

            

            context = {
                "test_obj": test_obj,
                "auctionr_name": auctionr_name
            }

            subject = "Resultado del test " + str(lot_number) + "listos."
            string = render_to_string('email_rts/result_upload.html', context)
            plain_message = strip_tags(string)
            to_email = auctionr_email
            email_status = send_email(subject, plain_message, to_email)

            send_data = {"msg": "Bid approved successfully", "status": "1"}

            send_data = {"msg": "Request is not post", "status": "1"}
        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
        print(traceback.format_exc())
    return JsonResponse(send_data)






############  Function Use For Edit uploaded result At bidder side ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_uploaded_result_bidder(request):

    try:
        if request.method == "POST":
            for key, file in request.FILES.items():
                # print(key, file)
                test_list = key.split('_')             

                if test_list[1] == '1':
                    print('file...1', file)
                    doc1_obj = UserTest.objects.get(id=test_list[2])
                    doc1_obj.bidder_doc_first = file
                    doc1_obj.save()

                elif test_list[1] == '2':
                    print('file...2', file)
                    obj2_doc = UserTest.objects.get(id=test_list[2])
                    obj2_doc.bidder_doc_second = file
                    obj2_doc.save()


            send_data = {"msg": "Documents uploaded successfully...", "status": "1"}
        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        send_data = {"msg": "Something went wrong","status": "0", "error": traceback.format_exc()}
        print(traceback.format_exc())
    return JsonResponse(send_data)






############  Function Use For Retriving Test Of Specific Lot ############
@csrf_exempt
def get_user_test_by_lot_id(request):
    try:
        
        if request.method == "POST":

            data = json.loads(request.body.decode('utf-8'))
            lot_id = data['user_lot_id']
            obj_lot = TestLots.objects.get(id=lot_id)
            user_test_id = obj_lot.tests_in_lot
            result = ast.literal_eval(user_test_id)
            empt_list = [int(i) for i in result]  # list comprehenssion
            user_test_obj = UserTest.objects.filter(id__in=empt_list)
            context = {
                "user_test_obj": user_test_obj
            }

            send_data = render_to_string('user_rts/img_uploaad_modal.html', context)

            return HttpResponse(send_data)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())
        return redirect('landing_page')



############  Function Use For Download Test Of Specific Lot ############
@csrf_exempt
def get_user_test_to_admin_for_download(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            lot_id = data['user_lot_id']
            obj_lot = TestLots.objects.get(id=lot_id)
            user_test_id = obj_lot.tests_in_lot
            result = ast.literal_eval(user_test_id)
            empt_list = [int(i) for i in result]  # list comprehenssion
            user_test_obj = UserTest.objects.filter(id__in=empt_list)

            coment_on_lot = TestLots.objects.get(id=lot_id).comment
            
            context = {
                "user_test_obj": user_test_obj,
                "coment_on_lot":coment_on_lot
            }

            send_data = render_to_string('admin/download-test-admin.html', context)

            return HttpResponse(send_data)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())
        return redirect('landing_page')






############  Function Use For Retriving All The Bids on My Test At Auctioner Side ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_all_bids_on_my_test_auctioner_side(request):
    try:
        session_id = request.session.get('user_id')

        if session_id:

            if request.method == "POST":
                data = json.loads(request.body.decode('utf-8'))
                lot_id = data['test_id']

                if UserMaster.objects.filter(id=session_id).exists():
                    user_obj = UserMaster.objects.get(id=session_id)
                    if TestLots.objects.filter(id=lot_id):
                        test_lot_obj = TestLots.objects.filter(id=lot_id)

                        for test in test_lot_obj:
                            test.temp_string = joined_string = " , ".join(
                                ast.literal_eval(test.test_pathalogy))

                        for test in test_lot_obj:
                            test.temp_gens = joined_string = " , ".join(
                                ast.literal_eval(test.test_gen))

                        bid_obj = UserBids.objects.filter(
                            fk_test_lot_id=lot_id, bid_status="Pending").order_by('-id')

                        a = 0
                        num = 0
                        for i in bid_obj:
                            price = i.bid_Price
                            num += 1
                            a = a+price

                        try:
                            ave_value = a/num
                            print(ave_value)
                        except ZeroDivisionError:
                            ave_value = 0

                        approved_bid_obj = UserBids.objects.get(Q(fk_test_lot_id=lot_id, bid_status="Approved") | Q(fk_test_lot_id=lot_id, bid_status="Result_Upload_By_Bidder")) if UserBids.objects.filter(
                            Q(fk_test_lot_id=lot_id, bid_status="Approved") | Q(fk_test_lot_id=lot_id, bid_status="Result_Upload_By_Bidder")).exists() else None

                        recent_bid_obj = UserBids.objects.filter(fk_test_lot_id=lot_id, bid_status="Cancelled") if UserBids.objects.filter(
                            fk_test_lot_id=lot_id, bid_status="Cancelled").exists() else None

                        bidcount = bid_obj.count()


                    context = {
                        "user_obj": user_obj,
                        "test_lot_obj": test_lot_obj,
                        "bid_obj": bid_obj,
                        "bidcount": bidcount,
                        "ave_value": ave_value,
                        # "approved_bid": approved_bid_obj,
                        # "recent_bid_obj": recent_bid_obj
                    }

                    send_data = render_to_string(
                        'user_rts/rts_bid_auctioner_side.html', context)
                else:

                    send_data = {"msg": "User Not Exist"}
            else:
                send_data = {"msg": "Request Not Post"}
        else:
            send_data = {"msg": "User Not Exist"}
    except:
        print(traceback.format_exc())
        send_data = {"msg": "Something Went Wrong",
                     "staus": "0", "error": traceback.format_exc()}
    return HttpResponse(send_data)







############  Function Use For Show Recived Bid ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_recived_bids(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            lotid = data['lotid']

            recived_bids = UserBids.objects.filter(
                fk_test_lot_id=lotid).order_by('-id')

            context = {
                "recived_bids": recived_bids
            }

            send_data = render_to_string('user_rts/recived_bid.html', context)
            return HttpResponse(send_data)
        else:
            return redirect('landing_page')

    except:
        print(traceback.format_exc())
        return redirect('landing_page')
