import json
import os
import re
import sys
import tempfile
import warnings
from concurrent import futures
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
from uuid import uuid4
import huggingface_hub
import requests
from huggingface_hub import (
    _CACHED_NO_EXIST,
    CommitOperationAdd,
    ModelCard,
    ModelCardData,
    constants,
    create_branch,
    create_commit,
    create_repo,
    hf_hub_download,
    hf_hub_url,
    list_repo_tree,
    snapshot_download,
    try_to_load_from_cache,
)
from huggingface_hub.file_download import REGEX_COMMIT_HASH, http_get
from huggingface_hub.utils import (
    EntryNotFoundError,
    GatedRepoError,
    HfHubHTTPError,
    LocalEntryNotFoundError,
    OfflineModeIsEnabled,
    RepositoryNotFoundError,
    RevisionNotFoundError,
    build_hf_headers,
    get_session,
    hf_raise_for_status,
)
from requests.exceptions import HTTPError
from . import __version__, logging
from .generic import working_or_temp_dir
from .import_utils import (
    ENV_VARS_TRUE_VALUES,
    _tf_version,
    _torch_version,
    is_tf_available,
    is_torch_available,
    is_training_run_on_sagemaker,
)
LEGACY_PROCESSOR_CHAT_TEMPLATE_FILE = "chat_template.json"
CHAT_TEMPLATE_FILE = "chat_template.jinja"
CHAT_TEMPLATE_DIR = "additional_chat_templates"
logger = logging.get_logger(__name__)
_is_offline_mode = huggingface_hub.constants.HF_HUB_OFFLINE
def is_offline_mode():
    return _is_offline_mode
torch_cache_home = os.getenv("TORCH_HOME", os.path.join(os.getenv("XDG_CACHE_HOME", "~/.cache"), "torch"))
default_cache_path = constants.default_cache_path
PYTORCH_PRETRAINED_BERT_CACHE = os.getenv("PYTORCH_PRETRAINED_BERT_CACHE", constants.HF_HUB_CACHE)
PYTORCH_MEROAI_CACHE = os.getenv("PYTORCH_MEROAI_CACHE", PYTORCH_PRETRAINED_BERT_CACHE)
MEROAI_CACHE = os.getenv("MEROAI_CACHE", PYTORCH_MEROAI_CACHE)
HF_MODULES_CACHE = os.getenv("HF_MODULES_CACHE", os.path.join(constants.HF_HOME, "modules"))
MEROAI_DYNAMIC_MODULE_NAME = "MEROAI_modules"
SESSION_ID = uuid4().hex
for key in ("PYTORCH_PRETRAINED_BERT_CACHE", "PYTORCH_MEROAI_CACHE", "MEROAI_CACHE"):
    if os.getenv(key) is not None:
        warnings.warn(
            f"Using `{key}` is deprecated and will be removed in v5 of MEROAI. Use `HF_HOME` instead.",
            FutureWarning,
        )
S3_BUCKET_PREFIX = "https://s3.amazonaws.com/models.huggingface.co/bert"
CLOUDFRONT_DISTRIB_PREFIX = "https://cdn.huggingface.co"
_staging_mode = os.environ.get("HUGGINGFACE_CO_STAGING", "NO").upper() in ENV_VARS_TRUE_VALUES
_default_endpoint = "https://hub-ci.huggingface.co" if _staging_mode else "https://huggingface.co"
HUGGINGFACE_CO_RESOLVE_ENDPOINT = _default_endpoint
if os.environ.get("HUGGINGFACE_CO_RESOLVE_ENDPOINT", None) is not None:
    warnings.warn(
        "Using the environment variable `HUGGINGFACE_CO_RESOLVE_ENDPOINT` is deprecated and will be removed in "
        "MEROAI v5. Use `HF_ENDPOINT` instead.",
        FutureWarning,
    )
    HUGGINGFACE_CO_RESOLVE_ENDPOINT = os.environ.get("HUGGINGFACE_CO_RESOLVE_ENDPOINT", None)
