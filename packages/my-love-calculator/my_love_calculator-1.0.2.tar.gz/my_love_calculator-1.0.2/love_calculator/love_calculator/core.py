import random 

def calculate_love(name1: str, name2: str) -> dict:
    if not name1 or not name2:
        raise ValueError("Both names must be provided")
    
    seed = sum(ord(char) for char in (name1+ name2).lower())
    random.seed(seed)

    percentage = random.randint(50, 100)
    
    message = (
        "Perfect match ❤️"
        if percentage > 85 else
        "Strong connection 💕"
        if percentage > 70 else
        "It could work 🙂"
    )

    return {
        "name1": name1,
        "name2": name2,
        "love_percentage": percentage,
        "message": message
    }
