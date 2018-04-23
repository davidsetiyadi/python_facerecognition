import face_recognition
import cv2
import os
import os.path
import psycopg2
import logging
import time


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        logger.info(self.mogrify(sql, args))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception, exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise
# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(1)

# Load a sample picture and learn how to recognize it.
# david_image = face_recognition.load_image_file("david.jpg")
# david_face_encoding = face_recognition.face_encodings(david_image)[0]

# Load a second sample picture and learn how to recognize it.
# irvan_image = face_recognition.load_image_file("irvan.jpg")
# irvan_face_encoding = face_recognition.face_encodings(irvan_image)[0]
def nothing(x):
    pass

#Initialize some variable
known_face_names = []
known_face_encodings = []
n = 0
for image_file in os.listdir("image_database"):
	full_file_path = os.path.join("image_database", image_file)
	known_face_names.append(image_file[:-4])
	david_image = face_recognition.load_image_file(full_file_path)
	david_face_encoding = face_recognition.face_encodings(david_image)[0]

	known_face_encodings.append(david_face_encoding)
	print("Looking for faces in {}".format(image_file))
	n +=1	
# Create arrays of known face encodings and their names
# known_face_encodings = [
# 	david_face_encoding,
# 	irvan_face_encoding
# ]
# known_face_names = [
# 	"David",
# 	"irvan"
# ]
#For Connect to databases
db = psycopg2.connect("dbname='v8_TA'")
db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
# cr = openerp.sql_db.db_connect(partner.database).cursor()
# pool = pooler.get_pool(cr.dbname)
# employee_obj = pool.get('hr.employee')
# employe_ids = employee_obj.search(cr, 1, [])
# conn = psycopg2.connect(DSN)
cur = db.cursor(cursor_factory=LoggingCursor)
# cur.execute("select login,id from res_users")
# for row in cur.fetchall():
# 	print ('rowwwwwww',row)
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
# create switch for ON/OFF functionality
switch = 'Sign OUT'
#Hi *** you was sign in at %s
cv2.namedWindow('Attendance Facerecogniton')
cv2.createTrackbar(switch, 'Attendance Facerecogniton',0,1,nothing)	
while True:
	# Get positioning tracbar
	s = cv2.getTrackbarPos(switch,'Attendance Facerecogniton')
	# print ('sssss',s)
	# Grab a single frame of video
	ret, frame = video_capture.read()

	# Resize frame of video to 1/4 size for faster face recognition processing
	small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

	# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	rgb_small_frame = small_frame[:, :, ::-1]

	# Only process every other frame of video to save time
	if process_this_frame:
		# Find all the faces and face encodings in the current frame of video
		face_locations = face_recognition.face_locations(rgb_small_frame)
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

		face_names = []
		for face_encoding in face_encodings:
			# See if the face is a match for the known face(s)
			matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
			name = "Unknown"

			# If a match was found in known_face_encodings, just use the first one.
			if True in matches:
				first_match_index = matches.index(True)
				name = known_face_names[first_match_index]
				cur.execute("select id from hr_employee where name_related = %s",(name,))
				employe_ids = cur.fetchall()
				print (employe_ids,'employe_ids')
				date_start = time.strftime('%Y-%m-%d 00:00:00')
				date_stop = time.strftime('%Y-%m-%d 23:59:59')
				if employe_ids:
					vals = ('action',employe_ids[0][0],'2018 04 22 17:46:34')
					print ('testset',time.strftime('%Y-%m-%d %H:%M:%S') ,vals)
					if s == 0:
						action = 'sign_in'
						cur.execute("select id from hr_attendance where name >= %s and name <= %s and employee_id = %s and action ='sign_in' ",(date_start,date_stop,employe_ids[0][0]))
						attendance_ids = cur.fetchall()
						if not attendance_ids:
							cur.execute("INSERT INTO hr_attendance (action,employee_id,name) VALUES (%s,%s,%s)",(action,employe_ids[0][0],time.strftime('%Y-%m-%d %H:%M:%S')) )
					# cur.execute("INSERT INTO hr_attendance (action,employee_id,name) VALUES (%s,%s,%s)",('action',employe_ids[0][0],time.strftime('%Y-%m-%d %H:%M:%S')) )
					# cur.commit()
					if s == 1:
						action = 'sign_out'
						cur.execute("select id from hr_attendance where name >= %s and name <= %s and employee_id = %s and action ='sign_out' ",(date_start,date_stop,employe_ids[0][0]))
						attendance_ids = cur.fetchall()
						if not attendance_ids:
							cur.execute("INSERT INTO hr_attendance (action,employee_id,name) VALUES (%s,%s,%s)",(action,employe_ids[0][0],time.strftime('%Y-%m-%d %H:%M:%S')) )
				# employe_ids = employee_obj.search(cr, uid, [('name','=',name)])
				# if employe_ids:
				# 	print 'employeee_id',employe_ids
				# 	vals = {'action':'action','employee_id':employe_ids[0]}
				# 	context = {}					
				# 	attendance_obj.create(cr, uid, vals, context=context)
			face_names.append(name)

	process_this_frame = not process_this_frame


	# Display the results
	for (top, right, bottom, left), name in zip(face_locations, face_names):
		# Scale back up face locations since the frame we detected in was scaled to 1/4 size
		top *= 4
		right *= 4
		bottom *= 4
		left *= 4

		# Draw a box around the face
		cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

		# Draw a label with a name below the face
		cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
		font = cv2.FONT_HERSHEY_DUPLEX
		cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


    # cvCreateButton(nameb2,callbackButton,nameb2,CV_CHECKBOX,0);
	
	cv2.imshow('Attendance Facerecogniton', frame)

	# Hit 'q' on the keyboard to quit!
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
