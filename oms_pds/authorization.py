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

from tastypie.authorization import Authorization
from oms_pds.authentication import OAuth2Authentication
from oms_pds.pds.models import Profile, AuditEntry, ClientRegistryEntry, Role, Purpose, Scope

import settings
import pdb
import requests

class PDSAuthorization(Authorization):
    audit_enabled = True
    scopes = []
    requester_uuid = ""
    minimal_sharing_level = 0
    resource_scope_name = None
    
    def requester(self):
        print self.requester_uuid
        return self.requester_uuid

    def getSharingLevel(self, profile):
	# assume only one is selected, and return the first
        sharinglevel = profile.sharinglevel_owner.get(isselected = True)
#	if sharinglevel.count() == 0:
#	   raise Exception("No sharing level objects are selected.")
#	elif sharinglevel.count() > 1:
#	   raise Exception("Too many sharing level objects selected.")
	return sharinglevel

    def get_userinfo_from_token(self, token, datastore_owner_uuid, profile):
	print 'get user info from token'
	user_info = {}
        try:
	    print settings.SERVER_OMS_REGISTRY
            r = requests.get("http://"+settings.SERVER_OMS_REGISTRY+"/get_key_from_token?bearer_token="+str(token))
	    print r.json()
	    user_info = r.json()
	    
            if user_info['status'] == 'error':
                raise Exception(result['error'])
	    self.requester_uuid = user_info['client_id']
	    self.scopes = user_info['scopes']
	    client_re = None
	    try:
	        client_re = ClientRegistryEntry.objects.get(client_id=str(self.requester_uuid))
	    except:
                # client doesn't exist, create a new one, with default role + purpose.
		#TODO: default values for pupose and group should be standardized and placed in a setting file.
 	        purpose, purpose_created = Purpose.objects.get_or_create(name="trustframework", datastore_owner=profile)
                purpose.save()

	        role, role_created = Role.objects.get_or_create(name="group", datastore_owner=profile, issharing=True)
                role.save()

	        client_re = ClientRegistryEntry(client_id=str(self.requester_uuid), role = role)
		client.save()
	    

        except Exception as ex:
            print ex
            return False
        return user_info, client_re


    def trustWrapper(self, profile, client_re):
        print "checking trust wrapper"
        print "resource_scope_name?  ",self.resource_scope_name
        #Check the user's global sharing level
        sharinglevel = self.getSharingLevel(profile)
        print sharinglevel.level
        if sharinglevel.level < self.minimal_sharing_level:
            print "insufficient sharing level return false"
            return False
        if self.scope.issharing == False:
            print "insufficient scope return false"
            return False
        if client_re.role.issharing == False:
            return False

        print "user's global sharing level: ",sharinglevel.level
        #Check if the user is sharing with this client
        

       # p0.role_owner.latest("id")
       # p0.role_owner.latest("id").name
       # p0.sharinglevel_owner.filter(isselected = True)
       # p0.sharinglevel_owner.filter(isselected = True).level
       # sl = p0.sharinglevel_owner.first(isselected = True)
       # sl = p0.sharinglevel_owner.filter(isselected = True)
       # sl.latest("id")
       # sl.latest("id").level
	return True
 
    def is_authorized(self, request, object=None):
        print "is authorized?"
        _authorized = True
        # Note: the trustwrapper must be run regardless of if auditting is enabled on this call or not
       
        if request.REQUEST.has_key("datastore_owner__uuid"):
            print "has uuid"
        else:
	    print "Missing ds uuid"
	    raise Exception("Missing datastore_owner__uuid.  Please make sure it exists as a querystring parameter") 
        datastore_owner_uuid = request.REQUEST.get("datastore_owner__uuid")
        datastore_owner, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)

        #TODO: default values for pupose and group should be standardized and placed in a setting file.
        self.purpose, purpose_created = Purpose.objects.get_or_create(name=self.purpose_name, datastore_owner=datastore_owner)
        if purpose_created:
            self.purpose.save()

        self.scope, scope_created = Scope.objects.get_or_create(name=self.resource_scope_name, datastore_owner=datastore_owner)
        if scope_created:
            self.scope.save()

        token = request.REQUEST["bearer_token"] if "bearer_token" in request.REQUEST else request.META["HTTP_BEARER_TOKEN"]

	# userinfo (primarily a list of scopes the token is authorized for), client_re (the pds registry for grants of authorization...is used user control post-grant-of-authorization).
	userinfo, client_re = self.get_userinfo_from_token(token,datastore_owner_uuid, datastore_owner)
        _authorized = self.trustWrapper(datastore_owner, client_re)
	print "trust wrapper result: ", _authorized
         
        # Result will be the uuid of the requesting party
        print self.requester_uuid
        try:
            if (self.audit_enabled):
                #pdb.set_trace()
                audit_entry = AuditEntry(token = token)
                audit_entry.method = request.method
                scope_string = ""
		for s in self.scopes:
                    scope_string += str(s)+" "
                audit_entry.scope = scope_string
                audit_entry.purpose = request.REQUEST["purpose"] if "purpose" in request.REQUEST else ""
                audit_entry.system_entity_toggle = request.REQUEST["system_entity"] if "system_entity" in request.REQUEST else False
                # NOTE: datastore_owner and requester are required
                # if they're not available, the KeyError exception should raise and terminate the request
                audit_entry.datastore_owner = datastore_owner
                audit_entry.requester, created = Profile.objects.get_or_create(uuid = self.requester_uuid)
                audit_entry.script = request.path
                audit_entry.save()
        except Exception as e:
            print e
        
        print 'is authorized?'
        print _authorized
        return _authorized

    def __init__(self, scope, audit_enabled = True, minimal_sharing_level = 0, purpose_name = "trustframework"):
        self.resource_scope_name = scope
        self.audit_enabled = audit_enabled
        self.minimal_sharing_level = minimal_sharing_level
	self.purpose_name = purpose_name


    
    # Optional but useful for advanced limiting, such as per user.
    # def apply_limits(self, request, object_list):
    #    if request and hasattr(request, 'user'):
    #        return object_list.filter(author__username=request.user.username)
    #
    #    return object_list.none()

