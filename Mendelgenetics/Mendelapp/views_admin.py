import ast
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.template.loader import get_template, render_to_string
import json, random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
import traceback

from requests import delete
from .models import *
from django.db.models import Q
from datetime import datetime
from .views import *
import yaml



############  Function Use For Admin Login ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_user_login(request):
    session_id = request.session.get('admin_user_id')
    try:
        
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            username = data['username']
            password = data['password']
          
            if AdminUser.objects.filter(username=username, password=password).exists():
                if AdminUser.objects.get(username=username, password=password):
                    user_obj = AdminUser.objects.get(username=username, password=password)
                    request.session['admin_user_id'] = str(user_obj.id)
                    request.session['user_name'] = str(user_obj.username)
                    send_data = {"status": "1","msg": "User Login Successfully", "obj": user_obj.id}
                else:
                    send_data = {"status": "0", "msg": "Invalid Credential"}
            else:
                print('in else')
                send_data = {"status": "0", "msg": "User Not Exist"}
        else:
            print(session_id)
            if session_id:
                return redirect('pending_test')
            else:    
                return render(request, 'admin/admin_login.html', {"user_obj": session_id})
    except:       
        print(traceback.format_exc())
        send_data = {"status": "0", "msg": "Something Went wrong", "error": str(traceback.format_exc())}

        return redirect('landing_page')
    return JsonResponse(send_data)






############  Function Use For Admin Logout ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_user_logout(request):
    try:
        del request.session['admin_user_id']
    
        return redirect('admin_user_login')
    except:
        return redirect('admin_user_login')






############  Function Use For Render Dashboard Page ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    session_id = request.session.get('admin_user_id')
    
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






############  Function Use For Show Corporate  User To Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_corprate_user_to_admin(request):
    try:
        session_id = request.session.get('admin_user_id')
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






############  Function Use For Show Individual  User To Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def show_individual_user_to_admin(request):
    session_id = request.session.get('admin_user_id')
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






############  Function Use To Show Pending Test To Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pending_test(request):
    try:
        session_id = request.session.get('admin_user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)
                all_test_obj = UserTest.objects.filter(status="Pending").order_by('-id')
                
                context = {
                    "user_obj": user_obj,
                    "all_test_obj": all_test_obj,
                }
                return render(request,'admin/show-pending-test.html',context)
            else:
                return redirect('landing_page')
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc()) 








############  Function Use To Show Published Test To Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def published_test(request):
    try:
        session_id = request.session.get('admin_user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.get(id=session_id)
            
                # published_test_obj = TestLots.objects.filter(Q(lot_status="Published") | Q(lot_status="Approved")).order_by('-id')
                published_test_obj = TestLots.objects.filter(lot_status="Published").order_by('-id')
              
                for i in published_test_obj: 
                    i.bid_count = UserBids.objects.filter(fk_test_lot__id = i.id).count()
 
    
                context = {
                    "user_obj": user_obj,
                    "published_test_obj": published_test_obj,
                }
                return render(request, 'admin/show-published-test.html', context)
            else:
                return render(request, 'admin/show-published-test.html.html', context)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())






############  Function Use To Show Confirm Test To Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def uploaded_result_test(request):
    
    try:
        session_id = request.session.get('admin_user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.filter(id=session_id)

                uploaded_result_obj = TestLots.objects.filter(lot_status="Completed").order_by('-id')
            
                for test in uploaded_result_obj:
                    if UserBids.objects.filter(fk_test_lot_id=test.id).exists():

                        test.bid_count = UserBids.objects.filter(fk_test_lot_id=test.id).count()
                        test.bidder_name = UserBids.objects.filter(
                            fk_test_lot_id=test.id, bid_status="Result_Upload_By_Bidder")
                        
                        for i in test.bidder_name:
                            print(i.fk_user_master.name)
                    else:
                        pass

                context = {
                    "user_obj": user_obj,
                    "uploaded_result_obj": uploaded_result_obj,
                    
                     }
                return render(request, 'admin/uploaded_test.html', context)
            else:
                return render(request, 'admin/uploaded_test.html', context)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())







############  Function Use To Show Conmpleted Test To Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def completed_test(request):
    try:
        session_id = request.session.get('admin_user_id')
        if session_id:
            if AdminUser.objects.filter(id=session_id).exists():
                user_obj = AdminUser.objects.filter(id=session_id)

                comfirmed_test_obj = TestLots.objects.filter(lot_status="Approved").order_by('-id')
                for test in comfirmed_test_obj:
                    if UserBids.objects.filter(fk_test_lot_id=test.id).exists():

                        test.bid_count = UserBids.objects.filter(fk_test_lot_id=test.id).count()
                        test.bidder_name = UserBids.objects.filter(fk_test_lot_id=test.id, bid_status="Approved")

                        for i in test.bidder_name:
                            print(i.fk_user_master.name)
                    else:
                        pass

                context = {
                    "user_obj": user_obj,
                    "comfirmed_test_obj": comfirmed_test_obj,

                }
                return render(request, 'admin/test_completed.html', context)
            else:
                return render(request, 'admin/test_completed.html', context)
        else:
            return redirect('landing_page')
    except:
        print(traceback.format_exc())






