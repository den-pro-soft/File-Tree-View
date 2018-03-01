from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


root_xml = xml.etree.ElementTree.parse('app/static/app/assets/test.xml').getroot()

def index(request):
	return render(request, 'app/index.html')

def get_roots(request):
	result_data = []
	data = [{
		"id" : 'tree-',
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
	checked_status = True if request.GET.get('checked', None) == 'true' else False
	paths = node_id[5:].split('-')
	item = root_xml
	if paths != ['']:
		for path in paths:
			item = item[int(path)]
	data = []

	if node_id == "tree-":
		node_id = "tree"
	for idx, child in enumerate(item):
		if child.tag == 'file':
			ext = ''
			for ex in child.attrib['name'][::-1]:
				if ex == '.':
					break;
				ext += ex

			if len(ext) == len(child.attrib['name']) or len(ext) >= 4:
				ext = 'txEoN'
			data.append({
				"icon" : "/static/app/assets/file.png",
				"id" : '%s-%s' % (node_id, str(idx)),
				"filename" : child.attrib['name'],
				"size" : child.attrib['size'],
				"type" : ext[::-1],
				"last modified" : child.attrib['modify_time'],
				"selected" : checked_status
			})
		else:
			data.append({
				"icon" : "/static/app/assets/folder.png",
				"id" : '%s-%s' % (node_id, str(idx)),
				"filename" : child.attrib['name'],
				"size" : ' ',
				"type" : 'Directory',
				"last modified" : '',
				"selected" : checked_status
			})
	return JsonResponse(data, safe=False)
