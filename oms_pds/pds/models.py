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

from django.conf import settings
from django.db import models
from django.db.models import signals
from mongoengine import *

from datetime import timedelta
from datetime import *

from django.contrib.auth.models import User
from django.contrib import admin

connect(settings.MONGODB_DATABASE)

DEFAULT_PURPOSE = "TrustFramework"
DEFAULT_ROLE = "default"

class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)
    isinit = models.BooleanField(default=False)
admin.site.register(Profile)

class Role(models.Model):
    ''' @name : The user defined name of the role
         '''
    name = models.CharField(max_length=120)
    issharing = models.BooleanField(default=False)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="role_owner")
admin.site.register(Role)

class Purpose(models.Model):
    name = models.CharField(max_length=120)
#    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="purpose_owner")
admin.site.register(Purpose)

class Scope(models.Model):
    # Globally defined.  Each user(profile) should have PersonalAnswerSettings for each scope.
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
admin.site.register(Scope)
        
class PersonalAnswerSetting(models.Model):
    # TODO: Enable TrustWrapper2 with scopesetting model.
    sharing_level = models.IntegerField()
    scope = models.ForeignKey(Scope)
    role = models.ForeignKey(Role, related_name="personal_answer_settings")
    purpose = models.ManyToManyField(Purpose)
    #datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="scope_owner")
admin.site.register(PersonalAnswerSetting)

class ResourceKey(models.Model):
    ''' A way of controlling sharing within a collection.  Maps to any key within a collection.  For example, funf probes and individual answers to questions'''
    key = models.CharField(max_length=120)
    issharing = models.BooleanField(default=True)

class ProbeGroupSetting(models.Model):
    ''' A way of grouping resource keys for sharing.'''
    name = models.CharField(max_length=120)
    issharing = models.BooleanField(default=False)
    keys = models.ManyToManyField(ResourceKey) #a list of roles the user is currently sharing with

class SharingLevel(models.Model):
    # TODO: Enable TrustWrapper2 with scope sharing settings for each role.
    scopes = models.ManyToManyField(PersonalAnswerSetting)
    level = models.IntegerField()
    purpose = models.ManyToManyField(Purpose)
    isselected = models.BooleanField(default=False)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="sharinglevel_owner")

class ClientRegistryEntry(models.Model):
    # Version 0.5 method for controlling access to data.
    client_id = models.CharField(max_length=120)
    client_name = models.CharField(max_length=120)
    role = models.ForeignKey(Role, blank = False, null = False, related_name="client_role")

#TODO: More UMA-esque...to be re-evaluted after OIDC integration and v0.5.  For now use ClientReg...
#class TokenRegistryEntry(models.Model):
#    # This serves as a cache for entries of oauth tokens existing in the AuthorizationServer.
#    token = models.CharField(max_length=120) #A token the user issued to a client via the authorization server.
#    client = models.CharField(max_length=120)
#    role = models.ForeignKey(Profile, blank = False, null = False, related_name="client_role")
#    isrevoked = models.BooleanField(default=False)
    


# Represents an audit of a request against the PDS
# Given that there will be many entries (one for each request), 
# we are strictly limiting the size of data entered for each row
# The assumption is that script names and symbolic user ids
# will be under 64 characters 
class AuditEntry(models.Model):
    
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_owner")
    requester = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_requester")
    method = models.CharField(max_length=10)
    scopes = models.CharField(max_length=1024) # actually storing csv of valid scopes
    purpose = models.CharField(max_length=64, blank=True, null=True)
    script = models.CharField(max_length=64)
    token = models.CharField(max_length=64)
    system_entity_toggle = models.BooleanField()
    trustwrapper_result = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        self.pk


def create_profile(sender, instance, created, **kwargs):
    # TODO Create a set of personalanswersettings for the profile
    if created:
        role = Role(name=DEFAULT_ROLE, issharing=True, datastore_owner=instance)
        role.save()

def create_scope(sender, instance, created, **kwargs):
    if created:
        if instance.purpose.all().count() == 0:
            purpose, is_created = Purpose.objects.get_or_create(name=DEFAULT_PURPOSE)
            if is_created:
                purpose.save()
            instance.purpose.add(purpose)
            instance.save()
        profile_list = Profile.objects.all()
        for profile in profile_list: 
            for role in profile.role_owner.all():
                purpose, is_created = Purpose.objects.get_or_create(name=DEFAULT_PURPOSE)
                if is_created:
                    purpose.save()
                pas = PersonalAnswerSetting(scope=instance, sharing_level=0, role=role)
                pas.save()
                pas.purpose.add(purpose)
                pas.save()

def create_role(sender, instance, created, **kwargs):
    # TODO Create a set of personalanswersettings for the profile
    scopes = Scope.objects.all()
    purpose, is_created = Purpose.objects.get_or_create(name=DEFAULT_PURPOSE)
    if is_created:
        purpose.save()
    if created:
        for scope in scopes:
            print scope.name
            print "creating new personal answer setting"
            pas = PersonalAnswerSetting(scope=scope, sharing_level=0, role=instance)
            pas.save()
            pas.purpose.add(purpose)
            pas.save()
            instance.personal_answer_settings.add(pas)
            instance.save()

signals.post_save.connect(create_role, sender=Role)
signals.post_save.connect(create_scope, sender=Scope)
signals.post_save.connect(create_profile, sender=Profile)
