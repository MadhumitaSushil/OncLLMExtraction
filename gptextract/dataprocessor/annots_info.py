import os
import json

class AnnotsInfo:
    def __init__(self):
        """
        Note that all these elements should be automatically inferred in a later iteration of the pipeline.
        """
        with open(os.path.join('../../data/', 'note_section_texts.json')) as f:
            self.annotated_section_text = json.load(f)

        self.entities = {
            'Datetime',
            'PatientCharacteristics',
            'Symptom',
            'ClinicalCondition',
            'Allergy',
            'SDoH',
            'Alcohol',
            'Drugs',
            'Tobacco',
            'PhysicalActivity',
            'Employment',
            'LivingCondition',
            'Insurance',
            'SexualOrientation',
            'MaritalStatus',
            'SDoHModifier',
            'ConsumptionQuantity',
            'GenomicTest',
            'GermlineMutation',
            'SomaticMutation',
            'Site',
            'Laterality',
            'TumorTest',
            'Pathology',
            'Radiology',
            'DiagnosticLabTest',
            'TestResult',
            'RadPathResult',
            'GenomicTestResult',
            'LabTestResult',
            'TumorCharacteristics',
            'Histology',
            'Metastasis',
            'LymphNodeInvolvement',
            'Stage',
            'TNM',
            'Grade',
            'Size',
            'LocalInvasion',
            'BiomarkerName',
            'BiomarkerResult',
            'ProcedureName',
            'ProcedureModifier',
            'ProcedureOutcome',
            'MarginStatus',
            'MedicationName',
            'MedicationRegimen',
            'MedicationModifier',
            'Cycles',
            'RadiationTherapyName',
            'RadiationTherapyModifier',
            'TreatmentDosage',
            'TreatmentDoseModification',
            'TreatmentType',
            'ClinicalTrial',
            'Remission',
            'DiseaseProgression',
            'Hospice',
            'UnspecifiedEntity',
        }

        self.temporal_rels = {
            'HappensAtOnDuring',
            'BeginsOnOrAt',
            'EndsOnOrAt',
            'HappensBefore',
            'HappensAfter',
            'HappensOverlapping',
            'Temporal',
        }

        self.desc_rels = {
            'ConsumptionQuantityRel',
            'SDoHDesc',
            'LateralityOfSite',
            'SiteOf',
            'ResultOfTest',
            'BiomarkerRel',
            'ProcedureDesc',
            'TumorDesc',
            'TreatmentDesc',
            'RegimenFor',
        }

        self.adv_rels = {
            'TestOrProcedureReveals',
            'TestOrProcedureConductedForProblem',
            'TreatmentDiscontinuedBecauseOf',
            'ConditionOrTreatmentCausesProblem',
            'TreatmentAdministeredForProblem',
            'NotUndergoneBecauseOf',
            'InclusionCriteriaFor',
            'ExclusionCriteriaFor',
        }

        # ent: [list of att for ent ] ?
        self.atts = {
            'DatetimeVal',
            'NegationModalityVal',
            'IsStoppedOrContinuing',
            'IsPresentOnFirstCancerDiagnosis',
            'IsCausedByDiagnosedCancer',
            'ChronicVal',
            'ContinuityVal',
            'ExperiencerVal',
            'IntentVal',
            'RadPathResultVal',
            'LabTestResultVal',
            'GenomicTestType',
            'MarginVal',
            'HistoryVal',
            'EpisodeDescription',
            'BiomarkerResultVal',
            'TreatmentContinuityVal',
            'CycleType',
            'TreatmentTypeVal',
            'TreatmentIntentVal',
            'TreatmentCategory',
            'IsTumorRemaining',
            'SectionSkipType',
        }

if __name__ == '__main__':
    AnnotsInfo()