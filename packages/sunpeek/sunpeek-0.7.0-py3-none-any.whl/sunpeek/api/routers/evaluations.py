from typing import Union, List
import pandas as pd
import datetime as dt
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse, FileResponse

import sunpeek.components.helpers
from sunpeek.api.routers.helper import update_obj
from sunpeek.api.dependencies import session, crud
from sunpeek.api.routers.plant import plant_router
# from sunpeek.api.routers.config import config_router
from sunpeek.core_methods.power_check import PowerCheckFormulaeEnum, PowerCheckMethods
from sunpeek.core_methods.power_check.wrapper import run_power_check, list_feedback
import sunpeek.core_methods.power_check.plotting as plot
import sunpeek.common.plot_utils as pu
import sunpeek.serializable_models as smodels
import sunpeek.common.errors as errors

evaluations_router = APIRouter(
    prefix=plant_router.prefix + "/evaluations",
    tags=["methods", "evaluations"]
)


@evaluations_router.get("/power_check", summary="Run the Power Check", response_model=smodels.PowerCheckOutput)
def run_power_check_api(plant_id: int,
                        method: Union[PowerCheckMethods, None] = None,
                        formula: Union[PowerCheckFormulaeEnum, None] = None,
                        eval_start: Union[dt.datetime, None] = None,
                        eval_end: Union[dt.datetime, None] = None,
                        ignore_wind: Union[bool, None] = None,
                        safety_pipes: Union[float, None] = None,
                        safety_uncertainty: Union[float, None] = None,
                        safety_others: Union[float, None] = None,
                        max_nan_density: Union[float, None] = None,   # 0.0 - 1.0
                        min_data_in_interval: Union[int, None] = None,
                        max_gap_in_interval: Union[int, None] = None, # seconds
                        min_intervals_in_output: Union[int, None] = None,
                        interval_length: Union[int, None] = None,    # seconds
                        sess=Depends(session), crd=Depends(crud)):
    """Runs the Power Check for the specified dates range.
    """
    plant = crd.get_plants(sess, plant_id=plant_id)

    # Convert integer seconds to timedelta
    interval_length_td = pd.Timedelta(seconds=interval_length) if interval_length else None
    max_gap_td = pd.Timedelta(seconds=max_gap_in_interval) if max_gap_in_interval is not None else None

    try:
        power_check_result = run_power_check(
            plant=plant,
            method=[method],
            formula=[formula],
            use_wind=[None] if ignore_wind is None else [not ignore_wind],
            eval_start=eval_start,
            eval_end=eval_end,
            safety_pipes=safety_pipes,
            safety_uncertainty=safety_uncertainty,
            safety_others=safety_others,
            interval_length=interval_length_td,
            max_nan_density=max_nan_density,
            min_data_in_interval=min_data_in_interval,
            max_gap_in_interval=max_gap_td,
            min_intervals_in_output=min_intervals_in_output,
        )
    except errors.NoDataError as e:
        return JSONResponse(
            status_code=400,
            content={'error': 'Cannot run Thermal Power Check analysis.',
                     'message': str(e)}
        )

    power_check_output = power_check_result.output
    if power_check_output is not None:
        return power_check_output

    # power_check_output None -> None of the Power Check strategies was successful -> Return problem report
    return JSONResponse(
        status_code=400,
        content={'error': 'Could not calculate Thermal Power Check analysis.',
                 'message': f'None of the chosen Power Check strategies '
                            f'({len(power_check_result.feedback.sub_feedback)}) was successful.',
                 'detail': power_check_result.feedback.parse()}
    )


