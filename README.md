<h1 align="center">Cloud Project</h1>

This repo is the backend of the cloud project. 
If you want to see the streamlit app, go [here](https://github.com/Maskrpone/cloud-project).
Our project is divided into two repositories : @FIXME : add url to frontend 

## Links 

- [GitHub repo of the streamlit app](https://github.com/Maskrpone/cloud-project)
- [Public API URL](https://cloud-project-api-container.victorioushill-fba44ff1.uksouth.azurecontainerapps.io)

### Context

A lot of women struggle with nutrition during their menstrual cycle.
Depending on the phase of this cycle, their body's needs variate a lot.
This is why we had the idea to make a tool that would prove actually useful for selfcare.
This tool is able to determine in which phase of the cycle a woman is and, based on that, 
proposes some nutrients that would help with struggles linked to this specific phase (e.g : high iron levels during the period phase to compensate the blood).
Because of its extensive database, it can proposes different foods for the same phase, making it easy to find something likeable. 
This tool is also able to recommand some recipes based on Marmiton.

### Disclaimer

This tool is by no mean a medical device, and can't replace some medical advices given by a professional healthcare.
The recipes might need to be double checked.

## Technical description 

### Built with

The project (backend + frontend) was built using :

- [Streamlit](https://streamlit.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Terraform](https://developer.hashicorp.com/terraform)
- [Docker](https://www.docker.com/)
- [Azure](https://azure.microsoft.com/fr-fr/get-started/azure-portal/)


> [!NOTE]
> Even the github repositories were configured using terraform (under `github-config/` folders), making it easy to explore.

### Infrastructure 

The setup of the infrastructure can be found in `infra/`.

All of the infrastructure is hosted on Azure platform in one resource group.
This resource group is randomly generated, preventing *name already in use* errors using **random_pet**. The same have been done for the mssql server, which host the SQL database of foods and all their detailed descriptions.

An ACR is created to securely store the images of the applications.
Both API and streamlit frontend were defined as Azure container apps (ACA).

<details>
<summary>Details about some specific terraform configurations</summary>

The following code shows the declaration of the SQL DB. 
To make it as cost efficient as possible, the sku_name was set to GP_S_GEN5_1, one of the most basic sku possible, and a auto_pause setting was set to 60 minutes, making the DB go idle after 1 hour of inactivity.

```terraform
resource "azurerm_mssql_database" "db" {
  name      = var.sql_db_name
  server_id = azurerm_mssql_server.server.id

  # Cost efficiency
  sku_name                    = "GP_S_Gen5_1"
  auto_pause_delay_in_minutes = 60
  min_capacity                = 0.5
}
```

The following chunk describe the firewall configuration. Puting 0.0.0.0 IP address as allowed configures the API to be accessible for any other Azure services in the resource group.

```terraform
# Firewall configuration to allow all Azure services to communicate 
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
```
</details>

### Installation

To deploy this infrastructure, you first need : 

- An Azure account
- az CLI installed and your account logged in
- docker
- terraform 

> [!INFOS]
> To log in to az CLI, simply run `az login`, and it will open a web page.

The infrastructue is deployable using terraform CLI :
```bash
terraform plan
terraform apply -target=azurerm_container_app_environment.env
```

> [!WARNING]
> `-target=azurerm_container_app_environment.env` is required for first deployment

As the ACR does not already have the docker images, you first need to push the images to the ACR, and then you can finish by doing `terraform apply`.

> [!TIPS]
> You need to log in into the acr before pushing.
> Use `az acr login --name <ACR-NAME>`
> You can find the name on the Azure portal, 
> or by running : `az acr list --resource-group <name-of-resource-group> --output table`. The resource group gives its name in the terraform outputs.

To push the docker image of the API : 

```bash
docker build -t <ACR-LOGIN-SERVER>/api-container:latest .
docker push cloudprojectapiacr.azurecr.io/api-container:latest 
```

You can then proceed to finish the deployment by doing `terraform apply`.

We wanted to automate the deployment of the docker image using GitHub Actions, but this action is impossible given the low authorizations given to Student accounts.

In this case, the creation of a service principal was not allowed to handle the login.

___

### Data provision

The data on which is based our tool is from the [swiss nutrients database](https://valeursnutritives.ch/fr/telechargement/).

The data cleansing was done using the `scripts/populate.py` script.
This script : 
- remove unused columns, 
- rename them for better access, 
- give them a type, 
- replace values (e.g : 't.r.' in a float column means 'traces', so the script approximate it to 0),
- remove N/As and duplicates

The original dataset is provided under `data/` folder, to prevent URL changes.

___

## API

The API contains two main routes : "/top-foods/", and "/food-by-phase/".

"/top-foods/" is a GET method taking a nutrient and a percentage as parameters, and return the top percentage of foods. 

Example : nutrient=phosphore&percentage=0.2 return the top 20% foods (above the 80th percentile) with the highest rates of phosphore.

"food-by-phase" is the other GET main method, taking a phase and a percentage. It returns a list of foods containing some good nutrients for the specified phase.

Example : phase=ovulatoire&percentage=0.05 will return the top 5% foods containing zinc, fibers, C vitamin, selenium.

___ 

## GitHub configuration 

> [!NOTE]
> The GitHub repositories are configured using Terraform, in the `github-config/`

The github repositories were setup following a Git Flow based approach.
All the feature are done on "feature-*" branches, and merged on the "dev" branch.
Only when the dev branch is stable and all features for a specific need are merged, the dev branch is merged on main.

The main and dev branches are protected, meaning to add something, it can only be done by opening a pull request.

Pull requests on dev and main trigger a CI checking formatting and linting (for better readability), and unit test using pytest.

___

### A (side) note on *.nix files

At the root of this project, you will find three files related to Nix: flake.nix, flake.lock, and shell.nix.

If you are unfamiliar with Nix or NixOS, these files are simply the tools that guarantee that this project works and its development environment is the same anytime. 
They solve common development issues like "It works on my machine!"

Here is a breakdown of what each file is and why it's convenient:
flake.nix

What it is: This is the main configuration file, acting as the master recipe for the project. It declares all the project's dependencies (other packages, tools, and code) and defines what the project ultimately provides (e.g., a specific development environment).

Convenience: It makes the project fully reproducible. It ensures that everyone is asking for the same set of tools and packages defined in a structured, standard way.

flake.lock

What it is: A machine-generated file that "locks down" the exact versions of every dependency listed in flake.nix. Instead of saying "get the latest version of library X," this file records the precise version, commit hash, or source URL used when the project was last known to work.

Convenience: It guarantees stability. If a dependency gets updated or breaks upstream, our project will not be affected unless this lock file is manually updated. This ensures a consistent environment for all developers and CI/CD pipelines.

shell.nix (or the development shell)

What it is: This file defines a temporary, isolated development environment specific to this project. It lists all the necessary tools (compilers, interpreters, linters, etc.) needed to build and work on the code.

Convenience: It enables effortless onboarding. A developer can run one command (like nix develop) and instantly get all the required tools without installing them globally or worrying about version conflicts with other projects on their computer. When they exit the shell, their system returns to its previous state.

Of course, it is not mandatory for development nor deployment. But it was a nice quality of life, as reproducibility is guaranteed, as opposed to docker which runs imperative commands (apt upgrade), and integration was better because it simply modifies your PATH and shell (as opposed to docker which requires complete filesystem/network isolation). 
