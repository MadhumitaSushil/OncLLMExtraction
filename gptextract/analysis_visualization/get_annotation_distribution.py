import os
from collections import defaultdict

import matplotlib.pyplot as plt
import seaborn as sns


from gptextract.bratreader.brat import Collection


class CollectionAnalysis:
    def __init__(self, coll_dir, output_dir='../../output/'):
        self.collection = Collection.read_collection(coll_dir)

        self.temporal_rels = ('HappensAtOnDuring', 'BeginsOnOrAt', 'EndsOnOrAt', 'HappensBefore', 'HappensAfter',
                              'HappensOverlapping', 'Temporal')
        self.desc_rels = ('ConsumptionQuantityRel', 'SDoHDesc', 'LateralityOfSite', 'SiteOf', 'ResultOfTest',
                          'BiomarkerRel', 'ProcedureDesc', 'TumorDesc', 'TreatmentDesc', 'RegimenFor')
        self.adv_rels = ('TestOrProcedureReveals', 'TestOrProcedureConductedForProblem',
                         'TreatmentAdministeredForProblem', 'TreatmentDiscontinuedBecauseOf',
                         'ConditionOrTreatmentCausesProblem', 'NotUndergoneBecauseOf', 'InclusionCriteriaFor',
                         'ExclusionCriteriaFor')

        self.counter_dict = self.get_counter()

        self.output_dir = output_dir

    def get_counter(self):
        ent_counter = defaultdict(int)
        att_counter = defaultdict(int)
        temp_rel_counter = defaultdict(int)
        desc_rel_counter = defaultdict(int)
        adv_rel_counter = defaultdict(int)

        for cur_doc, doc_annots in self.collection.documents.items():
            for cur_ent in doc_annots.entities:
                ent_counter[cur_ent.type] += 1

            for cur_att in doc_annots.attributes:
                att_counter[cur_att.type + '-' + cur_att.val] += 1

            for cur_rel in doc_annots.relations:
                if cur_rel.type in self.desc_rels:
                    desc_rel_counter[cur_rel.type] += 1
                elif cur_rel.type in self.adv_rels:
                    adv_rel_counter[cur_rel.type] += 1
                elif cur_rel.type in self.temporal_rels:
                    temp_rel_counter[cur_rel.type] += 1
                else:
                    print("Relation type not matched: ", cur_rel.type)
                    continue

        return {
            'entity': ent_counter,
            'attribute': att_counter,
            'temporal relation': temp_rel_counter,
            'descriptive relation': desc_rel_counter,
            'advanced relation': adv_rel_counter,
        }

    def get_num_annots(self,):
        n_ents, n_atts, n_rels = 0, 0, 0

        n_ents += sum(self.counter_dict['entity'].values())
        n_atts += sum(self.counter_dict['attribute'].values())
        n_rels += sum(self.counter_dict['temporal relation'].values())
        n_rels += sum(self.counter_dict['descriptive relation'].values())
        n_rels += sum(self.counter_dict['advanced relation'].values())

        print("Total number of annotated entities: ", n_ents)
        print("Total number of annotated attributes: ", n_atts)
        print("Total number of annotated relations: ", n_rels)
        return n_ents, n_atts, n_rels

    def plot(self):
        ent_att_dict = {k: v for k, v in self.counter_dict.items() if 'relation' not in k}
        relations_dict = {k: v for k, v in self.counter_dict.items() if 'relation' in k}

        self._plot_from_dict(ent_att_dict, 'entities_attributes')
        self._plot_from_dict(relations_dict, 'relations')

    def _plot_from_dict(self, data_dicts, plot_type):
        sns.set_style("whitegrid")

        num_plots = len(data_dicts)
        if 'relation' in plot_type:
            fig, axs = plt.subplots(nrows=1, ncols=num_plots, figsize=(5 * num_plots, 5))
        else:
            fig, axs = plt.subplots(nrows=1, ncols=num_plots, figsize=(8 * num_plots, 16))

        for i, (dict_type, data_dict) in enumerate(data_dicts.items()):
            # Sort the data by values in descending order
            sorted_data = dict(sorted(data_dict.items(), key=lambda x: x[1], reverse=True))
            print(sorted_data)

            # Create a horizontal bar plot
            sns.barplot(x=list(sorted_data.values()),
                        y=list(sorted_data.keys()),
                        ax=axs[i],
                        color='#1ebbd7',
                        )

            axs[i].tick_params(labelsize=14)

            # Set the x-axis and y-axis labels and title
            axs[i].set_xlabel('Frequency', fontsize=14)
            axs[i].set_ylabel(dict_type.title(), fontsize=14)
            axs[i].set_title(dict_type.title() + ' annotations')

            axs[i].grid(True, axis='x', linewidth=0.2)

        # Save the plot
        plt.tight_layout(w_pad=6)
        plt.savefig(os.path.join(self.output_dir + plot_type + '_annot_distr.png'), dpi=300)


def main(coll_dir):
    coll = CollectionAnalysis(coll_dir)
    coll.get_num_annots()
    coll.plot()


if __name__ == '__main__':
    coll_dir = '../../data/all_annotated'
    main(coll_dir)
