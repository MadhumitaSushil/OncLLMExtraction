import argparse
import ast
import csv
import ipdb
import os
import pathlib
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd

from gptextract.dataprocessor.annots_for_inference import InferenceAnnots
from gptextract.bratreader.brat import Collection
from gptextract.prompts.prompt_design import Prompt
from gptextract.modeling.openai_api_azure import OpenaiApiCall
from gptextract.modeling.hf_pipeline import HuggingfaceModel
from gptextract.utils.parse_output import parse_namedtuples
from gptextract.utils.metrics import Metrics

from gptextract import *


class Annotation:
    def __init__(self, doc_idx, section_name, section_text, inf_type, inf_subtype, annotations):
        self.doc_idx = doc_idx
        self.section_name = section_name
        self.section_text = section_text
        self.inf_type = inf_type
        self.inf_subtype = inf_subtype
        self.annotations = annotations

    def serialize(self, fannot, dir_annot):
        headers = ['doc_idx', 'section_name', 'section_text', 'inference_type', 'inference_subtype',
                   'annotation_set']

        data = [self.doc_idx, self.section_name, self.section_text, self.inf_type, self.inf_subtype,
                self.annotations]

        with open(os.path.join(dir_annot, fannot), 'a') as f:
            csvwriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if f.tell() == 0:
                # write header to empty file
                csvwriter.writerow(headers)
            csvwriter.writerow(data)


class AnnotationColl:

    def __init__(self, annot_lst):
        self.annotation_coll = annot_lst

        self.processed = {str(cur_annot.doc_idx) + cur_annot.section_name
                          + cur_annot.inf_type + cur_annot.inf_subtype
                          for cur_annot in self.annotation_coll}

    @classmethod
    def read_existing_coll(cls, fname_coll, dir_coll):
        df = pd.read_csv(os.path.join(dir_coll, fname_coll), quotechar='"')
        df.drop_duplicates(inplace=True)
        annot_lst = list()

        for row in df.itertuples(index=False):
            if row.inference_type == 'advanced_inference':
                annots = [eval(cur_annot) for cur_annot in row.annotation_set.strip().split('\n')]
            else:
                raise ValueError("Unsupported inference type")

            cur_annot = Annotation(row.doc_idx, row.section_name, row.section_text,
                                   row.inference_type, row.inference_subtype, annots)

            annot_lst.append(cur_annot)

        return cls(annot_lst)

    def is_processed(self, example):
        if example in self.processed:
            return True
        else:
            return False

    def get_annot_from_coll(self, doc_idx, section_name, inf_type, inf_subtype):
        matching_annots = list()
        for annot in self.annotation_coll:
            if (annot.doc_idx == doc_idx and annot.section_name == section_name and
                    annot.inf_type == inf_type and annot.inf_subtype == inf_subtype):
                matching_annots.append(annot)

        return matching_annots


class Output:
    def __init__(self, doc_idx, section_name, section_text, inf_type, inf_subtype,
                 model_type, temperature, prompt_preamble, prompt,
                 output):
        self.doc_idx = doc_idx
        self.section_name = section_name
        self.section_text = section_text
        self.inf_type = inf_type
        self.inf_subtype = inf_subtype

        self.model_type = model_type
        self.temp = temperature
        self.prompt_preamble = prompt_preamble
        self.prompt = prompt
        self.output = output

    def serialize(self, fname_output, dir_output):
        headers = ['doc_idx', 'section_name', 'section_text', 'inference_type', 'inference_subtype',
                   'model_type', 'temperature', 'prompt_preamble', 'prompt', 'model_output'
                   ]

        data = [self.doc_idx, self.section_name, self.section_text, self.inf_type, self.inf_subtype,
                self.model_type, self.temp, self.prompt_preamble, self.prompt, self.output]

        with open(os.path.join(dir_output, fname_output), 'a') as f:
            csvwriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if f.tell() == 0:
                # write header to empty file
                csvwriter.writerow(headers)
            csvwriter.writerow(data)


