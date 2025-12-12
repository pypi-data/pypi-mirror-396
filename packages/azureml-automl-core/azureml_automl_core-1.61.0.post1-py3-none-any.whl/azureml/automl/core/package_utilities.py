# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common utilities related to package discovery and version checks."""
from typing import cast, Dict, List, Optional, Set, Tuple, Type, TYPE_CHECKING
import json
import logging
import os
import subprocess
import sys

import azureml.automl.core

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    IncompatibleDependency,
    IncompatibleOrMissingDependency,
    IncompatibleOrMissingDependencyDatabricks)
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from importlib.metadata import PackageNotFoundError, distribution, distributions
import importlib.metadata as package_metadata
import importlib.resources as package_resources
from packaging.requirements import Requirement, InvalidRequirement
from packaging.specifiers import SpecifierSet

# The Environment import causes an error importing WorkspaceClient in local runs.
# So, only import it for type checking.
if TYPE_CHECKING:
    from azureml.core.environment import Environment

logger = logging.getLogger(__name__)


AUTOML_PACKAGES = {'azureml-automl-runtime',
                   'azureml-train-automl-runtime',
                   'azureml-core',
                   'azureml-telemetry',
                   'azureml-defaults',
                   'azureml-automl-core',
                   'azureml-pipeline-steps',
                   'azureml-widgets',
                   'azureml-dataprep',
                   'azureml-train-automl-client',
                   'azureml-interpret',
                   'azureml-train-restclients-hyperdrive',
                   'azureml-train-core',
                   'azureml-pipeline-core'}

VALIDATED_REQ_FILE_NAME = 'validated_{}_requirements.txt'.format(sys.platform)
PACKAGES_IGNORED_IN_VALIDATION = ['cryptography', 'pyopenssl', 'azure-mgmt-resource', 'jinja2', 'idna',
                                  'onnx', 'onnxruntime', 'skl2onnx', 'tqdm', 'werkzeug', 'gunicorn']
PACKAGE_NAME = 'azureml.automl.core'

_PACKAGES_TO_IGNORE_VERSIONS = set()       # type: Set[str]

DISABLE_ENV_MISMATCH = "DISABLE_ENV_MISMATCH"


def _all_dependencies() -> Dict[str, str]:
    """
    Retrieve the packages from the site-packages folder by using importlib.metadata.

    :return: A dict contains packages and their corresponding versions.
    """
    dependencies_versions = dict()
    for d in distributions():
        dependencies_versions[d.name] = d.version
    return dependencies_versions


def _is_sdk_package(name: str) -> bool:
    """Check if a package is in sdk by checking the whether the package startswith('azureml')."""
    return name.startswith('azureml')


