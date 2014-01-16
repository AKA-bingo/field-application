#-*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import models

from field_application.account.models import Organization
from field_application.custom.utils import generate_date_list_this_week
from field_application.custom.utils import get_application_this_week 
from field_application.utils.models import file_save_path


class StudentActivityCenterApplication(models.Model):

    PLACE = (
        ('Square', u'学生活动中心前广场'),
        ('LectureHall', u'一楼影视报告厅'),
        ('3rdFloorEast', u'学生活动中心三楼天台(东)'),
        ('3rdFloorWest', u'学生活动中心三楼天台(西)'),
        ('TheStoneDock', u'石头坞广场'),
    )
    TIME = (
        ('MOR', u'早上'),
        ('AFT', u'下午'),
        ('EVE', u'晚上'),
    )

    organization = models.ForeignKey(Organization)
    place = models.CharField(max_length=20, choices=PLACE)
    date = models.DateField()
    time = models.CharField(max_length=10, choices=TIME)
    activity = models.CharField(max_length=30)
    approved = models.BooleanField(default=False)
    application_time = models.DateTimeField(auto_now_add=True)
    plan_file = models.FileField(
            upload_to=file_save_path('student_activity_center'))

    applicant_name = models.CharField(max_length=10)
    applicant_phone_number = models.CharField(max_length=30)
    activity_summary = models.CharField(max_length=200)
    sponsor = models.CharField(max_length=30, blank=True, null=True)
    sponsorship = models.CharField(max_length=30, blank=True, null=True)
    sponsorship_usage = models.CharField(max_length=40, blank=True, null=True)

    @classmethod
    def generate_table(cls):
        field_used_this_week_applications = get_application_this_week(cls)
        table = {}
        empty_time_dict = { cls.TIME[i][0]: None for i in range(0, 3) }
        for short_name, full_name in cls.PLACE:
            table[full_name] = []
            for i in range(0, 7):
                table[full_name].append(dict(empty_time_dict))
            apps = field_used_this_week_applications.filter(place=short_name)
            for app in apps:
                if app.time in empty_time_dict:
                    table[full_name][app.date.weekday()][app.time] = app
                else:
                    raise Exception('invalid time')
        table['date'] = generate_date_list_this_week()
        return table
