class GameCalendar:  # controls the time in game. to advance time in game we do it with this.
    def __init__(self, seconds, minutes, hours, days, months, years):
        self.SECONDS = seconds
        self.MINUTES = minutes
        self.HOURS = hours
        self.DAYS = days
        self.MONTHS = months
        self.YEARS = years
        self.SEASON = 'Spring'  # 'Summer', 'Winter', 'Fall'
        self.SECONDS_PER_MINUTE = 60
        self.MINUTES_PER_HOUR = 60
        self.HOURS_PER_DAY = 24
        self.DAYS_PER_MONTH = 28
        self.MONTHS_PER_YEAR = 12
        self.TURN = self.SECONDS + int(self.MINUTES * self.SECONDS_PER_MINUTE) + int(self.HOURS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR) + int(self.DAYS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR * self.HOURS_PER_DAY) + int(
            self.MONTHS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR * self.HOURS_PER_DAY * self.DAYS_PER_MONTH) + int(self.YEARS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR * self.HOURS_PER_DAY * self.DAYS_PER_MONTH * self.MONTHS_PER_YEAR)

    # if we need to do something every so often we should set it up here.
    def do_events(self):
        return

    def save_calendar(self):
        path = str("./world/calendar.data")
        with open(path, "w") as fp:
            fp.write(str(self.SECONDS) + ',' + str(self.MINUTES) + ',' + str(self.HOURS)+ ',' + str(self.DAYS) + ',' + str(self.MONTHS) + ',' + str(self.YEARS))

    def load_calendar(self):
        try:
            path = str("./world/calendar.data")
            with open(path) as calendar:
                data = calendar.read()
                split = data.split(',')
                self.SECONDS = int(split[0])
                self.MINUTES = int(split[1])
                self.HOURS = int(split[2])
                self.DAYS = int(split[3])
                self.MONTHS = int(split[4])
                self.YEARS = int(split[5])
        except FileNotFoundError:
            path = str("./world/calendar.data")
            with open(path, "w") as fp:
                fp.write(str(self.SECONDS) + ',' + str(self.MINUTES) + ',' + str(self.HOURS) + ',' + str(
                    self.DAYS) + ',' + str(self.MONTHS) + ',' + str(self.YEARS))
    def localtime(self):
        return str(self.HOURS) + ':' + str(self.MINUTES) + ':' + str(self.SECONDS)


    def advance_time_by_x_seconds(self, amount):
        for x in range(amount):
            self.SECONDS = self.SECONDS + 1
            self.do_events()  # if anything needs doing this will do it.
            if(self.SECONDS >= self.SECONDS_PER_MINUTE):
                self.SECONDS = 0
                self.MINUTES = self.MINUTES + 1

            if(self.MINUTES >= self.MINUTES_PER_HOUR):
                self.MINUTES = 0
                self.HOURS = self.HOURS + 1

            if(self.HOURS >= self.HOURS_PER_DAY):
                self.HOURS = 0
                self.DAYS = self.DAYS + 1

            if(self.DAYS >= self.DAYS_PER_MONTH):
                self.DAYS = 0
                self.MONTHS = self.MONTHS + 1

            if(self.MONTHS >= self.MONTHS_PER_YEAR):
                self.MONTHS = 0
                self.YEARS = self.YEARS + 1

    def advance_turn(self):
        """
        Advance the game by one turn (one second).
        This is the standard method to advance time in the game loop.
        """
        self.advance_time_by_x_seconds(1)

    def get_time_string(self):
        """
        Return a formatted string of the current time (HH:MM:SS).
        """
        return f"{self.HOURS:02}:{self.MINUTES:02}:{self.SECONDS:02}"

    def get_date_string(self):
        """
        Return a formatted string of the current date (Year-Month-Day, Season).
        """
        season = self.get_season()
        return f"Year {self.YEARS+1}, Month {self.MONTHS+1}, Day {self.DAYS+1} ({season})"

    def get_full_datetime_string(self):
        """
        Return a full string of the current date and time.
        """
        return f"{self.get_date_string()} {self.get_time_string()}"

    def is_night(self):
        """
        Return True if the current time is considered night (e.g., 20:00-6:00).
        """
        return self.HOURS < 6 or self.HOURS >= 20

    def is_day(self):
        """
        Return True if the current time is considered day (e.g., 6:00-20:00).
        """
        return not self.is_night()

    def get_day_of_year(self):
        """
        Return the day of the year (1-based).
        """
        return self.DAYS + 1 + self.MONTHS * self.DAYS_PER_MONTH

    def get_week_of_year(self):
        """
        Return the week of the year (1-based, 7 days per week).
        """
        return (self.get_day_of_year() - 1) // 7 + 1

    def get_total_seconds(self):
        """
        Return the total number of seconds since the start of the game.
        """
        return self.get_turn()

    def get_time_of_day(self):
        """
        Return a string representing the time of day (morning, afternoon, evening, night).
        """
        if 6 <= self.HOURS < 12:
            return "morning"
        elif 12 <= self.HOURS < 18:
            return "afternoon"
        elif 18 <= self.HOURS < 20:
            return "evening"
        else:
            return "night"

    def get_turn(self):
        self.TURN = self.SECONDS + int(self.MINUTES * self.SECONDS_PER_MINUTE) + int(self.HOURS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR) + int(self.DAYS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR * self.HOURS_PER_DAY) + int(
            self.MONTHS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR * self.HOURS_PER_DAY * self.DAYS_PER_MONTH) + int(self.YEARS * self.SECONDS_PER_MINUTE * self.MINUTES_PER_HOUR * self.HOURS_PER_DAY * self.DAYS_PER_MONTH * self.MONTHS_PER_YEAR)

        return self.TURN

    def moon_phase(self):  # moon phases are 1/4 month roughly
        # 28 days / 4 phases.
        # First Quarter, Full Moon, Third Quarter, New Moon
        if self.DAYS < self.DAYS_PER_MONTH * 0.25:
            return 'First Quarter'
        elif self.DAYS < self.DAYS_PER_MONTH * 0.5:
            return 'Full Moon'
        elif self.DAYS < self.DAYS_PER_MONTH * 0.75:
            return 'Third Quarter'
        else:
            return 'New Moon'

    def get_season(self):
        self.season_names = []
        self.season_names.insert(len(self.season_names), 'Spring')  # 0
        self.season_names.insert(len(self.season_names), 'Summer')  # 1
        self.season_names.insert(len(self.season_names), 'Winter')  # 2, etc..
        self.season_names.insert(len(self.season_names), 'Fall')
        if self.MONTHS < self.MONTHS_PER_YEAR * 0.25:
            self.SEASON = self.season_names[0]
        elif self.MONTHS < self.MONTHS_PER_YEAR * 0.5:
            self.SEASON = self.season_names[1]
        elif self.MONTHS < self.MONTHS_PER_YEAR * 0.75:
            self.SEASON = self.season_names[2]
        else:
            self.SEASON = self.season_names[3]

        return self.SEASON

    def sunrise(self):
        return

    def sunset(self):
        return

    def current_daylight_level(self):
        return

    def sunlight(self):
        return

    def day_of_week(self):
        self.weekday_names = []
        self.weekday_names.insert(len(self.weekday_names), 'Sunday')  # 0
        self.weekday_names.insert(len(self.weekday_names), 'Monday')  # 1
        # 2, etc..
        self.weekday_names.insert(len(self.weekday_names), 'Tuesday')
        self.weekday_names.insert(len(self.weekday_names), 'Wednesday')
        self.weekday_names.insert(len(self.weekday_names), 'Thursday')
        self.weekday_names.insert(len(self.weekday_names), 'Friday')
        self.weekday_names.insert(len(self.weekday_names), 'Saturday')
        days = self.DAYS  # How many days have passed this month.
        while(days >= len(self.weekday_names)):  # loop until we get a number 0-6
            days = days - len(self.weekday_names)

        # what's left over is the day of the week.
        return self.weekday_names[days]
