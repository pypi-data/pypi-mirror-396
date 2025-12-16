"""Google Air Quality Library API Data Model."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class AQICategory:
    """Represents an AQI category with normalized and original names."""

    normalized: str
    original: str


class AQICategoryMapping:
    """Mapping of AQI categories to their normalized and original names."""

    _reverse_mapping: ClassVar[dict[str, str] | None] = None
    _mapping: ClassVar[dict[str, list[AQICategory]]] = {
        "uaqi": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("low_air_quality", "Low air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
        ],
        "and_aire": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("regular_air_quality", "Regular air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
        ],
        "aus_combined": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "aus_nsw": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("extremely_poor_air_quality", "Extremely poor air quality"),
        ],
        "aut_umwelt": [
            AQICategory("1_green", "1 - Green"),
            AQICategory("2_light_green", "2 - Light green"),
            AQICategory("3_yellow", "3 - Yellow"),
            AQICategory("4_orange", "4 - Orange"),
            AQICategory("5_red", "5 - Red"),
        ],
        "aut_vienna": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("unsatisfactory_air_quality", "Unsatisfactory air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "bel_irceline": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fairly_good_air_quality", "Fairly good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
            AQICategory("horrible_air_quality", "Horrible air quality"),
        ],
        "bgd_case": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("caution", "Caution"),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very Unhealthy air quality"),
            AQICategory(
                "extremely_unhealthy_air_quality", "Extremely Unhealthy air quality"
            ),
        ],
        "bgr_niggg": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "bra_saopaulo": [
            AQICategory("n1_good_air_quality", "N1 - Good air quality"),
            AQICategory("n2_moderate_air_quality", "N2 - Moderate air quality"),
            AQICategory("n3_bad_air_quality", "N3 - Bad air quality"),
            AQICategory("n4_very_bad_air_quality", "N4 - Very bad air quality"),
            AQICategory("n5_poor_air_quality", "N5 - Poor air quality"),
        ],
        "can_ec": [
            AQICategory("low_health_risk", "Low health risk"),
            AQICategory("moderate_health_risk", "Moderate health risk"),
            AQICategory("high_health_risk", "High health risk"),
            AQICategory("very_high_health_risk", "Very high health risk"),
        ],
        "caqi": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "che_cerclair": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("evident_air_pollution", "Evident air pollution"),
            AQICategory("considerable_air_pollution", "Considerable air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "chn_mep": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("light_air_pollution", "Light air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("heavy_air_pollution", "Heavy air pollution"),
            AQICategory("severe_air_pollution", "Severe air pollution"),
        ],
        "col_rmcab": [
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("regular_air_quality", "Regular air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "cri_icca": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory(
                "unfavorable_air_quality_for_sensitive_groups",
                "Unfavorable air quality for sensitive groups",
            ),
            AQICategory("unfavorable_air_quality", "Unfavorable air quality"),
            AQICategory("very_unfavorable_air_quality", "Very unfavorable air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "cyp_dli": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "cze_chmi": [
            AQICategory("1a_very_good_air_quality", "1A - Very good air quality"),
            AQICategory("1b_good_air_quality", "1B - Good air quality"),
            AQICategory("2a_acceptable_air_quality", "2A - Acceptable air quality"),
            AQICategory("2b_acceptable_air_quality", "2B - Acceptable air quality"),
            AQICategory("3a_aggravated_air_quality", "3A - Aggravated air quality"),
            AQICategory("3b_bad_air_quality", "3B - Bad air quality"),
        ],
        "deu_lubw": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("sufficient_air_quality", "Sufficient air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "deu_uba": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
        ],
        "dnk_aarhus": [
            AQICategory("below_average_air_pollution", "Below average air pollution"),
            AQICategory("average_air_pollution", "Average air pollution"),
            AQICategory("above_average_air_pollution", "Above average air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("warning_air_pollution", "Warning level air pollution"),
        ],
        "eaqi": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("extremely_poor_air_quality", "Extremely poor air quality"),
        ],
        "ecu_quitoambiente": [
            AQICategory("desirable_air_quality", "Desirable air quality"),
            AQICategory("acceptable_air_quality", "Acceptable air quality"),
            AQICategory("precautionary_level", "Precautionary level"),
            AQICategory("alert_level", "Alert level"),
            AQICategory("alarm_level", "Alarm level"),
            AQICategory("emergency_level", "Emergency level"),
        ],
        "esp_madrid": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("acceptable_air_quality", "Acceptable air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
        ],
        "esp_miteco": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("reasonably_good_air_quality", "Reasonably good air quality"),
            AQICategory("regular_air_quality", "Regular air quality"),
            AQICategory("unfavorable_air_quality", "Unfavorable air quality"),
            AQICategory("very_unfavorable_air_quality", "Very unfavorable air quality"),
            AQICategory(
                "extremely_unfavorable_air_quality", "Extremely unfavorable air quality"
            ),
        ],
        "est_ekuk": [
            AQICategory("very_good_air_quality", "Very Good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("medium_air_quality", "Medium air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very Bad air quality"),
        ],
        "fin_hsy": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
        ],
        "fra_atmo": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("medium_air_quality", "Medium air quality"),
            AQICategory("degraded_air_quality", "Degraded air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
            AQICategory("extremely_bad_air_quality", "Extremely bad air quality"),
        ],
        "gbr_defra": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "gib_gea": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "hkg_epd": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
            AQICategory("serious_air_pollution", "Serious air pollution"),
        ],
        "hrv_azo": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "hun_bler": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "idn_menlhk": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "ind_cpcb": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("severe_air_quality", "Severe air quality"),
        ],
        "irl_epa": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
        ],
        "isr_moep": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "ita_moniqa": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
        ],
        "jpn_aeros": [
            AQICategory("1_blue", "1 - Blue"),
            AQICategory("2_cyan", "2 - Cyan"),
            AQICategory("3_green", "3 - Green"),
            AQICategory("4_yellow_watch", "4 - Yellow/Watch"),
            AQICategory("5_orange_alert", "5 - Orange/Alert"),
            AQICategory("6_red_alert", "6 - Red/Alert+"),
        ],
        "kor_airkorea": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
        ],
        "kwt_beatona": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "lie_cerclair": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("evident_air_pollution", "Evident air pollution"),
            AQICategory("considerable_air_pollution", "Considerable air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "ltu_gamta": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("average_air_pollution", "Average air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "lux_emwelt": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fairly_good_air_quality", "Fairly good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
            AQICategory("horrible_air_quality", "Horrible air quality"),
        ],
        "mex_cdmx": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("regular_air_quality", "Regular air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("extremely_poor_air_quality", "Extremely poor air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "mex_gto": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("unsatisfactory_air_quality", "Unsatisfactory air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "mex_icars": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("acceptable_air_quality", "Acceptable air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("extremely_poor_air_quality", "Extremely poor air quality"),
        ],
        "mkd_moepp": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "mng_eic": [
            AQICategory("clean", "Clean"),
            AQICategory("normal", "Normal"),
            AQICategory("low", "Low pollution"),
            AQICategory("moderate_air_pollution", "Moderate pollution"),
            AQICategory("high_air_pollution", "High pollution"),
            AQICategory("very_high_air_pollution", "Very High pollution"),
        ],
        "mng_ubgov": [
            AQICategory("clean", "Clean"),
            AQICategory("normal", "Normal"),
            AQICategory("slightly_polluted", "Slightly Polluted"),
            AQICategory("polluted", "Polluted"),
            AQICategory("heavily_polluted", "Heavily Polluted"),
            AQICategory("seriously_polluted", "Seriously Polluted"),
        ],
        "mys_doe": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "nld_rivm": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "nor_nilu": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "npl_doenv": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("moderately_polluted", "Moderately polluted"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("very_poor_air_quality", "Very poor air quality"),
            AQICategory("severe_air_quality", "Severe air quality"),
        ],
        "nzl_lawa": [
            AQICategory("below_10", "Less than 10% of guideline"),
            AQICategory("10_33", "10-33% of guideline"),
            AQICategory("33_66", "33-66% of guideline"),
            AQICategory("66_100", "66-100% of guideline"),
            AQICategory("greater_100", "Greater than 100% of guideline"),
        ],
        "per_infoaire": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("alert", "Alert threshold"),
        ],
        "phl_emb": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("fair_air_quality", "Fair air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("acutely_unhealthy", "Acutely unhealthy air quality"),
            AQICategory("emergency", "Emergency"),
        ],
        "pol_gios": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("sufficient_air_quality", "Sufficient air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "prt_qualar": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("low_air_quality", "Low air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
        ],
        "rou_calitateaer": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "sgp_nea": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "srb_sepa": [
            AQICategory("excellent", "Excellent"),
            AQICategory("good", "Good"),
            AQICategory("acceptable", "Acceptable"),
            AQICategory("polluted", "Polluted"),
            AQICategory("very_polluted", "Very Polluted"),
        ],
        "svk_shmu": [
            AQICategory("very_good_air_quality", "Very good air quality"),
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very bad air quality"),
        ],
        "tha_pcd": [
            AQICategory("excellent_air_quality", "Excellent air quality"),
            AQICategory("satisfactory_air_quality", "Satisfactory air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
        ],
        "tur_havaizleme": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy for sensitive groups air quality"
            ),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "twn_epa": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "usa_epa": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "usa_epa_nowcast": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("moderate_air_quality", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("unhealthy_air_quality", "Unhealthy air quality"),
            AQICategory("very_unhealthy_air_quality", "Very unhealthy air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
        "vnm_vea": [
            AQICategory("good_air_quality", "Good air quality"),
            AQICategory("average_air_quality", "Average air quality"),
            AQICategory("poor_air_quality", "Poor air quality"),
            AQICategory("bad_air_quality", "Bad air quality"),
            AQICategory("very_bad_air_quality", "Very Bad air quality"),
            AQICategory("hazardous_air_quality", "Hazardous air quality"),
        ],
    }

    @classmethod
    def get_reverse_mapping(cls) -> dict[str, str]:
        """Build and return a cached reverse mapping (Ruff-konform)."""
        if (
            not hasattr(cls, "_cached_reverse_mapping")
            or cls._cached_reverse_mapping is None
        ):
            reverse_map = {}
            for category_list in cls._mapping.values():
                for category in category_list:
                    if category.original.lower() not in reverse_map:
                        reverse_map[category.original.lower()] = category.normalized
            cls._cached_reverse_mapping = reverse_map
        return cls._cached_reverse_mapping

    @classmethod
    def get(cls, code: str) -> list[AQICategory] | None:
        """Return the AQI categories for a given code."""
        return cls._mapping.get(code)

    @classmethod
    def get_all(cls) -> list[AQICategory]:
        """Return all AQI categories across all mappings."""
        categories = []
        for entries in cls._mapping.values():
            categories.extend(entries)
        return categories