@evaluations_router.get("/power_check_report", summary="Run the Power Check and create a PDF report")
def get_power_check_pdf_report(plant_id: int,
                               method: Union[PowerCheckMethods, None] = None,
                               formula: Union[PowerCheckFormulaeEnum, None] = None,
                               eval_start: Union[dt.datetime, None] = None,
                               eval_end: Union[dt.datetime, None] = None,
                               ignore_wind: Union[bool, None] = None,
                               safety_pipes: Union[float, None] = None,
                               safety_uncertainty: Union[float, None] = None,
                               safety_others: Union[float, None] = None,
                               with_interval_plots: Union[bool, None] = None,
                               include_creation_date: Union[bool, None] = None,
                               anonymize: Union[bool, None] = None,
                               max_nan_density: Union[float, None] = None,
                               min_data_in_interval: Union[int, None] = None,
                               max_gap_in_interval: Union[int, None] = None,
                               min_intervals_in_output: Union[int, None] = None,
                               interval_length: Union[int, None] = None,
                               sess=Depends(session), crd=Depends(crud)):
    """Run the Power Check for the specified dates range and return a PDF report.

    Time-related parameters (interval_length, max_gap_in_interval) are specified in seconds.
    For example, interval_length=3600 represents 1 hour.
    """
    power_check_output = run_power_check_api(plant_id=plant_id,
                                             method=method,
                                             formula=formula,
                                             eval_start=eval_start,
                                             eval_end=eval_end,
                                             ignore_wind=ignore_wind,
                                             safety_pipes=safety_pipes,
                                             safety_uncertainty=safety_uncertainty,
                                             safety_others=safety_others,
                                             interval_length=interval_length,
                                             max_nan_density=max_nan_density,
                                             min_data_in_interval=min_data_in_interval,
                                             max_gap_in_interval=max_gap_in_interval,
                                             min_intervals_in_output=min_intervals_in_output,
                                             sess=sess, crd=crd)

    # Check if no intervals found
    if power_check_output.plant_output.n_intervals == 0:
        return JSONResponse(
            status_code=400,
            content={'error': 'Thermal Power Check found no intervals.',
                     'message': 'Thermal Power Check found no intervals.',
                     'detail': 'The Thermal Power Check analysis completed successfully, '
                               'but found no valid intervals in the specific time range.'}
        )

    # Create pdf report
    settings = pu.PlotSettings(with_interval_plots=with_interval_plots,
                               include_creation_date=include_creation_date,
                               anonymize=anonymize)
    pdf_path = plot.create_pdf_report(power_check_output=power_check_output, settings=settings)
    response = FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.name)

    return response


@evaluations_router.get("/power_check_feedback",
                        summary="Feedback about which Power Check variants can be run with the given plant configuration",
                        response_model=List[smodels.PowerCheckFeedback])
def list_power_check_feedback_api(plant_id: int,
                                  method: Union[PowerCheckMethods, None] = None,
                                  formula: Union[PowerCheckFormulaeEnum, None] = None,
                                  ignore_wind: Union[bool, None] = None,
                                  sess=Depends(session), crd=Depends(crud)) -> List[smodels.PowerCheckFeedback]:
    """List problems for the Power Check for the specified dates range"""
    plant = crd.get_plants(sess, plant_id=plant_id)
    power_check_feedback = list_feedback(
        plant=plant,
        method=[method],
        formula=[formula],
        use_wind=None if ignore_wind is None else [not ignore_wind],
    )

    return power_check_feedback


@evaluations_router.get("/power_check_settings",
                        summary="Get Settings for the Power Check",
                        response_model=smodels.PowerCheckSettings)
def get_power_check_settings(plant_id: int,
                             sess=Depends(session), crd=Depends(crud)):
    """Get Power Check settings for given plant.
    """
    settings = crd.get_components(sess, sunpeek.components.helpers.PowerCheckSettingsDefaults, plant_id=plant_id)
    if len(settings) == 1:
        return settings[0]
    return JSONResponse(
        status_code=400,
        content={'error': 'Power Check Settings not found.',
                 'message': 'No Power Check setting seems to be directly assigned to this plant.',
                 'detail': 'This might happen if the submitted plant_id is incorrect or missing, or in case '
                           'multiple/no Settings are assigned to the plant due to a inconsistency in the database.'}
    )


