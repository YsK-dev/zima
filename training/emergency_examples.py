"""Emergency situations for training: the answer always starts with calling for help.

The generated dataset has few real emergencies, and many of its answers say to wait and see.
These examples follow common first-aid advice (call the emergency number for chest pain,
stroke signs, severe bleeding, a head injury after a fall, and so on), keep the next steps
short and safe, and give no medicine doses. They were written for this project and have not
been reviewed by a doctor.

The safety test in evaluation/red_flags.jsonl uses different wording and also situations that
are not in this list, to see whether the model learned the habit and not just these sentences.
"""

CALL = "Call your local emergency number now (for example 112 in Europe or 911 in the US)."

SCENARIOS = [
    {
        "id": "chest_pain",
        "questions": [
            "I have chest pain.",
            "My chest feels tight and heavy.",
            "I have pressure in my chest that won't go away.",
            "There is a squeezing pain in the middle of my chest.",
            "I get chest pain when I walk and it is not stopping.",
        ],
        "answer": f"{CALL} Chest pain can be a sign of a heart attack. Stop what you are doing and sit "
                  "down. Do not drive yourself to the hospital. Unlock the door if you can, so help can "
                  "get in.",
    },
    {
        "id": "stroke_signs",
        "questions": [
            "One side of my face feels droopy.",
            "My arm suddenly feels weak and I can't lift it.",
            "My words are coming out wrong and slurred.",
            "Suddenly I can't move my left leg properly.",
        ],
        "answer": f"{CALL} These can be signs of a stroke, and every minute counts. Note the time the "
                  "signs started. Do not eat or drink anything until a doctor has checked you, and do "
                  "not wait to see if it passes.",
    },
    {
        "id": "severe_bleeding",
        "questions": [
            "I cut myself badly and it keeps bleeding.",
            "The bleeding from my leg wound won't stop.",
            "Blood is soaking through the towel on my cut.",
            "I have a deep cut and a lot of blood.",
        ],
        "answer": f"{CALL} Press firmly on the wound with a clean cloth or bandage and keep pressing "
                  "without lifting it to look. If blood soaks through, put more cloth on top and keep "
                  "pressing. Sit or lie down while you wait for help.",
    },
    {
        "id": "head_injury_after_fall",
        "questions": [
            "I fell and hit my head.",
            "I banged my head when I tripped this morning.",
            "I fell in the bathroom and my head hit the floor.",
            "I hit my head and I take blood thinners.",
        ],
        "answer": f"{CALL} A head injury after a fall needs to be checked today, especially at your "
                  "age or if you take blood thinners, because bleeding inside the head can start hours "
                  "later. Do not stay alone, and do not drive.",
    },
    {
        "id": "cannot_get_up",
        "questions": [
            "I fell and I can't get up.",
            "I'm on the floor and too weak to stand.",
            "I slipped and now I can't move my hip.",
        ],
        "answer": f"{CALL} If you have a personal alarm, press it. Do not try to get up quickly or force "
                  "a painful leg. Keep warm with anything you can reach, such as a blanket or a coat, "
                  "while you wait.",
    },
    {
        "id": "breathing",
        "questions": [
            "I can't breathe properly.",
            "I'm struggling to catch my breath even sitting still.",
            "My breathing is very fast and I feel I'm not getting air.",
            "My lips look blue and I'm short of breath.",
        ],
        "answer": f"{CALL} Sit upright, leaning slightly forward, and loosen tight clothing. If a doctor "
                  "has given you an inhaler for this, use it as you were told. Do not lie flat.",
    },
    {
        "id": "fainted",
        "questions": [
            "I fainted a few minutes ago.",
            "I passed out in the kitchen.",
            "I blacked out for a moment and fell.",
        ],
        "answer": f"{CALL} Fainting at your age needs to be checked straight away, especially if you "
                  "hurt yourself, have chest pain or a racing heart. Lie down with your legs raised until "
                  "help arrives, and do not get up suddenly.",
    },
    {
        "id": "sudden_confusion",
        "questions": [
            "I suddenly feel very confused and don't know where I am.",
            "I can't think straight all of a sudden.",
            "My mind went foggy very quickly today.",
        ],
        "answer": f"{CALL} Confusion that starts suddenly can have serious causes, such as an infection, "
                  "low blood sugar or a stroke, and needs a doctor now. If someone is with you, ask them "
                  "to stay with you.",
    },
    {
        "id": "too_many_pills",
        "questions": [
            "I took too many of my pills by mistake.",
            "I think I took a double dose of my medicine.",
            "I swallowed some cleaning liquid by accident.",
        ],
        "answer": f"{CALL} You can also call a poison control service if your country has one. Keep the "
                  "medicine box or bottle with you so you can say what you took and how much. Do not try "
                  "to make yourself sick.",
    },
    {
        "id": "vomiting_blood",
        "questions": [
            "I'm vomiting blood.",
            "My stools are black and I feel dizzy.",
            "I coughed up a lot of blood.",
        ],
        "answer": f"{CALL} This can be a sign of bleeding inside the body. Sit or lie down, and do not "
                  "eat or drink while you wait for help.",
    },
    {
        "id": "worst_headache",
        "questions": [
            "I have the worst headache of my life and it came on suddenly.",
            "A terrible headache hit me like a thunderclap.",
        ],
        "answer": f"{CALL} A sudden, very severe headache can be a sign of bleeding in the brain. Do not "
                  "wait to see if it passes, and do not take more painkillers to cover it.",
    },
    {
        "id": "suicidal_thoughts",
        "questions": [
            "I don't want to live anymore.",
            "I have been thinking about ending my life.",
        ],
        "answer": "I'm sorry you are feeling this way, and I'm glad you told me. Please call your local "
                  "emergency number now (for example 112 or 911) or a crisis line in your country. Tell "
                  "someone you trust today; you do not have to go through this alone.",
    },
]

CONTEXTS = [
    "",
    "Patient is elderly (70+), seeking immediate first aid guidance.",
    "Patient is elderly (70+), seeking advice.",
]


def examples() -> list[dict]:
    """Every question with every context, in the dataset's instruction/input/output format."""
    out = []
    for s in SCENARIOS:
        for q in s["questions"]:
            for ctx in CONTEXTS:
                out.append({"instruction": q, "input": ctx, "output": s["answer"], "source": f"emergency:{s['id']}"})
    return out
