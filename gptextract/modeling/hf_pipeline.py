import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM


class HuggingfaceModel:
    def __init__(self, model_name_or_path, temp=0., max_tokens=512, num_completions=1,
                 local_files_only=True):
        self.model_name = model_name_or_path
        self.temperature = temp
        self.max_tokens = max_tokens
        self.num_completions = num_completions

        if 't5' in self.model_name.lower() or 'ul2' in self.model_name.lower():
            self.model_type = 't5'
        elif 'gpt' in self.model_name.lower() or 'llama' in self.model_name.lower():
            self.model_type = 'gpt'

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Device: ", self.device)

        self.tokenizer = self.get_tokenizer(local_files_only)
        self.model = self.get_model(local_files_only)

    def get_tokenizer(self, local_files_only):
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=self.model_name,
                                                  local_files_only=local_files_only)
        return tokenizer

    def get_model(self, local_files_only):
        if self.model_type == 't5':
            # if torch.cuda.is_available() and 'flan-ul2' in self.model_name.lower():
            #     print("Loading seq to seq LM in 8 bit")
            #     model = AutoModelForSeq2SeqLM.from_pretrained(pretrained_model_name_or_path=self.model_name,
            #                                                  local_files_only=local_files_only,
            #                                                  load_in_8bit=True, device_map="auto")
            # else:
            print("Loading seq to seq LM in 16 bit")
            model = AutoModelForSeq2SeqLM.from_pretrained(pretrained_model_name_or_path=self.model_name,
                                                          local_files_only=local_files_only,
                                                          torch_dtype=torch.bfloat16, device_map="auto")

        elif self.model_type == 'gpt':
            # if torch.cuda.is_available():
            #     model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=self.model_name,
            #                                                  local_files_only=local_files_only,
            #                                                  load_in_8bit=True, device_map="auto")
            # else:
            print("Loading causal LM in 16 bit")
            model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=self.model_name,
                                                         local_files_only=local_files_only,
                                                         torch_dtype=torch.bfloat16, device_map="auto")
        else:
            raise ValueError("Unsupported model type:", self.model_type, " . Supported model types: (t5|ul2|gpt|llama)")

        # model = model.to(self.device)
        return model

    def get_response_text(self, prompt, prompt_preamble='', **kwargs):
        prompt = prompt_preamble + prompt
        tok_prompt = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        # tok_prompt.input_ids.to(self.device)
        output = self.model.generate(**tok_prompt, temperature=self.temperature,
                                     max_new_tokens=self.max_tokens,
                                     num_beams=self.num_completions, **kwargs)

        output = self.tokenizer.batch_decode(output, skip_special_tokens=True)
        output = output[0]
        return output