############  Function Use To Create Lot By  Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_lot_of_test_from_admin(request):
    try:
        if request.method =="POST":
            data = json.loads(request.body.decode('utf-8'))
            testlot = data['testlot'] 


            for i in testlot:
                path_list = []
                gen_list = []
                
                for k in i['lot_tests']:
                    path_list.append(UserTest.objects.get(id=k).fk_sample_master.pathalogy)
                    gen_list.append(UserTest.objects.get(id=k).fk_sample_master.gens)
                    
                    UserTest.objects.filter(id=k).update(status="Active")
                # lot_id = 'AA' + str(random.randint(1000000, 9999999))  # code for genrate auction id

            
                
                lot_obj = TestLots.objects.create(fk_user_master_id=i['user_id'], tests_in_lot=i['lot_tests'], test_group=i['group_id'], test_pathalogy=path_list,  lot_status="Published",  test_quantity=len(i['lot_tests']), test_gen=gen_list, created_date_time=datetime.now())

                lot_obj.test_lot_id = f"AA{lot_obj.id:06d}"
                lot_obj.save()

            send_data = {'msg': "Lot created succesfully", 'status': "1"}
        else:
            send_data = {'msg':"Request is not post",'status':"0"}

    except:
        send_data = {'msg':"Something went wrong",'status':"0","error":traceback.format_exc()}
        print(traceback.format_exc())
    return JsonResponse(send_data)





############  Function Use To Reject The Test By  Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def test_reject_by_admin(request):
    session_id = request.session.get('admin_user_id')
    try:
        session_id = request.session.get('user_id')
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            test_id = data['test_id']
            
            rejected_test_obj = UserTest.objects.filter(Q(id__in=test_id) & Q(fk_user__id__in=user_id)).update(status="Cancelled",rejected_reason = "Test rejected by Admin")
        

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






############  Function Use To Delete The Test By  Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def test_delete_by_admin(request):
    session_id = request.session.get('admin_user_id')
    try:
       
        session_id = request.session.get('user_id')
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            user_id = data['user_id']
            test_id = data['test_id']

            rejected_test_obj = UserTest.objects.filter(Q(id__in=test_id) & Q(fk_user__id__in=user_id)).delete()

            send_data = {"msg": "this test are rejected","status": "1"}
        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        print(traceback.format_exc())
        send_data = {"msg": "something went wrong","status": "0", "error": traceback.format_exc()}
    return JsonResponse(send_data)






############  Function Use To Upload Result  By  Admin ############
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def upload_result_by_admin(request):
    try:
        if request.method == "POST":
            # data = json.loads(request.body.decode('utf-8'))
            first_doccument = request.FILES.get('first_documet')
            second_doccument = request.FILES.get('second_documet')
            lot_id = request.POST.get('lot_id')


            TestLots.objects.filter(id=lot_id).update(upload_date_time=datetime.now(), result_upload_status="AdminUpload")

            bid_obj = UserBids.objects.get(fk_test_lot_id=lot_id, bid_status="Result_Upload_By_Bidder")
            bid_obj.bid_status="Result_Upload_By_Admin"
            bid_obj.save()
            obj = TestLots.objects.get(id=lot_id)
            if first_doccument:
                obj.admin_doc_first=first_doccument
            if second_doccument:
                obj.admin_doc_second=second_doccument
            obj.save()    
            send_data = {"msg": "Request is not post", "status": "1"}

        else:
            send_data = {"msg": "Request is not post", "status": "0"}
    except:
        send_data = {"msg": "Something went wrong",
                     "status": "0", "error": traceback.format_exc()}
        print(traceback.format_exc())
    return JsonResponse(send_data)

    





############  Function Use Support Chat View By Admin ############
def support_chat_admin(request):
    try:
        session_id = request.session.get('admin_user_id')
        if session_id:
            user_obj = AdminUser.objects.get(id=session_id)
            
            context = {
                "user_obj": user_obj
            }

            return render(request, 'admin/support_chat_admin.html', context=context)
        return redirect('/admin_user_login')
    except:
        traceback.print_exc()
    return redirect('/admin_user_login')





######### function for delete user tests ###########
@csrf_exempt
def delete_user_test(request):
    try : 
        if request.method == "POST" :
            user_id = request.POST.get('user_id')
            UserTest.objects.get(id=user_id).delete()
            return JsonResponse({'status': '1'})
        return JsonResponse({'status': '0'})
    except : 
        traceback.print_exc()
        return JsonResponse({'status': '0'})




######### function for show user tests #######
@csrf_exempt
def show_user_test(request): 
    if request.method == 'POST': 
        lot_id = request.POST.get('lot_id')  
        lot_obj = TestLots.objects.filter(id=lot_id).last()
        test_list = get_brief_path_list(lot_obj.test_pathalogy)     
        string  = render_to_string('admin/r_t_s_admin/r_t_s_show_user_publish_test.html',{"test_list": test_list}) 
        return JsonResponse({"status":'1', "string": string})
    return JsonResponse({"status":'0'}) 
 


######### function for delete user lot and tests ###########
@csrf_exempt
def delete_user_lot(request):
    try : 
        if request.method == "POST" :
            lot_id = request.POST.get('lot_id')
            lot_obj = TestLots.objects.get(id = lot_id)  
            UserTest.objects.filter(id__in = yaml.safe_load(lot_obj.tests_in_lot)).delete()
            lot_obj.delete() 
            return JsonResponse({'status': '1'})
        return JsonResponse({'status': '0'})
    except : 
        traceback.print_exc()
        return JsonResponse({'status': '0'})
 ########################