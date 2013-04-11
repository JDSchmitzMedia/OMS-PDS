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


from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from django.contrib import admin
admin.autodiscover()

#from tastypie.api import Api
#from oms_pds.pds.api import FunfResource, FunfConfigResource, RoleResource, PurposeResource, SocialHealthResource, RealityAnalysisResource
#
#v1_api = Api(api_name='personal_data')
#v1_api.register(FunfResource())
#v1_api.register(FunfConfigResource())
#v1_api.register(RoleResource())
#v1_api.register(PurposeResource())
#v1_api.register(SocialHealthResource())
#v1_api.register(RealityAnalysisResource())

from oms_pds.pds.tools import v1_api
#v1_api.register(SharingResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from oms_pds.pds.api import AuditEntryResource

audit_entry_resource = AuditEntryResource()

urlpatterns = patterns('oms_pds.views',
    (r'^home/', 'home'),
    (r'^api/', include(v1_api.urls)),
    (r'^discovery/', include('oms_pds.discovery.urls')),
    (r'^purpose/', 'purpose'), 
    (r'^trust/', include('oms_pds.trust.urls')),
    (r'^sharing/', include('oms_pds.sharing.urls')),
    (r'^pdssettings/', 'permissions'), 
    (r'^mysharing/', 'sharing'), 
    (r'^editpas/(?P<id>\d+)/', 'editpas'), 
    (r'^trustsettings/', 'permissions'),
    (r'^pds/', include('oms_pds.pds.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/audit', TemplateView, { 'template' : 'audit.html' }),
    #(r'^documentation/', include('tastytools.urls'), {'api_name': v1_api.api_name}),
    (r'^admin/roles', TemplateView, { 'template' : 'roles.html' }),
    (r'^(?P<owner_uuid>\w+)/api/', include(audit_entry_resource.urls)),
#    (r'^admin/viz', 'django.views.generic.simple.direct_to_template', { 'template' : 'reality_analysis/reality_analysis/visualization.html' }),
    # Examples:
    # url(r'^$', 'OMS_PDS.views.home', name='home'),
    # url(r'^OMS_PDS/', include('OMS_PDS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
