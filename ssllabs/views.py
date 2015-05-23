from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib import messages
from django.db import models, Error, IntegrityError
from django.db.models import Count, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .models import Host, Account, Profile

import socket
import csv

#def index(request):
#	host_list = Host.objects.order_by('host')
#	context = {'host_list': host_list}
#	return render(request, 'ssllabs/index.html', context)


#def hosts(request, host_id):
#	host_detail = get_object_or_404(Host, pk=host_id);
#	context = {'host_detail': host_detail}
#	return render(request, 'ssllabs/hosts.html', context)

def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('ssllabs:auth'))

def auth(request):

	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('ssllabs:dashboard'))
			else:
				# Return a 'disabled account' error message
				error = "Account is disabled"

		else:
			error = "Invalid username and/or password"

		context = {'error' : error}
	else:
		context = {}

	return render(request, 'ssllabs/auth.html', context)

@login_required
def dashboard(request):

	account_name = 'All Accounts'
	selected_account_id = request.GET.get('select_account')
	selected_grade = ''
	selected_sig = ''
	selected_rc4 = ''
	
	if selected_account_id:
		kwargs = {}
		selected_account_id = request.GET.get('select_account')
		selected_grade = request.GET.get('grade_filter')
		selected_sig = request.GET.get('sig_filter')
		selected_rc4 = request.GET.get('rc4_filter')

		if selected_account_id != '0':
			kwargs['account_id'] = selected_account_id
			account_name = get_object_or_404(Account, pk=selected_account_id)
		if selected_grade != '':
			kwargs['grade'] = selected_grade
		if selected_sig != '':
			kwargs['signatureAlg'] = selected_sig
		if selected_rc4 != '':
			kwargs['supportsRC4'] = selected_rc4
	else:
		kwargs = {}
		selected_account_id='0'

	h_all = Host.objects.all().filter(**kwargs).order_by('account_id__name', 'host')

	#Export to csv
	if request.GET.get('exportCSV') == 'true':
		return export_to_csv(request, h_all)

	q_grade = Host.objects.all().values('grade').annotate(num_hosts=Count('host')).filter(**kwargs).order_by('grade')
	q_sig_alg = Host.objects.all().values('signatureAlg').annotate(num_hosts=Count('host')).filter(**kwargs).order_by('signatureAlg')
	q_rc4 = Host.objects.all().values('supportsRC4').annotate(num_hosts=Count('host')).filter(**kwargs).order_by('supportsRC4')
	a_all = Account.objects.all().order_by('name')
	q_last_update = Host.objects.all().aggregate(last_update=Max('endTime'))

	last_update = q_last_update['last_update']

	h_all_paginator = Paginator(h_all, settings.PAGE_SIZE)
	page = request.GET.get('page')

	try:
		hosts = h_all_paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		hosts = h_all_paginator.page(1)
	except EmptyPage:
	# If page is out of range (e.g. 9999), deliver last page of results.
		hosts = h_all_paginator.page(h_all_paginator.num_pages)

	#Is anything in the scan queue?
	if h_all.filter(status='QUEUED') or h_all.filter(status='RUNNING'):
		warning = 'At least one record is in the queue to be scanned, or is actively running.  Data may be stale until this completes.'
	else:
		warning = None

	context = {
		'q_result_grade' : q_grade, 
		'q_result_all' : hosts, 
		'account_list' : a_all, 
		'p_account_id' : int(selected_account_id), 
		'p_grade' : selected_grade,
		'p_sig' : selected_sig,
		'p_rc4' : selected_rc4,
		'account_name': account_name, 
		'last_update': last_update, 
		'num_pages': range(h_all_paginator.num_pages), 
		'q_result_sig_alg': q_sig_alg,
		'q_result_rc4' : q_rc4,
		'warning' : warning
	}

	return render(request, 'ssllabs/dashboard.html', context)

