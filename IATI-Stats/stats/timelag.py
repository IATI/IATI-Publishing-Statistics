import stats.dashboard

class PublisherStats(stats.dashboard.PublisherStats):
    enabled_stats = ['timelag']

class ActivityFileStats(object):
    pass

class ActivityStats(stats.dashboard.ActivityStats):
    enabled_stats = ['transaction_months_with_year']

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
        
class AllDataStats(object):
    pass

