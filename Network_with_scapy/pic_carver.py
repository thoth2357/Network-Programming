# importing packages
import re
import zlib
import cv2
from scapy.all import *

# Defining directories
pic_directory = '~/Pictures/Pics'
faces_directory = '~/Pictures/Faces'

pcap_file = '192.168.43.74_capture.pcap'

def get_http_headers(http_payload):
    'Http header passing function.Splits out the headers from the HTTP traffic using regular expression.'
    try:
        # split the headers off it it is HTTP traffic
        headers_raw = http_payload[:http_payload.index('\r\n\r\n') + 2]

        # break out the headers
        headers = dict(re.findall(r"(?P<'name>.*?): (?P<value>.*?)\r\n",headers_raw))
    except:
        return None
    if 'Content-Type' not in headers:
        return None
    return headers

def extract_image(headers, http_payload):
    ''' Takes the HTTP headers and determines whether we received an image in the HTTP response. If we detect that the Content-Type header does indeed contain the image MIME type, we split out the type of image; and if there is compression 
    applied to the image in transit, we attempt to decompress it before returning the image type and the raw image buffer.'''
    
    image = None
    image_type = None
    try:
        if 'image' in headers['Content-Type']:
            # grab the image and image body
            image_type = headers['Content-Type'].split('/')[1]
            image = http_payload[http_payload.index('\r\n\r\n') + 4:]
            
            # if we detect compression decompress the image
            try:
                if 'Content-Encoding' in headers.keys():
                    if headers['Content-Encoding'] == 'gzip':
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == 'deflate':
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None, None
    return image, image_type

def face_detect(path, file_name):
    'detect if there is a human face in any of the images we retrieved'
    img  = cv2.imread(path)
    cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return False
    rects[:, 2:] += rects[:, :2]

    # highlight the faces in the image
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img(x1, y1), (x2,y2),(127,555,0),2)
    cv2.imwrite("%s/%s-%s" % (faces_directory,pcap_file,file_name),img)
    return True

def http_assembler(pcap_file):
    'main skeleton'
    carved_images = 0
    faces_detected = 0

    a = rdpcap(pcap_file)

    # separating the Tcp sessions into dictionaries
    sessions = a.sessions()
    for session in sessions:
        http_payload = ''
        for packet in sessions[session]:
            try:
                if packet['TCP'].dport == 80 or packet['TCP'].sport == 80:
                    # filtering out only the HTTP traffic and concatenating the payload of all of the HTTP traffic
                    # reassemble the stream
                    http_payload += str(packet['TCP'].payload)
            except:
                pass
        # passing our reassembled http data to our HTTP header function
        headers = get_http_headers(http_payload)
        if headers is None: # validating that we receiving an image in our http response
            continue
        image,image_type = extract_image(headers,http_payload) # extracting the raw_image from the http response

        if image is not None and image_type is not None:
            # storing the image
            file_name = '%s -pic_carver_%d.%s' %(pcap_file,carved_images, image_type)
            fd = open('%s/%s'%(pic_directory, file_name),'wb')
            fd.write(image)
            fd.close()

            carved_images += 1

            # now attempt face detection
            try:
                # passing the file path to our face detection function
                result = face_detect('%s/%s'%(pic_directory,file_name),file_name)
                if result is True:
                    faces_detected += 1
            except:
                    pass

    return carved_images, faces_detected

carved_images, faces_detected = http_assembler(pcap_file)
print('EXtracted %d images'% carved_images)
print('Detected %d faces'% faces_detected)
