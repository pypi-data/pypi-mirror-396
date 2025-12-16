"""
This module holds an example to show the functionality of the SunPeek package and the Performance Check method.

The Python code shows how to configure the plant / collector array, call the Performance Check method (ISO 24194) and
produce some plots. 
This script is based on the FHW / Fernheizwerk plant in Graz, Austria.
The data used here (together with a detailed description) is available at https://doi.org/10.5281/zenodo.7741084

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Marnoch Hamilton-Jones <m.hamilton-jones@aee.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
"""

import logging

import sunpeek.demo
from sunpeek.common import config_parser
from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.utils import DatetimeTemplates
from sunpeek.components import CoolPropFluid, FluidFactory, Plant
from sunpeek.core_methods.power_check.plotting import create_pdf_report
from sunpeek.core_methods.power_check.wrapper import run_power_check
from sunpeek.data_handling.wrapper import use_csv
from sunpeek.definitions.collectors import get_definition as get_collector_definition
from sunpeek.definitions.fluid_definitions import WPDFluids, get_definition
from sunpeek.demo.demo_plant import requires_demo_data

logging.getLogger('sp_logger').setLevel(logging.INFO)


def get_fluid(fluid: str | WPDFluids = WPDFluids.fhw_pekasolar):
    """Return heat transfer fluid: Default is fluid of FHW plant. Choose other fluid to see how they would behave.
    """
    fluid_str = fluid.value.name if isinstance(fluid, WPDFluids) else fluid

    if fluid_str == WPDFluids.fhw_pekasolar.value.name:
        # FHW laboratory-tested fluid, with property models trained from csv files
        return FluidFactory(fluid=get_definition(fluid_str))

    # Examples of CoolProp fluids
    if fluid_str.lower() == 'water':
        return FluidFactory(fluid=get_definition('water'))

    fluid = CoolPropFluid(get_definition(fluid_str), concentration=Q(40, 'percent'))

    if fluid is not None:
        return fluid
    raise ValueError(f'Unknown fluid string "{fluid_str}".')


def get_demo_plant_nodata() -> Plant:
    """Return configured FHW plant ("demo plant") without data, but with fluid and collector set.

    Returns
    -------
    `plant` : A :class:`physical.Plant` object, the FHW demo plant: https://doi.org/10.5281/zenodo.7741084
    """
    p = config_parser.make_plant_from_config_file(sunpeek.demo.DEMO_CONFIG_PATH)
    # Define collector type
    p.arrays[0].collector = get_collector_definition("Arcon 3510")

    # Define heat transfer fluid
    p.fluid_solar = get_fluid()
    # This is just to showcase how other fluids would be used:
    # p.fluid_solar = get_fluid('water')
    # p.fluid_solar = get_fluid('ASHRAE, Propylene Glycol')
    # p.fluid_solar = get_fluid('Antifrogen L')

    return p


if __name__ == '__main__':
    plant = get_demo_plant_nodata()
    # Submit measurement data
    requires_demo_data(None)
    data = sunpeek.demo.DEMO_DATA_PATH_2DAYS
    # data = sunpeek.demo.DEMO_DATA_PATH_1MONTH
    # data = sunpeek.demo.DEMO_DATA_PATH_1YEAR
    data_output = use_csv(plant, csv_files=[data], timezone='utc', datetime_template=DatetimeTemplates.year_month_day)

    # STEP 3: Run Performance Check method & create plots
    # Use default settings:
    power_check_output = run_power_check(plant).output
    # or try specific settings:
    # power_check_output = run_power_check(plant,
    #                                      method=['extended'],
    #                                      formula=[2],
    #                                      safety_uncertainty=0.9,
    #                                      ).output

    # Create pdf report
    report_path = create_pdf_report(power_check_output)
    # Include all hourly-interval plots -> may be slow!
    # report_path = create_pdf(power_check_output, include_interval_plots=True)
    # Optionally, open file
    # os.startfile(report_path)
