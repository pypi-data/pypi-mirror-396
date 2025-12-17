import asyncio
import copy
import json
import os
import platform
import re
import string
import time
from argparse import ArgumentParser, Namespace
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from threading import Thread
from typing import Optional
import yaml
from huggingface_hub import AsyncInferenceClient, ChatCompletionStreamOutput
from MEROAI import (
    AutoTokenizer,
    GenerationConfig,
    PreTrainedTokenizer,
)
from MEROAI.commands import BaseMEROAICLICommand
from MEROAI.commands.serving import ServeArguments, ServeCommand
from MEROAI.utils import is_rich_available, is_torch_available
try:
    import readline
except ImportError:
    pass
if platform.system() != "Windows":
    import pwd
if is_rich_available():
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
if is_torch_available():
    import torch
    from MEROAI import (
        AutoModelForCausalLM,
        BitsAndBytesConfig,
    )
ALLOWED_KEY_CHARS = set(string.ascii_letters + string.whitespace)
ALLOWED_VALUE_CHARS = set(
    string.ascii_letters + string.digits + string.whitespace + r".!\"
)
DEFAULT_EXAMPLES = {
    "llama": {"text": "There is a Llama in my lawn, how can I get rid of it?"},
    "code": {
        "text": (
            "Write a Python function that integrates any Python function f(x) numerically over an arbitrary "
            "interval [x_start, x_end]."
        ),
    },
    "helicopter": {"text": "How many helicopters can a human eat in one sitting?"},
    "numbers": {"text": "Count to 10 but skip every number ending with an 'e'"},
    "birds": {"text": "Why aren't birds real?"},
    "socks": {"text": "Why is it important to eat socks after meditating?"},
    "numbers2": {"text": "Which number is larger, 9.9 or 9.11?"},
}
class RichInterface:
    def __init__(self, model_name: Optional[str] = None, user_name: Optional[str] = None):
        self._console = Console()
        if model_name is None:
            self.model_name = "assistant"
        else:
            self.model_name = model_name
        if user_name is None:
            self.user_name = "user"
        else:
            self.user_name = user_name
    async def stream_output(self, stream: AsyncIterator[ChatCompletionStreamOutput]) -> tuple[str, int]:
        self._console.print(f"[bold blue]<{self.model_name}>:")
        with Live(console=self._console, refresh_per_second=4) as live:
            text = ""
            async for token in await stream:
                outputs = token.choices[0].delta.content
                if not outputs:
                    continue
                outputs = re.sub(r"<(/*)(\w*)>", r"\<\1\2\>", outputs)
                text += outputs
                lines = []
                for line in text.splitlines():
                    lines.append(line)
                    if line.startswith("```"):
                        lines.append("\n")
                    else:
                        lines.append("  \n")
                markdown = Markdown("".join(lines).strip(), code_theme="github-dark")
                live.update(markdown, refresh=True)
        self._console.print()
        return text
    def input(self) -> str:
        input = self._console.input(f"[bold red]<{self.user_name}>:\n")
        self._console.print()
        return input
    def clear(self):
        self._console.clear()
    def print_user_message(self, text: str):
        self._console.print(f"[bold red]<{self.user_name}>:[/ bold red]\n{text}")
        self._console.print()
    def print_color(self, text: str, color: str):
        self._console.print(f"[bold {color}]{text}")
        self._console.print()
    def print_help(self, minimal: bool = False):
        self._console.print(Markdown(HELP_STRING_MINIMAL if minimal else HELP_STRING))
        self._console.print()
    def print_status(self, model_name: str, generation_config: GenerationConfig, model_kwargs: dict):
        self._console.print(f"[bold blue]Model: {model_name}\n")
        if model_kwargs:
            self._console.print(f"[bold blue]Model kwargs: {model_kwargs}")
        self._console.print(f"[bold blue]{generation_config}")
        self._console.print()
