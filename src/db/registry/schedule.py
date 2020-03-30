import datetime
from db.database import Database
from db.registry._registry_base import _RegistryBase
from configs.schedule import Period, Schedule, Limitation


class RegistrySchedule(_RegistryBase):
    def __init__(self, database: Database):
        super().__init__(database, "registry_datetime")

    def setSchedule(self, schedule: Schedule):
        self._set("schedule.date.since", schedule.date.since)
        self._set("schedule.date.until", schedule.date.until)
        self._set("schedule.limitation.entry.since", schedule.limitation.entry.since)
        self._set("schedule.limitation.entry.until", schedule.limitation.entry.until)
        self._set("schedule.limitation.attend.since", schedule.limitation.attend.since)
        self._set("schedule.limitation.attend.until", schedule.limitation.attend.until)
        self._set("schedule.limitation.submit.since", schedule.limitation.submit.since)
        self._set("schedule.limitation.submit.until", schedule.limitation.submit.until)
        self._set("schedule.limitation.final_submit.since", schedule.limitation.final_submit.since)
        self._set("schedule.limitation.final_submit.until", schedule.limitation.final_submit.until)
        self._set("schedule.limitation.catalog.since", schedule.limitation.catalog.since)
        self._set("schedule.limitation.catalog.until", schedule.limitation.catalog.until)

    def getEntryPeriod(self) -> Period:
        """ エントリー期間を取得する """
        return Period(
            since=self._get("schedule.limitation.entry.since"),
            until=self._get("schedule.limitation.entry.until"))

    def getDate(self) -> Period:
        return Period(
            since=self._get("schedule.date.since"),
            until=self._get("schedule.date.until")
        )

    def getAttendPeriod(self) -> Period:
        return Period(
            since=self._get("schedule.limitation.attend.since"),
            until=self._get("schedule.limitation.attend.until")
        )

    def getSubmitPeriod(self) -> Period:
        return Period(
            since=self._get("schedule.limitation.submit.since"),
            until=self._get("schedule.limitation.submit.until")
        )

    def getFinalSubmitPeriod(self) -> Period:
        return Period(
            since=self._get("schedule.limitation.final_submit.since"),
            until=self._get("schedule.limitation.final_submit.until")
        )

    def getCatalogPeriod(self) -> Period:
        return Period(
            since=self._get("schedule.limitation.catalog.since"),
            until=self._get("schedule.limitation.catalog.until")
        )

    def getSchedule(self) -> Schedule:
        return Schedule(
            date=self.getDate(),
            limitation=Limitation(
                entry=self.getEntryPeriod(),
                attend=self.getAttendPeriod(),
                submit=self.getSubmitPeriod(),
                final_submit=self.getFinalSubmitPeriod(),
                catalog=self.getCatalogPeriod()
            )
        )

    """ ユースケースに沿った実装にする
    def setEntryPeriod(self, entry_period: Period):
        self._set("entry.since", entry_period.since)
        self._set("entry.until", entry_period.until)
    """
