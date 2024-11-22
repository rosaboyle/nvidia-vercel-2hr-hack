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