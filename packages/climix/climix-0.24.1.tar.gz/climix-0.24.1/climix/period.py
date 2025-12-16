# -*- coding: utf-8 -*-

from collections import namedtuple
import logging

import iris
import iris.coord_categorisation

from .index_functions.support import ComputationalPeriod


class Period:
    def __init__(self, output_coord, label, constraint=None, specialization=None):
        self.constraint = constraint
        self.input_coord = "time"
        self.output_coord = output_coord
        self.label = label
        self.specialization = specialization


class Annual(Period):
    YEAR = "jfmamjjasond" * 3
    MONTHS_SHORT = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]
    MONTHS = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    def __init__(self, season, timerange):
        self.computational_period = ComputationalPeriod(timerange)
        if isinstance(season, str):
            self.season = season.lower()
            if self.season[:3] in self.MONTHS_SHORT:
                self.season = self.season[:3]
                self.first_month_number = self.MONTHS_SHORT.index(self.season) + 1
                self.last_month_number = self.first_month_number
            else:
                self.first_month_number = self.YEAR.find(self.season) + 1
                self.last_month_number = self.first_month_number + len(self.season) - 1

            if self.last_month_number > 12:
                self.last_month_number %= 12

                def selector(cell):
                    m = cell.point.month
                    if self.computational_period.timerange is not None:
                        t = cell.point
                        return (
                            (self.first_month_number <= m <= 12)
                            | (1 <= m <= self.last_month_number)
                        ) and (
                            self.computational_period.timerange.start
                            < t
                            < self.computational_period.timerange.end
                        )
                    return (self.first_month_number <= m <= 12) | (
                        1 <= m <= self.last_month_number
                    )

            else:

                def selector(cell):
                    m = cell.point.month
                    if self.computational_period.timerange is not None:
                        t = cell.point
                        return (
                            self.first_month_number <= m <= self.last_month_number
                        ) and (
                            self.computational_period.timerange.start
                            < t
                            < self.computational_period.timerange.end
                        )
                    return self.first_month_number <= m <= self.last_month_number

            constraint = iris.Constraint(time=selector)
            super().__init__("year", "yr", constraint, self.season)
        else:

            def selector(cell):
                t = cell.point
                return (
                    self.computational_period.timerange.start
                    < t
                    < self.computational_period.timerange.end
                )

            self.season = None
            if self.computational_period.timerange is not None:
                constraint = iris.Constraint(time=selector)
            else:
                constraint = None
            super().__init__("year", "yr", constraint)

    @staticmethod
    def season_complement(season):
        season = season.lower()
        length = len(season)
        index = Annual.YEAR.find(season)
        if index < 0:
            # Can't match the season, raise an error.
            raise ValueError("unrecognised season: {!s}".format(season))
        complement_length = 12 - length
        complement_start = index + length
        complement_end = complement_start + complement_length
        complement_season = Annual.YEAR[complement_start:complement_end]
        return complement_season

    def long_label(self):
        first_month = self.MONTHS[self.first_month_number - 1]
        last_month = self.MONTHS[self.last_month_number - 1]
        long_label = f"{first_month}-{last_month}"
        return long_label

    def add_coord_categorisation(self, cube):
        if self.season is None or self.season in self.MONTHS_SHORT:
            try:
                iris.coord_categorisation.add_year(
                    cube, self.input_coord, name=self.output_coord
                )
            except ValueError:
                existing_coord = cube.coords(self.output_coord)
                cube.remove_coord(self.output_coord)
                iris.coord_categorisation.add_year(
                    cube, self.input_coord, name=self.output_coord
                )
                logging.warning(
                    f"Existing coordinate <{existing_coord}> was removed. New "
                    f"coordinate <{cube.coords(self.output_coord)}> was added."
                )
        else:
            complement_season = Annual.season_complement(self.season)
            iris.coord_categorisation.add_season_year(
                cube,
                self.input_coord,
                name=self.output_coord,
                seasons=(self.season, complement_season),
            )
        return self.output_coord


class Monthly(Period):
    def __init__(self, seasons, timerange):
        self.seasons = seasons
        self.computational_period = ComputationalPeriod(timerange)
        if self.computational_period.timerange is not None:
            constraint = iris.Constraint(
                time=lambda t: self.computational_period.timerange.start
                < t.point
                < self.computational_period.timerange.end
            )
        else:
            constraint = None
        super().__init__(("year", "month_number"), "mon", constraint)

    def add_coord_categorisation(self, cube):
        try:
            iris.coord_categorisation.add_year(cube, self.input_coord, name="year")
        except ValueError:
            existing_coord = cube.coord("year")
            cube.remove_coord("year")
            iris.coord_categorisation.add_year(cube, self.input_coord, name="year")
            logging.warning(
                f"Existing coordinate <{existing_coord}> was removed. New coordinate "
                f"<{cube.coords('year')}> was added."
            )
        iris.coord_categorisation.add_month_number(
            cube, self.input_coord, name="month_number"
        )
        return self.output_coord


class Season(Period):
    def __init__(self, seasons, timerange):
        self.seasons = seasons
        self.computational_period = ComputationalPeriod(timerange)
        if self.computational_period.timerange is not None:
            constraint = iris.Constraint(
                time=lambda t: self.computational_period.timerange.start
                < t.point
                < self.computational_period.timerange.end
            )
        else:
            constraint = None
        super().__init__(("season_year", "season"), "sem", constraint)
        if self.seasons is None:
            self.seasons = ("djf", "mam", "jja", "son")

    def add_coord_categorisation(self, cube):
        iris.coord_categorisation.add_season_year(
            cube,
            self.input_coord,
            name="season_year",
            seasons=self.seasons,
        )
        iris.coord_categorisation.add_season(
            cube,
            self.input_coord,
            name="season",
            seasons=self.seasons,
        )
        return self.output_coord


PeriodSpecification = namedtuple("PeriodSpecification", "type parameters")

PERIODS = {
    "annual": Annual,
    "seasonal": Season,
    "monthly": Monthly,
}


def build_period(period_spec):
    try:
        Period = PERIODS[period_spec.type]
    except KeyError:
        raise ValueError(f"Unknown period specification <{period_spec}>")
    period = Period(*period_spec.parameters)
    return period
