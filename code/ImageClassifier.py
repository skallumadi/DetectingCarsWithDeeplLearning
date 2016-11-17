#  this is a very slightly modified version of the example code that was pulled from the nvidia digits files
import os, time
import tarfile, tempfile, zipfile
import cv2, PIL.Image
import scipy.misc
import numpy as np
from google.protobuf import text_format

os.environ['GLOG_minloglevel'] = '2'  # suppress caffe output  # must be done before importing caffe
import caffe
from caffe.proto import caffe_pb2


class ImageClassify:
    def __init__(self, archive_path):
        self.archive_path = archive_path

    def get_net(self, caffemodel, deploy_file, use_gpu=True):
        """
        Returns an instance of caffe.Net

        Arguments:
        caffemodel -- path to a .caffemodel file
        deploy_file -- path to a .prototxt file

        Keyword arguments:
        use_gpu -- if True, use the GPU for inference
        """
        if use_gpu:
            caffe.set_mode_gpu()

        # load a new model
        return caffe.Net(deploy_file, caffemodel, caffe.TEST)

    @staticmethod
    def get_transformer(deploy_file, mean_file=None):
        """
        Returns an instance of caffe.io.Transformer

        Arguments:
        deploy_file -- path to a .prototxt file

        Keyword arguments:
        mean_file -- path to a .binaryproto file (optional)
        """
        network = caffe_pb2.NetParameter()
        with open(deploy_file) as infile:
            text_format.Merge(infile.read(), network)

        if network.input_shape:
            dims = network.input_shape[0].dim
        else:
            dims = network.input_dim[:4]

        t = caffe.io.Transformer(
            inputs={'data': dims}
        )
        t.set_transpose('data', (2, 0, 1))  # transpose to (channels, height, width)

        # color images
        if dims[1] == 3:
            # channel swap
            t.set_channel_swap('data', (2, 1, 0))

        if mean_file:
            # set mean pixel
            with open(mean_file, 'rb') as infile:
                blob = caffe_pb2.BlobProto()
                blob.MergeFromString(infile.read())
                if blob.HasField('shape'):
                    blob_dims = blob.shape
                    assert len(blob_dims) == 4, 'Shape should have 4 dimensions - shape is "%s"' % blob.shape
                elif blob.HasField('num') and blob.HasField('channels') and \
                        blob.HasField('height') and blob.HasField('width'):
                    blob_dims = (blob.num, blob.channels, blob.height, blob.width)
                else:
                    raise ValueError('blob does not provide shape or 4d dimensions')
                pixel = np.reshape(blob.data, blob_dims[1:]).mean(1).mean(1)
                t.set_mean('data', pixel)

        return t

    @staticmethod
    def load_image(path, height, width, mode='RGB'):
        """
        Load an image from disk

        Returns an np.ndarray (channels x width x height)

        Arguments:
        path -- path to an image on disk
        width -- resize dimension
        height -- resize dimension

        Keyword arguments:
        mode -- the PIL mode that the image should be converted to
            (RGB for color or L for grayscale)
        """
        image = PIL.Image.open(path)
        image = image.convert(mode)
        image = np.array(image)
        # squash
        image = scipy.misc.imresize(image, (height, width), 'bilinear')

        return image

    @staticmethod
    def forward_pass(images, net, transformer, batch_size=None):
        """
        Returns scores for each image as an np.ndarray (nImages x nClasses)

        Arguments:
        images -- a list of np.ndarrays
        net -- a caffe.Net
        transformer -- a caffe.io.Transformer

        Keyword arguments:
        batch_size -- how many images can be processed at once
            (a high value may result in out-of-memory errors)
        """
        if batch_size is None:
            batch_size = 1

        caffe_images = []
        for image in images:
            if image.ndim == 2:
                caffe_images.append(image[:, :, np.newaxis])
            else:
                caffe_images.append(image)

        dims = transformer.inputs['data'][1:]

        scores = None
        for chunk in [caffe_images[x:x + batch_size] for x in xrange(0, len(caffe_images), batch_size)]:
            new_shape = (len(chunk),) + tuple(dims)
            if net.blobs['data'].data.shape != new_shape:
                net.blobs['data'].reshape(*new_shape)
            for index, image in enumerate(chunk):
                image_data = transformer.preprocess('data', image)
                net.blobs['data'].data[index] = image_data
            start = time.time()
            output = net.forward()[net.outputs[-1]]
            end = time.time()
            if scores is None:
                scores = np.copy(output)
            else:
                scores = np.vstack((scores, output))
                # print 'Processed %s/%s images in %f seconds ...' % (len(scores), len(caffe_images), (end - start))

        return scores

    @staticmethod
    def read_labels(labels_file):
        """
        Returns a list of strings

        Arguments:
        labels_file -- path to a .txt file
        """
        if not labels_file:
            print 'WARNING: No labels file provided. Results will be difficult to interpret.'
            return None

        labels = []
        with open(labels_file) as infile:
            for line in infile:
                label = line.strip()
                if label:
                    labels.append(label)
        assert len(labels), 'No labels found'
        return labels

    def classify(self, caffemodel, deploy_file, image_files,
                 mean_file=None, labels_file=None, batch_size=None, use_gpu=True):
        """
        Classify some images against a Caffe model and return the results in a list
        The returned list is in the form of [('Label', PercentageConfidence), ('Label', PercentageConfidence)]

        Arguments:
        caffemodel -- path to a .caffemodel
        deploy_file -- path to a .prototxt
        image_files -- list of paths to images

        Keyword arguments:
        mean_file -- path to a .binaryproto
        labels_file path to a .txt file
        use_gpu -- if True, run inference on the GPU
        """
        # Load the model and images
        net = self.get_net(caffemodel, deploy_file, use_gpu)
        transformer = self.get_transformer(deploy_file, mean_file)
        _, channels, height, width = transformer.inputs['data']
        if channels == 3:
            mode = 'RGB'
        elif channels == 1:
            mode = 'L'
        else:
            raise ValueError('Invalid number for channels: %s' % channels)
        images = [self.load_image(image_file, height, width, mode) for image_file in image_files]
        labels = self.read_labels(labels_file)

        # Classify the image
        scores = self.forward_pass(images, net, transformer, batch_size=batch_size)

        # Process the results
        indices = (-scores).argsort()[:, :5]  # take top 5 results
        classifications = []
        for image_index, index_list in enumerate(indices):
            result = []
            for i in index_list:
                # 'i' is a category in labels and also an index into scores
                if labels is None:
                    label = 'Class #%s' % i
                else:
                    label = labels[i]
                result.append((label, round(100.0 * scores[image_index, i], 4)))
            classifications.append(result)

        # classifications is in the form of [('Occupied', 100.0), ('Empty', 0.0)]
        # originally this function just printed out results. modified to send an array with the results and labels
        # for use elsewhere in the program
        return classifications

    @staticmethod
    def unzip_archive(archive):
        """
        Unzips an archive into a temporary directory
        Returns a link to that directory

        Arguments:
        archive -- the path to an archive file
        """
        assert os.path.exists(archive), 'File not found - %s' % archive

        tmpdir = os.path.join(tempfile.gettempdir(),
                              os.path.basename(archive))
        assert tmpdir != archive  # That wouldn't work out

        if os.path.exists(tmpdir):
            # files are already extracted
            pass
        else:
            if tarfile.is_tarfile(archive):
                print 'Extracting tarfile ...'
                with tarfile.open(archive) as tf:
                    tf.extractall(path=tmpdir)
            elif zipfile.is_zipfile(archive):
                print 'Extracting zipfile ...'
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(path=tmpdir)
            else:
                raise ValueError('Unknown file type for %s' % os.path.basename(archive))
        return tmpdir

    def classify_with_archive(self, image_files, batch_size=None, use_gpu=True):
        """
        """
        archive = self.archive_path
        tmpdir = self.unzip_archive(archive)
        caffemodel = None
        deploy_file = None
        mean_file = None
        labels_file = None
        for filename in os.listdir(tmpdir):
            full_path = os.path.join(tmpdir, filename)
            if filename.endswith('.caffemodel'):
                caffemodel = full_path
            elif filename == 'deploy.prototxt':
                deploy_file = full_path
            elif filename.endswith('.binaryproto'):
                mean_file = full_path
            elif filename == 'labels.txt':
                labels_file = full_path

        assert caffemodel is not None, 'Caffe model file not found'
        assert deploy_file is not None, 'Deploy file not found'

        return self.classify(caffemodel, deploy_file, image_files,
                             mean_file=mean_file, labels_file=labels_file,
                             batch_size=batch_size, use_gpu=use_gpu)