class OutputColl:
    def __init__(self, output_lst):
        self.outputs = output_lst

        self.processed = {str(cur_out.doc_idx) + cur_out.section_name + cur_out.inf_type + cur_out.inf_subtype +
                          str(cur_out.model_type) + str(cur_out.temp) + cur_out.prompt_preamble + cur_out.prompt
                          for cur_out in self.outputs}

    @classmethod
    def read_existing_coll(cls, fname_coll, dir_coll):
        df = pd.read_csv(os.path.join(dir_coll, fname_coll), quotechar='"', encoding='cp1252')
        df = df.dropna(how='all')
        output_lst = list()

        for row in df.itertuples(index=False):
            if row.inference_type == 'advanced_inference':
                parsed_output = parse_namedtuples(row.model_output.replace('\r\n', '\n'), row.inference_subtype)
            else:
                raise ValueError("Unsupported inference type")

            if str(row.prompt_preamble) == 'nan':
                prompt_preamble = ''
            else:
                prompt_preamble = row.prompt_preamble.replace('\r\n', '\n')

            cur_out = Output(row.doc_idx,
                             row.section_name, row.section_text.replace('\r\n', '\n'),
                             row.inference_type, row.inference_subtype, row.model_type, row.temperature,
                             prompt_preamble, row.prompt.replace('\r\n', '\n'),
                             parsed_output
                             )

            output_lst.append(cur_out)

        return cls(output_lst)

    def is_processed(self, example):
        if example in self.processed:
            return True
        else:
            return False


