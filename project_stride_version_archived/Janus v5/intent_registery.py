"""
Version: 3.0.0 (Slim)
Categories: 6
Total Keywords: ~900
Coverage: High-confidence conversational routing only

DESCRIPTION:
A minimal, zero-overlap intent registry for reliable query classification.
Handles only social lubrication (greetings, farewells, thanks, apologies, 
small talk) and temporal queries. Everything else falls through to semantic 
search or a general-purpose model.

DESIGN PRINCIPLES:
- Zero duplicate keywords across categories (no routing ambiguity)
- High-precision, low-recall (better to miss than misclassify)
- Fast model for all social/temporal intents
- Semantic search handles  domain-specific or slightly complex queries
"""

INTENT_REGISTRY = {
    "GREETINGS": {
        "name": "Greetings & Salutations",
        "description": "Initial hellos, welcomes, and social openers",
        "keywords": [
            "hi", "hello", "hey", "hiya", "howdy", "greetings", "salutations",
            "good morning", "good afternoon", "good evening", "morning", "afternoon", "evening",
            "what's up", "whats up", "sup", "yo", "hola", "bonjour", "ciao", "namaste",
            "heyy", "heyyy", "hii", "hiii", "helloo", "hellooo",
            "hey there", "hi there", "hello there", "hi everyone", "hey everyone", "hello everyone",
            "greetings everyone", "mornin", "evenin",
            "im back", "i'm back", "back again", "here again", "me again",
            "its me again", "it's me again", "first time here", "new here", "just joined", "new user",
            "reaching out", "dropping by", "checking in", "popping in",
            "just saying hi", "just saying hello", "wanted to say hi",
            "you there", "are you there", "anyone there", "is anyone there", "knock knock",
            "can you hear me", "testing",
            "dear assistant", "dear ai", "dear friend", "my friend",
            "good day", "gday", "gd day", "yo yo", "ahoy", "ello", "hai", "hewwo",
            "welcome", "welcome back", "nice to meet you", "pleased to meet you",
            "great to meet you", "good to see you", "nice to see you"
        ],
        "model": "Fast",
        "tool" : None,
        "priority": 1,
    },
    "FAREWELLS": {
        "name": "Farewells & Goodbyes",
        "description": "Parting phrases, session endings, and sign-offs",
        "keywords": [
            "bye", "goodbye", "see you", "see ya", "later", "catch you later",
            "talk to you later", "ttyl", "talk later", "speak later",
            "see you later", "see you soon", "see you tomorrow", "see ya later",
            "later gator", "cya", "adieu", "farewell",
            "peace out", "peace", "im out", "i'm out", "gotta go", "got to go",
            "i gotta run", "i have to go", "i need to go", "must be going",
            "signing off", "logging off", "going offline", "shutting down",
            "thats all", "that's all", "thats it", "that's it", "all done",
            "im done", "i'm done", "were done", "we're done", "done here",
            "finished", "complete", "completed", "wrapping up",
            "thanks bye", "thank you bye", "thanks goodbye", "bye thanks",
            "thanks for everything", "thanks again", "cheers bye",
            "brb", "be right back", "back soon", "stepping away",
            "going for a bit", "away for a while", "taking a break",
            "ill be back", "i'll be back", "bbl", "be back later",
            "end session", "end conversation", "close session", "stop chatting",
            "disconnect", "exit", "quit", "terminate", "kill session",
            "done chatting", "no more questions", "nothing else", "no more",
            "that will be all", "that'll be all", "this is the end",
            "have a good day", "have a great day", "have a nice day",
            "have a good night", "have a great night", "sleep well",
            "take care", "take it easy", "stay safe", "be well",
            "until next time", "until we meet again", "till next time",
            "thank you for everything", "thanks for the help", "grateful for your help",
            "couldn't have done it without you", "you've been great",
            "you've been helpful", "you were very helpful",
            "night night", "good night", "night", "sleep tight", "sweet dreams",
            "adios", "sayonara", "zai jian", "annyeonghi gaseyo", "dosvidanya", "kwaheri",
            "au revoir", "arrivederci", "auf wiedersehen", "tschuss", "bye bye", "byee"
        ],
        "model": "Fast",
        "tool" : None,
        "priority": 1,
    },
    "GRATITUDE": {
        "name": "Gratitude & Appreciation",
        "description": "Expressions of thanks, compliments, and positive feedback",
        "keywords": [
            "thank you", "thanks", "thank u", "thx", "tx", "ty", "tyvm",
            "thank you so much", "thank you very much", "thanks so much",
            "thanks a lot", "thanks a bunch", "thanks a million", "thanks for help", "thanks again",
            "many thanks", "much thanks", "big thanks", "huge thanks",
            "thank you kindly", "thanks kindly", "thank you indeed",
            "appreciate it", "appreciate that", "appreciate your help",
            "i appreciate it", "i appreciate that", "really appreciate",
            "greatly appreciate", "deeply appreciate", "truly appreciate",
            "appreciated", "much appreciated", "greatly appreciated",
            "grateful", "i'm grateful", "im grateful", "so grateful",
            "very grateful", "truly grateful", "eternally grateful",
            "you have my gratitude", "my gratitude", "eternal gratitude",
            "indebted", "im indebted", "i'm indebted", "owe you one",
            "awesome thanks", "fantastic thanks", "wonderful thanks",
            "perfect thanks", "excellent thanks", "brilliant thanks",
            "amazing thanks", "outstanding thanks", "marvelous thanks",
            "you're amazing", "you are amazing", "you're awesome", "you are awesome",
            "you're great", "you are great", "you're fantastic", "you are fantastic",
            "you're brilliant", "you are brilliant", "you're wonderful", "you are wonderful",
            "you're helpful", "you are helpful", "you're the best", "you are the best",
            "you're incredible", "you are incredible", "you're outstanding",
            "you're smart", "you are smart", "you're intelligent", "you are intelligent",
            "good job", "great job", "excellent job", "fantastic job",
            "well done", "nicely done", "brilliantly done",
            "that helped", "that helps", "this helped", "this helps",
            "very helpful", "so helpful", "really helpful", "extremely helpful",
            "incredibly helpful", "immensely helpful", "quite helpful",
            "that worked", "this worked", "it worked", "works perfectly",
            "exactly what i needed", "just what i needed", "precisely what i needed",
            "you nailed it", "nailed it", "spot on", "perfect",
            "you saved me", "you saved my life", "lifesaver", "life saver",
            "you're a lifesaver", "you are a lifesaver",
            "couldn't do this without you", "don't know what I'd do without you",
            "where would i be without you",
            "bless you", "god bless you", "much obliged", "much obliged to you",
            "i owe you", "owe you big time", "i owe you one",
            "you're too kind", "how kind of you", "that's kind of you",
            "thank you for being patient", "thank you for your patience",
            "thank you for understanding",
            "kudos", "cheers", "hats off", "props", "mad respect",
            "you rock", "you rule", "you're a star", "you are a star",
            "legend", "absolute legend", "you're a legend", "you are a legend",
            "savior", "my savior", "you're my hero", "you are my hero"
        ],
        "model": "Fast",
        "tool" : None,
        "priority": 2,
    },
    "APOLOGIES": {
        "name": "Apologies & Corrections",
        "description": "User apologies, self-corrections, and clarifications",
        "keywords": [
            "sorry", "my bad", "my mistake", "my fault", "i apologize", "i apologise",
            "apologies", "i'm sorry", "im sorry", "so sorry", "very sorry",
            "really sorry", "terribly sorry", "deeply sorry", "truly sorry",
            "forgive me", "pardon me", "pardon", "excuse me",
            "i didn't mean", "i didnt mean", "didn't mean to", "didnt mean to",
            "that came out wrong", "wrong choice of words", "poor wording",
            "i meant", "actually i meant", "what i meant", "i mean",
            "correction", "correct that", "let me correct", "to be precise",
            "rather", "or rather", "i should say", "what i should have said",
            "scratch that", "forget that", "ignore that", "disregard that",
            "never mind", "nevermind", "nvm", "dont mind that", "don't mind that",
            "that was wrong", "i was wrong", "that's wrong", "thats wrong",
            "to clarify", "let me clarify", "clarifying", "just to clarify",
            "what i mean is", "in other words", "to put it another way",
            "more specifically", "to be more specific", "to be exact",
            "technically", "technically speaking", "strictly speaking",
            "let me rephrase", "rephrasing", "put differently",
            "said differently", "in simpler terms", "simply put",
            "long story short", "to make it short", "short version",
            "tl dr", "tldr", "tl;dr",
            "i misunderstood", "i see now", "now i understand", "i get it now",
            "oh i see", "oh okay", "ah okay", "i see what you mean",
            "that makes sense", "makes sense now", "crystal clear",
            "misunderstood", "confused", "i was confused", "got confused",
            "oops", "whoops", "uh oh", "oh no", "oh dear",
            "yikes", "darn", "dang", "shoot", "heck",
            "my apologies", "sincere apologies", "heartfelt apologies",
            "please forgive", "beg your pardon", "i beg your pardon",
            "i stand corrected", "my error", "mea culpa"
        ],
        "model": "Fast",
        "tool" : None,
        "priority": 2,
    },
    "CASUAL_TALK": {
        "name": "Small Talk & Personal",
        "description": "Casual well-being checks, AI identity questions, and mood sharing",
        "keywords": [
            "how are you", "how are u", "how r u", "howre you", "how you doing",
            "how you doin", "how's it going", "hows it going", "how is it going",
            "how are things", "hows everything", "how's everything",
            "how have you been", "how've you been", "hows your day",
            "how's your day", "how was your day", "how is your day going",
            "are you okay", "are you alright", "you okay", "you alright",
            "is everything okay", "is everything alright",
            "how do you feel", "how are you feeling", "you feeling okay",
            "who are you", "what are you", "what is your name", "whats your name",
            "your name", "what do i call you", "what should i call you",
            "are you a robot", "are you an ai", "are you human", "are you real",
            "are you alive", "are you conscious", "are you sentient",
            "do you have feelings", "can you feel", "do you have emotions",
            "can you think", "do you think", "are you thinking",
            "what do you look like", "do you have a body", "do you have a face",
            "how old are you", "when were you born", "what is your age",
            "where are you", "where are you located", "where do you live",
            "what language do you speak", "what languages do you know",
            "who made you", "who created you", "who built you", "who developed you",
            "what company made you", "what company built you",
            "what can you do", "what are your capabilities", "what can you help with",
            "what are you good at", "what are your skills",
            "i am happy", "i'm happy", "i am sad", "i'm sad",
            "i am tired", "i'm tired", "i am bored", "im bored",
            "i am excited", "i'm excited", "i am nervous", "i'm nervous",
            "i am stressed", "i'm stressed", "i am worried", "i'm worried",
            "i am angry", "i'm angry", "i am frustrated", "i'm frustrated",
            "i am feeling", "i'm feeling", "i feel", "feeling",
            "i had a good day", "i had a bad day", "terrible day", "great day",
            "my day was", "today was", "yesterday was",
            "i am doing well", "i'm doing well", "doing good", "doing great",
            "not doing well", "not so good", "could be better", "ive been better",
            "i like", "i love", "i enjoy", "i prefer", "i hate", "i dislike",
            "my favorite", "my favourite", "i dont like", "i don't like",
            "i think that", "in my opinion", "imo", "imho",
            "personally i think", "if you ask me", "as far as im concerned",
            "whats new", "what's new", "anything new", "what's going on",
            "whats going on", "what's happening", "whats happening",
            "tell me something", "tell me a joke", "say something funny",
            "make me laugh", "cheer me up", "entertain me",
            "chat with me", "lets chat", "let's chat", "just chatting",
            "can you", "do you know how to", "are you able to",
            "is it possible for you", "can you help me with",
            "do you understand", "can you understand", "do you speak",
            "can you speak", "do you know", "are you familiar with",
            "nice weather", "bad weather", "weather is nice", "weather sucks",
            "its hot", "it's hot", "its cold", "it's cold", "its raining",
            "it's raining", "lovely day", "beautiful day", "gloomy day",
            "i am hungry", "i'm hungry", "i am thirsty", "i'm thirsty",
            "i am sleepy", "i'm sleepy", "i am sick", "i'm sick",
            "i am busy", "i'm busy", "i am free", "i'm free",
            "i am lost", "i'm lost", "i am confused", "i'm confused",
            "i am scared", "i'm scared", "i am surprised", "i'm surprised",
            "i am disappointed", "i'm disappointed", "i am proud", "i'm proud",
            "i am thankful", "i'm thankful",
            "i am lucky", "i'm lucky", "i am unlucky", "i'm unlucky",
            "i am calm", "i'm calm", "i am relaxed", "i'm relaxed",
            "i am anxious", "i'm anxious", "i am depressed", "i'm depressed",
            "i am lonely", "i'm lonely", "i am in love", "i'm in love",
            "i am outraged", "i'm outraged", "i am shocked", "i'm shocked"
        ],
        "model": "Fast",
        "tool" : None,
        "priority": 1,
    },
    "TEMPORAL": {
        "name": "Time & Date Queries",
        "description": "Current time, date, timezone conversions, and calendar queries",
        "keywords": [
            "what time is it", "what's the time", "whats the time", "current time",
            "time now", "time right now", "what time", "tell me the time",
            "do you know the time", "can you tell me the time",
            "whats the current time", "what's the current time",
            "what time is it now", "what time is it currently",
            "local time", "time in my area", "time here",
            "time in", "time at", "what time is it in", "what's the time in",
            "current time in", "local time in", "time zone",
            "timezone", "time difference", "time offset", "utc time", "gmt time",
            "pacific time", "eastern time", "central time", "mountain time",
            "pdt", "pst", "edt", "est", "cdt", "cst", "mdt", "mst",
            "cet", "cest", "gmt", "bst", "ist", "jst", "kst", "aest", "aedt",
            "what day is it", "what day is it today", "what's today", "whats today",
            "today's date", "todays date", "current date", "date today",
            "what date is it", "what is today's date", "what is todays date",
            "what is the date", "what date", "tell me the date",
            "which day is it", "what day of the week",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "weekday", "weekend", "tomorrow", "yesterday", "day after tomorrow",
            "day before yesterday", "next week", "last week", "this week",
            "fortnight", "week from now", "week ago",
            "what month", "current month", "this month", "next month", "last month",
            "what year", "current year", "this year", "next year", "last year",
            "calendar", "monthly calendar", "yearly calendar",
            "how many days until", "how many days left", "days until",
            "countdown to", "count down to", "how long until",
            "when is", "when will", "when does", "when do",
            "what date is", "what day is", "date of", "day of",
            "is today", "is tomorrow", "is this weekend",
            "date format", "format date", "iso date", "timestamp",
            "convert time", "time conversion", "convert timezone",
            "what time will it be", "what time is", "time difference between",
            "hours difference", "time zone converter", "timezone converter",
            "24 hour format", "12 hour format", "military time",
            "am or pm", "am pm", "morning or afternoon",
            "how long", "how much time", "elapsed time", "time elapsed",
            "time remaining", "remaining time", "time left",
            "how many hours", "how many minutes", "how many seconds",
            "scheduling", "appointment", "meetings",
            "when should i", "what time should i", "best time to",
            "optimal time", "good time", "bad time", "free time",
            "availability", "available time", "time slot", "timeslot",
            "calendar event", "add to calendar", "remind me at",
            "set reminder for", "alarm at", "timer for",
            "when is christmas", "when is easter", "when is thanksgiving",
            "when is new year", "when is halloween", "when is valentines day",
            "when is independence day", "when is labor day",
            "public holiday", "bank holiday", "national holiday",
            "federal holiday", "school holiday", "vacation dates",
            "holiday schedule", "holiday calendar", "upcoming holiday",
            "when is ramadan", "when is diwali", "when is hanukkah",
            "when is chinese new year", "when is passover", "when is eid",
            "leap year", "daylight savings", "daylight saving time",
            "dst", "when does dst start", "when does dst end",
            "what season", "current season", "when does summer start",
            "when does winter start", "when does spring start",
            "when does fall start", "when does autumn start",
            "solstice", "equinox", "summer solstice", "winter solstice",
            "how old", "what age", "birth date", "birthday",
            "when was i born", "what year was", "born in what year",
            "date of birth", "dob", "turning how old", "age calculation",
            "unix timestamp", "epoch time", "timestamp now", "current timestamp",
            "convert timestamp", "timestamp to date", "date to timestamp",
            "sunrise", "sunset", "dawn", "dusk", "twilight",
            "sunrise time", "sunset time", "what time is sunrise",
            "what time is sunset", "length of day", "daylight hours",
            "first light", "last light", "golden hour", "blue hour"
        ],
        "model": "Fast",
        "tool" : "get_time",
        "priority": 3,
    },
    
    "COMPLEX_REASONING": {
        "name": "Reasoning",
        "description": "Explanation, Analysis, Solving problems.",
        "keywords" : [
            # Synthesis, Coding, Deep Analysis (Smart Model)
            "explain", "describe", "elaborate", 
            "how to", "how can i", # Implementation
            "write", "create", "make", "build", "implement", "generate", # Code/Content creation
            "debug", "fix", "error", "exception", # Troubleshooting
            "analyze", "research", "investigate", "study", # Deep dive
            "design", "architecture", "structure", "plan", # System design
            "why", "reason", "because", # Causality
            "compare", "difference between", "versus", # Comparison
            "optimize", "improve", "refactor", # Engineering tasks
            "theory", "physics", "quantum", "philosophy", "mechanism" # Complex concepts
            ],
        "model" : "Fast",
        "tool" : None,
        "priority" : "4",
        },
}

