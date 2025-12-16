from dataclasses import dataclass
from typing import Optional
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from croniter import croniter, CroniterBadCronError, CroniterBadDateError


@dataclass
class CronSummary:
    """
    Datová třída sumarizující informace o výrazu cron
    """
    expression: str
    syntax_ok: bool
    has_occurrence: bool
    next_run: Optional[datetime] = None
    errors: list[str] = None

def summarize_cron(expr: str, tz: str = "Europe/Prague") -> CronSummary:
    """
    Sumarizuje informace o výrazu cron

    :param expr:    výraz cron
    :param tz:      časová zóna
    :return:        CronSummary
    """
    errors: list[str] = []
    syntax_ok = is_cron_syntax_valid(expr)
    if not syntax_ok:
        errors.append("Neplatná cron syntaktika nebo hodnoty mimo rozsah.")
        return CronSummary(expr, syntax_ok, False, None, errors)

    tzinfo = ZoneInfo(tz)
    start = datetime.now(tzinfo)
    try:
        it = croniter(expr, start)
        nxt = it.get_next(datetime).astimezone(tzinfo)
        has_occ = True
    except Exception as e:
        # extrémně řídké/nesmyslné výrazy by spadly sem (teoreticky)
        errors.append(f"Nepodařilo se určit další výskyt: {e}")
        has_occ = False
        nxt = None

    # volitelně ještě použijeme horizont
    if has_occ and not has_next_occurrence(expr, start=start, horizon_years=5):
        has_occ = False
        nxt = None
        errors.append("Výraz je sice syntakticky správný, ale v horizontu 5 let nemá žádný výskyt.")

    return CronSummary(expr, syntax_ok, has_occ, nxt, errors)


def is_cron_syntax_valid(expr: str) -> bool:
    """
    Syntaktická validace

    :param expr:    Výraz cron
    :return:        True/False
    """
    try:
        croniter(expr, datetime.now())
        return True
    except (CroniterBadCronError, CroniterBadDateError):
        return False

def has_next_occurrence(expr: str, start: datetime | None = None, horizon_years: int = 10) -> bool:
    """
    Sémantická validace

    Vrátí True, pokud existuje výskyt do horizon_years od `start`.
    Chrání před „prázdnými“ výrazy typu 30. února.

    :param expr:    Výraz cron
    :param start:   Počáteční datum validace (None = now())
    :param horizon_years:   Časový horizont validace (implicitně 10 let)

    :return:        True/False
    """
    start = start or datetime.now()
    try:
        it = croniter(expr, start)
    except (CroniterBadCronError, CroniterBadDateError):
        return False

    limit_dt = start + timedelta(days=365 * horizon_years)
    # Zároveň nastavíme horní mez kroků, aby se to nikdy nezacyklilo.
    try:
        for _ in range(10000):
            nxt = it.get_next(datetime)
            if nxt <= limit_dt:
                return True
            else:
                break
    except (CroniterBadCronError, CroniterBadDateError):
        return False
    return False


def validate_cron(expr: str, horizon_years: int = 10) -> tuple[bool, list[str]]:
    """
    Validuje výraz cron syntakticky i sémanticky

    Vrací (is_valid, errors):
     - is_valid: True jen pokud je syntaktika OK a existuje budoucí výskyt do horizon_years.
     - errors: seznam zpráv s důvody nevalidity.

    :param expr:    Výraz cron
    :param horizon_years:   Časový horizont validace (implicitně 10 let)
    :return:        (is_valid, errors)
    """
    errors: list[str] = []

    if not is_cron_syntax_valid(expr):
        errors.append("Neplatná cron syntaktika nebo hodnoty mimo rozsah.")
        return False, errors

    if not has_next_occurrence(expr, horizon_years=horizon_years):
        errors.append(
            f"Výraz je syntakticky v pořádku, ale v následujících {horizon_years} letech "
            f"nenastane žádné spuštění (např. kombinace typu 30. února)."
        )
        return False, errors
    return True, errors