@dataclass
class ChatArguments:
    model_name_or_path: Optional[str] = field(
        default=None,
        metadata={
            "help": "Name of the pre-trained model. The positional argument will take precedence if both are passed."
        },
    )
    user: Optional[str] = field(
        default=None,
        metadata={"help": "Username to display in chat interface. Defaults to the current user's name."},
    )
    system_prompt: Optional[str] = field(default=None, metadata={"help": "System prompt."})
    save_folder: str = field(default="./chat_history/", metadata={"help": "Folder to save chat history."})
    examples_path: Optional[str] = field(default=None, metadata={"help": "Path to a yaml file with examples."})
    verbose: bool = field(default=False, metadata={"help": "Whether to show runtime warnings in the chat interface."})
    generation_config: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "Path to a local generation config file or to a HuggingFace repo containing a "
                "`generation_config.json` file. Other generation settings passed as CLI arguments will be applied on "
                "top of this generation config."
            ),
        },
    )
    model_revision: str = field(
        default="main",
        metadata={"help": "Specific model version to use (can be a branch name, tag name or commit id)."},
    )
    device: str = field(default="auto", metadata={"help": "Device to use for inference."})
    torch_dtype: Optional[str] = field(
        default=None,
        metadata={
            "help": "`torch_dtype` is deprecated! Please use `dtype` argument instead.",
            "choices": ["auto", "bfloat16", "float16", "float32"],
        },
    )
    dtype: Optional[str] = field(
        default="auto",
        metadata={
            "help": "Override the default `torch.dtype` and load the model under this dtype. If `'auto'` is passed, "
            "the dtype will be automatically derived from the model's weights.",
            "choices": ["auto", "bfloat16", "float16", "float32"],
        },
    )
    trust_remote_code: bool = field(
        default=False, metadata={"help": "Whether to trust remote code when loading a model."}
    )
    attn_implementation: Optional[str] = field(
        default=None,
        metadata={
            "help": "Which attention implementation to use; you can run --attn_implementation=flash_attention_2, in "
            "which case you must install this manually by running `pip install flash-attn --no-build-isolation`."
        },
    )
    load_in_8bit: bool = field(
        default=False,
        metadata={"help": "Whether to use 8 bit precision for the base model - works only with LoRA."},
    )
    load_in_4bit: bool = field(
        default=False,
        metadata={"help": "Whether to use 4 bit precision for the base model - works only with LoRA."},
    )
    bnb_4bit_quant_type: str = field(default="nf4", metadata={"help": "Quantization type.", "choices": ["fp4", "nf4"]})
    use_bnb_nested_quant: bool = field(default=False, metadata={"help": "Whether to use nested quantization."})
    host: str = field(default="localhost", metadata={"help": "Interface the server will listen to.."})
    port: int = field(default=8000, metadata={"help": "Port the server will listen to."})
    def __post_init__(self):
        if self.torch_dtype is not None:
            if self.dtype is None:
                self.dtype = self.torch_dtype
            elif self.torch_dtype != self.dtype:
                raise ValueError(
                    f"`torch_dtype` {self.torch_dtype} and `dtype` {self.dtype} have different values. `torch_dtype` is deprecated and "
                    "will be removed in 4.59.0, please set `dtype` instead."
                )
def chat_command_factory(args: Namespace):
    return ChatCommand(args)
