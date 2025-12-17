import functools
import inspect
import re
import textwrap
import types
from collections import OrderedDict

PT_RETURN_INTRODUCTION = """
Returns:
    `{full_output_type}` or `tuple({full_output_type})`:
    A `{full_output_type}` or a tuple of `{full_output_type}` (if `return_dict=False` is passed or when `config.return_dict=False`)
"""

TF_RETURN_INTRODUCTION = """
Returns:
    `{full_output_type}` or `tuple({full_output_type})`:
    A `{full_output_type}` or a tuple of `{full_output_type}` (if `return_dict=False` is passed or when `config.return_dict=False`)
"""

FAKE_MODEL_DISCLAIMER = """
    <Tip warning={true}>
    This example uses a random model as the real model checkpoint is gated.
    </Tip>
"""

PT_SEQUENCE_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # Example for sequence classification
    >>> pass
    ```
"""

PT_QUESTION_ANSWERING_SAMPLE = """
Example:
    ```python
    >>> # Example for question answering
    >>> pass
    ```
"""

PT_TOKEN_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # Example for token classification
    >>> pass
    ```
"""

PT_MULTIPLE_CHOICE_SAMPLE = """
Example:
    ```python
    >>> # Example for multiple choice
    >>> pass
    ```
"""

PT_MASKED_LM_SAMPLE = """
Example:
    ```python
    >>> # Example for masked language modeling
    >>> pass
    ```
"""

PT_CAUSAL_LM_SAMPLE = """
Example:
    ```python
    >>> # Example for causal language modeling
    >>> pass
    ```
"""

PT_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # Example for base model
    >>> pass
    ```
"""

PT_SPEECH_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # Example for speech base model
    >>> pass
    ```
"""

PT_SPEECH_CTC_SAMPLE = """
Example:
    ```python
    >>> # Example for CTC speech model
    >>> pass
    ```
"""

PT_SPEECH_SEQ_CLASS_SAMPLE = """
Example:
    ```python
    >>> # Example for speech sequence classification
    >>> pass
    ```
"""

PT_SPEECH_FRAME_CLASS_SAMPLE = """
Example:
    ```python
    >>> # Example for speech frame classification
    >>> pass
    ```
"""

PT_SPEECH_XVECTOR_SAMPLE = """
Example:
    ```python
    >>> # Example for speech x-vector
    >>> pass
    ```
"""

PT_VISION_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # Example for vision base model
    >>> pass
    ```
"""

PT_VISION_SEQ_CLASS_SAMPLE = """
Example:
    ```python
    >>> # Example for vision sequence classification
    >>> pass
    ```
"""

TF_SEQUENCE_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for sequence classification
    >>> pass
    ```
"""

TF_QUESTION_ANSWERING_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for question answering
    >>> pass
    ```
"""

TF_TOKEN_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for token classification
    >>> pass
    ```
"""

TF_MULTIPLE_CHOICE_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for multiple choice
    >>> pass
    ```
"""

TF_MASKED_LM_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for masked LM
    >>> pass
    ```
"""

TF_CAUSAL_LM_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for causal LM
    >>> pass
    ```
"""

TF_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for base model
    >>> pass
    ```
"""

TF_SPEECH_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for speech base model
    >>> pass
    ```
"""

TF_SPEECH_CTC_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for CTC
    >>> pass
    ```
"""

TF_VISION_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for vision base model
    >>> pass
    ```
"""

TF_VISION_SEQ_CLASS_SAMPLE = """
Example:
    ```python
    >>> # TensorFlow example for vision classification
    >>> pass
    ```
"""

FLAX_SEQUENCE_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # Flax example for sequence classification
    >>> pass
    ```
"""

FLAX_QUESTION_ANSWERING_SAMPLE = """
Example:
    ```python
    >>> # Flax example for question answering
    >>> pass
    ```
"""

FLAX_TOKEN_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # Flax example for token classification
    >>> pass
    ```
"""

FLAX_MULTIPLE_CHOICE_SAMPLE = """
Example:
    ```python
    >>> # Flax example for multiple choice
    >>> pass
    ```
"""

FLAX_MASKED_LM_SAMPLE = """
Example:
    ```python
    >>> # Flax example for masked LM
    >>> pass
    ```
"""

FLAX_BASE_MODEL_SAMPLE = """
Example:
    ```python
    >>> # Flax example for base model
    >>> pass
    ```
"""

FLAX_CAUSAL_LM_SAMPLE = """
Example:
    ```python
    >>> # Flax example for causal LM
    >>> pass
    ```
