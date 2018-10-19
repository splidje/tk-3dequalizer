import tde4

###
# CAMERA

class TDECamera(object):
    def __init__(self, cam_id):
        self._cam_id = cam_id

    def __unicode__(self):
        return self.name

    @property
    def id_(self):
        return self._cam_id

    @property
    def name(self):
        return tde4.getCameraName(self._cam_id)
    @name.setter
    def name(self, val):
        tde4.setCameraName(self._cam_id, val)

    @property
    def dimensions(self):
        return (self.width, self.height)
    @dimensions.setter
    def dimensions(self, val):
        self.width = val[0]
        self.height = val[1]

    @property
    def width(self):
        return tde4.getCameraImageWidth(self._cam_id)
    @width.setter
    def width(self, val):
        tde4.setCameraImageWidth(self._cam_id, val)

    @property
    def height(self):
        return tde4.getCameraImageHeight(self._cam_id)
    @height.setter
    def height(self, val):
        tde4.setCameraImageHeight(self._cam_id, val)

    @property
    def image_path(self):
        return tde4.getCameraPath(self._cam_id)
    @image_path.setter
    def image_path(self, val):
        tde4.setCameraPath(self._cam_id, val)

    @property
    def frame_range(self):
        return tde4.getCameraSequenceAttr(self._cam_id)
    @frame_range.setter
    def frame_range(self, val):
        tde4.setCameraSequenceAttr(self._cam_id, val)

    @property
    def type_(self):
        return tde4.getCameraType(self._cam_id)
    @type_.setter
    def type_(self, val):
        tde4.setCameraType(self._cam_id, val)

    @property
    def type_(self):
        return tde4.getCameraType(self._cam_id)
    @type_.setter
    def type_(self, val):
        tde4.setCameraType(self._cam_id, val)

    @property
    def frame_count(self):
        return tde4.getCameraNoFrames(self._cam_id)
    @frame_count.setter
    def frame_count(self, val):
        tde4.setCameraNoFrames(self._cam_id, val)

    @property
    def lens(self):
        return TDELens(tde4.getCameraLens(self._cam_id))

    @property
    def is_selected(self):
        return tde4.getCameraSelectionFlag(self._cam_id) > 0

    @staticmethod
    def iter_all():
        return (TDECamera(i) for i in tde4.getCameraList())
    
    @staticmethod
    def iter_selected():
        return (c for c in TDECamera.iter_all() if c.is_selected)

######
# LENS

class TDELens(object):
    def __init__(self, lens_id):
        self._lens_id = lens_id

    @property
    def id_(self):
        return self._lens_id

