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

from oms_pds.pds.models import Profile, SharingLevel, Purpose
from oms_pds.pds.api import SharingLevelResource, PurposeResource
from django.http import HttpResponse
import json


def validateRequest(request):
    if not request.GET.has_key('datastore_owner__uuid'):
        raise Exception('Missing datastore_owner__uuid.  Please add it as a querystring parameter.')
    return

def create(request):
    validateRequest(request)    
    p = Profile(uuid = request.GET.get('datastore_owner__uuid'))
    p.save()
    is_success = initializeTrustWrapper(p)
    print is_success
    response_dict = {}
    response_dict['status'] = "success"

    return HttpResponse(json.dumps(response_dict), content_type='application/json')

def initializeTrustWrapper(profile):

    p0 = Purpose(name="PDS", datastore_owner=profile)
    p0.save()

    s0 = SharingLevel(level = 0, datastore_owner=profile, isselected = True)
    s1 = SharingLevel(level = 1, datastore_owner=profile, isselected = False)
    s2 = SharingLevel(level = 2, datastore_owner=profile, isselected = False)
    s3 = SharingLevel(level = 3, datastore_owner=profile, isselected = False)
    s0.save()
    s1.save()
    s2.save()
    s3.save()
    # Mapping each sharing level to the purpose PDS
    s0.purpose = [p0]
    s1.purpose = [p0]
    s2.purpose = [p0]
    s3.purpose = [p0]
    # we need to save the sharing levels twice, becuse the act of saving creates the primary key necessary to map sharing level to purpose
    s0.save()
    s1.save()
    s2.save()
    s3.save()
    

    return True