"""

TEXT_TO_AUDIO_SPECTROGRAM_SAMPLE = """
Example:
    ```python
    >>> # Example for text to audio spectrogram
    >>> pass
    ```
"""

TEXT_TO_AUDIO_WAVEFORM_SAMPLE = """
Example:
    ```python
    >>> # Example for text to audio waveform
    >>> pass
    ```
"""

IMAGE_TEXT_TO_TEXT_GENERATION_SAMPLE = """
Example:
    ```python
    >>> # Example for image-text to text generation
    >>> pass
    ```
"""

IMAGE_TO_TEXT_SAMPLE = """
Example:
    ```python
    >>> # Example for image to text
    >>> pass
    ```
"""

VISUAL_QUESTION_ANSWERING_SAMPLE = """
Example:
    ```python
    >>> # Example for visual question answering
    >>> pass
    ```
"""

DEPTH_ESTIMATION_SAMPLE = """
Example:
    ```python
    >>> # Example for depth estimation
    >>> pass
    ```
"""

VIDEO_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # Example for video classification
    >>> pass
    ```
"""

ZERO_SHOT_IMAGE_CLASSIFICATION_SAMPLE = """
Example:
    ```python
    >>> # Example for zero-shot image classification
    >>> pass
    ```
"""

ZERO_SHOT_OBJECT_DETECTION_SAMPLE = """
Example:
    ```python
    >>> # Example for zero-shot object detection
    >>> pass
    ```
"""

OBJECT_DETECTION_SAMPLE = """
Example:
    ```python
    >>> # Example for object detection
    >>> pass
    ```
"""

IMAGE_SEGMENTATION_SAMPLE = """
Example:
    ```python
    >>> # Example for image segmentation
    >>> pass
    ```
"""

IMAGE_TO_IMAGE_SAMPLE = """
Example:
    ```python
    >>> # Example for image to image
    >>> pass
    ```
"""

IMAGE_FEATURE_EXTRACTION_SAMPLE = """
Example:
    ```python
    >>> # Example for image feature extraction
    >>> pass
    ```
"""

TEXT_GENERATION_SAMPLE = """
Example:
    ```python
    >>> # Example for text generation
    >>> pass
    ```
"""

TABLE_QUESTION_ANSWERING_SAMPLE = """
Example:
    ```python
    >>> # Example for table question answering
    >>> pass
    ```
"""

DOCUMENT_QUESTION_ANSWERING_SAMPLE = """
Example:
    ```python
    >>> # Example for document question answering
    >>> pass
    ```
"""

TEXT2TEXT_GENERATION_SAMPLE = """
Example:
    ```python
    >>> # Example for text2text generation
    >>> pass
    ```
"""

NEXT_SENTENCE_PREDICTION_SAMPLE = """
Example:
    ```python
    >>> # Example for next sentence prediction
    >>> pass
    ```
"""

FILL_MASK_SAMPLE = """
Example:
    ```python
    >>> # Example for fill mask
    >>> pass
    ```
"""

MASK_GENERATION_SAMPLE = """
Example:
    ```python
    >>> # Example for mask generation
    >>> pass
    ```
"""

PRETRAINING_SAMPLE = """
Example:
    ```python
    >>> # Example for pretraining
    >>> pass
    ```
"""

def get_docstring_indentation_level(func):
    if inspect.isclass(func):
        return 4
    source = inspect.getsource(func)
    first_line = source.splitlines()[0]
    function_def_level = len(first_line) - len(first_line.lstrip())
    return 4 + function_def_level
def add_start_docstrings(*docstr):
    def docstring_decorator(fn):
        fn.__doc__ = "".join(docstr) + (fn.__doc__ if fn.__doc__ is not None else "")
        return fn
    return docstring_decorator
def add_start_docstrings_to_model_forward(*docstr):
    def docstring_decorator(fn):
        class_name = f"[`{fn.__qualname__.split('.')[0]}`]"
        correct_indentation = get_docstring_indentation_level(fn)
        current_doc = fn.__doc__ if fn.__doc__ is not None else ""
        try:
            first_non_empty = next(line for line in current_doc.splitlines() if line.strip() != "")
            doc_indentation = len(first_non_empty) - len(first_non_empty.lstrip())
        except StopIteration:
            doc_indentation = correct_indentation
        docs = docstr
        if doc_indentation == 4 + correct_indentation:
            docs = [textwrap.indent(textwrap.dedent(doc), " " * correct_indentation) for doc in docstr]
            intro = textwrap.indent(textwrap.dedent(intro), " " * correct_indentation)
        docstring = "".join(docs) + current_doc
        fn.__doc__ = intro + docstring
        return fn
    return docstring_decorator
