import secret
from TangoConnection import TangoConnection


def get_jobs():
    tango = TangoConnection(secret.TANGO_URL, secret.TANGO_KEY)
    jobs = tango.get_current_jobs_count()
    print("Returned ", str(jobs))


if __name__ == '__main__':
    get_jobs()
