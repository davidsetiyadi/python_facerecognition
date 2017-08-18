from openerp import models

import numpy as np
import cv2
import dlib
import face_recognition
import urllib
import base64
from common import clock, draw_str

class hr_employee(models.Model):
	_inherit = 'hr.employee'

	def action_take_picture(self, cr, uid, ids, context=None):

		if context is None:
			context = {}

		res_model, res_id = self.pool.get(
			'ir.model.data').get_object_reference(cr, uid,
												  'hr_webcam',
												  'action_take_photo')
		dict_act_window = self.pool.get(
			'ir.actions.client').read(cr, uid, res_id, [])
		if not dict_act_window.get('params', False):
			dict_act_window.update({'params': {}})
		dict_act_window['params'].update(
			{'employee_id': len(ids) and ids[0] or False})
		return dict_act_window
	
	def detect(img, cascade):
		rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
		                             flags=cv2.CASCADE_SCALE_IMAGE)
		if len(rects) == 0:
			return []
		rects[:,2:] += rects[:,:2]
		return rects

	def draw_rects(img, rects, color):
		for x1, y1, x2, y2 in rects:
			cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

	def action_take_opencv(self, cr, uid, ids, context=None):
		print 'David_____________TESTET'
		employee_obj = self.pool.get('hr.employee')
		employee_ids = employee_obj.search(cr,uid,[],limit=3)
		print employee_ids,'employee_idsss'
		dictionary = {}
		face_encoding = {}
		for employee in employee_ids:
			employees = employee_obj.browse(cr,uid,employee)
			# dictionary[employees.name] = "http://127.0.6.1:7777/web/binary/image?model=hr.employee&field=image_medium&id="+str(employee)
			# urllib.urlretrieve("/web/binary/image?model=hr.employee&field=image_medium&id="+str(employee), str(employee)+"_uid.png")
			imgstring = employees.image_medium
			print imgstring
			imgdata = base64.b64decode(imgstring)
			filename = 'some_image.png'  # I assume you have a way of picking unique filenames
			with open(filename, 'wb') as f:
			    f.write(imgdata)
			# dictionary[employees.name] = face_recognition.load_image_file("http://127.0.6.1:7777/web/binary/image?model=hr.employee&field=image_medium&id="+str(employee))
			# print dictionary[employee.name],'dictionaryyyy'
			# face_encoding [employees.name] = face_recognition.face_encodings(dictionary[employees.name][0])
		# c = {}
		# for b in a:
		# c[b]=b+1
		# data = []
		# for a in dictionary:
			# data.append(dictionary[a])

		# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
		# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
		# unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
		# print ("david123")
		# known_faces = [
		#     biden_face_encoding,
		#     obama_face_encoding
		# ]

		# # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
		# results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
		print dictionary