@login_required
def managehost(request, host_id = '0'):

	#Get list of accounts
	account_list = Account.objects.all().order_by('name')

	#Add/Edit
	if request.POST:
		hostname = request.POST['hostname']
		account_id = request.POST['account']

		if host_id == '0':
			host_detail = { 'host_id': '0', 'host':hostname, 'account_id_id': int(account_id)}
		else:
			host_detail = get_object_or_404(Host, pk=host_id);

		if hostname == '':
			return render(request, "ssllabs/manage_host.html", {'h': host_detail, 'acc': account_list, 'error_message': "Error: Hostname cannot be blank"})


		#Get list of hostnames
		hostnames = hostname.split(" ")


		#Do all of the hostnames resolve?  If not, then throw and error and don't add anything
		error = False
		for this_hostname in hostnames:
			th = this_hostname.lower().strip()
			try:
				ip = socket.gethostbyname(this_hostname)
			except socket.error as e:
				error = True
				messages.error(request, "Error for "+this_hostname+" : "+e.strerror+".  No hostnames were added.")

		if error:
			return render(request, "ssllabs/manage_host.html", {'h': host_detail, 'acc': account_list})

		for this_hostname in hostnames:

			#Strip and lower
			th = this_hostname.lower().strip()

			#If stripping whitespaces results in no host, continue to next one
			if not th:
				continue

			#Add new record
			host_detail = Host(host=th, account_id=Account(account_id=account_id), status="QUEUED", statusMessage='QUEUED')
			
			#Insert or Update record
			error = False
			try:
				host_detail.save()
				messages.success(request, th+": Hostname Successfully Saved")
			except IntegrityError as e:
				messages.error(request, th+": Hostname Already Exists")
				error = True

			except Error as e:
				error = True
				messages.error(request, th+": "+str(e))
		
		# If an error occured, go back to manage page
		if error:
			host_detail.host = request.POST['hostname']
			return render(request, "ssllabs/manage_host.html", {'h': host_detail, 'acc': account_list})
		
		return HttpResponseRedirect(reverse('ssllabs:listhosts'))

	#Adding a new host
	#Empty object
	
	host_detail = { 'host_id': '0', 'host':''}
		
	context = {'h': host_detail, 'acc': account_list}
	
	return render(request, 'ssllabs/manage_host.html', context)	

@login_required
def scanhost(request, host_id):
	host_detail = get_object_or_404(Host, pk=host_id)
	host_detail.status = "QUEUED"
	host_detail.statusMessage = "QUEUED"
	host_detail.startTime = None
	host_detail.endTime = None
	host_detail.save()

	#Make Qualys API call
	#try:
	#except: 
	
	messages.success(request, "\""+host_detail.host+"\" Successfully Queued for Scan")
	return HttpResponseRedirect(reverse('ssllabs:listhosts'))

@login_required
def deletehost(request, host_id):
	h = get_object_or_404(Host, pk=host_id)
	
	h.delete()

	messages.success(request, "\""+h.host+"\" Successfully Deleted")

	return HttpResponseRedirect(reverse('ssllabs:listhosts'))	

@login_required
def export_to_csv(request, hosts):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="qualys_dashboard.csv"'
	
	writer = csv.writer(response)
	writer.writerow(['Account', 'Hostname', 'Port', 'Status', 'Status Message', 'Start Time', 'End Time', 'IP Address', 'Grade', 'Grade (Trust Ignored)', 'Signature Algorithm', 'Supports RC4', 'Not Before', 'Not After'])
	for h in hosts:
		writer.writerow([h.account_id, h.host, h.port, h.status, h.statusMessage, h.startTime, h.endTime, h.ipAddress, h.grade, h.gradeTrustIgnored, h.signatureAlg, h.supportsRC4, h.notBefore, h.notAfter])
		
	return response

class IndexView(generic.ListView):
	template_name = 'ssllabs/list_hosts.html'
	context_object_name = 'host_list'

	#def get_context_data(self, **kwargs):
		#context = super(IndexView, self).get_context_data(**kwargs)
		#context['account_list'] = Account.objects.order_by('name')
		#context['profile_list'] = Profile.objects.order_by('profileName')
		#return context
    
	def get_queryset(self):
		return Host.objects.order_by('host')

@login_required
class DetailView(generic.DetailView):
    model = Host
    context_object_name = 'host_detail'
    template_name = 'ssllabs/detail.html'