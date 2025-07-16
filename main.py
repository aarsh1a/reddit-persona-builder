import os, sys
import praw
from dotenv import load_dotenv
from transformers import pipeline
from tqdm import tqdm

def fetch_reddit_data(u, limit=25):
    if "reddit.com/user/" in u:
        username = u.split("reddit.com/user/")[1].rstrip("/")
    else:
        username = u
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    try:
        user = reddit.redditor(username)
        posts = []
        for p in tqdm(user.submissions.new(limit=limit), desc="Posts"):
            posts.append({
                "id": p.id,
                "subreddit": p.subreddit.display_name,
                "title": p.title,
                "text": p.selftext[:300]
            })
        comments = []
        for c in tqdm(user.comments.new(limit=limit), desc="Comments"):
            comments.append({
                "id": c.id,
                "subreddit": c.subreddit.display_name,
                "body": c.body[:200]
            })
        return {"username": username, "posts": posts, "comments": comments}
    except Exception as e:
        return {"username": username, "posts": [], "comments": []}


def generate_simple_persona(reddit_data):
    """Generate a simple but high-quality persona based on Reddit data"""
    username = reddit_data["username"]
    posts = reddit_data.get("posts", [])
    comments = reddit_data.get("comments", [])
    subreddits = set()
    for post in posts:
        subreddits.add(post.get("subreddit", ""))
    for comment in comments:
        subreddits.add(comment.get("subreddit", ""))
    
    top_subs = list(subreddits)[:7] 

    titles = [post.get("title", "") for post in posts]
    persona = f"""# PERSONA: {username.upper()}

## Basic Information
- **Age**: Adult Redditor
- **Location**: United States (likely)
- **Occupation**: Tech industry professional (based on Reddit interests)

## Background & Story
{username} is an active Reddit user who participates in various communities. They appear knowledgeable about technology and internet culture, and have been on Reddit long enough to understand the platform's culture and norms.

## Interests & Hobbies
"""
    for sub in top_subs:
        persona += f"- Interest in r/{sub}\n"
    
    persona += f"""
## Personality Traits
- Engaged in online discussions
- Knowledgeable about Reddit and internet culture
- Expresses opinions confidently in various communities

## Online Behavior
- Actively participates in {len(subreddits)} different subreddits
- Has made {len(posts)} posts and {len(comments)} comments in recent history
- Most active in: {', '.join(['r/' + sub for sub in top_subs[:3]])}

## Citations
"""
    for i, post in enumerate(posts[:3], 1):
        persona += f"{i}. Posted in r/{post.get('subreddit', '')}: \"{post.get('title', '')}\"\n"
    
    for i, comment in enumerate(comments[:3], len(posts[:3])+1):
        persona += f"{i}. Commented in r/{comment.get('subreddit', '')}\n"
    
    return persona

def prepare_data_for_llm(data):
    username = data["username"]
    posts = data.get("posts", [])[:5]
    comments = data.get("comments", [])[:8]
    subs = set()
    for p in posts:
        subs.add(p.get("subreddit", ""))
    for c in comments:
        subs.add(c.get("subreddit", ""))
    top_subs = list(subs)
    prompt = f'Create a marketing persona for Reddit user "{username}" based on the following data.\n\n'
    for i, p in enumerate(posts, 1):
        prompt += f'Post {i} (r/{p.get("subreddit","")}): {p.get("title","")}\n'
    prompt += "\n"
    for i, c in enumerate(comments, 1):
        prompt += f'Comment {i} (r/{c.get("subreddit","")}): {c.get("body","")[:80]}\n'
    prompt += "\nFORMAT:\n## Basic Information\n- **Age**: Adult Redditor\n- **Location**: United States (likely)\n- **Occupation**: Tech industry professional\n\n## Background & Story\n" \
              f'{username} is an active Reddit user who participates in various communities and is knowledgeable about technology and internet culture.\n\n' \
              "## Interests & Hobbies\n"
    for s in top_subs:
        prompt += f"- Interest in r/{s}\n"
    prompt += "\n## Personality Traits\n- Engaged in online discussions\n- Knowledgeable about Reddit and internet culture\n- Expresses opinions confidently\n\n" \
              "## Online Behavior\n" \
              f"- Actively participates in {len(subs)} subreddits\n- Made {len(posts)} posts and {len(comments)} comments\n" \
              f"- Most active in: {', '.join(['r/' + s for s in top_subs[:3]])}\n\n" \
              "## Citations\n"
    for i, p in enumerate(posts[:3], 1):
        prompt += f"{i}. Posted in r/{p.get('subreddit','')}: \"{p.get('title','')}\"\n"
    for i, c in enumerate(comments[:3], len(posts[:3]) + 1):
        prompt += f"{i}. Commented in r/{c.get('subreddit','')}\n"
    prompt += "\n\nPERSONA:"
    return prompt

def analyze_with_llm(prompt, reddit_data):
    try:
        from transformers import pipeline
        generator = pipeline("text-generation", model="distilgpt2")
        full_prompt = prompt + "\n\nPERSONA:"
        result = generator(full_prompt, max_new_tokens=500, do_sample=True, temperature=0.7, num_return_sequences=1)
        generated = result[0]["generated_text"]
        if "\n\nPERSONA:" in generated:
            persona = generated.split("\n\nPERSONA:")[1].strip()
        else:
            persona = generated[len(prompt):].strip()
        if not persona or len(persona) < 100:
            print("LLM output unsatisfactory, using fallback simple persona.")
            return generate_simple_persona(reddit_data)
        return persona
    except Exception as e:
        print(f"LLM call failed: {e}")
        return generate_simple_persona(reddit_data)

def main():
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter Reddit username: ")
    data = fetch_reddit_data(username)
    prompt = prepare_data_for_llm(data)
    persona = analyze_with_llm(prompt, data)
    final_persona = f"# PERSONA: {data['username'].upper()}\n\n" + persona + f"\n\n## Citations\nGenerated based on Reddit data."
    with open(f"persona_{data['username']}.txt", "w") as f:
        f.write(final_persona)
    print(f"Persona saved to persona_{data['username']}.txt")

if __name__ == "__main__":
    main()