def add_end_docstrings(*docstr):
    def docstring_decorator(fn):
        fn.__doc__ = (fn.__doc__ if fn.__doc__ is not None else "") + "".join(docstr)
        return fn
    return docstring_decorator
def _get_indent(t):
    search = re.search(r"^(\s*)\S", t)
    return "" if search is None else search.groups()[0]
def _convert_output_args_doc(output_args_doc):
    indent = _get_indent(output_args_doc)
    blocks = []
    current_block = ""
    for line in output_args_doc.split("\n"):
        if _get_indent(line) == indent:
            if len(current_block) > 0:
                blocks.append(current_block[:-1])
            current_block = f"{line}\n"
        else:
            current_block += f"{line[2:]}\n"
    blocks.append(current_block[:-1])
    for i in range(len(blocks)):
        blocks[i] = re.sub(r"^(\s+)(\S+)(\s+)", r"\1- **\2**\3", blocks[i])
        blocks[i] = re.sub(r":\s*\n\s*(\S)", r" -- \1", blocks[i])
    return "\n".join(blocks)
def _prepare_output_docstrings(output_type, config_class, min_indent=None, add_intro=True):
    output_docstring = output_type.__doc__
    params_docstring = None
    if output_docstring is not None:
        lines = output_docstring.split("\n")
        i = 0
        while i < len(lines) and re.search(r"^\s*(Args|Parameters):\s*$", lines[i]) is None:
            i += 1
        if i < len(lines):
            params_docstring = "\n".join(lines[(i + 1) :])
            params_docstring = _convert_output_args_doc(params_docstring)
        elif add_intro:
            raise ValueError(
                f"No `Args` or `Parameters` section is found in the docstring of `{output_type.__name__}`. Make sure it has "
                "docstring and contain either `Args` or `Parameters`."
            )
    if add_intro:
        full_output_type = f"{output_type.__module__}.{output_type.__name__}"
        intro = TF_RETURN_INTRODUCTION if output_type.__name__.startswith("TF") else PT_RETURN_INTRODUCTION
        intro = intro.format(full_output_type=full_output_type, config_class=config_class)
    else:
        full_output_type = str(output_type)
        intro = f"\nReturns:\n    `{full_output_type}`"
        if params_docstring is not None:
            intro += ":\n"
    result = intro
    if params_docstring is not None:
        result += params_docstring
    if min_indent is not None:
        lines = result.split("\n")
        i = 0
        while len(lines[i]) == 0:
            i += 1
        indent = len(_get_indent(lines[i]))
        if indent < min_indent:
            to_add = " " * (min_indent - indent)
            lines = [(f"{to_add}{line}" if len(line) > 0 else line) for line in lines]
            result = "\n".join(lines)
    return result
