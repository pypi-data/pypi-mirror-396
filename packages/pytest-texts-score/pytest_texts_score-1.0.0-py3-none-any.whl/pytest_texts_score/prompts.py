"""
Prompt templates used by pytest-texts-score.
These prompts are carefully engineered to guide the LLM's behavior for question generation and evaluation. Modifying them may have significant impacts on the scoring results.
"""

QUESTION_PROMPT = """You are a meticulous text analysis assistant. Your task is to generate **yes/no questions** that reflect the information explicitly or implicitly contained in a given text.

### OBJECTIVE
These questions will be used to **compare the informational overlap** between texts. Therefore, your questions must:
- Be **factual**, **specific**, and **clearly answerable as YES** based only on the content of the provided text.
- Reflect the **relative importance and frequency** of information in the text.
- Cover the entire content.

### FORM & STYLE REQUIREMENTS
- **Every question must start with “Does the text”** and end with a **question mark**.
- Each question must be **true** (i.e., answerable with YES) according to the text.
- **Do not use pronouns** like "he", "she", "they", or "it". Always rephrase into specific entities.
- Questions must be as **specific as possible**, while including enough **context** to be meaningful if read independently.
- Create **one or more precise** questions for each distinct piece of meaningful information.
- Cover the entire text thoroughly—ensure that no sentence, clause, or relevant detail is left unaddressed.
- The number of questions for information must respect the importance of the information in the text. For example, if a list is given and the list is important in the context, then ask for each item in the list in separate questions.
- Maximise the number of questions to cover **every sentence** and the whole text fully.
- Return **only valid JSON** in this format:

{
 "1": "Does the text...?",
 "2": "Does the text...?",
 ...
 "200": "Does the text...?"
}
---

### EXAMPLES ###

#### Example 1:
Input:
Text: "Marie Curie discovered radium and polonium. She was the first woman to win a Nobel Prize."

Output:
{
 "1": "Does the text state that Marie Curie discovered radium?",
 "2": "Does the text state that Marie Curie discovered polonium?",
 "3": "Does the text say that Marie Curie was the first woman to win a Nobel Prize?",
...
 "50": "Does the text mention two elements discovered by Marie Curie?",
...
 "75": "Does the text say that a woman won a Nobel Prize?"
}


#### Example 2:
Input:
Text: "The Amazon rainforest is home to millions of species. It plays a critical role in regulating the Earth's climate."

Output:
{
 "1": "Does the text state that the Amazon rainforest is home to millions of species?",
 "2": "Does the text mention that the Amazon plays a critical role in climate regulation?",
 "3": "Does the text refer to the Amazon as a rainforest?",
...
 "50": "Does the text describe the Amazon rainforest to play a critical role?",
...
 "250": "Does the text suggest that the Amazon's ecosystem is significant for the Earth's climate?"
}

#### Example 3:
Input:
Text: "The Eiffel Tower was completed in 1889 for the World's Fair in Paris. It stands 300 meters tall."

Output:
{
 "1": "Does the text state that the Eiffel Tower was completed in 1889?",
 "2": "Does the text mention that the Eiffel Tower was built for the World's Fair in Paris?",
 "3": "Does the text say that the Eiffel Tower is 300 meters tall?",
...
 "50": "Does the text associate the Eiffel Tower with Paris?",
...
 "260": "Does the text provide the year the Eiffel Tower was finished?"
}


---

Use **double quotes only**, properly escaped with backslashes.
Only return the final output as a valid JSON object (no explanation or extra text) with questions starting with “Does the text” and ending with a **question mark**.
"""

