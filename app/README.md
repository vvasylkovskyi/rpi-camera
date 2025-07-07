# Raspberry Pi Camera

Here we will talk about the step by step of the development of the raspberry pi camera. 


## Building Docker Image for Raspberry Pi

First things first, we need to ensure that the docker image builds a server for the Pi. Raspberry Pi usually have different hardware architecture from the traditional linux systems like the ones that run on Github CI. This means that docker image built on Github CI will be build for architecture that is incompatible with raspberry pi hardware. So there is already a challenge here that we will tackle in the next section. There are several methods to solve this such as building using architecture simulation tools like QEMU. However, I never managed to make it work this way. 

The other way of solving this problem is to build docker image on the raspberry pi itself. This way the image will be built using same architecture as the device where the image is meant to run. Github offers to run their pipelines using self-hosted runners, so we will describe in the next section about how to make a Raspberry Pi a Github Runner. 

### Promote Raspberry Pi to become a Github Runner

You can read this article [Setting Up a Raspberry Pi 4B as a GitHub Actions Self-Hosted Runner](https://www.vvasylkovskyi.com/posts/configuring-rpi-as-github-runner). This explains very well about the manual steps required to make a raspberry pi a runner. We can also automate this process with ansible. 

#### Ansible code to promote raspberry pi to Github Runner 

In `infra/ansible-configurations/roles/promote_to_github_runner/tasks/main.yml` I wrote an ansible script that applies the manual configurations above to the raspberry pi. After that, we can start running our pipeline using raspberry pi. You can also have a look at the CI here `.github/workflows/main.yaml`. Note that this pipeline runs on `self-hosted`

```sh
    runs-on: [self-hosted, ARM64]
```

## Deploying new app version on device restart

The next things that I would want to do ideally is to make CI deploy the new image on my device. But for now I don't have device exposed, it only works in my local network. So the next best thing we can do is to force re-deploy on device restart. We can do it using ansible configuration - where we will create a `systemd` daemon that will pull docker image and start the container every time the device has to start. 

This can be found at `infra/ansible-configurations/roles/docker_start_container_on_boot/tasks/main.yml`. 

Once you have the script, run `ansible-playbook -i inventory/all.yml playbooks/playbook.yml --vault-password-file .vault_pass.txt`. 

Restart the Rpi device and observe that your server has reloaded, and with the new version of the app.


## Device Setup workflow 

1. Make sure you have all the necessary environment variables in `.env` file, `.vault_pass.txt` and you have created the empty vault file with `ansible-vault create secrets.yml`. Make sure that `secrets.yml` is gitignored as well.
2. Encrypt the secrets for ansible by running `./infra/ansible-configurations/update-secrets.sh`
3. Bootstrap device only once by running `ansible-playbook -i inventory/all.yml playbooks/bootstrap_device.yml --vault-password-file .vault_pass.txt`.
4. Launch EC-2 Instance on AWS to serve as a reverse proxy, and use the SSH key created in the previous step. Note, terraform is using remote backend so you may need to comment it first for the resources to create locally. Just run once:
  - `terraform init`
  - `terraform apply --auto-approve`.
5. Update the secrets and start reverse ssh tunnel running: `ansible-playbook -i inventory/all.yml playbooks/start_reverse_tunnel.yml --vault-password-file .vault_pass.txt`
6. Open your app remotely on `your-domain.com` defined in `./infra/terraform/terraform.tfvars:domain_name`. 



## System packages

Note there are some packages that can only exist on device, we need to be aware that this code will only run on the device with system packages. 

So far we have `python3-picamera2` that is not available on `PyPI`. So we have installed this package using ansible: 

```sh
apt install -y python3-picamera2
```

Further, enable python virtual environment to access system packages we will run with `python -m venv` with `--system-site-packages`

```sh
.PHONY: new-venv
new-venv:
	@echo "Creating virtual environment with access to system packages"
	@$(PYTHON) -m venv --system-site-packages "$(VENV_PATH)"
```