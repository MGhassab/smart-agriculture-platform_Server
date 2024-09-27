from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from Baghyar.admin import get_linked_repr, get_linked_named_model_repr
from Device.models import LogDeviceCheckOut, DeviceNetworkCoverageLog, ExternalButtonEventSpoutChange
from Device.utils import get_last_log
from Irrigation.admin import get_linked_record_repr
from Irrigation.models import CustomerSpoutChangeRecord, ProgramSpoutChangeRecord, ProcessSpoutChangeRecord
# from . import models
from .models import Customer, Land, Spout, SpoutSensor, SmsReceiver, TempSensor, \
    HumiditySensor, SoilMoistureSensor, EvaporationSensor, WaterSensor, TrialWaterSensor, Device, ProgramGroup, \
    SubProgram, ChangeSpout
    # DailyInfos, SensorInfos

# admin.site.register(Customer)
# admin.site.register(Land)
# admin.site.register(Spout)
# admin.site.register(SpoutSensor)
# admin.site.register(Program)
# admin.site.register(models.Program)
# admin.site.register(models.Program2)
# admin.site.register(Sensor)
# admin.site.register(Device)
# admin.site.register(SmsReceiver)
# admin.site.register(TempSensor)
# admin.site.register(HumiditySensor)
# admin.site.register(SoilMoistureSensor)
# admin.site.register(DailyInfos)
# admin.site.register(SensorInfos)
# admin.site.register(EvaporationSensor)
# admin.site.register(WaterSensor)
# admin.site.register(TrialWaterSensor)
# admin.site.register(models.Device)
# admin.site.register(SubProgram)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    fields = ('name', 'serial', 'land', 'is_active', 'update_period', 'delay_to_action', 'type_number',
              'last_modified_program', 'last_modified_button')
    list_display = ('id_field', 'name', 'serial', 'land_field', 'update_period', 'delay_to_action', 'type_number',
                    'last_log',
                    # 'last_network_coverage', 'spout_1', 'spout_2', 'spout_3', 'spout_4',
                    'spouts_field',
                    'process_buttons_field', 'is_active',
                    # 'process_button_1', 'process_button_2', 'process_button_3', 'process_button_4'
                    )
    search_fields = ('id', 'name', 'land__name', 'land_id')

    def id_field(self, device: Device) -> int:
        return device.id
    id_field.short_description = 'آیدی'

    def land_field(self, device: Device) -> str:
        return get_linked_named_model_repr(device.land)
    land_field.short_description = 'زمین'

    def last_log(self, device: Device) -> str:
        try:
            log = get_last_log(device)
        except IndexError:
            return 'None'
        return get_linked_repr(log, f'{log.time}', f'{log.id}')
    last_log.short_description = 'آخرین لاگ'

    def last_network_coverage(self, device: Device):
        try:
            record = DeviceNetworkCoverageLog.objects.filter(device=device, time__lte=timezone.now())\
                .order_by('-time')[0]
        except IndexError:
            return 'None'
        return get_linked_repr(record, f'{record.value}', f'{record.id}')
    last_network_coverage.short_description = 'آخرین رکود شبکه'

    def spouts_field(self, device: Device):
        spouts = device.spouts.all()
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (spout.id, reverse(f'admin:{spout._meta.app_label}_{spout._meta.model_name}_change', args=(spout.id,)),
             f'{spout.number}-{spout.name}')
            for spout in spouts))
    spouts_field.short_description = 'شیرها'

    def process_buttons_field(self, device: Device):
        buttons = device.process_buttons.all()
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (button.id, reverse(f'admin:{button._meta.app_label}_{button._meta.model_name}_change', args=(button.id,)),
             f'{button.number}-{button.name}')
            for button in buttons))
    process_buttons_field.short_description = 'شیر‌های پروسه'


