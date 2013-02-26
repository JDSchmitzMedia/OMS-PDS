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

connect(settings.MONGODB_DATABASE)


class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)
    isinit = models.BooleanField(default=False)


def create_tw(sender, instance, created, **kwargs):
    # Check if the trust wrapper has been initialized.  Note: this may need to be a callback to a authrorization server for default values at some point... 
    print instance.isinit
    if instance.isinit == False:
        p0 = Purpose(name="PDS", datastore_owner=instance)
        p0.save()
        s0 = SharingLevel(level = 0, datastore_owner=instance, isselected = True)
        s1 = SharingLevel(level = 1, datastore_owner=instance, isselected = False)
        s2 = SharingLevel(level = 2, datastore_owner=instance, isselected = False)
        s3 = SharingLevel(level = 3, datastore_owner=instance, isselected = False)
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
        instance.isinit = True;
	instance.save()

signals.post_save.connect(create_tw, sender=Profile)

    
class ResourceKey(models.Model):
    ''' A way of controlling sharing within a collection.  Maps to any key within a collection.  For example, funf probes and individual answers to questions'''
    key = models.CharField(max_length=120)
    issharing = models.BooleanField(default=True)

class ProbeGroupSetting(models.Model):
    ''' A way of grouping resource keys for sharing.'''
    name = models.CharField(max_length=120)
    issharing = models.BooleanField(default=False)
    keys = models.ManyToManyField(ResourceKey) #a list of roles the user is currently sharing with

class Purpose(models.Model):
    name = models.CharField(max_length=120)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="purpose_owner")

class Scope(models.Model):
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
    issharing = models.BooleanField(default=True)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="scope_owner")

class Role(models.Model):
    """ @name : The user defined name of the role
        @purpose : A list of purposes associated with this role
        @tokens : A list of oauth tokens of users assigned to this role """
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
    issharing = models.BooleanField(default=False)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="role_owner")
    # TODO: fill in field for tokens (rather than ints / uuids)

class SharingLevel(models.Model):
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
