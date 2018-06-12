import datetime
from collections import defaultdict
from io import BytesIO

from six import string_types
from sqlalchemy import inspect
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import xlsxwriter
from inspect import isclass

FORMS_ART11 = {}
FORMS = {}                         # main chapter 1 article form classes
SUBFORMS = defaultdict(set)        # store subform references
ITEM_DISPLAYS = defaultdict(set)   # store registration for item displays
LABELS = {}                        # vocabulary of labels


def class_id(obj):
    if type(obj) is type:
        klass = obj
    else:
        klass = obj.__class__

    return klass.__name__.lower()


def register_form_art11(klass):
    """ Registers a 'secondary' form class for article 11

    """

    FORMS_ART11[class_id(klass)] = klass

    return klass


def register_form(klass):
    """ Registers a 'secondary' form class

    These are the forms implementing the 'Article 9 (GES determination)',
    'Article 10 (Targets)' and so on, for one of the 'chapters'.
    """

    FORMS[class_id(klass)] = klass

    return klass


def get_form(name):
    if name:
        return FORMS[name]


def register_subform(mainform):
    """ Registers a 'subform' as a possible choice for displaying data

    These are the 'pages', such as 'Ecosystem(s)', 'Functional group(s)' in the
    'Article 8.1a (Analysis of the environmental status)'
    """

    def wrapper(klass):
        SUBFORMS[mainform].add(klass)

        return klass

    return wrapper


def get_registered_subform(form, name):
    """ Get the subform for a "main" form. For ex: A81a selects Ecosystem
    """

    if name:
        return SUBFORMS.get((class_id(form), name))


def register_form_section(parent_klass):
    """ Registers a 'section' in a page with data.

    These are the 'sections' such as 'Pressures and impacts' or
    'Status assessment' in subform 'Ecosystem(s)' in 'Article 8.1a (Analysis of
    the environmental status)'
    """

    def wrapper(klass):
        ITEM_DISPLAYS[parent_klass].add(klass)

        return klass

    return wrapper


def get_registered_form_sections(form):
    return ITEM_DISPLAYS[form.__class__]


def scan(namespace):
    """ Scans the namespace for modules and imports them, to activate decorator
    """

    import importlib
    # import pkgutil
    # import wise.content.search

    name = importlib._resolve_name(namespace, 'wise.content.search', 1)
    importlib.import_module(name)


def print_value(value):
    if not value:
        return value

    if isinstance(value, string_types):
        if value in LABELS:
            tmpl = '<span title="%s">%s</span>'

            return tmpl % (value, LABELS[value])

        return value

    base_values = string_types + (int, datetime.datetime, list)

    if not isinstance(value, base_values):

        # TODO: right now we're not showing complex, table-like values
        # Activate below to show tables
        # return self.value_template(item=value)

        return None
        # return '&lt;hidden&gt;'

    return value


def data_to_xls(data):
    """ Convert python export data to XLS stream of data
    """

    # Create a workbook and add a worksheet.
    out = BytesIO()
    workbook = xlsxwriter.Workbook(out, {'in_memory': True})

    for wtitle, wdata in data:
        worksheet = workbook.add_worksheet(wtitle)

        row0 = wdata[0]
        is_tuple = isinstance(row0, tuple)
        # import pdb; pdb.set_trace()
        if not is_tuple:
            fields = sorted(get_obj_fields(row0))
        else:
            fields = row0._fields

        # write titles

        for i, f in enumerate(fields):
            worksheet.write(0, i, f)

        for j, row in enumerate(wdata):
            for i, f in enumerate(fields):
                if not is_tuple:
                    value = getattr(row, f)
                else:
                    value = row[i]

                if not isinstance(value,
                                  string_types + (float, int, type(None))):
                    value = 'not exported'

                worksheet.write(j + 1, i, value)

    workbook.close()
    out.seek(0)

    return out


def get_obj_fields(obj):
    mapper = inspect(obj)

    res = []
    keys = sorted([c.key for c in mapper.attrs])

    BLACKLIST = ['ID', 'Import']

    for key in keys:
        flag = False

        for bit in BLACKLIST:
            if bit in key:
                flag = True

        if not flag:
            res.append(key)

    return res


def db_objects_to_dict(data, excluded_columns=()):
    """
    Transform a list of sqlalchemy DB objects into
    a list of dictionaries, needed for pivot_data()

    :param data: list of sqlalchemy DB objects
    :return: list of dictionaries
    """
    out = []

    for row in data:
        columns = row.__table__.columns.keys()
        d = dict()

        for col in columns:
            if col not in excluded_columns:
                d.update({col: getattr(row, col)})
        out.append(d)

    return out


def pivot_data(data, pivot):
    out = defaultdict(list)

    for row in data:
        d = dict(row)
        p = d.pop(pivot)
        out[p].append(d)

    return out


def pivot_query(query, pivot):
    """ Pivot results from a query over a table
    """

    cols = [x['name'] for x in query.column_descriptions]
    res = [dict(zip(cols, row)) for row in query]

    if len(cols) == 1:
        return {pivot: res}

    return pivot_data(res, pivot)


def default_value_from_field(context, field):
    """ Get the defaulf value for a choice field
    """
    vocab = field.field.vocabulary

    if not vocab:
        name = field.field.vocabularyName
        vocab = getUtility(IVocabularyFactory, name=name)(context)

    if not vocab._terms:
        return

    term = vocab._terms[0]

    # import pdb;pdb.set_trace()

    if isclass(term.value):
        return term.value, term.token
    return term.token


def all_values_from_field(context, field):
    name = field.field.value_type.vocabularyName
    vocab = getUtility(IVocabularyFactory, name=name)(context)

    return [term.token for term in vocab._terms]
