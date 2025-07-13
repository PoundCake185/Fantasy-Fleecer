# Fantasy-Fleecer

Fantasy-Fleecer is a work-in-progress Python project designed to interact with the Sleeper API to retrieve fantasy football dynasty league roster data. The goal is to export league rosters into a JSON format, which can then be uploaded to tools like ChatGPT for analysis and trade proposal suggestions.

## Features

- Fetches team and roster data from the Sleeper API
- Exports league data to JSON for easy sharing and analysis
- Lays groundwork for future trade analysis tools

## Installation

1. Clone the repository:
```bash
   git clone git@github.com:PoundCake185/Fantasy-Fleecer.git
   cd Fantasy-Fleecer
```

2. Install dependencies:

Use a virtual environment if you're not a bum
```bash
   pip install -r requirements.txt
```

## Usage

Run the main application to fetch and export league data:
python main.py
Follow prompts or edit configuration as needed to specify your league.

### Updating KTC Data
To update KeepTradeCut (KTC) data found in `ktc_latest.csv`, you can use the `ktc_to_csv.py` script found from [this scraper repo](https://github.com/PoundCake185/KeepTradeCut-Scraper). Its my fork but credit to [ees4](https://github.com/ees4).

This script allows you to export player data to a CSV file, which can be useful for analysis or integration with other tools.

## Project Structure

- main.py - Entry point for the application
- requirements.txt - Python dependencies

## Contributing

Contributions are welcome! Please open issues or submit pull requests.
I want all work to be AI generated. If the code looks like it was written by a human, I will not accept it.
If you have a suggestion, please use ChatGPT to write the code and then submit it.

## License

MIT License. See LICENSE for details.

## Contact

For questions or feedback, contact [your GitHub profile link].