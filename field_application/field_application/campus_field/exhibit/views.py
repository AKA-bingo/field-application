#-*- coding: utf-8 -*-
import logging

from django.views.generic import View
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms.forms import NON_FIELD_ERRORS
from django.core.paginator import InvalidPage, Paginator

from field_application.campus_field.forms import ExhibitApplicationForm
from field_application.campus_field.models import ExhibitApplication
from field_application.utils.ajax import render_json
from field_application.account.permission import check_perms


class ApplyView(View):

    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'campus_field/exhibit/form.html', 
                      {'form': ExhibitApplicationForm(),
                       'post_url': reverse('exhibit:apply')})

    @method_decorator(login_required)
    def post(self, request):
        form = ExhibitApplicationForm(request.POST,
                                      request.FILES)
        if not form.is_valid():
            return render(request, 'campus_field/exhibit/form.html', 
                          {'form': form,
                           'post_url': reverse('exhibit:apply')})
        app = form.save(commit=False)
        app.organization = request.user.organization
        app.save()
        return HttpResponseRedirect(reverse('exhibit:table'))


def display_table(request):
    week = int(request.GET.get('week') or 0)
    table = ExhibitApplication.generate_table(offset=week)
    return render(request, 'campus_field/exhibit/table.html',
            {'table': table, 'curr_week': week})


def display_list(request):
    listing = ExhibitApplication.objects.all()
    paginator = Paginator(listing, 3)
    for app in listing:
        app.date = app.start_date.strftime('%Y年%m月%d日') \
            + '-' + app.start_date.strftime('%Y年%m月%d日')
    try:
        page = paginator.page(request.GET.get('page'))
    except InvalidPage:
        page = paginator.page(1)
    return render(request, 'list.html',
                {'page': page, 'title': u'校园文化活动露天场地申请'})


@login_required
def manage(request):
    org = request.user.organization
    listing = ExhibitApplication.objects.\
            filter(organization=org).order_by('-pk')
    for app in listing:
        app.date = app.start_date.strftime('%Y年%m月%d日') \
            + '-' + app.end_date.strftime('%Y年%m月%d日')
    paginator = Paginator(listing, 3)
    try:
        page = paginator.page(request.GET.get('page'))
    except InvalidPage:
        page = paginator.page(1)
    return render(request, 'manage.html',
            {'page': page, 'title': u'校园活动露天场地申请',
             'modify_url': reverse('exhibit:modify'),
             'approve_url': reverse('exhibit:manager_approve')})

 
def get_detail(request):
    app = ExhibitApplication.objects.get(
            id=request.GET.get('id'))
    data = {'organization': app.organization.chinese_name,
            'place': app.place, 
            'start_date': app.start_date.strftime('%Y年%m月%d日'),
            'end_date': app.end_date.strftime('%Y年%m月%d日'),
            'time': app.time,
            'activity': app.activity,
            'approved': app.approved, 'plan_file': app.plan_file.url,
            'applicant_name': app.applicant_name,
            'applicant_phone_number': app.applicant_phone_number,
            'application_time': \
                    app.application_time.strftime('%Y年%m月%d日 %H:%M:%S'),
            'sponsor': app.sponsor, 'sponsorship': app.sponsorship,
            'sponsorship_usage': app.sponsorship_usage,
            'activity_summary': app.activity_summary,
            'exhibit_board_number': app.exhibit_board_number,
            'exhibition': app.exhibition,
            'remarks': app.remarks}
    return render_json(data)


class ModifyView(View):

    @method_decorator(login_required)
    def get(self, request):
        app_id = request.GET.get('id')
        app = ExhibitApplication.objects.get(id=app_id)
        form = ExhibitApplicationForm(instance=app)
        return render(request, 'campus_field/exhibit/form.html', 
                {'form': form, 'app_id': app_id,
                 'post_url': \
                     reverse('exhibit:modify')+'?id='+app_id})

    @method_decorator(login_required)
    def post(self, request):
        app_id = request.GET.get('id')
        app = ExhibitApplication.objects.get(id=app_id)
        form = ExhibitApplicationForm(
                request.POST, request.FILES, instance=app)
        if not form.is_valid():
            return render(request, 'campus_field/exhibit/form.html', 
                {'form': form, 'app_id': app_id,
                 'post_url': \
                     reverse('exhibit:modify')+'?id='+app_id})
        form.save()
        return HttpResponseRedirect(reverse('exhibit:manage'))


@login_required
@check_perms('account.manager', u'无管理权限')
def manager_approve(request):
    app_id = request.GET.get('id')
    app = ExhibitApplication.objects.get(id=app_id)
    app.approved = not app.approved
    app.save()
    return HttpResponseRedirect(reverse('exhibit:manage'))

