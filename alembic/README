# Fluxo Ágil's API

## Setup

Python 3.11 is required.

1. Create new poetry env.

   ```bash
   poetry env use python3.11 # or another 3.11 path
   ```

2. Install dependencies with poetry

   ```bash
   poetry install
   ```

3. Set up databases.
   ```bash
   docker compose up
   ```
4. Set up initial data.
   ```bash
   poetry run bash init.sh
   ```
5. Run the app.
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Scraper

To recommend discipline flows, it is necessary to have information on the structure of departments, disciplines, curricula, etc.

As SIGAA does not provide an API to get the data, it is necessary to use a scraper.

The diagram below shows from which SIGAA pages data can be obtained from (you can also access the diagram through the [link](https://whimsical.com/scraper-3bBi6EMqxtq6z6HzdtGDQk@2Ux7TurymMmNus31JQQL)).

In the future, scraper should have its own repository.

![Image](/images/scraper-diagram.png)
