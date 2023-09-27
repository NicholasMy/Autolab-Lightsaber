import secret
from autolab_portal_connection import AutolabPortalConnection


def get_jobs():
    portal = AutolabPortalConnection(secret.PORTAL_URL, secret.PORTAL_API_KEY)
    jobs = portal.get_tango_histogram()
    print(jobs)


if __name__ == '__main__':
    get_jobs()