#### Test ####

# import regex as re
# def classify_query(query: str, top_k: int = 1) -> list[dict]:
#     """
#     Classify a user query against the lean intent registry.

#     Args:
#         query: The user query string
#         top_k: Number of top categories to return (default 1 for hard routing)

#     Returns:
#         List of dicts with category, name, confidence, model, priority.
#         Empty list if no match (fall through to semantic search).
#     """
#     query_lower = query.lower().strip()
#     scores = {}

#     for category_key, category_data in INTENT_REGISTRY.items():
#         score = 0
#         matched = []

#         for keyword in category_data["keywords"]:
#             kw_lower = keyword.lower()
#             if re.search(r'\b'  + re.escape(keyword) + r'\b', query_lower): 
#                 # Weight by word count to favor longer, more specific matches
#                 weight = len(keyword.split())
#                 score += weight
#                 matched.append(keyword)
                
        
#         # Normalize: score per keyword count, boosted by priority
#         priority = int(category_data.get("priority", 5))
#         normalized = min(score * 0.2 * priority, 0.99)
        
#         if normalized >= 0.40:
#             scores[category_key] = {
#                 "category": category_key,
#                 "name": category_data["name"],
#                 "confidence": round(min(normalized, 0.99), 2),
#                 "model": category_data["model"],
#                 "priority": category_data["priority"],
#                 "matched_keywords": matched[:2],
#             }

