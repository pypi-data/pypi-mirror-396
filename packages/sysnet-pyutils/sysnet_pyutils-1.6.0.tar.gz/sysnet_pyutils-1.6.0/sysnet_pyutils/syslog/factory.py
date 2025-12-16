import asyncio
import datetime
import os
import socket

from utils import LoggedObject, Singleton


class SyslogFactory(LoggedObject, metaclass=Singleton):
    """
    Slouží k přímému odesílání logů na syslog server
    """
    # Severity konstanty
    SEVERITY_EMERGENCY = 0
    SEVERITY_ALERT     = 1
    SEVERITY_CRITICAL  = 2
    SEVERITY_ERROR     = 3
    SEVERITY_WARNING   = 4
    SEVERITY_NOTICE    = 5
    SEVERITY_INFO      = 6
    SEVERITY_DEBUG     = 7

    # Facility konstanty
    FACILITY_USER      = 1
    FACILITY_LOCAL0    = 16

    def __init__(self, object_name='SYSLOG_FACTORY', server="localhost", port=514, facility=FACILITY_USER, tag="python-app", pid=None, udp=True):
        super().__init__(object_name)
        self.server = server
        self.port = port
        self.facility = facility
        self.tag = tag
        self.pid = pid if pid else os.getpid()
        self.hostname = socket.gethostname()
        self.udp = udp
        self.enabled = True

    def _format_message(self, message, severity, tag=None, pid=None):
        if not tag: tag = self.tag
        if not pid: pid = self.pid
        pri = self.facility * 8 + severity
        timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
        return f"<{pri}>{timestamp} {self.hostname} {tag}[{pid}]: {message}"

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    async def send(self, message, severity=SEVERITY_INFO, tag=None, pid=None):
        if not self.enabled:
            self.log.debug(f"{self.name} Factory is disabled.")
            return False
        syslog_msg = self._format_message(message, severity, tag=tag, pid=pid)
        # Nejprve zkusíme UDP
        if self.udp:
            out = await self._send_udp(syslog_msg)
            if out:
                return True
            out = await self._send_tcp(syslog_msg)
            if out:
                return True
        else:
            out = await self._send_tcp(syslog_msg)
            if out:
                return True
            out = await self._send_udp(syslog_msg)
            if out:
                return True
        return False

    async def _send_tcp(self, syslog_msg) -> bool:
        try:
            reader, writer = await asyncio.open_connection(self.server, self.port)
            writer.write(syslog_msg.encode("utf-8"))
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            self.log.debug(f"{self.name} Odesláno přes TCP: {syslog_msg}")
            return True
        except Exception as e:
            self.log.error(f"{self.name} TCP selhalo ({type(e)} - {e})")
            return False

    async def _send_udp(self, syslog_msg):
        try:
            loop = asyncio.get_running_loop()
            transport, _ = await loop.create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(),
                remote_addr=(self.server, self.port)
            )
            transport.sendto(syslog_msg.encode("utf-8"))
            transport.close()
            self.log.debug(f"{self.name} Odesláno přes UDP: {syslog_msg}")
            return True
        except Exception as e:
            self.log.error(f"{self.name} UDP selhalo ({type(e)} - {e})")
            return False


    # Wrapper metody
    async def log_info(self, message, tag=None, pid=None):
        """
        Odesílání INFO do syslog

        :param message: zpráva
        :param tag:     Tag-obvykle kód aplikace
        :param pid:     Identifikátor procesu (ponechat prázdné)
        :return:        True/False
        """
        await self.send(message, severity=self.SEVERITY_INFO, tag=tag, pid=pid)

    async def log_error(self, message, tag=None, pid=None):
        """
        Odesílání ERROR do syslog

        :param message: zpráva
        :param tag:     Tag-obvykle kód aplikace
        :param pid:     Identifikátor procesu (ponechat prázdné)
        :return:        True/False
        """
        await self.send(message, severity=self.SEVERITY_ERROR, tag=tag, pid=pid)

    async def log_critical(self, message, tag=None, pid=None):
        """
        Odesílání CRITICAL do syslog

        :param message: zpráva
        :param tag:     Tag-obvykle kód aplikace
        :param pid:     Identifikátor procesu (ponechat prázdné)
        :return:        True/False
        """
        await self.send(message, severity=self.SEVERITY_CRITICAL, tag=tag, pid=pid)

    async def log_debug(self, message, tag=None, pid=None):
        """
        Odesílání DEBUG do syslog

        :param message: zpráva
        :param tag:     Tag-obvykle kód aplikace
        :param pid:     Identifikátor procesu (ponechat prázdné)
        :return:        True/False
        """
        await self.send(message, severity=self.SEVERITY_DEBUG, tag=tag, pid=pid)