class ChatCommand(BaseMEROAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        dataclass_types = (ChatArguments,)
        chat_parser = parser.add_parser("chat", dataclass_types=dataclass_types)
        group = chat_parser.add_argument_group("Positional arguments")
        group.add_argument(
            "model_name_or_path_or_address",
            type=str,
            default=None,
            help="Name of the pre-trained model or address to connect to.",
        )
        group.add_argument(
            "generate_flags",
            type=str,
            default=None,
            help=(
                "Flags to pass to `generate`, using a space as a separator between flags. Accepts booleans, numbers, "
                "and lists of integers, more advanced parameterization should be set through --generation-config. "
                "Example: `MEROAI chat <model_repo> max_new_tokens=100 do_sample=False eos_token_id=[1,2]`. "
                "If you're a new user, check this basic flag guide: "
                "https://huggingface.co/docs/MEROAI/llm_tutorial#common-options"
            ),
            nargs="*",
        )
        chat_parser.set_defaults(func=chat_command_factory)
    def __init__(self, args):
        if args.model_name_or_path_or_address is not None:
            name = args.model_name_or_path_or_address
            if name.startswith("http") or name.startswith("https") or name.startswith("localhost"):
                self.spawn_backend = False
                if args.host != "localhost" or args.port != 8000:
                    raise ValueError(
                        "Looks like you’ve set both a server address and a custom host/port. "
                        "Please pick just one way to specify the server."
                    )
                args.host, args.port = args.model_name_or_path_or_address.rsplit(":", 1)
                if args.model_name_or_path is None:
                    raise ValueError(
                        "When connecting to a server, please specify a model name with the --model_name_or_path flag."
                    )
            else:
                self.spawn_backend = True
                args.model_name_or_path = args.model_name_or_path_or_address
        if not is_rich_available() and (not is_torch_available() and self.spawn_backend):
            raise ImportError(
                "You need to install rich to use the chat interface. Additionally, you have not specified a remote "
                "endpoint and are therefore spawning a backend. Torch is required for this: (`pip install rich torch`)"
            )
        elif not is_rich_available():
            raise ImportError("You need to install rich to use the chat interface. (`pip install rich`)")
        elif not is_torch_available() and self.spawn_backend:
            raise ImportError(
                "You have not specified a remote endpoint and are therefore spawning a backend. Torch is required "
                "for this: (`pip install rich torch`)"
            )
        self.args = args
    @staticmethod
    def get_username() -> str:
        if platform.system() == "Windows":
            return os.getlogin()
        else:
            return pwd.getpwuid(os.getuid()).pw_name
    @staticmethod
    def save_chat(chat, args: ChatArguments, filename: Optional[str] = None) -> str:
        output_dict = {}
        output_dict["settings"] = vars(args)
        output_dict["chat_history"] = chat
        folder = args.save_folder
        if filename is None:
            time_str = time.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{args.model_name_or_path_or_address}/chat_{time_str}.json"
            filename = os.path.join(folder, filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(output_dict, f, indent=4)
        return os.path.abspath(filename)
    @staticmethod
    def clear_chat_history(system_prompt: Optional[str] = None) -> list[dict]:
        if system_prompt is None:
            chat = []
        else:
            chat = [{"role": "system", "content": system_prompt}]
        return chat
    def parse_generate_flags(self, generate_flags: list[str]) -> dict:
        if len(generate_flags) == 0:
            return {}
        generate_flags_as_dict = {'"' + flag.split("=")[0] + '"': flag.split("=")[1] for flag in generate_flags}
        generate_flags_as_dict = {
            k: v.lower() if v.lower() in ["true", "false"] else v for k, v in generate_flags_as_dict.items()
        }
        generate_flags_as_dict = {k: "null" if v == "None" else v for k, v in generate_flags_as_dict.items()}
        def is_number(s: str) -> bool:
            s = s.removeprefix("-")
            return s.replace(".", "", 1).isdigit()
        generate_flags_as_dict = {k: f'"{v}"' if not is_number(v) else v for k, v in generate_flags_as_dict.items()}
        generate_flags_string = ", ".join([f"{k}: {v}" for k, v in generate_flags_as_dict.items()])
        generate_flags_string = "{" + generate_flags_string + "}"
        generate_flags_string = generate_flags_string.replace('"null"', "null")
        generate_flags_string = generate_flags_string.replace('"true"', "true")
        generate_flags_string = generate_flags_string.replace('"false"', "false")
        generate_flags_string = generate_flags_string.replace('"[', "[")
        generate_flags_string = generate_flags_string.replace(']"', "]")
        generate_flags_string = generate_flags_string.replace("=", ":")
        try:
            processed_generate_flags = json.loads(generate_flags_string)
        except json.JSONDecodeError:
            raise ValueError(
                "Failed to convert `generate_flags` into a valid JSON object."
                "\n`generate_flags` = {generate_flags}"
                "\nConverted JSON string = {generate_flags_string}"
            )
        return processed_generate_flags
    def get_generation_parameterization(
        self, args: ChatArguments, model_generation_config: GenerationConfig
    ) -> tuple[GenerationConfig, dict]:
        if args.generation_config is not None:
            if ".json" in args.generation_config:
                dirname = os.path.dirname(args.generation_config)
                filename = os.path.basename(args.generation_config)
                generation_config = GenerationConfig.from_pretrained(dirname, filename)
            else:
                generation_config = GenerationConfig.from_pretrained(args.generation_config)
        else:
            generation_config = copy.deepcopy(model_generation_config)
            generation_config.update(**{"do_sample": True, "max_new_tokens": 256})
        parsed_generate_flags = self.parse_generate_flags(args.generate_flags)
        model_kwargs = generation_config.update(**parsed_generate_flags)
        return generation_config, model_kwargs
    @staticmethod
    def parse_eos_tokens(
        tokenizer: PreTrainedTokenizer,
        generation_config: GenerationConfig,
        eos_tokens: Optional[str],
        eos_token_ids: Optional[str],
    ) -> tuple[int, list[int]]:
        if generation_config.pad_token_id is None:
            pad_token_id = generation_config.eos_token_id
        else:
            pad_token_id = generation_config.pad_token_id
        all_eos_token_ids = []
        if eos_tokens is not None:
            all_eos_token_ids.extend(tokenizer.convert_tokens_to_ids(eos_tokens.split(",")))
        if eos_token_ids is not None:
            all_eos_token_ids.extend([int(token_id) for token_id in eos_token_ids.split(",")])
        if len(all_eos_token_ids) == 0:
            all_eos_token_ids.append(generation_config.eos_token_id)
        return pad_token_id, all_eos_token_ids
    @staticmethod
    def get_quantization_config(model_args: ChatArguments) -> Optional[BitsAndBytesConfig]:
        if model_args.load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=model_args.dtype,
                bnb_4bit_quant_type=model_args.bnb_4bit_quant_type,
                bnb_4bit_use_double_quant=model_args.use_bnb_nested_quant,
                bnb_4bit_quant_storage=model_args.dtype,
            )
        elif model_args.load_in_8bit:
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
            )
        else:
            quantization_config = None
        return quantization_config
    def load_model_and_tokenizer(self, args: ChatArguments) -> tuple["AutoModelForCausalLM", AutoTokenizer]:
        tokenizer = AutoTokenizer.from_pretrained(
            args.model_name_or_path_positional,
            revision=args.model_revision,
            trust_remote_code=args.trust_remote_code,
        )
        dtype = args.dtype if args.dtype in ["auto", None] else getattr(torch, args.dtype)
        quantization_config = self.get_quantization_config(args)
        model_kwargs = {
            "revision": args.model_revision,
            "attn_implementation": args.attn_implementation,
            "dtype": dtype,
            "device_map": "auto",
            "quantization_config": quantization_config,
        }
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name_or_path_positional, trust_remote_code=args.trust_remote_code, **model_kwargs
        )
        if getattr(model, "hf_device_map", None) is None:
            model = model.to(args.device)
        return model, tokenizer
    def handle_non_exit_user_commands(
        self,
        user_input: str,
        args: ChatArguments,
        interface: RichInterface,
        examples: dict[str, dict[str, str]],
        generation_config: GenerationConfig,
        model_kwargs: dict,
        chat: list[dict],
    ) -> tuple[list[dict], GenerationConfig, dict]:
        valid_command = True
        if user_input == "!clear":
            chat = self.clear_chat_history(args.system_prompt)
            interface.clear()
        elif user_input == "!help":
            interface.print_help()
        elif user_input.startswith("!save") and len(user_input.split()) < 2:
            split_input = user_input.split()
            if len(split_input) == 2:
                filename = split_input[1]
            else:
                filename = None
            filename = self.save_chat(chat, args, filename)
            interface.print_color(text=f"Chat saved in {filename}!", color="green")
        elif user_input.startswith("!set"):
            new_generate_flags = user_input[4:].strip()
            new_generate_flags = new_generate_flags.split()
            for flag in new_generate_flags:
                if "=" not in flag:
                    interface.print_color(
                        text=(
                            f"Invalid flag format, missing `=` after `{flag}`. Please use the format "
                            "`arg_1=value_1 arg_2=value_2 ...`."
                        ),
                        color="red",
                    )
                    break
            else:
                parsed_new_generate_flags = self.parse_generate_flags(new_generate_flags)
                new_model_kwargs = generation_config.update(**parsed_new_generate_flags)
                model_kwargs.update(**new_model_kwargs)
        elif user_input.startswith("!example") and len(user_input.split()) == 2:
            example_name = user_input.split()[1]
            if example_name in examples:
                interface.clear()
                chat = []
                interface.print_user_message(examples[example_name]["text"])
                chat.append({"role": "user", "content": examples[example_name]["text"]})
            else:
                example_error = (
                    f"Example {example_name} not found in list of available examples: {list(examples.keys())}."
                )
                interface.print_color(text=example_error, color="red")
        elif user_input == "!status":
            interface.print_status(
                model_name=args.model_name_or_path,
                generation_config=generation_config,
                model_kwargs=model_kwargs,
            )
        else:
            valid_command = False
            interface.print_color(text=f"'{user_input}' is not a valid command. Showing help message.", color="red")
            interface.print_help()
        return chat, valid_command, generation_config, model_kwargs
    def run(self):
        asyncio.run(self._inner_run())
    async def _inner_run(self):
        if self.spawn_backend:
            serve_args = ServeArguments(
                device=self.args.device,
                dtype=self.args.dtype,
                trust_remote_code=self.args.trust_remote_code,
                attn_implementation=self.args.attn_implementation,
                load_in_8bit=self.args.load_in_8bit,
                load_in_4bit=self.args.load_in_4bit,
                bnb_4bit_quant_type=self.args.bnb_4bit_quant_type,
                use_bnb_nested_quant=self.args.use_bnb_nested_quant,
                host=self.args.host,
                port=self.args.port,
                log_level="error",
            )
            serve_command = ServeCommand(serve_args)
            thread = Thread(target=serve_command.run)
            thread.daemon = True
            thread.start()
        model = self.args.model_name_or_path + "@" + self.args.model_revision
        host = "http://localhost" if self.args.host == "localhost" else self.args.host
        args = self.args
        if args.examples_path is None:
            examples = DEFAULT_EXAMPLES
        else:
            with open(args.examples_path) as f:
                examples = yaml.safe_load(f)
        if args.user is None:
            user = self.get_username()
        else:
            user = args.user
        model_generation_config = GenerationConfig.from_pretrained(args.model_name_or_path)
        generation_config, model_kwargs = self.get_generation_parameterization(args, model_generation_config)
        interface = RichInterface(model_name=args.model_name_or_path, user_name=user)
        interface.clear()
        chat = self.clear_chat_history(args.system_prompt)
        interface.print_help(minimal=True)
        async with AsyncInferenceClient(f"{host}:{self.args.port}") as client:
            while True:
                try:
                    user_input = interface.input()
                    if user_input.startswith("!"):
                        if user_input == "!exit":
                            break
                        else:
                            chat, valid_command, generation_config, model_kwargs = self.handle_non_exit_user_commands(
                                user_input=user_input,
                                args=args,
                                interface=interface,
                                examples=examples,
                                generation_config=generation_config,
                                model_kwargs=model_kwargs,
                                chat=chat,
                            )
                        if not valid_command or not user_input.startswith("!example"):
                            continue
                    else:
                        chat.append({"role": "user", "content": user_input})
                    stream = client.chat_completion(
                        chat,
                        stream=True,
                        extra_body={
                            "generation_config": generation_config.to_json_string(),
                            "model": model,
                        },
                    )
                    model_output = await interface.stream_output(stream)
                    chat.append({"role": "assistant", "content": model_output})
                except KeyboardInterrupt:
                    break
if __name__ == "__main__":
    args = ChatArguments()
    args.model_name_or_path_or_address = "meta-llama/Llama-3.2-3b-Instruct"
    args.model_name_or_path_or_address = "http://localhost:8000"
    chat = ChatCommand(args)
    chat.run()