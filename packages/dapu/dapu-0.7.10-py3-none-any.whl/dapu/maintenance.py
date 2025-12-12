"""
Otsime käismasolevaid pythoni processe, näitaks cron pool käivitauid, mis hetkel veel käivad
Kasutuskoht: cron käivitas mingi teadaoleva nimega scripti ja meil on vaja hoiduda tegvustest, kui see käib

NB! psutil peale saamiseks võib olla vaja teha lisategevusi, nt Alpine Linux korral:
apk add --no-cache gcc libc-dev musl-dev make binutils
apk add build-base linux-headers
(windows, ubuntu jms omavad juba vajalikke teeke)
viga saab testida: pip install psutil

"""
from loguru import logger
import psutil
from datetime import datetime
from time import sleep
from dbpoint.hub import Hub
from dapu.context import DapuContext
from .perks import halt, real_path_from_list
from .fileops import read_content_of_file, read_content_of_package_file


def cmdline_contains(proc_cmd_line: list[str], script_name: str, needed_args: list[str]) -> bool:
    script_name = script_name.lower()
    if not script_name.endswith('.py'):
        script_name += '.py'
    # simple way -- if script name is any arg (actually should be first without -m or any other switch)
    script_is_found = False
    for item in proc_cmd_line:
        if item.lower().endswith(script_name): # eg "/scripts/run_repeat.py" ends with "run_repeat.py"
            script_is_found = True
    if not script_is_found:
        return False
    for needed in needed_args:
        found = False
        for item in proc_cmd_line:
            if item == needed:
                found = True
        if not found:
            return False
    return True


def python_script_seek(script_name: str, needed_args: list[str]) -> bool:
    processes = psutil.process_iter()
    for process in processes:
        if 'python' in process.name().lower(): # both 'python3' and 'python' and 'Python'
            if cmdline_contains(process.cmdline(), script_name, needed_args):
                return True
    return False


def maintenance_context(args) -> DapuContext:
    work_dir = real_path_from_list(args, 0) # first argument is working directory
    if work_dir is None:
        halt(3, "No project (work) directory specified")
        return # type: ignore # only for pylance
    profiles_text: str = read_content_of_file(work_dir + "/conf/sql.yaml") or read_content_of_file(work_dir + "/conf/profiles.yaml") or "" # FIXME make it configurable...
    sql_drivers_text: str = read_content_of_package_file("dapu", "drivers.yaml") or "" # known SQL drivers from package
    added_and_overloaded_drivers: str = read_content_of_file(work_dir + "/conf/drivers.yaml") or ""
    sql_drivers_text += "\n" + added_and_overloaded_drivers  # FIXME kerge mure -- mis siis kui erinevadfailid pole sama taandega?

    hub = Hub(profiles_text, sql_drivers_text) # dbpoint gets all sql-type profiles / all profiles (who cares)
    context = DapuContext(work_dir, hub)
    profiles_text += "\n" + (read_content_of_file(work_dir + "/conf/file.yaml") or "") # FIXME kerge mure -- mis siis kui erinevadfailid pole sama taandega?
    context.set_profiles(profiles_text) # text -> dict
    context.set_tags(args[1:] if len(args) > 1 and args[1] is not None else [])
    return context


def maintenance_start(args):
    """
    args[0] = work_dir, gives as conf (incl conf for database)
    args[1] = script name to avoid running (eg run_repeat.py)
    args{2] = how many minutes to wait, default 55 minutes
    maintenance pause flag is set in database (meta.)
    if no subfolder "routes" present or if any global exception then it is the first time and can be ignored
    """
    context = maintenance_context(args)
    script = "run_repeat.py"
    if len(args) > 1:
        script = args[1] # "run_repeat.py"

    # raise the flag
    try: # error may occur on very first run then database is not ready
        context.signal_pause_switch(True)
    except:
        logger.info(f"Pause error, assuming database is not ready and may continue")
        return
    logger.info(f"Set to pause (maintenance mode now)")
    # check and wait
    start_time = datetime.now()
    sleep_time_seconds = 5 # seconds
    total_wait_minutes = 55 # minutes
    if len(args) > 2:
        total_wait_minutes = int(args[2])
    countdown = (60 / sleep_time_seconds) * total_wait_minutes # how many times cycle with sleep will occur
    while python_script_seek(script, []):
        countdown -= 1
        if countdown == 0:
            logger.error("Tired of waiting")
            halt(8, f"Tired of waiting ({datetime.now() - start_time} seconds), script {script} still running")
        sleep(5)
    end_time = datetime.now()
    logger.info(f"we waited for {script} to finish {end_time - start_time} seconds")


def maintenance_end(args):
    context = maintenance_context(args)
    # lower the flag
    context.signal_pause_switch(False)
    logger.info(f"Restored from pause (work mode now)")
