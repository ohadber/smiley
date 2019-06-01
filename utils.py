"""
Implement utils for the server
"""
from itertools import chain

import cognitive_face as cf
from multiprocessing.pool import ThreadPool
from PIL import Image

# Key for the Azure sever
KEY = '657e81b8babc4e1c878611cca0ca807a'

# Replace with your regional Base URL
BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/'

# Pool thread size per client.
MAX_THREAD_PER_CLIENT = 10

# Maximum timeout for all the detection requests should be done. A long
# timeout is applied in order to allow a large number of photos to
# be analyzed.
MAX_DETECT_TIMEOUT = 60


class Face:
    """
    Represents a single face.
    """
    def __init__(self, raw_data, photo):
        """
        :param dict raw_data: The raw data returned about the face.
        :param Photo photo: The photo that this face was captured in.
        """
        self.uid = raw_data['faceId']
        self.photo = photo

        self.attrs = raw_data['faceAttributes']
        self.age = self.attrs['age']
        self.gender = self.attrs['gender']

        rec = raw_data['faceRectangle']  # Face size
        self.size = rec['width'] * rec['height']


class Photo:
    """
    Represents an image.
    """
    def __init__(self, file_handle):
        """
        :param file_handle: A handle to the file.
        :type file_handle: werkzeug.datastructures.FileStorage
        """
        self.file_handle = file_handle

        # Following variables will be initialized when `analyze_image` will
        # be called.
        self.size = None
        self.uid_to_face = dict()

    def analyze_image(self):
        """
        Get the image size and detect the faces in the image.
        """
        height, width = Image.open(self.file_handle).size
        self.size = height * width

        self.file_handle.seek(0)
        result = cf.face.detect(self.file_handle, attributes='age,gender',
                                landmarks=True)
        self.uid_to_face = {face['faceId']: Face(face, self) for face in result}

    def __contains__(self, face):
        """
        Check if the person exists in the image.

        :param Face face: The face detection object that we're going to match.
        :return: True if the face exists, Otherwise, False.
        :rtype: bool.
        """
        return face.uid in self.uid_to_face.keys()


def init_azure_client():
    """
    Initialize the Azure photo detection client.
    """
    cf.Key.set(KEY)
    cf.BaseUrl.set(BASE_URL)


def get_common_face_uids(photos):
    """
    Get the Face objects that relates to the most common person in the
    received photos

    :param list photos: The photos to search in.
    :return: The Face objects of the most recognized face.
    :rtype: list of Face
    """
    faces_lsts = map(lambda x: x.uid_to_face.values(), photos)
    faces = list(chain(*faces_lsts))
    faces_uids = [x.uid for x in faces]

    if len(faces_uids) <= 1:
        return _get_faces_by_uids(faces_uids, faces)

    result = cf.face.group(list(faces_uids))
    if len(result['groups']) > 0:
        # UIDs of the most common face.
        face_uids = result['groups'][0]
    else:
        # There no determined 'most common face' - return just one of
        # the faces.
        face_uids = [result['messyGroup'][0]]
    return _get_faces_by_uids(face_uids, faces)


def _get_faces_by_uids(uids, faces):
    """
    Get the faces with the corresponding UIDs from the faces list

    :param uids: The face UIDs to search in the faces list.
    :param faces: The faces list.
    :return: The faces with the searched UIDs
    :rtype: list of Face
    """
    face_anaylzes = []
    for uid in uids:
        for face in faces:
            if uid == face.uid:
                face_anaylzes.append(face)
                continue
    return face_anaylzes


def get_best_face(faces):
    """
    Get the face recognition with the "best picture". The best picture is
    defined to be the picture that the face has the best face-size to
    image-size ratio.

    :param faces: The detected faces.
    :return: The best face recognition within received faces.
    :rtype: Face
    """
    best_ratio = 0
    best_analyze = None

    for face in faces:
        ratio = face.size / face.photo.size
        if ratio > best_ratio:
            best_analyze = face
            best_ratio = ratio

    return best_analyze


def get_best_most_common_face(files):
    """
    The the best photo of the most common face.

    :param list files: A list of the most common files.
    :return: The best face detection
    :rtype: Face
    """
    photo_lst = []
    for f in files:
        photo_lst.append(Photo(f))

    results = []
    for photo in photo_lst:
        pool = ThreadPool(MAX_THREAD_PER_CLIENT)
        result = pool.apply_async(photo.analyze_image)
        results.append(result)

    [res.get(timeout=MAX_DETECT_TIMEOUT) for res in results]

    faces = get_common_face_uids(photo_lst)
    return get_best_face(faces)
