"""
The MIT License (MIT)

Copyright (c) 2020 Arthurdw
Copyright (c) 2024-2025 null8626

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Union, Optional
from datetime import datetime
from enum import Enum


class DataPoint:
  """A data point."""

  __slots__: tuple[str, ...] = ('value',)

  value: int
  """This data point's value."""

  def __init__(self, value: int):
    self.value = value

  def __int__(self) -> int:
    return self.value

  def __float__(self) -> float:
    return float(self.value)

  def __str__(self) -> str:
    return str(self.value)

  def __eq__(self, other: object) -> bool:
    if other_float := getattr(other, '__float__', None):
      return self.value == other_float()

    return False

  def __lt__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value < float(other)

  def __gt__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value > float(other)

  def __le__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value <= float(other)

  def __ge__(self, other: Union['DataPoint', float, int]) -> bool:
    return self.value >= float(other)


class Ranked(DataPoint):
  """A ranked data point. This class contains a value and its rank compared to others and/or difference compared to its previous data point."""

  __slots__: tuple[str, ...] = ('rank', 'difference')

  rank: Optional[int]
  """This data point's rank compared to others."""

  difference: Optional[int]
  """This data point's change difference compared to its previous data point."""

  def __init__(self, json: dict, key: str):
    self.rank = json.get(f'{key}_rank')
    self.difference = json.get(f'{key}_change')

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} value={self.value!r} rank={self.rank!r} difference={self.difference!r}>'


class Timestamped(DataPoint):
  """A timestamped data point. This class contains a value and its dated timestamp."""

  __slots__: tuple[str, ...] = ('timestamp',)

  timestamp: datetime
  """When this data point was retrieved."""

  def __init__(self, json: dict, key: str):
    self.timestamp = datetime.fromisoformat(json['time'].replace('Z', '+00:00'))

    super().__init__(json[key])

  def __repr__(self) -> str:
    return f'<{__class__.__name__} value={self.value!r} timestamp={self.timestamp!r}>'


class Period(Enum):
  """The requested time period for fetching historical bot stats."""

  __slots__: tuple[str, ...] = ()

  ALL_TIME = 'alltime'
  LAST_5_YEARS = '5y'
  LAST_3_YEARS = '3y'
  LAST_YEAR = '1y'
  LAST_9_MONTHS = '270d'
  LAST_6_MONTHS = '180d'
  LAST_3_MONTHS = '90d'
  LAST_MONTH = '30d'
  LAST_WEEK = '7d'
  LAST_3_DAYS = '3d'
  LAST_DAY = '1d'
  LAST_12_HOURS = '12h'
  LAST_6_HOURS = '6h'

  def __repr__(self) -> str:
    return f'{__class__.__name__}.{self.name}'

  def __str__(self) -> str:
    return self.name.replace('_', ' ').title()


class SortBy:
  """The requested sorting method for sorting Discord bots."""

  __slots__: tuple[str, ...] = ('_by', '_method')

  def __init__(
    self,
    sort_by: str,
    ascending: bool,
  ):
    self._by = f'{sort_by}_rank'
    self._method = f'{"a" if ascending else "de"}sc'

  @staticmethod
  def monthly_votes(*, ascending: bool = False) -> 'SortBy':
    """
    Sorts Discord bots by their monthly vote count.

    :param ascending: Whether to sort by ascending or not. Defaults to sort by descending.
    :type ascending: :py:class:`bool`
    """

    return SortBy('monthly_votes', ascending)

  @staticmethod
  def total_votes(*, ascending: bool = False) -> 'SortBy':
    """
    Sorts Discord bots by their total vote count.

    :param ascending: Whether to sort by ascending or not. Defaults to sort by descending.
    :type ascending: :py:class:`bool`
    """

    return SortBy('total_votes', ascending)

  @staticmethod
  def server_count(*, ascending: bool = False) -> 'SortBy':
    """
    Sorts Discord bots by their server count.

    :param ascending: Whether to sort by ascending or not. Defaults to sort by descending.
    :type ascending: :py:class:`bool`
    """

    return SortBy('server_count', ascending)

  @staticmethod
  def review_count(*, ascending: bool = False) -> 'SortBy':
    """
    Sorts Discord bots by their review count.

    :param ascending: Whether to sort by ascending or not. Defaults to sort by descending.
    :type ascending: :py:class:`bool`
    """

    return SortBy('review_count', ascending)
