from stats.common.decorators import returns_numberdict
from stats.common import transaction_date

class PublisherStats(object):
    pass

class ActivityFileStats(object):
    pass

class ActivityStats(object):
    blank = False

    @returns_numberdict
    def activities_with_future_transactions(self):
        future_transactions = 0
        for transaction in self.element.findall('transaction'):
            if transaction_date(transaction) > self.today:
                future_transactions += 1
        if future_transactions:
            return {self.element.find('iati-identifier').text:future_transactions}
    pass

class OrganisationFileStats(object):
    pass

class OrganisationStats(object):
    pass
        
class AllDataStats(object):
    pass

