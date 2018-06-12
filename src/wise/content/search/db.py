import os
import threading

from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register

from wise.content.search import sql

DB = os.environ.get('MSFDURI', "mssql+pymssql://SA:bla3311!@msdb/MarineDB")

threadlocals = threading.local()


def connection():
    if hasattr(threadlocals, 'connection'):
        return threadlocals.connection

    session = _make_session()
    threadlocals.connection = session.connection()

    return threadlocals.connection


def session():
    if hasattr(threadlocals, 'session'):
        return threadlocals.session

    session = _make_session()
    threadlocals.session = session

    return session


def _make_session():
    engine = create_engine(DB)
    Session = scoped_session(sessionmaker(bind=engine))
    register(Session, keep_session=True)

    return Session()


def get_unique_from_table(table, column):
    """ Retrieves unique values for a column table
    """
    col = getattr(table.c, column)

    sess = session()
    res = sess.query(col).distinct().order_by(col)

    return sorted([x[0] for x in res])


def get_unique_from_mapper(mapper_class, column, *conditions):
    """ Retrieves unique values for a mapper class
    """
    col = getattr(mapper_class, column)

    sess = session()
    res = sess.query(func.trim(col))\
        .filter(*conditions)\
        .distinct()\
        .order_by(col)

    return [x[0] for x in res]


def get_unique_from_mapper_join(
        mapper_class,
        column,
        klass_join,
        order_field,
        *conditions,
        **kwargs):
    """ Retrieves unique values for a mapper class
    """
    page = kwargs.get('page', 0)
    col = getattr(mapper_class, column)

    sess = session()
    q = sess.query(col).join(klass_join).filter(
        *conditions
    ).order_by(order_field)

    total = q.count()
    item = q.offset(page).limit(1).first()

    return [total, item]


def get_all_columns_from_mapper(mapper_class, column, *conditions):
    """ Retrieves all columns for a mapper class
    """
    col = getattr(mapper_class, column)

    sess = session()
    res = sess.query(mapper_class).filter(*conditions).order_by(col)

    return_value = [x for x in res]

    return return_value


def get_marine_unit_ids(**data):
    """ Return a list of available MarineUnitIDs for the query
    """
    table = sql.t_MSFD4_GegraphicalAreasID
    col = table.c.MarineUnitID

    sess = session()
    query = sess.query(col).filter(
        table.c.MemberState.in_(data['member_states']),
        table.c.RegionSubRegions.in_(data['region_subregions']),
        table.c.AreaType.in_(data['area_types']),
    )

    l = sorted([x[0] for x in query])

    return (query.count(), l)


def get_item_by_conditions(mapper_class, order_field, *conditions, **kwargs):
    """Paged retrieval of items based on conditions
    """

    page = kwargs.get('page', 0)
    sess = session()
    order_field = getattr(mapper_class, order_field)
    q = sess.query(mapper_class).filter(
        *conditions
    ).order_by(order_field)

    total = q.count()
    item = q.offset(page).limit(1).first()

    return [total, item]


def get_item_by_conditions_joined(
        mapper_class,
        klass_join,
        order_field,
        *conditions,
        **kwargs):
    # Paged retrieval of items based on conditions with joining two tables
    page = kwargs.get('page', 0)
    sess = session()
    order_field = getattr(mapper_class, order_field)
    q = sess.query(mapper_class).join(klass_join).filter(
        *conditions
    ).order_by(order_field)

    total = q.count()
    item = q.offset(page).limit(1).first()

    return [total, item]


def get_table_records(columns, *conditions, **kwargs):
    order_by = kwargs.get('order_by')
    sess = session()
    q = sess.query(*columns).filter(*conditions)

    if order_by:
        q = q.order_by(order_by)

    total = q.count()

    return total, q


def get_available_marine_unit_ids(marine_unit_ids, klass):
    """ Returns a list of which muid is available, of the ones provided
    """
    sess = session()
    q = sess.query(klass.MarineUnitID).filter(
        klass.MarineUnitID.in_(marine_unit_ids)
    ).order_by(klass.MarineUnitID).distinct()

    total = q.count()

    return [total, q]


def get_marine_unit_id_names(marine_unit_ids):
    """ Returns tuples of (id, label) based on the marine_unit_ids
    """
    sess = session()
    t = sql.t_MSFD4_GegraphicalAreasID

    q = sess.query(t.c.MarineUnitID, t.c.MarineUnits_ReportingAreas)\
        .filter(t.c.MarineUnitID.in_(marine_unit_ids))\
        .order_by(t.c.MarineUnits_ReportingAreas)\
        .distinct()

    total = q.count()

    return [total, q]


# def get_a10_feature_targets(target_id):
#     """ Used in extra_data for A10
#     """
#     conn = connection()
#     res = conn.execute(text("""
# SELECT DISTINCT FeatureType, PhysicalChemicalHabitatsFunctionalPressures
# FROM MarineDB.dbo.MSFD10_FeaturesPressures
# WHERE MSFD10_Target = :target_id
# """), target_id=target_id)
#
#     items = []
#
#     for item in res:
#         items.append(item)
#
#     return sorted(items)
#
#
# def get_a10_criteria_indicators(target_id):
#     conn = connection()
#     res = conn.execute(text("""
# SELECT DISTINCT GESDescriptorsCriteriaIndicators
# FROM MarineDB.dbo.MSFD10_DESCrit
# WHERE MSFD10_Target = :target_id
# """), target_id=target_id)
#
#     items = []
#
#     for item in res:
#         items.append(item)
#
#     return sorted(items)


def get_related_record(klass, column, rel_id):
    sess = session()
    q = sess.query(klass).filter(
        getattr(klass, column) == rel_id
    )
    item = q.first()

    return [q.count(), item]


def get_related_record_join(klass, klass_join, column, rel_id):
    sess = session()
    q = sess.query(klass).join(klass_join).filter(
        getattr(klass_join, column) == rel_id
    )
    item = q.first()

    return [q.count(), item]


def get_all_records(mapper_class, *conditions):
    sess = session()
    q = sess.query(mapper_class).filter(*conditions)

    return [q.count(), q]
