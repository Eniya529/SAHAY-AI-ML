import re


def extract_emotional_indicators(text):
    text_lower = text.lower()

    indicators = []

    emotional_patterns = {
        "fear": [
            "afraid",
            "scared",
            "fear",
            "terrified",
            "frightened"
        ],
        "distress": [
            "distressed",
            "overwhelmed",
            "can't cope",
            "cannot cope",
            "desperate"
        ],
        "anxiety": [
            "anxious",
            "anxiety",
            "nervous",
            "worried",
            "panic"
        ],
        "helplessness": [
            "helpless",
            "don't know what to do",
            "cannot do anything",
            "can't do anything"
        ]
    }

    for indicator, patterns in emotional_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                indicators.append(indicator)
                break

    return list(set(indicators))


def extract_contextual_indicators(text):
    text_lower = text.lower()

    indicators = []

    contextual_patterns = {
        "threat": [
            "threat",
            "threatened",
            "kill",
            "harm",
            "hurt"
        ],
        "retaliation": [
            "retaliate",
            "retaliation",
            "punish me",
            "because i reported",
            "if i report"
        ],
        "intimidation": [
            "intimidate",
            "scare me",
            "pressure me",
            "forcing me"
        ],
        "repeated_contact": [
            "keep calling",
            "keeps calling",
            "repeatedly",
            "again and again",
            "keeps messaging"
        ],
        "following": [
            "following me",
            "followed me",
            "watching me",
            "tracking me"
        ]
    }

    for indicator, patterns in contextual_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                indicators.append(indicator)
                break

    return list(set(indicators))


def extract_safety_indicators(text):
    text_lower = text.lower()

    indicators = []

    safety_patterns = {
        # Basic safety indicators
        "immediate_safety_concern": [
            "right now",
            "here right now",
            "not safe",
            "unsafe",
            "in danger",
            "immediate danger",
            "danger right now",
            "currently in danger"
        ],

        "family_safety_concern": [
            "my family",
            "my parents",
            "my mother",
            "my father",
            "my children",
            "family"
        ],

        "home_safety_concern": [
            "outside my house",
            "at my house",
            "near my home",
            "came to my house",
            "outside my home",
            "near my house"
        ],

        "workplace_safety_concern": [
            "workplace",
            "office",
            "at my work",
            "at work"
        ],

        # Advanced safety indicators
        "extreme_vulnerability": [
            "completely helpless",
            "totally helpless",
            "i cannot protect myself",
            "i can't protect myself",
            "i have no control",
            "i feel powerless",
            "i feel completely powerless"
        ],

        "isolation": [
            "i have nobody",
            "i have no one",
            "no one to help me",
            "nobody to help me",
            "i am alone",
            "i feel alone",
            "no one knows",
            "nobody knows"
        ],

        "dependency_or_inability_to_seek_help": [
            "i cannot leave",
            "i can't leave",
            "i cannot get help",
            "i can't get help",
            "i have no way to get help",
            "i am unable to get help",
            "i cannot ask for help",
            "i can't ask for help",
            "i cannot escape",
            "i can't escape"
        ],

        "possible_self_harm_indicator": [
            "i don't want to live",
            "i do not want to live",
            "i want to die",
            "i don't want to be here anymore",
            "i do not want to be here anymore",
            "end my life",
            "hurt myself",
            "harm myself"
        ]
    }

    for indicator, patterns in safety_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                indicators.append(indicator)
                break

    return list(set(indicators))


def extract_key_evidence(text):
    if not text.strip():
        return []

    return [text.strip()]