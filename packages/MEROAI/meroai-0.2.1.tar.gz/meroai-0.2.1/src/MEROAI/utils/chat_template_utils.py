import inspect
import json
import re
import types
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from inspect import isfunction
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from packaging import version
from . import logging
from .import_utils import is_jinja_available, is_torch_available, is_vision_available
logger = logging.get_logger(__name__)
if is_jinja_available():
    import jinja2
    from jinja2.ext import Extension
    from jinja2.sandbox import ImmutableSandboxedEnvironment
else:
    jinja2 = None
if is_vision_available():
    from PIL.Image import Image
if is_torch_available():
    from torch import Tensor
BASIC_TYPES = (int, float, str, bool, Any, type(None), ...)
description_re = re.compile(r"^(.*?)[\n\s]*(Args:|Returns:|Raises:|\Z)", re.DOTALL)
args_re = re.compile(r"\n\s*Args:\n\s*(.*?)[\n\s]*(Returns:|Raises:|\Z)", re.DOTALL)
args_split_re = re.compile(
    r"""
    (?:^|\n)                          # Start of string or newline
    \s*                               # Optional whitespace
    (\w+)                             # Parameter name (captured)
    \s*                               # Optional whitespace
    (?:\([^)]*\))?                    # Optional type hint in parentheses
    \s*:\s*                           # Colon separator
    (.+?)                             # Description (captured, non-greedy)
    (?=\n\s*\w+\s*(?:\([^)]*\))?\s*:|$)  # Lookahead for next param or end
    """,
    re.DOTALL | re.VERBOSE,
)
returns_re = re.compile(r"\n\s*Returns:\n\s*(.*?)[\n\s]*(Raises:|\Z)", re.DOTALL)
class TypeHintParsingException(Exception):
    pass
class DocstringParsingException(Exception):
    pass
def _get_json_schema_type(param_type: type) -> dict[str, str]:
    type_mapping = {
        int: {"type": "integer"},
        float: {"type": "number"},
        str: {"type": "string"},
        bool: {"type": "boolean"},
        type(None): {"type": "null"},
        Any: {},
    }
    if is_vision_available():
        type_mapping[Image] = {"type": "image"}
    if is_torch_available():
        type_mapping[Tensor] = {"type": "audio"}
    return type_mapping.get(param_type, {"type": "object"})
def _parse_type_hint(hint: str) -> dict:
    origin = get_origin(hint)
    args = get_args(hint)
    if origin is None:
        try:
            return _get_json_schema_type(hint)
        except KeyError:
            raise TypeHintParsingException(
                "Couldn't parse this type hint, likely due to a custom class or object: ", hint
            )
    elif origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        subtypes = [_parse_type_hint(t) for t in args if t is not type(None)]
        if len(subtypes) == 1:
            return_dict = subtypes[0]
        elif all(isinstance(subtype["type"], str) for subtype in subtypes):
            return_dict = {"type": sorted([subtype["type"] for subtype in subtypes])}
        else:
            return_dict = {"anyOf": subtypes}
        if type(None) in args:
            return_dict["nullable"] = True
        return return_dict
    elif origin is Literal and len(args) > 0:
        LITERAL_TYPES = (int, float, str, bool, type(None))
        args_types = []
        for arg in args:
            if type(arg) not in LITERAL_TYPES:
                raise TypeHintParsingException("Only the valid python literals can be listed in typing.Literal.")
            arg_type = _get_json_schema_type(type(arg)).get("type")
            if arg_type is not None and arg_type not in args_types:
                args_types.append(arg_type)
        return {
            "type": args_types.pop() if len(args_types) == 1 else list(args_types),
            "enum": list(args),
        }
    elif origin is list:
        if not args:
            return {"type": "array"}
        else:
            return {"type": "array", "items": _parse_type_hint(args[0])}
    elif origin is tuple:
        if not args:
            return {"type": "array"}
        if len(args) == 1:
            raise TypeHintParsingException(
                f"The type hint {str(hint).replace('typing.', '')} is a Tuple with a single element, which "
                "we do not automatically convert to JSON schema as it is rarely necessary. If this input can contain "
                "more than one element, we recommend "
                "using a list[] type instead, or if it really is a single element, remove the tuple[] wrapper and just "
                "pass the element directly."
            )
        if ... in args:
            raise TypeHintParsingException(
                "Conversion of '...' is not supported in Tuple type hints. "
                "Use list[] types for variable-length"
                " inputs instead."
            )
        return {"type": "array", "prefixItems": [_parse_type_hint(t) for t in args]}
    elif origin is dict:
        out = {"type": "object"}
        if len(args) == 2:
            out["additionalProperties"] = _parse_type_hint(args[1])
        return out
    raise TypeHintParsingException("Couldn't parse this type hint, likely due to a custom class or object: ", hint)