PT_SAMPLE_DOCSTRINGS = {
    "SequenceClassification": PT_SEQUENCE_CLASSIFICATION_SAMPLE,
    "QuestionAnswering": PT_QUESTION_ANSWERING_SAMPLE,
    "TokenClassification": PT_TOKEN_CLASSIFICATION_SAMPLE,
    "MultipleChoice": PT_MULTIPLE_CHOICE_SAMPLE,
    "MaskedLM": PT_MASKED_LM_SAMPLE,
    "LMHead": PT_CAUSAL_LM_SAMPLE,
    "BaseModel": PT_BASE_MODEL_SAMPLE,
    "SpeechBaseModel": PT_SPEECH_BASE_MODEL_SAMPLE,
    "CTC": PT_SPEECH_CTC_SAMPLE,
    "AudioClassification": PT_SPEECH_SEQ_CLASS_SAMPLE,
    "AudioFrameClassification": PT_SPEECH_FRAME_CLASS_SAMPLE,
    "AudioXVector": PT_SPEECH_XVECTOR_SAMPLE,
    "VisionBaseModel": PT_VISION_BASE_MODEL_SAMPLE,
    "ImageClassification": PT_VISION_SEQ_CLASS_SAMPLE,
}
AUDIO_FRAME_CLASSIFICATION_SAMPLE = PT_SPEECH_FRAME_CLASS_SAMPLE
AUDIO_XVECTOR_SAMPLE = PT_SPEECH_XVECTOR_SAMPLE
MULTIPLE_CHOICE_SAMPLE = PT_MULTIPLE_CHOICE_SAMPLE
IMAGE_CLASSIFICATION_SAMPLE = PT_VISION_SEQ_CLASS_SAMPLE
QUESTION_ANSWERING_SAMPLE = PT_QUESTION_ANSWERING_SAMPLE
TEXT_CLASSIFICATION_SAMPLE = PT_SEQUENCE_CLASSIFICATION_SAMPLE
TOKEN_CLASSIFICATION_SAMPLE = PT_TOKEN_CLASSIFICATION_SAMPLE
AUDIO_CLASSIFICATION_SAMPLE = PT_SPEECH_SEQ_CLASS_SAMPLE
AUTOMATIC_SPEECH_RECOGNITION_SAMPLE = PT_SPEECH_CTC_SAMPLE
PIPELINE_TASKS_TO_SAMPLE_DOCSTRINGS = OrderedDict(
    [
        ("text-to-audio-spectrogram", TEXT_TO_AUDIO_SPECTROGRAM_SAMPLE),
        ("text-to-audio-waveform", TEXT_TO_AUDIO_WAVEFORM_SAMPLE),
        ("automatic-speech-recognition", AUTOMATIC_SPEECH_RECOGNITION_SAMPLE),
        ("audio-frame-classification", AUDIO_FRAME_CLASSIFICATION_SAMPLE),
        ("audio-classification", AUDIO_CLASSIFICATION_SAMPLE),
        ("audio-xvector", AUDIO_XVECTOR_SAMPLE),
        ("image-text-to-text", IMAGE_TEXT_TO_TEXT_GENERATION_SAMPLE),
        ("image-to-text", IMAGE_TO_TEXT_SAMPLE),
        ("visual-question-answering", VISUAL_QUESTION_ANSWERING_SAMPLE),
        ("depth-estimation", DEPTH_ESTIMATION_SAMPLE),
        ("video-classification", VIDEO_CLASSIFICATION_SAMPLE),
        ("zero-shot-image-classification", ZERO_SHOT_IMAGE_CLASSIFICATION_SAMPLE),
        ("image-classification", IMAGE_CLASSIFICATION_SAMPLE),
        ("zero-shot-object-detection", ZERO_SHOT_OBJECT_DETECTION_SAMPLE),
        ("object-detection", OBJECT_DETECTION_SAMPLE),
        ("image-segmentation", IMAGE_SEGMENTATION_SAMPLE),
        ("image-to-image", IMAGE_TO_IMAGE_SAMPLE),
        ("image-feature-extraction", IMAGE_FEATURE_EXTRACTION_SAMPLE),
        ("text-generation", TEXT_GENERATION_SAMPLE),
        ("table-question-answering", TABLE_QUESTION_ANSWERING_SAMPLE),
        ("document-question-answering", DOCUMENT_QUESTION_ANSWERING_SAMPLE),
        ("question-answering", QUESTION_ANSWERING_SAMPLE),
        ("text2text-generation", TEXT2TEXT_GENERATION_SAMPLE),
        ("next-sentence-prediction", NEXT_SENTENCE_PREDICTION_SAMPLE),
        ("multiple-choice", MULTIPLE_CHOICE_SAMPLE),
        ("text-classification", TEXT_CLASSIFICATION_SAMPLE),
        ("token-classification", TOKEN_CLASSIFICATION_SAMPLE),
        ("fill-mask", FILL_MASK_SAMPLE),
        ("mask-generation", MASK_GENERATION_SAMPLE),
        ("pretraining", PRETRAINING_SAMPLE),
    ]
)
MODELS_TO_PIPELINE = OrderedDict(
    [
        ("MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING_NAMES", "text-to-audio-spectrogram"),
        ("MODEL_FOR_TEXT_TO_WAVEFORM_MAPPING_NAMES", "text-to-audio-waveform"),
        ("MODEL_FOR_SPEECH_SEQ_2_SEQ_MAPPING_NAMES", "automatic-speech-recognition"),
        ("MODEL_FOR_CTC_MAPPING_NAMES", "automatic-speech-recognition"),
        ("MODEL_FOR_AUDIO_FRAME_CLASSIFICATION_MAPPING_NAMES", "audio-frame-classification"),
        ("MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING_NAMES", "audio-classification"),
        ("MODEL_FOR_AUDIO_XVECTOR_MAPPING_NAMES", "audio-xvector"),
        ("MODEL_FOR_IMAGE_TEXT_TO_TEXT_MAPPING_NAMES", "image-text-to-text"),
        ("MODEL_FOR_VISION_2_SEQ_MAPPING_NAMES", "image-to-text"),
        ("MODEL_FOR_VISUAL_QUESTION_ANSWERING_MAPPING_NAMES", "visual-question-answering"),
        ("MODEL_FOR_DEPTH_ESTIMATION_MAPPING_NAMES", "depth-estimation"),
        ("MODEL_FOR_VIDEO_CLASSIFICATION_MAPPING_NAMES", "video-classification"),
        ("MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING_NAMES", "zero-shot-image-classification"),
        ("MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING_NAMES", "image-classification"),
        ("MODEL_FOR_ZERO_SHOT_OBJECT_DETECTION_MAPPING_NAMES", "zero-shot-object-detection"),
        ("MODEL_FOR_OBJECT_DETECTION_MAPPING_NAMES", "object-detection"),
        ("MODEL_FOR_IMAGE_SEGMENTATION_MAPPING_NAMES", "image-segmentation"),
        ("MODEL_FOR_IMAGE_TO_IMAGE_MAPPING_NAMES", "image-to-image"),
        ("MODEL_FOR_IMAGE_MAPPING_NAMES", "image-feature-extraction"),
        ("MODEL_FOR_CAUSAL_LM_MAPPING_NAMES", "text-generation"),
        ("MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING_NAMES", "table-question-answering"),
        ("MODEL_FOR_DOCUMENT_QUESTION_ANSWERING_MAPPING_NAMES", "document-question-answering"),
        ("MODEL_FOR_QUESTION_ANSWERING_MAPPING_NAMES", "question-answering"),
        ("MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES", "text2text-generation"),
        ("MODEL_FOR_NEXT_SENTENCE_PREDICTION_MAPPING_NAMES", "next-sentence-prediction"),
        ("MODEL_FOR_MULTIPLE_CHOICE_MAPPING_NAMES", "multiple-choice"),
        ("MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES", "text-classification"),
        ("MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING_NAMES", "token-classification"),
        ("MODEL_FOR_MASKED_LM_MAPPING_NAMES", "fill-mask"),
        ("MODEL_FOR_MASK_GENERATION_MAPPING_NAMES", "mask-generation"),
        ("MODEL_FOR_PRETRAINING_MAPPING_NAMES", "pretraining"),
    ]
)
TF_SAMPLE_DOCSTRINGS = {
    "SequenceClassification": TF_SEQUENCE_CLASSIFICATION_SAMPLE,
    "QuestionAnswering": TF_QUESTION_ANSWERING_SAMPLE,
    "TokenClassification": TF_TOKEN_CLASSIFICATION_SAMPLE,
    "MultipleChoice": TF_MULTIPLE_CHOICE_SAMPLE,
    "MaskedLM": TF_MASKED_LM_SAMPLE,
    "LMHead": TF_CAUSAL_LM_SAMPLE,
    "BaseModel": TF_BASE_MODEL_SAMPLE,
    "SpeechBaseModel": TF_SPEECH_BASE_MODEL_SAMPLE,
    "CTC": TF_SPEECH_CTC_SAMPLE,
    "VisionBaseModel": TF_VISION_BASE_MODEL_SAMPLE,
    "ImageClassification": TF_VISION_SEQ_CLASS_SAMPLE,
}
FLAX_SAMPLE_DOCSTRINGS = {
    "SequenceClassification": FLAX_SEQUENCE_CLASSIFICATION_SAMPLE,
    "QuestionAnswering": FLAX_QUESTION_ANSWERING_SAMPLE,
    "TokenClassification": FLAX_TOKEN_CLASSIFICATION_SAMPLE,
    "MultipleChoice": FLAX_MULTIPLE_CHOICE_SAMPLE,
    "MaskedLM": FLAX_MASKED_LM_SAMPLE,
    "BaseModel": FLAX_BASE_MODEL_SAMPLE,
    "LMHead": FLAX_CAUSAL_LM_SAMPLE,
}
def filter_outputs_from_example(docstring, **kwargs):
    for key, value in kwargs.items():
        if value is not None:
            continue
        doc_key = "{" + key + "}"
        docstring = re.sub(rf"\n([^\n]+)\n\s+{doc_key}\n", "\n", docstring)
    return docstring
