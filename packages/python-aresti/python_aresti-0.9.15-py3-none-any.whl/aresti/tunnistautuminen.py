import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cached_property
import time
from typing import ClassVar, Iterable, Literal, Optional

from aiohttp import BasicAuth

from .yhteys import AsynkroninenYhteys


@dataclass(kw_only=True)
class Tunnistautuminen(AsynkroninenYhteys):

  tunnistautuminen: dict = field(init=False, repr=False)

  def __post_init__(self):
    try:
      # pylint: disable=no-member
      super_post_init = super().__post_init__
    except AttributeError:
      pass
    else:
      super_post_init()
      # else
    # def __post_init__

  async def pyynnon_otsakkeet(self, **kwargs):
    return {
      **await super().pyynnon_otsakkeet(**kwargs),
      **(self.tunnistautuminen or {}),
    }
    # async def pyynnon_otsakkeet

  # class Tunnistautuminen


@dataclass(kw_only=True)
class KayttajaSalasanaTunnistautuminen(Tunnistautuminen):

  kayttajatunnus: str
  salasana: str = field(default='', repr=False)

  def __post_init__(self):
    super().__post_init__()
    self.tunnistautuminen = {
      'Authorization': BasicAuth(self.kayttajatunnus, self.salasana).encode()
    }
    # def __post_init__

  # class KayttajaSalasanaTunnistautuminen


@dataclass(kw_only=True)
class AvainTunnistautuminen(Tunnistautuminen):

  avain: str = field(repr=False)

  avaimen_tyyppi: ClassVar[Literal['Token', 'Bearer']] = 'Token'

  def __post_init__(self):
    super().__post_init__()
    self.tunnistautuminen = {
      'Authorization': f'{self.avaimen_tyyppi} {self.avain}'
    }
    # def __post_init__

  # class AvainTunnistautuminen


@dataclass(kw_only=True)
class Oauth2Tunnistautuminen(AsynkroninenYhteys):

  oauth2_palvelin: Optional[str] = None  # Oletuksena `palvelin`.

  kayttaja_id: str
  yksityinen_avain_pem: str = field(repr=False)
  avain_id: Optional[str] = None

  oikeus: str | Iterable[str] = ()
  avaimen_voimassaolo: timedelta = timedelta(seconds=300)

  @dataclass(kw_only=True)
  class Oauth2Yhteys(AsynkroninenYhteys):

    # PEM-avain ja sen haltija.
    kayttaja_id: str
    yksityinen_avain_pem: str = field(repr=False)
    algoritmi: str = 'ES256'

    # Avaimen valinta (`kid`).
    avain_id: Optional[str] = None

    # API-polku, johon OAuth-avainnuspyyntö tehdään.
    avainnus_polku: ClassVar[str] = '/api/oauth2/token'

    # Välimuisti jo pyydetyistä ja saaduista avaimista.
    _saadut_avaimet: set[
      tuple[
        frozenset[str],  # Saadut oikeustasot.
        str,             # Bearer-avain.
        datetime,        # Voimassaolo päättyen.
      ],
    ] = field(default_factory=set, init=False, repr=False)

    # Lukko, jolla estetään useiden avainten haku rinnakkain.
    _avainpyynto_lukko: asyncio.Lock = field(
      default_factory=asyncio.Lock,
      init=False,
      repr=False,
    )

    class TunnistautuminenEpaonnistui(AsynkroninenYhteys.Poikkeus):
      pass

    async def _hae_avain(
      self,
      scope: Iterable[str],  # Pyydetyt oikeudet.
      exp: timedelta,        # Pyydetty voimassaolo.
    ) -> tuple[
      frozenset[str],  # Saadut oikeudet.
      str,             # Bearer-avain.
      datetime,        # Voimassaolo päättyen.
    ]:
      import jwt
      assert self.palvelin is not None
      koko_polku = self.palvelin + self.avainnus_polku
      vaatimus = {
        'sub': str(self.kayttaja_id),
        'iss': str(self.kayttaja_id),
        'exp': int(time.time()) + exp.total_seconds(),
        'nbf': int(time.time()),
        'aud': koko_polku,
        'scope': ' '.join(scope),
      }
      data = {
        'grant_type': 'client_credentials',
        'audience': koko_polku,
        'client_assertion_type': (
          'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
        ),
        'client_assertion': jwt.encode(
          vaatimus,
          self.yksityinen_avain_pem,
          self.algoritmi,
          headers=(
            {'kid': self.avain_id}
            if self.avain_id
            else {}
          ),
        )
      }

      # Tehdään avainnuspyyntö HTTP-lomakemuodossa.
      async with self._istunto.post(
        koko_polku,
        data=data,
        headers={
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      ) as sanoma:
        if sanoma.status >= 400:
          raise self.TunnistautuminenEpaonnistui(
            sanoma=sanoma,
            status=sanoma.status,
            data=await sanoma.text(),
          )
        sanoma = await sanoma.json()
      return (
        frozenset(sanoma['scope'].split(' ')),
        sanoma['access_token'],
        datetime.fromtimestamp(
          jwt.decode(
            sanoma['access_token'],
            options={'verify_signature': False}
          )['exp']
        ),
      )
      # async def _hae_avain

    async def hae_avain(self, *, oikeudet: set[str], voimassaolo: timedelta):
      nyt: datetime = datetime.now()

      async with self._avainpyynto_lukko:
        for saadut_oikeudet, avain, voimassa in frozenset(
          self._saadut_avaimet
        ):
          if voimassa <= nyt:
            self._saadut_avaimet.remove((saadut_oikeudet, avain, voimassa))
          elif not oikeudet - saadut_oikeudet:
            break
        else:
          try:
            saadut_oikeudet, avain, voimassa = await self._hae_avain(
              scope=oikeudet,
              exp=voimassaolo,
            )
          except Exception as exc:  # pylint: disable=broad-except
            raise self.TunnistautuminenEpaonnistui(
              teksti=str(exc)
            ) from exc
          else:
            if puuttuvat_oikeudet := oikeudet - saadut_oikeudet:
              raise self.TunnistautuminenEpaonnistui(
                teksti=(
                  f'Pyydettyjä oikeuksia ei myönnetty: {puuttuvat_oikeudet}'
                ),
              )
            self._saadut_avaimet.add((saadut_oikeudet, avain, voimassa))
            # else
          # else
        # async with self._avainpyynto_lukko
      return avain

    # class Oauth2Yhteys

  @cached_property
  def _oauth2_yhteys(self):
    ''' Alusta erillinen rajapintayhteys tunnistautumista varten. '''
    return self.Oauth2Yhteys(
      palvelin=self.oauth2_palvelin or self.palvelin,
      kayttaja_id=self.kayttaja_id,
      yksityinen_avain_pem=self.yksityinen_avain_pem,
      avain_id=self.avain_id,
    )
    # def _oauth2_yhteys

  async def pyynnon_otsakkeet(self, **kwargs):
    oikeudet: set[str] = set()
    if isinstance(self.oikeus, str):
      # pylint: disable=unhashable-member
      oikeudet = {self.oikeus}
    elif self.oikeus:
      oikeudet = set(self.oikeus)

    async with self._oauth2_yhteys as yhteys:
      avain = await yhteys.hae_avain(
        oikeudet=oikeudet,
        voimassaolo=self.avaimen_voimassaolo,
      )
    return {
      **await super().pyynnon_otsakkeet(**kwargs),
      'Authorization': f'Bearer {avain}',
    }
    # async def pyynnon_otsakkeet

  # class Oauth2Tunnistautuminen
