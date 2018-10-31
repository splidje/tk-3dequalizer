import tde4


######
# LENS

class TDELens(object):
    def __init__(self, cam, lens_id):
        self._cam = cam
        self._lens_id = lens_id
        self._lens_centre = self.LensCentre(self)

    @property
    def id_(self):
        return self._lens_id

    @property
    def filmback_dimensions(self):
        return (self.filmback_width, self.filmback_height)
    @filmback_dimensions.setter
    def filmback_dimensions(self, val):
        self.filmback_width = val[0]
        self.filmback_height = val[1]

    @property
    def filmback_width(self):
        return tde4.getLensFBackWidth(self._lens_id)
    @filmback_width.setter
    def filmback_width(self, val):
        tde4.setLensFBackWidth(self._lens_id, val)

    @property
    def filmback_height(self):
        return tde4.getLensFBackHeight(self._lens_id)
    @filmback_height.setter
    def filmback_height(self, val):
        tde4.setLensFBackHeight(self._lens_id, val)

    @property
    def pixel_aspect(self):
        return tde4.getLensPixelAspect(self._lens_id)
    @pixel_aspect.setter
    def pixel_aspect(self, val):
        tde4.setLensPixelAspect(self._lens_id, val)

    @property
    def distortion_model_name(self):
        return tde4.getLensLDModel(self._lens_id)
    
    @property
    def distortion_model_parameter_names(self):
        return [
            tde4.getLDModelParameterName(self.distortion_model_name, i)
            for i in xrange(tde4.getLDModelNoParameters(self.distortion_model_name))
        ]

    def get_distortion_parameter(self, param_name, frame):
        return tde4.getLensLDAdjustableParameter(
            self._lens_id,
            param_name,
            self._cam.get_focal_length(frame),
            self._cam.get_focus(frame),
        )

    @property
    def dynamic_distortion_mode(self):
        return tde4.getLensDynamicDistortionMode(self._lens_id)

    class LensCentre(object):
        def __init__(self, lens):
            self._lens = lens

        @property
        def x(self):
            return tde4.getLensLensCenterX(self._lens.id_)
        @x.setter
        def x(self, val):
            tde4.setLensLensCenterX(self._lens.id_, val)

        @property
        def y(self):
            return tde4.getLensLensCenterY(self._lens.id_)
        @x.setter
        def y(self, val):
            tde4.setLensLensCenterY(self._lens.id_, val)

        def __getitem__(self, i):
            if i == 0: return self.x
            if i == 1: return self.y
            raise IndexError()

        @property
        def as_tuple(self):
            return (self.x, self.y)

    @property
    def lens_centre(self):
        return self._lens_centre

    @property
    def as_dict(self):
        return dict(
            id=self.id_,
            filmback_dimensions=self.filmback_dimensions,
            pixel_aspect=self.pixel_aspect,
            lens_centre=self.lens_centre.as_tuple,
            distortion_model_name=self.distortion_model_name,
            dynamic_distortion_mode=self.dynamic_distortion_mode,
            distortion_parameters={
                pn: [
                    self.get_distortion_parameter(pn, f)
                    for f in (
                        self.dynamic_distortion_mode == 'DISTORTION_STATIC' and (1,)
                        or xrange(1, self._cam.frame_count + 1)
                    )
                ]
                for pn in
                self.distortion_model_parameter_names
            }
        )