@admin.register(Spout)
class SpoutAdmin(admin.ModelAdmin):
    list_display = ('id_field', 'name', 'number', 'isOn', 'device_field', 'land_field', 'default_is_on_value',
                    'controller',
                    'modified', 'last_record_field', 'last_change_record', 'last_change_by_customer', 'last_change_by_program',
                    'last_change_by_process', 'next_change_by_program', 'next_change_by_process',
                    'is_active',
                    )
    search_fields = ('id', 'name', 'device__name', 'device__land__name')

    def id_field(self, spout: Spout) -> int:
        return spout.id
    id_field.short_description = 'آیدی'

    def device_field(self, spout: Spout):
        return get_linked_named_model_repr(spout.device)
    device_field.short_description = 'دستگاه'

    def land_field(self, spout: Spout):
        try:
            return get_linked_named_model_repr(spout.device.land)
        except AttributeError:
            return None
    land_field.short_description = 'زمین'

    def last_change_record(self, spout: Spout):
        try:
            record = spout.change_records.filter(time__lte=timezone.now()).order_by('-time')[0]
            return get_linked_record_repr(record)
        except IndexError:
            return None
    last_change_record.short_description = 'آخرین رکورد تغییر'

    def last_change_by_customer(self, spout: Spout):
        try:
            record = CustomerSpoutChangeRecord.objects.filter(spout=spout, time__lte=timezone.now()).order_by('-time')[0]
        except IndexError:
            return None
        return get_linked_record_repr(record)
    last_change_by_customer.short_description = 'آخرین تغییر مستقیم کاربر'

    def last_change_by_program(self, spout: Spout):
        try:
            record = ProgramSpoutChangeRecord.objects.filter(spout=spout, time__lte=timezone.now()).order_by('-time')[0]
        except IndexError:
            return None
        return get_linked_record_repr(record)
    last_change_by_program.short_description = 'آخرین تغییر توسط برنامه'

    def last_change_by_process(self, spout: Spout):
        try:
            record = ProcessSpoutChangeRecord.objects.filter(spout=spout, time__lte=timezone.now(),
                                                             button_record__canceled=False).order_by('-time')[0]
        except IndexError:
            return None
        return get_linked_record_repr(record)
    last_change_by_process.short_description = 'آخرین تغییر توسط دکمه‌ی پروسه'

    def next_change_by_program(self, spout: Spout):
        try:
            record = ProgramSpoutChangeRecord.objects.filter(spout=spout, time__gt=timezone.now()).order_by('time')[0]
        except IndexError:
            return None
        return get_linked_record_repr(record)
    next_change_by_program.short_description = 'اولین تغییر آینده توسط برنامه'

    def next_change_by_process(self, spout: Spout):
        try:
            record = ProcessSpoutChangeRecord.objects.filter(spout=spout, time__gt=timezone.now()).order_by('time')[0]
        except IndexError:
            return None
        return get_linked_record_repr(record)
    next_change_by_process.short_description = 'اولین تغییر آینده توسط پروسه'

    def last_record_field(self, spout: Spout):
        try:
            return get_linked_record_repr(spout.last_record)
        except AttributeError:
            return None
    last_record_field.short_description = 'آخرین رکورد اعمال شده'


@admin.register(ProgramGroup)
class ProgramGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'land_field', 'device_field', 'repeatable', 'interval', 'start', 'next_start', 'passed',
                    'events_field', 'change_spouts_field', 'last_change_time')

    def land_field(self, program_group: ProgramGroup):
        return get_linked_named_model_repr(program_group.land)
    land_field.short_description = 'زمین'

    def device_field(self, program_group: ProgramGroup):
        return get_linked_named_model_repr(program_group.device)
    device_field.short_description = 'دستگاه'

    def events_field(self, program_group: ProgramGroup):
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (event.id, reverse(f'admin:{event._meta.app_label}_{event._meta.model_name}_change', args=(event.id,)),
             f'{event.id}.{event.number}_{event.delay}')
            for event in program_group.programs.all()))
    events_field.short_description = 'رویدادها'

    def change_spouts_field(self, program_group: ProgramGroup):
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (change_spout.id, reverse(f'admin:{change_spout._meta.app_label}_{change_spout._meta.model_name}_change',
                                      args=(change_spout.id,)),
             f'{change_spout.is_on}.spout={change_spout.spout_id}.{change_spout.spout.name}'
             f'_delay={change_spout.sub_program.delay}')
            for change_spout in ChangeSpout.objects.filter(
            sub_program__program_group=program_group)))
    change_spouts_field.short_description = 'تغییر شیرها'


