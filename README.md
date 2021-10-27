# PKPassCreator

This is a companion script for the blog

## Installation

First clone the repository:

```bash
git clone https://github.com/TranzerDev/PKPassCreator.git
cd PKPassCreator
```

Then, install the requirements:

```bash
pipenv shell
pipenv install
```

## Usage

Run the following in your terminal for a quick dialog flow:

```bash
python main.py
```

To skip the dialog flow you can give the following flags to the command:

- To provide the certificate password: `--certificate-password`
- To provide the pass type identifier linked to the certificate `--pass-type-identifier`
- To provide the team identifier linked to the certificate `--team-identifier`
- To provide the path to the certificate `--certificate-path`
- To provide the path to the Apple Worldwide Developer Relations Certification Authority.pem `--wwdr-path`
