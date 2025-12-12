from string import Template
from dotenv import load_dotenv
from pathlib import Path
from HowdenLLM.providers.provider_factory import ProviderFactory
from typing import Any
import hashlib
import json


class LLM:
    def __init__(self,
                 provider_and_model: str,
                 template: Template,
                 use_web_search_tool: bool,
                 system: str = None,
                 name: str = None
    ):
        super().__init__()
        self.input_params = {
            k: v
            for k, v in locals().items()
            if k not in ("self", "__class__", "__len__")
        }

        load_dotenv()
        self.provider_name = provider_and_model.split(":")[0].lower()
        self.model = provider_and_model.split(":")[1]
        self.template = template
        self.name: str = name
        self.system: str = system
        self.provider = ProviderFactory.create(self.provider_name)
        self.use_web_search_tool = use_web_search_tool
        self.hashed = self.compute_hash(self.input_params)

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_runs = 0

    def _count_tokens(self, text: str) -> int:
        """Try to count tokens with tiktoken; fallback to rough word count."""
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model(self.model)
            return len(enc.encode(text))
        except (KeyError, LookupError, AttributeError, ImportError):
            return len(text.split())

    def __call__(self, filepath: Path) -> str:
        """
        Execute one completion round and return:
        (output_text, input_token_count, output_token_count)
        """
        content = filepath.read_text(encoding="utf-8")
        prompt = self.template.substitute(content=content)

        # --- count input tokens ---
        input_text = f"{self.system or ''}\n{prompt}"
        input_tokens = self._count_tokens(input_text)

        # --- run model ---
        output = self.provider.complete(self.system, prompt, self.model, self.use_web_search_tool)

        # --- count output tokens ---
        output_tokens = self._count_tokens(output)

        # --- update totals ---
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_runs += 1
        print(f"[{self.name or 'LLM'}] "
              f"Input tokens: {input_tokens}, "
              f"Output tokens: {output_tokens}, "
              f"Total_input: {self.total_input_tokens}, "
              f"Total_output: {self.total_output_tokens}, "
              f"Total_input_average: {round(self.total_input_tokens / self.total_runs, 2)}, "
              f"Total_output_average: {round(self.total_output_tokens / self.total_runs, 2)}")

        return output

    def make_serializable(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (list, tuple, set)):
            return [self.make_serializable(v) for v in obj]
        if isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in sorted(obj.items())}
        if hasattr(obj, "__dict__"):
            return self.make_serializable(vars(obj))

        if isinstance(obj, Template):
            return obj.template  # return the actual template string

        return f"{type(obj).__name__}:{repr(obj)}"

    def compute_hash(self, parameter: dict) -> str:

        attrs = {
            k: v
            for k, v in parameter.items()
            if k != "hash"
               and not k.startswith("_")
               and k not in ("client", "provider")
        }
        serializable = self.make_serializable(attrs)
        attrs_str = json.dumps(serializable, sort_keys=True, ensure_ascii=True)
        hashed = hashlib.sha256(attrs_str.encode()).hexdigest()[:8]
        return hashed

    @staticmethod
    def _convert(obj) -> str:
        return str(obj)

    def write_json_hyperparameter(self, folder_file_path: Path) -> None:
        folder_file_path.write_text(
            json.dumps(self.make_serializable(self.input_params),
                default=self._convert,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )


class LLMSwitch:
    """
    A class that inspects a file to determine which LLM instance to invoke based on file content.
    Changes made to this class by Casper 19/11-25
    """
    def __init__(self, LLMs: list[LLM], name: str, json_key: str = None) -> None:
        """
        Parameters
        ----------
        LLMs : list[LLM]
            A list of LLM objects that may be invoked based on the file content.
        json_key : str, optional
            Key into a json file. If provided, the file passed to ``__call__`` must be a JSON file.
        """
        self.LLMS = LLMs
        self.hashed = self.compute_hash({"json_key":json_key, "hashed": [llm.hashed for llm in LLMs]})
        self.input_parameter = {llm.name: llm.input_params for llm in LLMs}
        self.json_key = json_key
        self.name = name

    def _get_json_content(self, filepath: Path) -> str:
        """
        Load and return content from a JSON file using the configured JSON key.

        Parameters
        ----------
        filepath : Path
            Path to the JSON file from which to extract the content.
        Returns
        -------
        str
            The extracted content from the JSON file using ``self.json_key``.
        Raises
        ------
        SystemExit
            If ``filepath`` does not refer to a JSON file.
        """
        if filepath.suffix == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)[self.json_key]
        else:
            print(f"File: {filepath} is not a json file")
            exit(1)

    def __call__(self, filepath: Path, data_path: Path) -> str:
        """
        Reads a file to determine which of the provided LLM objects to call. The method checks each model in
    `   self.LLMS` and calls the first model whose `name` appears in the content.

        Parameters
        ----------
        filepath : Path
            Path to the file to be processed. Must be a JSON or Markdown file.
        data_path : Path
            Path to the directory or file containing additional data required by the invoked model.
        Returns
        -------
        str
            The output returned by the selected model. If no model is found, an empty string is returned.
        Raises
        ------
        SystemExit
            If `filepath` has an unsupported file extension.
        """
        if self.json_key:
            content = self._get_json_content(filepath)
        elif filepath.suffix == ".md":
            content = filepath.read_text(encoding="utf-8")
        else:
            print(f"{filepath} is of unsupported file type")
            exit(1)
        result = ""

        for model in self.LLMS:
            if model.name in content:
                result = model(data_path)
        return result

    def make_serializable(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (list, tuple, set)):
            return [self.make_serializable(v) for v in obj]
        if isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in sorted(obj.items())}
        if hasattr(obj, "__dict__"):
            return self.make_serializable(vars(obj))

        if isinstance(obj, Template):
            return obj.template  # return the actual template string

        return f"{type(obj).__name__}:{repr(obj)}"


    def compute_hash(self, parameter: dict) -> str:

        attrs = {
            k: v
            for k, v in parameter.items()
            if k != "hash"
               and not k.startswith("_")
               and k not in ("client", "provider")
        }
        serializable = self.make_serializable(attrs)
        attrs_str = json.dumps(serializable, sort_keys=True, ensure_ascii=True)
        hashed = hashlib.sha256(attrs_str.encode()).hexdigest()[:8]
        return hashed

    @staticmethod
    def _convert(obj) -> str:
        return str(obj)

    def write_json_hyperparameter(self, folder_file_path: Path) -> None:
        folder_file_path.write_text(
            json.dumps(
                self.make_serializable(self.input_parameter),
                default=self._convert,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )
