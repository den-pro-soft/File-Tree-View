from django.http import HttpResponse
from django.shortcuts import render
import xml.etree.ElementTree
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# -*- coding: utf-8 -*-
import json

# Make it work for Python 2+3 and with Unicode
import io

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

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
           'opened' : False,
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

			ext = child.attrib['name'].split('.')
			extens = ''
			if len(ext) >= 2:
				if child.attrib['name'][0] != '.':
					extens = ext[1]

			data.append({
				"icon" : "/static/app/assets/file.png",
				"id" : '%s-%s' % (node_id, str(idx)),
				"filename" : child.attrib['name'],
				"size" : child.attrib['size'],
				"type" : extens,
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

#-----This is Searching Algorithm-----------------------

stack = []
json_result = []
def getxmlTojson(element, size):
	global json_result
	global stack

	files = element.findall('file')
	for f in files:
		size += sum([int(f.attrib['size'])])
	directories = element.findall('directory')
	for idx, directory in enumerate(directories):
		stack.append(idx)
		size += getxmlTojson(directory, 0)
		stack.pop()

	field_id = TREE_ELEMENTID_PREFIX

	for idx, d in enumerate(stack):
		if idx:
			field_id += "-"
		field_id += str(d)
	json_result.append({
		'id' : field_id,
		'name' : element.attrib['name'],
		'size' : size,
		'type' : 'Directory',
		'file_cnt' : len(files)
	})
	for idx, f in enumerate(files):
		json_result.append({
			'id' : field_id + "-" + str(len(directories) + idx),
			'name' : f.attrib['name'],
			'size' : f.attrib['size'],
			'type' : 'file',
			'file_cnt' : 0
		})
	return size
#----------------------------------------------

def get_whole_structure(request):
	global json_result

	json_result = []
	node_id = request.GET.get ('node_id', None)
	root = root_xml
	node_id = node_id.replace(TREE_ELEMENTID_PREFIX, '')

	if node_id:
		paths = node_id.split('-')
		for path in paths:
			root = root[int(path)]
	result = getxmlTojson(root, 0)

	return JsonResponse(json_result, safe=False)

#---------------Create User Seleted Json File-----------------
@csrf_exempt
def usersel_json_file(request):
	sel_ids = request.POST.getlist('sel_info[]')
	result = getxmlTojson(root_xml, 0)

	ele_array = []

	for sel_id in sel_ids:
		dir_root = root_xml
		sel_id = sel_id.replace(TREE_ELEMENTID_PREFIX, '')

		if sel_id:
			import pdb; pdb.set_trace()
			paths = sel_id.split('-')
			file_path = ""
			for path in paths:
				dir_root = dir_root[int(path)]
				file_path += "/" + dir_root.attrib['name']
			ele_array.append({
				"User Select Path" : root_xml.attrib['name'] + file_path
			})
	with io.open('file_path.json', 'w', encoding='utf8') as outfile:
		str_ = json.dumps(ele_array, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=True)
		outfile.write(to_unicode(str_))
		response = HttpResponse(str_, content_type="application/json")
		response['Content-Disposition'] = "attachment; filename=file_path.json"
		return response

	return Http404
