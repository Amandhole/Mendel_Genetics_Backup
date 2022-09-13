from django.conf import settings
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.shortcuts import redirect, render
from html2text import pad_tables_in_text
from numpy import append
from requests import request
from .models import *
import json
from django.http import HttpResponse, JsonResponse
import traceback
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from datetime import datetime
from django.views.decorators.cache import cache_control

from django.template.loader import get_template, render_to_string
import csv

# Create your views here.
# send message to number extends



def send_sms_web(mobile_no, message_body):
    try:
        account_sid = 'AC5866debd310e650176e0ebb6660a5069'

        auth_token = 'd9d2de0c67f3af8d26be476a7677f5b4'
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_='++12056513141',
            body=message_body,
            to=mobile_no)
        print(message.sid)
        print('sent sms on this number 9766281848')
        return "success"
    except Exception as e:
        return "error"


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def landing_page(request):
    return render(request, 'landing-page.html')


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_signup(request):
    try :
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
                user_obj = UserMaster(name=name, email=email,  password=password, created_datime=datetime.now())      # Remove the mobile no and address fields from signup Page 
                if user_type == 'Corporate':
                    user_obj.is_corporate = True

                elif user_type == "Individual":
                    user_obj.is_individual = True

                user_obj.save()
                send_data = {'status': "1", 'msg': "Account created Successful", 'user_id': str(user_obj.id)}
            return JsonResponse(send_data)
        else:
            return render(request, "signup.html")
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",'error': str(traceback.format_exc())}
        return redirect('landing_page')

    return JsonResponse(send_data)
        

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
            print(email)
            print(password)
            print(user_type)

            print(type(password))

            if UserMaster.objects.filter(email=email, password=password).exists():

                obj = UserMaster.objects.get(email=email, password=password)

                request.session['user_id'] = str(obj.id)
                request.session['user_name'] = str(obj.email)

                if user_type == "Individual":
                    if obj.is_individual:
                        send_data = {
                            "status": "1", "msg": "individual Login succesfull", "obj": obj.id}
                        return JsonResponse(send_data)
                    else:
                        send_data = {"status": "0",
                                     "msg": "Invalid credential", "obj": obj.id}
                        return JsonResponse(send_data)

                elif user_type == "Corporate":

                    if obj.is_corporate:
                        send_data = {
                            "status": "2", "msg": "Corporate Login succesfull", "obj": obj.id}


                        print('in login function 1111111111111111111111111111111111111111111111111111')   
                        return JsonResponse(send_data)
                    else:
                        send_data = {"status": "0",
                                     "msg": "Invalid credential", "obj": obj.id}
                        return JsonResponse(send_data)
            else:
                print('in else')
                data = {"status": "0", "msg": "invalid credential"}
                print(data)
                return JsonResponse(data)
        else:
            session_id = request.session.get('user_id')
            if session_id:  
                return redirect('user_profile_page')
            else:
                print('request not post')
                return render(request, 'login.html', {"session_id": session_id})
    except:
        send_data = {"status": "0", "msg": "Invalid credential",
                     "error": str(traceback.format_exc())}
        return redirect('landing_page')
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlogout(request):
    try:
        del request.session['user_id']
        print('deleting session')
        return redirect('login_page')
    except:
        return redirect('login_page')


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_otp_for_signup_verification(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data['email_id']
        # mobile_no = data['mobile_no']

        if UserMaster.objects.filter(email=email).exists():
            send_data = {'status': "2", 'msg': "Email Already Exists"}
        # elif UserMaster.objects.filter(mobile_no=mobile_no).exists():
            # send_data = {'status': "2", 'msg': "Mobile Already Exists"}
        else:
            # email_otp = str(random.randint(100000, 999999))
            email_otp = '123456'

            message = email_otp+" is your otp for varification."
            # status = send_sms_web(mobile_no, message)
            print(email_otp)
            

            send_data = {'status': "1",'msg': "OTP Sent Successfully", 'Email_OTP': email_otp}

    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)


@ csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def forget_password_OTP(request):

    session_id = request.session.get('user_id')
    print('creating session', session_id)
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            email = data['email_id']

            if UserMaster.objects.filter(email=email).exists():

                # email_otp = str(random.randint(100000, 999999))
                email_otp = '123456'
                print(email_otp)

                send_data = {
                    'status': "1", 'msg': "OTP Sent succesfully", "email_otp": email_otp}

                return JsonResponse(send_data)
            else:
                send_data = {'status': "0", 'msg': "Email Not Exists"}
                return JsonResponse(send_data)
        else:
            return render(request, 'forget-pasword.html')
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
        return redirect('landing_page')

    return JsonResponse(send_data)


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


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_profile_page(request):

    session_id = request.session.get('user_id')
    print(session_id)
    try:
        if session_id:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)

                # print('user_obj', user_obj.user_image.url)
                print(user_obj.name, user_obj.email, user_obj.mobile_no, user_obj.address_line1,
                      user_obj.password, user_obj.is_individual, user_obj.is_corporate, user_obj.created_datime)
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
                    print('in if oo')

                elif tgl_btn_value == 0:
                    obj.auc_bid_status = False
                    obj.save()
                    print('in else ifllllllpppppppppppppppppppppppppl')

                send_data = {'status': '1', 'msg': "Field Toggle Succesfully"}

            else:
                send_data = {'status': '0', 'msg': "User Not Found"}

        else:
            send_data = {'status': '0', 'msg': "Request Not Post"}
    except:
        send_data = {'status': '0', 'msg': "Something Went Wrong",
                     'error': traceback.format_exc()}             
    return JsonResponse(send_data)


