export interface BiomarkerInfo {
  summary: string;
  goodRange: string;
  howToImprove: string;
}

const INFO: Record<string, BiomarkerInfo> = {
  // ── Lipids ────────────────────────────────────────────────────────────────
  "Total Cholesterol": {
    summary: "Total cholesterol is the aggregate of all cholesterol particles in your blood — LDL, HDL, VLDL, and IDL. Alone it is a blunt tool; its value lies in context with the sub-fractions, since a high number driven by large HDL particles is very different from one driven by small dense LDL.",
    goodRange: "Below 200 mg/dL is considered desirable. 200–239 is borderline high; 240+ is high. For individuals with established cardiovascular disease the target is often below 150–170 mg/dL.",
    howToImprove: "Reduce saturated and trans fats; increase soluble fibre (oats, legumes, psyllium); exercise ≥150 min/week of moderate aerobic activity; maintain healthy weight. Statins are the most evidence-backed pharmacological option when lifestyle changes are insufficient.",
  },
  "LDL Cholesterol": {
    summary: "LDL ('bad') cholesterol carries cholesterol from the liver to cells. When oxidised, small dense LDL particles embed in arterial walls and drive atherosclerosis. It is the primary pharmacological target for cardiovascular risk reduction.",
    goodRange: "Optimal: <100 mg/dL. Near-optimal: 100–129. For high-risk individuals (diabetes, prior heart attack, strong family history) many guidelines now target <70 mg/dL.",
    howToImprove: "Dietary changes (replace saturated fat with unsaturated fat, add plant sterols) can lower LDL by 10–20%. Statins reduce LDL by 30–50%. PCSK9 inhibitors achieve 50–70% reduction and are options when statins are insufficient or not tolerated.",
  },
  "HDL Cholesterol": {
    summary: "HDL ('good') cholesterol scavenges excess cholesterol from the arteries and returns it to the liver for excretion — a process called reverse cholesterol transport. Higher HDL is associated with lower cardiovascular risk, though very high levels (>80) carry diminishing returns.",
    goodRange: "For men: ≥40 mg/dL is normal; ≥60 mg/dL is protective. Below 40 is a cardiovascular risk factor. Target ≥50 mg/dL for optimal cardioprotection.",
    howToImprove: "Regular aerobic exercise is the single strongest lifestyle lever — it can raise HDL by 5–10%. Smoking cessation, moderate alcohol (1 drink/day), replacing refined carbs with healthy fats, and niacin (under medical supervision) also help.",
  },
  "Triglycerides": {
    summary: "Triglycerides are the main form of stored fat in the body. Elevated levels reflect excess dietary calories (especially from refined carbohydrates and alcohol), insulin resistance, and poor metabolic health. Very high triglycerides (>500 mg/dL) carry a risk of pancreatitis.",
    goodRange: "Normal: <150 mg/dL. Borderline high: 150–199. High: 200–499. Very high: ≥500 mg/dL. Many cardiologists now prefer <100 mg/dL as optimal.",
    howToImprove: "Reduce sugar and refined carbohydrates — this is more effective than fat reduction. Cut alcohol. Increase omega-3 fatty acids (fatty fish, fish oil ≥2 g EPA+DHA/day). Lose weight. Fibrates or high-dose omega-3 prescriptions (Vascepa) are medication options.",
  },
  "VLDL Cholesterol": {
    summary: "VLDL (very low-density lipoprotein) is the liver-produced carrier of triglycerides to peripheral tissues. Elevated VLDL contributes directly to triglyceride burden and is usually calculated as triglycerides ÷ 5. It is a marker of carbohydrate and metabolic dysregulation.",
    goodRange: "Normal: 2–30 mg/dL. Levels above 30 mg/dL reflect elevated triglycerides and indicate metabolic risk.",
    howToImprove: "VLDL mirrors triglycerides — the same interventions apply: reduce sugar and alcohol, increase omega-3s, exercise regularly, and achieve a healthy weight.",
  },
  "Non-HDL Cholesterol": {
    summary: "Non-HDL cholesterol is total cholesterol minus HDL — it captures all atherogenic (artery-clogging) particles including LDL, VLDL, IDL, and Lp(a). It is considered a better predictor of cardiovascular risk than LDL alone because it doesn't require fasting and accounts for triglyceride-rich particles.",
    goodRange: "Optimal: <130 mg/dL. <160 mg/dL is acceptable for average-risk individuals. High-risk individuals should target <100 mg/dL.",
    howToImprove: "The same strategies that lower LDL and triglycerides apply here. Non-HDL responds well to statins, fibrates, omega-3s, and dietary changes.",
  },

  // ── CBC ───────────────────────────────────────────────────────────────────
  "WBC": {
    summary: "White blood cell count is your immune system's army count. An elevated WBC (leukocytosis) can signal infection, inflammation, or rarely a blood disorder. A low WBC (leukopenia) indicates immune suppression, often from viral illness, medications, or bone marrow issues.",
    goodRange: "4.5–11.0 × 10³/µL is the standard reference range. Values above 11 warrant investigation for infection or inflammatory cause; values below 4 should be evaluated for immune compromise.",
    howToImprove: "WBC itself is not a target — it reflects underlying conditions. Treating infections, managing autoimmune disease, avoiding unnecessary medications that suppress marrow, and optimising nutrition (zinc, vitamin C, vitamin D) support a healthy immune baseline.",
  },
  "RBC": {
    summary: "Red blood cell count reflects how many oxygen-carrying erythrocytes are circulating. Low counts (anaemia) cause fatigue, breathlessness, and poor exercise tolerance. Elevated counts (polycythaemia) increase blood viscosity and clot risk.",
    goodRange: "Men: 4.5–5.9 × 10⁶/µL. Women: 4.0–5.2 × 10⁶/µL.",
    howToImprove: "For iron-deficiency anaemia: optimise dietary iron (red meat, lentils, spinach) with vitamin C to enhance absorption, or supplement under guidance. Adequate B12 and folate are essential. For polycythaemia, investigate secondary causes (sleep apnoea, smoking, excess EPO).",
  },
  "Hemoglobin": {
    summary: "Haemoglobin is the iron-containing protein inside red blood cells that binds and transports oxygen. It is the most clinically important anaemia marker — symptoms of fatigue, pallor, and shortness of breath directly correlate with how low it falls.",
    goodRange: "Men: 13.5–17.5 g/dL. Women: 12.0–15.5 g/dL. Below 13 (men) or 12 (women) meets criteria for anaemia; below 8 g/dL is severe and often requires intervention.",
    howToImprove: "Identify the cause — iron deficiency, B12/folate deficiency, or chronic disease are the most common. Iron supplementation raises haemoglobin by ~1 g/dL per month. B12 injections or high-dose oral B12 are used for deficiency-related anaemia. Erythropoiesis-stimulating agents are reserved for chronic kidney disease anaemia.",
  },
  "Hematocrit": {
    summary: "Haematocrit (HCT) is the percentage of blood volume occupied by red blood cells. It closely tracks haemoglobin and is used to classify anaemia severity and monitor hydration status — dehydration raises it artificially.",
    goodRange: "Men: 41–53%. Women: 36–46%. Below 36% in men or 33% in women indicates anaemia.",
    howToImprove: "Mirrors haemoglobin interventions: treat the underlying cause (iron, B12, chronic disease). Maintain adequate hydration for accurate readings.",
  },
  "MCV": {
    summary: "Mean corpuscular volume measures the average size of red blood cells. Small cells (microcytosis) suggest iron deficiency or thalassaemia. Large cells (macrocytosis) point to B12 or folate deficiency, alcohol excess, or hypothyroidism. Normal MCV with anaemia points to chronic disease or acute blood loss.",
    goodRange: "80–100 fL (femtoliters). Below 80 is microcytic; above 100 is macrocytic.",
    howToImprove: "Treat the deficiency driving the size abnormality. Iron supplementation corrects microcytosis; B12 or folate supplementation corrects macrocytosis. Re-check in 3 months to confirm response.",
  },
  "Platelets": {
    summary: "Platelets are tiny cell fragments critical for blood clotting. Too few (thrombocytopenia) leads to easy bruising and bleeding risk; too many (thrombocytosis) can increase clot risk. They are consumed in infections and autoimmune conditions, and suppressed by many medications.",
    goodRange: "150–400 × 10³/µL is normal. Below 100 requires investigation; below 50 is clinically significant for bleeding risk.",
    howToImprove: "Low platelets require identifying the cause — medication review, viral illness, or autoimmune workup. High platelets often reflect iron deficiency or inflammation; treating the underlying condition normalises them.",
  },
  "Neutrophils": {
    summary: "Neutrophils are the first-responder white cells that attack bacterial and fungal infections. Elevated levels indicate acute infection or inflammation. Low levels (neutropenia) significantly impair the body's ability to fight bacterial infections.",
    goodRange: "1.8–7.7 × 10³/µL (or 45–75% of WBC). Below 1.5 is mild neutropenia; below 0.5 is severe.",
    howToImprove: "Neutrophilia typically resolves when the underlying infection or stressor is treated. Neutropenia warrants review of medications and may require haematology input.",
  },
  "Lymphocytes": {
    summary: "Lymphocytes (T cells, B cells, NK cells) are the adaptive immune system's specialists, targeting viruses and producing antibodies. Elevated levels often indicate viral infections; persistently high lymphocytes can indicate lymphoma. Low lymphocytes are seen post-steroid therapy and in HIV.",
    goodRange: "1.0–4.8 × 10³/µL (or 20–40% of WBC).",
    howToImprove: "Transient changes are normal with viral illness. Persistent abnormalities require further immunological investigation.",
  },
  "Monocytes": {
    summary: "Monocytes are immune cells that migrate into tissues and become macrophages, phagocytosing debris and coordinating inflammation. Mildly elevated monocytes are a common non-specific finding in chronic inflammation, viral illness, and autoimmune disease.",
    goodRange: "0.2–1.0 × 10³/µL (or 2–10% of WBC).",
    howToImprove: "Address chronic inflammation drivers: optimise sleep, reduce processed food intake, manage stress, and treat any underlying autoimmune or infectious conditions.",
  },
  "Eosinophils": {
    summary: "Eosinophils fight parasitic infections and mediate allergic responses. Elevated counts (eosinophilia) most commonly reflect allergic disease (asthma, eczema, hay fever) or, in travellers, parasitic infection. Extreme eosinophilia can damage the heart and nervous system.",
    goodRange: "0.05–0.5 × 10³/µL (or 1–4% of WBC). Above 0.5 is eosinophilia; above 1.5 is hypereosinophilia.",
    howToImprove: "Manage allergic triggers (antihistamines, inhaled corticosteroids for asthma). Rule out parasitic infection if there is travel history. Avoid medications known to cause drug-induced eosinophilia.",
  },
  "Basophils": {
    summary: "Basophils are the rarest circulating white cells, involved in allergic and inflammatory responses by releasing histamine and heparin. They are rarely the sole abnormality of clinical significance but elevated basophils can be seen in hypothyroidism and myeloproliferative disorders.",
    goodRange: "0.01–0.1 × 10³/µL (or 0–1% of WBC).",
    howToImprove: "Isolated mild basophilia is rarely actionable. Persistently elevated levels warrant thyroid and haematological evaluation.",
  },

  // ── Metabolic Panel ───────────────────────────────────────────────────────
  "Glucose": {
    summary: "Fasting blood glucose measures the amount of sugar in your blood after an overnight fast. It is the primary diagnostic test for diabetes and prediabetes and reflects your body's ability to regulate insulin and maintain metabolic homeostasis.",
    goodRange: "Normal fasting: 70–99 mg/dL. Prediabetes: 100–125 mg/dL. Diabetes: ≥126 mg/dL on two occasions.",
    howToImprove: "Reduce refined carbohydrates and added sugars. Time-restricted eating and low-glycaemic diets improve fasting glucose significantly. Regular exercise — particularly resistance training — improves insulin sensitivity. Metformin is the first-line medication for prediabetes/type 2 diabetes.",
  },
  "HbA1c": {
    summary: "Haemoglobin A1c (glycated haemoglobin) reflects your average blood glucose over the preceding 2–3 months. It is the gold standard for diabetes diagnosis and monitoring — more reliable than a single fasting glucose because it cannot be gamed by one day of careful eating.",
    goodRange: "Normal: <5.7%. Prediabetes: 5.7–6.4%. Diabetes: ≥6.5%. Well-controlled diabetes target: <7%. Below 5.4% is optimal for longevity.",
    howToImprove: "Every 1% reduction in HbA1c reduces diabetes complications by 20–40%. Dietary carbohydrate restriction, weight loss of even 5–10%, aerobic and resistance exercise, and medications (metformin, GLP-1 agonists, SGLT2 inhibitors) all lower HbA1c effectively.",
  },
  "Creatinine": {
    summary: "Creatinine is a waste product of muscle metabolism filtered almost entirely by the kidneys. Elevated creatinine signals reduced kidney filtration function. Levels are affected by muscle mass — athletes and muscular individuals naturally run higher.",
    goodRange: "Men: 0.74–1.35 mg/dL. Women: 0.59–1.04 mg/dL. Values should always be interpreted alongside eGFR for clinical context.",
    howToImprove: "Stay well-hydrated. Control blood pressure (the leading cause of kidney damage). Manage blood sugar in diabetes. Avoid nephrotoxic medications and NSAIDs. A low-protein diet modestly reduces creatinine in CKD.",
  },
  "eGFR": {
    summary: "Estimated glomerular filtration rate quantifies how well your kidneys are filtering blood per minute. It is calculated from creatinine, age, and sex. eGFR is the most sensitive ongoing marker of kidney health — it declines years before creatinine visibly rises.",
    goodRange: "≥60 mL/min/1.73m² is normal. 45–59 is mildly-to-moderately reduced (CKD Stage 3a). Below 30 is severe. Below 15 indicates kidney failure.",
    howToImprove: "Control blood pressure rigorously (target <130/80). Optimise blood sugar in diabetes. ACE inhibitors or ARBs are renoprotective medications. Limit NSAID use, stay hydrated, and avoid dietary protein excess.",
  },
  "BUN": {
    summary: "Blood urea nitrogen is a byproduct of protein metabolism excreted by the kidneys. Elevated BUN can indicate kidney dysfunction, dehydration, or high protein intake. A low BUN may reflect malnutrition or liver disease.",
    goodRange: "7–25 mg/dL. The BUN-to-creatinine ratio (normal 10–20) helps differentiate pre-renal (dehydration) from intrinsic kidney disease.",
    howToImprove: "Maintain adequate hydration. If chronically elevated with normal creatinine, reduce dietary protein intake. Treat underlying kidney disease.",
  },
  "Sodium": {
    summary: "Sodium is the primary electrolyte governing fluid balance and nerve/muscle function. Low sodium (hyponatraemia) causes confusion and seizures in severe cases; high sodium (hypernatraemia) indicates dehydration or hormonal dysregulation.",
    goodRange: "136–145 mEq/L. Values outside this range usually reflect fluid imbalance rather than dietary sodium directly.",
    howToImprove: "Sodium levels are tightly regulated by the kidneys and hormones — they are rarely corrected by dietary changes alone. Treatment targets the underlying fluid/hormonal cause.",
  },
  "Potassium": {
    summary: "Potassium is critical for heart rhythm and muscle function. Low potassium (hypokalaemia) — often from diuretics, poor intake, or GI losses — can cause arrhythmias and muscle weakness. High potassium (hyperkalaemia) is dangerous in kidney disease.",
    goodRange: "3.5–5.1 mEq/L. Below 3.0 and above 5.5 require prompt attention due to cardiac risk.",
    howToImprove: "Increase dietary potassium (bananas, avocados, leafy greens, legumes) for deficiency. Review diuretic medications. For hyperkalaemia in kidney disease, reduce high-potassium foods and medications that raise potassium (ACE inhibitors, NSAIDs).",
  },
  "ALT": {
    summary: "Alanine aminotransferase (ALT) is an enzyme found predominantly in the liver. It is released into the blood when liver cells are damaged. It is the most specific marker of hepatocellular injury — elevated ALT points to fatty liver, hepatitis, alcohol use, or medication toxicity.",
    goodRange: "Men: <40–56 U/L (lab-dependent). Women: <35 U/L. Levels above 3× the upper limit warrant investigation. Some experts argue the true healthy range is <30 (men) and <19 (women).",
    howToImprove: "Eliminate or reduce alcohol. Achieve a healthy weight — NAFLD (fatty liver) is the most common cause of elevated ALT in non-drinkers and reverses with 7–10% weight loss. Review all supplements and medications for hepatotoxicity. Coffee consumption (3–4 cups/day) is consistently associated with lower liver enzyme levels.",
  },
  "AST": {
    summary: "Aspartate aminotransferase is found in the liver, heart, and muscle. It is less liver-specific than ALT — elevated AST can also reflect muscle damage (from intense exercise) or heart injury. The AST:ALT ratio is diagnostically useful; a ratio >2:1 suggests alcoholic liver disease.",
    goodRange: "10–40 U/L. Interpret alongside ALT and the AST/ALT ratio for best clinical context.",
    howToImprove: "Same approaches as ALT: reduce alcohol, lose weight if overweight, review medications. Differentiate exercise-related elevation (expected in athletes) from true hepatocellular injury.",
  },
  "Alkaline Phosphatase": {
    summary: "Alkaline phosphatase (ALP) is produced by the liver, bile ducts, and bone. Elevated levels may reflect bile duct obstruction, bone disease (fractures, Paget's disease), or liver disease. It is a useful screen for biliary pathology when elevated disproportionately to other liver enzymes.",
    goodRange: "44–147 U/L (adults). Levels are physiologically elevated in growing children and pregnancy.",
    howToImprove: "Treat the underlying cause — bile duct obstruction requires imaging and potentially intervention. Bone-derived elevation warrants DEXA scan and vitamin D/calcium optimisation.",
  },
  "Albumin": {
    summary: "Albumin is the main protein synthesised by the liver and serves as a carrier for hormones, drugs, and fatty acids. It is also the major determinant of oncotic pressure (keeping fluid in blood vessels). Low albumin reflects chronic liver disease, malnutrition, or severe illness.",
    goodRange: "3.4–5.4 g/dL. Below 3.4 suggests significant protein deficiency or hepatic dysfunction.",
    howToImprove: "Ensure adequate protein intake (0.8–1.2 g/kg body weight). Treat underlying liver disease. Address malabsorption or inflammatory conditions that increase protein catabolism.",
  },
  "Total Protein": {
    summary: "Total protein measures both albumin and globulins in the blood. A low total protein indicates malnutrition or liver/kidney disease. A high level with elevated globulins warrants investigation for multiple myeloma or chronic inflammatory states.",
    goodRange: "6.3–8.2 g/dL.",
    howToImprove: "Ensure adequate dietary protein, particularly in older adults who are at risk of sarcopenia. Investigate elevated globulin fractions with serum protein electrophoresis if total protein is persistently high.",
  },
  "Calcium": {
    summary: "Calcium in the blood (ionised and protein-bound) is tightly regulated by parathyroid hormone and vitamin D. Elevated calcium (hypercalcaemia) is most commonly caused by primary hyperparathyroidism or malignancy. Low calcium (hypocalcaemia) can cause muscle cramps and in severe cases cardiac arrhythmias.",
    goodRange: "8.5–10.5 mg/dL. Corrected for albumin level (add 0.8 mg/dL for every 1 g/dL albumin below 4.0).",
    howToImprove: "Hypercalcaemia: requires PTH and vitamin D metabolite testing to identify cause. Hypocalcaemia: supplement calcium and vitamin D; check magnesium levels (low Mg impairs PTH response).",
  },

  // ── Thyroid ───────────────────────────────────────────────────────────────
  "TSH": {
    summary: "Thyroid-stimulating hormone (TSH) is produced by the pituitary and is the master regulator of thyroid function. It is the most sensitive thyroid test — it rises when the thyroid is underactive (hypothyroidism) and falls when it is overactive (hyperthyroidism). After thyroidectomy, TSH is closely managed to balance suppression (to reduce cancer recurrence risk) against avoiding overt hyperthyroidism.",
    goodRange: "General population: 0.4–4.0 mIU/L. For post-thyroidectomy thyroid cancer patients, target is typically 0.1–0.5 mIU/L (mild suppression) or even lower in high-risk cases, per oncology guidance.",
    howToImprove: "Post-thyroidectomy, TSH is managed entirely through levothyroxine dose titration. There is no lifestyle intervention that replaces this. Selenium adequacy may support residual thyroid tissue. Annual monitoring of TSH alongside Free T4 is standard.",
  },
  "Free T4": {
    summary: "Free T4 (thyroxine) is the predominant hormone produced by the thyroid gland. It is the inactive precursor that tissues convert to the active T3. After thyroidectomy, all T4 comes from levothyroxine replacement — Free T4 confirms adequate dosing and avoids over- or under-replacement.",
    goodRange: "0.8–1.8 ng/dL. Post-thyroidectomy targets vary by cancer risk tier but typically aim for the upper half of normal or slightly above (1.2–1.8 ng/dL) when mild TSH suppression is intended.",
    howToImprove: "Adjust levothyroxine dose under endocrinologist guidance. Take on an empty stomach 30–60 minutes before food. Avoid calcium, iron, or antacids within 4 hours. Consistent timing improves stability.",
  },
  "Free T3": {
    summary: "Free T3 (triiodothyronine) is the biologically active thyroid hormone that enters cells and drives metabolism. While T4 is the storage form, T3 binds thyroid receptors directly. Post-thyroidectomy, some patients have suboptimal T3 levels even with adequate T4, leading to persistent fatigue and brain fog — a combination T4/T3 approach is debated.",
    goodRange: "2.3–4.2 pg/mL (or 230–420 pg/dL depending on lab units). Optimal symptom relief is often associated with levels in the upper-third of the range.",
    howToImprove: "In cases where T3 remains suboptimal on levothyroxine alone, combination therapy (T4 + T3 or desiccated thyroid extract) may be considered with an endocrinologist. Selenium supplementation supports T4-to-T3 conversion in the peripheral tissues.",
  },
  "Thyroglobulin": {
    summary: "Thyroglobulin (Tg) is a protein produced exclusively by thyroid tissue. After total thyroidectomy for papillary thyroid cancer (PTC), thyroglobulin should be undetectable — any measurable level suggests residual thyroid tissue or recurrence. It is the primary tumour marker for PTC surveillance.",
    goodRange: "Post-total thyroidectomy with radioiodine ablation: undetectable (<0.1–0.2 ng/mL). Even stimulated Tg (after TSH stimulation or THW) should be <1–2 ng/mL for low-risk patients. Rising Tg is the key signal for recurrence.",
    howToImprove: "Thyroglobulin itself is not modifiable — it reflects residual or recurrent thyroid tissue. Management decisions (observation, re-ablation, further surgery) are made by the treating endocrinologist and oncologist based on Tg trajectory and imaging.",
  },
  "Thyroglobulin Antibodies": {
    summary: "Anti-thyroglobulin antibodies (TgAb) are produced by the immune system against thyroglobulin. Their presence interferes with Tg assays — making Tg appear falsely low — and thus TgAb must always be measured alongside Tg in thyroid cancer surveillance. Elevated TgAb are also seen in Hashimoto's thyroiditis.",
    goodRange: "<4 IU/mL (or <1.0 IU/mL depending on lab). The key clinical point is the trend — rising TgAb in a post-thyroidectomy patient is treated with the same suspicion as rising Tg.",
    howToImprove: "TgAb levels are not directly modifiable. For autoimmune thyroid disease, selenium supplementation (200 µg/day) has been shown in multiple trials to reduce TgAb levels over 6–12 months.",
  },

  // ── Other markers ─────────────────────────────────────────────────────────
  "Vitamin D": {
    summary: "Vitamin D (25-hydroxyvitamin D) is a fat-soluble prohormone that regulates calcium metabolism, immune function, and gene expression in virtually every tissue. Deficiency is exceptionally common, linked to fatigue, bone loss, immune dysfunction, depression, and increased cardiovascular risk.",
    goodRange: "Deficiency: <20 ng/mL. Insufficiency: 20–29 ng/mL. Sufficient: 30–50 ng/mL. Optimal: many functional medicine practitioners target 40–60 ng/mL. Toxicity risk above 100 ng/mL.",
    howToImprove: "Sun exposure (15–30 min midday on arms and legs, 3–4×/week) raises vitamin D but is insufficient at high latitudes in winter. Supplement vitamin D3 (cholecalciferol) — 2000–4000 IU/day is safe for most adults. Take with a meal containing fat for best absorption. Recheck levels in 3 months.",
  },
  "Vitamin B12": {
    summary: "Vitamin B12 is essential for DNA synthesis, red blood cell formation, and neurological function. Deficiency causes macrocytic anaemia, peripheral neuropathy, and cognitive decline — neurological damage can be irreversible if untreated. It is especially common in vegans, older adults, and those on metformin or proton pump inhibitors.",
    goodRange: "190–950 pg/mL. Below 300 pg/mL often causes subclinical symptoms even if technically 'normal'. Many clinicians target >400 pg/mL for optimal neurological function.",
    howToImprove: "Animal products are the primary dietary source. Vegans require B12 supplementation — 1000 mcg oral cyanocobalamin daily is effective even without intrinsic factor due to passive absorption. For confirmed deficiency with neurological symptoms, intramuscular injections are preferred for faster repletion.",
  },
  "Iron": {
    summary: "Serum iron measures the concentration of iron bound to transferrin in the blood. It varies significantly throughout the day and with recent meals — it is always interpreted alongside ferritin and transferrin saturation. Low serum iron with low ferritin confirms iron deficiency.",
    goodRange: "Men: 60–170 µg/dL. Women: 50–170 µg/dL. Transferrin saturation <20% suggests iron deficiency; >45% suggests iron overload.",
    howToImprove: "Increase haem iron (red meat, organ meat) or non-haem iron (lentils, beans, spinach, fortified cereals) paired with vitamin C. Avoid calcium, tea, or coffee within 1 hour of iron-rich meals. For symptomatic deficiency, iron supplements (ferrous sulphate 325 mg every other day) are effective and better tolerated than daily dosing.",
  },
  "Ferritin": {
    summary: "Ferritin is the protein that stores iron inside cells. It is the most reliable indicator of iron stores in the body. Low ferritin precedes a falling haemoglobin — catching it early prevents overt iron-deficiency anaemia. Ferritin is also an acute-phase reactant; it rises with inflammation, making it unreliable in the setting of infection or chronic disease.",
    goodRange: "Men: 30–400 ng/mL. Women: 13–150 ng/mL. Many functional practitioners target 50–100 ng/mL for optimal energy and hair health. Levels >200 (without inflammation) may indicate haemochromatosis.",
    howToImprove: "Low ferritin: iron supplementation, dietary optimisation. High ferritin: investigate haemochromatosis (genetic iron overload). Therapeutic phlebotomy is the treatment for haemochromatosis. If high ferritin is due to inflammation, treating the underlying inflammatory condition is the priority.",
  },
  "Uric Acid": {
    summary: "Uric acid is the end-product of purine metabolism. Elevated uric acid (hyperuricaemia) is the root cause of gout — it precipitates as monosodium urate crystals in joints. Chronically elevated uric acid is also independently associated with hypertension, kidney stones, and metabolic syndrome.",
    goodRange: "Men: 3.5–7.2 mg/dL. Women: 2.6–6.0 mg/dL. Below 6.0 mg/dL is the target for gout management; below 5.0 mg/dL for tophaceous gout.",
    howToImprove: "Reduce high-purine foods (organ meats, shellfish, red meat). Eliminate alcohol, particularly beer and spirits. Fructose and sugar-sweetened beverages are major drivers. Stay well-hydrated (>2L water/day). Cherry extract and vitamin C modestly lower uric acid. Allopurinol or febuxostat are effective medications when lifestyle changes are insufficient.",
  },
  "hsCRP": {
    summary: "High-sensitivity C-reactive protein (hsCRP) is a systemic inflammation marker produced by the liver. At low levels (<3 mg/L), it is one of the strongest independent predictors of future cardiovascular events. Elevated hsCRP without obvious infection reflects chronic low-grade inflammation — the substrate of metabolic disease and ageing.",
    goodRange: "Low cardiovascular risk: <1.0 mg/L. Average risk: 1.0–3.0 mg/L. High risk: >3.0 mg/L. Values >10 mg/L suggest acute infection or major inflammation rather than chronic risk.",
    howToImprove: "Anti-inflammatory lifestyle: omega-3 fatty acids (EPA+DHA ≥2 g/day), Mediterranean-style diet, regular aerobic exercise, weight loss, smoking cessation, and optimising sleep. Statins also reduce hsCRP independently of LDL lowering (the JUPITER trial rationale).",
  },
  "PSA": {
    summary: "Prostate-specific antigen (PSA) is a protein produced by prostate cells. Elevated PSA may indicate prostate cancer, benign prostatic hyperplasia (BPH), or prostatitis. It is a widely debated screening marker — sensitivity and specificity are imperfect, and the PSA velocity (rate of change over time) is often more informative than a single value.",
    goodRange: "Age-adjusted ranges: 40–49 years: <2.5 ng/mL. 50–59: <3.5 ng/mL. 60–69: <4.5 ng/mL. PSA doubling time <3 years warrants urological evaluation.",
    howToImprove: "No lifestyle intervention reliably lowers PSA long-term. Avoid ejaculation 48 hours before testing (temporarily elevates PSA). 5-alpha reductase inhibitors (finasteride, dutasteride) suppress PSA and are used for BPH. Rising PSA requires formal urological evaluation including potential biopsy.",
  },
  // ── Ratios ────────────────────────────────────────────────────────────────
  "Cholesterol/HDL Ratio": {
    summary: "The total cholesterol-to-HDL ratio (also called the cardiac risk ratio or Castelli risk index) divides all cholesterol — good and bad — by the protective HDL fraction. It is one of the most widely used single-number cardiovascular risk predictors because it captures both the atherogenic burden and the protective capacity simultaneously. A high ratio means too much cholesterol relative to your protective HDL.",
    goodRange: "Below 3.5 is optimal. 3.5–5.0 is average risk. Above 5.0 is elevated risk. The American Heart Association considers above 5.0 a flag for increased cardiovascular event risk, independent of absolute LDL.",
    howToImprove: "Two levers: raise HDL (aerobic exercise ≥150 min/week, replace refined carbs with unsaturated fats, moderate alcohol if applicable, niacin under medical supervision) and lower total cholesterol (reduce saturated fat, increase soluble fibre, plant sterols, statins if indicated). Losing excess weight improves both simultaneously.",
  },
  "A/G Ratio": {
    summary: "The albumin-to-globulin (A/G) ratio compares albumin (the liver's main export protein) to globulin (an umbrella term for immune and transport proteins). A low ratio signals either insufficient albumin production (liver disease, malnutrition) or excess globulins (chronic infection, autoimmune disease, multiple myeloma). A high ratio is rarely clinically significant.",
    goodRange: "1.1–2.5 is normal. Below 1.0 warrants investigation for liver pathology or protein dysregulation. Above 2.5 is unusual but generally benign.",
    howToImprove: "A low ratio driven by low albumin responds to protein optimisation (0.8–1.2 g/kg/day) and treating underlying liver disease. A low ratio driven by high globulins requires identifying the inflammatory or immune cause — protein electrophoresis is the next step.",
  },
  "HDL/LDL Ratio": {
    summary: "The HDL-to-LDL ratio captures the balance between the 'good' (scavenging) and 'bad' (depositing) cholesterol particles. A higher ratio means more protective cholesterol relative to atherogenic cholesterol — it is a more nuanced cardiovascular risk signal than either value alone.",
    goodRange: "Above 0.3 is the general minimum; above 0.4 is good; above 0.5 is optimal for cardiovascular protection. Many cardiologists prefer this ratio to total cholesterol as a risk stratification tool.",
    howToImprove: "Raise HDL through aerobic exercise and replacing refined carbohydrates with healthy fats. Lower LDL through dietary saturated fat reduction, plant sterols, and statins if needed. Both levers move the ratio in your favour.",
  },
  "LDL/HDL Ratio": {
    summary: "The LDL-to-HDL ratio (also called the cardiac risk ratio) directly measures atherogenic burden relative to protective capacity. Lower is better — it is one of the strongest lipid-based predictors of cardiovascular event risk and is increasingly preferred over total cholesterol alone.",
    goodRange: "Below 3.5 is acceptable; below 2.5 is optimal; below 2.0 is associated with very low cardiovascular risk. Above 5.0 is high risk.",
    howToImprove: "Reduce LDL via dietary changes (saturated fat, refined carbs) and statins if indicated. Raise HDL via exercise and replacing carbohydrates with unsaturated fats. A combined approach achieves the largest ratio improvement.",
  },
};

// Case-insensitive lookup with partial-match fallback
export function getBiomarkerInfo(name: string): BiomarkerInfo | null {
  const lower = name.toLowerCase().trim();
  // Exact key match (case-insensitive)
  for (const key of Object.keys(INFO)) {
    if (key.toLowerCase() === lower) return INFO[key];
  }
  // Partial: name contains key or key contains name
  for (const key of Object.keys(INFO)) {
    const k = key.toLowerCase();
    if (lower.includes(k) || k.includes(lower)) return INFO[key];
  }
  return null;
}
