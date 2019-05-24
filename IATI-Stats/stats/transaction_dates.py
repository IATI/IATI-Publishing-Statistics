import stats.dashboard

class PublisherStats(stats.dashboard.PublisherStats):
    enabled_stats = ['most_recent_transaction_date', 'latest_transaction_date']

class ActivityFileStats(object):
    pass

class ActivityStats(stats.dashboard.ActivityStats):
    enabled_stats = ['transaction_dates']

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
        
class AllDataStats(object):
    pass

