from sqlalchemy.inspection import inspect
from zope.browserpage.viewpagetemplatefile import \
    ViewPageTemplateFile as Z3ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.interface import implements

from plone.z3cform.layout import FormWrapper
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from wise.content.search import interfaces
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form

from .db import get_available_marine_unit_ids, get_item_by_conditions
from .interfaces import IMainForm
from .utils import (default_value_from_field, get_obj_fields,
                    get_registered_form_sections, print_value)
from .widget import MarineUnitIDSelectFieldWidget


class BaseUtil(object):
    """ Generic utilities for search views
    """

    value_template = ViewPageTemplateFile('pt/value-display.pt')

    def name_as_title(self, text):
        """ Given a "CamelCase" text, changes it to "Title Text"

        This is used to transform the database column names to usable labels
        """
        text = text.replace('_', ' ')

        for l in range(len(text) - 1):
            if text[l].islower() and text[l + 1].isupper():
                text = text[:(l + 1)] + ' ' + \
                    text[(l + 1):]

        return text

    def form_name(self):
        """ Returns an auto-generated form name, based on class name
        """

        return self.__class__.__name__.lower()

    def get_marine_unit_ids(self):
        """ Return the selected ids by looking up for data in parent forms
        """

        parent = self

        while True:
            if not hasattr(parent, 'data'):
                return []
            ids = parent.data.get('marine_unit_ids')

            if ids:
                break
            else:
                parent = parent.context

        return ids

    def get_marine_unit_id(self):
        """ Return the current selected MarineUnitID looking up data in parents
        """

        parent = self

        while True:
            mid = parent.data.get('marine_unit_id')

            if mid:
                break
            else:
                parent = parent.context

        return mid

    def get_obj_fields(self, obj):
        """ Inspect an SA object and return its field names
        """

        return get_obj_fields(obj)

    def print_value(self, value):
        return print_value(value)

    def get_main_form(self):
        """ Crawl back form chain to get to the main form
        """

        context = self

        while not IMainForm.providedBy(context):
            context = context.context

        return context


class MainForm(Form):
    """ The main forms need to inherit from this clas
    """

    implements(IMainForm)
    template = ViewPageTemplateFile('pt/mainform.pt')
    ignoreContext = True
    reset_page = False
    subform = None
    subform_content = None
    should_download = False     # flag that signals download button is hit
    # method = 'get'

    main_forms = (
        ('msfd-c1', ('Article 8, 9 & 10', '2012 reporting exercise')),
        ('msfd-c2', ('Article 11', '2014 reporting exercise')),
        ('msfd-c3', ('Article 13 & 14', '2015 reporting exercise')),
    )

    @buttonAndHandler(u'Apply filters', name='continue')
    def handle_continue(self, action):
        self.reset_page = True

    @buttonAndHandler(u'Download as XLS', name='download')
    def handle_download(self, action):
        self.should_download = True

    @property
    def title(self):
        return [x[1] for x in self.main_forms if x[0] == self.name][0]

    def extractData(self):
        """ Override to be able to provide defaults
        """
        data, errors = super(MainForm, self).extractData()

        for k, v in data.items():
            if not v:
                default = getattr(self, 'default_' + k, None)
                # import pdb;pdb.set_trace()
                if default:
                    data[k] = default()
                    self.widgets[k].value = data[k]

        return data, errors

    def update(self):
        super(MainForm, self).update()
        self.data, self.errors = self.extractData()

        has_values = self.data.values() and all(self.data.values())

        if has_values:
            self.subform = self.get_subform()

            if self.subform:
                # we need to update and "execute" the subforms to be able to
                # discover them, because the decision process regarding
                # discovery is done in the update() method of subforms
                self.subform_content = self.subform()

    def render(self):
        download_action = self.find_download_action()

        if download_action in (None, False):
            del self.actions['download']

        if download_action and self.should_download:
            # TODO: need to implement this as xls response

            data = download_action()

            sh = self.request.response.setHeader
            sh('Content-Type', 'application/vnd.ms-excel')
            sh('Content-Disposition', 'attachment; filename=marinedb.xls')

            return data.read()

        return super(MainForm, self).render()

    def find_download_action(self):
        """ Look for a download method in all subform children
        """

        ctx = self

        while hasattr(ctx, 'subform'):

            if hasattr(ctx, 'download_results'):
                return ctx.download_results

            ctx = ctx.subform

        if hasattr(ctx, 'download_results'):
            return ctx.download_results


class MainFormWrapper(FormWrapper):
    """ Override mainform wrapper to be able to return XLS file
    """

    index = ViewPageTemplateFile('pt/layout.pt')

    def render(self):
        if 'text/html' not in self.request.response.getHeader('Content-Type'):
            return self.contents

        return super(MainFormWrapper, self).render()