def _convert_type_hints_to_json_schema(func: Callable) -> dict:
    type_hints = get_type_hints(func)
    signature = inspect.signature(func)
    required = []
    for param_name, param in signature.parameters.items():
        if param.annotation == inspect.Parameter.empty:
            raise TypeHintParsingException(f"Argument {param.name} is missing a type hint in function {func.__name__}")
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    properties = {}
    for param_name, param_type in type_hints.items():
        properties[param_name] = _parse_type_hint(param_type)
    schema = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema
def parse_google_format_docstring(docstring: str) -> tuple[Optional[str], Optional[dict], Optional[str]]:
    description_match = description_re.search(docstring)
    args_match = args_re.search(docstring)
    returns_match = returns_re.search(docstring)
    description = description_match.group(1).strip() if description_match else None
    docstring_args = args_match.group(1).strip() if args_match else None
    returns = returns_match.group(1).strip() if returns_match else None
    if docstring_args is not None:
        docstring_args = "\n".join([line for line in docstring_args.split("\n") if line.strip()])
        matches = args_split_re.findall(docstring_args)
        args_dict = {match[0]: re.sub(r"\s*\n+\s*", " ", match[1].strip()) for match in matches}
    else:
        args_dict = {}
    return description, args_dict, returns
def get_json_schema(func: Callable) -> dict:
    doc = inspect.getdoc(func)
    if not doc:
        raise DocstringParsingException(
            f"Cannot generate JSON schema for {func.__name__} because it has no docstring!"
        )
    doc = doc.strip()
    main_doc, param_descriptions, return_doc = parse_google_format_docstring(doc)
    json_schema = _convert_type_hints_to_json_schema(func)
    if (return_dict := json_schema["properties"].pop("return", None)) is not None:
        if return_doc is not None:
            return_dict["description"] = return_doc
    for arg, schema in json_schema["properties"].items():
        if arg not in param_descriptions:
            raise DocstringParsingException(
                f"Cannot generate JSON schema for {func.__name__} because the docstring has no description for the argument '{arg}'"
            )
        desc = param_descriptions[arg]
        enum_choices = re.search(r"\(choices:\s*(.*?)\)\s*$", desc, flags=re.IGNORECASE)
        if enum_choices:
            schema["enum"] = [c.strip() for c in json.loads(enum_choices.group(1))]
            desc = enum_choices.string[: enum_choices.start()].strip()
        schema["description"] = desc
    output = {"name": func.__name__, "description": main_doc, "parameters": json_schema}
    if return_dict is not None:
        output["return"] = return_dict
    return {"type": "function", "function": output}
def _render_with_assistant_indices(
    compiled_template, messages, tools, documents, add_generation_prompt, **template_kwargs
):
    rendered_blocks = []
    generation_indices = []
    with compiled_template.environment.activate_tracker(rendered_blocks, generation_indices):
        for block in compiled_template.generate(
            messages=messages,
            tools=tools,
            documents=documents,
            add_generation_prompt=add_generation_prompt,
            **template_kwargs,
        ):
            rendered_blocks.append(block)
        rendered_chat = "".join(rendered_blocks)
    return rendered_chat, generation_indices
@lru_cache
def _compile_jinja_template(chat_template):
    if not is_jinja_available():
        raise ImportError(
            "apply_chat_template requires jinja2 to be installed. Please install it using `pip install jinja2`."
        )
    class AssistantTracker(Extension):
        tags = {"generation"}
        def __init__(self, environment: ImmutableSandboxedEnvironment):
            super().__init__(environment)
            environment.extend(activate_tracker=self.activate_tracker)
            self._rendered_blocks = None
            self._generation_indices = None
        def parse(self, parser: jinja2.parser.Parser) -> jinja2.nodes.CallBlock:
            lineno = next(parser.stream).lineno
            body = parser.parse_statements(["name:endgeneration"], drop_needle=True)
            return jinja2.nodes.CallBlock(self.call_method("_generation_support"), [], [], body).set_lineno(lineno)
        @jinja2.pass_eval_context
        def _generation_support(self, context: jinja2.nodes.EvalContext, caller: jinja2.runtime.Macro) -> str:
            rv = caller()
            if self.is_active():
                start_index = len("".join(self._rendered_blocks))
                end_index = start_index + len(rv)
                self._generation_indices.append((start_index, end_index))
            return rv
        def is_active(self) -> bool:
            return self._rendered_blocks or self._generation_indices
        @contextmanager
        def activate_tracker(self, rendered_blocks: list[int], generation_indices: list[int]):
            try:
                if self.is_active():
                    raise ValueError("AssistantTracker should not be reused before closed")
                self._rendered_blocks = rendered_blocks
                self._generation_indices = generation_indices
                yield
            finally:
                self._rendered_blocks = None
                self._generation_indices = None
    if version.parse(jinja2.__version__) < version.parse("3.1.0"):
        raise ImportError(
            f"apply_chat_template requires jinja2>=3.1.0 to be installed. Your version is {jinja2.__version__}."
        )
    def raise_exception(message):
        raise jinja2.exceptions.TemplateError(message)
    def tojson(x, ensure_ascii=False, indent=None, separators=None, sort_keys=False):
        return json.dumps(x, ensure_ascii=ensure_ascii, indent=indent, separators=separators, sort_keys=sort_keys)
    def strftime_now(format):
        return datetime.now().strftime(format)
    jinja_env = ImmutableSandboxedEnvironment(
        trim_blocks=True, lstrip_blocks=True, extensions=[AssistantTracker, jinja2.ext.loopcontrols]
    )
    jinja_env.filters["tojson"] = tojson
    jinja_env.globals["raise_exception"] = raise_exception
    jinja_env.globals["strftime_now"] = strftime_now
    return jinja_env.from_string(chat_template)
