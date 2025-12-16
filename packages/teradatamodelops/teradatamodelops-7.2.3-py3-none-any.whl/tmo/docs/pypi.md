# Teradata ModelOps Client

- [Installation](#installation)
- [CLI](#cli)
  - [configuration](#configuration)
  - [help](#help)
  - [list](#list)
  - [add](#add)
  - [run](#run)
  - [init](#init)
  - [clone](#clone)
  - [link](#link)
  - [task](#task)
    - [add](#task-add)
    - [run](#task-run)
  - [connection](#connection)
  - [feature](#feature)
    - [compute-stats](#feature-compute-stats)
    - [list-stats](#feature-list-stats)
    - [create-stats-table](#feature-create-stats-table)
    - [import-stats](#feature-import-stats)
  - [doctor](#doctor)
- [Authentication](#authentication)
- [SDK](#sdk)
  - [Create Client](#create-client)
  - [Read Entities](#read-entities)
  - [Deploy Model Version](#deploy-model-version)
  - [Import Model Version](#import-model-version)
- [Release Notes](#release-notes)

# Installation<a id="installation"></a>

The teradatamodelops is available from [pypi](https://pypi.org/project/teradatamodelops/)

```bash
pip install teradatamodelops
```

_Note: previously Teradata ModelOps was known as AnalyticsOps Accelerator (AOA), so you might encounter mentions of AOA or aoa, it's referring to an older version of ModelOps_

_Note: If you're installing on Windows, you need to install OpenSSL manually to be able to authenticate with your ModelOps instance._

# CLI<a id="cli"></a>

## configuration<a id="configuration"></a>

By default, the CLI looks for configuration stored in `~/.tmo/config.yaml`. Copy the config from ModelOps UI -> Session Details -> CLI Config. This will provide the command to create or update the `config.yaml`. If required, one can override this configuration at runtime by specifying environment variables (see `api_client.py`)

## help<a id="help"></a>

The cli can be used to perform a number of interactions and guides the user to perform those actions.

```bash
> tmo -h
usage: tmo [-h] [--debug] [--version] {list,add,run,init,clone,link,task,connection,feature,doctor} ...

TMO CLI

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  --version             Display the version of this tool

actions:
  valid actions

  {list,add,run,init,clone,link,task,connection,feature,doctor}
    list                List projects, models, local models or datasets
    add                 Add model to working dir
    run                 Train and Evaluate model locally
    init                Initialize model directory with basic structure
    clone               Clone Project Repository
    link                Link local repo to project
    task                Manage feature engineering tasks
    connection          Manage local connections
    feature             Manage feature statistics
    doctor              Diagnose configuration issues
```

## list<a id="list"></a>

Allows to list the tmo resources. In the cases of listing models (pushed / committed) and datasets, it will prompt the user to select a project prior showing the results. In the case of local models, it lists both committed and non-committed models.

```bash
> tmo list -h
usage: tmo list [-h] [--debug] [-p] [-m] [-lm] [-t] [-d] [-c]

options:
  -h, --help           show this help message and exit
  --debug              Enable debug logging
  -p, --projects       List projects
  -m, --models         List registered models (committed / pushed)
  -lm, --local-models  List local models. Includes registered and non-registered (non-committed / non-pushed)
  -t, --templates      List dataset templates
  -d, --datasets       List datasets
  -c, --connections    List local connections
```

All results are shown in the format

```
[index] (id of the resource) name
```

for example:

```
List of models for project Demo:
--------------------------------
[0] (03c9a01f-bd46-4e7c-9a60-4282039094e6) Diabetes Prediction
[1] (74eca506-e967-48f1-92ad-fb217b07e181) IMDB Sentiment Analysis
```

## add<a id="add"></a>

Add a new model to a given repository based on a model template. A model in any other existing ModelOps git repository (specified via the `-t <giturl>`) can be used.

```bash
> tmo add -h
usage: tmo add [-h] [--debug] -t TEMPLATE_URL -b BRANCH

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -t TEMPLATE_URL, --template-url TEMPLATE_URL
                        Git URL for template repository
  -b BRANCH, --branch BRANCH
                        Git branch to pull templates (default is main)
```

Example usage

```bash
> tmo add -t https://github.com/Teradata/modelops-demo-models -b master
```

## run<a id="run"></a>

The cli can be used to validate the model training and evaluation logic locally before committing to git. This simplifies the development lifecycle and allows you to test and validate many options. It also enables you to avoid creating the dataset definitions in ModelOps UI until you are ready and have a finalised version.

```bash
> tmo run -h
usage: tmo run [-h] [--debug] [-id MODEL_ID] [-m MODE] [-d DATASET_ID] [-t DATASET_TEMPLATE_ID] [-ld LOCAL_DATASET] [-lt LOCAL_DATASET_TEMPLATE] [-c CONNECTION]

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -id MODEL_ID, --model-id MODEL_ID
                        Id of model
  -m MODE, --mode MODE  Mode (train or evaluate)
  -d DATASET_ID, --dataset-id DATASET_ID
                        Remote datasetId
  -t DATASET_TEMPLATE_ID, --dataset-template-id DATASET_TEMPLATE_ID
                        Remote datasetTemplateId
  -ld LOCAL_DATASET, --local-dataset LOCAL_DATASET
                        Path to local dataset metadata file
  -lt LOCAL_DATASET_TEMPLATE, --local-dataset-template LOCAL_DATASET_TEMPLATE
                        Path to local dataset template metadata file
  -c CONNECTION, --connection CONNECTION
                        Local connection id
```

You can run all of this as a single command or interactively by selecting some optional arguments, or none of them.

For example, if you want to run the cli interactively you just select `tmo run` but if you wanted to run it non interactively to train a given model with a given datasetId you would expect

```bash
> tmo run -id <modelId> -m <mode> -d <datasetId>
```

## init<a id="init"></a>

When you create a git repository, its empty by default. The `init` command allows you to initialize the repository with the structure required by ModelOps. It also adds a default README.md and HOWTO.md.

```bash
> tmo init -h
usage: tmo init [-h] [--debug]

options:
  -h, --help  show this help message and exit
  --debug     Enable debug logging
```

## clone<a id="clone"></a>

The `clone` command provides a convenient way to perform a git clone of the repository associated with a given project. The command can be run interactively and will allow you to select the project you wish to clone. Note that by default it clones to the current working directory so you either need to make sure you create an empty folder and run it from within there or else provide the `--path ` argument.

```bash
> tmo clone -h
usage: tmo clone [-h] [--debug] [-id PROJECT_ID] [-p PATH]

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -id PROJECT_ID, --project-id PROJECT_ID
                        Id of Project to clone
  -p PATH, --path PATH  Path to clone repository to
```

## link<a id="link"></a>

Links the current local repository to a remote project.

```bash
> tmo link -h
usage: tmo link [-h] [--debug]

options:
  -h, --help  show this help message and exit
  --debug     Enable debug logging
```

## task<a id="task"></a>

Manage feature tasks actions. The feature tasks are used to automate the feature engineering process. The tasks are stored in a git repository and can be shared across multiple projects.

```bash
> tmo task -h
usage: tmo task [-h] {add,run} ...

options:
  -h, --help  show this help message and exit

actions:
  valid actions

  {add,run}
    add       Add feature engineering task to working dir
    run       Run feature engineering tasks locally
```

### task add<a id="task-add"></a>

Add a new feature engineering task to a given repository based on a task template. A task in any other existing ModelOps git repository (specified via the `-t <giturl>`) can be used.

```bash
> tmo task add -h
usage: tmo task add [-h] [--debug] -t TEMPLATE_URL -b BRANCH

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -t TEMPLATE_URL, --template-url TEMPLATE_URL
                        Git URL for template repository
  -b BRANCH, --branch BRANCH
                        Git branch to pull task (default is main)
```

Example usage

```bash
> tmo task add -t https://github.com/Teradata/modelops-demo-models -b feature_engineering
```

### task run<a id="task-run"></a>

The cli can be used to run feature engineering tasks locally before committing to git.

```bash
> tmo task run -h
usage: tmo task run [-h] [--debug] [-c CONNECTION] [-f FUNCTION_NAME]

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -c CONNECTION, --connection CONNECTION
                        Local connection id
  -f FUNCTION_NAME, --function-name FUNCTION_NAME
                        Task function name
```

You can run all of this as a single command or interactively by selecting some optional arguments, or none of them.

For example, if you want to run the cli interactively you just select `tmo task run` but if you wanted to run it non interactively to run a given task function you would expect

```bash
> tmo task run -f <functionName> -c <connectionId>
```

## connection<a id="connection"></a>

The connection credentials stored in the ModelOps service cannot be accessed remotely through the CLI for security reasons. Instead, users can manage connection information locally for the CLI. These connections are used by other CLI commands which access Vantage.

```bash
> tmo connection -h
usage: tmo connection [-h] {list,add,remove,export,test,create-byom-table} ...

options:
  -h, --help            show this help message and exit

actions:
  valid actions

  {list,add,remove,export,test,create-byom-table}
    list                List all local connections
    add                 Add a local connection
    remove              Remove a local connection
    export              Export a local connection to be used as a shell script
    test                Test a local connection
    create-byom-table   Create a table to store BYOM models
```

## feature<a id="feature"></a>

Manage feature metadata by creating and populating feature metadata table(s). The feature metadata tables contain information required when computing statistics during training, scoring etc. This metadata depends on the feature type (categorical or continuous).

As this metadata can contain sensitive profiling information (such as categories), it is recommended to treat this metadata in the same manner as you treat the features for a given use case. That is, the feature metadata should live in a project or use case level database.

```bash
> tmo feature -h
usage: tmo feature [-h] {compute-stats,list-stats,create-stats-table,import-stats} ...

options:
  -h, --help            show this help message and exit

action:
  valid actions

  {compute-stats,list-stats,create-stats-table,import-stats}
    compute-stats       Compute feature statistics
    list-stats          List available statistics
    create-stats-table  Create statistics table
    import-stats        Import column statistics from local JSON file
```

### feature compute-stats<a id="feature-compute-stats"></a>

Compute the feature metadata information required when computing statistics during training, scoring etc. This metadata depends on the feature type (categorical or continuous).

Continuous: the histograms edges  
Categorical: the categories

```bash
> tmo feature compute-stats -h
usage: tmo feature compute-stats [-h] [--debug] -s SOURCE_TABLE -m METADATA_TABLE [-t {continuous,categorical}] -c COLUMNS

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -s SOURCE_TABLE, --source-table SOURCE_TABLE
                        Feature source table/view
  -m METADATA_TABLE, --metadata-table METADATA_TABLE
                        Metadata table for feature stats, including database name
  -t {continuous,categorical}, --feature-type {continuous,categorical}
                        Feature type: continuous or categorical (default is continuous)
  -c COLUMNS, --columns COLUMNS
                        List of feature columns
```

Example usage

```bash
tmo feature compute-stats \
  -s <feature-db>.<feature-data> \
  -m <feature-metadata-db>.<feature-metadata-table> \
  -t continuous -c numtimesprg,plglcconc,bloodp,skinthick,twohourserins,bmi,dipedfunc,age
```

### feature list-stats<a id="feature-list-stats"></a>

Lists the name and type (categorical or continuous) for all the features stored in the specified metadata table.

```bash
> tmo feature list-stats -h
usage: tmo feature list-stats [-h] [--debug] -m METADATA_TABLE

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -m METADATA_TABLE, --metadata-table METADATA_TABLE
                        Metadata table for feature stats, including database name
```

Example usage

```bash
tmo feature list-stats \
  -m <feature-metadata-db>.<feature-metadata-table>
```

### feature create-stats-table<a id="feature-create-stats-table"></a>

Creates or prints out the required SQL to create the metadata statistics table with the specified name.

```bash
> tmo feature create-stats-table -h
usage: tmo feature create-stats-table [-h] [--debug] -m METADATA_TABLE [-e]

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -m METADATA_TABLE, --metadata-table METADATA_TABLE
                        Metadata table for feature stats, including database name
  -e, --execute-ddl     Execute CREATE TABLE DDL, not just generate it
```

Example usage

```bash
tmo feature create-stats-table \
  -m <feature-metadata-db>.<feature-metadata-table> \
  -e
```

### feature import-stats<a id="feature-import-stats"></a>

Imports feature metadata statistics from a local JSON file to the target table. It also supports showing an example of the file structure.

```bash
> tmo feature import-stats -h
usage: tmo feature import-stats [-h] [--debug] -m METADATA_TABLE -f STATISTICS_FILE [-s]

options:
  -h, --help            show this help message and exit
  --debug               Enable debug logging
  -m METADATA_TABLE, --metadata-table METADATA_TABLE
                        Metadata table for feature stats, including database name
  -f STATISTICS_FILE, --statistics-file STATISTICS_FILE
                        Name of statistics JSON file
  -s, --show-example    Show file structure example and exit
```

Example usage

```bash
tmo feature import-stats \
  -m <feature-metadata-db>.<feature-metadata-table> \
  -f <path-to-statistics-file>
```

## doctor<a id="doctor"></a>

Runs healtchecks on the current setup. First checks the health of the remote ModelOps service configuration and secondly checks the health of any of the locally created connections.

```bash
> tmo doctor -h
usage: tmo doctor [-h] [--debug]

options:
  -h, --help  show this help message and exit
  --debug     Enable debug logging
```

# Authentication<a id="authentication"></a>

A number of authentication methods are supported for both the CLI and SDK.

- device_code (interactive)
- client_credentials (service-service)
- bearer (raw bearer token)
- pat (personal access token)

When working interactively, the recommended auth method for the CLI is `device_code`. It will guide you through the auth automatically. For Vantage CloudLake (VCL), the recommended auth method is `pat`. To learn more about working with PATs, please refer to the VCL documentation. For the SDK, use `bearer` if working interactively.
For both CLI and SDK, if working in an automated service-service manner, use `client_credentials`.

# SDK<a id="sdk"></a>

The SDK for ModelOps allows users to interact with ModelOps APIs from anywhere they can execute python such as notebooks, IDEs etc. It can also be used for devops to automate additional parts of the process and integrate into the wider organization.

## Create Client<a id="create-client"></a>

By default, creating an instance of the `TmoClient` looks for configuration stored in `~/.tmo/config.yaml`. When working with the SDK, we recommend that you specify (and override) all the necessary configuration as part of the `AoaClient` invocation.

An example to create a client using a bearer token for a given project is

```python
from tmo import TmoClient

client = TmoClient(
  vmo_url="<modelops-endpoint>",
  auth_mode="bearer",
  auth_bearer="<bearer-token>",
  project_id="23e1df4b-b630-47a1-ab80-7ad5385fcd8d",
)
```

To get the values to use for bearer token and vmo_url, go to the ModelOps UI -> Session Details -> SDK Config.

## Read Entities<a id="read-entities"></a>

We provide an extensive sdk implementation to interact with the APIs. You can find, create, update, archive, etc any entity that supports it via the SDK. In addition, most if not all search endpoints are also implemented in the sdk. Here are some examples

```python
from tmo import TmoClient
import pprint

client = TmoClient(project_id="23e1df4b-b630-47a1-ab80-7ad5385fcd8d")

datasets = client.datasets().find_all()
pprint.pprint(datasets)

dataset = client.datasets().find_by_id("11e1df4b-b630-47a1-ab80-7ad5385fcd8c")
pprint.pprint(dataset)

jobs = client.jobs().find_by_id("21e1df4b-b630-47a1-ab80-7ad5385fcd1c")
pprint.pprint(jobs)
```

## Deploy Model Version<a id="deploy-model-version"></a>

Let's assume we have a model version `4131df4b-b630-47a1-ab80-7ad5385fcd15` which we want to deploy In-Vantage and schedule it to execute once a month at midnight of the first day of the month using dataset connection `11e1df4b-b630-47a1-ab80-7ad5385fcd8c` and dataset template `d8a35d98-21ce-47d0-b9f2-00d355777de1`. We can use the SDK as follows to perform this.

```python
from tmo import TmoClient

client = TmoClient(project_id="23e1df4b-b630-47a1-ab80-7ad5385fcd8d")

trained_model_id = "4131df4b-b630-47a1-ab80-7ad5385fcd15"
deploy_request = {
  "engineType": "IN_VANTAGE",
  "publishOnly": False,
  "language": "PMML",
  "cron": "0 0 1 * *",
  "byomModelLocation": {
    "database": "<db-name>",
    "table": "<table-name>"
  },
  "datasetConnectionId": "11e1df4b-b630-47a1-ab80-7ad5385fcd8c",
  "datasetTemplateId": "d8a35d98-21ce-47d0-b9f2-00d355777de1",
  "engineTypeConfig": {
    "dockerImage": "",
    "engine": "byom",
    "resources": {
      "memory": "1G",
      "cpu": "1"
    }
  }
}

job = client.trained_models().deploy(trained_model_id, deploy_request)

# wait until the job completes (if the job fails it will raise an exception)
client.jobs().wait(job['id'])
```

## Import Model Version<a id="import-model-version"></a>

Let's assume we have a PMML model which we have trained in another data science platform. We want to import the artefacts for this version (model.pmml and data_stats.json) against a BYOM model `f937b5d8-02c6-5150-80c7-1e4ff07fea31`.

```python
from tmo import TmoClient

client = TmoClient(project_id="23e1df4b-b630-47a1-ab80-7ad5385fcd8d")

# set metadata for your import request
model_id = '<model-uuid>'
filename = './pima.pmml'
language = 'PMML'
dataset_connection_id = '<dataset-connection-uuid>'
train_dataset_id = '<train-dataset-uuid>'

# first, upload the artefacts which we want to associate with the BYOM model version
import_id = client.trained_model_artefacts().upload_byom_model(language, filename)

import_request = {
  "artefactImportId": import_id,
  "externalId": "my_model_external_id",
  "modelMonitoring": {
    "language": language,
    "useDefaultEvaluation": True,
    "evaluationEnabled": True,
    "modelType": "CLASSIFICATION",
    "byomColumnExpression": "CAST(CAST(json_report AS JSON).JSONExtractValue('$.predicted_HasDiabetes') AS INT)",
    "driftMonitoringEnabled": True,
    "datasetId": train_dataset_id,
    "datasetConnectionId": dataset_connection_id,
  },
}

job = client.models().import_byom(model_id, import_request)

# wait until the job completes (if the job fails it will raise an exception)
client.jobs().wait(job["id"])

# now you can list the artefacts which were uploaded and linked to the model version
trained_model_id = job["metadata"]["trainedModel"]["id"]
artefacts = client.trained_model_artefacts().list_artefacts(trained_model_id)
```

## Release Notes<a id="release-notes"></a>

### 7.2.3
- Chore: Remove pandas warning for `DataFrameGroupBy.apply`.

### 7.2.2
- Bug: Fix for charset setting fallback in case Vantage does not support it.

### 7.2.1
- Feature: Added `developer_experience` jupyter notebook to examples.
- Feature: Added `create()` function to `DatasetTemplateApi` to create dataset templates.
- Feature: Added `create()` function to `DatasetApi` to create and link datasets.
- Feature: Added `compute_stats()` function to `tmo.stats.stats` to compute and insert feature metadata into database table.
- Refactor: Made `credsEncrypted` and `log_mech` parameters optional for creating dataset connections using API.
- Refactor: Made `archived`, `isChecked` and `gitCredentials` parameters optional for creating projects using API.
- Bug: Fix auth spinner not working as expected.
- Bug: Fix `vmo_url` not being set correctly when converting config folder to `.vmo` from `.aoa`.

### 7.2.0

- Chore: removing support for python 3.8 and 3.9 and upgrading dependencies.
- Bug: Fixed OAuth refresh token flow for device code.

### 7.1.8

- Bug: Fixed renaming of CLI config values.
- Bug: Fixed STO stats.
- Bug: Fixed OAuth refresh token flow for device code.
- Bug: Fixed encryption and decryption methods.

### 7.1.7

- Feature: teradataml Library upgrade for UTF-8 character set support.
- Bug: Fixed signed URL handling for model artifact uploads/downloads with Azure Blob Storage.

### 7.1.6

- Feature: Added support for Personal Access Tokens (PAT).

### 7.1.5

- Bug: Fix env vars renaming from `AOA_` to `VMO_`.

### 7.1.4

- Feature: Added support for Windows OS.
- Bug: Fixed `tmo feature import-stats` not working for local statistics file.
- Refactor: Deprecated `aoa_create_context` in favour of `tmo_create_context`.
- Refactor: Renamed all `aoa` legacy references to `tmo`.

### 7.1.3

- Feature: Exposed `run_scoring` method for Deployment API.
- Chore: Security fixes.
- Feature: CSAE updates.

### 7.1.2

- Feature: Added shortcut methods to `AoaClient` to improve developer experience.
- Feature: Exposed more API methods, such as:
  - `deployments().find_by_deployment_job_id()`
  - `jobs().find_by_deployment_id()`
  - `dataset_connections().validate_connection()`
  - `describe_current_project()`
- Documentation: Added example for scheduling a Jupyter notebook.
- Feature: Added BYOM recipe in examples.

### 7.1.1

- Bug: Fix for OAuth2 Device code grant type.
- Feature: Updated pypi.md with new release notes.
- Bug: Fix for rest api compliance after core upgrading.
- Feature: Added feature engineering support.
- Chore: Updated license agreement.

### 7.1.0

- Feature: Explicitly ask for `logmech` when defining a local Vantage connection.
- Bug: Fixed `tmo connection create-byom-table` logging error.
- Feature: Added support for `access_token` when using OAuth2 Device code grant type.
- Feature: Updated `requests` dependency.
- Feature: Client hardening efforts.
- Feature: Added Feature Engineering Tasks functions `tmo task add` and `tmo task run`.

### 7.0.6

- Bug: Fixed compatibility issue with `teradataml>=20.0.0.0`.
- Feature: Minor formatting updates.
- Feature: Added user attributes API.
- Feature: Updated programmatic BYOM import examples.

### 7.0.5

**WARNING** Please recreate statistics metadata if you are using this version. It will produce more accurate results and correct behaviour.

- Bug: Fixed computing statistics metadata for continuous features with all NULLs.
- Bug: Fixed training/eval/scoring statistics on columns with all NULLs.
- Bug: Added a workaround for VAL Histograms failure due to SP argument being longer than 31000 characters.
- Feature: Forced rounding of all decimal and flloat bin edges to Teradata-supported FLOAT literals (15 digits max).
- Bug: Fixed CLI error computing continuous statistics metadata related to mixed case column names.

### 7.0.4

**WARNING** Please recreate statistics metadata if you are using this version. It will produce more accurate results and correct behaviour.

- Bug: Fixed STO helper functions to pick up correct python environment.
- Feature: Computing statistics metadata:
  - Allow less than 10 bins for continuous integer features.
  - Ignore continuous features that have single value for all rows.
  - Allow different precision for decimal and float continuous features.
  - Fix a bug with repeating edges for decimal/float continuous features.
  - Using rounded edges for integer continuous features.
  - Ignore NULLs for categorical features.
  - Ignore categorical features that have NULL value for all rows.
- Feature: Allow collecting training statistics without providing a target (unsupervised learning).
- Feature: Report right and left outliers when computing statistics on continuous features.
- Feature: Allow collecting training/evaluation/scoring statistics when statistics metadata is missing for some columns (missing columns are reported in data_stats.json).
- Feature: For categorical features, report outlier categories in "unmonitored_frequency".
- Feature: Assume statistics metadata is empty, in case it could not be read from the database.
- Refactor: Minor fixes and improvements.

### 7.0.3

- Bug: Fixed statistics computation for symmetric distributions.
- Feature: Added automatic retry for device_code expired session or refresh token.

### 7.0.2

- Refactor: Updated dependencies.

### 7.0.1

- Feature: Updates to new name.
- Feature: Changes to support both 1.x and 2.x version of SQLAlchemy.
- Feature: Added a command to create BYOM table.
- Refactor: Various quality of life and performance improvements.

### 7.0.0.0

- Refactor: Refactor data statistics API / internals to be simpler (breaking changes).
- Feature: Switch CLI authentication to use `device_code` grant flow.
- Feature: Add raw Bearer token support for authentication (SDK).

### 6.1.4

- Feature: Document user facing stats functions.
- Feature: Improve end user error messaging related to stats.
- Bug: Fix `aoa init` and `aoa add` not working due to refactor in 6.1.3.

### 6.1.3

- Feature: Improve error messages for statistics calculations and validation.
- Feature: Use [aia](https://pypi.org/project/aia/) for AIA chasing for missing intermediate certificates.
- Bug: No defaults for set when BYOM and VAL DBs not configured on connections.
- Bug: Fixed requirement versions to ensure more stability across python versions.
- Bug: Fixed slow CLI for some commands due to repeated server initialization.

### 6.1.2

- Bug: Work around problems with special character in passwords for teradataml.

### 6.1.0

- Cleanup: Remove all non OAuth2 (JWT) authentication methods.
- Cleanup: Remove `aoa configure`.
- Feature: Improve error messages to user on CLI.
- Feature: Add `aoa link` for linking project to repo locally.
- Bug: Don't show archived datasets.
- Bug: Fix issue with `aoa feature create-table`.

### 6.0.0

- Feature: Support API changes on ModelOps 06.00.
- Feature: CLI DX improvements.
- Feature: Add Telemetry query bands to session.
- Feature: `aoa feature` support for managing feature metadata.
- Feature: `aoa add` uses reference git repository for model templates.
- Feature: Improve DX from Notebooks.

### 5.0.0

- Feature: Add simpler teradataml context creation via aoa_create_context.
- Feature: Add database to connections.
- Feature: Support for human-readable model folder names.
- Feature: Improve UX of aoa run.
- Feature: Improved error messages for users related to auth and configure.
- Refactor: Package refactor of aoa.sto.util to aoa.util.sto.
- Bug: cli listing not filtering archived entities.
- Cleanup: Remove pyspark support from CLI.

### 4.1.12

- Bug: aoa connection add now hides password symbols.
- Bug: sto.util.cleanup_cli() used hardcoded models table.
- Feature: sto.util.check_sto_version() checks In-Vantage Python version compatibility.
- Feature: sto.util.collect_sto_versions() fetches dict with Python and packages versions.

### 4.1.11

- Bug: aoa run (evaluation) for R now uses the correct scoring file.

### 4.1.10

- Bug: aoa init templates were out of date.
- Bug: aoa run (score) didn't read the dataset template correctly.
- Bug: aoa run (score) tried to publish to prometheus.
- Bug: aoa run (score) not passing model_table kwargs.

### 4.1.9

- Bug: Histogram buckets incorrectly offset by 1 for scoring metrics.

### 4.1.7

- Bug: Quoted and escaped exported connection environmental variables.
- Bug: aoa clone with `path` argument didn't create .aoa/config.yaml in correct directory.
- Feature: aoa clone without `path` now uses repository name by default.
- Feature: update BYOM import to upload artefacts before creating version.

### 4.1.6

- Feature: Added local connections feature with Stored Password Protection.
- Feature: Self creation of .aoa/config.yaml file when cloning a repo.
- Bug: Fix argparse to use of common arguments.
- Feature: Support dataset templates for listing datasets and selecting dataset for train/eval.
- Bug: Fix aoa run for batch scoring, prompts for dataset template instead of dataset.
- Bug: Fix batch scoring histograms as cumulative.

### 4.1.5

- Bug: Fix computing stats.
- Feature: Autogenerate category labels and support for overriding them.
- Feature: Prompt for confirmation when retiring/archiving.

### 4.1.4

- Feature: Retiring deployments and archiving projects support.
- Feature: Added support for batch scoring monitoring.

### 4.1.2

- Bug: Fix computing stats.
- Bug: Fix local SQL model training and evaluation.

### 4.1

- Bug: CLI shows archived entities when listing datasets, projects, etc.
- Bug: Adapt histogram bins depending on range of integer types.

### 4.0

- Feature: Extract and record dataset statistics for Training, Evaluation.

### 3.1.1

- Feature: `aoa clone` respects project branch.
- Bug: support Source Model ID from the backend.

### 3.1

- Feature: ability to separate evaluation and scoring logic into separate files for Python/R.

### 3.0

- Feature: Add support for Batch Scoring in run command.
- Feature: Added STO utilities to extract metadata for micro-models.

### 2.7.2

- Feature: Add support for OAUTH2 token refresh flows.
- Feature: Add dataset connections api support.

### 2.7.1

- Feature: Add TrainedModelArtefactsApi.
- Bug: pyspark cli only accepted old resources format.
- Bug: Auth mode not picked up from environment variables.

### 2.7.0

- Feature: Add support for dataset templates.
- Feature: Add support for listing models (local and remote), datasets, projects.
- Feature: Remove pykerberos dependency and update docs.
- Bug: Fix tests for new dataset template api structure.
- Bug: Unable to view/list more than 20 datasets / entities of any type in the cli.

### 2.6.2

- Bug: Added list resources command.
- Bug: Remove all kerberos dependencies from standard installation, as they can be now installed as an optional feature.
- Feature: Add cli support for new artefact path formats.

### 2.6.1

- Bug: Remove pykerberos as an installation dependency.

---

_Copyright 2025 Teradata. All Rights Reserved._