ANSWER_PROMPT = """You are a precise and attentive assistant. Your task is to assess how closely a given **list of questions** corresponds to a provided text. Your evaluation will help compare how well different pieces of information are **supported by the text**.

# TASK

- You are an attentive and detailed assistant who objectively analyses text exactly according to instructions.
- Our ultimate goal is to compare the similarity of information between texts.
- Your goal is to help us with one particular task - answer the YES/NO questions **based purely on a given text**. You will proceed according to a specified criterion in the CRITERION section.
- Based on the criterion, you must answer in the format specified in the FORMAT section.
- Your answer must be truthful.
 
# CRITERION

Given a text, your goal is to answer each of the given YES/NO questions according to the text. Only use information found within the text as the basis of your answer.
You must return the text of the question and answer as a number.
Respond with a valid JSON in this format:
{
    "list": [
        {"question":"question1","answer":0},
        {"question":"question2","answer":0.5},
        ...
    ]
}
The answer must be 
1 - The information in the question is **fully and exactly present** in the text. There are no missing details and no contradictions.
0.5 - The information is partially present, but about half of it is missing, incorrect, or contradicted.
0 - The information is not present at all in the text.
0.75 - The information is mostly present, but with a small omission or minor inaccuracy. This is stronger than 0.5, but not fully correct like 1.
0.25 - The information is slightly present, but most of it is missing or inaccurate. This is stronger than 0, but weaker than 0.5.

Do not lower the score if the question is missing all the details. The score must be decreased only for missing information in the text from the relevant question.

### EXAMPLES ###

#### Example 1:
Input:
Text:

The company was founded in 2020 by Patrik.


Questions to answer:


{
    "1":"Does the text state that the company was founded in 2020?",
    "2":"Does the text state that the company was founded in 2010?",
    "3":"Does the text state that the company was founded in an even year?",
    "4":"Does the text state that the company was founded in 2020 and later merged in 2022?"
}


Output:
{
  "list": [
    {"question": "Does the text state that the company was founded in 2020?", "answer": 1},
    {"question": "Does the text state that the company was founded in 2010?", "answer": 0},
    {"question": "Does the text state that the company was founded in an even year?", "answer": 1},
    {"question": "Does the text state that the company was founded in 2020 and later merged in 2022?", "answer": 0.5}
  ]
}

#### Example 2:
Input:
Text:

A Graphics Processing Unit is a specialized electronic circuit designed to rapidly perform parallel mathematical computations.


Questions to answer:


{
    "1":"Does the text state that the Graphics Processing Unit is electronic circuit designed for calculation?",
    "2":"Does the text state that the Graphics Processing Unit is circuit used for playing games?",
    "3":"Does the text state that the Graphics Processing Unit is designed to perform computations?",
    "4":"Does the text state that the Graphics Processing Unit is used for playing games?",
}


Output:
{
  "list": [
    {"question": "Does the text state that the Graphics Processing Unit is electronic circuit designed for calculation?", "answer": 0.75},
    {"question": "Does the text state that the Graphics Processing Unit is circuit used for playing games?", "answer": 0.25},
    {"question": "Does the text state that the Graphics Processing Unit is designed to perform computations?", "answer": 1},
    {"question": "Does the text state that the Graphics Processing Unit is used for playing games?", "answer": 0}
  ]
}
---

Use **double quotes only**, properly escaped with backslashes.
Only return the final output as a valid JSON object (no explanation or extra text).
"""


def get_system_questions_prompt() -> str:
    """
    Get the system prompt for generating questions.

    This function returns the predefined system prompt that instructs the LLM
    on how to generate factual yes/no questions from a given text.

    :return: The question generation prompt string.
    :rtype: str
    """
    return QUESTION_PROMPT


def get_system_answers_prompt() -> str:
    """
    Get the system prompt for answering questions.

    This function returns the predefined system prompt that instructs the LLM
    on how to answer a list of questions based on a given text, using a numeric scoring system.

    :return: The question answering prompt string.
    :rtype: str
    """
    return ANSWER_PROMPT


def get_user_questions_prompt(text: str) -> str:
    """
    Create a user prompt for question generation.

    This function formats the user-provided text into a simple prompt
    that will be paired with the system question prompt.

    :param text: The text to generate questions from.
    :type text: str
    :return: The formatted user prompt string.
    :rtype: str
    """
    return f"""Text : "{text}\""""


def get_user_answers_prompt(answer_text: str, questions_text: str) -> str:
    """
    Create a user prompt for answering questions.

    This function formats the text and the questions into a single prompt
    that will be paired with the system answer prompt.

    :param answer_text: The text to use for answering the questions.
    :type answer_text: str
    :param questions_text: The JSON string of questions to be answered.
    :type questions_text: str
    :return: The formatted user prompt string.
    :rtype: str
    """
    return f"""Text:

{answer_text}


Questions to answer:


{questions_text}
"""
