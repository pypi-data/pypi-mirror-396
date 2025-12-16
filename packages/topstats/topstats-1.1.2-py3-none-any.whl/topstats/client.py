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

from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from typing import Any, Optional, Union
from collections.abc import Iterable
from collections import namedtuple
from asyncio import sleep
from yarl import Query
from time import time
from re import sub
import json

from .errors import Error, RequestError, Ratelimited
from .ratelimiter import Ratelimiter, Ratelimiters
from .bot import Bot, PartialBot, RecentBotStats
from .data import Period, SortBy, Timestamped
from .version import VERSION


BASE_URL = 'https://api.topstats.gg'
MAXIMUM_DELAY_THRESHOLD = 5.0


class Client:
  """
  Interact with the API's endpoints.

  :param token: The API token to use. To retrieve it, see https://docs.topstats.gg/authentication/tokens/.
  :type token: :py:class:`str`
  :param session: Whether to use an existing :class:`~aiohttp.ClientSession` for requesting or not. Defaults to :py:obj:`None` (creates a new one instead)
  :type session: Optional[:class:`~aiohttp.ClientSession`]

  :exception TypeError: ``token`` is not a :py:class:`str` or is empty.
  """

  __slots__: tuple[str, ...] = (
    '__own_session',
    '__session',
    '__token',
    '__global_ratelimiter',
    '__ratelimiters',
    '__current_ratelimits',
  )

  def __init__(self, token: str, *, session: Optional[ClientSession] = None):
    if not isinstance(token, str) or not token:
      raise TypeError('An API token is required to use this API.')

    self.__own_session = session is None
    self.__session = session or ClientSession(
      timeout=ClientTimeout(total=MAXIMUM_DELAY_THRESHOLD * 1000.0)
    )
    self.__token = token

    self.__global_ratelimiter = Ratelimiter(119, 60)

    endpoint_ratelimits_kwargs = {
      'search': Ratelimiters((self.__global_ratelimiter, Ratelimiter(59, 60))),
      'discord_tags': Ratelimiters((self.__global_ratelimiter, Ratelimiter(59, 60))),
      'discord_bots': Ratelimiters((self.__global_ratelimiter, Ratelimiter(59, 60))),
      'discord_bots_historical': Ratelimiters(
        (self.__global_ratelimiter, Ratelimiter(59, 60))
      ),
      'discord_bots_recent': Ratelimiters(
        (self.__global_ratelimiter, Ratelimiter(59, 60))
      ),
      'discord_compare': Ratelimiters((self.__global_ratelimiter, Ratelimiter(59, 60))),
      'discord_compare_historical': Ratelimiters(
        (self.__global_ratelimiter, Ratelimiter(59, 60))
      ),
      'discord_rankings_bots': Ratelimiters(
        (self.__global_ratelimiter, Ratelimiter(59, 60))
      ),
      'discord_users_bots': Ratelimiters(
        (self.__global_ratelimiter, Ratelimiter(59, 60))
      ),
    }

    endpoint_ratelimits = namedtuple(
      'EndpointRatelimits', ' '.join(endpoint_ratelimits_kwargs.keys())
    )

    self.__ratelimiters = endpoint_ratelimits(**endpoint_ratelimits_kwargs)
    self.__current_ratelimits = endpoint_ratelimits(
      **{key: None for key in endpoint_ratelimits_kwargs.keys()}
    )

  def __repr__(self) -> str:
    return f'<{__class__.__name__} {self.__session!r}>'

  async def __get(
    self,
    path: str,
    **params: Query,
  ) -> Any:
    if self.__session.closed:
      raise Error('Client session is already closed.')

    ratelimiter_key = sub(
      '_{2,}', '_', sub(r'\d+', '', path).strip('/').replace('/', '_')
    )
    current_ratelimit = getattr(self.__current_ratelimits, ratelimiter_key)

    if current_ratelimit is not None:
      current_time = time()

      if current_time < current_ratelimit:
        raise Ratelimited(current_ratelimit - current_time)
      else:
        setattr(self.__current_ratelimits, ratelimiter_key, None)

    ratelimiter = getattr(self.__ratelimiters, ratelimiter_key)

    kwargs = {}

    if params:
      kwargs['params'] = params

    status = None
    retry_after = 0.0
    output = None

    async with ratelimiter:
      try:
        async with self.__session.get(
          BASE_URL + path,
          headers={
            'Authorization': self.__token,
            'Content-Type': 'application/json',
            'User-Agent': f'topstats (https://github.com/top-stats/python-sdk {VERSION}) Python/',
          },
          **kwargs,
        ) as resp:
          status = resp.status

          try:
            output = await resp.json()
            retry_after = float(output.get('expiresIn', 0)) / 1000.0
          except (ValueError, json.decoder.JSONDecodeError):
            pass

          resp.raise_for_status()

          return output
      except ClientResponseError:
        if status == 429 and retry_after is not None:
          if retry_after > MAXIMUM_DELAY_THRESHOLD:
            setattr(self.__current_ratelimits, ratelimiter_key, time() + retry_after)

            raise Ratelimited(retry_after) from None

          await sleep(retry_after)

          return await self.__get(path, **params)

        raise RequestError(output and output.get('message'), status) from None

  @staticmethod
  def __validate_ids(*ids: int) -> Iterable[str]:
    ids = tuple(set(ids))
    ids_len = len(ids)

    if not (2 <= ids_len <= 4):
      raise IndexError(f'Expected 2 to 4 unique bot IDs to compare, but got {ids_len}.')

    return map(str, ids)

  async def get_bot(self, id: int) -> Bot:
    """
    Fetches a Discord bot from its ID.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested bot.
    :rtype: :class:`.Bot`
    """

    return Bot(await self.__get(f'/discord/bots/{id}'))

  async def search_bots(
    self,
    *,
    name: Optional[str] = None,
    tag: Optional[str] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    include_deleted: bool = False,
  ) -> Iterable[Bot]:
    """
    Fetches and yields several Discord bots from their name or tag.

    :param name: The requested bot name. If :py:obj:`None`, defaults to the tag parameter.
    :type name: Optional[:py:class:`str`]
    :param tag: The requested bot tag. If :py:obj:`None`, defaults to the name parameter.
    :type tag: Optional[:py:class:`str`]
    :param offset: The amount of bots to be skipped.
    :type offset: Optional[:py:class:`int`]
    :param limit: The maximum amount of bots to be queried. Defaults to ``50`` or ``100`` depending on the parameter. This can't exceed the default value.
    :type limit: Optional[:py:class:`int`]
    :param include_deleted: Whether to include deleted bots or not. Defaults to :py:obj:`False`.
    :type include_deleted: :py:class:`bool`

    :exception Error: The client is already closed or both the name and tag parameters are unspecified.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of bots that matches the specified query.
    :rtype: Iterable[:class:`.Bot`]
    """

    url = '/search'
    query = name
    max_limit = 100

    if tag:
      url = '/discord/tags'
      query = tag
      max_limit = 50
    elif not name:
      raise Error('Either a bot name or tag must be specified.')

    return map(
      Bot,
      (
        await self.__get(
          url,
          query=query,
          offset=str(max(offset or 0, 0)),
          limit=str(max(min(limit or max_limit, max_limit), 1)),
          includeDeleted=str(include_deleted).lower(),
        )
      )['data']['results'],
    )

  async def compare_bots(self, *ids: int) -> Iterable[Bot]:
    """
    Fetches and yields several Discord bots from a set of IDs.

    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: The amount of IDs provided are not within range.
    :exception Error: The client is already closed.
    :exception RequestError: One of the specified bots do not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of bots to compare.
    :rtype: Iterable[:class:`.Bot`]
    """

    c = await self.__get(f'/discord/compare/{"/".join(Client.__validate_ids(*ids))}')

    return map(Bot, c['data'])

  async def get_users_bot(self, id: int) -> Iterable[Bot]:
    """
    Fetches a Discord user's Discord bots from their ID.

    :warning: Data returned by this method may be inaccurate! This is because bots moved to a team will remain on a user's account irrespective of ownership.

    :param id: The requested user's ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The specified user has not logged in to Top.gg or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of bots made by this user.
    :rtype: Iterable[:class:`.Bot`]
    """

    b = await self.__get(f'/discord/users/{id}/bots')

    return map(Bot, b.get('bots', ()))

  async def __get_historical_bot_stats(
    self, kind: str, id: int, period: Optional[Period]
  ) -> Iterable[Timestamped]:
    if not isinstance(period, Period):
      period = Period.ALL_TIME

    response = await self.__get(
      f'/discord/bots/{id}/historical', timeFrame=period.value, type=kind
    )

    return (Timestamped(data, kind) for data in response['data'])

  async def __compare_historical_bot_stats(
    self, kind: str, period: Optional[Union[Period, int]], *ids: int
  ) -> Iterable[tuple[Timestamped, ...]]:
    if not isinstance(period, Period):
      if isinstance(period, int):
        ids = period, *ids

      period = Period.ALL_TIME

    validated_ids = tuple(Client.__validate_ids(*ids))
    c = await self.__get(
      f'/discord/compare/historical/{"/".join(validated_ids)}',
      timeFrame=period.value,
      type=kind,
    )

    return zip(*((Timestamped(t, kind) for t in c['data'][i]) for i in validated_ids))

  async def get_historical_bot_monthly_votes(
    self, id: int, period: Optional[Period] = None
  ) -> Iterable[Timestamped]:
    """
    Fetches and yields a Discord bot's historical monthly vote count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of this bot's monthly vote counts.
    :rtype: Iterable[:class:`.Timestamped`]
    """

    return await self.__get_historical_bot_stats('monthly_votes', id, period)

  async def compare_bot_monthly_votes(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Iterable[tuple[Timestamped, ...]]:
    """
    Fetches and yields several Discord bots' historical monthly vote count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: The amount of IDs provided are not within range.
    :exception Error: The client is already closed.
    :exception RequestError: One of the specified bots do not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of monthly vote counts to compare.
    :rtype: Iterable[tuple[:class:`.Timestamped`, ...]]
    """

    return await self.__compare_historical_bot_stats('monthly_votes', period, *ids)

  async def get_historical_bot_total_votes(
    self, id: int, period: Optional[Period] = None
  ) -> Iterable[Timestamped]:
    """
    Fetches and yields a Discord bot's historical total vote count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of this bot's total vote counts.
    :rtype: Iterable[:class:`.Timestamped`]
    """

    return await self.__get_historical_bot_stats('total_votes', id, period)

  async def compare_bot_total_votes(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Iterable[tuple[Timestamped, ...]]:
    """
    Fetches and yields several Discord bots' historical total vote count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: The amount of IDs provided are not within range.
    :exception Error: The client is already closed.
    :exception RequestError: One of the specified bots do not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of total vote counts to compare.
    :rtype: Iterable[tuple[:class:`.Timestamped`, ...]]
    """

    return await self.__compare_historical_bot_stats('total_votes', period, *ids)

  async def get_historical_bot_server_count(
    self, id: int, period: Optional[Period] = None
  ) -> Iterable[Timestamped]:
    """
    Fetches and yields a Discord bot's historical server count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of this bot's server counts.
    :rtype: Iterable[:class:`.Timestamped`]
    """

    return await self.__get_historical_bot_stats('server_count', id, period)

  async def compare_bot_server_count(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Iterable[tuple[Timestamped, ...]]:
    """
    Fetches and yields several Discord bots' historical server count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: The amount of IDs provided are not within range.
    :exception Error: The client is already closed.
    :exception RequestError: One of the specified bots do not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of server counts to compare.
    :rtype: Iterable[tuple[:class:`.Timestamped`, ...]]
    """

    return await self.__compare_historical_bot_stats('server_count', period, *ids)

  async def get_historical_bot_review_count(
    self, id: int, period: Optional[Period] = None
  ) -> Iterable[Timestamped]:
    """
    Fetches and yields a Discord bot's historical review count for a certain period of time.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`
    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`.
    :type period: Optional[:class:`.Period`]

    :exception Error: The client is already closed.
    :exception RequestError: The specified bot does not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of this bot's review counts.
    :rtype: Iterable[:class:`.Timestamped`]
    """

    return await self.__get_historical_bot_stats('review_count', id, period)

  async def compare_bot_review_count(
    self, period: Optional[Union[Period, int]], *ids: int
  ) -> Iterable[tuple[Timestamped, ...]]:
    """
    Fetches and yields several Discord bots' historical review count for a certain period of time.

    :param period: The requested time period. Defaults to :attr:`.Period.ALL_TIME`. If this argument is an :py:class:`int`, then it will be treated as a bot ID as a part of the second argument.
    :type period: Optional[Union[:class:`.Period`, :py:class:`int`]]
    :param ids: Set of bot IDs to compare. The API currently only accepts 2 to 4 IDs.
    :type ids: :py:class:`int`

    :exception IndexError: The amount of IDs provided are not within range.
    :exception Error: The client is already closed.
    :exception RequestError: One of the specified bots do not exist or the client has received other non-favorable responses from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of review counts to compare.
    :rtype: Iterable[tuple[:class:`.Timestamped`, ...]]
    """

    return await self.__compare_historical_bot_stats('review_count', period, *ids)

  async def get_recent_bot_stats(self, id: int) -> RecentBotStats:
    """
    Fetches recent stats of a Discord bot for the past 30 hours and past month.

    :param id: The requested bot's ID.
    :type id: :py:class:`int`

    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested recent bot stats for the past 30 hours and past month.
    :rtype: :class:`.RecentBotStats`
    """

    return RecentBotStats(await self.__get(f'/discord/bots/{id}/recent'))

  async def get_top_bots(
    self, sort_by: SortBy, *, limit: Optional[int] = None
  ) -> Iterable[PartialBot]:
    """
    Fetches and yields top Discord bots based on a certain criteria.

    :param sort_by: The requested criteria and sorting method.
    :type sort_by: :class:`.SortBy`
    :param limit: Limit of data to be returned. Defaults to ``100``. This can't exceed ``100``.
    :type limit: Optional[:py:class:`int`]

    :exception TypeError: The requested sorting criteria is of invalid type.
    :exception Error: The client is already closed.
    :exception RequestError: The client received a non-favorable response from the API.
    :exception Ratelimited: Ratelimited from sending more requests.

    :returns: The requested list of top bots based on the requested criteria.
    :rtype: Iterable[:class:`.PartialBot`]
    """

    if not isinstance(sort_by, SortBy):
      raise TypeError('The requested sorting criteria is of invalid type.')

    t = await self.__get(
      '/discord/rankings/bots',
      limit=str(max(min(limit or 100, 100), 1)),
      sortBy=sort_by._by,
      sortMethod=sort_by._method,
    )

    return map(PartialBot, t.get('data', ()))

  async def close(self) -> None:
    """Closes the :class:`.Client` object. Nothing will happen if the client uses a pre-existing :class:`~aiohttp.ClientSession` or if the session is already closed."""

    if self.__own_session and not self.__session.closed:
      await self.__session.close()

  async def __aenter__(self) -> 'Client':
    return self

  async def __aexit__(self, *_, **__) -> None:
    await self.close()
