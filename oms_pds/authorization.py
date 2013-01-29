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
from oms_pds.pds.models import Profile, AuditEntry

import settings
import pdb
import requests

class PDSAuthorization(Authorization):
    audit_enabled = True
    scopes = []
    requester_uuid = ""
    minimal_sharing_level = 0
    
    def requester(self):
        print self.requester_uuid
        return self.requester_uuid

    def getSharingLevel(self, profile):
        sharinglevel = profile.sharinglevel_owner.get(isselected = True)
#	if sharinglevel.count() == 0:
#	   raise Exception("No sharing level objects are selected.")
#	elif sharinglevel.count() > 1:
#	   raise Exception("Too many sharing level objects selected.")
	return sharinglevel

    def get_userinfo_from_token(self, token):
	print 'get user info from token'
	user_info = {}
        try:
	    print settings.SERVER_OMS_REGISTRY
            r = requests.get("http://"+settings.SERVER_OMS_REGISTRY+"/get_key_from_token?bearer_token="+str(token))
	    print r.json()
	    user_info = r.json()
	    
            if user_info['status'] == 'error':
                raise Exception(result['error'])
	    self.requester_uuid = user_info['client']
	    self.scopes = user_info['scopes']

        except Exception as ex:
            print ex
            return False
        return user_info


    def trustWrapper(self, profile):
        print "checking trust wrapper"
       # sharinglevel = self.getSharingLevel(profile)
       # print sharinglevel.level
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
        token = request.REQUEST["bearer_token"] if "bearer_token" in request.REQUEST else request.META["HTTP_BEARER_TOKEN"]

	userinfo = self.get_userinfo_from_token(token)
	print userinfo
#        authenticator = OAuth2Authentication(self.scope)
#        self.requester_uuid = authenticator.get_userinfo_from_token(token, self.scope)
        self.trustWrapper(datastore_owner)
        
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

    def __init__(self, scope, audit_enabled = True, minimal_sharing_level = 0):
        #pdb.set_trace()
        self.scope = scope
        self.audit_enabled = audit_enabled
	self.minimal_sharing_level = minimal_sharing_level
    
    # Optional but useful for advanced limiting, such as per user.
    # def apply_limits(self, request, object_list):
    #    if request and hasattr(request, 'user'):
    #        return object_list.filter(author__username=request.user.username)
    #
    #    return object_list.none()






#import pymongo
#import logging
#from pymongo import Connection
#import json
#
##TODO This trust wrapper implements sharing as defined in DARPA DCAPS project.  Eventually we will need to implement sharing fully defined at the PDS level, and not a shared database.
#
##To install this trustwrapper on a resourceServer, run install_trustWrapper.py, which is located in the same directory as this file.
#
#
#def getPDSSharingLevel(db):
#    return sharing_level
#
# 
#def checkTrustWrapper( purpose, ro_sid=None, permitted_roles=None):
#    #ro_sid - the resource owner's symbolic key (also the postfix of the mongo store)
#    #id - the requester's id (used for mapping the role relationship)
#    #purpose - 'purpose' defined in SDD
#
#    logging.debug('resource owner symbolic ID')
#    logging.debug(ro_sid)
#    if ro_sid is None:
#	logging.debug('access request self...returning')
#        return True
#
#    try:
#	#TODO When PDS' are distributed, the database will be known implicitly
#
#	#sharing_level = getPDSSharingLevel(db)
#	sharing_level = 3
#
#
#	#TODO We will need to define application parameters where we can hold a list of installled applications, and create application specific stores on the fly
#	connection = Connection()
#        db_RA = connection["RealityAnalysis"]
#
#	#check sharing -> purpose
#	logging.debug("checking sharing to purpose")
#	logging.debug(sharing_level)
#	logging.debug(purpose)
#	if (db_RA.mapping.find_one({"SHARING": int(sharing_level), "PURPOSE": str(purpose)}) is not None):
#	    #TODO: check system entity toggle
#
#	    #check purpose -> role
#	    logging.debug("checking purpose to role")
#	    logging.debug(purpose)
#            for role in permitted_roles:
#		logging.debug(role)
#                if (db_RA.mapping.find_one({"ROLE":str(role), "PURPOSE": str(purpose)}) is not None):
#                     return True
#	    raise Exception("couldn't find a mapping for purpose - role")
#	else:
#	    raise Exception("couldn't find a mapping for sharing -> purpose")
#
#    except TypeError as e:
#        logging.debug('ERROR: personalPermissions store is not configured correctly.  Check that the collection "personalPermissions" exists, as well as entries for key-value "permission_type"-"sharing" as well as sub element object keys for "sharing" and "uidRoles"')
#        logging.debug(e.message)
#    finally:
#        connection.disconnect()
#    return False
