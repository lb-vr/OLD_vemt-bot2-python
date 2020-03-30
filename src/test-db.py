from datetime import datetime
import subprocess
import logging
import json
from db.registry.schedule import RegistrySchedule
from configs.schedule import Period
from setup_log import setupLogger
from db.user.entries import Entries, EntryInfo
from db.database import Database
from db.registry.event import RegistryEvent
from db.registry.submit import RegistrySubmit
from db.question.prologue import PrologueDB
from db.question.question_item import QuestionItemDB
from db.registry.guild import RegistryGuild
from configs.loader import parseConfigFromJson
from configs.event import Event
from configs.schedule import Schedule
from configs.question import Question
from configs.submit import Submit

if __name__ == "__main__":

    # logger = setupLogger("vemt", stdout_level=logging.DEBUG, logfile_level=logging.DEBUG)
    db_proc = subprocess.Popen("sqlite3 {} < {}".format("test.db", "src/db/scheme.sql"),
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    cout, cerr = db_proc.communicate()

    print("COUT")
    print(cout)
    print("\ncerr")
    print(cerr)

    with open("event-settings.json", mode="r", encoding="utf-8") as f:
        jdict = json.load(f)
        event = parseConfigFromJson(jdict["event"], Event)
        schedule = parseConfigFromJson(jdict["schedule"], Schedule)
        question: Question = parseConfigFromJson(jdict["question"], Question)
        submit: Submit = parseConfigFromJson(jdict["submit"], Submit)
        # EventParser(jdict).parse()
        print(event)

        with Database("test.db") as db:
            reg_guild = RegistryGuild(db)

            reg_event = RegistryEvent(db)
            print(reg_event.getEvent())
            reg_event.setEvent(event)
            print(reg_event.getEvent())

            reg_schedule = RegistrySchedule(db)
            reg_schedule.setSchedule(schedule)
            print(reg_schedule.getSchedule())

            entry_since = reg_schedule.getEntryPeriod().since
            print(entry_since, type(entry_since))

            reg_prologue = PrologueDB(db)
            reg_prologue.setPrologue(question.prologue)
            print(reg_prologue.getPrologue())

            reg_qitem = QuestionItemDB(db)

            qitem_id = 1
            for qitem in question.require:
                qitem.id = qitem_id
                reg_qitem.setQuestionItem(qitem, True)
                qitem_id += 1

            for qitem in question.optional:
                qitem.id = qitem_id
                reg_qitem.setQuestionItem(qitem, False)
                qitem_id += 1

            print(reg_qitem.getAllQuestions(is_request=True))

            reg_submit = RegistrySubmit(db)
            reg_submit.setSubmit(submit)
            print(reg_submit.getSubmit())
