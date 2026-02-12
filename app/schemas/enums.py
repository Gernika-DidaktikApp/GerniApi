"""Enumeraciones para estados y tipos del sistema.

Este módulo define enums para prevenir errores de typos en estados
y garantizar consistencia en la base de datos y APIs.

Autor: Gernibide
"""

from enum import Enum


class EstadoPartida(str, Enum):
    """Estado de una partida/juego.

    Valores posibles:
    - EN_PROGRESO: Partida activa, en curso
    - COMPLETADO: Partida finalizada exitosamente
    - ABANDONADA: Partida iniciada pero no completada
    """

    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    ABANDONADA = "abandonada"


class EstadoActividad(str, Enum):
    """Estado de progreso de una actividad educativa.

    Valores posibles:
    - EN_PROGRESO: Actividad iniciada pero no completada
    - COMPLETADO: Actividad finalizada
    """

    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"


class EstadoPunto(str, Enum):
    """Estado de progreso de un punto/módulo del mapa.

    Valores posibles:
    - NO_INICIADA: Usuario no ha comenzado el punto
    - EN_PROGRESO: Punto parcialmente completado
    - COMPLETADA: Punto completado al 100%
    """

    NO_INICIADA = "no_iniciada"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"


class DeviceType(str, Enum):
    """Tipo de dispositivo desde el cual se realiza una acción.

    Valores posibles:
    - IOS: Dispositivos iPhone/iPad
    - ANDROID: Dispositivos Android
    - WEB: Navegador web (desktop/mobile)
    - UNKNOWN: Tipo desconocido o no especificado
    """

    IOS = "iOS"
    ANDROID = "Android"
    WEB = "Web"
    UNKNOWN = "Unknown"