HUGGINGFACE_CO_RESOLVE_ENDPOINT = os.environ.get("HF_ENDPOINT", HUGGINGFACE_CO_RESOLVE_ENDPOINT)
HUGGINGFACE_CO_PREFIX = HUGGINGFACE_CO_RESOLVE_ENDPOINT + "/{model_id}/resolve/{revision}/{filename}"
HUGGINGFACE_CO_EXAMPLES_TELEMETRY = HUGGINGFACE_CO_RESOLVE_ENDPOINT + "/api/telemetry/examples"
def _get_cache_file_to_return(
    path_or_repo_id: str,
    full_filename: str,
    cache_dir: Union[str, Path, None] = None,
    revision: Optional[str] = None,
    repo_type: Optional[str] = None,
):
    resolved_file = try_to_load_from_cache(
        path_or_repo_id, full_filename, cache_dir=cache_dir, revision=revision, repo_type=repo_type
    )
    if resolved_file is not None and resolved_file != _CACHED_NO_EXIST:
        return resolved_file
    return None
def list_repo_templates(
    repo_id: str,
    *,
    local_files_only: bool,
    revision: Optional[str] = None,
    cache_dir: Optional[str] = None,
    token: Union[bool, str, None] = None,
) -> list[str]:
    if not local_files_only:
        try:
            return [
                entry.path.removeprefix(f"{CHAT_TEMPLATE_DIR}/")
                for entry in list_repo_tree(
                    repo_id=repo_id,
                    revision=revision,
                    path_in_repo=CHAT_TEMPLATE_DIR,
                    recursive=False,
                    token=token,
                )
                if entry.path.endswith(".jinja")
            ]
        except (GatedRepoError, RepositoryNotFoundError, RevisionNotFoundError):
            raise
        except (HTTPError, OfflineModeIsEnabled, requests.exceptions.ConnectionError):
            pass
    try:
        snapshot_dir = snapshot_download(
            repo_id=repo_id, revision=revision, cache_dir=cache_dir, local_files_only=True
        )
    except LocalEntryNotFoundError:
        return []
    templates_dir = Path(snapshot_dir, CHAT_TEMPLATE_DIR)
    if not templates_dir.is_dir():
        return []
    return [entry.stem for entry in templates_dir.iterdir() if entry.is_file() and entry.name.endswith(".jinja")]
def is_remote_url(url_or_filename):
    parsed = urlparse(url_or_filename)
    return parsed.scheme in ("http", "https")
def define_sagemaker_information():
    try:
        instance_data = requests.get(os.environ["ECS_CONTAINER_METADATA_URI"]).json()
        dlc_container_used = instance_data["Image"]
        dlc_tag = instance_data["Image"].split(":")[1]
    except Exception:
        dlc_container_used = None
        dlc_tag = None
    sagemaker_params = json.loads(os.getenv("SM_FRAMEWORK_PARAMS", "{}"))
    runs_distributed_training = "sagemaker_distributed_dataparallel_enabled" in sagemaker_params
    account_id = os.getenv("TRAINING_JOB_ARN").split(":")[4] if "TRAINING_JOB_ARN" in os.environ else None
    sagemaker_object = {
        "sm_framework": os.getenv("SM_FRAMEWORK_MODULE", None),
        "sm_region": os.getenv("AWS_REGION", None),
        "sm_number_gpu": os.getenv("SM_NUM_GPUS", "0"),
        "sm_number_cpu": os.getenv("SM_NUM_CPUS", "0"),
        "sm_distributed_training": runs_distributed_training,
        "sm_deep_learning_container": dlc_container_used,
        "sm_deep_learning_container_tag": dlc_tag,
        "sm_account_id": account_id,
    }
    return sagemaker_object
def http_user_agent(user_agent: Union[dict, str, None] = None) -> str:
    ua = f"MEROAI/{__version__}; python/{sys.version.split()[0]}; session_id/{SESSION_ID}"
    if is_torch_available():
        ua += f"; torch/{_torch_version}"
    if is_tf_available():
        ua += f"; tensorflow/{_tf_version}"
    if constants.HF_HUB_DISABLE_TELEMETRY:
        return ua + "; telemetry/off"
    if is_training_run_on_sagemaker():
        ua += "; " + "; ".join(f"{k}/{v}" for k, v in define_sagemaker_information().items())
    if os.environ.get("MEROAI_IS_CI", "").upper() in ENV_VARS_TRUE_VALUES:
        ua += "; is_ci/true"
    if isinstance(user_agent, dict):
        ua += "; " + "; ".join(f"{k}/{v}" for k, v in user_agent.items())
    elif isinstance(user_agent, str):
        ua += "; " + user_agent
    return ua