def add_code_sample_docstrings(
    *docstr,
    processor_class=None,
    checkpoint=None,
    output_type=None,
    config_class=None,
    mask="[MASK]",
    qa_target_start_index=14,
    qa_target_end_index=15,
    model_cls=None,
    modality=None,
    expected_output=None,
    expected_loss=None,
    real_checkpoint=None,
    revision=None,
):
    def docstring_decorator(fn):
        model_class = fn.__qualname__.split(".")[0] if model_cls is None else model_cls
        if model_class[:2] == "TF":
            sample_docstrings = TF_SAMPLE_DOCSTRINGS
        elif model_class[:4] == "Flax":
            sample_docstrings = FLAX_SAMPLE_DOCSTRINGS
        else:
            sample_docstrings = PT_SAMPLE_DOCSTRINGS
        doc_kwargs = {
            "model_class": model_class,
            "processor_class": processor_class,
            "checkpoint": checkpoint,
            "mask": mask,
            "qa_target_start_index": qa_target_start_index,
            "qa_target_end_index": qa_target_end_index,
            "expected_output": expected_output,
            "expected_loss": expected_loss,
            "real_checkpoint": real_checkpoint,
            "fake_checkpoint": checkpoint,
            "true": "{true}",
        }
        if ("SequenceClassification" in model_class or "AudioClassification" in model_class) and modality == "audio":
            code_sample = sample_docstrings["AudioClassification"]
        elif "SequenceClassification" in model_class:
            code_sample = sample_docstrings["SequenceClassification"]
        elif "QuestionAnswering" in model_class:
            code_sample = sample_docstrings["QuestionAnswering"]
        elif "TokenClassification" in model_class:
            code_sample = sample_docstrings["TokenClassification"]
        elif "MultipleChoice" in model_class:
            code_sample = sample_docstrings["MultipleChoice"]
        elif "MaskedLM" in model_class or model_class in ["FlaubertWithLMHeadModel", "XLMWithLMHeadModel"]:
            code_sample = sample_docstrings["MaskedLM"]
        elif "LMHead" in model_class or "CausalLM" in model_class:
            code_sample = sample_docstrings["LMHead"]
        elif "CTC" in model_class:
            code_sample = sample_docstrings["CTC"]
        elif "AudioFrameClassification" in model_class:
            code_sample = sample_docstrings["AudioFrameClassification"]
        elif "XVector" in model_class and modality == "audio":
            code_sample = sample_docstrings["AudioXVector"]
        elif "Model" in model_class and modality == "audio":
            code_sample = sample_docstrings["SpeechBaseModel"]
        elif "Model" in model_class and modality == "vision":
            code_sample = sample_docstrings["VisionBaseModel"]
        elif "Model" in model_class or "Encoder" in model_class:
            code_sample = sample_docstrings["BaseModel"]
        elif "ImageClassification" in model_class:
            code_sample = sample_docstrings["ImageClassification"]
        else:
            raise ValueError(f"Docstring can't be built for model {model_class}")
        code_sample = filter_outputs_from_example(
            code_sample, expected_output=expected_output, expected_loss=expected_loss
        )
        if real_checkpoint is not None:
            code_sample = FAKE_MODEL_DISCLAIMER + code_sample
        func_doc = (fn.__doc__ or "") + "".join(docstr)
        output_doc = "" if output_type is None else _prepare_output_docstrings(output_type, config_class)
        built_doc = code_sample.format(**doc_kwargs)
        if revision is not None:
            if re.match(r"^refs/pr/\\d+", revision):
                raise ValueError(
                    f"The provided revision '{revision}' is incorrect. It should point to"
                    " a pull request reference on the hub like 'refs/pr/6'"
                )
            built_doc = built_doc.replace(
                f'from_pretrained("{checkpoint}")', f'from_pretrained("{checkpoint}", revision="{revision}")'
            )
        fn.__doc__ = func_doc + output_doc + built_doc
        return fn
    return docstring_decorator
def replace_return_docstrings(output_type=None, config_class=None):
    def docstring_decorator(fn):
        func_doc = fn.__doc__
        lines = func_doc.split("\n")
        i = 0
        while i < len(lines) and re.search(r"^\s*Returns?:\s*$", lines[i]) is None:
            i += 1
        if i < len(lines):
            indent = len(_get_indent(lines[i]))
            lines[i] = _prepare_output_docstrings(output_type, config_class, min_indent=indent)
            func_doc = "\n".join(lines)
        else:
            raise ValueError(
                f"The function {fn} should have an empty 'Return:' or 'Returns:' in its docstring as placeholder, "
                f"current docstring is:\n{func_doc}"
            )
        fn.__doc__ = func_doc
        return fn
    return docstring_decorator
def copy_func(f):
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g