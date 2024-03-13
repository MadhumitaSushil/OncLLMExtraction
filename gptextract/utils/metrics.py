import os
import evaluate
import transformers

from gptextract.modeling.openai_api_azure import OpenaiApiCall

# Somehow evaluate doesn't work for me without this:
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class Metrics:

    def __init__(self, tokenizer='default'):
        if tokenizer.lower() == 'gpt':
            self.tokenizer = transformers.OpenAIGPTTokenizerFast.from_pretrained("openai-gpt")
        elif tokenizer.lower() == 'default':
            self.tokenizer = None
        else:
            print("Supported tokenizers: (gpt|default). Using default.")
            self.tokenizer = None

        self.semantic_scorer = OpenaiApiCall(model='gpt-4')

    def compute_bleu_score(self, preds, references, max_n=1, smooth=False, **kwargs):
        """
        :param preds: list of all predictions
        :param references: list of list of all references for all predictions.
        :return: results
        """
        bleu = evaluate.load("bleu")

        if self.tokenizer is not None:
            results = bleu.compute(predictions=preds, references=references, max_order=max_n, smooth=smooth,
                                   tokenizer=self.tokenizer.tokenize, **kwargs
                                   )
        else:
            results = bleu.compute(predictions=preds, references=references, max_order=max_n, smooth=smooth,
                                   **kwargs)

        return results

    def compute_rouge_score(self, preds, references, rouge_types=None, **kwargs):
        """
        :param preds:  list of all predictions
        :param references: list of all references for all predictions (list of list)
        :param rouge_types: A list of rouge types to calculate
        :param kwargs: any additional supported parameters for metric computation
        :return: rouge score results
        """
        rouge = evaluate.load('rouge')
        if self.tokenizer is not None:
            results = rouge.compute(predictions=preds, references=references, rouge_types=rouge_types,
                                    tokenizer=self.tokenizer.tokenize, **kwargs
                                    )
        else:
            results = rouge.compute(predictions=preds, references=references, rouge_types=rouge_types,
                                    use_stemmer=True, **kwargs
                                    )
        return results

    def compute_em_accuracy(self, preds, references, **kwargs):
        """
        Exact match accuracy across set of values
        :param preds: list of all predictions
        :param references: list of list of all references for all predictions.
        :return: results

        """
        em_acc = evaluate.load('exact_match')
        return em_acc.compute(predictions=preds, references=references, **kwargs)

    def compute_em_F1(self, preds, references, pos_label=None, average="macro", **kwargs):
        """
        Macro or micro F1 score for classification values
        """
        f1_func = evaluate.load("f1")
        f1_score = f1_func.compute(references=references, predictions=preds, average=average, pos_label=pos_label,
                                   **kwargs)

        return f1_score

    def compute_em_over_multiset_prec_recall_f1(self, model_outputs, annots):
        model_outputs = set(model_outputs)
        annots = set(annots)

        TP = len(model_outputs.intersection(annots))
        FP = len(model_outputs - annots)
        FN = len(annots - model_outputs)

        precision = TP / (TP + FP)
        recall = TP / (TP + FN)

        if precision == 0. and recall == 0.:
            f1_score = 0.
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)

        return precision, recall, f1_score

