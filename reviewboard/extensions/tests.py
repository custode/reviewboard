from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.template import Context, Template
from django.test.client import RequestFactory
from djblets.extensions.manager import ExtensionManager
from djblets.extensions.models import RegisteredExtension

from reviewboard.admin.widgets import (primary_widgets,
                                       secondary_widgets,
                                       Widget)
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import (AdminWidgetHook,
                                          CommentDetailDisplayHook,
                                          DiffViewerActionHook,
                                          HeaderActionHook,
                                          HeaderDropdownActionHook,
                                          HostingServiceHook,
                                          IntegrationHook,
                                          NavigationBarHook,
                                          ReviewRequestActionHook,
                                          ReviewRequestApprovalHook,
                                          ReviewRequestDropdownActionHook,
                                          ReviewRequestFieldSetsHook,
                                          WebAPICapabilitiesHook)
from reviewboard.hostingsvcs.service import (get_hosting_service,
                                             HostingService)
from reviewboard.integrations.integration import (Integration,
                                                  get_integration,
                                                  get_integrations)
from reviewboard.testing.testcase import TestCase
from reviewboard.reviews.models.review_request import ReviewRequest
from reviewboard.reviews.fields import (BaseReviewRequestField,
                                        BaseReviewRequestFieldSet)
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import root_item_mimetype
from reviewboard.webapi.tests.urls import get_root_url


class DummyExtension(Extension):
    registration = RegisteredExtension()


class HookTests(TestCase):
    """Tests the extension hooks."""
    def setUp(self):
        super(HookTests, self).setUp()

        manager = ExtensionManager('')
        self.extension = DummyExtension(extension_manager=manager)

    def tearDown(self):
        super(HookTests, self).tearDown()

        self.extension.shutdown()

    def test_diffviewer_action_hook(self):
        """Testing diff viewer action extension hooks"""
        self._test_action_hook('diffviewer_action_hooks', DiffViewerActionHook)

    def test_review_request_action_hook(self):
        """Testing review request action extension hooks"""
        self._test_action_hook('review_request_action_hooks',
                               ReviewRequestActionHook)

    def test_review_request_dropdown_action_hook(self):
        """Testing review request drop-down action extension hooks"""
        self._test_dropdown_action_hook('review_request_dropdown_action_hooks',
                                        ReviewRequestDropdownActionHook)

    def test_action_hook_context_doesnt_leak(self):
        """Testing ActionHooks' context won't leak state"""
        action = {
            'label': 'Test Action',
            'id': 'test-action',
            'url': 'foo-url',
        }

        ReviewRequestActionHook(extension=self.extension, actions=[action])

        context = Context({})

        t = Template(
            "{% load rb_extensions %}"
            "{% review_request_action_hooks %}")
        t.render(context)

        self.assertNotIn('action', context)

    def _test_action_hook(self, template_tag_name, hook_cls):
        action = {
            'label': 'Test Action',
            'id': 'test-action',
            'image': 'test-image',
            'image_width': 42,
            'image_height': 42,
            'url': 'foo-url',
        }

        hook = hook_cls(extension=self.extension, actions=[action])

        context = Context({})
        entries = hook.get_actions(context)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], action)

        t = Template(
            "{% load rb_extensions %}"
            "{% " + template_tag_name + " %}")

        self.assertEqual(t.render(context).strip(),
                         self._build_action_template(action))

    def _test_dropdown_action_hook(self, template_tag_name, hook_cls):
        action = {
            'id': 'test-menu',
            'label': 'Test Menu',
            'items': [
                {
                    'id': 'test-action',
                    'label': 'Test Action',
                    'url': 'foo-url',
                    'image': 'test-image',
                    'image_width': 42,
                    'image_height': 42
                }
            ]
        }

        hook = hook_cls(extension=self.extension,
                        actions=[action])

        context = Context({})
        entries = hook.get_actions(context)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], action)

        t = Template(
            "{% load rb_extensions %}"
            "{% " + template_tag_name + " %}")

        content = t.render(context).strip()

        self.assertIn(('id="%s"' % action['id']), content)
        self.assertIn((">%s &#9662;" % action['label']), content)
        self.assertIn(self._build_action_template(action['items'][0]),
                      content)

    def _build_action_template(self, action):
        return ('<li><a id="%(id)s" href="%(url)s">'
                '<img src="%(image)s" width="%(image_width)s" '
                'height="%(image_height)s" border="0" alt="" />'
                '%(label)s</a></li>' % action)

    def test_navigation_bar_hooks(self):
        """Testing navigation entry extension hooks"""
        entry = {
            'label': 'Test Nav Entry',
            'url': 'foo-url',
        }

        hook = NavigationBarHook(extension=self.extension, entries=[entry])

        context = Context({})
        entries = hook.get_entries(context)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], entry)

        t = Template(
            "{% load rb_extensions %}"
            "{% navigation_bar_hooks %}")

        self.assertEqual(t.render(context).strip(),
                         '<li><a href="%(url)s">%(label)s</a></li>' % entry)

    def test_navigation_bar_hooks_with_url_name(self):
        "Testing navigation entry extension hooks with url names"""
        entry = {
            'label': 'Test Nav Entry',
            'url_name': 'dashboard',
        }

        hook = NavigationBarHook(extension=self.extension, entries=[entry])

        context = Context({})
        entries = hook.get_entries(context)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], entry)

        t = Template(
            "{% load rb_extensions %}"
            "{% navigation_bar_hooks %}")

        self.assertEqual(
            t.render(context).strip(),
            '<li><a href="%(url)s">%(label)s</a></li>' % {
                'label': entry['label'],
                'url': '/dashboard/',
            })

    def test_header_hooks(self):
        """Testing header action extension hooks"""
        self._test_action_hook('header_action_hooks', HeaderActionHook)

    def test_header_dropdown_action_hook(self):
        """Testing header drop-down action extension hooks"""
        self._test_dropdown_action_hook('header_dropdown_action_hooks',
                                        HeaderDropdownActionHook)


