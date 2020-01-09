import io
import os
import time

from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict

import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/triznam/Downloads/API_Project-87969f455695.json"
client = vision.ImageAnnotatorClient()

image_list = os.listdir('thumbnails')

google_results = []
for image_name in image_list[:5]:
	if image_name.endswith('.jpg'):
		try:
			start_time = time.perf_counter()
			image_id = image_name.split('.')[0]
			#print(image_id)
			image_path = os.path.join('thumbnails',image_name)
			with io.open(image_path, 'rb') as image_file:
			    content = image_file.read()
			image = types.Image(content=content)
			response = client.annotate_image({
			    'image': {'content': content},
			    'features': [{'type':vision.enums.Feature.Type.LABEL_DETECTION},
			                 {'type':vision.enums.Feature.Type.OBJECT_LOCALIZATION},
			                 {'type':vision.enums.Feature.Type.WEB_DETECTION}
			                ]
			})
			response_dict = MessageToDict(response, preserving_proto_field_name = True)
			response_dict['image_id'] = image_id
			elapsed_time = time.perf_counter() - start_time
			response_dict['elapsed_time'] = elapsed_time
			google_results.append(response_dict)
		except:
			print(image_id)

with open('google_results.json','w') as google_out:
	json.dump(google_results, google_out, indent=2)