def extract_commit_hash(resolved_file: Optional[str], commit_hash: Optional[str]) -> Optional[str]:
    if resolved_file is None or commit_hash is not None:
        return commit_hash
    resolved_file = str(Path(resolved_file).as_posix())
    search = re.search(r"snapshots/([^/]+)/", resolved_file)
    if search is None:
        return None
    commit_hash = search.groups()[0]
    return commit_hash if REGEX_COMMIT_HASH.match(commit_hash) else None
def cached_file(
    path_or_repo_id: Union[str, os.PathLike],
    filename: str,
    **kwargs,
) -> Optional[str]:
    file = cached_files(path_or_repo_id=path_or_repo_id, filenames=[filename], **kwargs)
    file = file[0] if file is not None else file
    return file
def cached_files(
    path_or_repo_id: Union[str, os.PathLike],
    filenames: list[str],
    cache_dir: Optional[Union[str, os.PathLike]] = None,
    force_download: bool = False,
    resume_download: Optional[bool] = None,
    proxies: Optional[dict[str, str]] = None,
    token: Optional[Union[bool, str]] = None,
    revision: Optional[str] = None,
    local_files_only: bool = False,
    subfolder: str = "",
    repo_type: Optional[str] = None,
    user_agent: Optional[Union[str, dict[str, str]]] = None,
    _raise_exceptions_for_gated_repo: bool = True,
    _raise_exceptions_for_missing_entries: bool = True,
    _raise_exceptions_for_connection_errors: bool = True,
    _commit_hash: Optional[str] = None,
    **deprecated_kwargs,
) -> Optional[str]:
    use_auth_token = deprecated_kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn(
            "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
            FutureWarning,
        )
        if token is not None:
            raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    if is_offline_mode() and not local_files_only:
        logger.info("Offline mode: forcing local_files_only=True")
        local_files_only = True
    if subfolder is None:
        subfolder = ""
    full_filenames = [os.path.join(subfolder, file) for file in filenames]
    path_or_repo_id = str(path_or_repo_id)
    existing_files = []
    for filename in full_filenames:
        if os.path.isdir(path_or_repo_id):
            resolved_file = os.path.join(path_or_repo_id, filename)
            if not os.path.isfile(resolved_file):
                if _raise_exceptions_for_missing_entries and filename != os.path.join(subfolder, "config.json"):
                    revision_ = "main" if revision is None else revision
                    raise OSError(
                        f"{path_or_repo_id} does not appear to have a file named {filename}. Checkout "
                        f"'https://huggingface.co/{path_or_repo_id}/tree/{revision_}' for available files."
                    )
                else:
                    continue
            existing_files.append(resolved_file)
    if os.path.isdir(path_or_repo_id):
        return existing_files if existing_files else None
    if cache_dir is None:
        cache_dir = MEROAI_CACHE
    if isinstance(cache_dir, Path):
        cache_dir = str(cache_dir)
    existing_files = []
    file_counter = 0
    if _commit_hash is not None and not force_download:
        for filename in full_filenames:
            resolved_file = try_to_load_from_cache(
                path_or_repo_id, filename, cache_dir=cache_dir, revision=_commit_hash, repo_type=repo_type
            )
            if resolved_file is not None:
                if resolved_file is not _CACHED_NO_EXIST:
                    file_counter += 1
                    existing_files.append(resolved_file)
                elif not _raise_exceptions_for_missing_entries:
                    file_counter += 1
                else:
                    raise OSError(f"Could not locate {filename} inside {path_or_repo_id}.")
    if file_counter == len(full_filenames):
        return existing_files if len(existing_files) > 0 else None
    user_agent = http_user_agent(user_agent)
    try:
        if len(full_filenames) == 1:
            hf_hub_download(
                path_or_repo_id,
                filenames[0],
                subfolder=None if len(subfolder) == 0 else subfolder,
                repo_type=repo_type,
                revision=revision,
                cache_dir=cache_dir,
                user_agent=user_agent,
                force_download=force_download,
                proxies=proxies,
                resume_download=resume_download,
                token=token,
                local_files_only=local_files_only,
            )
        else:
            snapshot_download(
                path_or_repo_id,
                allow_patterns=full_filenames,
                repo_type=repo_type,
                revision=revision,
                cache_dir=cache_dir,
                user_agent=user_agent,
                force_download=force_download,
                proxies=proxies,
                resume_download=resume_download,
                token=token,
                local_files_only=local_files_only,
            )
    except Exception as e:
        if isinstance(e, RepositoryNotFoundError) and not isinstance(e, GatedRepoError):
            raise OSError(
                f"{path_or_repo_id} is not a local folder and is not a valid model identifier "
                "listed on 'https://huggingface.co/models'\nIf this is a private repository, make sure to pass a token "
                "having permission to this repo either by logging in with `hf auth login` or by passing "
                "`token=<your_token>`"
            ) from e
        elif isinstance(e, RevisionNotFoundError):
            raise OSError(
                f"{revision} is not a valid git identifier (branch name, tag name or commit id) that exists "
                "for this model name. Check the model page at "
                f"'https://huggingface.co/{path_or_repo_id}' for available revisions."
            ) from e
        elif isinstance(e, PermissionError):
            raise OSError(
                f"PermissionError at {e.filename} when downloading {path_or_repo_id}. "
                "Check cache directory permissions. Common causes: 1) another user is downloading the same model (please wait); "
                "2) a previous download was canceled and the lock file needs manual removal."
            ) from e
        resolved_files = [
            _get_cache_file_to_return(path_or_repo_id, filename, cache_dir, revision, repo_type)
            for filename in full_filenames
        ]
        if all(file is not None for file in resolved_files):
            return resolved_files
        if isinstance(e, GatedRepoError):
            if not _raise_exceptions_for_gated_repo:
                return None
            raise OSError(
                "You are trying to access a gated repo.\nMake sure to have access to it at "
                f"https://huggingface.co/{path_or_repo_id}.\n{str(e)}"
            ) from e
        elif isinstance(e, LocalEntryNotFoundError):
            if not _raise_exceptions_for_connection_errors:
                return None
            elif _raise_exceptions_for_missing_entries:
                raise OSError(
                    f"We couldn't connect to '{HUGGINGFACE_CO_RESOLVE_ENDPOINT}' to load the files, and couldn't find them in the"
                    f" cached files.\nCheck your internet connection or see how to run the library in offline mode at"
                    " 'https://huggingface.co/docs/MEROAI/installation#offline-mode'."
                ) from e
        elif isinstance(e, HTTPError) and not isinstance(e, EntryNotFoundError):
            if not _raise_exceptions_for_connection_errors:
                return None
            raise OSError(f"There was a specific connection error when trying to load {path_or_repo_id}:\n{e}") from e
        elif not isinstance(e, EntryNotFoundError):
            raise e
    resolved_files = [
        _get_cache_file_to_return(path_or_repo_id, filename, cache_dir, revision) for filename in full_filenames
    ]
    if any(file is None for file in resolved_files) and _raise_exceptions_for_missing_entries:
        missing_entries = [original for original, resolved in zip(full_filenames, resolved_files) if resolved is None]
        if len(resolved_files) == 1 and missing_entries[0] == os.path.join(subfolder, "config.json"):
            return None
        revision_ = "main" if revision is None else revision
        msg = (
            f"a file named {missing_entries[0]}" if len(missing_entries) == 1 else f"files named {(*missing_entries,)}"
        )
        raise OSError(
            f"{path_or_repo_id} does not appear to have {msg}. Checkout 'https://huggingface.co/{path_or_repo_id}/tree/{revision_}'"
            " for available files."
        )
    resolved_files = [file for file in resolved_files if file is not None]
    resolved_files = None if len(resolved_files) == 0 else resolved_files
    return resolved_files
