from django.contrib import admin
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from Baghyar.admin import get_linked_repr, get_linked_named_model_repr
from Device.models import LogDeviceCheckOut, DeviceNetworkCoverageLog, ExternalButton, ExternalButtonEvent, \
    ExternalButtonEventSpoutChange, SpoutSensorRecord, ExternalButtonStatusRecord
from Device.models import TestCall

# admin.site.register(LogDeviceCheckOut)
# admin.site.register(DeviceNetworkCoverageLog)
# admin.site.register(ExternalButton)
# admin.site.register(ExternalButtonEvent)
# admin.site.register(ExternalButtonEventSpoutChange)
# admin.site.register(SpoutSensorRecord)


@admin.register(ExternalButton)
class ExternalButtonAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'name', 'is_on', 'on_in_device_field', 'customer_reachable_field', 'is_active_field',
                    'device_field', 'land', 'last_run', 'events_field', 'change_spout_fields', 'period_quantity',
                    'duration_field', 'last_record', 'modified')
    search_fields = ('id', 'name', 'device__name', 'device_id')

    def is_on(self, button: ExternalButton) -> bool:
        return button.is_on
    is_on.short_description = 'وضعیت'
    is_on.boolean = True

    def device_field(self, button: ExternalButton):
        return get_linked_named_model_repr(button.device)
    device_field.short_description = 'دستگاه'

    def land(self, button: ExternalButton):
        land = button.device.land
        try:
            get_linked_repr(land, land.name, land.id)
        except AttributeError:
            try:
                get_linked_repr(land, land.id)
            except AttributeError:
                return 'None'
    land.short_description = 'زمین'

    def on_in_device_field(self, button: ExternalButton):
        return button.on_in_device
    on_in_device_field.short_description = 'فعال در دستگاه'
    on_in_device_field.boolean = True

    def period_quantity(self, button: ExternalButton):
        events = button.events.all().count()
        if events < 2:
            return 0
        return events - 1
    period_quantity.short_description = 'تعداد دوره‌ها'

    def is_active_field(self, button: ExternalButton):
        return button.is_active
    is_active_field.short_description = 'غیر فعال نشده'
    is_active_field.boolean = True

    def customer_reachable_field(self, button: ExternalButton):
        return button.customer_reachable
    customer_reachable_field.short_description = 'دسترسی کاربر'
    customer_reachable_field.boolean = True

    def duration_field(self, button: ExternalButton):
        return str(button.duration)
    duration_field.short_description = 'مدت'

    def events_field(self, button: ExternalButton):
        events = button.events.all()
        return format_html_join(
            ',', '{}.<a href="{}">{}</a><br/>',
            ((event.id, reverse(f'admin:{event._meta.app_label}_{event._meta.model_name}_change', args=(event.id,)),
             f'priority:{event.priority}-delay:{event.delay}-conditions:{event.string_condition}')
            for event in events
        ))
    events_field.short_description = 'فرآیندها'

    def change_spout_fields(self, button: ExternalButton):
        # change_spouts = button.events.prefetch_related('spout_changes').all()
        # testy = button.events.
        change_spouts = ExternalButtonEventSpoutChange.objects.filter(external_button_event__external_button=button)\
            .order_by('external_button_event', 'spout__number')
        return format_html_join(
            ',', '{}.<a href="{}">{}-spout={}</a><br/>',
            ((change_spout.id, reverse(f'admin:{change_spout._meta.app_label}_{change_spout._meta.model_name}_change',
                                       args=(change_spout.id,)),
              f':{change_spout.is_on}-dalay:{change_spout.external_button_event.delay}',
              f'{change_spout.spout.id}.{change_spout.spout.name}',)
             for change_spout in change_spouts)
        )
    change_spout_fields.short_description = 'تغییر شیرها'

    def last_record(self, button: ExternalButton):
        try:
            record = button.records.all().order_by('-time')[0]
            return get_linked_repr(record, f'{record.status}-time={record.time}', record.id)
        except IndexError:
            return None
    last_record.short_description = 'آخرین ثبت'


@admin.register(LogDeviceCheckOut)
class LogDeviceCheckOutAdmin(admin.ModelAdmin):
    fields = ('device',)
    list_display = ('id', 'device_field', 'time', 'device_message', 'response_message', 'get_updates')
    search_fields = ('id', 'device_id')

    def device_field(self, log: LogDeviceCheckOut):
        return get_linked_named_model_repr(log.device)
    device_field.short_description = 'دستگاه'


