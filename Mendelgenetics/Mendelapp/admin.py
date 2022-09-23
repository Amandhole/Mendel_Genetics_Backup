from django.contrib import admin

from .models import *

# Register your models here.


# admin.site.register(admin)

from django.contrib import admin
from .models import *


class UserMasterClass(admin.ModelAdmin):
	list_display = ('id', 'name', 'email', 'mobile_no',
	                'is_individual', 'is_corporate')


admin.site.register(UserMaster, UserMasterClass)


class UserTestClass(admin.ModelAdmin):
	list_display = ('id', 'Contact_person_name',  'patient_test',
	                'test_requested', 'doctor_name', 'status', 'rejected_reason' ,'date')

admin.site.register(UserTest, UserTestClass)


class CountryMasterClass(admin.ModelAdmin):
	list_display = ('id', 'sortname', 'name', 'phonecode')


admin.site.register(CountryMaster, CountryMasterClass)


class StateMasterclass(admin.ModelAdmin):
	list_display = ('id', 'name', 'country_id')


admin.site.register(StateMaster, StateMasterclass)


class CityMasterClass(admin.ModelAdmin):
	list_display = ('id', 'name', 'state_id')


admin.site.register(CityMaster, CityMasterClass)


class UserBidsClass(admin.ModelAdmin):
	list_display = ('id', 'bid_Price', 'expect_result_date', 'checkbox')

admin.site.register(UserBids, UserBidsClass)

#


class SampleTestMasterClass(admin.ModelAdmin):
	list_display = ('id', 'group', 'plazo', 'pathalogy',
	                'gens', 'group', 'sample_type', 'transport')

admin.site.register(SampleTestMaster, SampleTestMasterClass)


class AdminUserClass(admin.ModelAdmin):
	list_display = ('id', 'name', 'username', 'password')
	
admin.site.register(AdminUser, AdminUserClass)


class TestLotsClass(admin.ModelAdmin):
	list_display = ('id', 'test_lot_id', 'tests_in_lot','test_group',
	                'test_pathalogy', 'test_gen','test_quantity', 'lot_status')

admin.site.register(TestLots, TestLotsClass)
