from configs.loader import parseConfigFromJson
from configs.event import Event
from configs.schedule import Schedule
from configs.question import Question
from configs.submit import Submit
import json


with open("event-settings.json", mode="r", encoding="utf-8") as f:
    jdict = json.load(f)
    print(parseConfigFromJson(jdict["event"], Event))
    print(parseConfigFromJson(jdict["schedule"], Schedule))
    print(parseConfigFromJson(jdict["question"], Question))
    print(parseConfigFromJson(jdict["submit"], Submit))
    # EventParser(jdict).parse()