@admin.register(ExternalButtonStatusRecord)
class ExternalButtonStatusRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'status_field', 'time', 'process_button_field', 'device_field', 'actor', 'canceled',
                    'canceled_by_field', 'finished', 'spout_records_field', 'user_field')
    search_fields = ('id', 'process_button_id', 'process_button__name', )
    ordering = ('-time',)

    def spout_records_field(self, record: ExternalButtonStatusRecord):
        return format_html_join(
            ',', '{}.<a href="{}">{}</a><br/>',
            ((spout_record.id, reverse(f'admin:{spout_record._meta.app_label}_{spout_record._meta.model_name}_change',
                                       args=(spout_record.id,)),
             f'{spout_record.status}-spout:{spout_record.spout_id}.{spout_record.spout.name}-{spout_record.time}')
             for spout_record in record.spout_records.all()
             )
        )
    spout_records_field.short_description = 'رکوردهای شیرهای خروجی'

    def status_field(self, record: ExternalButtonStatusRecord):
        if record.canceled:
            return None
        if record.status == ExternalButtonStatusRecord.STATUS.on:
            return True
        if record.status == ExternalButtonStatusRecord.STATUS.off:
            return False
        return None
    status_field.short_description = 'وضعیت'
    status_field.boolean = True

    def process_button_field(self, record: ExternalButtonStatusRecord):
        button = record.process_button
        return get_linked_named_model_repr(button)
    process_button_field.short_description = 'دکمه'

    def device_field(self, record: ExternalButtonStatusRecord):
        device = record.process_button.device
        return get_linked_named_model_repr(device)
    device_field.short_description = 'دستگاه'

    def canceled_by_field(self, record: ExternalButtonStatusRecord):
        canceler_record = record.canceled_by
        try:
            return get_linked_repr(
                canceler_record.canceled_by, f'{canceler_record.canceled_by.status}-'
                                             f'by:{canceler_record.canceled_by.actor}-in:({canceler_record.time})',
                canceler_record.id
            )
        except AttributeError:
            return None
    canceled_by_field.short_description = 'کنسل شده توسط'

    def user_field(self, record: ExternalButtonStatusRecord):
        try:
            return get_linked_repr(record.user, record.user.username, record.user.id)
        except AttributeError:
            return None
    user_field.short_description = 'کاربر'


@admin.register(ExternalButtonEventSpoutChange)
class ExternalButtonEventSpoutChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'spout_field', 'is_on', 'event_field', 'button_field', 'device_field')
    search_fields = ('id', 'spout_id')

    def spout_field(self, change_spout=ExternalButtonEventSpoutChange):
        return get_linked_named_model_repr(change_spout.spout)
    spout_field.short_description = 'شیر خروجی'

    def event_field(self, change_spout=ExternalButtonEventSpoutChange):
        event = change_spout.external_button_event
        return get_linked_repr(event, event.delay, event.id)
    event_field.short_description = 'رخداد'

    def button_field(self, change_spout=ExternalButtonEventSpoutChange):
        button = change_spout.external_button_event.external_button
        return get_linked_named_model_repr(button)
    button_field.short_description = 'دکمه پروسه'

    def device_field(self, change_spout=ExternalButtonEventSpoutChange):
        device = change_spout.external_button_event.external_button.device
        return get_linked_named_model_repr(device)
    device_field.short_description = 'دستگاه'


@admin.register(DeviceNetworkCoverageLog)
class DeviceNetworkCoverageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'value', 'time', 'device_field', 'land_field')
    search_fields = ('id', 'device_id')

    def device_field(self, log: DeviceNetworkCoverageLog):
        return get_linked_named_model_repr(log.device)
    device_field.short_description = 'دستگاه'

    def land_field(self, log: DeviceNetworkCoverageLog):
        return get_linked_named_model_repr(log.device.land)
    land_field.short_description = 'زمین'


@admin.register(ExternalButtonEvent)
class ExternalButtonEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'delay', 'priority', 'button_field', 'device_field')
    search_fields = ('id', 'external_button_id')

    def button_field(self, event: ExternalButtonEvent):
        return get_linked_named_model_repr(event.external_button)
    button_field.short_description = 'دکمه‌ی پروسه'

    def device_field(self, event: ExternalButtonEvent):
        return get_linked_named_model_repr(event.external_button.device)
    device_field.short_description = 'دستگاه'


@admin.register(TestCall)
class TestCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'header', 'body')