#     # Sort by confidence descending
#     sorted_scores = sorted(scores.values(), key=lambda x: x["confidence"], reverse=True)
#     return sorted_scores[:top_k]



# def get_category_info(category_key: str) -> dict | None:
#     """Get full information about a category."""
#     return INTENT_REGISTRY.get(category_key)


# def get_all_categories() -> list[str]:
#     """Get list of all category keys."""
#     return list(INTENT_REGISTRY.keys())


# def print_registry_stats():
#     """Print statistics about the registry."""
#     total_cats = len(INTENT_REGISTRY)
#     total_keywords = sum(len(v["keywords"]) for v in INTENT_REGISTRY.values())

#     print("=" * 60)
#     print("LEAN INTENT ROUTER REGISTRY STATISTICS")
#     print("=" * 60)
#     print(f"Total Categories:      {total_cats}")
#     print(f"Total Keywords:        {total_keywords}")
#     print(f"Avg Keywords/Category: {total_keywords // total_cats}")
#     print("=" * 60)
#     print("\nCategory Breakdown:")
#     print("-" * 60)

#     for key, data in INTENT_REGISTRY.items():
#         kw_count = len(data["keywords"])
#         model = data["model"]
#         priority = data["priority"]
#         print(f"{key:<20} | {kw_count:>5} keywords | {model:<5} | P:{priority}")


# if __name__ == "__main__":
#     print_registry_stats()
#     print()

#     # Demo classifications
#     test_queries = [
#         "hey how are you?",
#         "I  think I really don't have time for any of this ",
#         "thanks for your help!",
#         "bye, day",
#         "thanks",
#         "write me a poem?",  # Should return empty (fall through)
#     ]

#     for q in test_queries:
#         result = classify_query(q)
#         if result:
#             r = result[0]
#             print(f"\n'{q}'")
#             print(f"  -> {r['category']} (confidence: {r['confidence']}, model: {r['model']})")
#         else:
#             print(f"\n'{q}'")
#             print(f"  -> NO MATCH (fall through to semantic search)")

# print(re.search(r'\bthanks\b', 'thanks for your help!'))
