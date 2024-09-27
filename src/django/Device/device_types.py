from datetime import timedelta

from Customer.models import Device, Spout
from Device.models import ExternalButton, ExternalButtonEvent, ExternalButtonEventSpoutChange

device_types = [
    {
        'name': 'basic',
        'code': '001',
        'type_number': 1,
        'spouts': [
            {'type_no': 1, 'name': 'خروجی 1'},
            {'type_no': 1, 'name': 'خروجی 2'},
        ],
        # 'spouts': 2,
        # 'spout_names': ['شیر اول', 'شیر دوم'],
        # 'spout_types': [1, 1],
        'device_update_minutes': 2,
        # 'process_buttons': 2,
        # 'process_button_names': ['شیفت ۱', 'شیفت ۲'],
        # 'process_button_delays_minute': [60, 60],
        # 'process_spout_conditions': [
        #     [['True', 'False'], ['False', 'False']],
        #     [['False', 'True'], ['False', 'False']],
        # ],
        'process_buttons': [
            {
                'name': 'دکمه 1',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=4),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'دکمه 2',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=4),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
        ],
    },
    {
        'name': 'abgiri',
        'code': '002',
        'type_number': 2,
        'spouts': [
            {'type_no': 1, 'name': 'شیر'},
            {'type_no': 2, 'name': 'پمپ'},
            {'type_no': 3, 'name': 'سنسور'},
        ],
        'process_buttons': [
            {
                'name': 'آبگیری',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 3, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=12),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 3, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'اوتومات',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=2),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'سنسور',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=12),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': False},
                        ],
                    },
                ],
                'user_access': False
            },
        ],

        # 'spouts': 4,
        # 'spout_names': ['', 'شیر دوم', 'شیر سوم', 'شیر چهارم'],
        # 'spout_types': [1, 1, 1, 1],
        'device_update_minutes': 2,
        # 'process_buttons': 3,
        # 'process_button_names': ['شیفت ۱', 'شیفت ۲', 'شیفت ۳'],
        # 'process_button_delays_minute': [60, 60, 60],
        # 'process_spout_conditions': [
        #     [['True', 'False', 'False'], ['False', 'False', 'False']],
        #     [['False', 'True', 'False'], ['False', 'False', 'False']],
        #     [['False', 'False', 'True'], ['False', 'False', 'False']],
        # ],
    },
    {
        'name': '2shift',
        'code': '003',
        'type_number': 3,
        'spouts': [
            {'type_no': 1, 'name': 'شیر 1', },
            {'type_no': 1, 'name': 'شیر 2', },
            {'type_no': 2, 'name': 'پمپ', },
        ],
        'process_buttons': [
            {
                'name': 'شیفت اول',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': True},
                            {'spout_index': 3, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=1),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': False},
                            {'spout_index': 3, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'شیفت دوم',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': True},
                            {'spout_index': 3, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=1),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': False},
                            {'spout_index': 3, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'اتومات',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': True},
                            {'spout_index': 2, 'is_on': False},
                            {'spout_index': 3, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=1),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': False},
                            {'spout_index': 2, 'is_on': True},
                            {'spout_index': 3, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=2),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': False},
                            {'spout_index': 2, 'is_on': False},
                            {'spout_index': 3, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
        ],

        # 'spouts': 4,
        # 'spout_names': ['', 'شیر دوم', 'شیر سوم', 'شیر چهارم'],
        # 'spout_types': [1, 1, 1, 1],
        'device_update_minutes': 2,
        # 'process_buttons': 3,
        # 'process_button_names': ['شیفت ۱', 'شیفت ۲', 'شیفت ۳'],
        # 'process_button_delays_minute': [60, 60, 60],
        # 'process_spout_conditions': [
        #     [['True', 'False', 'False'], ['False', 'False', 'False']],
        #     [['False', 'True', 'False'], ['False', 'False', 'False']],
        #     [['False', 'False', 'True'], ['False', 'False', 'False']],
        # ],
    },
    {
        'name': '3shift',
        'code': '004',
        'type_number': 4,
        'spouts': [
            {'type_no': 1, 'name': 'شیر 1', },
            {'type_no': 1, 'name': 'شیر 2', },
            {'type_no': 1, 'name': 'شیر 3', },
            {'type_no': 2, 'name': 'پمپ', },
        ],
        'process_buttons': [
            {
                'name': 'شیفت اول',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': True},
                            {'spout_index': 4, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=1),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 1, 'is_on': False},
                            {'spout_index': 4, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'شیفت دوم',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': True},
                            {'spout_index': 4, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=1),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 2, 'is_on': False},
                            {'spout_index': 4, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
            {
                'name': 'شیفت سوم',
                'events': [
                    {
                        'delay': timedelta(hours=0),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 3, 'is_on': True},
                            {'spout_index': 4, 'is_on': True},
                        ],
                    },
                    {
                        'delay': timedelta(hours=1),
                        'priority': 1,
                        'button_changes': [
                            {'spout_index': 3, 'is_on': False},
                            {'spout_index': 4, 'is_on': False},
                        ],
                    },
                ],
                'user_access': True
            },
        ],

        # 'spouts': 4,
        # 'spout_names': ['', 'شیر دوم', 'شیر سوم', 'شیر چهارم'],
        # 'spout_types': [1, 1, 1, 1],
        'device_update_minutes': 2,
        # 'process_buttons': 3,
        # 'process_button_names': ['شیفت ۱', 'شیفت ۲', 'شیفت ۳'],
        # 'process_button_delays_minute': [60, 60, 60],
        # 'process_spout_conditions': [
        #     [['True', 'False', 'False'], ['False', 'False', 'False']],
        #     [['False', 'True', 'False'], ['False', 'False', 'False']],
        #     [['False', 'False', 'True'], ['False', 'False', 'False']],
        # ],
    },
]


def get_device_type_by_code(code):
    for typeo in device_types:
        if typeo['code'] == code:
            return typeo
    raise NotImplementedError


def get_device_type_by_type_number(num):
    for typeo in device_types:
        if typeo['type_number'] == num:
            return typeo
    raise NotImplementedError


def create_device(serial: str) -> Device:
    code = serial[-3:]
    typo = get_device_type_by_code(code)
    device = Device.objects.create(serial=serial, update_period=timedelta(minutes=typo['device_update_minutes']),
                                   type_number=typo['type_number'], )
    # print(f'#######-{typo}')
    # for index, spout in enumerate(typo['spouts'], 1):
    #     print(f'{index}_{spout}')
    spouts = [Spout.objects.create(
        name=spout['name'],
        # type_no=spout['type_no'],
        number=index,
        device=device
    )
              for index, spout in enumerate(typo['spouts'], 1)]
    for button_index, button_dict in enumerate(typo['process_buttons']):
        button = ExternalButton.objects.create(
            number=button_index+1, device=device, name=button_dict['name'],
            customer_reachable=button_dict['user_access']
        )
        for event_index, event_dict in enumerate(button_dict['events']):
            event = ExternalButtonEvent.objects.create(external_button=button, delay=event_dict['delay'],
                                                       priority=event_index)
            for spout_index, change_spout_dict in enumerate(event_dict['button_changes']):
                change_spout = ExternalButtonEventSpoutChange.objects.create(
                    external_button_event=event, spout=spouts[change_spout_dict['spout_index'] - 1],
                    is_on=change_spout_dict['is_on'])

    # TODO create process buttons and programs
    return device
