from __future__ import annotations

import datetime as dt
import math
from collections.abc import Iterable

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd

def _common_str(self) -> str:
    return f'[{getattr(self, "_acronym", type(self).__name__)}] {getattr(self, "name", "")}'

def _common_repr(self) -> str:
    def fmt(v):
        if isinstance(v, (int, float, str, bool, type(None))):
            return repr(v)
        if hasattr(v, 'name') and not isinstance(v, (str, bytes)):
            return repr(getattr(v, 'name'))
        if isinstance(v, dict):
            return f'<dict len={len(v)}>'
        if isinstance(v, (list, tuple, set)):
            return f'<{type(v).__name__} len={len(v)}>'
        shape = getattr(v, 'shape', None)
        if shape is not None:
            try:
                r, c = shape
                return f'<{type(v).__name__} shape={r}x{c}>'
            except Exception:
                return f'<{type(v).__name__} shape={shape}>'
        return repr(v)

    names: list[str] = []
    for cls in type(self).__mro__:
        slots = getattr(cls, '__slots__', ())
        names.extend((slots,) if isinstance(slots, str) else slots)

    seen = set()
    items: list[tuple[str, object]] = []
    for name in names:
        if name and name not in seen and hasattr(self, name):
            seen.add(name)
            items.append((name, getattr(self, name)))

    if not items and hasattr(self, '__dict__'):
        items = list(self.__dict__.items())

    body = ',\n  '.join(f'{k}={fmt(v)}' for k, v in items)
    return f'{type(self).__name__}(\n  {body}\n)'

class Calendar:
    """
    Calendar class.
    """

    name:         str
    working_days: set[int]
    holidays:     set[dt.date]

    __slots__ = (
        'name',
        'working_days',
        'holidays',
    )
    
    _acronym = 'C'
    __str__ = _common_str
    __repr__ = _common_repr

    def __init__(
        self, 
        name:         str                                                        = 'Calendar',
        working_days: None | Iterable[int | float | str                        ] = None,
        holidays:     None | Iterable[int | float | str | dt.datetime | dt.date] = None,
    ):
        self.name =         str(name)
        self.working_days = {0, 1, 2, 3, 4} if working_days is None else {int(float(wday))       for wday in working_days} 
        self.holidays =     set()           if holidays     is None else {self._parse_date(hday) for hday in holidays}

    def _is_working_day(
        self, 
        date: dt.date
    ) -> bool:
        return date.weekday() in self.working_days and date not in self.holidays
    
    def _workday(
        self, 
        start_date: dt.date, 
        days:       float | int
    ) -> dt.date:
        current_date = start_date
        remaining_days = abs(round(days))
        step = dt.timedelta(days=1 if days >= 0 else -1)
        while remaining_days:
            current_date += step    
            if self._is_working_day(current_date):
                remaining_days -= 1
        return current_date
    
    def _networkdays(
        self, 
        start_date:  dt.date, 
        finish_date: dt.date
    ) -> int:
        if start_date < finish_date:
            sign = 1
        elif start_date == finish_date:
            return 1 if self._is_working_day(start_date) else 0
        else:
            start_date, finish_date = finish_date, start_date
            sign = -1
        wdays = self.working_days
        hdays = self.holidays
        total_days = (finish_date - start_date).days + 1
        full_weeks, extra_days = divmod(total_days, 7)
        count = full_weeks * len(wdays)
        start_weekday = start_date.weekday()
        count += sum(((start_weekday + i) % 7) in wdays for i in range(extra_days))
        if hdays:
            for h in hdays:
                if start_date <= h <= finish_date and h.weekday() in wdays:
                    count -= 1
        return sign * count

    @staticmethod
    def _parse_date(
        date_val: dt.date | dt.datetime | str | int | float,
    ) -> dt.date:
        if isinstance(date_val, dt.datetime):
            return date_val.date()
        if isinstance(date_val, dt.date):
            return date_val
        if isinstance(date_val, str):
            return dt.datetime.strptime(date_val.strip(), '%Y%m%d').date()
        if isinstance(date_val, (int, float)):
            return dt.datetime.strptime(str(int(date_val)), '%Y%m%d').date()
        
class Resource:
    """
    Resource class.
    """

    name:          str
    resource_type: str
    unit_cost:     float
    availability:  float
    _allocations:  dict[str, tuple[Activity, float]]
    _cost:         float

    __slots__ = (
        'name',
        'resource_type',
        'unit_cost',
        'availability',
        '_allocations',
        '_cost',
    )
    
    _acronym = 'R'
    __str__ = _common_str
    __repr__ = _common_repr

    def __init__(
        self,
        name:          str = 'Resource',
        resource_type: str = 'work',
        unit_cost:     float | int | str = 0.0,
        availability:  float | int | str = math.inf,
    ):  
        
        # Basic
        self.name =          str(name)
        self.resource_type = resource_type
        self.unit_cost =     float(unit_cost)
        self.availability =  float(availability)

        # Scheduling
        self._allocations: dict[str, tuple[Activity, float]] = {}
        self._cost: float                                    = 0.0

    @property
    def allocations(self) -> dict[str, tuple[Activity, float]]:
        return self._allocations
    
    @property
    def cost(self) -> float:
        return self._cost
    
