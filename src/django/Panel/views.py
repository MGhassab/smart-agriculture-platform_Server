from datetime import timedelta, datetime
from functools import reduce

from django.contrib.auth import login, REDIRECT_FIELD_NAME, logout
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView, TemplateView
from django.conf import settings
from django.db.models import Max, Min, Q, DurationField, DateField, Avg, Sum
from django.db.models import F, FloatField
from django.http import JsonResponse

from Customer import utils as customer_utils
from Customer.models import Land, Customer, TempSensor, WaterSensor, \
    SoilMoistureSensor, Spout, TrialWaterSensor, HumiditySensor

from Panel import jalali_date_convertor
from Panel.forms import SignInForm


class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)


class LogInOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)


class LogOutView(View):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(settings.LOGIN_URL)


class IndexPageView(LogInOnlyView):

    def get(self, request, *args, **kwargs):
        user = request.user
        customers = Customer.objects.all()
        customers = customers.filter(user__id=request.user.id)
        if not customers.exists():
            # TODO
            return render(request, "main/index.html")
        customer = customers[0]
        lands = customer.lands.all()
        land = lands[0]

        temps = TempSensor.objects.filter(land=land).order_by('created').filter(temp_value__gt=0)

        if temps.exists():
            temp_value = temps[0].temp_value
        else:
            temp_value = 0

        waters = WaterSensor.objects.filter(land=land).exclude(created_string__isnull=True)\
            .filter(water_value__gt=0).order_by('-created')

        if waters.exists():
            water_value = waters[0].water_value
        else:
            water_value = 0

        soils = SoilMoistureSensor.objects.filter(land=land).exclude(created_string__isnull=True)\
            .filter(soil_moisture_value__gte=0).order_by('created')
        if soils.exists():
            soil_value = soils[0].soil_moisture_value
        else:
            soil_value = 0

        trial_waters = TrialWaterSensor.objects.filter(land=land).order_by('-created').filter(trial_water_value__gt=0)

        humidity = HumiditySensor.objects.filter(land=land).order_by('created').filter()

        if humidity.exists():
            today_humidity = humidity[0].humidity_value
        else:
            today_humidity = 0

        right_now = customer_utils.get_current_time()

        today = customer_utils.start_of_day(right_now)

        min_max_temp = temps.exclude(created_string__isnull=True).order_by() \
            .values(date=F('created_string'),

                    ) \
            .annotate(max_temp=Max(F('temp_value'), output_field=FloatField()),
                      min_temp=Min(F('temp_value'), output_field=FloatField()),
                      ) \
            .order_by('-date')
        total_gdd = 0.0\

        for temp in min_max_temp:
            total_gdd += max((min(30.0, temp['max_temp']) + min(30.0, temp['min_temp'])) / 2.0, 10.0) - 10

        avg_soils = soils.exclude(created_string__isnull=True).order_by() \
            .values(date=F('created_string'),
            ) \
            .annotate(avg_soil_moisture=((3.3 - Avg(F('soil_moisture_value'), output_field=FloatField())) / 3.3) * 100) \
            .order_by('-date')
        avg_humiditys = humidity.exclude(created_string__isnull=True) \
            .values(
                date=F('created_string'),
            ) \
            .annotate(avg_humidity=Avg(F('humidity_value'), output_field=FloatField())) \
            .order_by('-date')

        day = today.date()
        # daystr = customer_utils.date_to_string(day)
        week_values = {}
        for i in range(0, 7 * 9):
            day = today - timezone.timedelta(days=i)
            next_day = day + timezone.timedelta(days=1)
            pweekday = customer_utils.get_persian_week_day(day.weekday())
            j_day = jalali_date_convertor.gregorian_to_jalali(gy=day.year, gm=day.month, gd=day.day)
            today_gdd = total_gdd
            if min_max_temp.filter(date=customer_utils.date_to_string(day)).exists():
                record = min_max_temp.filter(date=customer_utils.date_to_string(day))[0]
                max_temp = record['max_temp']
                min_temp = record['min_temp']
                total_gdd -= max((min(30.0, temp['max_temp']) + min(30.0, temp['min_temp'])) / 2.0, 10.0) - 10
            else:
                max_temp = 0
                min_temp = 0

            if avg_soils.filter(date=customer_utils.date_to_string(day)).exists():
                record = avg_soils.filter(date=customer_utils.date_to_string(day))[0]
                avg_soil = record['avg_soil_moisture']
            else:
                avg_soil = 0

            filtered_waters = waters.filter(created__lte=next_day)
            if filtered_waters.exists():
                record = filtered_waters[0]
                last_water = record.water_value * 10000 / 10 / land.area
            else:
                last_water = 0

            filtered_trial_wates = trial_waters.filter(created__lte=next_day)
            if filtered_trial_wates.exists():
                record = filtered_trial_wates[0]
                last_trial_water = (record.trial_water_value * 10000 / 10 / land.area) * 0.5
            else:
                last_trial_water = 0

            if avg_humiditys.filter(date=customer_utils.date_to_string(day)).exists():
                record = avg_humiditys.filter(date=customer_utils.date_to_string(day))[0]
                avg_humidity = record['avg_humidity']
            else:
                avg_humidity = 0

            week_values[i] = {
                'jalali_date': j_day,
                'weekday': pweekday,
                'max_temp': round(max_temp, 2),
                'min_temp': round(min_temp, 2),
                'avg_soil_moisture': round(avg_soil, 2),
                'last_water': round(last_water, 2),
                'last_trial_water': round(last_trial_water, 2),
                'gdd': round(today_gdd, 2),
                'avg_humidity': round(avg_humidity, 2),
            }

        daily_values = {}
        time = right_now
        period = timezone.timedelta(minutes=5)
        for i in range(0, 24 * 12):
            period_soils = soils.filter(created__gt=time - period).filter(created__lt=time)
            if (period_soils.exists()):
                record_value = period_soils[0].soil_moisture_value
            else:
                record = soils.filter(created__lt=time).order_by('-created').first()
                record_value = record.soil_moisture_value if record else 0
                # if soils.filter(created__lt=time).order_by('-created').exits():
                #     record_value = soils.filter(created__lt=time).order_by('-created')[0].soil_moisture_value
                # else:
                #     record_value = 0
            jalaliTime = jalali_date_convertor.gregorian_to_jalali(gy=time.year, gm=time.month, gd=time.day)
            daily_values[i] = {
                0: round(customer_utils.soil_percentage(record_value), 2),
                1: jalaliTime[0],
                2: jalaliTime[1],
                3: jalaliTime[2],
                4: time.hour,
                5: time.minute,
            }
            time = time - period
        if week_values[0]['last_water'] > 0:
            today_water = (week_values[0]['last_water'] - week_values[1]['last_water']) * land.area * 10 / 10000
        else:
            today_water = (week_values[1]['last_water'] - week_values[2]['last_water']) * land.area * 10 / 10000
        if today_water < 0:
            today_water = 0

        spouts = Spout.objects.filter(device__land=land)
        spouts_condition = {}
        for spout in spouts:
            spouts_condition[spout.number] = {"is_on": spout.isOn}

        context = {
            'land': land,
            'temp_value': str(round(temp_value, 2)),
            'water_value': str(float(water_value)),
            'soil_value': str(round(soil_value, 2)),
            'week_values': week_values,
            'today_water': str(today_water),
            'spouts_condition': spouts_condition,
            'today_humidity': str(round(today_humidity, 2)),
            'daily_values': daily_values,
        }
        return render(request, "main/index.html", context=context)


