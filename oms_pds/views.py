# Copyright (C) 2012 Massachusetts Institute of Technology and Institute 
# for Institutional Innovation by Data Driven Design Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE  MASSACHUSETTS INSTITUTE OF
# TECHNOLOGY AND THE INSTITUTE FOR INSTITUTIONAL INNOVATION BY DATA
# DRIVEN DESIGN INC. BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE 
# USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Except as contained in this notice, the names of the Massachusetts 
# Institute of Technology and the Institute for Institutional 
# Innovation by Data Driven Design Inc. shall not be used in 
# advertising or otherwise to promote the sale, use or other dealings
# in this Software without prior written authorization from the 
# Massachusetts Institute of Technology and the Institute for 
# Institutional Innovation by Data Driven Design Inc

from django.http import HttpResponse
import json
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
import settings
import httplib
from django import forms
from django.forms import ModelForm
import json
from oms_pds.forms.settingsforms import PermissionsForm, Purpose_Form
from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel, PersonalAnswerSetting, Profile

from oms_pds.pds.models import PersonalAnswerSetting
class PersonalAnswerSettingForm(ModelForm):
    class Meta:
        model = PersonalAnswerSetting


def purpose(request):
    form = Purpose_Form()
    template = {"form":form}
    template = get_datastore_owner(template, request)

    return render_to_response('purpose.html',
        template,
        RequestContext(request))

def editpas(request, id):

    print "edit personal answer setting"
    if request.method == 'POST':
        instance = get_object_or_404(PersonalAnswerSetting, id=id)
        form = PersonalAnswerSettingForm(request.POST, instance=instance)
        if form.is_valid():
            print "form is valid"
            print form.cleaned_data
            form.save()
            return redirect('/')
            
            #form.save()
    pers = PersonalAnswerSetting.objects.get(pk=id)
    print "pers", pers
    pas_form = PersonalAnswerSettingForm(instance=pers)
    print "pers", pers
    return render_to_response('editpas.html',{'form': pas_form}, RequestContext(request))

def sharing(request):
    pers = PersonalAnswerSetting.objects.all()
    print pers.count()
    p = Profile.objects.all()
    p0 = p[0]
    roles = p0.role_owner.all()
    #[<Role: Role object>]
    #template = {"personal_answer_settings":PersonalAnswerSetting.objects.all()}
    template = {"roles":roles}
    template = get_datastore_owner(template, request)

    return render_to_response('sharing.html',
        template,
        RequestContext(request))

def permissions(request):
    form = Purpose_Form()
    template = {"form":form}
    template = get_datastore_owner(template, request)

    if request.META.get('CONTENT_TYPE') == 'application/json' or request.GET.get('format') == "json":
	response_dict = {}
	scope_dict = {} 
	for s in Scope.objects.all(datastore_owner_id=request.GET.get('datastore_owner__uuid')):
	    scope_dict.update({s.name:s.name})
	response_dict['scope'] = scope_dict
	role_dict = {} 
	for r in Role.objects.all(datastore_owner_id=request.GET.get('datastore_owner__uuid')):
	    role_dict.update({r.name:r.name})
	response_dict['role'] = role_dict
	sl_dict = {} 
	for sl in SharingLevel.objects.all(datastore_owner_id=request.GET.get('datastore_owner__uuid')):
	    sl_dict.update({sl.level:sl.level})
	response_dict['sharing_level'] = sl_dict
	    
        return HttpResponse(json.dumps(response_dict), content_type='application/json')

    return render_to_response('permissions.html',
        template,
        RequestContext(request))



def home(request):
    template = {}
    template = get_datastore_owner(template, request)

    return render_to_response('home.html',
        template,
        RequestContext(request))


def get_datastore_owner(template, request):
    if request.GET.get('datastore_owner__uuid') == None:
        raise Exception('missing datastore_owner')
    template['datastore_owner__uuid']=request.GET.get('datastore_owner__uuid')
    return template

