from collections import namedtuple

SymptomEnt = namedtuple("SymptomEnt", "Symptom, Datetime")
CancerDiagnosis = namedtuple("CancerDiagnosis", "Datetime")
RadTest = namedtuple("RadTest", "RadiologyTest, Datetime, Site, Reason, Result")
Proc = namedtuple("Proc", "ProcedureName, Datetime, Site, Reason, Result")
Genomics = namedtuple("Genomics", "GenomicTestName, Datetime, Result")
TxBiomarker = namedtuple('TxBiomarker', 'Biomarker, Datetime')
Histo = namedtuple('Histo', 'Histology Datetime')
MetastasisEnt = namedtuple('MetastasisEnt', 'Metastasis, Site, Procedure, Datetime')
StageEnt = namedtuple('StageEnt', 'Stage, Datetime, AdditionalTesting')
TnmEnt = namedtuple('TnmEnt', 'TNM, Datetime, AdditionalTesting')
GradeEnt = namedtuple('GradeEnt', 'Grade, Datetime, AdditionalTesting')
PrescribedMedEnt = namedtuple('PrescribedMedEnt', 'MedicationName, Begin, End, Reason, Continuity, '
                                                  'ConfirmedAdvEvent, PotentialAdvEvent')
FutureMedEnt = namedtuple('FutureMedEnt', 'MedicationName, Consideration, PotentialAdvEvent')

RadTestL = namedtuple("RadTest", "RadiologyTest, Datetime, Site, Laterality, Result")
ProcL = namedtuple("Proc", "ProcedureName, Datetime, Site, Laterality, Result")
RadTestS = namedtuple("RadTest", "RadiologyTest, Datetime, Site, Result")
ProcS = namedtuple("Proc", "ProcedureName, Datetime, Site, Result")
PrescribedMedEntNoAE = namedtuple('PrescribedMedEnt', 'MedicationName, Begin, End, Continuity')
FutureMedEntNoAE = namedtuple('FutureMedEnt', 'MedicationName, Consideration')

inference_subtype_to_default_ne_dict = {
        'symptoms': SymptomEnt('unknown', {'unknown'}),
        'symptoms_at_diagnosis': SymptomEnt('unknown', {'unknown'}),
        'symptoms_due_to_cancer': SymptomEnt('unknown', {'unknown'}),
        'radtest_datetime_site_reason_result': RadTest('unknown', {'unknown'}, {'unknown'}, {'unknown'}, {'unknown'}),
        'procedure_datetime_site_reason_result': Proc('unknown', {'unknown'}, {'unknown'}, {'unknown'}, {'unknown'}),
        'biomarker_datetime': TxBiomarker('unknown', {'unknown'}),
        'histology_datetime': Histo('unknown', {'unknown'}),
        'metastasis_site_procedure_datetime': MetastasisEnt('unknown', {'unknown'}, {'unknown'}, {'unknown'}),
        'stage_datetime_addtest': StageEnt('unknown', {'unknown'}, {'unknown'}),
        'tnm_datetime_addtest': TnmEnt('unknown', {'unknown'}, {'unknown'}),
        'grade_datetime_addtest': GradeEnt('unknown', {'unknown'}, {'unknown'}),
        'prescribed_med_begin_end_reason_continuity_ae': PrescribedMedEnt('unknown',
                                                                                {'unknown'}, {'unknown'}, {'unknown'},
                                                                                'unknown',
                                                                                {'unknown'}, {'unknown'}),
        'future_med_consideration_ae': FutureMedEnt('unknown', 'unknown', {'unknown'}),
        'genomictest_datetime_result': Genomics('unknown', {'unknown'}, {'unknown'}),
        'radtest_datetime_site_result': RadTestS('unknown', {'unknown'}, {'unknown'}, {'unknown'}),
        'procedure_datetime_site_result': ProcS('unknown', {'unknown'}, {'unknown'}, {'unknown'}),
        'radtest_datetime_site_lat_result': RadTestL('unknown', {'unknown'}, {'unknown'}, {'unknown'}, {'unknown'}),
        'procedure_datetime_site_lat_result': ProcL('unknown', {'unknown'}, {'unknown'}, {'unknown'}, {'unknown'}),
        'prescribed_med_begin_end_continuity': PrescribedMedEntNoAE('unknown', {'unknown'}, {'unknown'}, 'unknown'),
        'future_med_consideration': FutureMedEntNoAE('unknown', 'unknown'),
    }