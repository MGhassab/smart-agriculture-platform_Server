from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from Baghyar.admin import get_linked_repr, get_linked_named_model_repr
from .models import SpoutChangeRecord, CustomerSpoutChangeRecord, ProgramSpoutChangeRecord, ProcessSpoutChangeRecord


# admin.site.register(ProcessSpoutChangeRecord)
# admin.site.register(SpoutLastIrrigation)
# admin.site.register(CustomerSpoutChangeRecord)
@admin.register(CustomerSpoutChangeRecord)
class CustomerSpoutChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('Id', 'status_field', 'time', 'spout__name', 'Created', 'Modified', 'customer_user')
    list_filter = ('spout__device__land', )
    search_fields = ('spout__name__startswith', 'spout__device__land__name__startswith', )

    def status_field(self, record: ProcessSpoutChangeRecord):
        return record.status == ProcessSpoutChangeRecord.STATUS.turn_on
    status_field.short_description = 'تغییر وضعیت'
    status_field.boolean = True

    def spout__name(self, record: CustomerSpoutChangeRecord) -> str:
        url = reverse(
            f'admin:{record.spout._meta.app_label}_{record.spout._meta.model_name}_change',
            args=(record.spout.id,)
        )
        return format_html('<a href="{}">{}</a>', url, f'{record.spout.id}.{record.spout.name}')
    spout__name.short_description = 'شیر'

    def customer_user(self, record: CustomerSpoutChangeRecord) -> str:
        url = reverse(
            f'admin:{record.customer._meta.app_label}_{record.customer._meta.model_name}_change',
            args=(record.customer.id,)
        )
        return format_html('<a href="{}">{}</a>', url, f'{record.customer.id}.{record.customer.user.username}')
    customer_user.short_description = 'مشتری'

    def Id(self, obj: CustomerSpoutChangeRecord) -> int:
        return obj.id
    Id.short_description = 'آیدی'

    def Status(self, obj: CustomerSpoutChangeRecord) -> str:
        status_str = {
            'turn_off': 'خاموش',
            'turn_on': 'روشن',
            'un_change': 'بی تغییر',
        }
        return status_str[obj.status]
    Status.short_description = 'وضعیت تغییر'

    def Created(self, obj: CustomerSpoutChangeRecord) -> str:
        return obj.created
    Created.short_description = 'زمان ساخت'

    def Modified(self, obj: CustomerSpoutChangeRecord) -> str:
        return obj.modified
    Modified.short_description = 'زمان تغییر'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # form.base_fields["first_name"].label = "First Name (Humans only!):"
        return form


def get_linked_record_repr(record: SpoutChangeRecord):
    return get_linked_repr(record, f'{record.status}-{record.time}', record.id)


@admin.register(ProcessSpoutChangeRecord)
class ProcessSpoutChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'status', 'status_field', 'spout_field', 'button_record_canceled',
                    'button_record_finiched',
                    'button_record_field',
                    'process_button_field', 'start',
                    'finish', 'execute_before_cancel', 'change_spout_field')
    search_fields = ('id', 'button_record_id', 'button_record__process_button')
    ordering = ('-time', )

    def status_field(self, record: ProcessSpoutChangeRecord):
        if record.button_record.canceled:
            return None
        return record.status == ProcessSpoutChangeRecord.STATUS.turn_on
    status_field.short_description = 'تغییر وضعیت'
    status_field.boolean = True

    def button_record_field(self, record: ProcessSpoutChangeRecord):
        button_record = record.button_record
        return get_linked_repr(
            button_record, f'{button_record.status}-button:{button_record.process_button_id}'
                           f'.{button_record.process_button.name}',
            f'{button_record.id}'
        )
    button_record_field.short_description = 'لاگ تغییر کل دکمه‌ی پروسه'

    def process_button_field(self, record: ProcessSpoutChangeRecord):
        button = record.button_record.process_button
        return get_linked_named_model_repr(button)
    process_button_field.short_description = 'دکمه‌ی پروسه'

    def button_record_canceled(self, record: ProcessSpoutChangeRecord):
        button_record = record.button_record
        return button_record.canceled
    button_record_canceled.short_description = 'کنسل شدگی'
    button_record_canceled.boolean = True

    def button_record_finiched(self, record: ProcessSpoutChangeRecord):
        return record.button_record.finished
    button_record_finiched.short_description = 'پایان یافته'
    button_record_finiched.boolean = True

    def spout_field(self, record: ProcessSpoutChangeRecord):
        return get_linked_named_model_repr(record.spout)
    spout_field.short_description = 'شیر خروجی'

    def change_spout_field(self, record: ProcessSpoutChangeRecord):
        change_spout = record.change_spout
        try:
            return get_linked_repr(change_spout, str(change_spout.is_on), change_spout.id)
        except AttributeError:
            return None
    change_spout_field.short_description = 'فیلد تغییر وضعیت خروجی'


@admin.register(SpoutChangeRecord)
class SpoutChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'spout_field', 'time', )
    search_fields = ('id',)

    def spout_field(self, record: SpoutChangeRecord):
        return get_linked_named_model_repr(record.spout)
    spout_field.short_description = 'شیر خروجی'


@admin.register(ProgramSpoutChangeRecord)
class ProgramSpoutChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'status_field', 'start', 'finish', 'canceled', 'execute_before_cancel',
                    'program_group_field')
    search_fields = ('id', 'program_group_id', )

    def status_field(self, record: ProcessSpoutChangeRecord):
        return record.status == ProcessSpoutChangeRecord.STATUS.turn_on
    status_field.short_description = 'تغییر وضعیت'
    status_field.boolean = True

    def program_group_field(self, record: ProgramSpoutChangeRecord):
        return get_linked_named_model_repr(record.program_group)
    program_group_field.short_description = 'برنامه‌ی زمانی'

