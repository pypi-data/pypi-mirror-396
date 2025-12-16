from __future__ import annotations

import copy
import json
from pathlib import Path

from sqlalchemy import exc, select

import sunpeek.components as cmp
from sunpeek.common.errors import ConfigurationError, DuplicateNameError


def _check_collector_in_db(session, coll_name):
    if session is not None:
        import sqlalchemy.exc
        try:
            session.execute(
                select(cmp.Collector).filter(cmp.Collector.name == coll_name)
            ).scalar_one()
            return True
        except sqlalchemy.exc.NoResultFound:
            return False
    return False


def make_full_plant(conf: dict, session=None) -> cmp.Plant:
    """Create a Plant from a configuration dictionary.

    Parameters
    ----------
    conf : dict
        Configuration dictionary containing plant specification.
        May include 'collectors' and 'plant' keys at the top level,
        or plant configuration directly.
    session : sqlalchemy.orm.Session, optional
        Database session. If provided, the plant is added to the session.

    Returns
    -------
    cmp.Plant
        The created Plant instance.

    Raises
    ------
    ConfigurationError
        If collector test_type is not 'SST' or 'QDT'.
    """
    conf = copy.deepcopy(conf)
    collectors = {}

    # 1) Handle collectors
    if 'collectors' in conf:
        colls = conf['collectors']
        for coll in colls:
            test_type = coll.pop('test_type')
            if _check_collector_in_db(session, coll['name']):
                coll_obj = coll['name']
            elif test_type in ['SST', "static"]:
                coll_obj = cmp.CollectorSST(**coll)
            elif test_type in ['QDT', "dynamic"]:
                coll_obj = cmp.CollectorQDT(**coll)
            else:
                raise ConfigurationError(
                    "Collector test_type parameter must be 'SST' or 'QDT'.")
            collectors[coll_obj.name] = coll_obj

    # 2) Extract plant config
    if 'plant' in conf:
        conf = conf['plant']
        # Replace collector names in arrays
        for array in conf['arrays']:
            if array['collector'] in collectors.keys():
                array['collector'] = collectors[array['collector']]

    # 3) Extract operational events, if any
    operational_events = conf.pop('operational_events', [])

    # 4) Create plant instance
    plant = cmp.Plant(**conf)

    # 5) Attach operational events
    for evt in operational_events:
        cmp.OperationalEvent(**{**evt, "plant": plant})
        # no need to explicitly append to plant.operational_events

    # 6) Persist data
    if session is not None:
        session.add(plant)
        # session.rollback()

    return plant


def make_plant_from_config_file(config_path: str | Path, session=None) -> cmp.Plant:
    """Create a Plant from a JSON configuration file.

    Parameters
    ----------
    config_path : str | Path
        Path to the JSON configuration file.
    session : sqlalchemy.orm.Session, optional
        Database session for persistence.

    Returns
    -------
    cmp.Plant
        The created Plant instance.
    """
    with open(config_path) as f:
        conf = json.load(f)
    return make_full_plant(conf, session)


def make_and_store_plant(conf: dict, session) -> cmp.Plant:
    """Create a Plant from a configuration dictionary and persist it to the database.

    Parameters
    ----------
    conf : dict
        Configuration dictionary containing plant specification.
    session : sqlalchemy.orm.Session
        Database session for persistence (required).

    Returns
    -------
    cmp.Plant
        The created and persisted Plant instance.

    Raises
    ------
    DuplicateNameError
        If a plant with the same name already exists in the database.
    """
    plant = make_full_plant(conf, session)
    session.add(plant)

    try:
        session.flush()
    except exc.IntegrityError as e:
        session.rollback()
        raise DuplicateNameError(f'Plant with name "{plant.name}" already exists.')

    return plant

