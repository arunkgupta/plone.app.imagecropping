from Products.CMFCore.utils import getToolByName
from plone.app.imagecropping.testing import PLONE_APP_IMAGECROPPING_INTEGRATION
import unittest2 as unittest


class TestExample(unittest.TestCase):

    layer = PLONE_APP_IMAGECROPPING_INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'plone.app.imagecropping'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')

    def test_css_registered(self):
        cssreg = getattr(self.portal, 'portal_css')
        stylesheets_ids = cssreg.getResourceIds()
        self.assertTrue(
            '++resource++plone.app.imagecropping.static/jquery.Jcrop.css' in \
            stylesheets_ids)
        self.assertTrue(
            '++resource++plone.app.imagecropping.static/cropping.css' in \
            stylesheets_ids)
