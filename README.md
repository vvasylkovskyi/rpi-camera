# rpi-camera
A Raspberry Pi Camera integration code


## Adding Pycamera2

```sh
sudo apt install python3-picamera2
```

## Install Poetry on Linux

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Then add Poetry to your shell profile:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

Append the above line to ~/.bashrc, then reload:

```sh
source ~/.bashrc
```


Use right version of python for poetry

```sh
poetry env use $(which python3)
```


## Install Python on Linux

```sh
sudo apt update
sudo apt upgrade
```

### Install dependencies for building Python:

```sh
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl
```

### Download Python 3.13.1 source:

Go to the Python downloads page and find the 3.13.1 source, or use wget to download it directly:

```sh
wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tgz
tar -xvzf Python-3.13.1.tgz
cd Python-3.13.1
```

### Configure and compile Python:

```sh
./configure --enable-optimizations
make -j$(nproc)
```

### Install Python:

```sh
sudo make altinstall
```

### Verify installation:

```sh
python3.13 --version

```

### Create a symlink:

Assuming Python 3.13.1 is installed under /usr/local/bin/python3.13 (default location when built from source), create the symlink:

```sh
sudo ln -sf /usr/local/bin/python3.13 /usr/bin/python3

```