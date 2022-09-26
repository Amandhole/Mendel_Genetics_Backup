from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.template.loader import get_template, render_to_string
import json, random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
import traceback
from .models import *
from django.db.models import Q
from datetime import datetime

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_user_login(request):
    session_id = request.session.get('user_id')
    try:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            username = data['username']
            password = data['password']
          
            if AdminUser.objects.filter(username=username, password=password).exists():
                if AdminUser.objects.get(username=username, password=password):
                    user_obj = AdminUser.objects.get(username=username, password=password)
                    request.session['user_id'] = str(user_obj.id)
                    request.session['user_name'] = str(user_obj.username)
                    send_data = {"status": "1","msg": "User Login Successfully", "obj": user_obj.id}
                else:
                    send_data = {"status": "0", "msg": "Invalid Credential"}
            else:
                print('in else')
                send_data = {"status": "0", "msg": "User Not Exist"}
        else:
            session_id = request.session.get('user_id')
            if session_id:
                return redirect('user_profile_page')
            else:
                print('request not post')
                return render(request, 'admin/login.html', {"session_id": session_id})
    except:
        send_data = {"status": "0", "msg": "Something Went wrong", "error": str(traceback.format_exc())}

        print(traceback.format_exc())
        return redirect('landing_page')
    return JsonResponse(send_data)



@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    session_id = request.session.get('user_id')
    try:
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)
                context = {
                "user_obj": user_obj,            
                }
    except:
        print(traceback.format_exc())
        return redirect('landing_page')
    return render(request, 'admin/admin-dashboard.html', context)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_corprate_user_to_admin(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)

                corporate_user = UserMaster.objects.filter(is_corporate=True)
            context = {
                "user_obj": user_obj, 
                "corporate_user": corporate_user
                }
    except:
        print(traceback.format_exc())
        return redirect('landing_page')
    return render(request, 'admin/corporate-user.html', context)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_individual_user_to_admin(request):
    session_id = request.session.get('user_id')
    try:
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)
                individual_user = UserMaster.objects.filter(is_individual=True)
            else:
                return redirect('landing_page')
            context = {
                "user_obj": user_obj,
                "individual_user": individual_user
            }
        else:
            return redirect('landing_page')    
    except:
        print(traceback.format_exc()) 
        return redirect('landing_page')

    return render(request, 'admin/individual-user.html', context)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pending_test(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)
                all_test_obj = UserTest.objects.filter(status="Pending").order_by('-fk_user__name')
                context = {
                    "user_obj": user_obj,
                    "all_test_obj": all_test_obj,
                }
                return render(request, 'admin/show-pending-test.html', context)
            else:
                return render(request, 'admin/show-pending-test.html.html', context)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc()) 


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def published_test(request):
    try:
        session_id = request.session.get('user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)
            
                published_test_obj = TestLots.objects.filter(
                    Q(lot_status="Published") | Q(lot_status="Approved")).order_by('-fk_user_master__name')
               
                
                print('published test', published_test_obj)
    
                context = {
                    "user_obj": user_obj,
                    "published_test_obj": published_test_obj
                }
                return render(request, 'admin/show-published-test.html', context)
            else:
                return render(request, 'admin/show-published-test.html.html', context)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())



@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_lot_of_test_from_admin(request):
    try:
        if request.method =="POST":
            data = json.loads(request.body.decode('utf-8'))
            testlot = data['testlot'] 

            print(testlot)

            for i in testlot:
                path_list = []
                gen_list = []
                
                for k in i['lot_tests']:
                    path_list.append(UserTest.objects.get(id=k).fk_sample_master.pathalogy)
                    gen_list.append(UserTest.objects.get(id=k).fk_sample_master.gens)
                    
                    UserTest.objects.filter(id=k).update(status="Active")
                lot_id = 'AA' + str(random.randint(1000000, 9999999))  # code for genrate auction id
                
                # l = i['lot_tests']
                # s = [str(integer) for integer in l]
                # a_string = "".join(s)
        
                # test_id = int(a_string)

                # print(test_id)
                # print(type(test_id))
                TestLots.objects.create(fk_user_master_id=i['user_id'], test_lot_id=lot_id, tests_in_lot=i['lot_tests'], test_group=i['group_id'],

                                        test_pathalogy=path_list,  lot_status="Published",  test_quantity=len(i['lot_tests']), test_gen=gen_list, created_date_time=datetime.now())
            
            send_data = {'msg': "Lot created succesfully", 'status': "1"}
        else:
            send_data = {'msg':"Request is not post",'status':"0"}

    except:
        send_data = {'msg':"Something went wrong",'status':"0","error":traceback.format_exc()}
        print(traceback.format_exc())
    return JsonResponse(send_data)


@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def test_reject_by_admin(request):
    try:
        session_id = request.session.get('user_id')
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            test_id = data['test_id']
            
            rejected_test_obj = UserTest.objects.filter(Q(id__in=test_id) & Q(fk_user__id__in=user_id)).update(status="Cancelled",rejected_reason = "Test rejected by Admin")
            
            # for i in rejected_test_obj:
            #     i = i.status = "Cancelled"
            #     i.save()

            print('dddddddd',rejected_test_obj)

            context = {
                "rejected_test_obj": rejected_test_obj
                }
            send_data = {"msg": "this test are rejected",
                         "status": "1"}
        else:
            send_data = {"msg":"Request is not post","status":"0"}    
    except:
        print(traceback.format_exc())
        send_data = {"msg":"something went wrong", "status":"0","error":traceback.format_exc()}
    return JsonResponse(send_data)