class Activity:
    """
    Activity class.
    """
    
    name:                  str

    predecessors:          dict[str, tuple[Activity, str, float | int]]
    successors:            dict[str, tuple[Activity, str, float | int]]

    baseline_resources:    dict[str, tuple[Resource,      float | int]]
    baseline_duration:     float
    effort_driven:         bool
    resources:             dict[str, tuple[Resource,      float | int]]
    duration:              float

    calendar:              Calendar | None
    es:                    dt.date  | None
    ef:                    dt.date  | None
    ls:                    dt.date  | None
    lf:                    dt.date  | None
    es_constraint:         bool
    ef_constraint:         bool
    ls_constraint:         bool
    lf_constraint:         bool
    slack:                 int      | None
    critical:              bool     | None

    direct_cost:           float
    overhead_rate:         float
    overhead_criterion:    str
    indirect_cost:         float
    total_cost:            float

    duration_distribution: str
    duration_mean:         float
    duration_stdev:        float
    duration_params:       dict
    cost_distribution:     str
    cost_mean:             float
    cost_stdev:            float
    cost_params:           dict
    criticality:           float

    control_accounts:      dict[str, ControlAccount]
    records:               dict[int, dict]
    as_date:               dt.date | None
    as_days:               int     | None
    af_date:               dt.date | None
    af_days:               int     | None

    project:               Project | None

    __slots__ = (
        'name',

        'predecessors', 
        'successors',

        'baseline_resources', 
        'baseline_duration',
        'effort_driven',
        'resources',
        'duration',
        'calendar',

        'es', 'ef', 
        'ls', 'lf',
        'es_constraint', 
        'ef_constraint',
        'ls_constraint', 
        'lf_constraint',
        'slack', 
        'critical',

        'direct_cost',
        'overhead_rate', 
        'overhead_criterion',
        'indirect_cost',
        'total_cost',

        'duration_distribution', 
        'duration_mean', 
        'duration_stdev', 
        'duration_params',
        'cost_distribution', 
        'cost_mean', 
        'cost_stdev', 
        'cost_params', 
        'criticality',

        'control_accounts',
        'records',
        '_as_date', 
        '_as_days',
        '_af_date', 
        '_af_days',

        'project',
    )
    _acronym = 'A'
    __str__ = _common_str
    __repr__ = _common_repr

    def __init__(
        self,

        name:                  str                                                 = 'Activity',
        predecessors:          dict[str, tuple[Activity, str, float | int]] | None = None,

        baseline_resources:    dict[str, tuple[Resource,      float | int]] | None = None,
        baseline_duration:     float                                               = 0.0,
        effort_driven:         bool | int | float                                  = True,
        resources:             dict[str, tuple[Resource,      float | int]] | None = None,

        calendar:              None | Calendar                                     = None,
        es:                    None | int | float | str | dt.date | dt.datetime    = None,
        ef:                    None | int | float | str | dt.date | dt.datetime    = None,
        ls:                    None | int | float | str | dt.date | dt.datetime    = None,
        lf:                    None | int | float | str | dt.date | dt.datetime    = None,

        direct_cost:           None | float | int                                  = None,
        overhead_rate:                float | int                                  = 0.0,
        overhead_criterion:    str                                                 = 'direct_cost',
        indirect_cost:         None | float | int                                  = None,
        total_cost:            None | float | int                                  = None,

        duration_distribution: str                                                 = 'fixed',
        duration_mean:         None | float | int                                  = None,
        duration_stdev:               float | int                                  = 0.0,
        duration_params:       dict | None                                         = None,
        cost_distribution:     str                                                 = 'fixed',
        cost_mean:             None | float | int                                  = None,
        cost_stdev:                   float | int                                  = 0.0,
        cost_params:           dict | None                                         = None,

        as_date:               None | int | float | str | dt.date | dt.datetime    = None,
        af_date:               None | int | float | str | dt.date | dt.datetime    = None,
    ): 
        
        # Basic
        self.name = str(name)

        # Planning
        self.predecessors = predecessors if predecessors is not None else {}       
        self.successors   =                                               {}

        # Resources, Duration
        self.baseline_resources = baseline_resources if baseline_resources is not None else {}
        self.baseline_duration =  float(baseline_duration)
        self.resources =          resources          if resources          is not None else {}
        self.effort_driven =      bool(effort_driven)
        self.duration =           self._calculate_duration()

        # Scheduling
        self.calendar =      calendar
        self.es =            None if es is None else Calendar._parse_date(es)
        self.ef =            None if ef is None else Calendar._parse_date(ef)
        self.ls =            None if ls is None else Calendar._parse_date(ls)
        self.lf =            None if lf is None else Calendar._parse_date(lf)
        self.es_constraint = self.es is not None
        self.ef_constraint = self.ef is not None
        self.ls_constraint = self.ls is not None
        self.lf_constraint = self.lf is not None
        self.slack         = None
        if self.calendar is not None and self.es is not None and self.ls is not None:
            self.slack    = self.calendar._networkdays(self.es, self.ls) - 1
            self.critical = self.slack <= 0
        else:
            self.slack    = None
            self.critical = None

        # Costs
        self.direct_cost =        self._calculate_direct_cost()   if direct_cost   is None else direct_cost
        self.overhead_rate =      float(overhead_rate)
        self.overhead_criterion = overhead_criterion
        self.indirect_cost =      self._calculate_indirect_cost() if indirect_cost is None else indirect_cost
        self.total_cost =         self._calculate_total_cost()    if total_cost    is None else total_cost

        # MC Simulation
        self.duration_distribution = duration_distribution
        self.duration_mean =         self.duration   if duration_mean   is None else float(duration_mean)
        self.duration_stdev =        float(duration_stdev)
        self.duration_params =       {}              if duration_params is None else duration_params 
        self.cost_distribution =     cost_distribution
        self.cost_mean =             self.total_cost if cost_mean       is None else float(cost_mean)
        self.cost_stdev =            float(cost_stdev)
        self.cost_params =           {}              if cost_params     is None else cost_params  

        self.criticality =           0.0

        # Allocations
        self._add_allocations()

        # Monitoring
        self._as_date = None
        self._as_days = None
        if as_date is not None:
            self.as_date = as_date

        self._af_date = None
        self._af_days = None
        if af_date is not None:
            self.af_date = af_date

        self.records =              {}
        self.control_accounts =     {}
        self._add_controlaccounts()

    # Duration

    def _calculate_duration(self) -> float:
        b_res = self.baseline_resources
        if self.effort_driven and b_res:
            res = self.resources
            if res:
                scaling_factors: list[float] = []
                for r, requirement in b_res.values():
                    if r.name in res:
                        allocated = res[r.name][1]
                        if r.resource_type == 'work':
                            if allocated > 0:
                                scaling_factors.append(allocated / requirement)
                            else:
                                return math.inf
                        else:
                            if allocated >= requirement:
                                scaling_factors.append(1.0)
                            else:
                                return math.inf
                    else:
                        return math.inf
                else:
                    return self.baseline_duration / min(scaling_factors, default=1.0)
            else:
                return math.inf
        else:
            return self.baseline_duration

    # Costs

    def _calculate_direct_cost(self) -> float:
        pd_days = self.baseline_duration
        total = 0.0
        for r, units in self.resources.values():
            total += r.unit_cost * units * pd_days if r.resource_type == 'work' else r.unit_cost * units
        return total

    def _calculate_indirect_cost(self) -> float:
        return self.duration * self.overhead_rate
    
    def _calculate_total_cost(self) -> float:
        return self.direct_cost + self.indirect_cost
    
    # Allocations

    def _add_allocations(self) -> None:
        if self.direct_cost > 0.0 and not self.baseline_resources:
            r = Resource(
                name = f'[{self.name}] Direct', 
                resource_type = 'cost', 
                unit_cost = self.direct_cost,
            )
            self.baseline_resources[r.name] = (r, 1.0)
            self.resources[r.name] = (r, 1.0)
        for r, units in self.resources.values():
            r.allocations[self.name] = (self, float(units))

    # Monitoring
    
    ## CAs

    def _add_controlaccounts(self) -> None:
        for r, u in self.resources.values():
            ca = ControlAccount(
                name=f'{self.name}-{r.name}',
                activity=self,
                resource=r,
                units=u,
            )
            self.control_accounts[ca.name] = ca    

    ## AS

    @property
    def as_date(self) -> dt.date | None:
        return self._as_date

    @property
    def as_days(self) -> int | None:
        return self._as_days

    @as_date.setter
    def as_date(
        self, 
        value: dt.date | dt.datetime | str | int | float | None
    ) -> None:
        if value is None:
            self._as_date = None
            self._as_days = None
            return
        cal = self.calendar
        self._as_date = Calendar._parse_date(value)
        if cal is not None and self.es is not None:
            self._as_days = cal._networkdays(self.es, self._as_date) - 1
        else:
            self._as_days = None

    ## AF

    @property
    def af_date(self) -> dt.date | None:
        return self._af_date

    @property
    def af_days(self) -> int | None:
        return self._af_days
    
    @af_date.setter
    def af_date(
        self, 
        value: dt.date | dt.datetime | str | int | float | None
    ) -> None:
        if value is None:
            self._af_date = None
            self._af_days = None
            return
        cal = self.calendar
        self._af_date = Calendar._parse_date(value)
        if cal is not None and self.es is not None:
            self._af_days = cal._networkdays(self.es, self._af_date) - 1
        else:
            self._af_days = None

    ## EVM

    def add_update_record(
        self, 
        date_key: dt.date | dt.datetime | str | int | float, 
        wp: float
    ) -> None:
        
        # Calendar
        cal = self.calendar

        # AS, AT
        as_date = self.as_date
        as_days = self.as_days
        af_date = self.af_date
        af_days = self.af_days
        at_date = cal._parse_date(date_key)
        at_days = cal._networkdays(as_date, at_date)

        # BAC, PD
        bac = self.total_cost
        pd_days = self.duration
        pd_date = self.ef

        # WS
        if as_date is not None and pd_days > 0:
            if at_date < as_date:
                ws = 0.0
            else:
                nd = cal._networkdays(as_date, at_date)
                ws = max(
                    0.0, 
                    min(nd, pd_days) / pd_days
                )
        else:
            ws = 0.0
        
        # AC
        ac = 0.0
        for ca in self.control_accounts.values():
            if date_key in ca.records:
                ac_record = ca.records[date_key]['AC']
            else:
                prev_dates = [d for d in ca.records if d <= date_key]
                ac_record = ca.records[max(prev_dates)]['AC'] if prev_dates else None
            if ac_record is not None:
                ac += ac_record

        # PV, EV, CV, SV, CPI, SPI, CEACs, TEACs
        pv = bac * ws                   
        ev = bac * wp                   
        cv = ev - ac                    
        sv = ev - pv                    
        cpi = ev / ac if ac != 0.0 else 1.0 
        spi = ev / pv if pv != 0.0 else 1.0
        ceac_cv = bac - cv
        ceac_cpi = bac / cpi if cpi != 0 else math.inf
        teac_spi_days = pd_days / spi if spi != 0 else math.inf
        teac_spi_date = cal._workday(as_date, teac_spi_days) if teac_spi_days != math.inf else math.inf

        # Add Record
        self.records[date_key] = {
            'AS[Date]': as_date,
            'AF[Date]': af_date,
            'PD[Date]': pd_date,
            'AT[Date]': at_date,
            'AS[Days]': as_days,
            'AF[Days]': af_days,
            'PD[Days]': pd_days,
            'AT[Days]': at_days,
            'BAC': bac,
            'WS': ws, 
            'WP': wp, 
            'PV': pv, 
            'EV': ev, 
            'AC': ac,
            'CV': cv,
            'SV': sv,
            'CPI': cpi,
            'SPI': spi,
            'EAC_CV': ceac_cv,
            'EAC_CPI': ceac_cpi,
            'EAC(t)_SPI[Date]': teac_spi_date,
            'EAC(t)_SPI[Days]': teac_spi_days
        }

    def df_evm(self) -> pd.DataFrame:
        recs = self.records
        for date_key in sorted(recs):
            wp = max(
                (rec.get('WP', 0.0)
                for rec_date, rec in recs.items()
                if rec_date <= date_key),
                default=0.0,
            )
            for ca in self.control_accounts.values():
                ac = max(
                    (rec.get('AC', 0.0)
                    for rec_date, rec in ca.records.items()
                    if rec_date <= date_key),
                    default=0.0,
                )
                ca.add_update_record(date_key, ac)
            self.add_update_record(date_key, wp)
            self.project.add_update_record(date_key)
        return pd.DataFrame.from_dict(recs, orient='index')

    # MC Simulation

    def _sample_dimension(
            self, 
            dimension: str
    ) -> float:
        if dimension == 'duration':
            distribution = self.duration_distribution
            mean = self.duration_mean
            stdev = self.duration_stdev
            params = self.duration_params
        elif dimension == 'cost':
            distribution = self.cost_distribution
            mean = self.cost_mean
            stdev = self.cost_stdev
            params = self.cost_params
        match distribution:
            case 'fixed':
                return float(mean)
            case 'uniform':
                return float(np.random.uniform(params['low'], params['high']))
            case 'exponential':
                return float(np.random.exponential(mean))
            case 'normal':
                return float(np.random.normal(mean, stdev))
            case 'log-normal':
                variance = stdev ** 2
                mu = np.log(mean ** 2 / math.sqrt(variance + mean ** 2))
                sigma = math.sqrt(math.log(1 + (variance / mean ** 2)))
                return np.random.lognormal(mu, sigma)
            case 'triangular':
                return float(np.random.triangular(params['left'], params['mode'], params['right']))
            case 'pert':
                low = params['left']
                high = params['right']
                mode = params['mode']
                mean = (low + 4 * mode + high) / 6
                variance = ((high - low) / 6) ** 2
                alpha = ((mean - low) / (high - low)) * ((mean * (1 - mean)) / variance - 1)
                beta = alpha * (1 - (mean - low) / (high - low))
                return float(low + (high - low) * np.random.beta(alpha, beta))
            case 'beta':
                return float(np.random.beta(params['a'], params['b']) * (stdev if stdev else 1) + mean)


