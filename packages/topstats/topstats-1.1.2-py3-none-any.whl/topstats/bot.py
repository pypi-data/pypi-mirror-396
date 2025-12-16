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

from datetime import datetime, timezone
from typing import Optional

from .data import Ranked


class BotStats:
  """A Discord bot's statistics."""

  __slots__: tuple[str, ...] = (
    'monthly_votes',
    'total_votes',
    'server_count',
    'review_count',
  )

  monthly_votes: Ranked
  """The amount of votes this bot has this month."""

  total_votes: Ranked
  """The amount of votes this bot has."""

  server_count: Ranked
  """The amount servers this bot is in."""

  review_count: Ranked
  """The amount reviews this bot has."""

  def __init__(self, json: dict):
    self.monthly_votes = Ranked(json, 'monthly_votes')
    self.total_votes = Ranked(json, 'total_votes')
    self.server_count = Ranked(json, 'server_count')
    self.review_count = Ranked(json, 'review_count')


class TimestampedBotStats(BotStats):
  """A Discord bot's timestamped stats. This class contains several data points and their dated timestamps."""

  __slots__: tuple[str, ...] = ('timestamp',)

  timestamp: datetime
  """When this stats was retrieved."""

  def __init__(self, json: dict):
    self.timestamp = datetime.fromisoformat(json['time'].replace('Z', '+00:00'))

    super().__init__(json)

  def __repr__(self) -> str:
    return f'<{__class__.__name__} monthly_votes={self.monthly_votes!r} total_votes={self.total_votes!r} server_count={self.server_count!r} review_count={self.review_count!r} timestamp={self.timestamp!r}>'


class RecentBotStats:
  """A Discord bot's recent stats for the past 30 hours and past month."""

  __slots__: tuple[str, ...] = (
    'hourly',
    'daily',
  )

  hourly: list[TimestampedBotStats]
  """This bot's stats for the past 30 hours."""

  daily: list[TimestampedBotStats]
  """This bot's stats for the past month."""

  def __init__(self, json: dict):
    self.hourly = [TimestampedBotStats(entry) for entry in json['hourlyData']]
    self.daily = [TimestampedBotStats(entry) for entry in json['dailyData']]

  def __repr__(self) -> str:
    return f'<{__class__.__name__} hourly={self.hourly!r} daily={self.daily!r}>'


class PartialBot(BotStats):
  """A Discord bot's brief information."""

  __slots__: tuple[str, ...] = ('id', 'name')

  id: int
  """This bot's Discord ID."""

  name: str
  """This bot's username."""

  def __init__(self, json: dict):
    self.id = int(json['id'])
    self.name = json['name']

    super().__init__(json)

  def __repr__(self) -> str:
    return f'<{self.__class__.__name__} id={self.id} name={self.name!r} monthly_votes={self.monthly_votes!r} server_count={self.server_count!r} review_count={self.review_count!r} total_votes={self.total_votes!r}>'

  def __int__(self) -> int:
    return self.id

  def __eq__(self, other: object) -> bool:
    if isinstance(other, __class__):
      return self.id == other.id

    return NotImplemented

  @property
  def created_at(self) -> datetime:
    """When this bot was created."""

    return datetime.fromtimestamp(
      ((self.id >> 22) + 1420070400000) // 1000, tz=timezone.utc
    )


class Bot(PartialBot):
  """A Discord bot's detailed information."""

  __slots__: tuple[str, ...] = (
    'topgg_id',
    'owners',
    'tags',
    'is_deleted',
    'avatar',
    'short_description',
    'prefix',
    'website',
    'submitted_at',
    'timestamp',
    'daily_difference',
    'monthly_difference',
  )

  topgg_id: int
  """This bot's Top.gg ID."""

  owners: list[int]
  """This bot's owner IDs."""

  tags: list[str]
  """This bot's tags."""

  is_deleted: bool
  """Whether this bot is deleted or not."""

  avatar: str
  """This bot's avatar URL."""

  short_description: str
  """This bot's short description."""

  prefix: str
  """This bot's prefix."""

  website: str
  """This bot's website URL."""

  submitted_at: datetime
  """When this bot was submitted on Top.gg."""

  timestamp: datetime
  """When this bot was updated by topstats.gg."""

  daily_difference: Optional[float]
  """Difference percentage from the previous day."""

  monthly_difference: Optional[float]
  """Difference percentage from the previous month."""

  def __init__(self, json: dict):
    self.topgg_id = int(json['topGGId'])
    self.owners = [int(i) for i in (json.get('owners') or ())]
    self.tags = json.get('tags') or []
    self.is_deleted = json['deleted']
    self.short_description = json['short_desc']
    self.prefix = json['prefix']
    self.website = json['website']
    self.submitted_at = datetime.fromisoformat(
      json['approved_at'].replace('Z', '+00:00')
    )
    self.timestamp = datetime.fromtimestamp(
      int(json['unix_timestamp']) // 1000, tz=timezone.utc
    )

    if percentage_changes := json.get('percentage_changes'):
      daily = percentage_changes.get('daily')
      monthly = percentage_changes.get('monthly')

      self.daily_difference = daily and float(daily)
      self.monthly_difference = monthly and float(monthly)
    else:
      self.daily_difference = None
      self.monthly_difference = None

    self.avatar = json['avatar']

    super().__init__(json)