def get_sdk_dependencies(
    all_dependencies_versions: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Return the package-version dict.

    :param all_dependencies_versions:
        If None, then get all and filter only the sdk ones.
        Else, only check within the that dict the sdk ones.
    :return: The package-version dict.
    """
    sdk_dependencies_version = dict()
    if all_dependencies_versions is None:
        all_dependencies_versions = _all_dependencies()
    for d in all_dependencies_versions:
        if _is_sdk_package(d):
            sdk_dependencies_version[d] = all_dependencies_versions[d]

    return sdk_dependencies_version


def _is_version_mismatch(a: str, b: str, custom_azureml_logic: bool = False) -> bool:
    """
    Check if a is a version mismatch from b.

    :param a: A version to compare.
    :type a: str
    :param b: A version to compare.
    :type b: str
    :custom_azureml_logic: Option to ask for check on azureml packages.
        If true, ignore hotfix version.
        If true, `a` can have a minor version 1 lower than `b` without being considered a mismatch.
        As curated environment will release slower than pypi release, the client inference version may
        be greater than the client training version for a short period of time. In order to avoid errors in a
        new installation during this time, we add this functionality.
    :type custom_azureml_logic: bool
    :return: True if a != b. False otherwise.
    :rtype: bool
    """
    if custom_azureml_logic:
        ver_a = a.split('.')
        ver_b = b.split('.')
        # currently azureml release uses the following format
        # major.minor.0<.hot_fix>
        # however previously we followed the format
        # major.0.minor<.hot_fix>
        for i in range(3):
            try:
                if ver_a[i] != ver_b[i]:
                    # As curated environment will release slower than pypi release, the client inference version may
                    # be greater than the training version for a short period of time. In order to avoid errors in a
                    # new installation during this time, we add this functionality.
                    if i == 1 and int(ver_a[i]) + 1 == int(ver_b[i]):
                        # This should allow for any X.Y.Z:
                        # inference Y+1 is not a mismatch
                        # any Z will be supported and not considered mismatch
                        break
                    if i == 2 and ver_a[0] == ver_b[0] and ver_a[1] == ver_b[1]:
                        break
                    return True
            except IndexError:
                return True
        return False
    else:
        return a != b


def _check_dependencies_versions(
    old_versions: Dict[str, str],
    new_versions: Dict[str, str]
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    """
    Check the SDK packages between the training environment and the predict environment.

    Then it gives out 2 kinds of warning combining sdk/not sdk with missing or version mismatch.

    :param old_versions: Packages in the training environment.
    :param new_versions: Packages in the predict environment.
    :return: sdk_dependencies_mismatch, sdk_dependencies_missing,
             other_depencies_mismatch, other_depencies_missing
    """
    sdk_dependencies_mismatch = set()
    other_depencies_mismatch = set()
    sdk_dependencies_missing = set()
    other_depencies_missing = set()

    for d in old_versions.keys():
        if d in new_versions and _is_version_mismatch(old_versions[d], new_versions[d], custom_azureml_logic=False):
            if not _is_sdk_package(d):
                other_depencies_mismatch.add(d)
            elif _is_version_mismatch(old_versions[d], new_versions[d], custom_azureml_logic=True):
                sdk_dependencies_mismatch.add(d)
        elif d not in new_versions:
            if not _is_sdk_package(d):
                other_depencies_missing.add(d)
            else:
                sdk_dependencies_missing.add(d)

    return sdk_dependencies_mismatch, sdk_dependencies_missing, \
        other_depencies_mismatch, other_depencies_missing


def _has_version_discrepancies(sdk_dependencies: Dict[str, str], just_automl: bool = False) -> bool:
    """
    Check if the sdk dependencies are different from the current environment.

    Returns true is there are discrepancies false otherwise.
    """
    # Disable version mismatch for dev builds or if an environmental flag is set
    env_var_disable = os.environ.get(DISABLE_ENV_MISMATCH, False)

    if azureml.automl.core.VERSION.startswith("0") or env_var_disable:
        return False

    current_dependencies = _all_dependencies()
    sdk_mismatch, sdk_missing, other_mismatch, other_missing = _check_dependencies_versions(
        sdk_dependencies, current_dependencies
    )

    if len(sdk_mismatch) == 0 and len(sdk_missing) == 0:
        logging.debug('No issues found in the SDK package versions.')
        return False

    if just_automl and 'azureml-train-automl-client' not in sdk_mismatch and \
            'azureml-train-automl-client' not in sdk_missing:
        logging.debug('No issues found in the azureml-train-automl package')
        return False

    if len(sdk_mismatch) > 0:
        logging.warning('The version of the SDK does not match the version the model was trained on.')
        logging.warning('The consistency in the result may not be guaranteed.')
        message_template = 'Package:{}, training version:{}, current version:{}'
        message = []
        for d in sorted(sdk_mismatch):
            message.append(message_template.format(d, sdk_dependencies[d], current_dependencies[d]))
        logging.warning('\n'.join(message))

    if len(sdk_missing) > 0:
        logging.warning('Below packages were used for model training but missing in current environment:')
        message_template = 'Package:{}, training version:{}'
        message = []
        for d in sorted(sdk_missing):
            message.append(message_template.format(d, sdk_dependencies[d]))
        logging.warning('\n'.join(message))

    return True


def _get_incompatible_dependency_versions(packages: Set[str],
                                          ignored_dependencies: Optional[Set[str]] = None) \
        -> Tuple[bool, Dict[str, List[Tuple[Requirement, Optional[Requirement]]]]]:
    """
    Check all the requirements of listed packages and return any incompatible versions or missing packages.

    :param packages: The set of packages whose requirements should be checked for incompatibilities.
    :param ignored_dependencies: The set of dependencies whose versions should be ignored.
    :return: A boolean representing whether or not at least one incompatibility was found and a Dictionary of the
    package and corresponding list of incompatibilities found. Each entry in the list is a Tuple of package's
    requirement (`class packaging.Requirement`), conflicting installed requirement
    `class packaging.Requirement` or `None` if the required package is not installed.
    """
    _ignored_dependencies = ignored_dependencies if ignored_dependencies is not None else set()  # type: Set[str]
    working_set_packages = []
    incompatibilities = {}  # type: Dict[str, List[Tuple[Requirement, Optional[Requirement]]]]

    for dist in distributions():
        working_set_packages.append(dist.name)

    do_incompatibilities_exist = False
    for package in packages.intersection(working_set_packages):
        incomp_list = []
        package_distribution = distribution(package)

        all_packages = package_distribution.metadata.get_all('Requires-Dist')
        if all_packages is not None:
            for req_text in all_packages:
                req = Requirement(req_text)
                if req.marker is None or req.marker.evaluate():
                    is_incompat, incompat_req = _has_versionconflict_or_not_installed(req)
                    if not is_incompat:
                        continue

                    if req.name in _ignored_dependencies:
                        logging.warning('Ignoring version check for {}'.format(req.name))
                        continue

                    do_incompatibilities_exist = True
                    incomp_list.append((req, incompat_req))

            if incomp_list:
                incompatibilities[package] = incomp_list

    return do_incompatibilities_exist, incompatibilities


def _has_versionconflict_or_not_installed(req: Requirement) -> Tuple[bool, Optional[Requirement]]:
    """
    Check whether a requirement exists in the working set or has an incompatible version installed.

    :param req: The requirement that needs to be checked for in the working set.
    :return: Tuple with the first element representing whether the package is not installed or has a version
    conflict and the second element being the conflicting requirement that is installed or None if not installed.
    """
    try:
        found_version = package_metadata.version(req.name)

        if found_version not in SpecifierSet(str(req.specifier), True):
            logger.warning('Package: {package}, Version: {version} found.'.format(
                           package=req.name, version=found_version))
            return True, Requirement(req.name + "==" + found_version)

        logger.info('Package: {package}, Version: {version} found.'.format(package=req.name,
                                                                           version=found_version))
        return False, None
    except PackageNotFoundError:
        logger.warning('Package: {package} not found.'.format(
            package=req.name))
        return True, None


def _get_unverified_dependencies(
        validated_requirements: List[Requirement],
        conda_list_packages: Dict[str, Tuple[str, str]]) -> Tuple[bool,
                                                                  List[Tuple[Requirement, Optional[Requirement]]]]:
    working_set_by_key = {}
    incompat_list = []
    compat_list = []
    skip_conda_channel = []

    for dist in distributions():
        working_set_by_key[dist.name] = dist.version

    for expected_req in validated_requirements:
        # get the lowercased package name
        package_name = expected_req.name.lower()
        if package_name not in working_set_by_key:
            logger.warning("Package {} missing from working set.".format((package_name)))
            continue
        if package_name in conda_list_packages and conda_list_packages[package_name][1] != 'pypi':
            skip_conda_channel.append(package_name)
            continue
        if package_name in PACKAGES_IGNORED_IN_VALIDATION:
            continue
        is_incompat, incompat_req = _has_versionconflict_or_not_installed(expected_req)
        if not is_incompat:
            compat_list.append(package_name)
            continue

        logger.error("found incompatible requirement {} but expected {}.".format(incompat_req, expected_req))
        incompat_list.append((expected_req, incompat_req))

    if compat_list:
        versions = ["{}=={}".format(pkg_name, working_set_by_key[pkg_name]) for pkg_name in compat_list]
        logger.info("User has the following compatible packages installed:\n{}".format("\n".join(versions)))

    if skip_conda_channel:
        versions = ["{}=={}".format(pkg_name, conda_list_packages[pkg_name][0]) for pkg_name in skip_conda_channel]
        logger.warning("Skipping package validation check for non pypi packages:\n{}".format("\n".join(versions)))
    return len(incompat_list) > 0, incompat_list


def _parse_package_name_conda(pkg_string):
    # normalize package names to replace underscores and dots with dashes
    return pkg_string.replace('_', '-').replace('.', '-')


def _all_dependencies_conda_list() -> Dict[str, Tuple[str, str]]:
    """
    Retrieve the packages using 'conda list' command.

    :return: A Dictionary of the package and the corresponding version with the build channel.
    """
    conda_list_cmd = ["conda", "list", "--json"]
    if os.getenv("AZUREML_CONDA_ENVIRONMENT_PATH"):
        conda_list_cmd.extend(["-p", os.getenv("AZUREML_CONDA_ENVIRONMENT_PATH", "")])
    try:
        process = subprocess.run(conda_list_cmd, shell=False, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (FileNotFoundError, subprocess.CalledProcessError) as err:
        logger.warning('subprocess failed to get dependencies list from conda')
        logging_utilities.log_traceback(err, logger)
        return {}
    output_str = process.stdout.decode('ascii')
    output_json = json.loads(output_str)
    conda_list_packages = {_parse_package_name_conda(pkg['name']): (
        pkg['version'], pkg['channel']) for pkg in output_json}
    return conda_list_packages


def _get_curated_environment_conda_list_packages() -> Tuple[List[str], List[str], Set[str]]:
    """
    Retrieve the packages using 'conda list' command.

    :return: A Tuple of the pip and conda package and the corresponding versions.
    """
    conda_list_cmd = ["conda", "list", "--json"]
    if os.getenv("AZUREML_CONDA_ENVIRONMENT_PATH"):
        conda_list_cmd.extend(["-p", os.getenv("AZUREML_CONDA_ENVIRONMENT_PATH", "")])
    try:
        process = subprocess.run(conda_list_cmd, shell=False, check=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (FileNotFoundError, subprocess.CalledProcessError) as err:
        logger.warning('subprocess failed to get dependencies list from conda')
        logging_utilities.log_traceback(err, logger)
        return [], [], set()
    output_str = process.stdout.decode('ascii')
    output_json = json.loads(output_str)
    conda_list = []
    pip_list = []
    added_set = set()
    channels = set()
    for pkg in output_json:
        pkg_name = pkg['name']
        pkg_version = pkg['version']
        pkg_channel = pkg['channel']
        if pkg_name not in added_set and pkg_name not in constants.Dependencies.PACKAGE_DELETION_LIST:
            added_set.add(pkg_name)
            is_valid_conda_pkg = pkg_name in constants.Dependencies.CONDA_PREFERRED_LIST
            # pkg_channel can be "pkgs/main" for conda packages.
            if is_valid_conda_pkg or pkg_channel != 'pypi':
                conda_list.append(pkg_name + "=" + pkg_version)
                if pkg_channel in constants.Dependencies.CONDA_CHANNELS_LIST:
                    channels.add(pkg_channel)
            elif pkg_name in constants.Dependencies.PACKAGE_REPLACEMENT_LIST:
                pip_list.append(constants.Dependencies.PACKAGE_REPLACEMENT_LIST[pkg_name])
            else:
                # Vision training runs use torch==1.13.1+cu116 and torchvision==0.14.1+cu116 from the extra-index-url
                # https://download.pytorch.org/whl/cu116. When these packages are exported in model as
                # torch==1.11.0+cu116, batch deployment fails. Batch deployment uses training image as base image and
                # installs packages from model conda.yaml on top of it. This leads to failures as installing from
                # extra-index-url doesn't work on top of training base image. Hence, we remove the suffix "+cu113"
                # and install basic version of torch during deployments.
                if pkg_version.endswith("+cu116"):
                    pkg_version = pkg_version[:-6]
                pip_list.append(pkg_name + "==" + pkg_version)

    return pip_list, conda_list, channels


def _get_validated_requirements(validated_req_file: Optional[str] = None) -> Optional[List[Requirement]]:
    """
    Get Requirements for all packages listed in the validated requirements file.

    :param requirements_file: Overwrite location for validated requirements file
    :return:
    """
    # check all unverified packages
    if validated_req_file is None:
        ref = package_resources.files(PACKAGE_NAME) / VALIDATED_REQ_FILE_NAME
        with package_resources.as_file(ref) as validated_req_path:
            return _get_validated_requirements_from_file(str(validated_req_path))
    else:
        return _get_validated_requirements_from_file(validated_req_file)


def _get_validated_requirements_from_file(validated_req_file: str) -> Optional[List[Requirement]]:
    """
    Get Requirements for all packages listed in the validated requirements file.

    :param requirements_file: Overwrite location for validated requirements file
    :return:
    """
    # check all unverified packages
    validated_requirements = []
    if os.path.exists(validated_req_file):
        logger.info("Verified requirements file {} found.".format(VALIDATED_REQ_FILE_NAME))
        with open(validated_req_file, 'r') as infile:
            text = infile.readlines()
            for req_text in text:
                if req_text.strip() and not (req_text.startswith('#') or req_text.startswith('-e')):
                    req_text = req_text.replace('==', '<=')
                    try:
                        parsed_req = Requirement(req_text)
                        if parsed_req.name.startswith('azureml-'):
                            continue
                        if parsed_req.name.lower() in PACKAGES_IGNORED_IN_VALIDATION:
                            continue
                        validated_requirements.append(parsed_req)
                    except (ValueError, InvalidRequirement):
                        logger.warning('failed to parse {}'.format(req_text))
                    except Exception as e:
                        logging_utilities.log_traceback(e, logger)
                        raise
        logger.debug("Verified requirements found and loaded.")
        return validated_requirements
    else:
        logger.warning("No verified requirements file found. Unable to verify all requirements.")
        return None


def _get_package_incompatibilities(packages: Set[str],
                                   ignored_dependencies: Optional[Set[str]] = None,
                                   is_databricks_run: Optional[bool] = False) -> None:
    """
    Check whether the listed packages's dependencies are met in the current environment.
    If not, throw a ``azureml.automl.core.shared.exceptions.ValidationException``.

    :param packages: The set of packages for which compatibility must be ensured for their dependencies.
    :param ignored_dependencies: The set of dependencies whose versions should be ignored.
    :raises: :class:`azureml.automl.core.shared.exceptions.ValidationException`
    """
    with logging_utilities.log_activity(logger, activity_name=constants.TelemetryConstants.PACKAGES_CHECK):
        # Check top level dependencies and their dependents
        do_incompatibilities_exist, incompatible_packages = _get_incompatible_dependency_versions(
            packages,
            ignored_dependencies
        )

        if do_incompatibilities_exist:
            messages = []
            message_template = '{0}/{1}/{2}'
            for package, incompat_packages in incompatible_packages.items():
                for incompatibility in incompat_packages:
                    messages.append(message_template.format(package,
                                                            incompatibility[0],
                                                            incompatibility[1] or 'not installed'))

            if is_databricks_run:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        IncompatibleOrMissingDependencyDatabricks,
                        target=','.join(incompatible_packages.keys()),
                        missing_packages_message_header='Package name/Required version/Installed version',
                        missing_packages_message='\n'.join(messages),
                        reference_code=ReferenceCodes._PACKAGE_INCOMPATIBILITIES_FOUND_ADB,
                    )
                )
            else:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        IncompatibleOrMissingDependency,
                        target=','.join(incompatible_packages.keys()),
                        missing_packages_message_header='Package name/Required version/Installed version',
                        missing_packages_message='\n'.join(messages),
                        reference_code=ReferenceCodes._PACKAGE_INCOMPATIBILITIES_FOUND
                    )
                )

        validated_requirements = _get_validated_requirements()
        if validated_requirements is None:
            return

        # Disable dependency check for dev builds or if an environmental flag is set
        env_var_disable = os.environ.get(DISABLE_ENV_MISMATCH, False)

        if azureml.automl.core.VERSION.startswith("0") or env_var_disable:
            logger.warning("Package validation disabled. env_var_disable set to {}".format(env_var_disable))
            return

        conda_list_packages = _all_dependencies_conda_list()

        do_incompatibilities_exist, unverified_packages = _get_unverified_dependencies(
            validated_requirements,
            conda_list_packages
        )

        if do_incompatibilities_exist:
            messages = []
            for unverified_package in unverified_packages:
                message_template = '{}/{}'
                messages.append(message_template.format(
                    unverified_package[0],
                    unverified_package[1]))

            if is_databricks_run:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        IncompatibleOrMissingDependencyDatabricks,
                        target=','.join(incompatible_packages.keys()),
                        missing_packages_message_header='Required version/Installed version',
                        missing_packages_message='\n'.join(messages),
                        reference_code=ReferenceCodes._UNVERIFIED_PACKAGES_ADB,
                    ))
            else:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        IncompatibleOrMissingDependency,
                        target=','.join(incompatible_packages.keys()),
                        missing_packages_message_header='Required version/Installed version',
                        missing_packages_message='\n'.join(messages),
                        reference_code=ReferenceCodes._UNVERIFIED_PACKAGES
                    ))

        logger.info("No package incompatibilities found.")


def _validate_package(package: str, requirements_file: Optional[str] = None) -> None:
    """
    Checks whether the correct version of the package is installed or raises an IncompatibleDependency Error.
    :param package: Name of the package
    :param requirements_file: Overwrite location for validated requirements file
    :return:
    """
    validated_requirements = _get_validated_requirements(requirements_file)
    if validated_requirements:
        requirements = [req for req in validated_requirements
                        if hasattr(req, "name") and req.name == package]
        if requirements:
            requirement = requirements[0]
            has_conflict, conflict = _has_versionconflict_or_not_installed(requirement)
            if has_conflict:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        IncompatibleDependency,
                        package=package,
                        current_package=conflict,
                        expected_package=str(requirement)
                    )
                )
