# Introduction 
Boman CLI is a Orchestration script written in python to run security scans on the local or CI/CD environment and upload the results to Boman.ai SaaS server.


# Installation

` pip install boman-cli`

# Getting Started

###  For help

` boman-cli -h` 

### Authentication of project has been moved from boman.yaml to boman-cli

`boman-cli -a run -at <project token> -ct <customer token>`

To obtain `project token` and `customer token`. Go to SaaS platform. Click on Apps -> app menu of the particular app -> Get Scan Token 


### To test the boman cli server

` boman-cli -a test-saas`


### To test the boman configuration written in boman.yaml file

` boman-cli -a test-yaml`

### To run the scan 

` boman-cli -a run`

### To run the scan on specific Boman SaaS URL (On prem)

` boman-cli -a run -u {URL}`


### To fail build on high/medium/low finding is detected

`boman-cli -a run -fb {severity}`

Severity can be high, medium or low.

Example: boman-cli -a run -fb high


### To custom change the boman.yaml file, pass the custom file name as input for -config argument

`boman-cli -a run -config <custom_boman_yaml_file_name_here>`

Example: boman-cli -a run -config ./customboman.yaml


### To inject custom zap auth session script file, pass the custom file name as input for -zap_session_script argument

`boman-cli -a run -zap_session_script <custom_session_script_file_name_here>`

Example: boman-cli -a run -zap_session_script ./session.js


### To pass semgrep api token, pass it with -semgrep_token

`boman-cli -a run -semgrep_token <value>`




# Error codes

0  : Successfull scan
1  : Server/SaaS error
2  : Auth error
3  : Docker/System error
4  : Misconfig error




### Release Note:

### 2.5.3
- **SLA** - new feature. Build fail SLA has been introduced it can be configured in SaaS platform. Build fails if the condition is met menioned in SaaS. Check Build SLA in SLA menu for more info.

### 2.5.1
- **SBOM** Added New fields as per certin

### 2.5.0
- **New Tool** Added Opengrep as default tool for SAST

### 2.4.11
- **Major Bug Fix** Multi times hashing has been fixed.

### 2.4.10
- **New:** Reachability Analysis add for SCA. Reachable can be viewed in every vulnerability (findings Page).

### 2.4.9
- **Feature:** Merged the Zaparg argument with the 2.4.8 build


### 2.4.8
- **New:** Semgrep pro (API) integration. Navigate to **Integrations -> Semgrep pro/api** in the Boman SaaS to setup Semgrep pro.

- **New:** Reachability analysis for SCA enabled.

- **Feature Request:** when Failbuild is configured. Boman should not take false positive, Accepted Risk, Not applicable and Muted vulnerabilities into account.

### V2.4.7
- **BUG:** Failing build if token is not configured.

### V2.4.6
- **New:** Semgrep CLI integration. Pass the semgrep token as -semgrep_token {value}.

### V2.4.5
- **New:** Snyk API integration. Navigate to **Integrations -> Snyk** in the Boman SaaS to setup Snyk.

### V2.4.4
- Minor bug fix + V2.4.3

### V2.4.3
- **New:** SonarCloud API integration. Navigate to **Integrations -> SonarCloud** in the Boman SaaS to setup SonarCloud.

### V2.4.2
- **New:** Advanced ZAP setup. Navigate to **Integrations -> OWASP ZAP -> Integrate -> enable Advance Zap Authentication** in the Boman SaaS to enable Advanced Zap setup.


### V2.4.1
- **New:** New CLI arguments for ZAP custom arguments.


### V2.4.0
- **New:** optimized CLI and Progression indicator in Boman SaaS.

### V2.3.0
- **New:** The pipeline configuration has been relocated from `boman.yaml` to the SaaS platform. Navigate to **Apps -> App menu -> Configure pipeline** to set it up. The current `boman.yaml` configuration will remain functional until it is officially deprecated.


### V2.2.0
    - New scan added: IaC.

### V2.1.1
    - Ignore files or directory for SAST and SCA

### V2.1
    - New scan added: SBOM.

### V2.0

    - New scan added: Container scan.
    - New Tool added for SCA scan type.


### V1.9:

    - [Bug fix] Updated the Upload Logs success message

Released on: 21 June 2024




### V1.8:

    - Adapted to our new Boman SaaS platform

Released on: 20 June 2024




### V1.7:

    - Fixed docker-request libraries issue
    - Zap Authenticated scan 
    - Fetch Git details
    - custom boman.yaml and zap session script load option

Released on: 21 May 2024




