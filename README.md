### Hexlet tests and linter status:
[![Actions Status](https://github.com/Unt0ten/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Unt0ten/python-project-83/actions)
[![Python CI](https://github.com/Unt0ten/python-project-83/actions/workflows/my-test.yml/badge.svg)](https://github.com/Unt0ten/python-project-83/actions/workflows/my-test.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/8539d9131daeb4fc1407/maintainability)](https://codeclimate.com/github/Unt0ten/python-project-83/maintainability) 

### Description
[SEO Page Analyzer](https://page-analyzer-8v17.onrender.com) is a web tool to check Serch Engine Optimization support of a given URL.

### Requirement
* Python
* Poetry
* Postgres
### Installation
**Setting up enviroment**
```bash
git clone https://github.com/Unt0ten/python-project-83.git
cd seo-page-analyzer
make build
```
Configure .env in the root folder
```
cp .env_example .env
```

**Dev**
```bash
make dev
```

**Prod**
```bash
make start
```