@admin.register(ChangeSpout)
class ChangeSpoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'spout_field', 'is_on', 'unchange', 'sub_program_field', 'program_field', 'device_field',
                    'modified', )
    search_fields = ('id', 'sub_program_id', 'spout_id')

    def spout_field(self, change_spout: ChangeSpout):
        return get_linked_named_model_repr(change_spout.spout)
    spout_field.short_description = 'شیر خروجی'

    def sub_program_field(self, change_spout: ChangeSpout):
        sub_program = change_spout.sub_program
        return get_linked_repr(sub_program, f'{sub_program.number}-{sub_program.delay}', f'{sub_program.id}')
    sub_program_field.short_description = 'رخداد برنامه'

    def program_field(self, change_spout: ChangeSpout):
        program_group = change_spout.sub_program.program_group
        return get_linked_named_model_repr(program_group)
    program_field.short_description = 'گروه برنامه'

    def device_field(self, change_spout: ChangeSpout):
        return get_linked_named_model_repr(change_spout.sub_program.program_group.device)
    device_field.short_description = 'دستگاه'


@admin.register(SmsReceiver)
class SmsReceiverAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'spout_field', )
    search_fields = ('id', 'number', 'spout_id', )

    def spout_field(self, change_spout: ChangeSpout):
        return get_linked_named_model_repr(change_spout.spout)
    spout_field.short_description = 'شیر خروجی'


@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'devices_field', 'customers_field', 'need_program_check', 'owner_field',
                    'longitude', 'latitude', 'city', 'has_advance_time', 'serial')
    search_fields = ('id', 'name', )

    def devices_field(self, land: Land):
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (device.id, reverse(f'admin:{device._meta.app_label}_{device._meta.model_name}_change', args=(device.id,)),
             f'{device.name}-type:{device.type_number}') for device in land.devices.all())
        )
    devices_field.short_description = 'دستگاه‌ها'

    def customers_field(self, land: Land):
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (customer.id, reverse(f'admin:{customer._meta.app_label}_{customer._meta.model_name}_change',
                                args=(customer.id,)),
             f'{customer.user.username}-{customer.phoneNumber}-{customer.type}') for customer in land.customers.all())
        )
    customers_field.short_description = 'مشتریان'

    def owner_field(self, land: Land):
        try:
            return get_linked_repr(land.owner, land.owner.user.username, land.owner.id)
        except AttributeError:
            return None
    owner_field.short_description = 'مالک زمین'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'username_field', 'phoneNumber', 'type', 'isBlocked', 'isActivated', 'is_admin',
                    'is_supervisor', 'has_registered_land', )
    search_fields = ('id', 'user__username', 'phoneNumber', )

    def username_field(self, customer: Customer):
        return customer.user.username
    username_field.short_description = 'کاربر'


@admin.register(SubProgram)
class SubProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'delay', 'program_group_field', 'change_spouts_field', 'modified', )
    search_fields = ('id', )

    def program_group_field(self, sub_program: SubProgram):
        return get_linked_named_model_repr(sub_program.program_group)
    program_group_field.short_description = 'برنامه'

    def change_spouts_field(self, sub_program: SubProgram):
        return format_html_join(',', '{}.<a href="{}">{}</a><br/>', (
            (change_spout.id, reverse(f'admin:{change_spout._meta.app_label}_{change_spout._meta.model_name}_change',
                                  args=(change_spout.id,)),
             f'{change_spout.is_on}-{change_spout.spout_id}.{change_spout.spout.name}')
            for change_spout in sub_program.spouts.all())
        )
    change_spouts_field.short_description = 'تغییر شیرهای خروجی'
