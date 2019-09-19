
WEEKDAY_NAMES = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
SEASON_NAMES = ('Spring', 'Summer', 'Winter', 'Fall')
DAYS_IN_WEEK = 7
MONTHS_PER_YEAR = 12
DAYS_PER_MONTH = 28
HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
SECONDS_PER_MINUTE = 60

MONTHS_PER_QUARTER = 4
DAYS_PER_QUARTER = DAYS_PER_MONTH * MONTHS_PER_QUARTER
SECONDS_PER_HOUR = SECONDS_PER_MINUTE*MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_HOUR*HOURS_PER_DAY
SECONDS_PER_MONTH = SECONDS_PER_DAY*DAYS_PER_MONTH
SECONDS_PER_YEAR = SECONDS_PER_MONTH*MONTHS_PER_YEAR


class Calendar:  # controls the time in game. to advance time in game we do it with this.
    def __init__(self, seconds, minutes, hours, days, months, years):
        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours
        self.days = days
        self.months = months
        self.years = years

    def do_events(self):  # if we need to do something every so often we should set it up here.
        return

    def advance_time_by_x_seconds(self, amount):
        for x in range(amount):
            self.seconds += 1
            self.do_events()  # if anything needs doing this will do it.
            if self.seconds >= SECONDS_PER_MINUTE:
                self.seconds = 0
                self.minutes += 1

            if self.minutes >= MINUTES_PER_HOUR:
                self.minutes = 0
                self.hours += 1

            if self.hours >= HOURS_PER_DAY:
                self.hours = 0
                self.days += 1

            if self.days >= DAYS_PER_MONTH:
                self.days = 0
                self.months += 1

            if self.months >= MONTHS_PER_YEAR:
                self.months = 0
                self.years += 1

    @property
    def turn(self):
        return self.seconds + \
               self.minutes * SECONDS_PER_MINUTE + \
               self.hours * SECONDS_PER_HOUR + \
               self.days * SECONDS_PER_DAY + \
               self.months * SECONDS_PER_MONTH + \
               self.years * SECONDS_PER_YEAR

    def moon_phase(self):  # moon phases are 1/4 month roughly
        # 28 days / 4 phases.
        # First Quarter, Full Moon, Third Quarter, New Moon
        if self.days < DAYS_PER_QUARTER:
            return 'First Quarter'
        elif self.days < DAYS_PER_QUARTER * 2:
            return 'Full Moon'
        elif self.days < DAYS_PER_QUARTER * 3:
            return 'Third Quarter'
        else:
            return 'New Moon'

    @property
    def season(self):
        if self.months < MONTHS_PER_QUARTER:
            return SEASON_NAMES[0]
        elif self.months < MONTHS_PER_QUARTER * 2:
            return SEASON_NAMES[1]
        elif self.months < MONTHS_PER_QUARTER * 3:
            return SEASON_NAMES[2]
        else:
            return SEASON_NAMES[3]

    def sunrise(self):
        return

    def sunset(self):
        return

    def current_daylight_level(self):
        return

    def sunlight(self):
        return

    def day_of_week(self):
        days = self.days % DAYS_IN_WEEK
        return WEEKDAY_NAMES[days]
