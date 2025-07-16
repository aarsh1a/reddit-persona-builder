# reddit user persona builder

a python tool that analyzes a reddit user's post and comment history to generate a detailed marketing-style persona using hugging face's free llm apis.

## features

- fetches user's recent posts & comments via the reddit api
- analyzes content using free llm models from hugging face
- generates detailed personas with demographic info, interests, motivations, etc.
- includes citations from posts/comments that support each trait
- outputs a professionally formatted persona document

## setup

### prerequisites

- python 3.8+
- reddit api credentials
- hugging face account (free)
### installation

1. clone this repository

2. install dependencies

3. create a `.env` file with your api credentials

## usage

run the script with a reddit username:

the generated persona will be saved as `persona.txt` in the current directory.

## example personas

the repository includes example personas generated for the following users:
- [spez](/persona_spez.txt)
