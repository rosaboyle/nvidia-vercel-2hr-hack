prompt_to_extract_toxins = """

You are a helpful assistant that extracts toxins from a given text.

The text is a report of a chemical.

Your task is to extract the toxins from the text.

You should return a list of toxins.


Each toxin should be a dictionary with the following keys:
- name
- sources
- health_effects
- related_diseases
- reference_context
- relevant_regulations

You should return a list of toxins.

and each toxin should be a dictionary with the above keys:

"""


text_to_url_text = """

You are a helpful assistant that extracts URLs from a given text.
The text is a report of a chemical.
Your task is to extract the URLs from the text. and also provide the text without the URLs.

Your output should be a JSON object with the following keys:
- urls: list of URLs found in the text
- text: text without the URLs

"""