# function for get the state list of country

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_state_of_country(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        country_id = data['country_id']
        print(country_id)
            
        if request.method == "POST":
    
            state_obj = StateMaster.objects.filter(country_id=country_id)
        
            

            send_data = {'status': "1", 'msg': "Got States Of Country", "state_obj": list(state_obj.values())}  # json object not serilizable

        else:
            
            send_data = {'status': "0", 'msg': "Request Is Not Post"}
    except:
        
        send_data = {'status': "0", 'msg': "Something Went Wrong","error": traceback(traceback.format_exc())}
  
    return JsonResponse(send_data)


@csrf_exempt
def get_city_of_state(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        state_id = data['state_id']
        print(state_id)

        if request.method == "POST":

            city_obj = CityMaster.objects.filter(state_id=state_id)
            print(city_obj)

            send_data = {'status': "1", 'msg': "Got city Of State",
                         "city_obj": list(city_obj.values())}

        else:
            send_data = {'status': "0", 'msg': "Request Is Not Post"}
    except:
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     "error": traceback(traceback.format_exc())}
    return JsonResponse(send_data)


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

                # print('ttttttttttt', user_id, profile_pic)
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


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_user_proifle_page(request):
    try :
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

        print('aaaaaaaaabbbbbbbbbbccccccccc',address)

        if UserMaster.objects.filter(id=user_id).exists():
            user_obj = UserMaster.objects.get(id=user_id)
            user_obj.name = name
            user_obj.mobile_no = mobile
            user_obj.address_line1 = address

            if country == "Select Country":
                user_obj.country = "----"
            else:
                user_obj.country = country

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
            user_obj.save()

            send_data = {'status': "1",
                         'msg': "Profile Updated successfully"}
        else:
            send_data = {'status': "0", 'msg': "User Id Not Exists"}
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_user_email_send_otp(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            email = data['email']

            if UserMaster.objects.filter(id=user_id, email=email).exists():
                # email_otp = str(random.randint(100000, 999999))
                email_otp = '123456'
                print(email_otp)

                send_data = {'status': "1",
                             'msg': "OTP Sent To Register Email", "email_otp": email_otp}
            else:

                send_data = {'status': "0", 'msg': "User Not Exists"}
        else:
            send_data = {'status': "0", 'msg': "Request is not post"}
    except:
        print(str(traceback.format_exc()))
        send_data = {'status': "0", 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_users_new_email_address(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            old_email = data['old_email']
            new_email = data['new_email']

            print(old_email)
            print(new_email)
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


#  Add test by user
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

            test_requested = data['test_requested']
            background_data = data['background_data']
            patient_test = data['patient_test']
            weight_unit = data['weight_unit']
            height_unit = data['height_unit']
            format_data = '%m-%d-%Y'

            print(patient_test, 'dsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
            converted_date = datetime.strptime(datepicker, format_data)
            # strfdate = converted_date.strftime("%Y-%m-%d %H:%M:%S")

            if UserMaster.objects.filter(id=user_id).exists():
                user_obj = UserMaster.objects.get(id=user_id)
                test_obj = UserTest(fk_user_id=user_id,  patient_first_name=first_name, patient_last_name=last_name,
                                    patient_age = patient_age, patient_race = patient_race, 
                                    patient_gender = gender, patient_weight = patient_weight,
                                    patient_height=patient_height, doctor_name=dr_name, date = converted_date,
                                    Centre = center ,Email = Email , other_way = other_way, test_requested = test_requested,
                                    background_data=background_data, patient_test=patient_test, weight_unit=weight_unit, height_unit=height_unit, Contact_person_name=Contact_person_name, status="Active", created_date_time=datetime.now())

                test_obj.save()

                send_data = {'status': "1", 'msg': "Test Added Succesfully"}
            else:
                send_data = {'status': "0", "msg": "User Not found"}
        else:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)

            context = {
                "user_obj": user_obj
            }
            return render(request, 'post-test.html', context)
    except:
        send_data = {'status': '0', 'msg': "Something Went Wrong",
                     'error': str(traceback.format_exc())}
        return redirect('landing_page')
    return JsonResponse(send_data)


# get test list of perticular user
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def test_added_by_user_list(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:

            today = datetime.today()
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)

                # test_obj = UserTest.objects.filter(fk_user_id=session_id, date__gte = today).order_by('-id') # for active test
                test_obj = UserTest.objects.filter( fk_user_id=session_id, status="Active").order_by('-id')
                for i in test_obj:
                    i.bid_count = UserBids.objects.filter(fk_user_test_id = i.id).count()
              
                
                Confirm_test_obj = UserTest.objects.filter( fk_user_id=session_id, status="Confirm").order_by('-id')
                for i in Confirm_test_obj:
                    i.bid_count = UserBids.objects.filter(fk_user_test_id = i.id).count()

                
                
                # expire_test_obj = UserTest.objects.filter(fk_user_id=session_id , date__lt = today).order_by('-id')   # expired test
                # print('expired test obj',expire_test_obj)

                context = {
                        
                        "user_obj": user_obj,
                        "test_obj": test_obj,
                        "Confirm_test_obj":Confirm_test_obj
                        # 'expire_test_obj': expire_test_obj
                            }
                return render(request, 'posted-test.html',context)
        else:            
            return redirect('landing_page')

    except:
        print(traceback.format_exc())
        return redirect('landing_page')


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def posted_test_delete_by_user(request):
    try:
        if request.method == "POST":

            data = json.loads(request.body.decode('utf-8'))
            test_id = data['test_id']

            if UserTest.objects.filter(id=test_id).exists():
                test_obj = UserTest.objects.get(id=test_id)
                test_obj.delete()

                send_data = {'status': '1', "msg": "Test Deleted Succusfully"}
            else:
                send_data = {'status': '1', "msg": "Test Does Not Exist"}
        else:
            send_data = {'status': '0', "msg": "Request Is Not Post"}
    except:
        send_data = {'status': '0', "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def posted_test_edit_by_user(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            test_id = data['test_id']
            firstname = data['firstname']
            lastname = data['lastname']
            patientage = data['patientage']
            patientrace = data['patientrace']
            selectgender = data['selectgender']
            patientweight = data['patientweight']


            patientheight = data['patientheight']
            drname = data['drname']
            datepicker = data['datepicker']
            centre = data['centre']
            email = data['email']
            otherway = data['otherway']
            contact_pereson = data['contact_pereson']
            patient_test = data['patienttest']

            testrequested = data['testrequested']
            backgrounddata = data['backgrounddata']

            weight_unit = data['weight_unit']
            height_unit = data['height_unit']

            if UserTest.objects.filter(id=test_id).exists():
                test_obj = UserTest.objects.get(id=test_id)

                converted_date = datetime.strptime(datepicker, "%m-%d-%Y")

                test_obj.patient_first_name = firstname
                test_obj.patient_last_name = lastname
                test_obj.patient_age = patientage
                test_obj.patient_race = patientrace
                test_obj.patient_gender = selectgender
                test_obj.patient_weight = patientweight
                test_obj.Contact_person_name =  contact_pereson
                test_obj.patient_height = patientheight
                test_obj.doctor_name = drname
                test_obj.date = converted_date
                test_obj.Centre = centre
                test_obj.Email = email
                test_obj.other_way = otherway
                test_obj.patient_test = patient_test
                test_obj.test_requested = testrequested
                test_obj.background_data = backgrounddata
                test_obj.weight_unit = weight_unit
                test_obj.height_unit = height_unit

                test_obj.save()
                send_data = {'status': '1', "msg": "Test Updated Succesfully"}

            else:
                send_data = {'status': '0', "msg": "Test Not Exists"}
        else:
            send_data = {'status': '0', "msg": "Request Is Not Post"}
    except:
        send_data = {'status': '0', "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
    return JsonResponse(send_data)


# get test list of all user except current user
# @csrf_exempt
# def All_test_list_exclude_current_user(request):

#     try:
#         data = json.loads(request.body.decode('utf-8'))
#         user_id = data['user_id']
#         test_dict = {}
#         test_list = []
#         if request.method == "POST":
#             if UserMaster.objects.filter(id = user_id).exists():
#                 tets_obj = UserTest.objects.filter(test_status="Pending").exclude(fk_user_id = user_id)
#                 for i in tets_obj:
#                     test_dict['test_id'] = str(i.id) if i.id else ""
#                     test_dict ['fk_user_id'] = str(i.fk_user_id) if i.fk_user_id else ""
#                     test_dict['test_title'] = str(i.test_title) if i.test_title else ""
#                     test_dict['test_detail'] =  str(i.test_detail) if i.test_detail else ""
#                     test_dict['charges'] = str(i.charges) if i.charges else ""
#                     test_dict['pickup_address'] = str(i.pickup_address) if i.pickup_address else ""
#                     test_dict['created_time']= str(i.created_time) if i.created_time else ""
#                     test_list.append(test_dict)
#                     test_dict = {}
#                     # print('empty dictionary',test_dict)
#                     # print(test_list)
#                 send_data = {'status' :'1' , 'msg' : 'Test List of All User Except Current User','test_list' : test_list}
#             else:
#                 send_data = {'status':'0' , 'msg' : 'User Not Found' }
#         else:
#             send_data = {'status':'0' , 'msg' : 'Request Not Post' }
#     except:
#         send_data = {'status' : '0' , 'msg' : 'Something Went Wrong' , 'error': str(traceback.format_exc())}
#     return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def All_test_list_exclude_current_user(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            print(session_id)
            today = datetime.today()
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)
                tets_obj = UserTest.objects.filter(status="Active").exclude(fk_user_id=session_id)

                # bid_obj = UserBids.objects.filter(fk_user_master__id = session_id)

                for test in tets_obj:
                    bids = UserBids.objects.filter(fk_user_test=test)
                    for bid in bids:
                        test.my_bid = True if bid.fk_user_master == user_obj else False
                        test.my_bid_obj = bid

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


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Show_state(request):
    try:
        country = request.POST.get('country_id')
        state = request.POST.get('state')
        city = request.POST.get('city')

        state_id = StateMaster.objects.get(name=state).id
        state = StateMaster.objects.filter(country_id=CountryMaster.objects.get(name=country).id).values()
        city_list = CityMaster.objects.filter(state_id=state_id).values()


        return JsonResponse({'status': '1', 'msg': 'Success', 'subcategory': list(state), 'citycategory': list(city_list)})
    except:
        traceback.print_exc()
        return JsonResponse({'status': '0', 'msg': 'Something went wrong.'})


# for storing data in csv file

fieldnames = ['id', 'sortname', 'name', 'phonecode']


# rows = list(CityMaster.objects.all().values())

# with open(f'{settings.BASE_DIR}/city.csv', 'w', encoding='UTF8', newline='') as f:
#     writer = csv.DictWriter(f, fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(rows)



# this code for add csv data to database file
# def add_css_data_coutnry_state_city(request):
#     print(settings.BASE_DIR)
#     with open(f'{settings.BASE_DIR}/city.csv', 'r') as f:
#         csvreader = csv.reader(f)
#         header = next(csvreader)
#         for row in csvreader:
#             CityMaster.objects.create(
#                 id=row[0], name=row[1], state_id=row[2])
#             print('done')
#             # return HttpResponse('data added succesfully')
#             print('data added succesfully')
#         return HttpResponse('data added succesfully')    






@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def User_bids_on_other_users_test(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))

            user_id = data['user_id']
            test_id = data['test_id']
            bidprice = data['bidprice']
            expect_result_date = data['expect_result']
            checkbox = data['checkbox']

            converted_date = datetime.strptime(expect_result_date, "%m-%d-%Y")
            print(user_id, test_id, bidprice, expect_result_date, checkbox)

            user_bid = UserBids(fk_user_master_id=user_id, fk_user_test_id=test_id,
                                bid_Price=bidprice, expect_result_date=converted_date, checkbox=checkbox,bid_status = "Pending")

            user_bid.save()

            send_data = {"status": "1", "msg": "Bid Added Succesfully"}
        else:
            send_data = {"status": "0", "msg": "Request Is Not Post"}
    except:
        send_data = {"status": "0", "msg": "Something Went Wrong",
                     "error": traceback.format_exc()}
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def User_edit_bids_on_other_users_test(request):
    print('===================')
    try:
        if request.method == "POST":

            data = json.loads(request.body.decode('utf-8'))

            bid_id = data['bid_id']
            bid_price = data['bid_price']
            biexpect_result_dated = data['expect_result_date']

            converted_date = datetime.strptime(
                biexpect_result_dated, "%m-%d-%Y")

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


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_all_bids_on_my_test(request):
    try :
        session_id = request.session.get('user_id')

        if session_id:
            print('-----------------------------------------------------------')
            if request.method == "POST":
                data = json.loads(request.body.decode('utf-8'))
                test_id = data['test_id']
                
                print('==================',test_id)


                if UserMaster.objects.filter(id=session_id).exists():
                    user_obj = UserMaster.objects.get(id=session_id)
                    if UserTest.objects.filter(id=test_id):
                        test_obj = UserTest.objects.get(id=test_id)
                        # print('test obj is------------', test_obj.patient_test)
                        # bid_obj = UserBids.objects.filter(fk_user_test_id = test_id)
                        
                        bid_obj = UserBids.objects.filter(fk_user_test_id = test_id,bid_status="Pending")

                        approved_bid_obj = UserBids.objects.get(fk_user_test_id=test_id, bid_status="Approved") if UserBids.objects.filter(fk_user_test_id=test_id, bid_status="Approved").exists() else None
                        # print('tttttttt', approved_bid_obj)
                        
                    
                    
                    
                        bidcount = bid_obj.count()
                        print('aaaaaaaaaaaaaaaaaaaaa',bidcount)

                    context = {
                        "user_obj": user_obj,
                        "test_obj": test_obj,
                        "bid_obj": bid_obj,
                        "approved_bid": approved_bid_obj
                    }
                    send_data = render_to_string('rts_bid_detail.html', context)
                else:
                    send_data = {"msg": "User Not Exist"}
            else:
                send_data = {"msg": "Request Not Post"}
        else :
            send_data= {"msg": "User Not Exist"}
    except:      
        send_data= {"msg": "Something Went Wrong", "staus": "0","error":traceback.format_exc()}
    return HttpResponse(send_data)    


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Approve_users_bid_on_test(request):
    try:
        if request.method =="POST":
            data = json.loads(request.body.decode('utf-8'))
            test_id = data['test_id']
            bid_id = data['bid_id']
            if UserTest.objects.filter(id=test_id):
                test_obj = UserTest.objects.get(id = test_id)
                print(test_obj.id)
                test_obj.status = "Confirm"
                test_obj.save()

                bid_obj = UserBids.objects.get(id = bid_id)
                bid_obj.bid_status = "Approved"
                bid_obj.save()

                send_data = {"msg":"Bid approved successfully","status":"1" }
            
        else:
            send_data = {"msg":"Request is not post","status":"0" }

    except:
        send_data = {"msg":"Something went wrong","status":"0" ,"error":traceback.format_exc()}
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Reject_bid_on_users_test(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            bid_id = data['bid_id']
            if UserBids.objects.filter(id=bid_id):
                bid_obj = UserBids.objects.get(id=bid_id)
                print(bid_obj.id)
                bid_obj.delete()
                send_data = {"msg": "Bid Rejected successfully", "status": "1"}

        else:
            send_data = {"msg": "Request is not post", "status": "0"}

    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
    return JsonResponse(send_data)


def my_bids_on_other_users_test(request):
    if 1 == 1:
        session_id = request.session.get('user_id')
        if session_id:
            if UserMaster.objects.filter(id=session_id).exists():
                user_obj = UserMaster.objects.get(id=session_id)

                print('my session id is',session_id)
                my_active_bid = UserBids.objects.filter( fk_user_master__id=session_id, bid_status='Pending')

                my_approved_bid = UserBids.objects.filter( fk_user_master__id=session_id, bid_status='Approved')

                # for i in my_active_bid:
                #     print(i)
                # print('my approved bid',my_approved_bid)
                # print('my active bid',my_active_bid)
                context = {            
                    "user_obj": user_obj,
                    'my_active_bid':my_active_bid,
                    'my_approved_bid': my_approved_bid
                    
                    }
                return render(request,'my-bids.html',context)                
        else:            
            return redirect('landing_page')                        
    else:
        print(traceback.format_exc())
        return redirect('landing_page')
        
