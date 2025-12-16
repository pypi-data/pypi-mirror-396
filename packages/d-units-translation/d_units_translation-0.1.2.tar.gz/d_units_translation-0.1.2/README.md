# TranslationPipeline

A robust translating pipeline designed for multi-file support and integration with multiple translation sources, enabling users to efficiently process and translate large datasets or documents across various formats and languages into a JSON in the target language.

## Funcionalities
- Flexible Translation Methods: Easily switch between translation APIs and models.
- Extensible: Add new file formats or translation methods with minimal effort.
- JSON Output: Consolidate translations into a structured JSON for easy integration.

### Format Support:
- JSON
- JSONL
- XML
- TML
- CSV
- Hugging Face Datasets

### Translation Methods:
- Deep Translator (supports Google API)
- Models (Via transformers Pipeline)

## Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt`
- Internet access for Deep Translator or Hugging Face models

## How to use

1. install the package
```
pip install d-units-translation
```
2. Make a config.json following the configuration_example

3. Import the model and use the main function
```
from d_units_translation.pipeline import translation_dataset

translation_dataset("config.json")
```


## Configuration_example

### Hugging Face Dataset

|       Field       |  Type   |                                                          Description                                                           |                             Options                              |
|:-----------------:|:-------:|:------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------:|
|       name        | string  |                                          A short name for this configuration or task.                                          |                               Any                                |
|      dataset      | string  |                                                      The dataset source.                                                       |              Any dataset from hugging face datasets              |
|      version      | string  |                                            Version, split or subset of the dataset.                                            |                               Any                                |
|  backup_interval  | integer | Frequency  at which to save progress or checkpoints. A value of 5 means the system will back up after every 5 processed items. |                            Unlimited                             |
| columns2translate |  array  |                                     Specifies which dataset columns should be translated.                                      |                               Any                                |
|      col_id       | string  |                                      Name of the unique identifier column in the dataset                                       | Any, if the id doesn't exist it will assume the index as the id. |
|      reader       | string  |                                           Defines the type of dataset/file to read.                                            |                  "hugging_face" (in this case)                   |
|  source_language  | string  |                                        The original language code of the given dataset                                         |                  Depends on the choosen method                   |
|  target_language  | string  |                                              The target translation language code                                              |                  Depends on the choosen method                   |
|  backup_interval  | integer | Frequency  at which to save progress or checkpoints. A value of 5 means the system will back up after every 5 processed items. |                            Unlimited                             |

We need to choose the method we will use for translation, at the moment, we have two options:


| Field  |  Type  |                        Description                        | Options |
|:------:|:------:|:---------------------------------------------------------:|:-------:|
| method | string | Defines the method that will be used for the translation. | "deepL" |

or

|   Field    |  Type  |                                   Description                                    |       Options        |
|:----------:|:------:|:--------------------------------------------------------------------------------:|:--------------------:|
|   method   | string |            Defines the method that will be used for the translation.             |       "model"        |
|   model    | string | The translation model to be used. The model should support transformers pipeline |         Any          |
| max_tokens |  int   | Sets the maximum number of tokens the model can process per translation request. | Depends on the model |

Example:
```
{       
        "name": "bigbench",
        "dataset": "tasksource/bigbench",
        "version": "movie_recommendation",
        "backup_interval": 10,
        "columns2translate": ["inputs", "targets", "multiple_choice_targets"],
        "col_id":"idx",
        "reader":"hugging_face",
        "source_language": "en",
        "target_language": "pt-PT",
        "method": "model",
        "model": "rhaymison/opus-en-to-pt-translator", 
        "max_tokens":400
}
```

### CSV | JSON | JSONL | XML | TML 

|       Field       |  Type   |                                                          Description                                                           |                                       Options                                        |
|:-----------------:|:-------:|:------------------------------------------------------------------------------------------------------------------------------:|:------------------------------------------------------------------------------------:|
|       name        | string  |                                          A short name for this configuration or task.                                          |                                         Any                                          |
|   source_folder   | string  |                                             File folder that we want to translated                                             |                                         Any                                          |
|  backup_interval  | integer | Frequency  at which to save progress or checkpoints. A value of 5 means the system will back up after every 5 processed items. |                                      Unlimited                                       |
| columns2translate |  array  |                                     Specifies which dataset columns should be translated.                                      |                                         Any                                          |
|      col_id       | string  |                                      Name of the unique identifier column in the dataset                                       | Any, if this field doesn't exist it will assume the index as the id. <br> (Optional) |
|    split_name     | string  |                               Choose the name of the split that will show in the column "split"                                |                                         Any                                          |
|      reader       | string  |                                           Defines the type of dataset/file to read.                                            |                        "csv", "json", "jsonl", "xml" or "tml"                        |
|  source_language  | string  |                                        The original language code of the given dataset                                         |                            Depends on the choosen method                             |
|  target_language  | string  |                                              The target translation language code                                              |                            Depends on the choosen method                             |


                   
We need to choose the method we will use for translation, at the moment, we have two options:


| Field  |  Type  |                        Description                        | Options |
|:------:|:------:|:---------------------------------------------------------:|:-------:|
| method | string | Defines the method that will be used for the translation. | "deepL" |

or

|   Field    |  Type  |                                   Description                                    |       Options        |
|:----------:|:------:|:--------------------------------------------------------------------------------:|:--------------------:|
|   method   | string |            Defines the method that will be used for the translation.             |       "model"        |
|   model    | string | The translation model to be used. The model should support transformers pipeline |         Any          |
| max_tokens |  int   | Sets the maximum number of tokens the model can process per translation request. | Depends on the model |

Example:
```
{
    "name": "mc_task",
    "source_folder": "original/TruthfulQA",
    "backup_interval": 10,
    "columns2translate": ["Question", "Best Answer", "Correct Answers", "Incorrect Answers"],
    "split_name": "train",
    "reader": "csv",
    "source_language": "en",
    "target_language": "pt",
    "method": "deepL"
}
```

```
{
    "name": "databricks-dolly-15k",
    "source_folder": "original/databricks-dolly-15k",
    "backup_interval": 10,
    "columns2translate": ["instruction", "context", "response"],
    "split_name": "instruction",
    "reader": "jsonl",
    "source_language": "en",
    "target_language": "pt",
    "method": "model",
    "model": "rhaymison/opus-en-to-pt-translator",
    "max_tokens":400
}
```


## Contributors

| Name              | Role      | Contact                                                     |
|-------------------|-----------|-------------------------------------------------------------|
| **José Soares**   | Developer | [jose.p.soares@inesctec.pt](mailto:jose.p.soares@inesctec.pt)     |
| **Nuno Guimarães** | Advisor   | |

## License

MIT License

Copyright (c) 2025 INESC TEC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