class TestService(HostingService):
    name = 'test-service'


class HostingServiceHookTests(TestCase):
    """Testing HostingServiceHook."""
    def setUp(self):
        super(HostingServiceHookTests, self).setUp()

        manager = ExtensionManager('')
        self.extension = DummyExtension(extension_manager=manager)

    def tearDown(self):
        super(HostingServiceHookTests, self).tearDown()

        self.extension.shutdown()

    def test_register(self):
        """Testing HostingServiceHook registration"""
        HostingServiceHook(extension=self.extension, service_cls=TestService)

        self.assertNotEqual(None, get_hosting_service(TestService.name))

    def test_unregister(self):
        """Testing HostingServiceHook unregistration"""
        hook = HostingServiceHook(extension=self.extension,
                                  service_cls=TestService)

        hook.shutdown()

        self.assertEqual(None, get_hosting_service(TestService.name))


class TestWidget(Widget):
    widget_id = 'test'
    title = 'Testing Widget'


class AdminWidgetHookTests(TestCase):
    """Testing AdminWidgetHook."""
    def setUp(self):
        super(AdminWidgetHookTests, self).setUp()

        manager = ExtensionManager('')
        self.extension = DummyExtension(extension_manager=manager)

    def tearDown(self):
        super(AdminWidgetHookTests, self).tearDown()

        self.extension.shutdown()

    def test_register(self):
        """Testing AdminWidgetHook initializing"""
        AdminWidgetHook(extension=self.extension, widget_cls=TestWidget)

        self.assertIn(TestWidget, secondary_widgets)

    def test_register_with_primary(self):
        """Testing AdminWidgetHook initializing with primary set"""
        AdminWidgetHook(extension=self.extension, widget_cls=TestWidget,
                        primary=True)

        self.assertIn(TestWidget, primary_widgets)

    def test_unregister(self):
        """Testing AdminWidgetHook unitializing"""
        hook = AdminWidgetHook(extension=self.extension, widget_cls=TestWidget)

        hook.shutdown()

        self.assertNotIn(TestWidget, secondary_widgets)


class WebAPICapabilitiesExtension(Extension):
    registration = RegisteredExtension()
    metadata = {
        'Name': 'Web API Capabilities Extension',
    }
    id = 'WebAPICapabilitiesExtension'

    def __init__(self, *args, **kwargs):
        super(WebAPICapabilitiesExtension, self).__init__(*args, **kwargs)