class ImageProcessor:
    def __init__(self, networkArchive, parkingLot):
        self.classifier = ImageClassify(networkArchive)
        self.parkinglot = parkingLot

    def divide_image(self, cv2_image):
        """Gets a list of parking spot ids and their specific sections of the given image.
           Then saves all images to a folder, named after their ID
        """

        img = cv2_image
        # [ [id, location], [id, location], ... ]
        infolist = zip([x.id for x in self.parkinglot.getParkingSpots()],
                       [x.location for x in self.parkinglot.getParkingSpots()])
        # [ [id, image], [id, image], ... ]
        cropped_images = [[str(x[0]), self.get_subimage(img, x[1])] for x in infolist]

        # must delete all images every time you write the list, or some changes will not be accurately shown
        for filename in os.listdir('cropped_images/'):
            try:
                os.remove('cropped_images/' + filename)
            except OSError:
                pass
        for img in cropped_images:
            cv2.imwrite('cropped_images/' + img[0] + '.jpg', img[1])

    @staticmethod
    def get_subimage(img, location):
        """ Returns a cv2 image.
            The image is rotated and cropped based on the given location
        """
        image_size = (len(img), len(img[0]))

        # need to get the stored location list into something more typical.
        # so from [x,y,x,y,...] to [[x,y],[x,y],...]
        loc_list = []
        for i in range(0, 8, 2):
            loc_list.append([location[i], location[i + 1]])
        numpy_loc = np.array(loc_list)

        # rotated rectangles are the way to go here, which this is.
        rectangle = cv2.minAreaRect(numpy_loc)
        box = np.int0(numpy_loc)

        angle = rectangle[2]
        center = rectangle[0]
        size = list(rectangle[1])
        size = [int(size[0]), int(size[1])]

        if angle < -45:
            angle += 90.0
            holder = size[0]
            size[0] = size[1]
            size[1] = holder

        m = cv2.getRotationMatrix2D(center, angle, 1.0)
        # for some reason the size of this needs to cover the area of the original box. so the size of original image
        # update, i have no idea, but a large size fixes it. so i just made it larger than it could ever need to be
        rotated = cv2.warpAffine(img, m, (image_size[0] + 500, image_size[1] + 500))
        cropped = cv2.getRectSubPix(rotated, (int(size[0]), int(size[1])), (center[0], center[1]))

        return cropped

    def get_results(self, cv2_image):
        """return a list of the shape
              [[id, [(Label, confidence)]
              now revised to [[id, most likely label], ...]
        """
        self.divide_image(cv2_image)
        image_names = os.listdir('cropped_images/')
        # no parking spots = crashing, so handle it
        if not image_names:
            return []
        listofimages = ['cropped_images/' + x for x in image_names]

        ids = [x[:-4] for x in image_names]

        confidences = self.classifier.classify_with_archive(listofimages) #######################################3

        winning_labels = []
        for item in confidences:
            l1 = item[0]
            l2 = item[1]

            if l1[1] > l2[1]:
                winning_labels.append(l1[0])
            else:
                winning_labels.append(l2[0])

        results = zip(ids, winning_labels)
        return results


if __name__ == '__main__':
    path = '/home/alloba/Trained_Models/test_cars_model_8/'
    caffemodel = 'snapshot_iter_3064.caffemodel'
    image = '0.jpg'

    ic = ImageClassify('/home/alloba/Trained_Models/test_cars.tar.gz')
    print ic.classify_with_archive(['0.jpg'])
