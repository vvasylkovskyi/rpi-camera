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
