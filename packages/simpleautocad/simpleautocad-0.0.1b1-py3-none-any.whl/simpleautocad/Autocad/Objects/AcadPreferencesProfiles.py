from __future__ import annotations
from ..Base import *
from ..Proxy import proxy_property, AccessMode
from ..AcadObject import *



class AcadPreferencesProfiles(AppObject):
    def __init__(self, obj) -> None: super().__init__(obj)

    ActiveProfile: str = proxy_property(str,'ActiveProfile',AccessMode.ReadOnly)
    Application: AcadApplication = proxy_property('AcadApplication','Application',AccessMode.ReadOnly)

    def CopyProfile(self, oldProfileName: In[str], newProfileName: In[str]) -> None:
        self._obj.CopyProfile(oldProfileName, newProfileName)

    def DeleteProfile(self, ProfileName: In[str]) -> None:
        self._obj.DeleteProfile(ProfileName)
        
    def ExportProfile(self, Profile: In[str], RegFile: In[str]) -> None:
        self._obj.ExportProfile(Profile, RegFile)

    def GetAllProfileNames(self) -> tuple[str]:
        pNames = self._obj.GetAllProfileNames()
        return pNames

    def ImportProfile(self, Profile: In[str], RegFile: In[str], IncludePathInfo: In[bool]) -> None:
        self._obj.ImportProfile(Profile, RegFile, IncludePathInfo)

    def RenameProfile(self, origProfileName: In[str], newProfileName: In[str]) -> None:
        self._obj.ImportProfile(origProfileName, newProfileName)
        
    def ResetProfile(self, Profile: In[str]) -> None:
        self._obj.ResetProfile(Profile)