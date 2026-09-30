"""Eastern time from operating-system rules; no third-party packages."""
from datetime import datetime, timedelta, tzinfo
from functools import lru_cache
import sys

KEY = 'America/New_York'

class WindowsEastern(tzinfo):
    def __init__(self):
        import ctypes as c
        from ctypes import wintypes as w
        class ST(c.Structure):
            _fields_ = [(n,w.WORD) for n in ('year','month','weekday','day','hour','minute','second','milliseconds')]
        fields=[('Bias',w.LONG),('StandardName',w.WCHAR*32),('StandardDate',ST),('StandardBias',w.LONG),('DaylightName',w.WCHAR*32),('DaylightDate',ST),('DaylightBias',w.LONG)]
        class TZI(c.Structure):
            _fields_=fields
        class Dynamic(c.Structure):
            _fields_=fields+[('TimeZoneKeyName',w.WCHAR*128),('DynamicDaylightTimeDisabled',w.BOOLEAN)]
        self.c,self.ST,self.TZI=c,ST,TZI
        self.api=c.WinDLL('kernel32',use_last_error=True)
        self.api.EnumDynamicTimeZoneInformation=c.WinDLL('advapi32',use_last_error=True).EnumDynamicTimeZoneInformation
        self.api.EnumDynamicTimeZoneInformation.argtypes=[w.DWORD,c.POINTER(Dynamic)]
        self.api.EnumDynamicTimeZoneInformation.restype=w.DWORD
        self.api.GetTimeZoneInformationForYear.argtypes=[w.WORD,c.POINTER(Dynamic),c.POINTER(TZI)]
        self.api.GetTimeZoneInformationForYear.restype=w.BOOL
        self.api.SystemTimeToTzSpecificLocalTimeEx.argtypes=[c.POINTER(Dynamic),c.POINTER(ST),c.POINTER(ST)]
        self.api.SystemTimeToTzSpecificLocalTimeEx.restype=w.BOOL
        for i in range(1024):
            d=Dynamic();code=self.api.EnumDynamicTimeZoneInformation(i,c.byref(d))
            if code==259:break
            if code:raise OSError(code,'Cannot enumerate Windows timezones')
            if d.TimeZoneKeyName=='Eastern Standard Time':
                self.dynamic=d
                break
        else:raise OSError('Windows timezone enumeration exceeded limit')
        if not hasattr(self,'dynamic'):raise OSError('Windows Eastern timezone unavailable')

    def __str__(self):return KEY
    def tzname(self,dt):return 'ET'

    @lru_cache(maxsize=128)
    def offsets(self,year):
        info=self.TZI()
        if not self.api.GetTimeZoneInformationForYear(year,self.c.byref(self.dynamic),self.c.byref(info)):
            raise self.c.WinError(self.c.get_last_error())
        standard=timedelta(minutes=-info.Bias-info.StandardBias)
        daylight=timedelta(minutes=-info.Bias-info.DaylightBias) if info.DaylightDate.month else standard
        return standard,daylight

    def local(self,utc):
        src=self.ST(utc.year,utc.month,0,utc.day,utc.hour,utc.minute,utc.second,0);dst=self.ST()
        if not self.api.SystemTimeToTzSpecificLocalTimeEx(self.c.byref(self.dynamic),self.c.byref(src),self.c.byref(dst)):
            raise self.c.WinError(self.c.get_last_error())
        return datetime(dst.year,dst.month,dst.day,dst.hour,dst.minute,dst.second,utc.microsecond)

    def utcoffset(self,dt):
        if dt is None:return None
        wall=dt.replace(tzinfo=None)
        standard,daylight=self.offsets(wall.year)
        candidates=sorted({wall-offset for offset in (standard,daylight) if self.local(wall-offset)==wall})
        if candidates:return wall-candidates[min(dt.fold,len(candidates)-1)]
        # PEP 495: reverse the fold rule for a nonexistent spring-forward time.
        return daylight if dt.fold else standard

    def dst(self,dt):
        if dt is None:return None
        return self.utcoffset(dt)-self.offsets(dt.year)[0]

    def fromutc(self,dt):
        if dt.tzinfo is not self:raise ValueError('fromutc requires this timezone')
        utc=dt.replace(tzinfo=None);wall=self.local(utc)
        candidates=sorted({wall-offset for offset in self.offsets(wall.year) if self.local(wall-offset)==wall})
        fold=int(len(candidates)==2 and utc==candidates[-1])
        return wall.replace(tzinfo=self,fold=fold)

@lru_cache(maxsize=1)
def eastern(name=KEY):
    if name not in (KEY,'ET'):
        raise ValueError('PAIGe reporting uses Eastern Time (America/New_York) only')
    if sys.platform=='win32':return WindowsEastern()
    # Read system files explicitly, so installed tzdata cannot mask a missing OS database.
    from zoneinfo import ZoneInfo, TZPATH
    from pathlib import Path
    for root in TZPATH:
        path=Path(root)/KEY
        if path.is_file():
            with path.open('rb') as stream:return ZoneInfo.from_file(stream,key=KEY)
    raise OSError('System Eastern timezone database unavailable; update or repair the operating system')

if __name__=='__main__':
    from datetime import timezone
    print(datetime.now(timezone.utc).astimezone(eastern()).isoformat()+' ET')