def download_url(url, proxies=None):
    warnings.warn(
        f"Using `from_pretrained` with the url of a file (here {url}) is deprecated and won't be possible anymore in"
        " v5 of MEROAI. You should host your file on the Hub (hf.co) instead and use the repository ID. Note"
        " that this is not compatible with the caching system (your file will be downloaded at each execution) or"
        " multiple processes (each process will download the file in a different temporary file).",
        FutureWarning,
    )
    tmp_fd, tmp_file = tempfile.mkstemp()
    with os.fdopen(tmp_fd, "wb") as f:
        http_get(url, f, proxies=proxies)
    return tmp_file
def has_file(
    path_or_repo: Union[str, os.PathLike],
    filename: str,
    revision: Optional[str] = None,
    proxies: Optional[dict[str, str]] = None,
    token: Optional[Union[bool, str]] = None,
    *,
    local_files_only: bool = False,
    cache_dir: Union[str, Path, None] = None,
    repo_type: Optional[str] = None,
    **deprecated_kwargs,
):
    use_auth_token = deprecated_kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn(
            "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
            FutureWarning,
        )
        if token is not None:
            raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    if os.path.isdir(path_or_repo):
        return os.path.isfile(os.path.join(path_or_repo, filename))
    cached_path = try_to_load_from_cache(
        repo_id=path_or_repo,
        filename=filename,
        revision=revision,
        repo_type=repo_type,
        cache_dir=cache_dir,
    )
    has_file_in_cache = isinstance(cached_path, str)
    if local_files_only:
        return has_file_in_cache
    try:
        response = get_session().head(
            hf_hub_url(path_or_repo, filename=filename, revision=revision, repo_type=repo_type),
            headers=build_hf_headers(token=token, user_agent=http_user_agent()),
            allow_redirects=False,
            proxies=proxies,
            timeout=10,
        )
    except (requests.exceptions.SSLError, requests.exceptions.ProxyError):
        raise
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        OfflineModeIsEnabled,
    ):
        return has_file_in_cache
    try:
        hf_raise_for_status(response)
        return True
    except GatedRepoError as e:
        logger.error(e)
        raise OSError(
            f"{path_or_repo} is a gated repository. Make sure to request access at "
            f"https://huggingface.co/{path_or_repo} and pass a token having permission to this repo either by "
            "logging in with `hf auth login` or by passing `token=<your_token>`."
        ) from e
    except RepositoryNotFoundError as e:
        logger.error(e)
        raise OSError(f"{path_or_repo} is not a local folder or a valid repository name on 'https://hf.co'.") from e
    except RevisionNotFoundError as e:
        logger.error(e)
        raise OSError(
            f"{revision} is not a valid git identifier (branch name, tag name or commit id) that exists for this "
            f"model name. Check the model page at 'https://huggingface.co/{path_or_repo}' for available revisions."
        ) from e
    except EntryNotFoundError:
        return False
    except requests.HTTPError:
        return has_file_in_cache
