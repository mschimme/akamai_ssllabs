from django.db import models

class Account(models.Model):
	account_id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100, unique=True)
	def __str__(self):
			return self.name

class Host(models.Model):

	host_id = models.AutoField(primary_key=True)
	account_id = models.ForeignKey(Account)
	host = models.CharField(max_length=100, unique=True)
	port = models.IntegerField(default=443)
	status = models.CharField(max_length=20, null=True)
	statusMessage = models.CharField(max_length=100, null=True)
	startTime = models.DateTimeField('Start Time',null=True, blank=True)
	endTime = models.DateTimeField('End Time', null=True, blank=True)
	notBefore = models.DateTimeField('Not Before', null=True, blank=True)
	notAfter = models.DateTimeField('Not After', null=True, blank=True)
	ipAddress = models.GenericIPAddressField(null=True, blank=True)
	grade = models.CharField(max_length=3, null=True, blank=True)
	gradeTrustIgnored = models.CharField(max_length=3, null=True, blank=True)
	signatureAlg = models.CharField(max_length=20, null=True, blank=True)
	supportsRC4 = models.CharField(max_length=10, null=True, blank=True)
	def __str__(self):
			return self.host;

class Profile(models.Model):
	profileId = models.AutoField(primary_key=True)
	profileName = models.CharField(max_length=20, unique=True)
	lastModified = models.DateTimeField('Last Modified')
	def __str__(self):
			return self.profileName

class ProfileHosts(models.Model):
	profileId = models.ForeignKey(Profile)
	host = models.ForeignKey(Host)
