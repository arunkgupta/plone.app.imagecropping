# -*- coding: utf-8 -*-
import json
from zope import component
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from plone.app.imaging.utils import getAllowedSizes


class CroppingEditor(BrowserView):

    template = ViewPageTemplateFile('editor.pt')

    fieldname = "image"
    interface = IATContentType
    default_editor_size = (900, 0)
    default_cropping_max_size = (0, 0)

    def scales(self):
        """Returns information to initialize JCrop for all available scales
           on the current content with the given fieldname and interface."""

        all_sizes = getAllowedSizes()
        ids = []
        current_selected = self.request.get('image-select', '')
        # TODO this is archetype only, we should do refactoring with an adapter
        # to provide dexterity and archetype support
        field = self.context.getField(self.fieldname)
        image_size = field.getSize(self.context)
        for index, size in enumerate(all_sizes):
            scale = dict()
            # scale jcrop config
            min_width, min_height = self._min_size(image_size, all_sizes[size])
            max_width, max_height = self.default_cropping_max_size[0],\
                self.default_cropping_max_size[1]
            ratio_width, ratio_height = all_sizes[size][0], all_sizes[size][1]
            config = dict([
                ("allowResize", True),
                ("allowMove", True),
                ("trueSize", [image_size[0], image_size[1]]),
                ("boxWidth", self.default_editor_size[0]),
                ("boxHeight", self.default_editor_size[1]),
                ("trueSize", [image_size[0], image_size[1]]),
                ("setSelect", [0, 0, min_width, min_height]),
                ("aspectRatio", ratio_width / ratio_height),
                ("minSize", [min_width, min_height]),
                ("maxSize", [max_width, max_height]),
                ("imageURL", self.image_url()),
            ])
            scale["config"] = json.dumps(config)
            # scale value/id
            scale["id"] = size
            scale["selected"] = size == current_selected and 'selected' or '',

            ids.append(scale)
        return ids

    def current_scale(self):
        """Returns information of the current selected scale"""
        images = self.scales()
        current_image = images[0]
        current = self.request.form.get('scalename', None)
        if isinstance(current, list):
            current = current[0]
        if current is not None:
            for image in images:
                if image["id"] == current:
                    current_image = image
        return current_image

    def current_url(self):
        """Returns the current page url"""
        context_state = component.getMultiAdapter(
            (self.context, self.request),
            name=u'plone_context_state'
        )
        return context_state.current_page_url()

    def image_url(self):
        """Returns the url to the unscaled image"""
        return "%s/@@images/%s" % (self.context.absolute_url(), self.fieldname)

    def __call__(self):
        form = self.request.form
        if form.get('form.button.Cancel', None) is not None:
            return self.request.response.redirect(
                self.context.absolute_url() + '/view')
        if form.get('form.button.Delete', None) is not None:
            # XXX TODO Delete
            return self.request.response.redirect(
                self.context.absolute_url() + '/view')
        if form.get('form.button.Save', None) is not None:
            x1 = int(round(float(self.request.form.get('x1'))))
            y1 = int(round(float(self.request.form.get('y1'))))
            x2 = int(round(float(self.request.form.get('x2'))))
            y2 = int(round(float(self.request.form.get('y2'))))
            scale_name = self.request.form.get('scalename')
            cropping_util = self.context.restrictedTraverse('@@crop-image')
            cropping_util._crop(fieldname=self.fieldname,
                                scale=scale_name,
                                box=(x1, y1, x2, y2),
                                interface=self.interface.__identifier__)
            # XXX TODO success message
        return self.template()

    def _min_size(self, image_size, scale_size):
        """ we need lower min-sizes if the image is smaller than the scale """
        width = scale_size[0]
        height = scale_size[1]
        if width > image_size[0]:
            ratio = float(image_size[0]) / float(width)
            width = image_size[0]
            height = float(height) * ratio
        if height > image_size[1]:
            ratio = float(image_size[1]) / float(height)
            height = image_size[1]
            width = float(width) * ratio
        return (int(round(width)), int(round(height)))