def date_equal_to_record(day, record):
    return day.day == record['day'] and day.month == record['month'] and day.year == record['year']


class BlankView(TemplateView):
    template_name = 'panel/503.html'


class LogInView(GuestOnlyView, FormView):
    template_name = 'panel/log_in.html'

    @staticmethod
    def get_form_class(**kwargs):
        return SignInForm
    #     if settings.DISABLE_USERNAME or settings.LOGIN_VIA_EMAIL:
    #         return SignInViaEmailForm
    #
    #     if settings.LOGIN_VIA_EMAIL_OR_USERNAME:
    #         return SignInViaEmailOrUsernameForm
    #
    #     return SignInViaUsernameForm

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        request = self.request

        # If the test cookie worked, go ahead and delete it since its no longer needed
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        # The default Django's "remember me" lifetime is 2 weeks and can be changed by modifying
        # the SESSION_COOKIE_AGE settings' option.
        if settings.USE_REMEMBER_ME:
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)
        login(request, form.user_cache)

        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())

        if url_is_safe:
            return redirect(redirect_to)

        return redirect(settings.LOGIN_REDIRECT_URL)


def getUserLand(user):
    customers = Customer.objects.all()
    customers = customers.filter(user__id=user.id)
    # if not customers.exists():
    #     # TODO
    #     return render(request, "main/index.html")
    customer = customers[0]
    lands = customer.lands.all()
    return lands[0]


class SensorsLastValuesView(LogInOnlyView):

    def get(self, request, *args, **kwargs):
        land = getUserLand(request.user)

        soils = SoilMoistureSensor.objects.filter(land=land).order_by('-created')
        if soils.exists():
            last_soil = soils[0]
        else:
            last_soil = 0  # TODO: raise error
        created_date = last_soil.created
        # date = Date(last_soil.created)
        update_values = [{
            "last_soil": {
                "value": round(customer_utils.soil_percentage(last_soil.soil_moisture_value), 2),
                "created": str(last_soil.created),
                "jalali_created": jalali_date_convertor.gregorian_to_jalali(created_date.year,created_date.month,created_date.day),
                # "hours_created": created_date.strftime('%m-%d-%y %H:%M:%S')
            },
        }]

        return JsonResponse(update_values, safe=False)

