from stats.common.decorators import returns_number

class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

class ActivityStats(object):
    blank = False

    @returns_number
    def activities(self):
        return 1
    pass

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
        
class AllDataStats(object):
    pass

