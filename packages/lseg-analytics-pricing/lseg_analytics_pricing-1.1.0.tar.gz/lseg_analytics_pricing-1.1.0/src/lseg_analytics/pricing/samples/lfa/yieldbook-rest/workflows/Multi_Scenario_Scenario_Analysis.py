import json as js

from lseg_analytics.pricing.yield_book_rest import (
        request_scenario_calculation_sync,
        CurveTypeAndCurrency,
        ScenarioCalcGlobalSettings,
        Scenario,
        ScenarioDefinition,
        SystemScenario,
        ScenarioCalcInput,
        SettlementInfo,
        HorizonInfo,
)

global_settings = ScenarioCalcGlobalSettings(
            pricing_date="2025-01-01",
        )

scenario_1 = Scenario(
            scenario_id="ScenID1",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="BEARFLAT100")
            ),
        )

scenario_2 = Scenario(
            scenario_id="ScenID2",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="BULLFLAT50")
            ),
        )

scenario_3 = Scenario(
            scenario_id="ScenID3",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="YR20PLUS25")
            ),
        )

scenario_4 = Scenario(
            scenario_id="ScenID4",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="PC3MOCOMP1DOWN")
            ),
        )

scenario_5 = Scenario(
            scenario_id="ScenID5",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="IRRBB26STEEP")
            ),
        )

# Combining Scenarios and Input instruments and parameters
input_1 = ScenarioCalcInput(
            identifier="US742718AV11",
            id_type="ISIN",
            curve=CurveTypeAndCurrency(
                curve_type="GVT",
                currency="USD",
            ),
            settlement_info=SettlementInfo(
                level="100",
            ),
            horizon_info=[
                HorizonInfo(
                    scenario_id="ScenID1",
                    level="100",
                ),                
                HorizonInfo(
                    scenario_id="ScenID2",
                    level="90",
                ),                
                HorizonInfo(
                    scenario_id="ScenID4",
                    level="95",
                ),
                HorizonInfo(
                    scenario_id="ScenID5",
                    level="105",
                )
            ],
            horizon_py_method="OAS",
        )

input_2 = ScenarioCalcInput(
            identifier="91282CLF6",
            id_type="CUSIP",
            curve=CurveTypeAndCurrency(
                curve_type="GVT",
                currency="USD",
            ),
            settlement_info=SettlementInfo(
                level="99",
            ),
            horizon_info=[
                HorizonInfo(
                    scenario_id="ScenID2",
                    level="98.15",
                ),                
                HorizonInfo(
                    scenario_id="ScenID3",
                    level="91.47",
                ),                
                HorizonInfo(
                    scenario_id="ScenID4",
                    level="95.54",
                ),
                HorizonInfo(
                    scenario_id="ScenID5",
                    level="101.13",
                )
            ],
            horizon_py_method="OAS",
        )

# Execute Post sync request with prepared inputs
sa_sync_post_response = request_scenario_calculation_sync(
                            global_settings=global_settings,
                            scenarios=[scenario_1, scenario_2, scenario_3, scenario_4, scenario_5],
                            input=[input_1, input_2],
                        )

print(js.dumps(sa_sync_post_response, indent=4))