class EmbededForm(Form, BaseUtil):
    """ Our most basic super-smart-superclass for forms

    It can embed other children forms
    """

    implements(interfaces.IEmbededForm)
    ignoreContext = True

    template = ViewPageTemplateFile('pt/subform.pt')
    subform_class = None

    def __init__(self, context, request):
        super(EmbededForm, self).__init__(context, request)
        self.__parent__ = self.context = context
        self.request = request
        self.data = {}

    def update(self):
        super(EmbededForm, self).update()

        self.data, errors = self.extractData()

        has_values = self.data.values() and all(self.data.values())

        if (not errors) and has_values:
            subform = self.get_subform()

            if subform is not None:
                self.subform = subform

    def extractData(self):
        """ Override to be able to provide defaults

        Create a function called "default_<name_of_field>" to provide default
        value
        """
        data, errors = super(EmbededForm, self).extractData()

        for k, v in data.items():
            if not v:
                default = getattr(self, 'default_' + k, None)

                if default:
                    value = data[k] = default()
                    # import pdb;pdb.set_trace()
                    if not value:
                        continue
                    widget = self.widgets[k]
                    widget.value = value
                    field = widget.field.bind(self.context)
                    field.default = value
                    widget.field = field
                    widget.ignoreRequest = True
                    widget.update()

        return data, errors

    def get_subform(self, klass=None):
        if klass is None:
            klass = self.subform_class

        if klass is None:
            return None

        return klass(self, self.request)

    def extras(self):
        extras = queryMultiAdapter((self, self.request), name='extras')

        if extras:
            return extras()


class MarineUnitIDSelectForm(EmbededForm):
    """ Base form for displaying information for a single MarineUnitID
    """

    template = ViewPageTemplateFile('pt/marine-unit-id-form.pt')
    fields = Fields(interfaces.IMarineUnitIDSelect)
    fields['marine_unit_id'].widgetFactory = MarineUnitIDSelectFieldWidget
    mapper_class = None         # what type of objects are we focused on?

    css_class = "left-side-form"

    def default_marine_unit_id(self):
        return default_value_from_field(self.context,
                                        self.fields['marine_unit_id'])

    def update(self):
        # Override the default to be able to have a default marine unit id
        super(MarineUnitIDSelectForm, self).update()        # EmbededForm

        self.data, errors = self.extractData()

        if (not (errors or (None in self.data.values()))) and \
                self.data.values():
            subform = self.get_subform()

            if subform is not None:
                self.subform = subform

    def updateWidgets(self, prefix=None):
        """ """
        super(MarineUnitIDSelectForm, self).updateWidgets(prefix=prefix)

        widget = self.widgets["marine_unit_id"]
        widget.template = Z3ViewPageTemplateFile("pt/marine-widget.pt")

    def get_available_marine_unit_ids(self):
        assert self.mapper_class
        ids = self.get_marine_unit_ids()
        count, res = get_available_marine_unit_ids(
            ids, self.mapper_class
        )

        return [x[0] for x in res]


class ItemDisplayForm(EmbededForm):
    """ Generic form for displaying records
    """

    implements(interfaces.IItemDisplayForm)

    fields = Fields(interfaces.IRecordSelect)

    template = ViewPageTemplateFile('pt/item-display-form.pt')
    data_template = ViewPageTemplateFile('pt/item-display.pt')
    extra_data_template = ViewPageTemplateFile('pt/extra-data.pt')

    mapper_class = None     # This will be used to retrieve the item
    order_field = None      # This will be used to properly page between items

    def update(self):
        super(ItemDisplayForm, self).update()

        # import pdb; pdb.set_trace()

        if not self.get_main_form().reset_page:
            self.data['page'] = self.widgets['page'].value
        else:
            self.widgets['page'].value = 0
            self.data['page'] = 0

        self.count, self.item = self.get_db_results()

        if self.count == (int(self.data['page']) + 1):
            del self.actions['next']

        if int(self.data['page']) == 0:
            del self.actions['prev']

    def updateWidgets(self, prefix=None):
        super(ItemDisplayForm, self).updateWidgets()
        self.widgets['page'].mode = 'hidden'

    @buttonAndHandler(u'Prev', name='prev')
    def handle_prev(self, action):
        value = int(self.widgets['page'].value)
        self.widgets['page'].value = max(value - 1, 0)

    @buttonAndHandler(u'Next', name='next')
    def handle_next(self, action):
        value = int(self.widgets['page'].value)
        self.widgets['page'].value = value + 1

    def get_extra_data(self):
        return []

    def extras(self):
        return self.extra_data_template()

    def get_page(self):
        page = self.data.get('page')

        if page:
            return int(page)
        else:
            return 0

    def get_db_results(self):
        page = self.get_page()
        muid = self.get_marine_unit_id()

        res = get_item_by_conditions(
            self.mapper_class, self.order_field,
            self.mapper_class.MarineUnitID == muid,
            page=page,
        )

        return res

    def item_title(self, item):
        state = inspect(item)

        return (item.__class__.__name__, state.identity[0])


class MultiItemDisplayForm(ItemDisplayForm):
    template = ViewPageTemplateFile('pt/multi-item-display.pt')

    fields = Fields(interfaces.IRecordSelect)

    def get_sections(self):

        klasses = get_registered_form_sections(self)
        views = [k(self, self.request) for k in klasses]

        return views


class ItemDisplay(BrowserView, BaseUtil):
    """ A not-registered view that will render inline (a database result)
    """

    index = ViewPageTemplateFile('pt/simple-item-display.pt')

    data_template = ViewPageTemplateFile('pt/item-display.pt')
    extra_data_template = ViewPageTemplateFile('pt/extra-data.pt')

    data = {}

    def __init__(self, context, request):
        self.__parent__ = self.context = context
        self.request = request

        self.count = 0
        self.item = None

        res = self.get_db_results()

        if res:
            self.count, self.item = res

    def __call__(self):

        if not self.item:
            return ''

        return self.index()

    def get_db_results(self):
        raise NotImplementedError

    def get_page(self):
        page = self.context.data.get('page')

        if page:
            return int(page)
        else:
            return 0

    def get_extra_data(self):
        return []

    def extras(self):
        return self.extra_data_template()
