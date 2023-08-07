class Prompt:
    def __init__(self):
        self.entity_chat_preamble = "Pretend you are a helpful Oncologist reading the given medical report." \
                                    "Answer as concisely as possible based on the input report."

        self.entity_prompt_template = "\n\nProvide only {} as a single python set of strings in the format: set<str>." \
                                      "Return set('no') when the information is not found. " \
                                      "Use '\'' for special quotation characters." \
                                      "Do not output information that is not present in input."

        self.adv_chat_preamble = "Pretend you are an oncologist. Answer based on the given clinical note for a patient."
        self.adv_prompt_template = "{} " \
                                   "Answer as concisely as possible." \
                                   "Use '\'' for special quotation characters." \
                                   "Do not return any information not present in the note. " \
                                   "Do not return any explanation."

        # TODO: add sdoh details
        self.sdoh_entity_chat_preamble = ""
        self.sdoh_entity_prompt_template = ""

        self.entity_to_prompt_mapping = {
            'Datetime': 'mentioned date and time',
            'Age': 'mentioned age',
            'Duration': 'mentioned duration of events',
            'Frequency': 'mentioned frequency of events',

            'Symptom': 'symptoms',
            'ClinicalCondition': 'confirmed clinical conditions',

            'GenomicTest': 'genomic test mention',
            'Site': 'mentioned site names with laterality',
            'Pathology': 'pathology method mention',
            'Radiology': 'mentioned radiology test name without results',
            'RadiologyResult': 'main radiology result',
            # 'GenomicTestResult': 'mentioned genomic test result value', # undecided
            'GenomicTestResult': 'genomic result mention',  # undecided
            'Histology': 'mentioned histology type',
            'Metastasis': "yes or no depending on whether metastatic disease is mentioned or not",
            'LymphNodeInvolvement': 'number of involved lymph nodes',
            # TODO: remove or union of TNM for eval? includes TNM otherwise.
            'Stage': 'mentioned cancer stage excluding TNM',
            'TNM': 'mentioned TNM value',
            'Grade': 'mentioned grade value',  # undecided.
            # 'Grade': 'grade value', # undecided.
            'Size': 'size',
            'BiomarkerNameAndResult': "biomarker names and their result",
            'TumorCharacteristics': "brief tumor characteristics",

            'ProcedureName': 'mentioned surgical and diagnostic procedure names',
            'MarginStatus': 'margin status (positive, negative or unknown)',
            'MedicationName': 'medication name mention',
            'MedicationRegimen': 'mentioned regimen name for medication',
            # 'Cycles': 'mentioned cycle value', # undecided
            'Cycles': 'treatment cycle value',  # undecided
            'RadiationTherapyName': 'yes or no depending on whether radiation therapy is mentioned or not',
            # 'TreatmentDosage': 'mentioned dose value', # undecided
            'TreatmentDosage': 'treatment dose value',
            'TreatmentType': 'category of treatment',
            'ClinicalTrial': 'mentioned clinical trial',  # undecided
            # 'ClinicalTrial': 'clinical trial mention',

            'Remission': 'yes or no depending on whether remission is discussed or not',
            'Hospice': 'yes or no depending on whether hospice is discussed or not',

            # EXCLUDED ENTITIES
            # unable to get rid of the laterality; fix in evaluation.
            # 'Laterality': 'mentioned lateralities of site',
            # 'BiomarkerName': "mentioned biomarker name without results",
            # 'BiomarkerResult': 'mentioned biomarker result value',  # attaches names to the values, results are elaborate.
            # 'RadPathResult': 'union of minimal radiology and pathology result',
            # 'PatientCharacteristics': '',
            # 'TumorTest': '',
            # 'TestResult': '',
            # 'Allergy': 'allergen', # Removing for now.
            # 'DiagnosticLabTest': 'diagnostic lab test name without results', # removing because not used for BC
            # 'LabTestResult': 'lab test result value',  # removing because not used for BC
            # 'LocalInvasion': 'mentions of local invasion', # removing for now. Too vague.
            # 'ProcedureModifier': '',
            # 'ProcedureOutcome': 'procedure outcome value', # Never annotated; removing
            # 'MedicationModifier': '',
            # 'RadiationTherapyModifier': '',
            # 'TreatmentDoseModification': 'treatment dose modification value',  # add later if needed.
            # 'DiseaseProgression': 'disease progression mention', # modify to recurrence label instead?
            # 'UnspecifiedEntity': '',
        }

        self.sdoh_entity_to_prompt_mapping = {
            # 'SDoH': '',  # TODO: add later as union of all sdoh
            'Alcohol': 'alcohol consumption value',
            'Drugs': 'drug use value',
            'Tobacco': 'tobacco use value',
            'PhysicalActivity': 'physical activity',
            'Employment': 'employment status mention',
            'LivingCondition': 'living status mention',
            'Insurance': 'insurance mention',
            'SexualOrientation': 'sexual orientation mention',
            'MaritalStatus': 'marital status mention',
            # 'SDoHModifier': '', # TODO: add later
            'ConsumptionQuantity': 'alcohol, drug or tobacco consumption quantity',
        }

        self.adv_criteria_to_prompt_mapping = {
            'symptoms': """
                For this note, please return all symptoms experienced by patient, paired with the date or time they experienced that symptom. 
                Do not return any medical diagnoses, radiological findings, clinical test, or procedure results.
                If a symptom is discussed, but only as a potential side effect or in the context of confirming the symptom’s absence, please do not include this symptom.
                In addition to returning the symptoms, return the date or time of the symptom onset.
                If the date or time is not present within the note, please return 'unknown' in the given format.
                Please return as namedtuples separated by newlines in the following format:
                SymptomEnt(Symptom='Symptom identified', Datetime={'Date or time identified'})
                Example:
                SymptomEnt(Symptom='Abdominal Pain', Datetime={'01/01/2020', '02/03/2020'})
                SymptomEnt(Symptom='lump', Datetime={'unknown'})
                """,

            'symptoms_at_diagnosis': """
                First, identify the date of first cancer diagnosis for this patient.
                After you have done this, please return symptoms experienced by the patient that were present before or at the time of cancer diagnosis.
                If present, pair these with the date or time they started experiencing that symptom. 
                If the date or time is not present within the note, please return 'unknown' in the given format.
                Do not return any medical diagnoses, radiological findings, clinical test or procedure results.
                Please return as namedtuples separated by newlines in the following format:
                CancerDiagnosis(Datetime={'Date or time of Cancer Diagnosis'})
                SymptomEnt(Symptom='Symptom identified', Datetime={'Date or time identified'})
                One example:
                CancerDiagnosis(Datetime={'03/01/2019'})
                SymptomEnt(Symptom='Abdominal Pain', Datetime={'01/01/2019'})
                Do not return any symptoms patient started experiencing subsequent to cancer diagnosis. 
            """,

            'symptoms_due_to_cancer': """
                For this note, please return all symptoms experienced by patient LIKELY TO BE CAUSED BY CANCER, paired with the date or time they started experiencing that symptom. 
                If the date or time is not present within the note, please return 'unknown' in the given format.
                Do not return any medical diagnoses, radiological findings, clinical test or procedure results.
                Please return as namedtuples separated by newlines in the following format:
                SymptomEnt(Symptom='Symptom identified", Datetime={'Date or time identified'})
                Example:
                SymptomEnt(Symptom='Abdominal Pain', Datetime={'01/01/2020', '02/03/2020'})
                SymptomEnt(Symptom='lump', Datetime={'unknown'})
                """,

            'radtest_datetime_site_reason_result': """
                For this note, please return all Radiology studies conducted for the patient, paired with the date or time when the study was performed, site of the study with its laterality, the symptom or clinical finding that the test was conducted for, and the results.
                Only include the results that are of relevance to an Oncologist.
                If any information is not present within the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                RadTest(RadiologyTest='Radiology test', Datetime={'Date or time'}, Site={'Laterality and Site of test'}, Reason={'Symptom or clinical finding for which the test was conducted'}, Result={'Result of the test'})
                Example:
                RadTest(RadiologyTest='MRI', Datetime={'01/01/2020'}, Site={'left breast'}, Reason={'lump'}, Result={'abnormal mass'})
                RadTest(RadiologyTest='PETCT', Datetime={'unknown'}, Site={'left, right breast'}, Reason={'unknown'}, Result={'unknown'})
            """,

            'procedure_datetime_site_reason_result': """
                For this note, please return all cancer-directed diagnostic and interventional procedures where there is a risk for bleeding.
                Pair these procedures with the date or time that the procedure was performed, laterality and site of the procedure, the clinical condition (e.g. diagnosis, symptom or problem) that the procedure was meant to identify or treat, and the result of the procedure. 
                Only include the results that are of relevance to an Oncologist.
                If the information is not present within the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                Proc(ProcedureName='Procedure identified', Datetime={'Date or time'}, Site={'laterality and site of procedure'}, Reason={'the clinical condition, such as diagnosis, symptom or problem that the procedure was meant to identify or treat'}, Result={'Result of the procedure'})
                Example:
                Proc(ProcedureName='Partial mastectomy', Datetime={'unknown'}, Site={'right breast'}, Reason={'lump'}, Result={'invasive carcinoma'})
                Proc(ProcedureName='mastectomy', Datetime={'01/01/2020'}, Site={'left, right breast'}, Reason={'unknown'}, Result={'unknown'})
                DO NOT return radiology tests.
            """,

            'genomictest_datetime_result': """
                For this note, please return all genomic and genetic tests that were conducted for the patient, and pair it with the date or time of the test and the result of the test.
                If any information is not present within the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                Genomics(GenomicTestName='Name of genomic test conducted', Datetime={'Date or time'}, Result={'Result of the test'})
                Example:
                Genomics(GenomicTestName='Onctotype', Datetime={'unknown'}, Result={'high risk'})
                Genomics(GenomicTestName='Genetic panel testing', Datetime={'01/01/2021'}, Result={'unknown'})
                Do not return radiology tests, surgical procedures, or cancer biomarkers that do not have a genomic or genetic basis.
            """,

            'biomarker_datetime': """
                For this note, please return all treatment relevant biomarkers identified for the breast cancer of this patient, paired with the date or time for that the characteristic was identified.
                If the date that identified the characteristic is not present within the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                TxBiomarker(Biomarker='biomarker name and result", Datetime={'Date or time identified'})
                Example:
                TxBiomarker(Biomarker='ER+', Datetime={'01/01/2020', '03/01/2021'})
                TxBiomarker(Biomarker='HER2-', Datetime={'unknown'})
                Do NOT return any radiological findings.
            """,

            'histology_datetime': """
                For this note, please return all morphological histology types identified for breast cancer of the patient, paired with the date that characteristic was identified.
                If the date for the identified characteristic is not present within the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                Histo(Histology='Histopathology', Datetime={'Date or time identified'})
                Example:
                Histo(Histology='IDC', Datetime={'unknown'})
                Histo(Histology='invasive ductal carcinoma', Datetime={'01/01/2020', '02/01/2013'})
                Do NOT return any radiological findings.
            """,

            'metastasis_site_procedure_datetime': """
                For this note, please return any evidence of metastatic spread identified for the cancer of this patient, paired with the procedure and date that identified the metastatic spread.
                If any information about the metastatic spread is not present within the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                MetastasisEnt(Metastasis='mention of Metastatic spread', Site={'Site of spread'}, Procedure={'Procedure that identified the metastatic spread'}, Datetime={'Date or time the procedure that identified the spread was conducted'})
                Example:
                MetastasisEnt(Metastasis='metastasis', Procedure={'CT Chest'}, Datetime={'01/01/2020'}, Site={'lungs'})
                MetastasisEnt(Metastasis='metastasis', Procedure={'unknown'}, Datetime={'unknown'}, Site={'nodes'})
            """,

            'stage_datetime_addtest': """
                For this note, please return staging for the breast cancer of this patient, paired with the date on which this staging was done.
                Do not include any stage indicated by the TNM staging criteria.
                If additional testing must be done to fully stage the patient, please return this within the same format as described below or return unclear.
                If the date of first staging is not clear in note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                StageEnt(Stage='Stage', Datetime={'Date conducted'}, AdditionalTesting={'test to be done'})
                Example:
                StageEnt(Stage='II', Datetime={'01/01/2020'}, AdditionalTesting={'CT Chest, abdomen, Pelvis'})
                StageEnt(Stage='early', Datetime={'unknown'}, AdditionalTesting={'unknown'})
            """,

            'tnm_datetime_addtest': """
                For this note, please return TNM Staging system for breast cancer.
                If additional testing must be done to fully stage the patient by TNM staging, please return this within the same format as described below.
                If the date of first staging is not clear in note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                TnmEnt(TNM='TNM Stage', Datetime={'Date conducted'}, AdditionalTesting={'test to be done'})
                Example:
                TnmEnt(TNM='cT3N1M0', Datetime={'01/01/2020'}, AdditionalTesting={'CT Chest, abdomen, Pelvis'})
                TnmEnt(TNM='T2N1', Datetime={'unknown'}, AdditionalTesting={'unknown'})
            """,

            'grade_datetime_addtest': """
                For this note, please return the combined Nottingham pathological grade for breast cancer.
                If additional testing must be done to fully grade the patients tumor, please return this within the same format as described below.
                If any information for the grade is not clear in the note, please return 'unknown'.
                Please return as namedtuples separated by newlines in the following format:
                GradeEnt(Grade='Combined grade', Datetime={'Date conducted'}, AdditionalTesting={'test to be done'})
                Example:
                GradeEnt(Grade='3', Datetime={'01/01/2020'}, AdditionalTesting={'unknown'})
                GradeEnt(Grade='GX', Datetime={'unknown'}, AdditionalTesting={'Number of mitoses'})
            """,

            'prescribed_med_begin_end_reason_continuity_ae': """
                    For this note, please return all cancer-directed medications that were prescribed to the patient.
                    Pair these medications with the date they were prescribed, and the date they were stopped as accurately as possible.
                    If the medication name has been identified, add the details of the symptom or clinical finding that it was prescribed for.
                    Also add details about the medication's continuity status among the following options: 'continuing', 'finished', 'discontinued early', or 'unknown'.
                    Additionally include any problems that were caused due to the medication, and any potential problems that the medication can cause, only if it is mentioned in text.
                    If any information is not present within the note, please return 'unknown'.
                    Please return as namedtuples separated by newlines in the following format:
                    PrescribedMedEnt(MedicationName='Medication identified', Begin={'Medication start date or time'}, End={'Medication end date or time'}, Reason={'symptom or clincal finding that the known medication was prescribed for'}, Continuity='continuity status of the medication', ConfirmedAdvEvent={'problems that were certainly caused due to the medication'}, PotentialAdvEvent={'problems that could potentially be caused due to the medication, but did not certainly happen.'})
                    Example:
                    PrescribedMedEnt(MedicationName='Anastrozole', Begin={'01/01/2019'}, End={'01/01/2020'}, Reason={'unknown'}, Continuity='finished', ConfirmedAdvEvent={'swelling'}, PotentialAdvEvent={'unknown'})
                    PrescribedMedEnt(MedicationName='Abraxane', Begin={'01/03/2022'}, End={'unknown'}, Reason={'cancer'}, Continuity='started', ConfirmedAdvEvent={'unknown'}, PotentialAdvEvent={'swelling'})
                    
                    Please do not provide an answer if the MedicationName itself is not available.
                    DO NOT return medications that are planned or may be given in future.
                    Do not skip any fields in the given format.
            """,

            'future_med_consideration_ae': """
                For this note, please return all cancer-directed medications that are being considered for future therapy. Please include drug classes if the medication isn't specifically mentioned.
                For each, please return whether its considerations is 'planned', or 'hypothetical'.
                Also return any potential problems that the medication could cause, only if it is mentioned in text.
                Please return as namedtuples separated by newlines in the following format:
                FutureMedEnt(MedicationName='Medication identified', Consideration='Classification of consideration', PotentialAdvEvent={'problems that could potentially be caused due to the medication'})
                Example:
                FutureMedEnt(MedicationName='Anastrozole', Consideration='planned', PotentialAdvEvent={'swelling'})
                FutureMedEnt(MedicationName='Hormone replacement therapy', Consideration='hypothetical', PotentialAdvEvent={'unknown'})
                DO NOT return medications that were previously prescribed or are currently being prescribed.
                Do not skip any fields in the given format.
            """,

        }

    def yield_inference_subtype_prompt(self, inference_type):
        if inference_type == 'entity':
            template = self.entity_prompt_template
            for inference_subtype, subprompt in self.entity_to_prompt_mapping.items():
                yield inference_subtype, template.format(subprompt)
        elif inference_type == 'sdoh_entity':
            template = self.sdoh_entity_prompt_template
            for inference_subtype, subprompt in self.sdoh_entity_to_prompt_mapping.items():
                yield inference_subtype, template.format(subprompt)
        else:
            template = self.adv_prompt_template
            for inference_subtype, subprompt in self.adv_criteria_to_prompt_mapping.items():
                subprompt = self.adv_criteria_to_prompt_mapping[inference_subtype]
                yield inference_subtype, template.format(subprompt)

    def get_prompt(self, inference_type, inference_subtype):
        if inference_type == 'entity':
            template = self.entity_prompt_template
            subprompt = self.entity_to_prompt_mapping[inference_subtype]
        elif inference_type == 'sdoh_entity':
            template = self.sdoh_entity_prompt_template
            subprompt = self.sdoh_entity_to_prompt_mapping[inference_subtype]
        else:
            template = self.adv_prompt_template
            subprompt = self.adv_criteria_to_prompt_mapping[inference_subtype]

        return template.format(subprompt)

    def get_prompt_preamble(self, model, inference_type):
        if model in ['gpt-35-turbo', 'gpt-4']:
            if inference_type in ['entity', 'sdoh_entity']:
                return self.entity_chat_preamble
            else:
                return self.adv_chat_preamble

        return ''

