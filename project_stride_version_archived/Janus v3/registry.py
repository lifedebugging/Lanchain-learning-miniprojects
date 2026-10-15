Janus_registry = {
        "TIME_DATE" : { 
            "keywords" : ["time", "clock", "date", "get_time"],
            "model" : "Fast",
            "tool": "get_time",
            "priority" : "4",
        },
        
        "FILE_SYSTEM" : {
            "keywords" : ["list", "files", "directory", "ls", "documents", "video", "audio","text file",],
            "model" : "Fast",
            "tool": None,
            "priority" : "3",
        },
         
        "FACTS_BASED": {
            "keywords" : [
            "what is", "what are", "what was", 
            "who is", "who was", "where is", "where was","when is", "when did",
            "meaning of", "definition of", "define", "translate", "spell", 
            "calculate", "solve", "add", "subtract", "sum", # Simple math
            "list","how do you", "how does", # Explanations of mechanics (like 'strip' or 'eval')
            "price of", "cost of", "population of" # Direct data retrieval
            ],
            "model" : "Fast",
            "tool" : None,
            "priority" : "2",
        },
        
            
        "COMPLEX_REASONING": {
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
            "model" : "Smart",
            "tool" : None,
            "priority" : "5",
        },
        
        "CASUAL_TALK":{
            "keywords":[
            # Social & Status (No Reasoning Needed)
            "hey", "hello", "hi", "sup", "yo",
            "good morning", "good night", "bye", "see you", "later",
            "how are you", "how are you doing", "how's it going",
            "i am", "i m", "i was", "i did", "i ran", # Personal updates
            "my day", "my weekend", "my plan",
            "thank you", "thanks", "appreciate", "sorry", "excuse me",
            "think", "opinion", "feel", "belief", # Subjective requests
            ],
            "model" : "Fast",
            "tool" : None,
            "priority" : "1",
        },
           
} 
