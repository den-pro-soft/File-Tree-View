from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


root_xml = xml.etree.ElementTree.parse('app/assets/test.xml').getroot()

def index(request):

	itemlist = []

	for child in root_xml:
		itemlist.append(child.attrib['name'])

	context = {
		'root': root_xml.attrib['name'],
		'folders': itemlist
	}
	return render(request, 'app/index.html', context)

def get_roots(request):
	data = []
	for idx, child in enumerate(root_xml):
		data.append({
			"id" : 'tree-%s' % str(idx),
			"text" : child.attrib['name'],
			"children" : child.tag == 'directory',
		})
	return JsonResponse(data, safe=False)

@csrf_exempt
def get_children(request):
	parent_id = request.GET.get('id', None)
	paths = parent_id[5:].split('-')
	item = root_xml
	for path in paths:
		item = item[int(path)]

	data = []
	for idx, child in enumerate(item):
		data.append({
			"id" : '%s-%s' % (parent_id, str(idx)),
			"text" : child.attrib['name'],
			"children" : child.tag == 'directory',
		})
	return JsonResponse(data, safe=False)