class WebAPICapabilitiesHookTests(BaseWebAPITestCase):
    """Testing WebAPICapabilitiesHook."""
    def setUp(self):
        super(WebAPICapabilitiesHookTests, self).setUp()

        manager = ExtensionManager('')
        self.extension = WebAPICapabilitiesExtension(
            extension_manager=manager)
        self.url = get_root_url()

    def tearDown(self):
        super(WebAPICapabilitiesHookTests, self).tearDown()

    def test_register(self):
        """Testing WebAPICapabilitiesHook initializing"""
        WebAPICapabilitiesHook(
            extension=self.extension,
            caps={
                'sandboxed': True,
                'thorough': True,
            })

        rsp = self.api_get(path=self.url,
                           expected_mimetype=root_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('capabilities', rsp)

        caps = rsp['capabilities']
        self.assertIn('WebAPICapabilitiesExtension', caps)

        extension_caps = caps[self.extension.id]
        self.assertTrue(extension_caps['sandboxed'])
        self.assertTrue(extension_caps['thorough'])

        self.extension.shutdown()

    def test_register_fails_no_id(self):
        """Testing WebAPICapabilitiesHook initializing with ID of None"""
        self.extension.id = None

        self.assertRaisesMessage(
            ValueError,
            'The capabilities_id attribute must not be None',
            WebAPICapabilitiesHook,
            self.extension,
            {
                'sandboxed': True,
                'thorough': True,
            })

        rsp = self.api_get(path=self.url,
                           expected_mimetype=root_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('capabilities', rsp)

        caps = rsp['capabilities']
        self.assertNotIn('WebAPICapabilitiesExtension', caps)
        self.assertNotIn(None, caps)

        self.assertRaisesMessage(
            KeyError,
            '"None" is not a registered web API capabilities set',
            self.extension.shutdown)

    def test_register_fails_default_capability(self):
        """Testing WebAPICapabilitiesHook initializing with default key"""
        self.extension.id = 'diffs'

        self.assertRaisesMessage(
            KeyError,
            '"diffs" is reserved for the default set of capabilities',
            WebAPICapabilitiesHook,
            self.extension,
            {
                'base_commit_ids': False,
                'moved_files': False,
            })

        rsp = self.api_get(path=self.url,
                           expected_mimetype=root_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('capabilities', rsp)

        caps = rsp['capabilities']
        self.assertIn('diffs', caps)

        diffs_caps = caps['diffs']
        self.assertTrue(diffs_caps['base_commit_ids'])
        self.assertTrue(diffs_caps['moved_files'])

        self.assertRaisesMessage(
            KeyError,
            '"diffs" is not a registered web API capabilities set',
            self.extension.shutdown)

    def test_unregister(self):
        """Testing WebAPICapabilitiesHook uninitializing"""
        hook = WebAPICapabilitiesHook(
            extension=self.extension,
            caps={
                'sandboxed': True,
                'thorough': True,
            })

        hook.shutdown()

        rsp = self.api_get(path=self.url,
                           expected_mimetype=root_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('capabilities', rsp)

        caps = rsp['capabilities']
        self.assertNotIn('WebAPICapabilitiesExtension', caps)

        self.extension.shutdown()


class SandboxExtension(Extension):
    registration = RegisteredExtension()
    metadata = {
        'Name': 'Sandbox Extension',
    }
    id = 'reviewboard.extensions.tests.SandboxExtension'

    def __init__(self, *args, **kwargs):
        super(SandboxExtension, self).__init__(*args, **kwargs)


class TestIntegration(Integration):
    integration_id = 'TestIntegration'


class IntegrationHookTest(TestCase):
    """Testing integration hook."""

    def setUp(self):
        super(IntegrationHookTest, self).setUp()

        manager = ExtensionManager('')
        self.extension = DummyExtension(extension_manager=manager)

    def tearDown(self):
        super(IntegrationHookTest, self).tearDown()

        self.extension.shutdown()

    def test_register(self):
        """Testing IntegrationHook initializing"""
        IntegrationHook(self.extension, TestIntegration)

        self.assertIn(TestIntegration, get_integrations())
        self.assertEqual(TestIntegration,
                         get_integration(TestIntegration.integration_id))

    def test_unregister(self):
        """Testing IntegrationHook unitializing"""
        hook = IntegrationHook(self.extension, TestIntegration)

        hook.shutdown()
        self.assertNotIn(TestIntegration, get_integrations())


class ReviewRequestApprovalTestHook(ReviewRequestApprovalHook):
    def is_approved(self, review_request, prev_approved, prev_failure):
        raise Exception


class NavigationBarTestHook(NavigationBarHook):
    def get_entries(self, context):
        raise Exception


class DiffViewerActionTestHook(DiffViewerActionHook):
    def get_actions(self, context):
        raise Exception


class HeaderActionTestHook(HeaderActionHook):
    def get_actions(self, context):
        raise Exception


class HeaderDropdownActionTestHook(HeaderDropdownActionHook):
    def get_actions(self, context):
        raise Exception


class ReviewRequestActionTestHook(ReviewRequestActionHook):
    def get_actions(self, context):
        raise Exception


class ReviewRequestDropdownActionTestHook(ReviewRequestDropdownActionHook):
    def get_actions(self, context):
        raise Exception


class CommentDetailDisplayTestHook(CommentDetailDisplayHook):
    def render_review_comment_detail(self, comment):
        raise Exception

    def render_email_comment_detail(self, comment, is_html):
        raise Exception


class BaseReviewRequestTestShouldRenderField(BaseReviewRequestField):
    field_id = 'should_render'

    def should_render(self, value):
        raise Exception


class BaseReviewRequestTestInitField(BaseReviewRequestField):
    field_id = 'init_field'

    def __init__(self, review_request_details):
        raise Exception


class TestIsEmptyField(BaseReviewRequestField):
    field_id = 'is_empty'


class TestInitField(BaseReviewRequestField):
    field_id = 'test_init'


class TestInitFieldset(BaseReviewRequestFieldSet):
    fieldset_id = 'test_init'
    field_classes = [BaseReviewRequestTestInitField]


class TestShouldRenderFieldset(BaseReviewRequestFieldSet):
    fieldset_id = 'test_should_render'
    field_classes = [BaseReviewRequestTestShouldRenderField]


class BaseReviewRequestTestIsEmptyFieldset(BaseReviewRequestFieldSet):
    fieldset_id = 'is_empty'
    field_classes = [TestIsEmptyField]

    @classmethod
    def is_empty(cls):
        raise Exception


class BaseReviewRequestTestInitFieldset(BaseReviewRequestFieldSet):
    fieldset_id = 'init_fieldset'
    field_classes = [TestInitField]

    def __init__(self, review_request_details):
        raise Exception


class SandboxTests(TestCase):
    """Testing extension sandboxing"""
    def setUp(self):
        super(SandboxTests, self).setUp()

        manager = ExtensionManager('')
        self.extension = SandboxExtension(extension_manager=manager)

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='reviewboard', email='',
                                             password='password')

    def tearDown(self):
        super(SandboxTests, self).tearDown()

        self.extension.shutdown()

    def test_is_approved_sandbox(self):
        """Testing sandboxing ReviewRequestApprovalHook when
        is_approved function throws an error"""
        ReviewRequestApprovalTestHook(extension=self.extension)
        review = ReviewRequest()
        review._calculate_approval()

    def test_get_entries(self):
        """Testing sandboxing NavigationBarHook when get_entries function
        throws an error"""
        entry = {
            'label': 'Test get_entries Function',
            'url': '/dashboard/',
        }

        NavigationBarTestHook(extension=self.extension, entries=[entry])

        context = Context({})

        t = Template(
            "{% load rb_extensions %}"
            "{% navigation_bar_hooks %}")

        t.render(context).strip()

    def test_render_review_comment_details(self):
        """Testing sandboxing CommentDetailDisplayHook when
        render_review_comment_detail throws an error"""
        CommentDetailDisplayTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% comment_detail_display_hook comment 'review'%}")

        t.render(context).strip()

    def test_email_review_comment_details(self):
        """Testing sandboxing CommentDetailDisplayHook when
        render_email_comment_detail throws an error"""
        CommentDetailDisplayTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% comment_detail_display_hook comment 'html-email'%}")

        t.render(context).strip()

    def test_action_hooks_diff_viewer_hook(self):
        """Testing sandboxing DiffViewerActionHook when
        action_hooks throws an error"""
        DiffViewerActionTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% diffviewer_action_hooks %}")

        t.render(context).strip()

    def test_action_hooks_header_hook(self):
        """Testing sandboxing HeaderActionHook when
        action_hooks throws an error"""
        HeaderActionTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% header_action_hooks %}")

        t.render(context).strip()

    def test_action_hooks_header_dropdown_hook(self):
        """Testing sandboxing HeaderDropdownActionHook when
        action_hooks throws an error"""
        HeaderDropdownActionTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% header_dropdown_action_hooks %}")

        t.render(context).strip()

    def test_action_hooks_review_request_hook(self):
        """Testing sandboxing ReviewRequestActionHook when
        action_hooks throws an error"""
        ReviewRequestActionTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% review_request_action_hooks %}")

        t.render(context).strip()

    def test_action_hooks_review_request_dropdown_hook(self):
        """Testing sandboxing ReviewRequestDropdownActionHook when
        action_hooks throws an error"""
        ReviewRequestDropdownActionTestHook(extension=self.extension)

        context = Context({'comment': 'this is a comment'})

        t = Template(
            "{% load rb_extensions %}"
            "{% review_request_dropdown_action_hooks %}")

        t.render(context).strip()

    def test_is_empty_review_request_fieldset(self):
        """Testing sandboxing ReivewRequestFieldset is_empty function in
        for_review_request_fieldset"""
        fieldset = [BaseReviewRequestTestIsEmptyFieldset]
        ReviewRequestFieldSetsHook(extension=self.extension,
                                   fieldsets=fieldset)

        review = ReviewRequest()

        request = self.factory.get('test')
        request.user = self.user
        context = Context({
            'review_request_details': review,
            'request': request
        })

        t = Template(
            "{% load reviewtags %}"
            "{% for_review_request_fieldset review_request_details %}"
            "{% end_for_review_request_fieldset %}")

        t.render(context).strip()

    def test_field_cls_review_request_field(self):
        """Testing sandboxing ReviewRequestFieldset init function in
        for_review_request_field"""
        fieldset = [TestInitFieldset]
        ReviewRequestFieldSetsHook(extension=self.extension,
                                   fieldsets=fieldset)

        review = ReviewRequest()
        context = Context({
            'review_request_details': review,
            'fieldset': TestInitFieldset
        })

        t = Template(
            "{% load reviewtags %}"
            "{% for_review_request_field review_request_details 'test_init' %}"
            "{% end_for_review_request_field %}")

        t.render(context).strip()

    def test_fieldset_cls_review_request_fieldset(self):
        """Testing sandboxing ReviewRequestFieldset init function in
        for_review_request_fieldset"""
        fieldset = [BaseReviewRequestTestInitFieldset]
        ReviewRequestFieldSetsHook(extension=self.extension,
                                   fieldsets=fieldset)

        review = ReviewRequest()
        request = self.factory.get('test')
        request.user = self.user
        context = Context({
            'review_request_details': review,
            'request': request
        })

        t = Template(
            "{% load reviewtags %}"
            "{% for_review_request_fieldset review_request_details %}"
            "{% end_for_review_request_fieldset %}")

        t.render(context).strip()

    def test_should_render_review_request_field(self):
        """Testing sandboxing ReviewRequestFieldset should_render function in
        for_review_request_field"""
        fieldset = [TestShouldRenderFieldset]
        ReviewRequestFieldSetsHook(extension=self.extension,
                                   fieldsets=fieldset)

        review = ReviewRequest()
        context = Context({
            'review_request_details': review,
            'fieldset': TestShouldRenderFieldset
        })

        t = Template(
            "{% load reviewtags %}"
            "{% for_review_request_field review_request_details"
            " 'test_should_render' %}"
            "{% end_for_review_request_field %}")

        t.render(context).strip()
