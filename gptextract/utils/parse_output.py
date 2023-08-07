import ast
import re

from gptextract import *


def parse_entity_output(output):
    if '=' in output:  # output as variable = {str1, str2} or variable = [str1, str2]
        if len(output.split('=')) > 2:
            print("More than 1 = ", output)
        output = output.split('=')[-1].strip()

    elif ': [' in output or ': {' in output:  # output as variable: {str1, str2} or variable: [str1, str2]
        output = output.split(':')[-1].strip()

    if 'set' in output.lower():
        output = output.replace('set', '').replace('Set', '')

    if output.strip() == '' or output.strip() == 'N/A' or output.strip().lower().startswith('no ') or output.strip().lower().startswith('none '):
        return set()

    try:
        if "o'clock" in output:
            output = output.replace("o'clock", "o clock")
        # parse the output into real sets
        output = ast.literal_eval(output.strip())
        if output is None:
            return set()
        elif type(output) == list or type(output) == tuple:
            output = set(output)
        elif type(output) == dict:
            output = set(output.values())
        elif type(output) == str:
            output = {output}

        if None in output:
            output.remove(None)

        if '' in output:
            output.remove('')

    except Exception as e:
        print(output)
        print(e)

        # Went back to manually correct some malformed string sets after this step.
        return {output}

    return output


def parse_namedtuples(output, inference_subtype):

    def _remove_unescaped_quote(cur_output):
        # hacky lines of code to fix unescaped quotes in o'clock
        if "o'clock" in cur_output:
            cur_output = cur_output.replace("o'clock", "o clock")

        return cur_output

    parsed_outputs = list()

    # Adds newline between any space-separated tuples
    output = re.sub(r'(\))\s([A-Z]+)', r'\1\n\2', output)

    if "\n" in output:
        for cur_output in output.strip().split("\n"):
            cur_output = cur_output.strip()
            cur_output = _remove_unescaped_quote(cur_output).strip()

            if cur_output == '' or cur_output.upper() == 'N/A' or cur_output.lower().startswith(
                    'no ') or cur_output.lower().startswith('none ') or cur_output.lower() == 'unknown':
                parsed_outputs.append(inference_subtype_to_default_ne_dict[inference_subtype])
            else:
                try:
                    cur_output = eval(cur_output)
                    parsed_outputs.append(cur_output)
                except Exception as e:
                    print(e)
                    print("Exception in the output: ", cur_output, "Defaulting to unknown entry.")
                    parsed_outputs.append(inference_subtype_to_default_ne_dict[inference_subtype])

    else:
        output = output.strip()
        output = _remove_unescaped_quote(output)
        try:
            parsed_outputs.append(eval(output))
        except:
            print("Defaulting to unknown due to parsing error")
            parsed_outputs.append(inference_subtype_to_default_ne_dict[inference_subtype])

    return parsed_outputs
