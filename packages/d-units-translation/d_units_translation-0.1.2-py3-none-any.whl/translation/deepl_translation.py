from deep_translator import GoogleTranslator
import logging
import random
import time

MAX_CHARS=4900

def segment_text_by_token(text: str) -> list:
    """
    Splits the input text into segments based on white spaces.

    Args:
        text (str): The input string to be segmented.

    Returns:
        list: A list of text segments, each with a character length 
        less than or equal to MAX_CHARS.
    """
    text_list=[]
    text_words=text.split(" ")
    temp_text=""
    for w in text_words:
        if(len(temp_text)+len(w)>=MAX_CHARS):
            text_list.append(temp_text)
            temp_text=w
        else:
            temp_text=temp_text+ " " +w
    if(len(temp_text)>0):
        text_list.append(temp_text)
    return text_list

def translate_text_DeepTranslator(source: str , target: str, text: str, entry_id: str) -> str:
    """
    Translates a given text from a source language to a target language 
    using the GoogleTranslator from the DeepTranslator library.

    Args:
        source (str): Source language code.
        target (str): Target language code.
        text (str): Input text to be translated.
    
    Returns:
        str: Translated text.
    """
    try:
        translator = GoogleTranslator(source=source, target=target)
        translation = translator.translate(text)
        return translation
    
    except Exception as e:
        logging.error(f"DeepTranslator failed entry {entry_id}: {e}")
        return ""

def translate_text_with_deepl(config: dict, text: str, entry_id: str) -> str:
    """
    Translates a given text from a source language to a target language using a fallback loop 
    to handle large inputs and external request errors. If there is an error it will retry after
    a random amount of time (10,15) and will log an error.

    Args:
        config (dict): 
        text (str): Input text to be translated.
    
    Returns:
        str: Translated text.
    """
    if not text:
        return ""

    validate_translation=False
    while validate_translation is False:
        try:
            if (len(text) >= MAX_CHARS):
                text_list = segment_text_by_token(text)
                translation = ""
                for text in text_list:
                    translated_segment = translate_text_DeepTranslator(config["source_language"], config["target_language"], text, entry_id)
                    translation = translation + " " + translated_segment
            else:
                translation = translate_text_DeepTranslator(config["source_language"], config["target_language"], text, entry_id)

        except Exception as e:
            logging.error(f"Error in translate_text: {e}")
            time.sleep(random.randint(10,15))
        else:
            validate_translation=True

    return translation