class ControlAccount:
    """
    Control Account class.
    """

    activity:      Activity
    resource:      Resource
    name:          str
    units:         float
    duration:      float

    direct_cost:   float
    indirect_cost: float
    total_cost:    float

    records:       dict[int, dict]

    __slots__ = (
        'activity',
        'resource',
        'name',
        'units',
        'duration',

        'direct_cost',
        'indirect_cost',
        'total_cost',

        'records',
    )
    _acronym = 'CA'
    __str__ = _common_str
    __repr__ = _common_repr

    def __init__(
        self,
        activity: Activity,
        resource: Resource,
        name: str | None,
        units: float | int | str,
    ):
       
        # Basic
        self.activity = activity
        self.resource = resource 
        self.name =     str(name) if name is not None else f'{self.activity.name}-{self.resource.name}'
        self.units =    float(units)
        self.duration = self.activity.duration

        # Costs
        self.direct_cost =   self._calculate_direct_cost()
        self.indirect_cost = self._calculate_indirect_cost()
        self.total_cost =    self._calculate_total_cost()

        # Monitoring
        self.records: dict[int, dict] = {}
    
    # Costs

    def _calculate_direct_cost(self) -> float:
        if self.resource.resource_type == 'work':
            return self.resource.unit_cost * self.units * self.activity.baseline_duration
        else:
            return self.resource.unit_cost * self.units

    def _calculate_indirect_cost(self) -> float:
        match self.activity.overhead_criterion:
            case 'direct_cost':
                if self.activity.direct_cost > 0.0:
                    return self.activity.indirect_cost * (self.direct_cost / self.activity.direct_cost)
                return self.activity.indirect_cost        
            case _:
                return 0.0
    
    def _calculate_total_cost(self) -> float:
        return self.direct_cost + self.indirect_cost
    
    # Monitoring

    ## EVM
    
    def add_update_record(
        self, 
        date: dt.date | dt.datetime | str | int | float, 
        ac: float | int
    ) -> None:

        # Calendar
        act = self.activity
        cal = act.calendar

        # AS, AT
        as_date = act.as_date
        as_days = act.as_days
        af_date = act.af_date
        af_days = act.af_days
        at_date = cal._parse_date(date)
        at_days = cal._networkdays(as_date, at_date)

        # BAC, PD
        bac = self.total_cost
        pd_days = act.duration
        pd_date = act.ef

        # WS
        if as_date is not None and pd_days > 0:
            if at_date < as_date:
                ws = 0.0
            else:
                nd = cal._networkdays(as_date, at_date)
                ws = max(
                    0.0, 
                    min(nd, pd_days) / pd_days
                )
        else:
            ws = 0.0
    
        # WP
        wp = max(
            (
                rec.get('WP', 0.0)
                for rec_date, rec in self.activity.records.items()
                if rec_date <= date
            ),
            default=0.0,
        )
        
        # PV, EV, CV, SV, CPI, SPI, CEACs, TEACs
        pv = bac * ws                   
        ev = bac * wp                   
        cv = ev - ac                    
        sv = ev - pv                    
        cpi = ev / ac if ac != 0.0 else 1.0 
        spi = ev / pv if pv != 0.0 else 1.0
        ceac_cv = bac - cv
        ceac_cpi = bac / cpi if cpi != 0 else math.inf
        teac_spi_days = pd_days / spi if spi != 0 else math.inf
        teac_spi_date = cal._workday(as_date, teac_spi_days) if teac_spi_days != math.inf else math.inf
        
        # Add Record
        self.records[date] = {
            'AS[Date]': as_date,
            'AF[Date]': af_date,
            'PD[Date]': pd_date,
            'AT[Date]': at_date,
            'AS[Days]': as_days,
            'AF[Days]': af_days,
            'PD[Days]': pd_days,
            'AT[Days]': at_days,
            'BAC': bac,
            'WS': ws, 
            'WP': wp, 
            'PV': pv, 
            'EV': ev, 
            'AC': ac,
            'CV': cv,
            'SV': sv,
            'CPI': cpi,
            'SPI': spi,
            'EAC_CV': ceac_cv,
            'EAC_CPI': ceac_cpi,
            'EAC(t)_SPI[Date]': teac_spi_date,
            'EAC(t)_SPI[Days]': teac_spi_days
        }

    def df_evm(self) -> pd.DataFrame:
        recs = self.records
        for date_key in sorted(recs):
            ac = max(
                (rec.get('AC', 0.0) 
                 for rec_date, rec in recs.items()
                 if rec_date <= date_key), 
                 default=0.0
            )
            self.add_update_record(date_key, ac)
            act = self.activity
            wp = max(
                (rec.get('WP', 0.0) 
                for rec_date, rec in act.records.items() 
                if rec_date <= date_key), 
                default=0.0
            )
            act.add_update_record(date_key, wp)
            act.project.add_update_record(date_key)
        return pd.DataFrame.from_dict(recs, orient='index')
    
