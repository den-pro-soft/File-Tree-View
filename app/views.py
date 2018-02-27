from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


root_xml = xml.etree.ElementTree.parse('app/assets/test.xml').getroot()

def index(request):
	return render(request, 'app/index.html')

def get_roots(request):
	result_data = []
	data = [{
		"id" : 'tree-#',
		"text" : root_xml.attrib['name'],
		'state' : {
           'opened' : True,
           'selected' : False
        },
	}]

	children = []
	for idx, child in enumerate(root_xml):
		children.append({
			"id" : 'tree-%s' % str(idx),
			"text" : child.attrib['name'],
			"children" : child.tag == 'directory',
		})
	data[0]['children'] = children
	# import pdb;
	# pdb.set_trace();
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
		if child.tag == 'directory':
			data.append({
				"id" : '%s-%s' % (parent_id, str(idx)),
				"text" : child.attrib['name'],
				"children" : child.tag == 'directory',
			})
	return JsonResponse(data, safe=False)

def get_listdata(request):
	node_id = request.GET.get('node_id', None)
	if node_id != 'rootdir':
		paths = node_id[5:].split('-')
		item = root_xml
		for path in paths:
			item = item[int(path)]
	else:
		item = root_xml
	data = []
	for idx, child in enumerate(item):
		if child.tag == 'file':
			data.append({
				"icon" : "icon",
				"id" : '%s-%s' % (node_id, str(idx)),
				"filename" : child.attrib['name'],
				"size" : child.attrib['size'],
				"type" : 'file',
				"last modified" : child.attrib['modify_time'],
			})
		else:
			data.append({
				"icon" : "icon",
				"id" : '%s-%s' % (node_id, str(idx)),
				"filename" : child.attrib['name'],
				"size" : ' ',
				"type" : 'Directory',
				"last modified" : ' ',
			})

	return JsonResponse(data, safe=False)
