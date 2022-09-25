from django.db import models

# Create your models here.
from django.db.models.fields import CharField, DateField,  TextField


class AdminUser(models.Model):
    name = models.CharField(max_length = 50,null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length = 100,null=True, blank=True)
    


class SampleTestMaster(models.Model):
    group = models.CharField(max_length=150, null=True)
    plazo = models.CharField(max_length=150, null=True)
    pathalogy = models.CharField(max_length=150, null=True)
    gens = models.CharField(max_length=150, null=True)
    sample_type = models.CharField(max_length=150, null=True)
    transport = models.CharField(max_length=150, null=True)

    
class CountryMaster(models.Model):
    sortname = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phonecode = models.IntegerField()

    def __str__(self):
        return self.name


class StateMaster(models.Model):
    name = models.CharField(max_length=100)
    country_id = models.IntegerField()

    def __str__(self):
        return self.name


class CityMaster(models.Model):
    name = models.CharField(max_length=100)
    state_id = models.IntegerField()

    def __str__(self):
        return self.name


class UserMaster(models.Model):
    name = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, null=True,blank=True)
    user_image = models.ImageField(upload_to ='UserImage/', null=True, blank=True)
    CIF_number = models.CharField(max_length=20, unique=True, null=True)
    Landline_number = models.CharField(max_length=20, null=True,blank=True)
    # for country and state
    address_line1 = models.CharField(max_length=400, blank=True, default='')
    addres_line2 = models.CharField(max_length=400, blank=True, null=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.IntegerField(null=True)
    password = models.CharField(max_length=200)
    is_individual = models.BooleanField(default=False)
    is_corporate = models.BooleanField(default=False)
    created_datime = models.DateTimeField(null=True, blank=True)
    auc_bid_status = models.BooleanField(default=False)
    def __str__(self):
        return self.name




class UserTest(models.Model):
    fk_sample_master = models.ForeignKey(SampleTestMaster, on_delete=models.CASCADE, null=True, blank=True)
    fk_user = models.ForeignKey( UserMaster, on_delete=models.CASCADE, null=True, blank=True)

    auction_test_id = models.CharField(max_length=10, blank=True, null=True, default='')
    patient_first_name = models.CharField( max_length=200, blank=True, null=True, default='')
    patient_last_name = models.CharField( max_length=600, blank=True, null=True ,default='')
    patient_age = models.IntegerField(blank=True, null=True)
    patient_race = models.CharField(max_length=300, blank=True, null=True,default='')
    patient_gender = models.CharField(max_length=50, null=True)
    patient_weight = models.FloatField(null=True, blank=True)
    weight_unit = models.CharField(null=True, max_length=20, blank=True)
    patient_height = models.FloatField(null=True, blank=True)
    height_unit = models.CharField(null=True, max_length=20, blank=True)
    doctor_name = models.CharField(max_length=100, null=True)
    Contact_person_name = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True, blank=True)
    Centre = models.CharField(null=True, max_length=500, blank=True)
    Email = models.CharField(null=True, max_length=100, blank=True)
    other_way = models.CharField(null=True, max_length=500, blank=True)
    test_requested_type = models.CharField(null=True, max_length=3000, blank=True)
    test_requested = models.CharField(null=True, max_length=3000, blank=True)
    background_data = models.CharField(null=True, max_length=3000, blank=True)
    status = models.CharField(null=True, max_length=15, default ="Pending") #Pending Active Confirm Cancelled
    
    rejected_reason = models.CharField(null=True, max_length=300)
    # Pending  and Published  this will status will chanage when admin publish the test
    admin_action_status = models.CharField( null=True, max_length=15, default="")

    patient_test = models.CharField(null=True, max_length=200, blank=True)  # for test
    other_test = models.CharField(null=True, max_length=500, blank=True)

    created_date_time = models.DateTimeField(null=True, blank=True)
    




class TestLots(models.Model):
    fk_user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE, null=True, blank=True)
    fk_user_test = models.ForeignKey(UserTest, on_delete=models.CASCADE, null=True, blank=True)
    test_lot_id = models.CharField(max_length=10, blank=True, null=True, default='')
    tests_in_lot = models.CharField(null=True, max_length=1000, default="")
    test_group = models.CharField(null=True, max_length=1000, default="")
    test_pathalogy = models.TextField(null=True, max_length=2000, default="")
    test_gen = models.TextField(null=True, max_length=2000, default="")
    test_quantity = models.IntegerField(blank=True, null=True)
    lot_status = models.CharField(null=True, max_length=15, default="Published") #after approve bid status is Approved
    created_date_time = models.DateTimeField(null=True, blank=True)


class UserBids(models.Model):
    # foreign key to the user who bid
    fk_user_master = models.ForeignKey(UserMaster, on_delete=models.CASCADE, null=True, blank=True)
    fk_user_test = models.ForeignKey(UserTest, on_delete=models.CASCADE, null=True, blank=True)
    fk_test_lot = models.ForeignKey(TestLots, on_delete=models.CASCADE, null=True, blank=True)
    bid_Price = models.FloatField(blank=True, default='')
    expect_result_date = models.DateField(null=True, blank=True)
    checkbox = models.CharField(max_length=50, null=True)
    bid_status = models.CharField(null=True, max_length=15, default="")  # Pending Approved Cancelled