class Project:
    """
    Project class.
    """

    activities: dict[str, Activity]
    name:       str

    calendar:    Calendar
    start_date:  dt.date
    finish_date: dt.date
    duration:    int

    tracking_freq:  str
    tracking_dates: list[dt.date]

    resources:        dict[str, Resource]
    control_accounts: dict[str, ControlAccount]
        
    direct_cost:   float
    indirect_cost: float
    total_cost:    float

    records: dict[int, dict]
    as_date: dt.date | None
    as_days: int     | None
    af_date: dt.date | None
    af_days: int     | None

    df_mc:                  pd.DataFrame
    df_mc_pmb_project:      pd.DataFrame
    df_mc_pmb_project_cuml: pd.DataFrame

    __slots__ = (
        'activities',
        'name',

        'calendar',
        'start_date', 'finish_date', 
        'duration',

        'tracking_freq',
        'tracking_dates',

        'resources',
        'control_accounts',
        
        'direct_cost',
        'indirect_cost',
        'total_cost',

        'records',
        'as_date', 'as_days',
        'af_date', 'af_days',

        'df_mc',
        'df_mc_pmb_project',
        'df_mc_pmb_project_cuml',
    )
    _acronym = 'P'
    __str__ = _common_str
    __repr__ = _common_repr

    def __init__(
        self,
        activities: dict[str, Activity] | Iterable[Activity],
        name:       str = 'Project',
        calendar:   None | Calendar = None,
        start_date: None | dt.datetime | dt.date | int | float | str = None,
        tracking_freq: str = 'D',
    ):

        # Basic
        self.name = str(name)

        # Planning
        self.calendar = Calendar() if calendar is None else calendar
        self.start_date = dt.datetime.today().date() if start_date is None else Calendar._parse_date(start_date)

        # Activities
        self.activities = activities if isinstance(activities, dict) else {a.name: a for a in activities}
        self._add_dependencies()
        self._init_activities()

        # Resources
        self.resources: dict[str, Resource] = {}
        self._add_resources()

        # Scheduling
        self._cpm()
        self._calculate_costs()

        # Control Accounts
        self.control_accounts: dict[str, ControlAccount] = {}
        self._add_controlaccounts()

        # Monitoring
        self.records: dict[int, dict] = {}
        self.as_date = None
        self.as_days = None
        self.af_date = None
        self.af_days = None
        self.tracking_freq = tracking_freq
        self.tracking_dates: list[dt.date] = []
        self._init_tracking_dates()
        self._init_activities_records()
        self._init_controlaccounts_records()
        self._init_project_records()

        # MC Simulation
        self.df_mc = pd.DataFrame()
        self.df_mc_pmb_project = pd.DataFrame()
        self.df_mc_pmb_project_cuml = pd.DataFrame()

    # Activities

    def _add_dependencies(self) -> None:
        for a in self.activities.values():
            if a.predecessors:
                for predecessor, rel_type, lag in a.predecessors.values():
                    predecessor.successors[a.name] = (a, rel_type, lag)

    def _init_activities(self) -> None:
        for a in self.activities.values():

            # Calendar
            if a.calendar is None:
                a.calendar = self.calendar

            # Scheduling
            if a.es is None and a.ef is None:
                es = self.start_date
                while not a.calendar._is_working_day(es):
                    es += dt.timedelta(days=1)
                a.es = es
                a.ef = a.calendar._workday(a.es, +(a.duration - 1))
            elif a.es is not None and a.ef is None:
                a.ef = a.calendar._workday(a.es, +(a.duration - 1))
            elif a.es is None and a.ef is not None:
                a.es = a.calendar._workday(a.ef, -(a.duration - 1))
            elif a.es is not None and a.ef is not None:
                a.duration = a.calendar._networkdays(a.es, a.ef)

            if a.ls is None and a.lf is None:
                a.ls = a.es
                a.lf = a.ef
            elif a.ls is not None and a.lf is None:
                a.lf = a.calendar._workday(a.ls, +(a.duration - 1))
            elif a.ls is None and a.lf is not None:
                a.ls = a.calendar._workday(a.lf, -(a.duration - 1))
            elif a.ls is not None and a.lf is not None:
                a.duration = min(
                    a.duration,
                    a.calendar._networkdays(a.ls, a.lf),
                )

            # Project
            a.project = self

    # Resources

    def _add_resources(self) -> None:
        for a in self.activities.values():
            for r, _ in a.resources.values():
                self.resources[r.name] = r

    # Scheduling

    def _calculate_costs(self) -> None:
        acts = self.activities
        self.direct_cost = sum(a.direct_cost for a in acts.values())
        self.indirect_cost = sum(a.indirect_cost for a in acts.values())
        self.total_cost = self.direct_cost + self.indirect_cost

    def _cpm(self) -> None:
        acts = list(self.activities.values())
        if not acts:
            self.finish_date = self.start_date
            self.duration = 0
            return

        processed_activities: set[Activity] = set()

        # Forward Pass (ES, EF)
        while len(processed_activities) < len(acts):
            for a in acts:
                if a in processed_activities:
                    continue
                if not getattr(a, 'es_constraint', False):
                    start_date = self.start_date
                    if a.predecessors:
                        max_start = start_date
                        all_predecessors_processed = True
                        for (predecessor, rel_type, lag) in a.predecessors.values():
                            if predecessor not in processed_activities:
                                all_predecessors_processed = False
                                break
                            if rel_type == 'fs':
                                candidate = a.calendar._workday(predecessor.ef, lag + 1)
                            elif rel_type == 'ff':
                                candidate = a.calendar._workday(predecessor.ef, -a.duration + lag)
                            elif rel_type == 'ss':
                                candidate = a.calendar._workday(predecessor.es, lag)
                            elif rel_type == 'sf':
                                candidate = a.calendar._workday(predecessor.es, -a.duration + lag - 1)
                            else:
                                candidate = start_date
                            max_start = max(max_start, candidate)
                        if all_predecessors_processed:
                            a.es = max(start_date, max_start)
                            if not getattr(a, 'ef_constraint', False):
                                a.ef = a.calendar._workday(a.es, max(0, a.duration - 1))
                            processed_activities.add(a)
                    else:
                        if not getattr(a, 'ef_constraint', False):
                            if a.es is None:
                                a.es = start_date
                            a.ef = a.calendar._workday(a.es, max(0, a.duration - 1))
                        processed_activities.add(a)
                else:
                    if not getattr(a, 'ef_constraint', False):
                        a.ef = a.calendar._workday(a.es, max(0, a.duration - 1))
                    processed_activities.add(a)

        # Interlude
        self.finish_date = max(a.ef for a in acts)
        self.duration = self.calendar._networkdays(self.start_date, self.finish_date)

        # Backward Pass (LS, LF)
        for a in acts:
            if not a.successors and not getattr(a, 'lf_constraint', False):
                a.lf = self.finish_date
                a.ls = a.calendar._workday(a.lf, -a.duration + 1)

        processed_activities.clear()
        while len(processed_activities) < len(acts):
            for a in acts:
                if a in processed_activities:
                    continue
                if not getattr(a, 'lf_constraint', False):
                    finish_date = self.finish_date
                    if a.successors:
                        min_finish = finish_date
                        all_successors_processed = True
                        for successor, rel_type, lag in a.successors.values():
                            if successor not in processed_activities:
                                all_successors_processed = False
                                break
                            if rel_type == 'fs':
                                candidate = a.calendar._workday(successor.ls, -lag - 1)
                            elif rel_type == 'ff':
                                candidate = a.calendar._workday(successor.lf, -lag - 1)
                            elif rel_type == 'ss':
                                candidate = a.calendar._workday(successor.ls, successor.duration - a.duration - lag)
                            elif rel_type == 'sf':
                                candidate = a.calendar._workday(successor.lf, successor.duration - a.duration - lag)
                            else:
                                candidate = finish_date
                            min_finish = min(min_finish, candidate) 
                        if all_successors_processed:
                            a.lf = max(a.ef, min_finish)
                            if not getattr(a, 'ls_constraint', False):
                                a.ls = a.calendar._workday(a.lf, -a.duration + 1)
                            processed_activities.add(a)
                    else:
                        processed_activities.add(a)
                else:
                    if not getattr(a, 'ls_constraint', False):
                        a.ls = a.calendar._workday(a.lf, -a.duration + 1)
                    processed_activities.add(a)

        # AS, Slack, Critical
        for a in acts:
            a.as_date = a.es
            a.slack = a.calendar._networkdays(a.es, a.ls) - 1
            a.critical = a.slack <= 0

        # Resource.cost
        resource_costs: dict[Resource, float] = {r: 0.0 for r in self.resources.values()}
        for a in acts:
            baseline_duration = a.baseline_duration
            for r, units in a.resources.values():
                if r.resource_type == 'work':
                    resource_costs[r] += r.unit_cost * units * baseline_duration
                else:
                    resource_costs[r] += r.unit_cost * units
        for r, c in resource_costs.items():
            r._cost = c

    def plot_gantt(self) -> None:
        _, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        ax.set_title('Gantt Chart')
        ax.set_xlabel('Time')
        ax.set_ylabel('Activity')
        df = self.df_activities()
        for i, row in df.iterrows():
            color = 'red' if row['Critical'] else 'blue'
            ax.barh(
                i,
                row['EF'] - row['ES'],
                left=row['ES'] + dt.timedelta(days=-1),
                color=color,
                alpha=0.8,
            )
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels(df['Name'])
        ax.invert_yaxis()
        plt.show()

    # CAs

    def _add_controlaccounts(self) -> None:
        for a in self.activities.values():
            for ca in a.control_accounts.values():
                self.control_accounts[ca.name] = ca

    # Monitoring

    def _init_tracking_dates(self) -> None:
        self.tracking_dates = sorted(
            {
                d.date()
                for d in pd.date_range(
                    self.start_date,
                    self.finish_date,
                    freq=self.tracking_freq,
                )
            }
        )

    def _init_activities_records(self) -> None:
        for a in self.activities.values():
            i = 1
            cal = a.calendar
            as_date_planned = a.es
            for at_date in self.tracking_dates:
                if cal._is_working_day(at_date):
                    i += 1
                date_key = int(at_date.strftime('%Y%m%d'))
                at_days = cal._networkdays(as_date_planned, at_date)
                bac = a.total_cost
                pd_days = a.duration
                pd_date = a.ef
                ws = max(0.0, min(1.0, i / pd_days)) if pd_days != 0 else 1.0

                a.records[date_key] = {
                    'AS[Date]': None,
                    'AF[Date]': None,
                    'PD[Date]': pd_date,
                    'AT[Date]': at_date,
                    'AS[Days]': None,
                    'AF[Days]': None,
                    'PD[Days]': pd_days,
                    'AT[Days]': at_days,
                    'BAC': bac,
                    'WS': ws, 
                    'WP': 0.0, 
                    'PV': bac * ws, 
                    'EV': 0.0, 
                    'AC': 0.0,
                    'CV': 0.0,
                    'SV': 0.0,
                    'CPI': 1.0,
                    'SPI': 1.0,
                    'EAC_CV': bac,
                    'EAC_CPI': bac,
                    'EAC(t)_SPI[Date]': pd_date,
                    'EAC(t)_SPI[Days]': pd_days
                }

    def _init_controlaccounts_records(self) -> None:
        for ca in self.control_accounts.values():
            i = 1
            cal = ca.activity.calendar
            as_date_planned = ca.activity.es
            for at_date in self.tracking_dates:
                if cal._is_working_day(at_date):
                    i += 1
                date_key = int(at_date.strftime('%Y%m%d'))
                at_days = cal._networkdays(as_date_planned, at_date)
                bac = ca.total_cost
                pd_days = ca.activity.duration
                pd_date = ca.activity.ef
                ws = max(0.0, min(1.0, i / pd_days)) if pd_days != 0 else 1.0

                ca.records[date_key] = {
                    'AS[Date]': None,
                    'AF[Date]': None,
                    'PD[Date]': pd_date,
                    'AT[Date]': at_date,
                    'AS[Days]': None,
                    'AF[Days]': None,
                    'PD[Days]': pd_days,
                    'AT[Days]': at_days,
                    'BAC': bac,
                    'WS': ws, 
                    'WP': 0.0, 
                    'PV': bac * ws, 
                    'EV': 0.0, 
                    'AC': 0.0,
                    'CV': 0.0,
                    'SV': 0.0,
                    'CPI': 1.0,
                    'SPI': 1.0,
                    'EAC_CV': bac,
                    'EAC_CPI': bac,
                    'EAC(t)_SPI[Date]': pd_date,
                    'EAC(t)_SPI[Days]': pd_days
                }

    def _init_project_records(self) -> None:
        as_date_planned = self.start_date
        for at_date in self.tracking_dates:
            date_key = int(at_date.strftime('%Y%m%d'))
            at_days = self.calendar._networkdays(as_date_planned, at_date)
            bac = self.total_cost
            pd_days = self.duration
            pd_date = self.finish_date
            
            pv = 0.0
            for ca in self.control_accounts.values():
                pv += ca.records[date_key]['PV']

            self.records[date_key] = {
                'AS[Date]': None,
                'AF[Date]': None,
                'PD[Date]': pd_date,
                'AT[Date]': at_date,
                'AS[Days]': None,
                'AF[Days]': None,
                'PD[Days]': pd_days,
                'AT[Days]': at_days,
                'BAC': bac,
                'WS': pv / bac if bac != 0 else 1.0, 
                'WP': 0.0, 
                'PV': pv, 
                'EV': 0.0, 
                'AC': 0.0,
                'CV': 0.0,
                'SV': 0.0,
                'CPI': 1.0,
                'SPI': 1.0,
                'EAC_CV': bac,
                'EAC_CPI': bac,
                'EAC(t)_SPI[Date]': pd_date,
                'EAC(t)_SPI[Days]': pd_days,
                'ES[Date]': None,
                'ES[Days]': None, 
                'SV(t)': 0.0,
                'SPI(t)': 1.0,
                'EAC(t)_SV(t)[Date]': pd_date,
                'EAC(t)_SV(t)[Days]': pd_days,
                'EAC(t)_SPI(t)[Date]': pd_date,
                'EAC(t)_SPI(t)[Days]': pd_days,               
            }

    # Dataframes

    def df_activities(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    'Name':          a.name,
                    'Predecessors': ', '.join(
                        f'{p.name}({r})+{l}'
                        for p, r, l in (a.predecessors or {}).values()
                    ),
                    'Successors': ', '.join(
                        f'{p.name}({r})+{l}'
                        for p, r, l in (a.successors or {}).values()
                    ),
                    'Duration':      a.duration,
                    'Direct Cost':   a.direct_cost,
                    'Indirect Cost': a.indirect_cost,
                    'Total Cost':    a.total_cost,
                    'ES':            a.es,
                    'EF':            a.ef,
                    'LS':            a.ls,
                    'LF':            a.lf,
                    'Slack':         a.slack,
                    'Critical':      a.critical,
                }
                for a in self.activities.values()
            ]
        )

    def df_resources(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    'Name':         r.name,
                    'Type':         r.resource_type,
                    'Availability': r.availability,
                    'Unit Cost':    r.unit_cost,
                    'Cost':         r.cost
                }
                for r in self.resources.values()
            ]
        )

    def df_controlaccounts(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    'Name':          ca.name,
                    'Activity':      ca.activity.name,
                    'Resource':      ca.resource.name,
                    'Units':         ca.units,
                    'Duration':      ca.duration,
                    'Direct Cost':   ca.direct_cost,
                    'Indirect Cost': ca.indirect_cost,
                    'Total Cost':    ca.total_cost,
                }
                for ca in self.control_accounts.values()
            ]
        )

    def df_project(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                'Name':          [self.name],
                'Start Date':    [self.start_date],
                'Finish Date':   [self.finish_date],
                'Duration':      [self.duration],
                'Direct Cost':   [self.direct_cost],
                'Indirect Cost': [self.indirect_cost],
                'Total Cost':    [self.total_cost],
            }
        )

    # Monte Carlo Simulation

    def mc(
        self,
        n_simulations: int = 1,
        track_pmb: bool = False,
        ) -> None:

        baseline_project_values = {
            'finish_date':    getattr(self, 'finish_date', None),
            'duration':       getattr(self, 'duration', None),
            'direct_cost':    getattr(self, 'direct_cost', None),
            'indirect_cost':  getattr(self, 'indirect_cost', None),
            'total_cost':     getattr(self, 'total_cost', None),
            'tracking_dates': list(getattr(self, 'tracking_dates', [])),
        }

        baseline_activities_values = {
            name: {
                'duration':      a.duration,
                'direct_cost':   a.direct_cost,
                'indirect_cost': a.indirect_cost,
                'total_cost':    a.total_cost,
                'es':            getattr(a, 'es', None),
                'ef':            getattr(a, 'ef', None),
                'ls':            getattr(a, 'ls', None),
                'lf':            getattr(a, 'lf', None),
                'slack':         getattr(a, 'slack', None),
                'critical':      getattr(a, 'critical', None),
                'as_date':       getattr(a, 'as_date', None),
            }
            for name, a in self.activities.items()
        }

        finish_dates = []
        direct_costs = []
        indirect_costs = []
        total_costs = []
        pmb_project_scenarios = []
        pmb_project_cum_scenarios = []

        def _restore_baseline():
            self.finish_date =    baseline_project_values['finish_date']
            self.duration =       baseline_project_values['duration']
            self.direct_cost =    baseline_project_values['direct_cost']
            self.indirect_cost =  baseline_project_values['indirect_cost']
            self.total_cost =     baseline_project_values['total_cost']
            self.tracking_dates = list(baseline_project_values['tracking_dates'])
            for name, attrs in baseline_activities_values.items():
                a = self.activities[name]
                for attr, value in attrs.items():
                    setattr(a, attr, value)

        for _ in range(n_simulations):
            _restore_baseline()

            for a in self.activities.values():
                a.duration =      a._sample_dimension('duration')
                a.direct_cost =   a._sample_dimension('cost')
                a.indirect_cost = a.duration * a.overhead_rate
                a.total_cost =    a.direct_cost + a.indirect_cost

            self._cpm()
            self._calculate_costs()

            # if track_pmb:
            #     self._init_tracking_dates()

            finish_dates.append(self.finish_date)
            direct_costs.append(self.direct_cost)
            indirect_costs.append(self.indirect_cost)
            total_costs.append(self.total_cost)

            if track_pmb:
                _, _, pmb_project, pmb_project_cuml = self._pmb()
                pmb_project_scenarios.append(pmb_project.to_numpy())
                pmb_project_cum_scenarios.append(pmb_project_cuml.to_numpy())

        self.df_mc = pd.DataFrame(
            {
                'Finish Date':   finish_dates,
                'Direct Cost':   direct_costs,
                'Indirect Cost': indirect_costs,
                'Total Cost':    total_costs,
            }
        )

        if track_pmb:
            def _aggregate_scenarios(scenarios) -> pd.DataFrame:
                max_len = max(len(arr) for arr in scenarios)
                data = np.full((len(scenarios), max_len), np.nan, dtype=float)
                for i, arr in enumerate(scenarios):
                    data[i, : len(arr)] = arr
                return pd.DataFrame(
                    {
                        'min':  np.nanmin(data, axis=0),
                        'p05':  np.nanpercentile(data, 5, axis=0),
                        'p25':  np.nanpercentile(data, 25, axis=0),
                        'p50':  np.nanpercentile(data, 50, axis=0),
                        'mean': np.nanmean(data, axis=0),
                        'p75':  np.nanpercentile(data, 75, axis=0),
                        'p95':  np.nanpercentile(data, 95, axis=0),
                        'max':  np.nanmax(data, axis=0),
                    }
                )
            self.df_mc_pmb_project =      _aggregate_scenarios(pmb_project_scenarios)
            self.df_mc_pmb_project_cuml = _aggregate_scenarios(pmb_project_cum_scenarios)
        else:
            self.df_mc_pmb_project =      pd.DataFrame()
            self.df_mc_pmb_project_cuml = pd.DataFrame()

    def plot_mc_1d(
        self,
        x: str,
        ) -> None:
        x_data = self.df_mc[x]
        _, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        ax.set_title('MC Analysis: ' + x)
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel(x)
        ax.set_ylabel('Frequency')
        ax.hist(x_data, color='tab:blue')   
        pcts = [.25, .50, .75, .90]
        x_qs = np.quantile(x_data, pcts)
        ax.set_xticks(x_qs)
        if x in ['Direct Cost', 'Indirect Cost', 'Total Cost']:
            ax.set_xticklabels([f'{x_qs[i]:.0f} ({pcts[i]:.2f})' for i in range(len(pcts))], rotation=90)
        else:
            ax.set_xticklabels([f'{x_qs[i]} ({pcts[i]:.2f})' for i in range(len(pcts))], rotation=90)
        try:
            ax1 = ax.twinx()
            ax1.spines[['top', 'bottom', 'left']].set_visible(False)
            ax1.set_ylabel('Probability')
            ax1.set_ylim(0, 1)
            for x_q in x_qs:
                ax.axvline(
                    x_q, 
                    color='grey', 
                    linestyle='--',
                    linewidth=.5, 
                )
            ax1.ecdf(x_data, color='tab:orange')
            ax1.set_yticks([.00, .25, .50, .75, .90, 1.00])
        except Exception:
            pass
        plt.show()

    def plot_mc_2d(
        self,
        x: str,
        y: str,
        ) -> None:
        
        x_data = self.df_mc[x]
        y_data = self.df_mc[y]

        # 2D
        pcts = [0.25, 0.5, 0.75, .90]
        x_qs = np.quantile(x_data, pcts)
        y_qs = np.quantile(y_data, pcts)

        _, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8), dpi=100)
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_xticks(x_qs)
        ax.set_yticks(y_qs)
        if x in ['Direct Cost', 'Indirect Cost', 'Total Cost']:
            ax.set_xticklabels([f'{x_qs[i]:.0f} ({pcts[i]:.2f})' for i in range(len(pcts))], rotation=90)
        else:
            ax.set_xticklabels([f'{x_qs[i]} ({pcts[i]:.2f})' for i in range(len(pcts))], rotation=90)
        if y in ['Direct Cost', 'Indirect Cost', 'Total Cost']:
            ax.set_yticklabels([f'{y_qs[i]:.0f} ({pcts[i]:.2f})' for i in range(len(pcts))])
        else:
            ax.set_yticklabels([f'{y_qs[i]} ({pcts[i]:.2f})' for i in range(len(pcts))]) 
        for x_q in x_qs:
            ax.axvline(
                x_q, 
                color='grey', 
                linestyle='--',
                linewidth=.5, 
                alpha = .75
            )
        for y_q in y_qs:
            ax.axhline(
                y_q, 
                color='grey', 
                linestyle='--',
                linewidth=.5, 
                alpha = .75
            )
        ax.scatter(
            x_data,
            y_data,
        )

        # 1D
        divider = make_axes_locatable(ax)
        ax_histx = divider.append_axes('top', 1.5, pad=0.5, sharex=ax)
        ax_histy = divider.append_axes('right', 1.5, pad=0.5, sharey=ax)

        ## Top
        ### Histogram
        ax_histx.spines[['right', 'top']].set_visible(False)
        ax_histx.tick_params(axis='x', labelbottom=False)
        ax_histx.set_ylabel('Frequency')
        ax_histx.hist(x_data, bins='auto')
        ### Line
        try:
            ax1 = ax_histx.twinx()
            ax1.spines[['top', 'bottom', 'left']].set_visible(False)
            ax1.set_ylabel('Probability')
            ax1.set_ylim(0, 1)
            ax1.set_yticks([.00, .25, .50, .75, .90, 1.00])
            ax1.ecdf(x_data, color='tab:orange')
        except:
            pass

        ## Right
        ### Histogram
        ax_histy.spines[['right', 'top']].set_visible(False)
        ax_histy.tick_params(axis='y', labelleft=False)
        ax_histy.set_xlabel('Frequency')
        ax_histy.hist(y_data, bins='auto', orientation='horizontal')
        ### Line
        try:
            ax2 = ax_histy.twiny()
            ax2.spines[['bottom', 'right', 'left']].set_visible(False)
            ax2.set_xlabel('Probability')
            ax2.set_xlim(0, 1)
            ax2.set_xticks([.00, .25, .50, .75, .90, 1.00])
            ax2.ecdf(y_data, color='tab:orange', orientation='horizontal')
        except Exception:
            pass

        plt.show()

    def plot_mc_pmb(
        self,
        cuml: bool = True,
        ) -> None:
        _, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel('Time')
        if cuml:
            data = self.df_mc_pmb_project_cuml.values.T
            ax.set_title('MC Analysis: cuml S-Curve')
            ax.set_ylabel('PV')
        else:
            data = self.df_mc_pmb_project.values.T
            ax.set_title('MC Analysis: Marginal S-Curve')
            ax.set_ylabel('dPV')
        time_points = np.arange(data.shape[1])
        LB, p25, p50, p75, UB = [
            np.nanpercentile(data, p, axis=0) for p in [10, 25, 50, 75, 90]
        ]
        min_curve, max_curve = np.nanmin(data, axis=0), np.nanmax(data, axis=0)
        ax.set_xlim(int(time_points.min()), int(time_points.max()))
        ax.set_ylim(0, float(max_curve.max()) if np.isfinite(max_curve.max()) else 1)
        ax.fill_between(time_points, min_curve, max_curve, color='tab:blue', alpha=0.25)
        ax.fill_between(time_points, LB, UB, color='tab:blue', alpha=0.25)
        ax.fill_between(time_points, p25, p75, color='tab:blue', alpha=0.25)
        ax.plot(time_points, p50, color='tab:blue')
        plt.show()

    # Performance Measurement Baseline

    def _pmb(self):
        activities = list(self.activities.values())

        dates = self.tracking_dates
        num_dates = len(dates)

        a_names = [a.name for a in activities]
        num_activities = len(a_names)

        pmb_array = np.zeros((num_activities, num_dates), dtype=float)
        a_name_to_index = {a.name: i for i, a in enumerate(activities)}
        date_to_index = {date: i for i, date in enumerate(dates)}

        for a in activities:
            working_days = [
                target_date.date()
                for target_date in pd.date_range(a.es, a.ef, freq='D')
                if a.calendar._is_working_day(target_date.date())
            ]
            daily_cost = a.total_cost / len(working_days) if working_days else 0.0

            a_idx = a_name_to_index[a.name]
            for day in working_days:
                idx = date_to_index.get(day)
                if idx is not None:
                    pmb_array[a_idx, idx] = daily_cost

        pmb_cuml = np.cumsum(pmb_array, axis=1)
        pmb_project = np.sum(pmb_array, axis=0)
        pmb_project_cuml = np.cumsum(pmb_project)

        df_pmb = pd.DataFrame(pmb_array, index=a_names, columns=dates)
        df_pmb_cuml = pd.DataFrame(pmb_cuml, index=a_names, columns=dates)

        df_pmb_project = pd.Series(pmb_project, index=dates, name='PV')
        df_pmb_project_cuml = pd.Series(pmb_project_cuml, index=dates, name='PV')
        
        return df_pmb, df_pmb_cuml, df_pmb_project, df_pmb_project_cuml

    def pmb(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        df_pmb, df_pmb_cuml, df_pmb_project, df_pmb_project_cuml = (
            self._pmb()
        )
        df_pmb = df_pmb.T
        return df_pmb, df_pmb_cuml, df_pmb_project, df_pmb_project_cuml

    def _resource_usage(self):
        activities = list(self.activities.values())
        resources = list(self.resources.values())

        dates = self.tracking_dates
        num_dates = len(dates)

        r_names = [r.name for r in resources]
        num_resources = len(r_names)

        usage_array = np.zeros((num_resources, num_dates), dtype=float)

        r_name_to_index = {resource.name: i for i, resource in enumerate(resources)}
        date_to_index = {date: i for i, date in enumerate(dates)}
        for a in activities:
            working_days = [
                date.date()
                for date in pd.date_range(a.es, a.ef, freq='D')
                if a.calendar._is_working_day(date.date())
            ]
            if not working_days:
                continue
            for res_name, (r, units) in a.resources.items():
                res_idx = r_name_to_index.get(res_name)
                if res_idx is None:
                    continue
                daily_use = units
                for day in working_days:  # day is datetime.date
                    day_idx = date_to_index.get(day)
                    if day_idx is not None:
                        usage_array[res_idx, day_idx] += daily_use
        usage_cuml = np.cumsum(usage_array, axis=1)
        df_resource_usage = pd.DataFrame(usage_array, index=r_names, columns=dates)
        df_resource_usage_cuml = pd.DataFrame(
            usage_cuml,
            index=r_names,
            columns=dates,
        )
        return df_resource_usage, df_resource_usage_cuml

    def resource_usage(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        df_resource_usage, df_resource_usage_cuml = self._resource_usage()
        return df_resource_usage.T, df_resource_usage_cuml.T

    # Monitoring

    def add_update_record(
        self,
        date_key: int,
    ) -> None:
        
        # Calendar
        cal = self.calendar

        # AS, AT
        at_date = cal._parse_date(date_key)
        
        as_dates = [a.as_date for a in self.activities.values() if a.as_date is not None]
        as_date = min(as_dates) if as_dates else None
        as_days = None if as_date is None else cal._networkdays(as_date, at_date)
        
        af_dates = [a.af_date for a in self.activities.values() if a.af_date is not None]
        af_date = max(af_dates) if af_dates else None
        af_days = None if af_date is None else cal._networkdays(as_date, af_date)
        

        at_days = cal._networkdays(as_date, at_date)

        # BAC, PD
        bac = self.total_cost
        pd_days = self.duration
        pd_date = self.finish_date

        # PV, EV, AC
        pv = 0.0
        ev = 0.0
        ac = 0.0
        for a in self.activities.values():
            rec = a.records[date_key]
            pv += rec['PV']
            ev += rec['EV']
            ac += rec['AC']

        # WS, WP, CV, SV, CPI, SPI, CEACs, TEACs
        ws = pv / bac                   
        wp = ev / bac                                               
        cv = ev - ac                                                
        sv = ev - pv                                                
        cpi = ev / ac if ac != 0.0 else 1.0                             
        spi = ev / pv if pv != 0.0 else 1.0                             
        ceac_cv = bac - cv
        ceac_cpi = bac / cpi if cpi != 0 else math.inf
        teac_spi_days = pd_days / spi if spi != 0 else math.inf
        teac_spi_date = cal._workday(as_date, teac_spi_days) if teac_spi_days != math.inf else math.inf

        # ESs, SV(t), SPI(t)
        es_days = 0.0
        
        _, _, _, ppmb_cuml = self.pmb()
        ppmb_cuml_ws = ppmb_cuml / bac
        if wp <= 0:
            es_days = 0.0
            es_date = as_date
        elif wp >= 1:
            es_days = pd_days
            es_date = pd_date
        else:
            c = sum(1 for val in ppmb_cuml_ws.values if wp > val)
            es_date = ppmb_cuml_ws.index[c]
            es_days = cal._networkdays(as_date, es_date)

        sv_t = es_days - at_days
        spi_t = es_days / at_days if at_days != 0.0 else 1.0
        teac_sv_t_days = pd_days - sv_t
        teac_sv_t_date = cal._workday(as_date, teac_sv_t_days) if teac_sv_t_days != math.inf else math.inf
        teac_spi_t_days = pd_days / spi_t if spi_t != 0 else math.inf
        teac_spi_t_date = cal._workday(as_date, teac_spi_t_days) if teac_spi_t_days != math.inf else math.inf

        # Add Record
        self.records[date_key] = {
            'AS[Date]': as_date,
            'AF[Date]': af_date,
            'PD[Date]': pd_date,
            'AT[Date]': at_date,
            'AS[Days]': as_days,
            'AF[Days]': af_days,
            'PD[Days]': pd_days,
            'AT[Days]': at_days,
            'BAC': bac,
            'WS': ws, 
            'WP': wp, 
            'PV': pv, 
            'EV': ev, 
            'AC': ac,
            'CV': cv,
            'SV': sv,
            'CPI': cpi,
            'SPI': spi,
            'EAC_CV': ceac_cv,
            'EAC_CPI': ceac_cpi,
            'EAC(t)_SPI[Days]': teac_spi_days,
            'EAC(t)_SPI[Date]': teac_spi_date,
            'ES[Days]': es_days,
            'ES[Date]': es_date,
            'SV(t)': sv_t,
            'SPI(t)': spi_t,
            'EAC(t)_SV(t)[Days]': teac_sv_t_days,
            'EAC(t)_SV(t)[Date]': teac_sv_t_date,
            'EAC(t)_SPI(t)[Days]': teac_spi_t_days,
            'EAC(t)_SPI(t)[Date]': teac_spi_t_date,
        }

    def df_evm(self) -> pd.DataFrame:
        recs = self.records
        for date_key in sorted(recs):
            for a in self.activities.values():
                wp = max(
                    (
                        rec.get('WP', 0.0)
                        for rec_date, rec in a.records.items()
                        if rec_date <= date_key
                    ),
                    default=0.0
                )
                for control_account in a.control_accounts.values():
                    ac = max(
                        (
                            rec.get('AC', 0.0)
                            for rec_date, rec in control_account.records.items()
                            if rec_date <= date_key
                        ),
                        default=0.0
                    )
                    control_account.add_update_record(date_key, ac)
                a.add_update_record(date_key, wp)
            self.add_update_record(date_key)
        return pd.DataFrame.from_dict(recs, orient='index')

class Portfolio:
    """
    Portfolio class.
    """

    __slots__ = (
        'projects',
    )
    _acronym = 'PF'
    __str__ = _common_str
    __repr__ = _common_repr

    def __init__(
        self,
        projects: dict[str, Project] | Iterable[Project],
    ) -> None:
        self.projects = {p.name: p for p in projects} if not isinstance(projects, dict) else projects


    def df_projects(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    'Name': p.name,
                    'Start Date': p.start_date,
                    'Finish Date': p.finish_date,
                    'Tracking Frequency': p.tracking_freq,
                    'Duration': p.duration,
                    'Direct Cost': p.direct_cost,
                    'Indirect Cost': p.indirect_cost,
                    'Total Cost': p.total_cost,
                }
                for p in self.projects.values()
            ]
        )

    def df_projects_evm(self) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        keys: list[str] = []
        for name, p in self.projects.items():
            frames.append(p.df_evm())
            keys.append(name)
        df = pd.concat(frames, keys=keys, names=['Project Name', 'AT[Date]']).reset_index(level='Project Name')
        df['AD[Date]'] = np.nan
        df['AD[Days]'] = np.nan
        df['AC(AD)'] = np.nan

        completed = (
            df.loc[df['WP'] == 1]
            .groupby('Project Name')
            .agg(
                AD=('AT[Days]', 'max'),
                AC_AD=('AC', 'max')
            )
            .rename(columns={'AC_AD': 'AC(AD)'})
        )
        df = df.merge(completed, on='Project Name', how='left')
        return df