def render_jinja_template(
    conversations: list[list[dict[str, str]]],
    tools: Optional[list[Union[dict, Callable]]] = None,
    documents: Optional[list[dict[str, str]]] = None,
    chat_template: Optional[str] = None,
    return_assistant_tokens_mask: bool = False,
    continue_final_message: bool = False,
    add_generation_prompt: bool = False,
    **kwargs,
) -> str:
    if return_assistant_tokens_mask and not re.search(r"\{\%-?\s*generation\s*-?\%\}", chat_template):
        logger.warning_once(
            "return_assistant_tokens_mask==True but chat template does not contain `{% generation %}` keyword."
        )
    compiled_template = _compile_jinja_template(chat_template)
    if tools is not None:
        tool_schemas = []
        for tool in tools:
            if isinstance(tool, dict):
                tool_schemas.append(tool)
            elif isfunction(tool):
                tool_schemas.append(get_json_schema(tool))
            else:
                raise ValueError(
                    "Tools should either be a JSON schema, or a callable function with type hints "
                    "and a docstring suitable for auto-conversion to a schema."
                )
    else:
        tool_schemas = None
    if documents is not None:
        for document in documents:
            if not isinstance(document, dict):
                raise TypeError("Documents should be a list of dicts with 'title' and 'text' keys!")
    rendered = []
    all_generation_indices = []
    continue_final_message_tag = "CONTINUE_FINAL_MESSAGE_TAG "
    for chat in conversations:
        if hasattr(chat, "messages"):
            chat = chat.messages
        if continue_final_message:
            chat = deepcopy(chat)
            final_message = chat[-1]["content"]
            if isinstance(final_message, (list, tuple)):
                for content_block in reversed(final_message):
                    if "text" in content_block:
                        final_message = content_block["text"]
                        content_block["text"] = content_block["text"] + continue_final_message_tag
                        break
                else:
                    raise ValueError(
                        "continue_final_message is set but we could not find any text to continue in the final message!"
                    )
            else:
                chat[-1]["content"] = chat[-1]["content"] + continue_final_message_tag
        if return_assistant_tokens_mask:
            rendered_chat, generation_indices = _render_with_assistant_indices(
                compiled_template=compiled_template,
                messages=chat,
                tools=tool_schemas,
                documents=documents,
                add_generation_prompt=add_generation_prompt,
                **kwargs,
            )
            all_generation_indices.append(generation_indices)
        else:
            rendered_chat = compiled_template.render(
                messages=chat,
                tools=tool_schemas,
                documents=documents,
                add_generation_prompt=add_generation_prompt,
                **kwargs,
            )
        if continue_final_message:
            if (final_message.strip() not in rendered_chat) or (
                continue_final_message_tag.strip() not in rendered_chat
            ):
                raise ValueError(
                    "continue_final_message is set but the final message does not appear in the chat after "
                    "applying the chat template! This can happen if the chat template deletes portions of "
                    "the final message. Please verify the chat template and final message in your chat to "
                    "ensure they are compatible."
                )
            tag_loc = rendered_chat.rindex(continue_final_message_tag.strip())
            if rendered_chat[tag_loc : tag_loc + len(continue_final_message_tag)] == continue_final_message_tag:
                rendered_chat = rendered_chat[:tag_loc]
            else:
                rendered_chat = rendered_chat[:tag_loc].rstrip()
        rendered.append(rendered_chat)
    return rendered, all_generation_indices