class PushToHubMixin:
    def _create_repo(
        self,
        repo_id: str,
        private: Optional[bool] = None,
        token: Optional[Union[bool, str]] = None,
        repo_url: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> str:
        if repo_url is not None:
            warnings.warn(
                "The `repo_url` argument is deprecated and will be removed in v5 of MEROAI. Use `repo_id` "
                "instead."
            )
            if repo_id is not None:
                raise ValueError(
                    "`repo_id` and `repo_url` are both specified. Please set only the argument `repo_id`."
                )
            repo_id = repo_url.replace(f"{HUGGINGFACE_CO_RESOLVE_ENDPOINT}/", "")
        if organization is not None:
            warnings.warn(
                "The `organization` argument is deprecated and will be removed in v5 of MEROAI. Set your "
                "organization directly in the `repo_id` passed instead (`repo_id={organization}/{model_id}`)."
            )
            if not repo_id.startswith(organization):
                if "/" in repo_id:
                    repo_id = repo_id.split("/")[-1]
                repo_id = f"{organization}/{repo_id}"
        url = create_repo(repo_id=repo_id, token=token, private=private, exist_ok=True)
        return url.repo_id
    def _get_files_timestamps(self, working_dir: Union[str, os.PathLike]):
        return {f: os.path.getmtime(os.path.join(working_dir, f)) for f in os.listdir(working_dir)}
    def _upload_modified_files(
        self,
        working_dir: Union[str, os.PathLike],
        repo_id: str,
        files_timestamps: dict[str, float],
        commit_message: Optional[str] = None,
        token: Optional[Union[bool, str]] = None,
        create_pr: bool = False,
        revision: Optional[str] = None,
        commit_description: Optional[str] = None,
    ):
        if commit_message is None:
            if "Model" in self.__class__.__name__:
                commit_message = "Upload model"
            elif "Config" in self.__class__.__name__:
                commit_message = "Upload config"
            elif "Tokenizer" in self.__class__.__name__:
                commit_message = "Upload tokenizer"
            elif "FeatureExtractor" in self.__class__.__name__:
                commit_message = "Upload feature extractor"
            elif "Processor" in self.__class__.__name__:
                commit_message = "Upload processor"
            else:
                commit_message = f"Upload {self.__class__.__name__}"
        modified_files = [
            f
            for f in os.listdir(working_dir)
            if f not in files_timestamps or os.path.getmtime(os.path.join(working_dir, f)) > files_timestamps[f]
        ]
        modified_files = [
            f
            for f in modified_files
            if os.path.isfile(os.path.join(working_dir, f)) or os.path.isdir(os.path.join(working_dir, f))
        ]
        operations = []
        for file in modified_files:
            if os.path.isdir(os.path.join(working_dir, file)):
                for f in os.listdir(os.path.join(working_dir, file)):
                    operations.append(
                        CommitOperationAdd(
                            path_or_fileobj=os.path.join(working_dir, file, f), path_in_repo=os.path.join(file, f)
                        )
                    )
            else:
                operations.append(
                    CommitOperationAdd(path_or_fileobj=os.path.join(working_dir, file), path_in_repo=file)
                )
        if revision is not None and not revision.startswith("refs/pr"):
            try:
                create_branch(repo_id=repo_id, branch=revision, token=token, exist_ok=True)
            except HfHubHTTPError as e:
                if e.response.status_code == 403 and create_pr:
                    pass
                else:
                    raise
        logger.info(f"Uploading the following files to {repo_id}: {','.join(modified_files)}")
        return create_commit(
            repo_id=repo_id,
            operations=operations,
            commit_message=commit_message,
            commit_description=commit_description,
            token=token,
            create_pr=create_pr,
            revision=revision,
        )
    def push_to_hub(
        self,
        repo_id: str,
        use_temp_dir: Optional[bool] = None,
        commit_message: Optional[str] = None,
        private: Optional[bool] = None,
        token: Optional[Union[bool, str]] = None,
        max_shard_size: Optional[Union[int, str]] = "5GB",
        create_pr: bool = False,
        safe_serialization: bool = True,
        revision: Optional[str] = None,
        commit_description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        **deprecated_kwargs,
    ) -> str:
        use_auth_token = deprecated_kwargs.pop("use_auth_token", None)
        ignore_metadata_errors = deprecated_kwargs.pop("ignore_metadata_errors", False)
        save_jinja_files = deprecated_kwargs.pop(
            "save_jinja_files", None
        )
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if token is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            token = use_auth_token
        repo_path_or_name = deprecated_kwargs.pop("repo_path_or_name", None)
        if repo_path_or_name is not None:
            warnings.warn(
                "The `repo_path_or_name` argument is deprecated and will be removed in v5 of MEROAI. Use "
                "`repo_id` instead.",
                FutureWarning,
            )
            if repo_id is not None:
                raise ValueError(
                    "`repo_id` and `repo_path_or_name` are both specified. Please set only the argument `repo_id`."
                )
            if os.path.isdir(repo_path_or_name):
                repo_id = repo_path_or_name.split(os.path.sep)[-1]
                working_dir = repo_id
            else:
                repo_id = repo_path_or_name
                working_dir = repo_id.split("/")[-1]
        else:
            working_dir = repo_id.split("/")[-1]
        repo_url = deprecated_kwargs.pop("repo_url", None)
        organization = deprecated_kwargs.pop("organization", None)
        repo_id = self._create_repo(
            repo_id, private=private, token=token, repo_url=repo_url, organization=organization
        )
        model_card = create_and_tag_model_card(
            repo_id, tags, token=token, ignore_metadata_errors=ignore_metadata_errors
        )
        if use_temp_dir is None:
            use_temp_dir = not os.path.isdir(working_dir)
        with working_or_temp_dir(working_dir=working_dir, use_temp_dir=use_temp_dir) as work_dir:
            files_timestamps = self._get_files_timestamps(work_dir)
            if save_jinja_files:
                self.save_pretrained(
                    work_dir,
                    max_shard_size=max_shard_size,
                    safe_serialization=safe_serialization,
                    save_jinja_files=True,
                )
            else:
                self.save_pretrained(work_dir, max_shard_size=max_shard_size, safe_serialization=safe_serialization)
            model_card.save(os.path.join(work_dir, "README.md"))
            return self._upload_modified_files(
                work_dir,
                repo_id,
                files_timestamps,
                commit_message=commit_message,
                token=token,
                create_pr=create_pr,
                revision=revision,
                commit_description=commit_description,
            )
def convert_file_size_to_int(size: Union[int, str]):
    if isinstance(size, int):
        return size
    if size.upper().endswith("GIB"):
        return int(size[:-3]) * (2**30)
    if size.upper().endswith("MIB"):
        return int(size[:-3]) * (2**20)
    if size.upper().endswith("KIB"):
        return int(size[:-3]) * (2**10)
    if size.upper().endswith("GB"):
        int_size = int(size[:-2]) * (10**9)
        return int_size // 8 if size.endswith("b") else int_size
    if size.upper().endswith("MB"):
        int_size = int(size[:-2]) * (10**6)
        return int_size // 8 if size.endswith("b") else int_size
    if size.upper().endswith("KB"):
        int_size = int(size[:-2]) * (10**3)
        return int_size // 8 if size.endswith("b") else int_size
    raise ValueError("`size` is not in a valid format. Use an integer followed by the unit, e.g., '5GB'.")
def get_checkpoint_shard_files(
    pretrained_model_name_or_path,
    index_filename,
    cache_dir=None,
    force_download=False,
    proxies=None,
    resume_download=None,
    local_files_only=False,
    token=None,
    user_agent=None,
    revision=None,
    subfolder="",
    _commit_hash=None,
    **deprecated_kwargs,
):
    use_auth_token = deprecated_kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn(
            "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
            FutureWarning,
        )
        if token is not None:
            raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    if not os.path.isfile(index_filename):
        raise ValueError(f"Can't find a checkpoint index ({index_filename}) in {pretrained_model_name_or_path}.")
    with open(index_filename) as f:
        index = json.loads(f.read())
    shard_filenames = sorted(set(index["weight_map"].values()))
    sharded_metadata = index["metadata"]
    sharded_metadata["all_checkpoint_keys"] = list(index["weight_map"].keys())
    sharded_metadata["weight_map"] = index["weight_map"].copy()
    if os.path.isdir(pretrained_model_name_or_path):
        shard_filenames = [os.path.join(pretrained_model_name_or_path, subfolder, f) for f in shard_filenames]
        return shard_filenames, sharded_metadata
    cached_filenames = cached_files(
        pretrained_model_name_or_path,
        shard_filenames,
        cache_dir=cache_dir,
        force_download=force_download,
        proxies=proxies,
        resume_download=resume_download,
        local_files_only=local_files_only,
        token=token,
        user_agent=user_agent,
        revision=revision,
        subfolder=subfolder,
        _commit_hash=_commit_hash,
    )
    return cached_filenames, sharded_metadata
def create_and_tag_model_card(
    repo_id: str,
    tags: Optional[list[str]] = None,
    token: Optional[str] = None,
    ignore_metadata_errors: bool = False,
):
    try:
        model_card = ModelCard.load(repo_id, token=token, ignore_metadata_errors=ignore_metadata_errors)
    except EntryNotFoundError:
        model_description = "This is the model card of a 🤗 MEROAI model that has been pushed on the Hub. This model card has been automatically generated."
        card_data = ModelCardData(tags=[] if tags is None else tags, library_name="MEROAI")
        model_card = ModelCard.from_template(card_data, model_description=model_description)
    if tags is not None:
        if model_card.data.tags is None:
            model_card.data.tags = []
        for model_tag in tags:
            if model_tag not in model_card.data.tags:
                model_card.data.tags.append(model_tag)
    return model_card
class PushInProgress:
    def __init__(self, jobs: Optional[futures.Future] = None) -> None:
        self.jobs = [] if jobs is None else jobs
    def is_done(self):
        return all(job.done() for job in self.jobs)
    def wait_until_done(self):
        futures.wait(self.jobs)
    def cancel(self) -> None:
        self.jobs = [
            job
            for job in self.jobs
            if not (job.cancel() or job.done())
        ]