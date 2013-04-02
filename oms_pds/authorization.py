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

    def create_client_registry_entry(self, profile):
        #Each OAuth client is "registered" in the user's PDS.  The client's registry information is used to make trust wrapper authorization decisions.

        #TODO: default values for pupose and group should be standardized and placed in a setting file.

        # Get or create a default purpose
        purpose, purpose_created = Purpose.objects.get_or_create(name="trustframework", datastore_owner=profile)
        purpose.save()
        
        # Get or create a default role
        role, role_created = Role.objects.get_or_create(name="group", datastore_owner=profile, issharing=True)
        role.save()

        client_re = ClientRegistryEntry(client_id=str(self.requester_uuid), role = role)
        client_re.save()
        
        return client_re

    def call_auth_server_token_introspection(self, token):
        # Make a call to the Authorization Server
        r = requests.get("http://"+settings.SERVER_OMS_REGISTRY+"/get_key_from_token?bearer_token="+str(token))
        

        return r.json()

    def extract_user_info(self, auth_server_response):
        #Extract the relevant information from the authorization server's token introspection response
        if auth_server_response['status'] == 'error':
            raise Exception(auth_server_response['message'])

        self.requester_uuid = auth_server_response['client_id']
        #the collection of both resource and answer scopes
        self.scopes = auth_server_response['scopes']


    def get_userinfo_from_token(self, token, datastore_owner_uuid, profile):
        #The function makes calls back to the Authorization server to for token introspection.  Token information is acquired from the Authorization server, and used by the PDS to make authorization choices.  
        # params
        #   token: the oauth token included in the http request
        #   datastore_owner_uuid: the owner of the data.  This is used to enable multiple personal data stores on one web service(python project).
        #   profile: the user's profile settings.  The main information held in the profile is links to trust wrapper(user defined run-time settings).

        print 'get user info from token'
        user_info = {}
        client_re = None

        try:
            # Make a call to the Authorization Server
            user_info = self.call_auth_server_token_introspection(token)
            self.extract_user_info(user_info)
	    
            try:
	        client_re = ClientRegistryEntry.objects.get(client_id=str(self.requester_uuid))
            except:
                # client doesn't exist, create a new one, with default role + purpose.
                client_re = self.create_client_registry_entry(profile)

        except Exception as ex:
            print ex
            return False

        return user_info, client_re


    def trustWrapper(self, profile, client_re):
        print "checking trust wrapper"
        #the scope required to access a resource for either answering questions or retrieving raw data.
        print "resource_scope_name?  ",self.resource_scope_name

        #Check the user's global sharing level
        sharinglevel = self.getSharingLevel(profile)

        print sharinglevel.level
        if sharinglevel.level < self.minimal_sharing_level:
            print "insufficient sharing level return false"
            return False
        #Each scope should 
        if self.scope.issharing == False:
            print "not sharing this scope return 0 as result"
            return False
        if client_re.role.issharing == False:
            return False

        print "user's global sharing level: ",sharinglevel.level
        #Check if the user is sharing with this client

        return True

    def trustWrapper2(self, uuid, client_re):
        # client_re.scope("movement").level
        # client_re.scope("communication").level
        role = client_re.role
        print uuid
        my_scope = Scope.objects.get_or_create(name="focus", datastore_owner_id=uuid)
        print "checking trustWrapper2"
        my_scope_settings = role.scopes.get_or_create(scope=my_scope)
	print my_scope_settings
	my_scope_settings.level

        print "checking issharing "
        if role.issharing == False:
            return False

        print "checking sharing level"
        if my_scope_setttings.level < self.minimal_sharing_level:
            return False

        return True
 
    def is_authorized(self, request, object=None):
        print "is authorized?"
        _authorized = True
        # Note: the trustwrapper must be run regardless of whether or not auditting is enabled       
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
        try:
	    userinfo, client_re = self.get_userinfo_from_token(token,datastore_owner_uuid, datastore_owner)
	    print "calling trust wrapper"
            #_authorized = self.trustWrapper(datastore_owner, client_re)
            _authorized = self.trustWrapper2(datastore_owner_uuid, client_re)
	    print "trust wrapper result: ", _authorized
        except Exception as ex:
            print "failed to get userinfo from token"
            _authorized = False
         
        # Result will be the uuid of the requesting party
        print self.requester_uuid
        try:
            if (self.audit_enabled):
                #pdb.set_trace()
		print "auditing"
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


