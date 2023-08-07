from collections import defaultdict

from gptextract import *

class InferenceAnnots:
    def __init__(self, entities, relations, attributes):
        self.all_entities = entities
        self.all_relations = relations
        self.all_attributes = attributes

        self.temporal_rels = ('HappensAtOnDuring',
                              'BeginsOnOrAt',
                              'EndsOnOrAt',
                              'HappensBefore',
                              'HappensAfter',
                              'HappensOverlapping',
                              'Temporal'
                              )

        self.begin_rels = ('BeginsOnOrAt', 'HappensAfter')
        self.end_rels = ('EndsOnOrAt', 'HappensBefore')

        self.result_rels = ('ResultOfTest', 'TestOrProcedureReveals')
        self.proc_result_rels = ('ResultOfTest', 'TestOrProcedureReveals', 'ProcedureDesc')
        self.test_proc_reasons_rels = ('TestOrProcedureConductedForProblem')
        self.site_rels = ('SiteOf')
        self.laterality_rels = ('LateralityOfSite')
        self.tumor_char_test_rels = ('TestOrProcedureReveals')
        self.treatment_reason_rels = ('TreatmentAdministeredForProblem')
        self.adv_event_rels = ('ConditionOrTreatmentCausesProblem', 'TreatmentDiscontinuedBecauseOf')

        self._update_biomarker_names_with_results()
        self._update_site_names_with_laterality()

    def _update_biomarker_names_with_results(self):
        """
        Update text of all BiomarkerName annotations with "BiomarkerName BiomarkerResult"
        """
        for ent in self.all_entities:
            if ent.type == 'BiomarkerName':
                for rel in self.all_relations:
                    if rel.ent1.idx == ent.idx:
                        if rel.ent2.type == 'BiomarkerResult':
                            ent.text = ent.text.strip() + ' ' + rel.ent2.text
                    elif rel.ent2.idx == ent.idx:
                        if rel.ent1.type == 'BiomarkerResult':
                            ent.text = ent.text.strip() + ' ' + rel.ent1.text

    def _update_site_names_with_laterality(self):
        """
        Update text of all Site annotations with "Laterality Site"
        """
        for ent in self.all_entities:
            if ent.type == 'Site':
                for rel in self.all_relations:
                    if rel.ent1.idx == ent.idx:
                        if rel.ent2.type == 'LateralityOfSite':
                            ent.text = rel.ent2.text.strip() + ' ' + ent.text.strip()
                    elif rel.ent2.idx == ent.idx:
                        if rel.ent1.type == 'LateralityOfSite':
                            ent.text = rel.ent1.text.strip() + ' ' + ent.text.strip()

    def _get_entities_of_type(self, entity_type):
        """
        :param entity_type: string, type of entity, case sensitive.
        :return: List of all annotated entities of given time
        """
        entities = list()
        for cur_ent in self.all_entities:
            if cur_ent.type == entity_type:
                entities.append(cur_ent)
        return entities

    def _get_attribute_for_entities(self, selected_entities, attribute_type):
        """
        :param selected_entities: list of entitites to get attribute values of
        :param attribute_type: string, case sensitive, attribute type.
        :return: dictionary of entities and their attribute value
        """
        ent_to_att = dict()
        for ent in selected_entities:
            for cur_att in self.all_attributes:
                if cur_att.ent.idx == ent.idx and cur_att.type == attribute_type:
                    ent_to_att[cur_att.ent] = cur_att

        return ent_to_att

    def _get_entity_pairs_in_relation(self, entities_of_interest, relations_to_consider):
        """
        :param entities_of_interest: list of entities to get relations of
        :param relations_to_consider: relations to consider for retrieving entity2
        :return: dictionary of set of related entities: [ent1: {ent2, ent3}] where ent1->ent2, ent1->ent3
        """
        ent_to_ent2 = defaultdict(set)
        for cur_ent in entities_of_interest:
            if cur_ent is None:
                continue
            found = False
            for cur_rel in self.all_relations:
                if cur_rel.ent1.idx == cur_ent.idx and cur_rel.type in relations_to_consider:
                    ent_to_ent2[cur_ent].add(cur_rel.ent2)
                    found = True
                if cur_rel.ent2.idx == cur_ent.idx and cur_rel.type in relations_to_consider:
                    ent_to_ent2[cur_ent].add(cur_rel.ent1)
                    found = True
            if not found:
                ent_to_ent2[cur_ent].add(None)

        return ent_to_ent2

    def _get_entity_pairs_in_transitive_relations(self, entities_of_interest,
                                                  first_relations_to_consider,
                                                  transitive_relations_to_consider):
        """

        :param entities_of_interest: list of entities to get relations of.
        :param first_relations_to_consider: iterable of first level of relations to consider.
        :param transitive_relations_to_consider: iterable of second level of relations to consider.
        :return: dictionary of set: {ent1: {ent2, ent3}} where ent1 may either be directly related, or related via
        the entities under the first relations to ent2 and ent3
        """
        linked_entities = self._get_entity_pairs_in_relation(entities_of_interest, first_relations_to_consider)
        entity2 = [ent for val in linked_entities.values() for ent in val]
        final_entities = self._get_entity_pairs_in_relation(entity2, transitive_relations_to_consider)
        transitive_entity_pairs = defaultdict(set)
        for ent1, ent2s_linked in linked_entities.items():
            for ent2_linked in ent2s_linked:
                for final_ent2 in final_entities[ent2_linked]:
                    transitive_entity_pairs[ent1].add(final_ent2)

        return transitive_entity_pairs

    def get_entity_mentions_for_inference(self):
        entity_mentions = defaultdict(set)
        for ent in self.all_entities:
            entity_mentions[ent.type].add(ent.text.strip().lower())

            if ent.type == 'BiomarkerResult' or ent.type == 'Laterality':
                # We have added the result to biomarker name and laterality to site; so skipping adding the result.
                continue

            if ent.type in ['Histology', 'Metastasis', 'LNInvolvement', 'Stage', 'TNM', 'Grade',
                            'BiomarkerName', 'TumorCharacteristics']:
                entity_mentions['TumorCharacteristics'].add(ent.text.strip().lower())

        for cur_rel in self.all_relations:
            if cur_rel.type in ['ResultOfTest', 'TestOrProcedureReveals']:
                if cur_rel.ent2.type == 'Radiology':
                    entity_mentions['RadiologyResult'].add(cur_rel.ent1.text.strip().lower())
                elif cur_rel.ent1.type == 'Radiology':
                    entity_mentions['RadiologyResult'].add(cur_rel.ent2.text.strip().lower())

        if 'BiomarkerName' in entity_mentions:
            entity_mentions['BiomarkerNameAndResult'] = entity_mentions.pop('BiomarkerName')
        return entity_mentions

    def _filter_assertion(self, entities,
                          remove_assertions=('negated',
                                             'hypothetical_in_future',
                                             'planned_in_future',
                                             # 'uncertain_in_past',
                                             # 'uncertain_in_present',
                                             )):
        assertions = self._get_attribute_for_entities(entities, 'NegationModalityVal')
        for ent, assertion in assertions.items():
            if any(to_remove.lower() in assertion.val.lower() for to_remove in remove_assertions):
                entities.remove(ent)

        return entities

    def _filter_experiencer(self, entities, remove_experiencers=('family', 'others')):
        experiencers = self._get_attribute_for_entities(entities, 'ExperiencerVal')
        for ent, experiencer in experiencers.items():
            if any(to_remove.lower() in experiencer.val.lower() for to_remove in remove_experiencers):
                entities.remove(ent)

        return entities

    def _get_entity_text_with_negation_uncertainty(self, entities):
        entities = {ent for ent in entities if ent is not None}
        if not len(entities):
            return {}

        assertions = self._get_attribute_for_entities(entities, 'NegationModalityVal')
        entity_texts = set()
        for ent in entities:
            if ent not in assertions:
                entity_texts.add(ent.text.lower().strip())
                continue

            res_assertion = assertions[ent]
            if 'hypothetical' in res_assertion.val.lower():
                continue
            if 'negated' in res_assertion.val.lower():
                entity_texts.add('no ' + ent.text.lower().strip())
            elif 'uncertain' in res_assertion.val.lower():
                entity_texts.add('unertain ' + ent.text.lower().strip())
            else:
                entity_texts.add(ent.text.lower().strip())

        return entity_texts

    def get_symptoms(self):
        symptom_ents = defaultdict(list)

        # symptom_datetime
        symptoms = self._get_entities_of_type('Symptom')
        symptoms = self._filter_experiencer(symptoms)
        symptoms = self._filter_assertion(symptoms)
        # symptom_assertions = self._get_attribute_for_entities(symptoms, 'NegationModalityVal')
        #
        # for symptom, assertion in symptom_assertions.items():
        #     if 'negated' in assertion.val or \
        #             'uncertain' in assertion.val or \
        #             'hypothetical' in assertion.val or \
        #             'planned' in assertion.val:
        #         symptoms.remove(symptom)

        symptom_dates = self._get_entity_pairs_in_relation(symptoms, self.temporal_rels)
        for ent in symptoms:
            dates = symptom_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_symptoms = SymptomEnt(ent.text.lower().strip(), dates)
            symptom_ents['symptoms'].append(cur_symptoms)

        # symptoms_at_diagnosis
        symptoms_at_diag = self._get_attribute_for_entities(symptoms, 'IsPresentOnFirstCancerDiagnosis')
        symptoms_at_diag = [key for key, att in symptoms_at_diag.items() if att.val == 'yes']
        symptoms_at_diag_dates = self._get_entity_pairs_in_relation(symptoms_at_diag, self.temporal_rels)
        for ent in symptoms_at_diag:
            dates = symptoms_at_diag_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_symptoms = SymptomEnt(ent.text.lower().strip(), dates)
            symptom_ents['symptoms_at_diagnosis'].append(cur_symptoms)

        # symptom_due_to_cancer
        symptoms_due_to_cancer = self._get_attribute_for_entities(symptoms, 'IsCausedByDiagnosedCancer')
        symptoms_due_to_cancer = [key for key, att in symptoms_due_to_cancer.items() if att.val == 'yes']
        symptoms_due_to_cancer_dates = self._get_entity_pairs_in_relation(symptoms_due_to_cancer,
                                                                          self.temporal_rels)

        for ent in symptoms_due_to_cancer:
            dates = symptoms_due_to_cancer_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_symptoms = SymptomEnt(ent.text.lower().strip(), dates)
            symptom_ents['symptoms_due_to_cancer'].append(cur_symptoms)

        return symptom_ents

    def get_radiology(self):
        rad_ents = defaultdict(list)

        # radtest_datetime_site_lat_result
        radtest = self._get_entities_of_type('Radiology')
        radtest = self._filter_experiencer(radtest)
        radtest = self._filter_assertion(radtest)
        radtest_datetimes = self._get_entity_pairs_in_relation(radtest, self.temporal_rels)
        radtest_sites = self._get_entity_pairs_in_relation(radtest, self.site_rels)
        # radtest_lateralities = self._get_entity_pairs_in_transitive_relations(radtest, self.site_rels,
        #                                                                       self.laterality_rels)
        radtest_reasons = self._get_entity_pairs_in_relation(radtest, self.test_proc_reasons_rels)
        radtest_results = self._get_entity_pairs_in_relation(radtest, self.result_rels)

        for ent in radtest:
            dates = radtest_datetimes[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}

            sites = radtest_sites[ent]
            sites = {site.text.lower().strip() for site in sites if site is not None}
            if not len(sites):
                sites = {'unknown'}

            # lateralities = radtest_lateralities[ent]
            # lateralities = {lat.text.lower().strip() for lat in lateralities if lat is not None}
            # if not len(lateralities):
            #     lateralities = {'unknown'}

            reasons = radtest_reasons[ent]
            reasons = self._get_entity_text_with_negation_uncertainty(reasons)
            if not len(reasons):
                reasons = {'unknown'}

            results = radtest_results[ent]
            results = self._get_entity_text_with_negation_uncertainty(results)
            if not len(results):
                results = {'unknown'}

            cur_ent = RadTest(ent.text.lower().strip(), dates, sites, reasons, results)
            rad_ents['radtest_datetime_site_reason_result'].append(cur_ent)

        return rad_ents

    def get_procedures(self):
        # procedure_datetime_site_reason_result
        proc_ents = defaultdict(list)

        procedure = self._get_entities_of_type('ProcedureName')
        procedure = self._filter_experiencer(procedure)
        procedure = self._filter_assertion(procedure)

        procedure_datetimes = self._get_entity_pairs_in_relation(procedure, self.temporal_rels)
        procedure_sites = self._get_entity_pairs_in_relation(procedure, self.site_rels)
        # procedure_lateralities = self._get_entity_pairs_in_transitive_relations(procedure, self.site_rels,
        #                                                                         self.laterality_rels)
        procedure_reasons = self._get_entity_pairs_in_relation(procedure, self.test_proc_reasons_rels)
        procedure_results = self._get_entity_pairs_in_relation(procedure, self.proc_result_rels)

        for ent in procedure:
            dates = procedure_datetimes[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}

            sites = procedure_sites[ent]
            sites = {site.text.lower().strip() for site in sites if site is not None}
            if not len(sites):
                sites = {'unknown'}

            # lateralities = procedure_lateralities[ent]
            # lateralities = {lat.text.lower().strip() for lat in lateralities if lat is not None}
            # if not len(lateralities):
            #     lateralities = {'unknown'}

            reasons = procedure_reasons[ent]
            reasons = self._get_entity_text_with_negation_uncertainty(reasons)
            if not len(reasons):
                reasons = {'unknown'}

            results = procedure_results[ent]
            results = self._get_entity_text_with_negation_uncertainty(results)
            if not len(results):
                results = {'unknown'}

            cur_ent = Proc(ent.text.lower().strip(), dates, sites, reasons, results)
            proc_ents['procedure_datetime_site_reason_result'].append(cur_ent)

        return proc_ents

    def get_genomics(self):
        genomic_ents = defaultdict(list)

        # genomictest_datetime_result
        genomictest = self._get_entities_of_type('GenomicTest')
        genomictest = self._filter_experiencer(genomictest)
        genomictest = self._filter_assertion(genomictest)
        genomictest_datetimes = self._get_entity_pairs_in_relation(genomictest, self.temporal_rels)
        genomictest_results = self._get_entity_pairs_in_relation(genomictest, self.result_rels)
        print(genomictest_results)

        for ent in genomictest:
            dates = genomictest_datetimes[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}

            results = genomictest_results[ent]
            results = self._get_entity_text_with_negation_uncertainty(results)
            if not len(results):
                results = {'unknown'}

            cur_ent = Genomics(ent.text.lower().strip(), dates, results)
            genomic_ents['genomictest_datetime_result'].append(cur_ent)

        return genomic_ents

    def get_tumor_chars(self):
        tumor_char_ents = defaultdict(list)

        # biomarker_datetime
        biomarkers = self._get_entities_of_type('BiomarkerName')
        biomarkers = self._filter_experiencer(biomarkers)
        biomarkers = self._filter_assertion(biomarkers)

        biomarker_dates = self._get_entity_pairs_in_transitive_relations(biomarkers,
                                                                         self.tumor_char_test_rels,
                                                                         self.temporal_rels)
        for ent in biomarkers:
            dates = biomarker_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_biomarkers = TxBiomarker(ent.text.lower().strip(), dates)
            tumor_char_ents['biomarker_datetime'].append(cur_biomarkers)

        # histology_datetime
        histology = self._get_entities_of_type('Histology')
        histology = self._filter_experiencer(histology)
        histology = self._filter_assertion(histology)
        histology_dates = self._get_entity_pairs_in_transitive_relations(histology,
                                                                         self.tumor_char_test_rels,
                                                                         self.temporal_rels)
        for ent in histology:
            dates = histology_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_histology = Histo(ent.text.lower().strip(), dates)
            tumor_char_ents['histology_datetime'].append(cur_histology)

        # metastasis_site_procedure_datetime
        metastasis = self._get_entities_of_type('Metastasis')
        metastasis = self._filter_experiencer(metastasis)
        metastasis = self._filter_assertion(metastasis)

        metastasis_sites = self._get_entity_pairs_in_relation(metastasis, self.site_rels)
        metastasis_sites2 = self._get_entity_pairs_in_transitive_relations(metastasis,
                                                                           self.tumor_char_test_rels,
                                                                           self.site_rels)
        for key, val in metastasis_sites2.items():
            metastasis_sites[key].update(val)

        metastasis_proc = self._get_entity_pairs_in_relation(metastasis, self.result_rels)
        metastasis_dates = self._get_entity_pairs_in_transitive_relations(metastasis,
                                                                          self.tumor_char_test_rels,
                                                                          self.temporal_rels)
        for ent in metastasis:
            sites = metastasis_sites[ent]
            sites = {site.text.lower().strip() for site in sites if site is not None}
            if not len(sites):
                sites = {'unknown'}
            procs = metastasis_proc[ent]
            procs = {proc.text.lower().strip() for proc in procs if proc is not None}
            if not len(procs):
                procs = {'unknown'}
            dates = metastasis_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}

            cur_ent = MetastasisEnt(ent.text.lower().strip(), sites, procs, dates)
            tumor_char_ents['metastasis_site_procedure_datetime'].append(cur_ent)

        # stage_datetime_addtest
        stage = self._get_entities_of_type('Stage')
        stage = self._filter_experiencer(stage)
        stage = self._filter_assertion(stage)
        stage_dates = self._get_entity_pairs_in_transitive_relations(stage,
                                                                     self.tumor_char_test_rels,
                                                                     self.temporal_rels)
        for ent in stage:
            dates = stage_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_stages = StageEnt(ent.text.lower().strip(), dates, {'unknown'})
            tumor_char_ents['stage_datetime_addtest'].append(cur_stages)

        # tnm_datetime_addtest
        tnm = self._get_entities_of_type('TNM')
        tnm = self._filter_experiencer(tnm)
        tnm = self._filter_assertion(tnm)
        tnm_dates = self._get_entity_pairs_in_transitive_relations(tnm, self.tumor_char_test_rels, self.temporal_rels)
        for ent in tnm:
            dates = tnm_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_tuple = TnmEnt(ent.text.lower().strip(), dates, {'unknown'})
            tumor_char_ents['tnm_datetime_addtest'].append(cur_tuple)


        # grade_datetime_addtest
        grade = self._get_entities_of_type('Grade')
        grade = self._filter_experiencer(grade)
        grade = self._filter_assertion(grade)
        grade_dates = self._get_entity_pairs_in_transitive_relations(grade, self.tumor_char_test_rels,
                                                                     self.temporal_rels)
        for ent in grade:
            dates = grade_dates[ent]
            dates = {date.text.lower().strip() for date in dates if date is not None}
            if not len(dates):
                dates = {'unknown'}
            cur_tuple = GradeEnt(ent.text.lower().strip(), dates, {'unknown'})
            tumor_char_ents['grade_datetime_addtest'].append(cur_tuple)

        return tumor_char_ents

    def get_treatments(self):
        med_ents = defaultdict(list)

        # prescribed_med_begin_end_continuity
        # future_med_consideration

        meds = self._get_entities_of_type('MedicationName')
        meds.extend(self._get_entities_of_type('MedicationRegimen'))
        # meds.extend(self._get_entities_of_type('TreatmentType')) # Does not contain TreatmentCategory
        meds = self._filter_experiencer(meds)
        # Removing non-cancer medicines
        med_types = self._get_attribute_for_entities(meds, 'TreatmentCategory')
        for med, med_type in med_types.items():
            if med_type.val == 'Supportive' or med_type.val == 'Others':
                meds.remove(med)

        # Removing medicines that have neither been certainly prescribed, nor considered for future
        meds = self._filter_assertion(meds, remove_assertions=['negated',
                                                               'uncertain_in_past',
                                                               'uncertain_in_present'
                                                               ])

        # TODO: check how to add other dates.
        meds_begin = self._get_entity_pairs_in_relation(meds, self.begin_rels)
        meds_end = self._get_entity_pairs_in_relation(meds, self.end_rels)
        meds_reasons = self._get_entity_pairs_in_relation(meds, self.treatment_reason_rels)
        meds_adv_events = self._get_entity_pairs_in_relation(meds, self.adv_event_rels)
        meds_assertions = self._get_attribute_for_entities(meds, 'NegationModalityVal')
        meds_continuity = self._get_attribute_for_entities(meds, 'TreatmentContinuityVal')

        for ent in meds:
            begins = meds_begin[ent]
            begins = {date.text.lower().strip() for date in begins if date is not None}
            if not len(begins):
                begins = {'unknown'}

            ends = meds_end[ent]
            ends = {date.text.lower().strip() for date in ends if date is not None}
            if not len(ends):
                ends = {'unknown'}

            reasons = meds_reasons[ent]
            reasons = self._get_entity_text_with_negation_uncertainty(reasons)
            if not len(reasons):
                reasons = {'unknown'}

            adv_events = meds_adv_events[ent]
            adv_events = {event for event in adv_events if event is not None}
            med_adv_event_assertions = self._get_attribute_for_entities(adv_events, 'NegationModalityVal')
            potential_aes = set()
            for cur_adv_event in list(adv_events):
                if cur_adv_event not in med_adv_event_assertions:
                    continue
                adv_event_assertion = med_adv_event_assertions[cur_adv_event]
                if adv_event_assertion.val == 'negated' or 'uncertain' in adv_event_assertion.val \
                        or 'hypothetical' in adv_event_assertion.val:
                    # remove all adverse events that are not affirmed
                    potential_aes.add(adv_event_assertion.ent.text)
                    adv_events.remove(adv_event_assertion.ent)
            adv_events = {ent.text for ent in adv_events}
            if not len(adv_events):
                adv_events = {'unknown'}
            if not len(potential_aes):
                potential_aes = {'unknown'}

            assertion = meds_assertions[ent].val.lower().strip() if ent in meds_assertions else 'affirmed'
            if 'hypothetical' in assertion:
                assertion = 'hypothetical'
            if 'planned' in assertion:
                assertion = 'planned'
            continuity = meds_continuity[ent].val.lower().strip() if ent in meds_continuity else 'unclear'
            if continuity == 'unclear':
                continuity = 'unknown'
            if continuity == 'started':
                continuity = 'continuing'

            if 'planned' in continuity or 'planned' in assertion:
                cur_ent = FutureMedEnt(ent.text.lower().strip(), 'planned', potential_aes)
                med_ents['future_med_consideration_ae'].append(cur_ent)
            elif 'hypothetical' in assertion:
                cur_ent = FutureMedEnt(ent.text.lower().strip(), 'hypothetical', potential_aes)
                med_ents['future_med_consideration_ae'].append(cur_ent)
            else:
                cur_ent = PrescribedMedEnt(ent.text.lower().strip(), begins, ends, reasons,
                                           continuity.replace('_', ' '),
                                           adv_events, potential_aes)
                med_ents['prescribed_med_begin_end_reason_continuity_ae'].append(cur_ent)

        return med_ents

    def get_tuples_for_advanced_inference(self):
        inference_tuple_dict = defaultdict(set)

        symptom_ents = self.get_symptoms()
        inference_tuple_dict.update(symptom_ents)

        rad_ents = self.get_radiology()
        inference_tuple_dict.update(rad_ents)

        proc_ents = self.get_procedures()
        inference_tuple_dict.update(proc_ents)

        genomic_ents = self.get_genomics()
        inference_tuple_dict.update(genomic_ents)

        tumor_ents = self.get_tumor_chars()
        inference_tuple_dict.update(tumor_ents)

        treatment_ents = self.get_treatments()
        inference_tuple_dict.update(treatment_ents)

        # print(inference_tuple_dict)
        return inference_tuple_dict