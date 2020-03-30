from db.database import Database
from db.registry._registry_base import _RegistryBase
from configs.submit import Submit
from typing import Optional


class RegistrySubmit(_RegistryBase):
    def __init__(self, database: Database):
        super().__init__(database, "registry_string")

    def setSubmit(self, submit: Submit):
        self._set("submit.upload_url", submit.upload_url)
        self._set("submit.download_url", submit.download_url)
        self._set("submit.unitypackage_rule", submit.unitypackage_rule)

    def getSubmit(self) -> Optional[Submit]:
        ret = None
        try:
            ret = Submit(
                upload_url=self._get("submit.upload_url"),
                download_url=self._get("submit.download_url"),
                unitypackage_rule=self._get("submit.unitypackage_rule")
            )
        except TypeError as e:
            self.logger.warning("Failed to get submit. %s", e)
        return ret