class OncInfoExtr:
    def __init__(self, coll_dir,
                 sections_to_infer=('hpi', 'a&p'),
                 inference_types=('advanced_inference',),
                 fdata='onc_pn_ie_data.csv', foutput='onc_pn_ie_output.csv', fscores='scores.csv',
                 data_dir='../data/', output_dir='../output/',
                 append_timestamp=True):

        self.collection = Collection.read_collection(coll_dir)
        self.sections_to_infer = sections_to_infer

        self.inference_types = inference_types

        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(data_dir)

        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(output_dir)

        self.fname_ie_data = fdata
        if append_timestamp:
            self.fname_ie_data = self.fname_ie_data.rstrip('csv').rstrip('.') + '_' + str(date.today()) + '.csv'

        self.fname_ie_output = foutput
        if append_timestamp:
            self.fname_ie_output = self.fname_ie_output.rstrip('csv').rstrip('.') + '_' + str(date.today()) + '.csv'

        self.fname_scores = fscores
        if append_timestamp:
            self.fname_scores = self.fname_scores.rstrip('csv').rstrip('.') + '_' + str(date.today()) + '.csv'

    def _get_section_texts_to_infer(self, sections_to_infer):
        for doc_idx, doc in self.collection.documents.items():
            for section in sections_to_infer:
                print(self.collection.get_annots_by_section_name(doc, section))

    def get_elements_for_inference(self, entities, attributes, relations):
        inference_annots = InferenceAnnots(entities, attributes, relations)
        advanced_inference_tuple_dict = inference_annots.get_tuples_for_advanced_inference()

        return advanced_inference_tuple_dict

    def serialize_annotated_ie_dataset(self):
        if os.path.exists(os.path.join(self.data_dir, self.fname_ie_data)):
            existing_coll = AnnotationColl.read_existing_coll(self.fname_ie_data, self.data_dir)
        else:
            existing_coll = None

        for doc_idx, doc in self.collection.documents.items():
            for section in self.sections_to_infer:
                cur_text, cur_ents, cur_atts, cur_rels = self.collection.get_annots_by_section_name(doc, section)
                cur_text = cur_text.replace('', ' ')
                adv_inf_tuples = self.get_elements_for_inference(cur_ents, cur_atts, cur_rels)

                for cur_inf_type, tuple in adv_inf_tuples.items():
                    str_tuple = ""
                    for cur_item in tuple:
                        str_tuple += str(cur_item)+'\n'

                    if existing_coll and existing_coll.is_processed(
                            doc_idx + section + 'advanced_inference' + cur_inf_type):
                        print("Skipping duplicate data entry")
                        continue

                    annot_obj = Annotation(doc_idx, section, cur_text, 'advanced_inference', cur_inf_type, str_tuple)
                    # serialize the input data
                    annot_obj.serialize(self.fname_ie_data, self.data_dir)

    def extract_information(self, model='gpt-35-turbo', backend='openai-azure'):
        if backend == 'openai-azure':
            model_obj = OpenaiApiCall(model=model, temperature=0., max_tokens=4096)
        else:
            model_obj = HuggingfaceModel(model_name_or_path=model)

        if os.path.exists(os.path.join(self.output_dir, self.fname_ie_output)):
            existing_coll = OutputColl.read_existing_coll(self.fname_ie_output, self.output_dir)
        else:
            existing_coll = None

        prompt_obj = Prompt()

        for cur_inference_type in self.inference_types:
            prompt_preamble = prompt_obj.get_prompt_preamble(model_obj.model_name, cur_inference_type)
            for cur_inference_subtype, prompt in prompt_obj.yield_inference_subtype_prompt(cur_inference_type):
                for cur_doc_idx, cur_doc in self.collection.documents.items():
                    for section in self.sections_to_infer:
                        cur_text, __, __, __ = self.collection.get_annots_by_section_name(cur_doc, section)
                        cur_text = cur_text.replace('', ' ')
                        cur_example = cur_doc_idx + section + cur_inference_type + \
                                      cur_inference_subtype + model_obj.model_name + str(model_obj.temperature) + \
                                      prompt_preamble + prompt
                        if existing_coll and existing_coll.is_processed(cur_example):
                            print("Instance already processed; continuing.")
                            continue

                        cur_prompt = cur_text + prompt

                        # ipdb.set_trace()
                        # get model output
                        result = model_obj.get_response_text(cur_prompt, prompt_preamble)
                        if result is None:
                            print("Failed inference: ", cur_doc_idx, section, cur_inference_type,
                                  cur_inference_subtype)
                            print("Failed note text: ", cur_text)
                            print("Failed prompt: ", prompt)
                            print("Failed prompt preamble: ", prompt_preamble)
                            continue

                        print("Response: ", result)
                        output_obj = Output(cur_doc_idx, section, cur_text,
                                            cur_inference_type, cur_inference_subtype,
                                            model_obj.model_name, model_obj.temperature, prompt_preamble,
                                            prompt, result)
                        # save the result
                        output_obj.serialize(self.fname_ie_output, self.output_dir)


    @staticmethod
    def _format_entity_annot_for_eval(annotation, inference_subtype):

        annotation = [item.lower() for item in annotation]

        if inference_subtype.lower() in ['metastasis', 'remission', 'hospice', 'radiationtherapyname'] \
                and len(annotation):
            annotation = ['yes']

        if not len(annotation):
            annotation = ['none', 'no', 'n/a', 'unknown']

        return annotation

    @staticmethod
    def _format_tuple_annots_for_eval(tuple_list):
        relations = defaultdict(set)

        for cur_tuple in tuple_list:
            if type(cur_tuple) == CancerDiagnosis:
                # print("skipping first cancer diagnosis")
                continue
            tuple_primary_type = cur_tuple._fields[0]
            tuple_primary_val = cur_tuple[0]

            for i, (name, vals) in enumerate(cur_tuple._asdict().items()):
                if not i or name == 'AdditionalTesting':
                    # print("Skipping additional testing")
                    continue
                if len(vals) == 0:
                    vals = 'unknown'
                if type(vals) == set:
                    for val in vals:
                        relations[tuple_primary_type + ' ' + name].add(tuple_primary_val + ' ' + val)
                else:
                    relations[tuple_primary_type + ' ' + name].add(tuple_primary_val + ' ' + vals)

        if not len(relations):
            raise ValueError("Empty output set", tuple_list)

        return relations

    def evaluate(self):
        metrics = Metrics(tokenizer='default')
        scores = list()

        annots_coll = AnnotationColl.read_existing_coll(self.fname_ie_data, self.data_dir)
        output_coll = OutputColl.read_existing_coll(self.fname_ie_output, self.output_dir)

        for cur_output in output_coll.outputs: # cur_output is the list of all outputs generated by a model at once

            # matching annots are the list of all corresponding annotations
            matching_annots = annots_coll.get_annot_from_coll(cur_output.doc_idx, cur_output.section_name,
                                                              cur_output.inf_type, cur_output.inf_subtype)

            if not len(matching_annots):  # the annotation does not exist in the document
                if cur_output.inf_type == 'advanced_inference':
                    matching_annots = [
                        Annotation(
                            doc_idx=cur_output.doc_idx,
                            section_name=cur_output.section_name,
                            section_text=cur_output.section_text,
                            inf_type=cur_output.inf_type,
                            inf_subtype=cur_output.inf_subtype,
                            annotations=[inference_subtype_to_default_ne_dict[cur_output.inf_subtype]]
                        )
                    ]

            if len(matching_annots) > 1:
                raise ValueError("More than one annotation for this case", matching_annots)

            annot = matching_annots[0]

            if annot.inf_type == 'advanced_inference':
                annotations = self._format_tuple_annots_for_eval(annot.annotations)
                outputs = self._format_tuple_annots_for_eval(cur_output.output)

                # outputs is a dictionary {relation: [all outputs of that relation type]}
                for cur_pred_type, cur_pred_vals in outputs.items():
                    cur_pred_vals = [item.lower() for item in cur_pred_vals]
                    cur_annot_vals = annotations[cur_pred_type]
                    if not len(cur_annot_vals):
                        # may never be used; retaining regardless.
                        cur_annot_vals = ['none'] #, 'no', 'n/a', 'unknown']
                    else:
                        cur_annot_vals = [item.lower() for item in cur_annot_vals]

                    bleus, rouge1s = list(), list() # computing mean bleu and rouge for multi-set output
                    for cur_pred in cur_pred_vals:
                        bleu = metrics.compute_bleu_score(preds=[cur_pred],
                                                          references=[cur_annot_vals],
                                                          max_n=4,
                                                          smooth=True
                                                          )['bleu']
                        bleus.append(bleu)

                    for cur_annot in cur_annot_vals:
                        cur_rouges = []
                        for cur_pred in cur_pred_vals:
                            rouge1 = metrics.compute_rouge_score(preds=[cur_pred], references=[cur_annot],
                                                                 rouge_types=['rouge1']
                                                                 )['rouge1']
                            cur_rouges.append(rouge1)
                        rouge1s.append(np.max(cur_rouges))

                    em_p, em_r, em_f1 = metrics.compute_em_over_multiset_prec_recall_f1(cur_pred_vals,
                                                                                        cur_annot_vals)

                    cur_scores = {
                        'doc_idx': annot.doc_idx,
                        'section_name': annot.section_name,
                        'inference_type': annot.inf_type,
                        'inference_subtype': annot.inf_subtype,
                        'model_type': cur_output.model_type,
                        'temp': cur_output.temp,
                        'prompt': cur_output.prompt,
                        'cur_pred_type': cur_pred_type,
                        'bleu4': np.mean(bleus),
                        'rouge1': np.mean(rouge1s),
                        'em_prec': em_p,
                        'em_recall': em_r,
                        'em_f1': em_f1,
                    }
                    scores.append(cur_scores)

        scores = pd.DataFrame(scores)
        scores.to_csv(os.path.join(self.output_dir, self.fname_scores), index=False)
        self.aggregate_scores()

        return scores

    def aggregate_scores(self, fscores='agg_scores.csv'):
        df = pd.read_csv(os.path.join(self.output_dir, self.fname_scores))
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)

        agg_df = df.groupby(['inference_type', 'inference_subtype', 'cur_pred_type',
                         'annotator_idx', 'model_type', 'temp', 'prompt',
                         ]).agg(mean_bleu4=('bleu4', 'mean'),
                                 mean_rouge1=('rouge1', 'mean'),
                                 mean_em_prec=('em_prec', 'mean'),
                                 mean_em_recall=('em_recall', 'mean'),
                                 mean_em_f1=('em_f1', 'mean'),
                                 )
        agg_df.to_csv(os.path.join(self.output_dir, fscores))
        agg_df = agg_df.reset_index()
        agg_df = self._reorganize_scores_df(agg_df)
        agg_df.to_csv(os.path.join(self.output_dir, 'results_overall.csv'), index=False)

        # Breast cancer only
        path_obj = pathlib.Path('../data/all_annotated/breastca')
        bc_doc_idx = [os.path.splitext(os.path.basename(fname))[0] for fname in path_obj.rglob("*.txt")]
        bc_df = df[df['doc_idx'].isin(bc_doc_idx)]

        agg_bc_df = bc_df.groupby(['inference_type', 'inference_subtype', 'cur_pred_type',
                             'annotator_idx', 'model_type', 'temp', 'prompt',
                             ]).agg(mean_bleu4=('bleu4', 'mean'),
                                 mean_rouge1=('rouge1', 'mean'),
                                 mean_em_prec=('em_prec', 'mean'),
                                 mean_em_recall=('em_recall', 'mean'),
                                 mean_em_f1=('em_f1', 'mean'),
                                 )
        agg_bc_df = agg_bc_df.reset_index()
        agg_bc_df = self._reorganize_scores_df(agg_bc_df)
        agg_bc_df.to_csv(os.path.join(self.output_dir, 'results_bc.csv'), index=False)

        # Pancreatic cancer only
        pdac_df = df[~df['doc_idx'].isin(bc_df['doc_idx'].unique())]
        agg_pdac_df = pdac_df.groupby(['inference_type', 'inference_subtype', 'cur_pred_type',
                                    'annotator_idx', 'model_type', 'temp', 'prompt',
                                    ]).agg(mean_bleu4=('bleu4', 'mean'),
                                         mean_rouge1=('rouge1', 'mean'),
                                         mean_em_prec=('em_prec', 'mean'),
                                         mean_em_recall=('em_recall', 'mean'),
                                         mean_em_f1=('em_f1', 'mean'),
                                         mean_sem_prec=('sem_prec', 'mean'),
                                         mean_sem_recall=('sem_recall', 'mean'),
                                         mean_sem_f1=('sem_f1', 'mean'),
                                        )
        agg_pdac_df = agg_pdac_df.reset_index()
        agg_pdac_df = self._reorganize_scores_df(agg_pdac_df)
        agg_pdac_df.to_csv(os.path.join(self.output_dir, 'results_pdac.csv'), index=False)

    def _reorganize_scores_df(self, scores_df):
        def _modify_med_rel(row):
            if '_med_' in row['inference_subtype']:
                prefix = row['inference_subtype'].split('_')[0]
                return f'{prefix.title()}{row["cur_pred_type"]}'
            else:
                return row['cur_pred_type']

        def _modify_symptom_rel(row):
            if 'symptoms' in row['inference_subtype']:
                prefix = ''.join([subword.capitalize() for subword in row['inference_subtype'].split('_')])
                return f'{prefix} {row["cur_pred_type"].split()[1]}'
            else:
                return row['cur_pred_type']

        # Apply the function to each row in the DataFrame
        scores_df['cur_pred_type'] = scores_df.apply(_modify_med_rel, axis=1)
        scores_df['cur_pred_type'] = scores_df.apply(_modify_symptom_rel, axis=1)

        new_df = list()
        metrics = [col for col in scores_df.columns if 'mean' in col]
        for cur_rel in scores_df['cur_pred_type'].unique():
            cur_dict = dict()
            cur_dict['Relation'] = cur_rel
            for metric in metrics:
                for model in scores_df['model_type'].unique():
                    cur_df = scores_df[(scores_df['cur_pred_type'] == cur_rel) &
                                       (scores_df['model_type'] == model)
                                       ]
                    if 'flan-ul2' in model:
                        model = 'FLANUL2'
                    elif 'gpt-35-turbo' in model:
                        model = 'GPT3.5'
                    cur_dict[metric[5:].upper()+'_'+model.upper()] = round(cur_df[metric].item(), 2)
            new_df.append(cur_dict)

        new_df = pd.DataFrame(new_df)
        # Rename fields for plotting
        new_df['Relation'].replace('PrescribedMedicationName PotentialAdvEvent',
                                   'PrescribedMedicationName PotentialAdverseEvent', inplace=True)
        new_df['Relation'].replace('PrescribedMedicationName ConfirmedAdvEvent',
                                   'PrescribedMedicationName ConfirmedAdverseEvent', inplace=True)
        new_df['Relation'].replace('FutureMedicationName PotentialAdvEvent',
                                   'FutureMedicationName PotentialAdverseEvent', inplace=True)

        return new_df


def main(data_dir, model='gpt-35-turbo', do_eval=True):
    ie_extractor = OncInfoExtr(
        coll_dir=data_dir,
        inference_types=('advanced_inference',),  # important to add , in the end to avoid character iteration
        fdata='onc_pn_ie_data.csv',
        foutput='onc_pn_ie_output.csv',
        fscores='scores.csv',
        append_timestamp=True)

    ie_extractor.serialize_annotated_ie_dataset()

    if 'gpt-35' in model or 'gpt-4' in model:
        ie_extractor.extract_information(model=model, backend='openai-azure')
    else:
        ie_extractor.extract_information(model=model, backend='hf')

    if do_eval:
        ie_extractor.evaluate()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-annotations_path",
                        default='../data/coral/annotated/',
                        type=str,
                        required=False,
                        help="Annotated data path")

    parser.add_argument("-model",
                        default='gpt-35-turbo',
                        type=str,
                        required=False,
                        help="Model name")

    parser.add_argument("--evaluate", action="store_true", help="Evaluates the model")

    args = parser.parse_args()

    main(args.annotations_path, args.model, args.evaluate)
