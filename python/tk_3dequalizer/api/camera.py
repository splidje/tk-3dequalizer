from __future__ import absolute_import
from builtins import range
from builtins import object
import tde4

from .lens import TDELens

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
    def image_dimensions(self):
        return (self.image_width, self.image_height)

    @image_dimensions.setter
    def image_dimensions(self, val):
        self.image_width = val[0]
        self.image_height = val[1]

    @property
    def image_width(self):
        return tde4.getCameraImageWidth(self._cam_id)

    @image_width.setter
    def image_width(self, val):
        tde4.setCameraImageWidth(self._cam_id, val)

    @property
    def image_height(self):
        return tde4.getCameraImageHeight(self._cam_id)

    @image_height.setter
    def image_height(self, val):
        tde4.setCameraImageHeight(self._cam_id, val)

    @property
    def image_path(self):
        return tde4.getCameraPath(self._cam_id)

    @image_path.setter
    def image_path(self, val):
        tde4.setCameraPath(self._cam_id, val)

    @property
    def image_frame_range(self):
        return tde4.getCameraSequenceAttr(self._cam_id)

    @image_frame_range.setter
    def image_frame_range(self, val):
        tde4.setCameraSequenceAttr(self._cam_id, val)

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
    def frame_offset(self):
        return tde4.getCameraFrameOffset(self._cam_id)

    @frame_offset.setter
    def frame_offset(self, val):
        tde4.setCameraFrameOffset(self._cam_id, val)

    @property
    def zooming_flag(self):
        return tde4.getCameraZoomingFlag(self._cam_id)

    def get_focal_length(self, frame):
        return tde4.getCameraFocalLength(self._cam_id, frame)

    def set_focal_length(self, frame, val):
        return tde4.setCameraFocalLength(self._cam_id, frame, val)

    @property
    def focus_mode(self):
        return tde4.getCameraFocusMode(self._cam_id)

    def get_focus(self, frame):
        return tde4.getCameraFocus(self._cam_id, frame)

    @property
    def fov(self):
        return tde4.getCameraFOV(self._cam_id)

    @property
    def lens(self):
        return TDELens(self, tde4.getCameraLens(self._cam_id))

    @property
    def as_dict(self):
        return dict(
            id=self.id_,
            name=self.name,
            image_dimensions=self.image_dimensions,
            image_path=self.image_path,
            image_frame_range=self.image_frame_range,
            frame_offset=self.frame_offset,
            frame_count=self.frame_count,
            type=self.type_,
            zooming_flag=self.zooming_flag,
            focal_lengths=[
                self.get_focal_length(f)
                for f in (self.zooming_flag and range(1, self.frame_count + 1) or (1,))
            ],
            focus_mode=self.focus_mode,
            focuses=[
                self.get_focus(f)
                for f in (
                    self.focus_mode == "FOCUS_DYNAMIC"
                    and range(1, self.frame_count + 1)
                    or (1,)
                )
            ],
            fov=self.fov,
            lens=self.lens.as_dict,
        )

    @property
    def is_selected(self):
        return tde4.getCameraSelectionFlag(self._cam_id) > 0

    @staticmethod
    def get_current():
        cc_id = tde4.getCurrentCamera()
        return cc_id and TDECamera(cc_id)

    @staticmethod
    def iter_all():
        return (TDECamera(i) for i in tde4.getCameraList())

    @staticmethod
    def iter_selected():
        return (c for c in TDECamera.iter_all() if c.is_selected)
