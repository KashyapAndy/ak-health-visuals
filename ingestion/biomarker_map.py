"""
Master biomarker registry.

Each entry defines:
  - canonical_name   : single display name used in DB and dashboard
  - canonical_unit   : the one unit we store in the DB
  - unit_conversions : { raw_unit_alias -> multiplier_to_canonical }
  - name_aliases     : list of raw strings that map to this biomarker
  - ref_range        : (low, high) typical adult reference range in canonical unit
                       (used as fallback if the PDF doesn't include one)
  - category         : grouping for dashboard panels

Conversion rule:
    stored_value = raw_value * unit_conversions[raw_unit]
    If raw_unit not in unit_conversions, value is stored as-is with a warning.
"""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class Biomarker:
    canonical_name:  str
    canonical_unit:  str
    category:        str
    name_aliases:    list[str]
    unit_conversions: dict[str, float]   # raw unit -> multiplier
    ref_low:         Optional[float] = None
    ref_high:        Optional[float] = None


REGISTRY: list[Biomarker] = [

    # =========================================================================
    # CBC
    # =========================================================================
    Biomarker(
        canonical_name="WBC",
        canonical_unit="10³/µL",
        category="CBC",
        name_aliases=["wbc", "white blood cell", "white blood cells",
                      "white blood count", "leukocytes", "total wbc",
                      "total leukocyte count", "tlc",
                      "white blood cell count", "wbc count",
                      "white cell count"],
        unit_conversions={
            "10³/µl": 1, "10^3/ul": 1, "k/ul": 1, "k/µl": 1,
            "thou/ul": 1, "×10³/µl": 1, "x10³/µl": 1,
            "10⁹/l": 1,   # 10⁹/L == 10³/µL
            "/cumm": 0.001, "cells/cumm": 0.001, "/mm³": 0.001,
            "thous/mcl": 1, "thds/cmm": 0.001, "thous/cmm": 0.001,
            "x10e3/ul": 1, "x10(3)/mcl": 1,
        },
        ref_low=4.5, ref_high=11.0,
    ),
    Biomarker(
        canonical_name="RBC",
        canonical_unit="10⁶/µL",
        category="CBC",
        name_aliases=["rbc", "red blood cell", "red blood cells",
                      "red blood count", "erythrocytes", "red cell count",
                      "red blood cell count", "red cell count"],
        unit_conversions={
            "10⁶/µl": 1, "10^6/ul": 1, "m/ul": 1, "mil/ul": 1,
            "×10⁶/µl": 1, "x10⁶/µl": 1, "10¹²/l": 1,
            "/cumm": 0.000001, "/mm³": 0.000001,
            "mill/mcl": 1, "mill/cmm": 0.000001, "x10e6/ul": 1,
            "x10(6)/mcl": 1, "million/ul": 1,
        },
        ref_low=4.5, ref_high=5.9,
    ),
    Biomarker(
        canonical_name="Hemoglobin",
        canonical_unit="g/dL",
        category="CBC",
        name_aliases=["hgb", "hb", "hemoglobin", "haemoglobin", "hgb."],
        unit_conversions={
            "g/dl": 1, "g/100ml": 1,
            "gm/dl": 1, "gm/100ml": 1,
            "g/l": 0.1, "gm/l": 0.1,
            "mmol/l": 1.6113,
        },
        ref_low=13.5, ref_high=17.5,
    ),
    Biomarker(
        canonical_name="Hematocrit",
        canonical_unit="%",
        category="CBC",
        name_aliases=["hct", "hematocrit", "haematocrit",
                      "packed cell volume", "pcv"],
        unit_conversions={
            "%": 1,
            "l/l": 100,   # 0.45 L/L -> 45%
            "proportion": 100,
        },
        ref_low=41.0, ref_high=53.0,
    ),
    Biomarker(
        canonical_name="MCV",
        canonical_unit="fL",
        category="CBC",
        name_aliases=["mcv", "mean corpuscular volume", "mean cell volume"],
        unit_conversions={"fl": 1, "fL": 1},
        ref_low=80.0, ref_high=100.0,
    ),
    Biomarker(
        canonical_name="MCH",
        canonical_unit="pg",
        category="CBC",
        name_aliases=["mch", "mean corpuscular hemoglobin", "mean cell hemoglobin"],
        unit_conversions={"pg": 1},
        ref_low=27.0, ref_high=33.0,
    ),
    Biomarker(
        canonical_name="MCHC",
        canonical_unit="g/dL",
        category="CBC",
        name_aliases=["mchc", "mean corpuscular hemoglobin concentration",
                      "mean cell hemoglobin concentration"],
        unit_conversions={"g/dl": 1, "gm/dl": 1, "gm/dL": 1, "GM/DL": 1, "g/l": 0.1, "%": 1},
        ref_low=32.0, ref_high=36.0,
    ),
    Biomarker(
        canonical_name="RDW",
        canonical_unit="%",
        category="CBC",
        name_aliases=["rdw", "rdw-cv", "rdw cv", "red cell distribution width",
                      "red blood cell distribution width"],
        unit_conversions={"%": 1},
        ref_low=11.5, ref_high=14.5,
    ),
    Biomarker(
        canonical_name="Platelets",
        canonical_unit="10³/µL",
        category="CBC",
        name_aliases=["plt", "platelets", "platelet count", "thrombocytes",
                      "platelet"],
        unit_conversions={
            "10³/µl": 1, "10^3/ul": 1, "k/ul": 1, "k/µl": 1,
            "thou/ul": 1, "×10³/µl": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "thous/mcl": 1, "thous/cmm": 0.001, "x10e3/ul": 1,
            "x10(3)/mcl": 1,
        },
        ref_low=150.0, ref_high=400.0,
    ),
    Biomarker(
        canonical_name="MPV",
        canonical_unit="fL",
        category="CBC",
        name_aliases=["mpv", "mean platelet volume"],
        unit_conversions={"fl": 1},
        ref_low=7.5, ref_high=12.5,
    ),

    # Differential
    Biomarker(
        canonical_name="Neutrophils %",
        canonical_unit="%",
        category="CBC Differential",
        name_aliases=["neutrophils %", "neutrophils", "neutrophil %",
                      "neut %", "neut%", "segs %", "segs", "pmn %",
                      "polymorphonuclear", "granulocytes %",
                      "neutro %", "neutrophils #"],
        unit_conversions={"%": 1},
        ref_low=40.0, ref_high=70.0,
    ),
    Biomarker(
        canonical_name="Neutrophils Abs",
        canonical_unit="10³/µL",
        category="CBC Differential",
        name_aliases=["neutrophils abs", "absolute neutrophils",
                      "absolute neutrophil count", "anc",
                      "neut abs", "neut #",
                      "neutrophils (absolute)", "neutrophils(absolute)",
                      "neutro absolute", "neutro abs"],
        unit_conversions={
            "10³/µl": 1, "k/ul": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "cells/mcl": 0.001, "cells/µl": 0.001, "cells/ul": 0.001,
            "x10(3)/mcl": 1, "x10e3/ul": 1,
        },
        ref_low=1.8, ref_high=7.7,
    ),
    Biomarker(
        canonical_name="Lymphocytes %",
        canonical_unit="%",
        category="CBC Differential",
        name_aliases=["lymphocytes %", "lymphocytes", "lymphocyte %",
                      "lymphs %", "lymphs", "lymph %",
                      "reactive lymph %"],
        unit_conversions={"%": 1},
        ref_low=20.0, ref_high=40.0,
    ),
    Biomarker(
        canonical_name="Lymphocytes Abs",
        canonical_unit="10³/µL",
        category="CBC Differential",
        name_aliases=["lymphocytes abs", "absolute lymphocytes",
                      "lymphs abs", "lymph abs", "lymph #",
                      "lymphs (absolute)", "lymphocytes (absolute)",
                      "lymph absolute", "lymphocytes #"],
        unit_conversions={
            "10³/µl": 1, "k/ul": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "cells/mcl": 0.001, "cells/µl": 0.001, "cells/ul": 0.001,
            "x10(3)/mcl": 1, "x10e3/ul": 1,
        },
        ref_low=1.0, ref_high=4.8,
    ),
    Biomarker(
        canonical_name="Monocytes %",
        canonical_unit="%",
        category="CBC Differential",
        name_aliases=["monocytes %", "monocytes", "monocyte %", "monos %", "monos",
                      "mono %"],
        unit_conversions={"%": 1},
        ref_low=2.0, ref_high=10.0,
    ),
    Biomarker(
        canonical_name="Monocytes Abs",
        canonical_unit="10³/µL",
        category="CBC Differential",
        name_aliases=["monocytes abs", "absolute monocytes", "monos abs",
                      "monocyte abs", "monocytes (absolute)", "monocytes(absolute)",
                      "mono abs", "mono #", "monocytes #"],
        unit_conversions={
            "10³/µl": 1, "k/ul": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "cells/mcl": 0.001, "cells/µl": 0.001, "cells/ul": 0.001,
            "x10(3)/mcl": 1, "x10e3/ul": 1,
        },
        ref_low=0.1, ref_high=0.9,
    ),
    Biomarker(
        canonical_name="Eosinophils %",
        canonical_unit="%",
        category="CBC Differential",
        name_aliases=["eosinophils %", "eosinophils", "eosinophil %",
                      "eos %", "eos"],
        unit_conversions={"%": 1},
        ref_low=1.0, ref_high=6.0,
    ),
    Biomarker(
        canonical_name="Eosinophils Abs",
        canonical_unit="10³/µL",
        category="CBC Differential",
        name_aliases=["eosinophils abs", "absolute eosinophils", "eos abs",
                      "eosinophil abs", "eosinophils (absolute)", "eos (absolute)",
                      "eos(absolute)", "eosinophils #"],
        unit_conversions={
            "10³/µl": 1, "k/ul": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "cells/mcl": 0.001, "cells/µl": 0.001, "cells/ul": 0.001,
            "x10(3)/mcl": 1, "x10e3/ul": 1,
        },
        ref_low=0.0, ref_high=0.4,
    ),
    Biomarker(
        canonical_name="Basophils %",
        canonical_unit="%",
        category="CBC Differential",
        name_aliases=["basophils %", "basophils", "basophil %",
                      "baso %", "basos %", "basos"],
        unit_conversions={"%": 1},
        ref_low=0.0, ref_high=2.0,
    ),
    Biomarker(
        canonical_name="Basophils Abs",
        canonical_unit="10³/µL",
        category="CBC Differential",
        name_aliases=["basophils abs", "absolute basophils", "baso abs",
                      "basophil abs", "basophils (absolute)", "baso (absolute)",
                      "baso(absolute)", "basophils #"],
        unit_conversions={
            "10³/µl": 1, "k/ul": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "cells/mcl": 0.001, "cells/µl": 0.001, "cells/ul": 0.001,
            "x10(3)/mcl": 1, "x10e3/ul": 1,
        },
        ref_low=0.0, ref_high=0.2,
    ),
    Biomarker(
        canonical_name="Immature Granulocytes %",
        canonical_unit="%",
        category="CBC Differential",
        name_aliases=["immature granulocytes", "immature granulocytes %",
                      "imm gran %", "ig %"],
        unit_conversions={"%": 1},
        ref_low=0.0, ref_high=1.0,
    ),
    Biomarker(
        canonical_name="Immature Granulocytes Abs",
        canonical_unit="10³/µL",
        category="CBC Differential",
        name_aliases=["immature grans (abs)", "imm gran absolute",
                      "absolute immature grans", "immature grans abs", "ig abs"],
        unit_conversions={
            "10³/µl": 1, "k/ul": 1, "10⁹/l": 1,
            "/cumm": 0.001, "/mm³": 0.001,
            "cells/mcl": 0.001, "cells/µl": 0.001, "cells/ul": 0.001,
            "x10(3)/mcl": 1, "x10e3/ul": 1,
        },
        ref_low=0.0, ref_high=0.1,
    ),

    # =========================================================================
    # Metabolic Panel (BMP / CMP)
    # =========================================================================
    Biomarker(
        canonical_name="Glucose",
        canonical_unit="mg/dL",
        category="Metabolic",
        name_aliases=["glucose", "blood glucose", "fasting glucose",
                      "gluc", "glucose fasting", "fbs", "fasting blood sugar",
                      "blood sugar", "glucose lvl random", "glucose random",
                      "sugar", "mean glucose est (calc)", "mean glucose est"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 18.018,
        },
        ref_low=70.0, ref_high=99.0,
    ),
    Biomarker(
        canonical_name="BUN",
        canonical_unit="mg/dL",
        category="Metabolic",
        name_aliases=["bun", "blood urea nitrogen", "urea nitrogen",
                      "urea", "blood urea", "urea nitrogen (bun)"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 2.8,
        },
        ref_low=7.0, ref_high=25.0,
    ),
    Biomarker(
        canonical_name="Creatinine",
        canonical_unit="mg/dL",
        category="Metabolic",
        name_aliases=["creatinine", "creat", "cr", "serum creatinine",
                      "creatinine serum"],
        unit_conversions={
            "mg/dl": 1,
            "µmol/l": 0.01131, "umol/l": 0.01131,
        },
        ref_low=0.74, ref_high=1.35,
    ),
    Biomarker(
        canonical_name="eGFR",
        canonical_unit="mL/min/1.73m²",
        category="Metabolic",
        name_aliases=["egfr", "estimated gfr", "glomerular filtration rate",
                      "gfr", "egfr (ckd-epi)", "egfr (mdrd)",
                      "egfr if nonafricn am", "egfr if africn am",
                      "gfr non african american", "gfr african american",
                      "egfr non-afr. american", "egfr african american",
                      "egfr non african american", "egfr african amer",
                      "egfr non-african amer"],
        unit_conversions={
            "ml/min/1.73m²": 1, "ml/min": 1,
            "ml/min/1.73m2": 1, "ml/min/1.73 m2": 1, "ml/min/1.73": 1,
        },
        ref_low=60.0, ref_high=None,
    ),
    Biomarker(
        canonical_name="BUN/Creatinine Ratio",
        canonical_unit="ratio",
        category="Metabolic",
        name_aliases=["bun/creatinine ratio", "bun/cr ratio",
                      "bun creatinine ratio", "bun/creat ratio"],
        unit_conversions={"ratio": 1, "": 1},
        ref_low=10.0, ref_high=20.0,
    ),
    Biomarker(
        canonical_name="Sodium",
        canonical_unit="mEq/L",
        category="Metabolic",
        name_aliases=["sodium", "na", "na+", "sodium serum", "sodium lvl"],
        unit_conversions={"meq/l": 1, "mmol/l": 1},
        ref_low=136.0, ref_high=145.0,
    ),
    Biomarker(
        canonical_name="Potassium",
        canonical_unit="mEq/L",
        category="Metabolic",
        name_aliases=["potassium", "k", "k+", "potassium serum", "potassium lvl"],
        unit_conversions={"meq/l": 1, "mmol/l": 1},
        ref_low=3.5, ref_high=5.1,
    ),
    Biomarker(
        canonical_name="Chloride",
        canonical_unit="mEq/L",
        category="Metabolic",
        name_aliases=["chloride", "cl", "cl-", "chloride serum"],
        unit_conversions={"meq/l": 1, "mmol/l": 1},
        ref_low=98.0, ref_high=107.0,
    ),
    Biomarker(
        canonical_name="CO2",
        canonical_unit="mEq/L",
        category="Metabolic",
        name_aliases=["co2", "carbon dioxide", "bicarbonate", "hco3",
                      "total co2", "co2 total", "carbon dioxide, total"],
        unit_conversions={"meq/l": 1, "mmol/l": 1},
        ref_low=22.0, ref_high=29.0,
    ),
    Biomarker(
        canonical_name="Calcium",
        canonical_unit="mg/dL",
        category="Metabolic",
        name_aliases=["calcium", "ca", "total calcium", "calcium serum",
                      "calcium total", "calcium lvl",
                      "calcium, serum", "calcium,"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 4.008,
        },
        ref_low=8.6, ref_high=10.3,
    ),
    Biomarker(
        canonical_name="Total Protein",
        canonical_unit="g/dL",
        category="Metabolic",
        name_aliases=["protein", "total protein", "serum protein",
                      "tp", "protein total",
                      "protein, total", "protein, total, serum",
                      "protein, total serum"],
        unit_conversions={"g/dl": 1, "gm/dl": 1, "g/l": 0.1},
        ref_low=6.3, ref_high=8.2,
    ),
    Biomarker(
        canonical_name="Albumin",
        canonical_unit="g/dL",
        category="Metabolic",
        name_aliases=["albumin", "alb", "albumin serum", "albumin lvl"],
        unit_conversions={"g/dl": 1, "gm/dl": 1, "g/l": 0.1},
        ref_low=3.5, ref_high=5.0,
    ),
    Biomarker(
        canonical_name="Globulin",
        canonical_unit="g/dL",
        category="Metabolic",
        name_aliases=["globulin", "total globulin", "globulin serum",
                      "globulin, total"],
        unit_conversions={"g/dl": 1, "gm/dl": 1, "g/l": 0.1},
        ref_low=2.0, ref_high=3.5,
    ),
    Biomarker(
        canonical_name="A/G Ratio",
        canonical_unit="ratio",
        category="Metabolic",
        name_aliases=["a/g ratio", "albumin/globulin ratio", "ag ratio",
                      "a:g ratio"],
        unit_conversions={"ratio": 1, "": 1},
        ref_low=1.2, ref_high=2.2,
    ),
    Biomarker(
        canonical_name="Total Bilirubin",
        canonical_unit="mg/dL",
        category="Liver",
        name_aliases=["bilirubin", "total bilirubin", "t bili", "t. bili",
                      "tbili", "bilirubin total", "bilirubin, total"],
        unit_conversions={
            "mg/dl": 1,
            "µmol/l": 0.05847, "umol/l": 0.05847,
        },
        ref_low=0.1, ref_high=1.2,
    ),
    Biomarker(
        canonical_name="Direct Bilirubin",
        canonical_unit="mg/dL",
        category="Liver",
        name_aliases=["direct bilirubin", "conjugated bilirubin",
                      "d bili", "bilirubin direct", "bilirubin, direct"],
        unit_conversions={
            "mg/dl": 1,
            "µmol/l": 0.05847, "umol/l": 0.05847,
        },
        ref_low=0.0, ref_high=0.3,
    ),
    Biomarker(
        canonical_name="Indirect Bilirubin",
        canonical_unit="mg/dL",
        category="Liver",
        name_aliases=["indirect bilirubin", "unconjugated bilirubin",
                      "bilirubin indirect"],
        unit_conversions={
            "mg/dl": 1,
            "µmol/l": 0.05847, "umol/l": 0.05847,
        },
        ref_low=0.1, ref_high=1.0,
    ),
    Biomarker(
        canonical_name="Alkaline Phosphatase",
        canonical_unit="U/L",
        category="Liver",
        name_aliases=["alkaline phosphatase", "alp", "alk phos", "alkphos",
                      "alk. phos.", "alkaline phosphatase serum",
                      "alkaline phosphatase, s"],
        unit_conversions={"u/l": 1, "iu/l": 1, "units/l": 1, "intl_unit/l": 1},
        ref_low=44.0, ref_high=147.0,
    ),
    Biomarker(
        canonical_name="ALT",
        canonical_unit="U/L",
        category="Liver",
        name_aliases=["alt", "alanine aminotransferase", "alanine transaminase",
                      "sgpt", "alt (sgpt)", "alanine aminotransferase (alt)"],
        unit_conversions={"u/l": 1, "iu/l": 1, "units/l": 1, "intl_unit/l": 1},
        ref_low=7.0, ref_high=56.0,
    ),
    Biomarker(
        canonical_name="AST",
        canonical_unit="U/L",
        category="Liver",
        name_aliases=["ast", "aspartate aminotransferase", "aspartate transaminase",
                      "sgot", "ast (sgot)", "aspartate aminotransferase (ast)"],
        unit_conversions={"u/l": 1, "iu/l": 1, "units/l": 1, "intl_unit/l": 1},
        ref_low=10.0, ref_high=40.0,
    ),
    Biomarker(
        canonical_name="GGT",
        canonical_unit="U/L",
        category="Liver",
        name_aliases=["ggt", "gamma-glutamyl transferase",
                      "gamma glutamyl transpeptidase",
                      "gamma-gt", "ggtp"],
        unit_conversions={"u/l": 1, "iu/l": 1, "units/l": 1, "intl_unit/l": 1},
        ref_low=8.0, ref_high=61.0,
    ),
    Biomarker(
        canonical_name="Anion Gap",
        canonical_unit="mEq/L",
        category="Metabolic",
        name_aliases=["anion gap", "ag"],
        unit_conversions={"meq/l": 1, "mmol/l": 1},
        ref_low=3.0, ref_high=11.0,
    ),

    # =========================================================================
    # Lipid Panel
    # =========================================================================
    Biomarker(
        canonical_name="Total Cholesterol",
        canonical_unit="mg/dL",
        category="Lipids",
        name_aliases=["total cholesterol", "cholesterol", "chol",
                      "cholesterol total", "t. chol", "t chol",
                      "cholesterol, total"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 38.67,
        },
        ref_low=None, ref_high=200.0,
    ),
    Biomarker(
        canonical_name="LDL Cholesterol",
        canonical_unit="mg/dL",
        category="Lipids",
        name_aliases=["ldl", "ldl cholesterol", "ldl-c", "low density lipoprotein",
                      "low-density lipoprotein", "ldl-chol", "ldl chol",
                      "ldl (calc)", "ldl calculated",
                      "ldl chol calc (nih)", "ldl-cholesterol",
                      "ldl chol (nih)"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 38.67,
        },
        ref_low=None, ref_high=100.0,
    ),
    Biomarker(
        canonical_name="HDL Cholesterol",
        canonical_unit="mg/dL",
        category="Lipids",
        name_aliases=["hdl", "hdl cholesterol", "hdl-c", "high density lipoprotein",
                      "high-density lipoprotein", "hdl-chol", "hdl chol"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 38.67,
        },
        ref_low=40.0, ref_high=None,
    ),
    Biomarker(
        canonical_name="Triglycerides",
        canonical_unit="mg/dL",
        category="Lipids",
        name_aliases=["triglycerides", "triglyceride", "trig", "trigs",
                      "tg", "triglycerides serum"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 88.57,
        },
        ref_low=None, ref_high=150.0,
    ),
    Biomarker(
        canonical_name="VLDL Cholesterol",
        canonical_unit="mg/dL",
        category="Lipids",
        name_aliases=["vldl", "vldl cholesterol", "very low density lipoprotein",
                      "vldl-c", "vldl chol",
                      "vldl cholesterol cal", "vldl calculation"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 38.67,
        },
        ref_low=None, ref_high=30.0,
    ),
    Biomarker(
        canonical_name="Non-HDL Cholesterol",
        canonical_unit="mg/dL",
        category="Lipids",
        name_aliases=["non-hdl cholesterol", "non hdl cholesterol",
                      "non-hdl chol", "non hdl chol", "nonhdl chol"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 38.67,
        },
        ref_low=None, ref_high=130.0,
    ),
    Biomarker(
        canonical_name="Cholesterol/HDL Ratio",
        canonical_unit="ratio",
        category="Lipids",
        name_aliases=["cholesterol/hdl ratio", "chol/hdl ratio", "chol/hdl",
                      "total chol/hdl", "cardiac risk ratio",
                      "chol/hdlc ratio", "risk ratio (chol/hdl)",
                      "coronary risk ratio"],
        unit_conversions={"ratio": 1, "": 1},
        ref_low=None, ref_high=5.0,
    ),

    # =========================================================================
    # Thyroid
    # =========================================================================
    Biomarker(
        canonical_name="TSH",
        canonical_unit="mIU/L",
        category="Thyroid",
        name_aliases=["tsh", "thyroid stimulating hormone", "thyrotropin",
                      "tsh, 3rd generation", "tsh reflex"],
        unit_conversions={
            "miu/l": 1, "µiu/ml": 1, "uiu/ml": 1, "miu/ml": 1,
        },
        ref_low=0.4, ref_high=4.0,
    ),
    Biomarker(
        canonical_name="Free T4",
        canonical_unit="ng/dL",
        category="Thyroid",
        name_aliases=["free t4", "ft4", "free thyroxine", "t4 free",
                      "thyroxine free", "t4, free", "t4,free(direct)",
                      "t4 free (direct)"],
        unit_conversions={
            "ng/dl": 1,
            "pmol/l": 0.07752,
        },
        ref_low=0.82, ref_high=1.77,
    ),
    Biomarker(
        canonical_name="T4 (Total)",
        canonical_unit="µg/dL",
        category="Thyroid",
        name_aliases=["t4", "thyroxine", "total t4", "t4 total",
                      "thyroxine total"],
        unit_conversions={
            "µg/dl": 1, "ug/dl": 1,
            "nmol/l": 0.07752,
        },
        ref_low=4.5, ref_high=12.5,
    ),
    Biomarker(
        canonical_name="Free T3",
        canonical_unit="pg/mL",
        category="Thyroid",
        name_aliases=["free t3", "ft3", "free triiodothyronine", "t3 free",
                      "t-3, free"],
        unit_conversions={
            "pg/ml": 1,
            "pmol/l": 0.6512,
        },
        ref_low=2.0, ref_high=4.4,
    ),
    Biomarker(
        canonical_name="T3 (Total)",
        canonical_unit="ng/dL",
        category="Thyroid",
        name_aliases=["t3", "triiodothyronine", "total t3", "t3 total"],
        unit_conversions={
            "ng/dl": 1,
            "nmol/l": 65.1,
        },
        ref_low=80.0, ref_high=200.0,
    ),
    Biomarker(
        canonical_name="Thyroid Peroxidase Ab",
        canonical_unit="IU/mL",
        category="Thyroid",
        name_aliases=["thyroid peroxidase (tpo) ab", "tpo antibodies", "tpo ab",
                      "anti-tpo", "thyroid peroxidase antibody"],
        unit_conversions={"iu/ml": 1, "u/ml": 1},
        ref_low=None, ref_high=34.0,
    ),
    Biomarker(
        canonical_name="Thyroglobulin",
        canonical_unit="ng/mL",
        category="Thyroid",
        name_aliases=["thyroglobulin", "thyroglobulin serum"],
        unit_conversions={"ng/ml": 1},
        ref_low=None, ref_high=None,
    ),
    Biomarker(
        canonical_name="Thyroglobulin Ab",
        canonical_unit="IU/mL",
        category="Thyroid",
        name_aliases=["thyroglobulin antibodies", "thyroglobulin antibody",
                      "anti-thyroglobulin"],
        unit_conversions={"iu/ml": 1},
        ref_low=None, ref_high=1.0,
    ),

    # =========================================================================
    # Vitamins & Minerals
    # =========================================================================
    Biomarker(
        canonical_name="Vitamin B12",
        canonical_unit="pg/mL",
        category="Vitamins",
        name_aliases=["vitamin b12", "vit b12", "b12", "cobalamin",
                      "cyanocobalamin", "vitamin b-12", "b-12"],
        unit_conversions={
            "pg/ml": 1, "ng/l": 1,
            "pmol/l": 1.355,
        },
        ref_low=200.0, ref_high=900.0,
    ),
    Biomarker(
        canonical_name="Vitamin D",
        canonical_unit="ng/mL",
        category="Vitamins",
        name_aliases=["vitamin d", "vit d", "vitamin d total",
                      "25-oh vitamin d", "25-hydroxyvitamin d",
                      "25 oh vitamin d", "25(oh)d",
                      "vitamin d, 25-hydroxy", "25-hydroxyvit. d",
                      "25 hydroxy vitamin d", "vitamin d-25 hydroxy",
                      "25-oh vit d",
                      "vitamin d,25-oh,total", "vitamin d,25-oh,total,ia",
                      "vitamin d,25-oh, d3", "vitamin d,25-oh, d2",
                      "vitamin d, 25-oh", "vitamin d (25-oh)"],
        unit_conversions={
            "ng/ml": 1,
            "nmol/l": 0.4006,
        },
        ref_low=30.0, ref_high=100.0,
    ),
    Biomarker(
        canonical_name="Folate",
        canonical_unit="ng/mL",
        category="Vitamins",
        name_aliases=["folate", "folic acid", "vitamin b9", "vit b9",
                      "folate serum", "folic acid serum",
                      "folate (folic acid), serum"],
        unit_conversions={
            "ng/ml": 1,
            "nmol/l": 0.4413,
        },
        ref_low=3.4, ref_high=None,
    ),
    Biomarker(
        canonical_name="Iron",
        canonical_unit="µg/dL",
        category="Iron Studies",
        name_aliases=["iron", "serum iron", "fe", "iron serum"],
        unit_conversions={
            "µg/dl": 1, "ug/dl": 1,
            "µmol/l": 5.585, "umol/l": 5.585,
        },
        ref_low=60.0, ref_high=170.0,
    ),
    Biomarker(
        canonical_name="TIBC",
        canonical_unit="µg/dL",
        category="Iron Studies",
        name_aliases=["tibc", "total iron binding capacity",
                      "iron binding capacity", "iron, total binding capacity"],
        unit_conversions={
            "µg/dl": 1, "ug/dl": 1,
            "µmol/l": 5.585, "umol/l": 5.585,
        },
        ref_low=250.0, ref_high=370.0,
    ),
    Biomarker(
        canonical_name="Transferrin Saturation",
        canonical_unit="%",
        category="Iron Studies",
        name_aliases=["transferrin saturation", "iron saturation",
                      "% saturation", "iron sat", "sat %"],
        unit_conversions={"%": 1},
        ref_low=20.0, ref_high=50.0,
    ),
    Biomarker(
        canonical_name="Ferritin",
        canonical_unit="ng/mL",
        category="Iron Studies",
        name_aliases=["ferritin", "serum ferritin", "ferritin serum"],
        unit_conversions={"ng/ml": 1, "µg/l": 1, "ug/l": 1},
        ref_low=12.0, ref_high=300.0,
    ),
    Biomarker(
        canonical_name="Magnesium",
        canonical_unit="mg/dL",
        category="Minerals",
        name_aliases=["magnesium", "mg", "magnesium serum"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 2.431, "meq/l": 1.215,
        },
        ref_low=1.7, ref_high=2.2,
    ),
    Biomarker(
        canonical_name="Phosphorus",
        canonical_unit="mg/dL",
        category="Minerals",
        name_aliases=["phosphorus", "phosphate", "phos", "phosphorus serum",
                      "inorganic phosphorus"],
        unit_conversions={
            "mg/dl": 1,
            "mmol/l": 3.097,
        },
        ref_low=2.5, ref_high=4.5,
    ),
    Biomarker(
        canonical_name="Zinc",
        canonical_unit="µg/dL",
        category="Minerals",
        name_aliases=["zinc", "serum zinc", "zinc serum"],
        unit_conversions={
            "µg/dl": 1, "ug/dl": 1,
            "µmol/l": 6.54, "umol/l": 6.54,
        },
        ref_low=60.0, ref_high=120.0,
    ),
    Biomarker(
        canonical_name="PTH",
        canonical_unit="pg/mL",
        category="Metabolic",
        name_aliases=["pth, intact", "parathyroid hormone", "intact pth", "pth"],
        unit_conversions={"pg/ml": 1, "pmol/l": 9.43},
        ref_low=15.0, ref_high=65.0,
    ),

    # =========================================================================
    # Diabetes / Metabolic
    # =========================================================================
    Biomarker(
        canonical_name="HbA1c",
        canonical_unit="%",
        category="Diabetes",
        name_aliases=["hba1c", "hemoglobin a1c", "haemoglobin a1c",
                      "a1c", "glycated hemoglobin", "glycosylated hemoglobin",
                      "hb a1c", "glycohemoglobin", "a1c hemoglobin",
                      "hgb a1c glycosylated"],
        unit_conversions={
            "%": 1,
            "mmol/mol": 0.09148,   # IFCC -> NGSP
        },
        ref_low=None, ref_high=5.7,
    ),
    Biomarker(
        canonical_name="Insulin",
        canonical_unit="µIU/mL",
        category="Diabetes",
        name_aliases=["insulin", "fasting insulin", "insulin fasting",
                      "insulin serum"],
        unit_conversions={
            "µiu/ml": 1, "uiu/ml": 1, "miu/l": 1,
            "pmol/l": 0.1440,
        },
        ref_low=2.6, ref_high=24.9,
    ),
    Biomarker(
        canonical_name="Mean Estimated Glucose",
        canonical_unit="mg/dL",
        category="Diabetes",
        name_aliases=["mean glucose est (calc)", "eag (mg/dl)",
                      "estimated average glucose"],
        unit_conversions={"mg/dl": 1},
        ref_low=None, ref_high=None,
    ),

    # =========================================================================
    # Inflammatory Markers
    # =========================================================================
    Biomarker(
        canonical_name="CRP",
        canonical_unit="mg/L",
        category="Inflammation",
        name_aliases=["crp", "c-reactive protein", "c reactive protein",
                      "crp quantitative"],
        unit_conversions={
            "mg/l": 1,
            "mg/dl": 10,
            "nmol/l": 0.1047,
        },
        ref_low=None, ref_high=10.0,
    ),
    Biomarker(
        canonical_name="hs-CRP",
        canonical_unit="mg/L",
        category="Inflammation",
        name_aliases=["hs-crp", "high sensitivity crp",
                      "high-sensitivity c-reactive protein", "hscrp",
                      "c-reactive protein, high sensitivity",
                      "crp, high sensitivity"],
        unit_conversions={
            "mg/l": 1,
            "mg/dl": 10,
        },
        ref_low=None, ref_high=3.0,
    ),
    Biomarker(
        canonical_name="ESR",
        canonical_unit="mm/hr",
        category="Inflammation",
        name_aliases=["esr", "erythrocyte sedimentation rate", "sed rate",
                      "sedimentation rate", "westergren esr"],
        unit_conversions={"mm/hr": 1, "mm/h": 1},
        ref_low=0.0, ref_high=20.0,
    ),
    Biomarker(
        canonical_name="Uric Acid",
        canonical_unit="mg/dL",
        category="Metabolic",
        name_aliases=["uric acid", "serum uric acid", "urate",
                      "uric acid serum"],
        unit_conversions={
            "mg/dl": 1,
            "µmol/l": 0.01681, "umol/l": 0.01681,
            "mmol/l": 16.81,
        },
        ref_low=3.5, ref_high=7.2,
    ),
    Biomarker(
        canonical_name="LDH",
        canonical_unit="U/L",
        category="Metabolic",
        name_aliases=["ld, serum", "ldh", "lactate dehydrogenase"],
        unit_conversions={"u/l": 1, "iu/l": 1},
        ref_low=122.0, ref_high=222.0,
    ),

    # =========================================================================
    # Hormones
    # =========================================================================
    Biomarker(
        canonical_name="Testosterone",
        canonical_unit="ng/dL",
        category="Hormones",
        name_aliases=["testosterone", "total testosterone", "serum testosterone",
                      "testosterone total", "testosterone serum"],
        unit_conversions={
            "ng/dl": 1,
            "nmol/l": 28.84,
            "pg/ml": 0.1,
        },
        ref_low=264.0, ref_high=916.0,
    ),
    Biomarker(
        canonical_name="Free Testosterone",
        canonical_unit="pg/mL",
        category="Hormones",
        name_aliases=["free testosterone", "testosterone free",
                      "testosterone, free"],
        unit_conversions={
            "pg/ml": 1,
            "pmol/l": 0.2887,
            "ng/dl": 10,
        },
        ref_low=9.3, ref_high=26.5,
    ),
    Biomarker(
        canonical_name="DHEA-S",
        canonical_unit="µg/dL",
        category="Hormones",
        name_aliases=["dhea", "dhea-s", "dhea sulfate",
                      "dehydroepiandrosterone sulfate", "dheas"],
        unit_conversions={
            "µg/dl": 1, "ug/dl": 1,
            "µmol/l": 36.86, "umol/l": 36.86,
        },
        ref_low=61.0, ref_high=695.0,
    ),
    Biomarker(
        canonical_name="Cortisol",
        canonical_unit="µg/dL",
        category="Hormones",
        name_aliases=["cortisol", "serum cortisol", "cortisol am",
                      "cortisol morning"],
        unit_conversions={
            "µg/dl": 1, "ug/dl": 1,
            "nmol/l": 0.03625,
        },
        ref_low=6.2, ref_high=19.4,
    ),
    Biomarker(
        canonical_name="PSA",
        canonical_unit="ng/mL",
        category="Hormones",
        name_aliases=["psa", "prostate specific antigen",
                      "prostate-specific antigen", "psa total"],
        unit_conversions={"ng/ml": 1},
        ref_low=None, ref_high=4.0,
    ),

    # =========================================================================
    # Vitals
    # =========================================================================
    Biomarker(
        canonical_name="Oxygen Saturation",
        canonical_unit="%",
        category="Vitals",
        name_aliases=["oxygen saturation", "o2 sat", "spo2", "pulse ox"],
        unit_conversions={"%": 1},
        ref_low=95.0, ref_high=100.0,
    ),

    # =========================================================================
    # Urinalysis
    # =========================================================================
    Biomarker(
        canonical_name="Urine pH",
        canonical_unit="pH",
        category="Urinalysis",
        name_aliases=["urine ph", "ph urine", "ph"],
        unit_conversions={"ph": 1, "": 1},
        ref_low=4.5, ref_high=8.0,
    ),
    Biomarker(
        canonical_name="Urine Specific Gravity",
        canonical_unit="ratio",
        category="Urinalysis",
        name_aliases=["specific gravity", "urine specific gravity",
                      "sp gravity", "sp gr", "s.g."],
        unit_conversions={"ratio": 1, "": 1},
        ref_low=1.005, ref_high=1.030,
    ),
    Biomarker(
        canonical_name="Urine Leukocyte Esterase",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["leukocyte esterase", "wbc esterase",
                      "urine leukocyte esterase"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Blood",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["urine blood", "blood", "occult blood"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Nitrite",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["urine nitrite", "nitrite, urine", "nitrite"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Microalbumin",
        canonical_unit="mg/L",
        category="Urinalysis",
        name_aliases=["microalbumin", "urine microalbumin",
                      "albumin urine", "microalbumin urine"],
        unit_conversions={"mg/l": 1, "µg/ml": 1, "mg/dl": 10},
        ref_low=None, ref_high=30.0,
    ),
    Biomarker(
        canonical_name="Urine Color",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["urine-color", "color", "urine color"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Appearance",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["appearance", "urine appearance"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Urobilinogen",
        canonical_unit="mg/dL",
        category="Urinalysis",
        name_aliases=["urobilinogen", "urobilinogen,semi-qn",
                      "urobilinogen semi-qn"],
        unit_conversions={"mg/dl": 1, "eu/dl": 1},
        ref_low=0.1, ref_high=1.0,
    ),
    Biomarker(
        canonical_name="Urine Ketones",
        canonical_unit="mg/dL",
        category="Urinalysis",
        name_aliases=["ketones", "urine ketones", "ketone bodies", "acetone"],
        unit_conversions={"mg/dl": 1},
        ref_low=None, ref_high=None,
    ),
    Biomarker(
        canonical_name="Urine Bilirubin",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["urine bilirubin", "bilirubin urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Mucus",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["mucus", "urine mucus"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Bacteria",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["bacteria", "urine bacteria"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Epithelial Cells",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["epithelial cells (non renal)", "epithelial cells",
                      "urine epithelial cells"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Urine Casts",
        canonical_unit="",
        category="Urinalysis",
        name_aliases=["casts", "urine casts"],
        unit_conversions={"": 1},
    ),

    # =========================================================================
    # Infectious Disease
    # =========================================================================
    Biomarker(
        canonical_name="HIV Screen",
        canonical_unit="",
        category="Infectious Disease",
        name_aliases=["hiv ab/p24 ag screen", "hiv screen", "hiv"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Hepatitis C Ab",
        canonical_unit="",
        category="Infectious Disease",
        name_aliases=["hcv ab", "hepatitis c antibody"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Hepatitis B Surface Ag",
        canonical_unit="",
        category="Infectious Disease",
        name_aliases=["hbsag screen", "hepatitis b surface antigen"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="RPR",
        canonical_unit="",
        category="Infectious Disease",
        name_aliases=["rpr", "rapid plasma reagin"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="SARS-CoV-2 NAA",
        canonical_unit="",
        category="Infectious Disease",
        name_aliases=["sars-cov-2, naa", "covid-19 pcr", "sars-cov-2 naa"],
        unit_conversions={"": 1},
    ),

    # =========================================================================
    # Drug Screen
    # =========================================================================
    Biomarker(
        canonical_name="Drug Screen Amphetamines",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["amphetamines, urine", "amphetamine screen, urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Cannabinoids",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["cannabinoid", "cannabinoids, urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Opiates",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["opiates", "opiates, urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Cocaine",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["cocaine (metab.)", "cocaine metabolite"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Benzodiazepines",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["benzodiazepines", "benzodiazepines, urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Barbiturates",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["barbiturate", "barbiturates, urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Methadone",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["methadone screen, urine", "methadone, urine"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen PCP",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["phencyclidine", "pcp, urine", "drug screen pcp",
                      "pcp (phencyclidine)", "pcp"],
        unit_conversions={"": 1},
    ),
    Biomarker(
        canonical_name="Drug Screen Propoxyphene",
        canonical_unit="",
        category="Drug Screen",
        name_aliases=["propoxyphene, urine"],
        unit_conversions={"": 1},
    ),

    # =========================================================================
    # Pulmonary
    # =========================================================================
    Biomarker(
        canonical_name="FEV1",
        canonical_unit="L",
        category="Pulmonary",
        name_aliases=["fev1", "forced expiratory volume 1s"],
        unit_conversions={"l": 1},
    ),
    Biomarker(
        canonical_name="FEV6",
        canonical_unit="L",
        category="Pulmonary",
        name_aliases=["fev6"],
        unit_conversions={"l": 1},
    ),
    Biomarker(
        canonical_name="FEV1/FEV6",
        canonical_unit="%",
        category="Pulmonary",
        name_aliases=["fev1/fev6"],
        unit_conversions={"%": 1},
    ),
    Biomarker(
        canonical_name="PEF",
        canonical_unit="L/min",
        category="Pulmonary",
        name_aliases=["pef", "peak expiratory flow"],
        unit_conversions={"l/min": 1},
    ),
]


# =========================================================================
# Lookup helpers
# =========================================================================

_NOISE = re.compile(
    r",?\s*\b(calculated|calc|serum|blood|level|levels)\b\s*",
    re.IGNORECASE,
)


def _build_name_index() -> dict[str, Biomarker]:
    idx = {}
    for bm in REGISTRY:
        for alias in bm.name_aliases:
            key = _NOISE.sub(" ", alias).lower()
            key = re.sub(r"\s+", " ", key).strip().strip(",").strip()
            idx[key] = bm
    return idx

def _build_unit_index() -> dict[str, dict[str, float]]:
    """canonical_name -> {raw_unit_lower -> multiplier}"""
    return {bm.canonical_name: bm.unit_conversions for bm in REGISTRY}

_NAME_INDEX = _build_name_index()
_UNIT_INDEX  = _build_unit_index()


def normalize_name(raw: str) -> str:
    """Return canonical name, or title-cased original if unknown."""
    key = _NOISE.sub(" ", raw).lower()
    key = re.sub(r"\s+", " ", key).strip().strip(",").strip()
    bm = _NAME_INDEX.get(key)
    return bm.canonical_name if bm else raw.strip().title()


def normalize_unit(canonical_name: str, raw_unit: str, raw_value: float | None) -> tuple[str, float | None]:
    """
    Given a canonical biomarker name + raw unit + raw value,
    return (canonical_unit, converted_value).
    If unit is unknown, returns (raw_unit, raw_value) with no conversion.
    """
    bm_map = _UNIT_INDEX.get(canonical_name)
    if bm_map is None or raw_value is None:
        return raw_unit, raw_value

    key = raw_unit.lower().strip() if raw_unit else ""
    multiplier = bm_map.get(key)
    if multiplier is None:
        return raw_unit, raw_value   # unknown unit — store as-is

    # Find the canonical unit for this biomarker
    bm = next((b for b in REGISTRY if b.canonical_name == canonical_name), None)
    canonical_unit = bm.canonical_unit if bm else raw_unit
    return canonical_unit, round(raw_value * multiplier, 6)


def get_fallback_refs(canonical_name: str) -> tuple[float | None, float | None]:
    """Return (ref_low, ref_high) from registry as fallback if PDF didn't include them."""
    bm = next((b for b in REGISTRY if b.canonical_name == canonical_name), None)
    return (bm.ref_low, bm.ref_high) if bm else (None, None)
