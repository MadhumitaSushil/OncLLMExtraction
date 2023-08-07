import evaluate
import transformers


class Metrics:

    def __init__(self, tokenizer='gpt'):
        if tokenizer.lower() == 'gpt':
            self.tokenizer = transformers.OpenAIGPTTokenizerFast.from_pretrained("openai-gpt")
        elif tokenizer.lower() == 'default':
            self.tokenizer = None
        else:
            print("Supported tokenizers: (gpt|default). Using default.")
            self.tokenizer = None

    def compute_bleu_score(self, preds, references, **kwargs):
        """
        :param preds: list of all predictions
        :param references: list of list of all references for all predictions.
        :return: results
        """
        bleu = evaluate.load("bleu")

        if self.tokenizer is not None:
            results = bleu.compute(predictions=preds, references=references, smooth=True,
                                   tokenizer=self.tokenizer.tokenize, **kwargs
                                   )
        else:
            results = bleu.compute(predictions=preds, references=references, smooth=True, **kwargs)

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
        f1_score = f1_func.compute(references=references, predictions=preds, average=average, pos_label=pos_label, **kwargs)

        return f1_score