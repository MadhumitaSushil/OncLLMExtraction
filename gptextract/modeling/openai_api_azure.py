import os
import openai
from openai.error import RateLimitError
import backoff


class OpenaiApiCall:
    def __init__(self, model='gpt-35-turbo',
                 temperature=0., max_tokens=512, append_prompt=False, num_completions=1):
        openai.api_type = "azure"
        openai.api_base = os.getenv("OPENAI_RESOURCE_ENDPOINT")
        openai.api_version = "2023-03-15-preview"
        openai.api_key = os.getenv("OPENAI_API_KEY")

        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.append_prompt = append_prompt
        self.num_completions = num_completions

    @backoff.on_exception(backoff.expo, RateLimitError)
    def get_response(self, prompt_preamble, prompt):
        if 'davinci' in self.model_name:
            response = self._get_completion(prompt_preamble, prompt)
        elif self.model_name == 'gpt-35-turbo' or self.model_name == 'gpt-4':
            response = self._get_chat_completion(prompt_preamble, prompt)

        print(response)
        return response

    def _get_completion(self, prompt_preamble, prompt, **kwargs):
        prompt = prompt_preamble + prompt
        return openai.Completion.create(
                engine=self.model_name,
                temperature=self.temperature,
                prompt=prompt,
                max_tokens=self.max_tokens,
                echo=self.append_prompt,
                n=self.num_completions,
                **kwargs
            )

    def _get_chat_completion(self, prompt_preamble, prompt, **kwargs):
        return openai.ChatCompletion.create(
                engine=self.model_name,
                messages=[
                    {"role": "system",
                     "content": prompt_preamble,
                     },
                    {
                        "role": "user",
                        "content": prompt,
                    }],
                temperature=self.temperature,
                n=self.num_completions,
                **kwargs
            )

    def get_response_text(self, prompt, prompt_preamble=""):
        response = self.get_response(prompt_preamble, prompt)
        if 'davinci' in self.model_name:
            result = response['choices'][0]['text']
        elif self.model_name == 'gpt-35-turbo' or self.model_name == 'gpt-4':
            result = response['choices'][0]['message']['content']
        else:
            raise ValueError("Unsupported response model: ", self.model_name)

        return result