@evaluations_router.post("/power_check_settings",
                         summary="Update Settings for the Power Check",
                         response_model=smodels.PowerCheckSettings)
def update_power_check_settings(plant_id: int,
                                setting_update: smodels.PowerCheckSettings,
                                sess=Depends(session), crd=Depends(crud)):
    """Update Power Check settings for given plant.
    """
    setting = crd.get_components(sess, component=sunpeek.components.helpers.PowerCheckSettingsDefaults,
                                 plant_id=plant_id)
    if len(setting) != 1:
        return JSONResponse(
            status_code=400,
            content={'error': 'Power Check Settings not found.',
                     'message': 'Settings for the Power Check not found.',
                     'detail': 'This might happen if the submitted plant_id is incorrect or missing, or in case '
                               'multiple/no settings are assigned to the plant due to a inconsistency in the database.'}
        )
    setting = setting[0]
    setting = update_obj(setting, setting_update)
    setting = crd.update_component(sess, setting)
    return setting

# @evaluations_router.get("/power_check", summary="Run the Power Check", response_model=smodels.PCMethodOutput)
# def quick_run_power_check_api(plant_id: int, method: AvailablePowerCheckMethods,
#                         equation: Union[AvailablePCEquations, None],
#                         eval_start: Union[dt.datetime, None] = None,
#                         eval_end: Union[dt.datetime, None] = None,
#                         sess=Depends(session), crd=Depends(crud)):
#     """Runs the Power Check for the specified dates range"""
#     plant = crd.get_plants(sess, plant_id=plant_id)
#     plant.context.set_eval_interval(eval_start=eval_start, eval_end=eval_end)
#     power_check_obj = PCMethod.create(method=method.name, plant=plant, equation=equation)
#     power_check_output = power_check_obj.run()
#     return power_check_output


# @methods_router.get("/get-dcat-method-results")
# async def get_dcat_method_results(plant_id: str, start_date: str = "2021-05-20 13:00:00", end_date: str = "2021-05-21 13:00:00"):
#     """Retrieves the results of the DCAT method for the specified dates range"""
#     results_dict = {"plant_id": plant_id,"start_date":start_date, "end_date":end_date, "results_array": [1,1,2,1.5] }
#     return results_dict


# @methods_router.get("/run-power_check-method")
# async def run_power_check_api(plant_id: str, start_date: str = "2021-05-20 13:00:00", end_date: str = "2021-05-21 13:00:00"):
#     """Runs the Power Check on the clean data stored between the specified dates range"""
#
#     results_dict = {"plant_id": plant_id,"start_date":start_date, "end_date":end_date, "results_array": [.35,.39,1.69,4.86,6.23,.51,5.25] }
#
#     return results_dict


# @methods_router.get("/run-dcat-method")
# async def run_dcat_method(plant_id: str, start_date: str = "2021-05-20 13:00:00", end_date: str = "2021-05-21 13:00:00"):
#     """Runs the DCAT method on the clean data stored between the specified dates range"""
#
#     results_dict = {"plant_id": plant_id,"start_date":start_date, "end_date":end_date, "results_array": [.35,.39,1.69,4.86,6.23,.51,5.25] }
#
#     return results_dict


## Stale - not planned to be supported

# @evaluations_router.get("/run")
# @stored_evaluations_router.get("/run", tags=["methods", "evaluations"])
# def run(plant_id: int, stored_eval_id: int, method: str = None,
#         eval_start: str = "1900-01-01 00:00:00", eval_end: str = "2021-01-01 00:00:00",
#         sess=Depends(session), crd=Depends(crud)):
#     crd.get_plants(sess, plant_id=plant_id)
#     raise HTTPException(status_code=501,
#                         detail="Stored evaluations are not yet implemented in SunPeek", headers=
#                         {"Retry-After": "Wed, 30 Nov 2022 23:59 GMT", "Cache-Control": "no-cache"})
