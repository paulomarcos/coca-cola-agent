# CokeConnect AI: Hyperlocal Marketing Agent

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Framework: LangChain](https://img.shields.io/badge/Framework-LangChain-purple.svg)
![Powered by: OpenAI](https://img.shields.io/badge/Powered%20By-OpenAI-black.svg)

CokeConnect AI is a sophisticated multi-agent autonomous system designed to solve the challenge of hyperlocal marketing for global brands. This project demonstrates how a team of specialized AI agents can monitor local events, analyze their marketing potential, and generate complete, culturally-aware creative campaign packages, including text and image assets.

_Disclaimer: This repository and its owner are not associated with Coca-Cola in any shape or form_.

---

## 📖 Table of Contents

- [Motivation](#-motivation)
- [How It Works: The Agentic Pipeline](#-how-it-works-the-agentic-pipeline)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Setup and Installation](#-setup-and-installation)
- [Usage](#-usage)
- [Example Output](#-example-output)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 🎯 Motivation

Global brands like Coca-Cola operate with a unified message, but true market resonance happens at the local level. A city-wide festival, a sports team's victory, or a sudden heatwave are all powerful marketing moments that traditional, slow-moving campaign workflows are unable to capitalize on.

This project was built to answer the question: **"Can an autonomous AI system bridge the gap between global brand strategy and hyperlocal execution?"**

The result is CokeConnect AI, a system that acts as a team of marketing experts, autonomously generating timely and relevant campaign ideas that would be impossible to create at scale with human teams alone.

---

## Result Example

The example can be found in [2025-09-14.md](2025-09-14.md).

This example was generated with only the `Tokyo` source. I recommend you using all the three sources, as well as 
more that you can come up on your own, to see the full benefits of this agentic workflow.

## 🤖 How It Works: The Agentic Pipeline

The system is managed by a central Orchestrator that runs on a daily schedule. It directs a pipeline of specialized agents, each with a distinct role.

The workflow begins with the EventScanner agent scanning local websites. If the TrendAnalyzer agent identifies a high-potential event, it's passed to the CreativeDirector to create a strategic brief. This brief is then sent to both the Copywriter and VisualStrategist agents to work in parallel. The VisualStrategist's output is used by the ImageCreator to generate a visual. Finally, the Orchestrator aggregates all these assets into a final campaign package.

### The Agents

* **EventScanner:** The "eyes" of the operation. Scrapes local news and event websites for potential opportunities.
* **TrendAnalyzer:** The "strategist." Analyzes each event against Coca-Cola's brand values and assigns a `marketing_potential_score`.
* **CreativeDirector:** The "brain." Takes high-potential events and creates a strategic brief defining the campaign's angle, emotion, and message.
* **Copywriter:** The "voice." Generates compelling, localized ad copy, slogans, and social media posts based on the creative brief.
* **VisualStrategist:** The "art director." Translates the creative brief into a rich, detailed prompt for a text-to-image model.
* **ImageCreator:** The "artist." Executes the image prompt, generating the final visual asset for the campaign.
* **MarkdownWriter:** Creates the publications in Markdown, to simplify the task of posting it on Social Media.
---

## ✨ Key Features

* **Autonomous Operation:** The system runs automatically on a daily schedule via the `orchestrator.py` script.
* **Multi-Agent System:** Utilizes a team of specialized agents, each with its own prompt and purpose, to handle complex, multi-step tasks.
* **Hyperlocal Focus:** Designed to generate campaigns for specific cities (e.g., São Paulo, New York, Tokyo), with agents capable of cultural and linguistic nuance.
* **End-to-End Generation:** The pipeline covers the entire creative process, from raw data ingestion to the creation of final text and image assets.
* **Modular & Extensible:** Each agent is a self-contained module, making it easy to add new capabilities or agents to the pipeline.

---

## 📁 Project Structure

The project is organized into a clean and understandable hierarchy. The root directory contains several key directories and all the Python scripts for the agents.

For example, the `campaign-images` directory is where all generated images are saved, `campaign-packages` holds the final JSON outputs, `logs` contains the orchestrator's log file, and `prompts` holds all the .txt system prompts for the agents.

---

## 🛠️ Setup and Installation

Follow these steps to get the CokeConnect AI system running on your local machine.

### Prerequisites

* Python 3.9 or higher
* Git
* OpenAI API Key -> to generate the campaign text and image

### 1. Clone the Repository

First, clone the repository from GitHub and navigate into the project directory.

### 2. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies. Create and activate a new virtual environment in the project directory.

```bash
python -m venv venv
```
Then, activate it with
```bash
source venv/bin/activate
```

### 3. Install Dependencies

To install dependencies, run:
```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the file `sample-env.txt` to `.env` in the root of the project directory. Inside this file, you must add your OpenAI API key. 

```bash
cp sample-env.txt .env
```

Then, edit `.env` and add your OpenAI API key.

```bash
vim .venv
```

---

## ▶️ Usage

The entire system is managed by the orchestrator.

1.  **Start the Orchestrator:**
    To start the system, run the `orchestrator.py` script from your terminal with `python -m orchestrator.py`

2.  **What Happens Next:**
    The script will start and log that the scheduler is configured to run daily (default is 3:00 AM). The orchestrator will now wait in the background for the next scheduled run time. All activities will be logged to the console and saved in the `logs/orchestrator.log` file.

3.  **Running a Test Immediately:**
    To test the full pipeline immediately without waiting, you can edit the `orchestrator.py` file to uncomment the test-run line near the end of the script.

4.  **Finding the Output:**
    All outputs are saved to their respective directories. For example, final campaign packages are saved in the `campaign-packages/` directory, and the generated PNG images are saved in the `campaign-images/` directory.

---

## 📊 Example Output

After a successful run, the system generates a comprehensive JSON package file and a corresponding image file.

The generated JSON package is a structured object containing all the information about the campaign. For example, it includes a `source_event` key holding the original event details, a `creative_brief` key with the strategic output from the Director, a `text_assets` key with the generated copy, and a `visual_assets_status` key which provides the filename of the created image.

---

## 🚀 Future Improvements

This project provides a solid foundation that can be extended in several ways:

* **Human-in-the-Loop:** Add an `Approval_Agent` to send completed campaign packages to a Slack channel or email for human review before publishing.
* **Publisher Agent:** Create an agent that uses social media APIs to automatically post the approved content to platforms like X (Twitter) or Instagram.
* **Performance Analyst:** Build an agent that monitors the engagement metrics of published campaigns and generates performance reports, creating a closed-loop system.
* **Vector Database for Memory:** Incorporate a vector DB to give agents long-term memory of past campaigns, preventing duplicate ideas and learning from what performed well.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.