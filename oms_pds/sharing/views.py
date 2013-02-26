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
from django.shortcuts import render_to_response
import httplib
from django import forms
import json
from oms_pds.sharing.forms.settingsforms import Sharing_Form, ProbeGroupSetting
import oms_pds.sharing.forms.settingsforms as settingsforms
#from oms_pds.trust.models import Scope, Purpose, Role, SharingLevel
from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel, Profile



def edit(request):
    '''A web interface for modifying trust framework permissions'''
    form = settingsforms.Sharing_Form()
    template = {"form":form}
    if request.GET.get('datastore_owner__uuid') == None:
        raise Exception('missing datastore_owner')
    datastore_owner = request.GET.get('datastore_owner__uuid')
    template['datastore_owner__uuid']=datastore_owner
    form.update_form(datastore_owner)

    p = Profile.objects.get(uuid=datastore_owner)
    probes = ProbeGroupSetting.objects.all()
    roles = p.role_owner.all()
    sharinglevels = p.sharinglevel_owner.all()
    scopes = p.scope_owner.all()

    try:
        if request.method == "POST":
    	    # Process web form from web permission interface
    	    for json_input in json.loads(request.body):
    	        if json_input.get('name') == 'probes':
    	            pgs = ProbeGroupSetting.objects.get(name=json_input['value'])
		    pgs.issharing = json_input['selected']
    		    pgs.save()
    	        elif json_input.get('name') == 'roles':
    	            role = Role.objects.get(name=json_input['value'], datastore_owner=p)
		    role.issharing = json_input['selected']
    		    role.save()
    	        elif json_input.get('name') == 'sharinglevel':
    	            sl = SharingLevel.objects.get(level=json_input['value'], datastore_owner=p)
		    sl.isselected = json_input['selected']
    		    sl.save()

        if request.META.get('CONTENT_TYPE') == 'application/json' or request.GET.get('format') == "json":
            response_dict = {}
            scope_dict = {}
            for s in scopes:
                scope_dict.update({s.name:s.name})
            response_dict['scope'] = scope_dict
            role_dict = {}
            for r in roles:
                role_dict.update({r.name:r.name})
            response_dict['role'] = role_dict
            sl_dict = {}
            for sl in sharinglevels:
                sl_dict.update({sl.level:sl.level})
            response_dict['sharing_level'] = sl_dict

            return HttpResponse(json.dumps(response_dict), content_type='application/json')
    except Exception as e:
	print e
	
    template['probes'] = probes
    template['roles'] = roles
    template['sharinglevels'] = sharinglevels

    return render_to_response('sharing/edit.html',
        template,
        RequestContext(request))


def update(request):
    return render_to_response('sharing/update.html',
        {},
        RequestContext(request))
