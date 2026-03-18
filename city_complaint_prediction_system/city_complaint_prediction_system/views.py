import django.shortcuts
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

def admin_dashboard(request):
    template = loader.get_template('admin/index.html')
    return HttpResponse(template.render({}, request))

