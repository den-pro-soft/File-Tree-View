from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


root_xml = xml.etree.ElementTree.parse('app/static/app/assets/test.xml').getroot()
TREE_ELEMENTID_PREFIX = 'tree-'

def index(request):
	return render(request, 'app/index.html')

def get_roots(request):
	result_data = []
	data = [{
		"id" : TREE_ELEMENTID_PREFIX,
		"text" : root_xml.attrib['name'],
		'state' : {
           'opened' : True,
           'selected' : False
        },
	}]

	children = []
	for idx, child in enumerate(root_xml):
		have_dir = False
		for child_again in child.getchildren():
			if child_again.tag == 'directory':
				have_dir = True
				break
		if child.tag == 'directory':
			have_dir_cls = '' if have_dir else 'jstree-leaf'
			children.append({
				"id" : '%s%s' % (TREE_ELEMENTID_PREFIX, str(idx)),
				"text" : child.attrib['name'],
				"children" : child.tag == 'directory',
				"li_attr": {'class': have_dir_cls}
			})

	data[0]['children'] = children
	return JsonResponse(data, safe=False)

@csrf_exempt
def get_children(request):
	parent_id = request.GET.get('id', None)
	paths = parent_id[5:].split('-')
	item = root_xml
	for path in paths:
		item = item[int(path)]

	children = []
	for idx, child in enumerate(item):
		have_dir = False
		for child_again in child.getchildren():
			if child_again.tag == 'directory':
				have_dir = True
				break
		if child.tag == 'directory':
			have_dir_cls = '' if have_dir else 'jstree-leaf'
			children.append({
				"id" : '%s-%s' % (parent_id, str(idx)),
				"text" : child.attrib['name'],
				"children" : child.tag == 'directory',
				"li_attr": {'class': have_dir_cls}
			})
	return JsonResponse(children, safe=False)

def get_listdata(request):
	node_id = request.GET.get('node_id', None)
	checked_status = True if request.GET.get('checked', None) == 'true' else False
	paths = node_id[5:].split('-')
	item = root_xml
	if paths != ['']:
		for path in paths:
			item = item[int(path)]
	data = []

	if node_id == TREE_ELEMENTID_PREFIX:
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

cnt_files = 0

def get_size_from_node(element, size):
	"""Recursively prints the tree."""
	global cnt_files
	files = element.findall('file')
	cnt_files += len(files)
	size += sum([int(f.attrib['size']) for f in files])

	directories = element.findall('directory')
	for directory in directories:
		size = get_size_from_node(directory, size)
	return size

def get_all_files(request):
	global cnt_files
	cnt_files = 0
	node_id = request.GET.get ('node_id', None)
	root = root_xml
	node_id = node_id.replace(TREE_ELEMENTID_PREFIX, '')
	if node_id:
		paths = node_id.split('-')
		for path in paths:
			root = root[int(path)]
	total_size = get_size_from_node(root, 0)
	result = {
		"selNode_size" : total_size,
		"selfile_count" : cnt_files
	}
	return JsonResponse(result, safe=False)

# def get_filesize(request):
# 	ode_id = request.GET.get('node_id', None)
# 	paths = node_id[5:].split('-')
# 	item = root_xml
# 	if paths != ['']:
# 		for path in paths:
# 			item = item[int(path)]
#
