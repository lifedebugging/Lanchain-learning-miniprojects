# Janus v3

It's been a while but here's the explanation of what's changed in Janus v3.

# The 3 stages of Janus v3 engine:

1. stage 1 : **The keyword & pattern registry**
   
   Weight dictionary in v2 wasn't doing so good, there were wholes you could easily bypass
   the intent and hallucinate the model. Hence, the need of dictionary that has more trigger words and
   intent categories(e.g., System_intent, casual_talk, fact_based and such).

   Introduction of Janus_registry : Data-Driven Heuristics.

     Janus registry contain the detailed keywords separated by ditinct intent using [key : value] pair dictionary method.
   
    # Meta data
     For Janus to "decide" what to do with those words. In v3, I attached a **Target Model**,
   **Target tool** and the **Priority** to each cateogory based on their Intent. It will make road ahead of us easier when implementing decision logic.
   

2. stage 2 : **The scoring loop**

   I already had a function of scoring system in *v2* but it wasn't enough because my motive was to take apart
   the logic out of *v2* and built a new better defining  decision logic for *v3*. 

   # The birth of new **Descision logic**
   The Decision logic consist of 4 stages:

   1. The Scoreboard

           scores = {category : 0 for category in Janus_registry}

      Basically, this is our leaderboard before we start scoring we need to set the score to 0.

          like this: {"TIME_DATE": 0, "FACTS_BASED": 0, "CASUAL_TALK": 0}.

      And when we do the **Multi-Keyword Scan**, we are updating this specific scoreboard.

   2. The multi-keyword scan

          for category, data in Janus_registry.items():
          for kw in data["keywords"]:
             if kw in query_lower:
                 scores[category] += len(kw.split())
      Line-by-line explanation :

       *For category,data in Janus_registry.items():*
      here, two things happining :

      1. pythone grabs the **key** and puts it in the variable `category`.
      2. Python grabs the **Whole Dictionary** and puts in the `data`.
         
          Example :
         
         Key : "TIME_DATE"
         
         Value : {"keywords": [...], "model" : Fast, "priority" : 4} (This is a dictionary itself)

       *for kw in data["keywords"]:

      1. It means to iterate over **keywords** and putting them in kw.
      2. since data itself is dictionary and we only need the **keyword** inside
         the dictionary. we do `data["keywords"] because **keywords** is the list
         inside dictionary.

      if kw in query_lower:
      
       Now, checking in the words in kw matches the words in my input.

      scores[category] += len(kw.split())

      1. if the words match, add value to the category in score so, `score[category]`
      2. How much value?
         It depends on the number of words, we find out len() of the words in kw.
     
         # Need of split

         But here's the catch, In the registry there are different two different types of keywords.
         Some are one word (`"why"`) and some are phrases (`"how can i"`).

         **The problem** :
         Let's say user says : "How can I fix this error?"

         1. In `FACT_BASED` you might have the keyword *"how"*.
         2. In `COMPLEX_REASONING` you have the keyword *"how can i"*.
        
         If we just add `+1` like : `scores[category] =+1` for every match, both categories get 1 point.
         But "how can i" is a much better match for the user's intent than just the word "how".

         **The solution** :
         `kw.split()` turn `"how can i"` into `['how', 'can, 'i']`.
         len(...) counts them 3.

         Now, `COMPLEX_REASONING` gets 3 point(because the match was specific).

         **Janus now "knows" that longer, more specific phrases are more important than single words.**

    3. Finding Maximum score
  
              max_score = max(scores.values())
              print(max_score)
    
              if max_score == 0:
                   return "CASUAL"

       Inside scores :

       `scores = {"TIME_DATE": 2, "COMPLEX_REASONING": 2, "CASUAL_TALK": 0}`

       So, `max_score` is 2.

       And if `max_score` is 0. It will return `CASUAL`. Meaning use default conversation intent.

       Putting it together:

       ```
       max_score = max(scores.values())   # Find the highest score among all entries
       print(max_score)                   # Show that highest score
       ```
   4. The winner

             winners = []
             for category, score in scores.items():
             if score == max_score:
                 winners.append(category)
        
             best_category = winners[0]
    
             for category in winners:
             if Janus_registry[category]["priority"] > Janus_registry[best_category]["priority"]:
                      best_category = category
            
             return {
                "category": best_category,
                "model" : Janus_registry[best_category]["model"],
                "tool" : Janus_registry[best_category]["tool"],     
             }
      There's no winner right now so, `Winners = []`.

      In the next part again, we iterate over `scores.items()`, By the way .item() shows view object in dictionary in key : value pair.

      Putting the value in `category` and `score` and if `max_score` is equal to `score`
      we put that cateogory in the `winners` list.

      Hence, `winners.append(category)` here `.append` is an method of putting values at the last of the list.

      At the end of this loop, `winners` looks liek this : `["TIME_DATE", "COMPLEX_REASONING"]`.

      `best_category = winners[0]` here, we putting the 1st in the `winners` list into `best_category`.

      ```
      for category in winners:
        if Janus_registry[category]["priority"] > Janus_registry[best_category]["priority"]:
            best_category = category
      ```
      With this loop, we finalize that if inside **Janus_registry** if a `category` has
      higher `"priority"` than the `best_category` `["priority"]` then that `category` will become the best category:

      Example : Think of it like a boxing tournament:
      1. You have a list of winners: [A, B, C].
      2. You don't know who is the strongest yet.
      3. The Logic: You pick the first person (A) and say, "For now, you are the Champion (best_category)."
      4. Then you look at the next person (B) and ask: "Is B stronger (higher priority) than my current Champion (A)?
      5. If Yes, then B becomes the new best_category.
      6. If No, A stays the best_category.
      7. Then you look at C and repeat.
         *This is AI generated logic
         
  3. stage 3 : **The final Binding**

     Now that we have a winning_category (e.g., "TIME_DATE"), we need to pull the instructions.

     Extract the Model and Tool from the Registry for that winner.

     nstead of just checking for "complex," your router_logic now returns a Decision Dictionary.
     We use that to decide exactly which Agent to call and which tools to "bind."

     The **Model selection** and **Tool selection** both happens simultaneously.

     The rest is just more `print()` to showcase the final output and what's going inside the Janus

# Errors

I did ran into some errors while writing logic for `decision` and final calls.

**The error** like : `unhashable type : list`, It happened because I was trying to use a **list**
as a key in a dictionary.

**Solution** : Iterated over actual strings in the list instead of feeding it the whole list.

**The error** `TypeError: 'StructuredTool' object is not subscriptable`

**Solutions** : This is a common error when transitioning from raw JSON (dictionaries) to LangChain Objects.

The error TypeError: 'StructuredTool' object is not subscriptable means you are trying to use square brackets ["name"] on an Object, but Python only allows square brackets on "Subscriptable" things like Dictionaries or Lists.
The Fix

In LangChain, a StructuredTool is a class.[1] You access its properties using Dot Notation (.), not square brackets.

# Final Working :

Input : Hello, What is the time?

output :

Phase A: The Scan (The Loop)

Janus looks at the first category: "TIME_DATE".

    It looks at the keywords: ["time", "clock", "date"].

    It finds "time" in the query.

    It goes to your scoreboard and changes "TIME_DATE": 0 to "TIME_DATE": 1.

Then it looks at "CASUAL_TALK".

    It finds "hey" in the query.

    It changes "CASUAL_TALK": 0 to "CASUAL_TALK": 1.

Phase B: Finding the Winners

Now the scan is over. Your scoreboard looks like this:
{"TIME_DATE": 1, "CASUAL_TALK": 1, "FACTS_BASED": 0}

We find the max_score. In this case, it is 1.
Now we look for Winners (everyone who has a 1).

    winners = ["TIME_DATE", "CASUAL_TALK"].

Phase C: The Priority Check (The Tie-Breaker)

Janus is now confused. Should I use the "Fast Model" for a chat, or the "Fast Model" with the "Time Tool"?
This is where Priority saves the day.

Janus looks at your Janus_registry:

    TIME_DATE has Priority: 4

    CASUAL_TALK has Priority: 1

Janus compares: Is 4 > 1? Yes.
Janus picks "TIME_DATE" as the absolute winner.


# Note 
The Router decides the Brain (Model), but the Agent still has the full toolbelt. 
This is the "Safety Net" of my architecture.




     

     

     

     

     

     
     
         
      
      
      
        

      
       
      

       

       
       

       
       
       
         
         


      

         
      
   
         
