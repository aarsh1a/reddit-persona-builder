# Reddit User Persona Builder

A Python tool that analyzes a Reddit user's post and comment history to generate a detailed marketing-style persona using Hugging Face's free LLM APIs.

## Features

- Fetches user's recent posts & comments via the Reddit API
- Analyzes content using free LLM models from Hugging Face
- Generates detailed personas with demographic info, interests, motivations, etc.
- Includes citations from posts/comments that support each trait
- Outputs a professionally formatted persona document

## Setup

### Prerequisites

- Python 3.8+
- Reddit API credentials
- Hugging Face account (free)

### Installation

1. Clone this repository

2. Install dependencies

3. Create a `.env` file with your API credentials

## Usage

Run the script with a Reddit username:


The generated persona will be saved as `persona.txt` in the current directory.

## Example Personas

The repository includes example personas generated for the following users:
- [spez](/persona_spez.txt)

## License

MIT